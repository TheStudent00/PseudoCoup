"""relational_ledger -- Converts a `URLedger` into a Flat Relational Tensor (`RelationalLedgerTable`).

Represents any branched program in `URLedger` (`URIf`, `URWhile`, `URHiOpCall`, `URHolderCast`,
`URCall`, `URAssign`, `URReturn`, `URFunc`) as a 2D integer tensor `nodes[N, 24]` with explicit
parent->child edges and top-down tree `depth` (`0 .. max_depth`), so every depth layer `d`
can be lowered in a single data-parallel GPU pass.
"""
from __future__ import annotations

from typing import Any
import torch

from .dict_lut import (
    KIND_ASSIGN_DECL,
    KIND_ASSIGN_MUT,
    KIND_BLOCK,
    KIND_CALL,
    KIND_CONST,
    KIND_FUNC,
    KIND_HIOP,
    KIND_HOLDER_CAST,
    KIND_IF,
    KIND_IF_ELSE,
    KIND_MODULE,
    KIND_PARAM_LIST,
    KIND_RETURN,
    KIND_VAR,
    KIND_WHILE,
    OP_TO_ID,
    RVAL_TO_ID,
)
from ..ledgerer.ur_ledger import (
    URAssign,
    URCall,
    URConst,
    URFunc,
    URHiOpCall,
    URHolderCast,
    URIf,
    URLedger,
    URReturn,
    URVar,
    URWhile,
    _is_bitmask_63,
)

COL_ID = 0
COL_DEPTH = 1
COL_KIND = 2
COL_OP = 3
COL_RVAL = 4
COL_EXTRA = 5
COL_INDENT = 6
COL_SYM_OFF = 7
COL_SYM_LEN = 8
COL_CHILDREN_START = 9
MAX_CHILDREN = 15
NUM_COLS = COL_CHILDREN_START + MAX_CHILDREN


