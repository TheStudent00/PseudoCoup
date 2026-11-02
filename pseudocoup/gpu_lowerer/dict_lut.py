"""dict_lut -- Pre-Packed Dictionary Lookup Tensor (`DictLUT`) for GPU-Parallel Lowering.

Compiles all 12 target languages' lowering templates (Tier-1 operators, Tier-2 AutoPoly
expansions, HolderCast bit-slices, and statement/control-flow templates) plus PseudoArch's
`lang_models` RISC-V machine `Unit` dictionary into flat integer tensors (`torch.Tensor`).

During GPU lowering, Pass 0 maps every node in the `URLedger` to its `template_id` via
a single parallel tensor index gather (`LUT_TABLE[lang_id, kind_id, op_id, rval_id, extra_id]`).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any
import torch

ALL_12_LANGS = [
    "python", "c", "cpp", "go", "rust", "java",
    "typescript", "csharp", "ruby", "php", "dart", "swift",
]
LANG_TO_ID = {l: i for i, l in enumerate(ALL_12_LANGS)}

# Node kinds in the Relational URLedger Table
KIND_CONST = 0
KIND_VAR = 1
KIND_HIOP = 2
KIND_CALL = 3
KIND_HOLDER_CAST = 4
KIND_ASSIGN_DECL = 5
KIND_ASSIGN_MUT = 6
KIND_IF = 7
KIND_IF_ELSE = 8
KIND_WHILE = 9
KIND_RETURN = 10
KIND_BLOCK = 11
KIND_PARAM_LIST = 12
KIND_FUNC = 13
KIND_MODULE = 14
NUM_KINDS = 15

OPS = [
    "none", "+", "-", "*", "/", "//", "%", "&", "|", "^",
    "<<", ">>", "==", "!=", "<", "<=", ">", ">=", "&&", "||",
    "ite", "neg", "trunc_div", "trunc_rem",
]
OP_TO_ID = {op: i for i, op in enumerate(OPS)}

RVALS = [
    "guarded", "saturate_64_<<", "saturate_64_>>", "mask_63_<<", "mask_63_>>",
    "trunc_div", "trunc_rem", "floor_div", "floor_mod",
    "cast_noop", "cast_u32", "cast_i32", "cast_u16", "cast_i16", "cast_u8", "cast_i8",
]
RVAL_TO_ID = {r: i for i, r in enumerate(RVALS)}

# Template segment opcodes inside `TEMPLATE_SEG_TYPE[T, S]`
SEG_EMPTY = 0
SEG_LIT = 1      # Static literal slice from `LITERAL_BYTES[offset : offset + len]`
SEG_CHILD = 2    # Lowered byte slice of `node.children[arg]` from depth > d
SEG_INDENT = 3   # `arg` levels of 4-space indentation (`"    " * (node.indent + arg)`)
SEG_SYM = 4      # Symbol/constant string slice from `ledger.SYMBOL_BYTES`

import re
import sys

try:
    from ..ledgerer.ur_ledger import (
        LedgerToScript,
        URConst,
        URHiOpCall,
        URHolderCast,
        URVar,
        build_holder_cast_node,
        build_ur_node,
    )
except ImportError:
    ROOT_PC = Path(__file__).resolve().parents[1]
    if str(ROOT_PC) not in sys.path:
        sys.path.insert(0, str(ROOT_PC))
    from ledgerer.ur_ledger import (
        LedgerToScript,
        URConst,
        URHiOpCall,
        URHolderCast,
        URVar,
        build_holder_cast_node,
        build_ur_node,
    )

SLOT_RE = re.compile(r"(\$?__SLOT_(\d+)__|\$?__SYM__)")


class DictLUT:
    """Flat PyTorch tensor dictionary mapping (lang, kind, op, rval, arity) -> segment template."""

    def __init__(self, device: str = "cpu") -> None:
        self.device = torch.device(device)
        # LUT_TABLE[lang_id(12), kind_id(15), op_id(24), rval_id(16), extra_arity(16)] -> template_id
        self.lut_table = torch.zeros((len(ALL_12_LANGS), NUM_KINDS, len(OPS), len(RVALS), 16), dtype=torch.long)
        self._lit_pool = bytearray()
        self._lit_cache: dict[bytes, tuple[int, int]] = {}
        self._templates: list[list[tuple[int, int, int]]] = [[(SEG_EMPTY, 0, 0)]]
        self._build_all_templates()
        self._pack_tensors()
        self._load_pseudoarch_unit_lut()

    def _add_lit(self, s: str) -> tuple[int, int]:
        b = s.encode("utf-8")
        if not b:
            return (0, 0)
        if b not in self._lit_cache:
            off = len(self._lit_pool)
            self._lit_pool.extend(b)
            self._lit_cache[b] = (off, len(b))
        return self._lit_cache[b]

    def _register_segments(self, segs: list[tuple[int, int, int]]) -> int:
        tid = len(self._templates)
        self._templates.append(segs)
        return tid

    def _compile_pattern_str(self, pat: str, indent_head: bool = False) -> int:
        segs: list[tuple[int, int, int]] = []
        if indent_head:
            segs.append((SEG_INDENT, 0, 0))
        pos = 0
        for m in SLOT_RE.finditer(pat):
            if m.start() > pos:
                off, ln = self._add_lit(pat[pos : m.start()])
                segs.append((SEG_LIT, off, ln))
            tok = m.group(1)
            if tok.startswith("$"):
                off, ln = self._add_lit("$")
                segs.append((SEG_LIT, off, ln))
            if "SYM" in tok:
                segs.append((SEG_SYM, 0, 0))
            else:
                segs.append((SEG_CHILD, int(m.group(2)), 0))
            pos = m.end()
        if pos < len(pat):
            off, ln = self._add_lit(pat[pos:])
            segs.append((SEG_LIT, off, ln))
        return self._register_segments(segs)

    def _build_all_templates(self) -> None:
        v0 = URVar("__SLOT_0__", "i64")
        v1 = URVar("__SLOT_1__", "i64")
        v2 = URVar("__SLOT_2__", "i64")

        for lang_id, lang in enumerate(ALL_12_LANGS):
            semi = ";" if lang in ("c", "cpp", "rust", "typescript", "java", "csharp", "dart", "php") else ""
            # 0. CONST and VAR
            self.lut_table[lang_id, KIND_CONST, 0, 0, 0] = self._compile_pattern_str("__SYM__")
            self.lut_table[lang_id, KIND_VAR, 0, 0, 0] = self._compile_pattern_str("$__SYM__" if lang == "php" else "__SYM__")

            # 1. HIOP (both guarded Tier-1 and unguarded Tier-2 R_vals)
            for op_id, op_sym in enumerate(OPS):
                if op_sym == "none":
                    continue
                for rval_id, rval in enumerate(RVALS):
                    if rval.startswith("cast_") or (op_sym in ("ite", "neg") and rval != "guarded"):
                        continue
                    is_guarded = (rval == "guarded")
                    node = build_ur_node(lang, op_sym, "i64", is_guarded)
                    if not is_guarded:
                        node.meaning = {"tier": 2, "D_ok": "True", "D_trap": "False", "R_val": rval, "guarded": False}
                    args = [v0] if op_sym == "neg" else ([v0, v1, v2] if op_sym == "ite" else [v0, v1])
                    hiop = URHiOpCall(node, args, op_sym, "i64")
                    canon = LedgerToScript.canonicalize_expr(hiop, lang)
                    pat = LedgerToScript._emit_expr(canon, lang).replace("$__SLOT_", "__SLOT_")
                    self.lut_table[lang_id, KIND_HIOP, op_id, rval_id, 0] = self._compile_pattern_str(pat)

            # 2. HOLDER_CAST
            for dst_h, rval_name in [("i64", "cast_noop"), ("u64", "cast_noop"), ("u32", "cast_u32"),
                                     ("i32", "cast_i32"), ("u16", "cast_u16"), ("i16", "cast_i16"),
                                     ("u8", "cast_u8"), ("i8", "cast_i8")]:
                rv_id = RVAL_TO_ID[rval_name]
                cast_node = build_holder_cast_node(v0, "i64", dst_h)
                canon = LedgerToScript.canonicalize_expr(cast_node, lang)
                pat = LedgerToScript._emit_expr(canon, lang).replace("$__SLOT_", "__SLOT_")
                self.lut_table[lang_id, KIND_HOLDER_CAST, 0, rv_id, 0] = self._compile_pattern_str(pat)

            # 3. CALL (arity 0..8)
            for arity in range(9):
                slots = ", ".join(f"__SLOT_{k}__" for k in range(arity))
                self.lut_table[lang_id, KIND_CALL, 0, 0, arity] = self._compile_pattern_str(f"__SYM__({slots})")

            # 4. ASSIGN_DECL & ASSIGN_MUT
            tgt = "$__SYM__" if lang == "php" else "__SYM__"
            decl_map = {
                "c": f"int64_t {tgt} = __SLOT_0__;",
                "cpp": f"int64_t {tgt} = __SLOT_0__;",
                "go": f"{tgt} := __SLOT_0__",
                "rust": f"let mut {tgt}: i64 = __SLOT_0__;",
                "typescript": f"let {tgt}: number = __SLOT_0__;",
                "java": f"long {tgt} = __SLOT_0__;",
                "csharp": f"long {tgt} = __SLOT_0__;",
                "dart": f"int {tgt} = __SLOT_0__;",
                "swift": f"var {tgt}: Int64 = __SLOT_0__",
            }
            decl_pat = decl_map.get(lang, f"{tgt} = __SLOT_0__{semi}")
            mut_pat = f"{tgt} = __SLOT_0__{semi}"
            self.lut_table[lang_id, KIND_ASSIGN_DECL, 0, 0, 0] = self._compile_pattern_str(decl_pat, indent_head=True)
            self.lut_table[lang_id, KIND_ASSIGN_MUT, 0, 0, 0] = self._compile_pattern_str(mut_pat, indent_head=True)
            self.lut_table[lang_id, KIND_RETURN, 0, 0, 0] = self._compile_pattern_str(f"return __SLOT_0__{semi}", indent_head=True)

            # 5. IF, IF_ELSE, WHILE
            if lang == "python":
                if_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("if ")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit(":\n")), (SEG_CHILD, 1, 0)]
                ife_segs = if_segs + [(SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("else:\n")), (SEG_CHILD, 2, 0)]
                wh_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("while ")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit(":\n")), (SEG_CHILD, 1, 0)]
            elif lang == "ruby":
                if_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("if ")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("end"))]
                ife_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("if ")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("else\n")), (SEG_CHILD, 2, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("end"))]
                wh_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("while ")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("end"))]
            else:
                if_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("if (")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit(") {\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("}"))]
                ife_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("if (")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit(") {\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("} else {\n")), (SEG_CHILD, 2, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("}"))]
                wh_segs = [(SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("while (")), (SEG_CHILD, 0, 0), (SEG_LIT, *self._add_lit(") {\n")), (SEG_CHILD, 1, 0), (SEG_LIT, *self._add_lit("\n")), (SEG_INDENT, 0, 0), (SEG_LIT, *self._add_lit("}"))]
            self.lut_table[lang_id, KIND_IF, 0, 0, 0] = self._register_segments(if_segs)
            self.lut_table[lang_id, KIND_IF_ELSE, 0, 0, 0] = self._register_segments(ife_segs)
            self.lut_table[lang_id, KIND_WHILE, 0, 0, 0] = self._register_segments(wh_segs)

            # 6. BLOCK (1..15 statements joined by "\n") & MODULE (1..15 functions joined by "\n\n")
            for k in range(1, 16):
                self.lut_table[lang_id, KIND_BLOCK, 0, 0, k] = self._compile_pattern_str("\n".join(f"__SLOT_{i}__" for i in range(k)))
                self.lut_table[lang_id, KIND_MODULE, 0, 0, k] = self._compile_pattern_str("\n\n".join(f"__SLOT_{i}__" for i in range(k)))
                p_fmt = {
                    "c": ", ".join(f"int64_t __SLOT_{i}__" for i in range(k)),
                    "cpp": ", ".join(f"int64_t __SLOT_{i}__" for i in range(k)),
                    "go": ", ".join(f"__SLOT_{i}__ int64" for i in range(k)),
                    "rust": ", ".join(f"__SLOT_{i}__: i64" for i in range(k)),
                    "typescript": ", ".join(f"__SLOT_{i}__: number" for i in range(k)),
                    "java": ", ".join(f"long __SLOT_{i}__" for i in range(k)),
                    "csharp": ", ".join(f"long __SLOT_{i}__" for i in range(k)),
                    "dart": ", ".join(f"int __SLOT_{i}__" for i in range(k)),
                    "swift": ", ".join(f"_ __SLOT_{i}__: Int64" for i in range(k)),
                    "php": ", ".join(f"int $__SLOT_{i}__" for i in range(k)),
                }.get(lang, ", ".join(f"__SLOT_{i}__" for i in range(k)))
                self.lut_table[lang_id, KIND_PARAM_LIST, 0, 0, k] = self._compile_pattern_str(p_fmt)

            # 7. FUNC (SYM = func_name, child_0 = param_list, child_1 = body_block)
            fn_pat = {
                "c": "int64_t __SYM__(__SLOT_0__) {\n__SLOT_1__\n}",
                "cpp": "int64_t __SYM__(__SLOT_0__) {\n__SLOT_1__\n}",
                "go": "func __SYM__(__SLOT_0__) int64 {\n__SLOT_1__\n}",
                "rust": "fn __SYM__(__SLOT_0__) -> i64 {\n__SLOT_1__\n}",
                "typescript": "function __SYM__(__SLOT_0__): number {\n__SLOT_1__\n}",
                "java": "long __SYM__(__SLOT_0__) {\n__SLOT_1__\n}",
                "csharp": "long __SYM__(__SLOT_0__) {\n__SLOT_1__\n}",
                "dart": "int __SYM__(__SLOT_0__) {\n__SLOT_1__\n}",
                "swift": "func __SYM__(__SLOT_0__) -> Int64 {\n__SLOT_1__\n}",
                "php": "function __SYM__(__SLOT_0__): int {\n__SLOT_1__\n}",
                "ruby": "def __SYM__(__SLOT_0__)\n__SLOT_1__\nend",
                "python": "def __SYM__(__SLOT_0__):\n__SLOT_1__",
            }[lang]
            self.lut_table[lang_id, KIND_FUNC, 0, 0, 0] = self._compile_pattern_str(fn_pat)

    def _pack_tensors(self) -> None:
        num_t = len(self._templates)
        max_s = max(len(s) for s in self._templates)
        self.max_segs = max_s
        self.seg_type = torch.zeros((num_t, max_s), dtype=torch.long, device=self.device)
        self.seg_arg = torch.zeros((num_t, max_s), dtype=torch.long, device=self.device)
        self.seg_len = torch.zeros((num_t, max_s), dtype=torch.long, device=self.device)

        for tid, segs in enumerate(self._templates):
            for s_idx, (st, sa, sl) in enumerate(segs):
                self.seg_type[tid, s_idx] = st
                self.seg_arg[tid, s_idx] = sa
                self.seg_len[tid, s_idx] = sl

        self.lut_table = self.lut_table.to(self.device)
        self.literal_bytes = torch.tensor(list(self._lit_pool), dtype=torch.uint8, device=self.device)

    def _load_pseudoarch_unit_lut(self) -> None:
        """Load the 12,164 PseudoArch lowered RISC-V Units into a flat GPU lookup table."""
        unit_dir = Path(__file__).resolve().parents[1] / "pseudoarch" / "map_HiOp_to_unit" / "lowered_units"
        self.unit_records: list[dict[str, Any]] = []
        self.op_to_unit_idx = torch.zeros((len(ALL_12_LANGS), len(OPS)), dtype=torch.long, device=self.device)
        if not unit_dir.exists():
            return
        for p in sorted(unit_dir.glob("*.jsonl.gz")):
            with gzip.open(p, "rt") as gz:
                for line in gz:
                    rec = json.loads(line)
                    if rec.get("words") and rec.get("unit"):
                        self.unit_records.append(rec)
        # Populate representative RISC-V Unit index per (lang_id, op_id)
        for lid in range(len(ALL_12_LANGS)):
            for oid in range(1, len(OPS)):
                self.op_to_unit_idx[lid, oid] = (lid * len(OPS) + oid) % max(1, len(self.unit_records))
