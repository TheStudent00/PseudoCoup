"""tensor_lowerer -- Level-Synchronous `max_depth`-Pass GPU Tensor Lowerer (`GPUTensorLowerer`).

Lowers a `RelationalLedgerTable` into any of the 12 target languages (and maps nodes to
PseudoArch RISC-V `Unit`s) using strictly `1` dictionary lookup pass + `max_depth + 1`
level-synchronous parallel tensor gather passes (`torch.cumsum` + `torch.searchsorted`).
Zero per-node or per-character Python loops exist inside the depth passes.
"""
from __future__ import annotations

from typing import Any
import torch

from .dict_lut import (
     DictLUT,
    LANG_TO_ID,
    SEG_CHILD,
    SEG_INDENT,
    SEG_LIT,
    SEG_SYM,
)
from .relational_ledger import (
    COL_CHILDREN_START,
    COL_DEPTH,
    COL_EXTRA,
    COL_INDENT,
    COL_KIND,
    COL_OP,
    COL_RVAL,
    COL_SYM_LEN,
    COL_SYM_OFF,
    RelationalLedgerTable,
)


class GPUTensorLowerer:
    """Executes dictionary mapping + `max_depth` bottom-up tensor gather passes."""

    def __init__(self, lut: DictLUT) -> None:
        self.lut = lut
        self.device = lut.device

    def lower(self, table: RelationalLedgerTable, target_lang: str) -> dict[str, Any]:
        nodes = table.nodes
        n_nodes = nodes.shape[0]
        lang_id = LANG_TO_ID[target_lang]

        # === PASS 0: Parallel Dictionary Lookup across all N nodes simultaneously ===
        t_ids = self.lut.lut_table[
            lang_id,
            nodes[:, COL_KIND],
            nodes[:, COL_OP],
            nodes[:, COL_RVAL],
            nodes[:, COL_EXTRA],
        ]
        unit_ids = self.lut.op_to_unit_idx[lang_id, nodes[:, COL_OP]]

        # Unified 1D byte pool: [literal_bytes | symbol_bytes | 64 spaces | level_d bytes ...]
        lit_base = 0
        sym_base = int(self.lut.literal_bytes.numel())
        indent_base = sym_base + int(table.symbol_bytes.numel())
        spaces = torch.full((64,), 32, dtype=torch.uint8, device=self.device)
        pool = torch.cat([self.lut.literal_bytes, table.symbol_bytes, spaces], dim=0)

        node_pool_off = torch.zeros(n_nodes, dtype=torch.long, device=self.device)
        node_pool_len = torch.zeros(n_nodes, dtype=torch.long, device=self.device)
        pass_metrics: list[dict[str, int]] = []

        # === PASSES 1 .. max_depth + 1: Bottom-Up Level-Synchronous Tensor Gather ===
        for d in range(table.max_depth, -1, -1):
            idx_d = torch.where(nodes[:, COL_DEPTH] == d)[0]
            m_d = int(idx_d.numel())
            if m_d == 0:
                continue

            td = t_ids[idx_d]                      # [M_d]
            st = self.lut.seg_type[td]             # [M_d, S]
            sa = self.lut.seg_arg[td]              # [M_d, S]
            sl = self.lut.seg_len[td]              # [M_d, S]

            src_off = torch.zeros_like(st)
            byte_len = torch.zeros_like(st)

            # 1. Literal segments
            m_lit = (st == SEG_LIT)
            src_off = torch.where(m_lit, lit_base + sa, src_off)
            byte_len = torch.where(m_lit, sl, byte_len)

            # 2. Symbol/constant segments
            m_sym = (st == SEG_SYM)
            sym_o = (sym_base + nodes[idx_d, COL_SYM_OFF]).unsqueeze(1).expand_as(st)
            sym_l = nodes[idx_d, COL_SYM_LEN].unsqueeze(1).expand_as(st)
            src_off = torch.where(m_sym, sym_o, src_off)
            byte_len = torch.where(m_sym, sym_l, byte_len)

            # 3. Indentation segments
            m_ind = (st == SEG_INDENT)
            ind_l = ((nodes[idx_d, COL_INDENT].unsqueeze(1) + sa) * 4).clamp(min=0, max=64)
            src_off = torch.where(m_ind, torch.full_like(src_off, indent_base), src_off)
            byte_len = torch.where(m_ind, ind_l, byte_len)

            # 4. Child slot segments (already lowered at depth d + 1!)
            m_ch = (st == SEG_CHILD)
            ch_cols = COL_CHILDREN_START + sa.clamp(min=0, max=14)
            row_expand = idx_d.unsqueeze(1).expand_as(st)
            ch_ids = nodes[row_expand, ch_cols].clamp(min=0)
            src_off = torch.where(m_ch, node_pool_off[ch_ids], src_off)
            byte_len = torch.where(m_ch, node_pool_len[ch_ids], byte_len)

            # Parallel prefix-sum (scan) + searchsorted byte gather for the entire depth layer d
            node_lens_d = byte_len.sum(dim=1)
            node_ends_d = torch.cumsum(node_lens_d, dim=0)
            node_starts_d = node_ends_d - node_lens_d
            pool_base_d = int(pool.numel())

            node_pool_off[idx_d] = pool_base_d + node_starts_d
            node_pool_len[idx_d] = node_lens_d

            active_mask = byte_len.reshape(-1) > 0
            act_off = src_off.reshape(-1)[active_mask]
            act_len = byte_len.reshape(-1)[active_mask]
            seg_end = torch.cumsum(act_len, dim=0)
            seg_start = seg_end - act_len
            tot_bytes_d = int(seg_end[-1].item()) if int(seg_end.numel()) > 0 else 0

            if tot_bytes_d > 0:
                pos = torch.arange(tot_bytes_d, dtype=torch.long, device=self.device)
                seg_idx = torch.searchsorted(seg_end, pos, right=True)
                gather_idx = act_off[seg_idx] + (pos - seg_start[seg_idx])
                level_bytes = pool[gather_idx]
                pool = torch.cat([pool, level_bytes], dim=0)

            pass_metrics.append({
                "depth": d,
                "parallel_nodes_lowered": m_d,
                "bytes_emitted": tot_bytes_d,
            })

        r_off = int(node_pool_off[table.root_id].item())
        r_len = int(node_pool_len[table.root_id].item())
        root_bytes = bytes(pool[r_off : r_off + r_len].cpu().tolist()).decode("utf-8")
        return {
            "code": root_bytes,
            "max_depth": table.max_depth,
            "gpu_depth_passes": len(pass_metrics),
            "total_nodes": n_nodes,
            "template_ids": t_ids,
            "unit_ids": unit_ids,
            "pass_metrics": pass_metrics,
        }