class RelationalLedgerTable:
    """Flat relational tensor representation of a URLedger with explicit depth levels."""

    def __init__(self, ledger: URLedger, device: str = "cpu") -> None:
        self.device = torch.device(device)
        self._rows: list[list[int]] = []
        self._sym_pool = bytearray()
        self._sym_cache: dict[bytes, tuple[int, int]] = {}
        self.root_id = self._build_module(ledger.functions, depth=0)
        self.nodes = torch.tensor(self._rows, dtype=torch.long, device=self.device)
        self.symbol_bytes = torch.tensor(list(self._sym_pool), dtype=torch.uint8, device=self.device)
        self.max_depth = int(self.nodes[:, COL_DEPTH].max().item()) if len(self._rows) > 0 else 0

    def _add_sym(self, s: str) -> tuple[int, int]:
        b = s.encode("utf-8")
        if not b:
            return (0, 0)
        if b not in self._sym_cache:
            off = len(self._sym_pool)
            self._sym_pool.extend(b)
            self._sym_cache[b] = (off, len(b))
        return self._sym_cache[b]

    def _alloc_row(self, depth: int, kind: int, op: int = 0, rval: int = 0,
                   extra: int = 0, indent: int = 0, sym: str = "") -> int:
        nid = len(self._rows)
        off, ln = self._add_sym(sym)
        row = [nid, depth, kind, op, rval, extra, indent, off, ln] + [-1] * MAX_CHILDREN
        self._rows.append(row)
        return nid

    def _set_children(self, nid: int, children: list[int]) -> None:
        for idx, cid in enumerate(children[:MAX_CHILDREN]):
            self._rows[nid][COL_CHILDREN_START + idx] = cid

    def _build_module(self, funcs: list[URFunc], depth: int) -> int:
        if len(funcs) <= MAX_CHILDREN:
            nid = self._alloc_row(depth, KIND_MODULE, extra=len(funcs))
            cids = [self._build_func(fn, depth + 1) for fn in funcs]
            self._set_children(nid, cids)
            return nid
        chunks = [funcs[i : i + MAX_CHILDREN] for i in range(0, len(funcs), MAX_CHILDREN)]
        nid = self._alloc_row(depth, KIND_MODULE, extra=len(chunks))
        cids = [self._build_module(ch, depth + 1) for ch in chunks]
        self._set_children(nid, cids)
        return nid

    def _build_func(self, fn: URFunc, depth: int) -> int:
        nid = self._alloc_row(depth, KIND_FUNC, sym=fn.func_name)
        pid = self._alloc_row(depth + 1, KIND_PARAM_LIST, extra=len(fn.params))
        p_cids = [self._alloc_row(depth + 2, KIND_CONST, sym=p.name) for p in fn.params]
        self._set_children(pid, p_cids)
        bid = self._build_block(fn.body, depth + 1, indent=1)
        self._set_children(nid, [pid, bid])
        return nid

    def _build_block(self, stmts: list[Any], depth: int, indent: int) -> int:
        if len(stmts) <= MAX_CHILDREN:
            nid = self._alloc_row(depth, KIND_BLOCK, extra=len(stmts))
            cids = [self._build_stmt(s, depth + 1, indent) for s in stmts]
            self._set_children(nid, cids)
            return nid
        chunks = [stmts[i : i + MAX_CHILDREN] for i in range(0, len(stmts), MAX_CHILDREN)]
        nid = self._alloc_row(depth, KIND_BLOCK, extra=len(chunks))
        cids = [self._build_block(ch, depth + 1, indent) for ch in chunks]
        self._set_children(nid, cids)
        return nid

    def _build_stmt(self, stmt: Any, depth: int, indent: int) -> int:
        if isinstance(stmt, URAssign):
            k = KIND_ASSIGN_DECL if stmt.is_decl else KIND_ASSIGN_MUT
            nid = self._alloc_row(depth, k, indent=indent, sym=stmt.target)
            cid = self._build_expr(stmt.expr, depth + 1)
            self._set_children(nid, [cid])
            return nid
        if isinstance(stmt, URIf):
            if stmt.else_body:
                nid = self._alloc_row(depth, KIND_IF_ELSE, indent=indent)
                c_cond = self._build_expr(stmt.cond, depth + 1)
                c_then = self._build_block(stmt.then_body, depth + 1, indent + 1)
                c_else = self._build_block(stmt.else_body, depth + 1, indent + 1)
                self._set_children(nid, [c_cond, c_then, c_else])
                return nid
            nid = self._alloc_row(depth, KIND_IF, indent=indent)
            c_cond = self._build_expr(stmt.cond, depth + 1)
            c_then = self._build_block(stmt.then_body, depth + 1, indent + 1)
            self._set_children(nid, [c_cond, c_then])
            return nid
        if isinstance(stmt, URWhile):
            nid = self._alloc_row(depth, KIND_WHILE, indent=indent)
            c_cond = self._build_expr(stmt.cond, depth + 1)
            c_body = self._build_block(stmt.body, depth + 1, indent + 1)
            self._set_children(nid, [c_cond, c_body])
            return nid
        if isinstance(stmt, URReturn):
            nid = self._alloc_row(depth, KIND_RETURN, indent=indent)
            cid = self._build_expr(stmt.expr, depth + 1)
            self._set_children(nid, [cid])
            return nid
        raise ValueError(f"Unsupported stmt: {stmt}")

    def _build_expr(self, expr: Any, depth: int) -> int:
        if isinstance(expr, URConst):
            return self._alloc_row(depth, KIND_CONST, sym=str(expr.value))
        if isinstance(expr, URVar):
            return self._alloc_row(depth, KIND_VAR, sym=expr.name)
        if isinstance(expr, URHolderCast):
            rval_name = "cast_noop" if (expr.src_holder == expr.dst_holder or expr.dst_holder in ("i64", "u64")) else f"cast_{expr.dst_holder}"
            nid = self._alloc_row(depth, KIND_HOLDER_CAST, rval=RVAL_TO_ID[rval_name])
            cid = self._build_expr(expr.expr, depth + 1)
            self._set_children(nid, [cid])
            return nid
        if isinstance(expr, URCall):
            nid = self._alloc_row(depth, KIND_CALL, extra=len(expr.args), sym=expr.func_name)
            cids = [self._build_expr(a, depth + 1) for a in expr.args]
            self._set_children(nid, cids)
            return nid
        if isinstance(expr, URHiOpCall):
            op_id = OP_TO_ID[expr.op_symbol]
            meaning = expr.ur_node.meaning
            if meaning.get("guarded", False):
                rval_str = "guarded"
            else:
                src_l = str(expr.ur_node.hiop.get("lang", "c")).lower()
                rval_str = f"src_{src_l}" if f"src_{src_l}" in RVAL_TO_ID else "guarded"
            rval_id = RVAL_TO_ID.get(rval_str, 0)
            extra = 1 if (len(expr.args) == 2 and _is_bitmask_63(expr.args[1])) else 0
            nid = self._alloc_row(depth, KIND_HIOP, op=op_id, rval=rval_id, extra=extra)
            cids = [self._build_expr(a, depth + 1) for a in expr.args]
            self._set_children(nid, cids)
            return nid
        raise ValueError(f"Unsupported expr: {expr}")

    def depth_histogram(self) -> dict[int, int]:
        depths = self.nodes[:, COL_DEPTH]
        return {int(d): int((depths == d).sum().item()) for d in range(self.max_depth + 1)}
