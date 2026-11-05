"""ur_ledger -- Multi-function URLedger, ScriptToLedger, LedgerToScript, and Automated Holder Linking.

Implements:
1. ScriptToLedger: parses multi-function scripts in any of the 12 languages into a URLedger,
   preserving exact parameter/local/return HolderDecls and folding canonical piecewise guards
   back into their semantic UniversalRichNodes.
2. Automated Ledger Linking (link_ledgers): walks URCall edges across functions from different
   languages, compares caller argument holders against callee parameter HolderDecls, and
   automatically splices URHolderCast (UniversalRichNode) bridges into the URLedger.
3. LedgerToScript: emits 100% native, runnable code in any of the 12 Original Languages.
"""
from __future__ import annotations
import ast
import re
from dataclasses import dataclass, field
from typing import Any
import z3
from .universal_rich_node import UniversalRichNode

RISCV64_HOLDER_LAYOUT: dict[str, tuple[int, int, bool]] = {
    "bool": (1, 1, False),
    "i8": (1, 1, True), "u8": (1, 1, False),
    "i16": (2, 2, True), "u16": (2, 2, False),
    "i32": (4, 4, True), "u32": (4, 4, False),
    "i64": (8, 8, True), "u64": (8, 8, False),
}

SURFACE_TO_CANON_HOLDER: dict[str, str] = {
    "int8_t": "i8", "i8": "i8", "int8": "i8", "sbyte": "i8", "Int8": "i8",
    "uint8_t": "u8", "u8": "u8", "uint8": "u8", "byte": "u8", "UInt8": "u8",
    "int16_t": "i16", "i16": "i16", "int16": "i16", "short": "i16", "Int16": "i16",
    "uint16_t": "u16", "u16": "u16", "uint16": "u16", "ushort": "u16", "UInt16": "u16",
    "int32_t": "i32", "i32": "i32", "int32": "i32", "Int32": "i32",
    "uint32_t": "u32", "u32": "u32", "uint32": "u32", "uint": "u32", "UInt32": "u32",
    "int64_t": "i64", "i64": "i64", "int64": "i64", "long": "i64", "int": "i64", "number": "i64", "Int64": "i64",
    "uint64_t": "u64", "u64": "u64", "uint64": "u64", "ulong": "u64", "UInt64": "u64",
}



@dataclass
class HolderDecl:
    name: str
    holder: str = "i64"
    size: int = 8
    align: int = 8
    signed: bool = True

    @classmethod
    def from_type(cls, name: str, holder: str = "i64") -> HolderDecl:
        canon = SURFACE_TO_CANON_HOLDER.get(holder, holder if holder in RISCV64_HOLDER_LAYOUT else "i64")
        sz, al, sg = RISCV64_HOLDER_LAYOUT.get(canon, (8, 8, True))
        return cls(name=name, holder=canon, size=sz, align=al, signed=sg)


@dataclass
class URVar:
    name: str
    holder: str = "i64"


@dataclass
class URConst:
    value: int
    holder: str = "i64"


@dataclass
class URHolderCast:
    """Automatic ledger-level Holder bridge inserted when caller/callee or assignment holders differ."""
    ur_node: UniversalRichNode
    expr: Any
    src_holder: str
    dst_holder: str
    bridge_kind: str

    @property
    def holder(self) -> str:
        return self.dst_holder


@dataclass
class URCall:
    func_name: str
    args: list[Any]
    holder: str = "i64"


@dataclass
class URHiOpCall:
    ur_node: UniversalRichNode
    args: list[Any]
    op_symbol: str
    holder: str = "i64"


@dataclass
class URAssign:
    target: str
    holder: str
    expr: Any
    is_decl: bool = False


@dataclass
class URIf:
    cond: Any
    then_body: list[Any]
    else_body: list[Any] = field(default_factory=list)


@dataclass
class URWhile:
    cond: Any
    body: list[Any]


@dataclass
class URReturn:
    expr: Any


@dataclass
class URFunc:
    func_name: str
    source_lang: str
    params: list[HolderDecl]
    locals: dict[str, HolderDecl]
    return_holder: str
    body: list[Any]


@dataclass
class URLedger:
    """Universal Rich Ledger holding one or more functions (potentially from multiple languages)."""
    func_name: str
    source_lang: str
    params: list[HolderDecl]
    locals: dict[str, HolderDecl]
    return_holder: str
    body: list[Any]
    functions: list[URFunc] = field(default_factory=list)
    bridge_events: list[dict[str, str]] = field(default_factory=list)


CANON_HOLDER_TO_C_TYPE: dict[str, str] = {
    "bool": "_Bool",
    "i8": "signed char",
    "u8": "unsigned char",
    "i16": "short",
    "u16": "unsigned short",
    "i32": "int",
    "u32": "unsigned int",
    "i64": "long",
    "u64": "unsigned long",
}

_UR_NODE_CACHE: dict[tuple[str, str, str, bool], UniversalRichNode] = {}


_LANG_DATASET_UL_CACHE: dict[str, dict[str, Any]] | None = None


def _get_dataset_unit_lean(lang: str, op_symbol: str, holder: str, guarded: bool) -> Any:
    """Look up the real lowered 64-bit `UnitLean` from `Research/lower_HiOp/out/` datasets when available."""
    global _LANG_DATASET_UL_CACHE
    if holder not in ("i64", "u64"):
        return None
    from ..hub.autopoly.polyfill import normalize_target_lang
    from ..hub.autopoly.verify_hiop_primitives import load_language_64bit_unit_leans

    if _LANG_DATASET_UL_CACHE is None:
        _LANG_DATASET_UL_CACHE = load_language_64bit_unit_leans()

    eff_lang = "c" if guarded else normalize_target_lang(lang)
    uls = _LANG_DATASET_UL_CACHE.get(eff_lang, {})
    is_u = holder == "u64"
    prim_map = {
        "+": "BV_ADD",
        "-": "BV_SUB",
        "*": "BV_MUL",
        "&": "BV_AND",
        "|": "BV_OR",
        "^": "BV_XOR",
        "~": "BV_NOT",
        "<<": "BV_SHL",
        ">>>": "BV_LSHR",
        ">>": "BV_LSHR" if is_u else "BV_ASHR",
        "<": "BV_ULT" if is_u else "BV_SLT",
        "trunc_div": "BV_UDIV" if is_u else "BV_SDIV",
        "trunc_rem": "BV_UREM" if is_u else "BV_SREM",
        "/": "BV_UDIV" if is_u else ("PY_FLOORDIV" if eff_lang == "python" else "BV_SDIV"),
        "//": "PY_FLOORDIV" if "PY_FLOORDIV" in uls else "BV_SDIV",
        "%": "BV_UREM" if is_u else ("PY_MOD" if "PY_MOD" in uls else "BV_SREM"),
        "ite": "BV_ITE",
    }
    pkey = prim_map.get(op_symbol)
    if pkey is None:
        return None
    if guarded and op_symbol in ("<<", ">>", ">>>"):
        # Guarded shifts represent already-masked 64-bit shifts (a << (b & 63)); compile via _state_info_0_for_op
        return None
    return uls.get(pkey)


def _state_info_0_for_op(op_symbol: str, holder: str, lang: str = "c", guarded: bool = False) -> Any:
    from PseudoArch.map_HiOp_to_unit.model_lang_parts import Operator
    from PseudoArch.map_HiOp_to_unit.model_lang_parts.context.entry_context import PartState0, StateInfo0

    c_type = CANON_HOLDER_TO_C_TYPE.get(holder, "long")
    if op_symbol == "neg":
        return StateInfo0(
            "c",
            Operator("c", "UnaryOperator.Minus", "-a", ("a",), "ur_ledger"),
            (PartState0("a", c_type),),
        )
    if op_symbol == "ite":
        return StateInfo0(
            "c",
            Operator("c", "ConditionalOperator", "a ? b : c", ("a", "b", "c"), "ur_ledger"),
            (PartState0("a", c_type), PartState0("b", c_type), PartState0("c", c_type)),
        )
    if op_symbol in ("<<", ">>"):
        return StateInfo0(
            "c",
            Operator("c", f"BinaryOperator.{op_symbol}", f"a {op_symbol} (b & 63)", ("a", "b"), "ur_ledger"),
            (PartState0("a", c_type), PartState0("b", c_type)),
        )
    c_op = "/" if op_symbol in ("trunc_div", "//") else ("%" if op_symbol == "trunc_rem" else op_symbol)
    return StateInfo0(
        "c",
        Operator("c", f"BinaryOperator.{c_op}", f"a {c_op} b", ("a", "b"), "ur_ledger"),
        (PartState0("a", c_type), PartState0("b", c_type)),
    )


def build_ur_node(
    lang: str,
    op_symbol: str,
    holder: str = "i64",
    guarded: bool = False,
    unit_lean: Any = None,
    state_info_0: Any = None,
) -> UniversalRichNode:
    if state_info_0 is not None:
        from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
        return UniversalRichNode.from_mapped_hiop(map_state_info_0_to_unit(state_info_0), state_info_0)
    if unit_lean is None:
        cache_key = (lang, op_symbol, holder, guarded)
        if cache_key not in _UR_NODE_CACHE:
            ds_ul = _get_dataset_unit_lean(lang, op_symbol, holder, guarded)
            if ds_ul is not None:
                node = UniversalRichNode(
                    hiop={"lang": lang, "operator": op_symbol, "spelling": op_symbol, "holders": (holder, holder)},
                    units={"riscv64": [{"opcode": l.constructor} for l in ds_ul.loop_leans]},
                    meaning={
                        "unit_lean": ds_ul,
                        "D_ok": str(ds_ul.pieces[0].domain) if len(ds_ul.pieces) == 1 else "piecewise",
                        "D_trap": "False",
                        "R_val": str(ds_ul.combined_term) if ds_ul.combined_term is not None else "",
                        "guarded": guarded,
                    },
                )
            else:
                from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
                s0 = _state_info_0_for_op(op_symbol, holder, lang=lang, guarded=guarded)
                mapped = map_state_info_0_to_unit(s0)
                if mapped.LoHiOp.refusal is not None:
                    raise ValueError(f"build_ur_node({lang!r}, {op_symbol!r}) compiler refusal: {mapped.LoHiOp.refusal}")
                node = UniversalRichNode.from_mapped_hiop(mapped, s0)
                node.hiop["lang"] = lang
                node.hiop["operator"] = op_symbol
                node.hiop["spelling"] = op_symbol
                node.meaning["guarded"] = guarded
            _UR_NODE_CACHE[cache_key] = node
        return _UR_NODE_CACHE[cache_key]
    return UniversalRichNode(
        hiop={"lang": lang, "operator": op_symbol, "holders": (holder, holder)},
        units={"riscv64": [{"opcode": l.constructor} for l in unit_lean.loop_leans]},
        meaning={
            "unit_lean": unit_lean,
            "D_ok": str(unit_lean.pieces[0].domain) if len(unit_lean.pieces) == 1 else "piecewise",
            "D_trap": "False",
            "R_val": str(unit_lean.combined_term) if unit_lean.combined_term is not None else "",
            "guarded": guarded,
        },
    )


def build_holder_cast_node(
    expr: Any, src_holder: str, dst_holder: str, lang: str = "hub", unit_lean: Any = None, state_info_0: Any = None
) -> URHolderCast:
    if state_info_0 is not None:
        from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
        ur_node = UniversalRichNode.from_mapped_hiop(map_state_info_0_to_unit(state_info_0), state_info_0)
    elif unit_lean is not None:
        ur_node = build_ur_node(lang, f"cast_{src_holder}_to_{dst_holder}", dst_holder, True, unit_lean=unit_lean)
    else:
        cache_key = (lang, f"cast_{src_holder}_to_{dst_holder}", dst_holder, True)
        if cache_key not in _UR_NODE_CACHE:
            from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
            from PseudoArch.map_HiOp_to_unit.model_lang_parts import Operator
            from PseudoArch.map_HiOp_to_unit.model_lang_parts.context.entry_context import PartState0, StateInfo0

            dst_c = CANON_HOLDER_TO_C_TYPE.get(dst_holder, "long")
            s0 = StateInfo0(
                "c",
                Operator("c", "CStyleCastExpr", f"(long)(({dst_c})a)", ("a",), "ur_ledger"),
                (PartState0("a", "long"),),
            )
            mapped = map_state_info_0_to_unit(s0)
            _UR_NODE_CACHE[cache_key] = UniversalRichNode.from_mapped_hiop(mapped, s0)
        ur_node = _UR_NODE_CACHE[cache_key]
    return URHolderCast(
        ur_node=ur_node, expr=expr, src_holder=src_holder, dst_holder=dst_holder, bridge_kind="sail_unit_cast"
    )



def _is_bitmask_63(expr_node: Any) -> bool:
    if getattr(expr_node, "_is_masked_slot", False):
        return True
    return (
        isinstance(expr_node, URHiOpCall)
        and expr_node.op_symbol == "&"
        and len(expr_node.args) == 2
        and isinstance(expr_node.args[1], URConst)
        and expr_node.args[1].value == 63
    )


def _normalize_inline_cond_and_div(ln: str, lang: str) -> str:
    """Normalize native inline conditionals (`? :`, Rust `if/else`, Go IIFE) into Python `IfExp`."""
    # Go IIFE (inside-out for arbitrary nesting): func() int64 { if COND { return THEN } else { return ELSE } }()
    go_iife_re = re.compile(
        r"func\(\)\s*\w+\s*\{\s*if\s+([^{}]+?)\s*\{\s*return\s+([^{}]+?)\s*\}\s*else\s*\{\s*return\s+([^{}]+?)\s*\}\s*\}\(\)"
    )
    while go_iife_re.search(ln):
        ln = go_iife_re.sub(r"(\2 if \1 else \3)", ln)
    # Rust inline if (inside-out for arbitrary nesting): (if COND { THEN } else { ELSE })
    rust_if_re = re.compile(
        r"\(\s*if\s+([^{}]+?)\s*\{\s*([^{}]+?)\s*\}\s*else\s*\{\s*([^{}]+?)\s*\}\s*\)"
    )
    while rust_if_re.search(ln):
        ln = rust_if_re.sub(r"(\2 if \1 else \3)", ln)
    # C/C++/Java/TS/C#/Dart/Swift/PHP/Ruby ternary: ((COND) ? (THEN) : (ELSE))
    if "?" in ln and ":" in ln:
        ln = _convert_balanced_ternary(ln)
    # Python native truncated remainder `(a - (int(a / b) * b))` -> `trunc_rem(a, b)`
    ln = re.sub(r"\(\s*([A-Za-z0-9_]+)\s*-\s*\(\s*int\(\s*\1\s*/\s*([A-Za-z0-9_]+)\s*\)\s*\*\s*\2\s*\)\s*\)", r"trunc_rem(\1, \2)", ln)
    # Python native truncated division `int(a / b)` -> `trunc_div(a, b)`
    ln = re.sub(r"int\(\s*([A-Za-z0-9_]+)\s*/\s*([A-Za-z0-9_]+)\s*\)", r"trunc_div(\1, \2)", ln)
    # Dart/Ruby native truncated remainder `(a.remainder(b))` -> `trunc_rem(a, b)`
    ln = re.sub(r"\(\s*([A-Za-z0-9_]+)\.remainder\(\s*([A-Za-z0-9_]+)\s*\)\s*\)", r"trunc_rem(\1, \2)", ln)
    # Ruby native truncated division `(a.fdiv(b).truncate)` -> `trunc_div(a, b)`
    ln = re.sub(r"\(\s*([A-Za-z0-9_]+)\.fdiv\(\s*([A-Za-z0-9_]+)\s*\)\.truncate\s*\)", r"trunc_div(\1, \2)", ln)
    # Dart native truncated division `(a ~/ b)` -> `trunc_div(a, b)`
    ln = re.sub(r"\(\s*([A-Za-z0-9_]+)\s*~/\s*([A-Za-z0-9_]+)\s*\)", r"trunc_div(\1, \2)", ln)
    if lang == "dart":
        ln = ln.replace("~/", "//")
    # PHP native truncated division `intdiv(a, b)` -> `trunc_div(a, b)`
    ln = re.sub(r"intdiv\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)", r"trunc_div(\1, \2)", ln)
    # TypeScript native truncated division `Math.trunc(a / b)` -> `trunc_div(a, b)`
    ln = re.sub(r"Math\.trunc\(\s*([A-Za-z0-9_]+)\s*/\s*([A-Za-z0-9_]+)\s*\)", r"trunc_div(\1, \2)", ln)
    # Rust wrapping_shl / wrapping_shr emitted by HIOP_PRIMITIVES: `.wrapping_shl(B as u32)` -> `<< (B & 63)`
    if lang == "rust":
        ln = re.sub(r"\.wrapping_shl\(\s*([^()]+?)\s+as\s+u32\s*\)", r" << (\1 & 63)", ln)
        ln = re.sub(r"\.wrapping_shr\(\s*([^()]+?)\s+as\s+u32\s*\)", r" >> (\1 & 63)", ln)
    return ln



def _convert_balanced_ternary(s: str) -> str:
    """Convert `(COND ? THEN : ELSE)` with arbitrary nested parentheses into `(THEN if COND else ELSE)`."""
    while "?" in s:
        q_idx = s.find("?")
        # Walk left from q_idx to find the enclosing '(' at depth 0
        depth = 0
        start = -1
        for i in range(q_idx - 1, -1, -1):
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                if depth == 0:
                    start = i
                    break
                depth -= 1
        # Walk right from q_idx + 1 to find matching ':' at depth 0, then closing ')' at depth 0
        depth = 0
        colon_idx = -1
        end = -1
        for i in range(q_idx + 1, len(s)):
            if s[i] == "(":
                depth += 1
            elif s[i] == ")":
                if depth == 0:
                    end = i
                    break
                depth -= 1
            elif s[i] == ":" and depth == 0 and colon_idx == -1:
                colon_idx = i
        if start == -1 or colon_idx == -1 or end == -1:
            break
        cond = s[start + 1 : q_idx].strip()
        then_e = s[q_idx + 1 : colon_idx].strip()
        else_e = s[colon_idx + 1 : end].strip()
        s = s[:start] + f"({then_e} if {cond} else {else_e})" + s[end + 1 :]
    return s



class ScriptToLedger:
    """Parse single- or multi-function scripts in `lang_x` into a `URLedger`."""

    HEADER_RE = re.compile(
        r"^(?:func|fn|def|function|int64_t|uint64_t|int32_t|uint32_t|int16_t|uint16_t|int8_t|uint8_t|long|int|uint)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:->\s*(\w+)|:\s*(\w+)|\s+(\w+))?"
    )

    @classmethod
    def _parse_param_decls(cls, raw_params: str) -> list[HolderDecl]:
        decls: list[HolderDecl] = []
        for p in raw_params.split(","):
            p = p.strip().lstrip("_").strip()
            if not p:
                continue
            tokens = [t.lstrip("$") for t in re.split(r"[\s:]+", p) if t]
            if len(tokens) == 1:
                decls.append(HolderDecl.from_type(tokens[0], "i64"))
            elif tokens[0] in SURFACE_TO_CANON_HOLDER:
                decls.append(HolderDecl.from_type(tokens[1], tokens[0]))
            else:
                decls.append(HolderDecl.from_type(tokens[0], tokens[1]))
        return decls

    @classmethod
    def _extract_return_holder(cls, header: str) -> str:
        first_tok = header.split()[0]
        if first_tok in SURFACE_TO_CANON_HOLDER:
            return SURFACE_TO_CANON_HOLDER[first_tok]
        m = re.search(r"\)\s*(?:->|:)?\s*([A-Za-z0-9_]+)\s*\{?$", header)
        if m and m.group(1) in SURFACE_TO_CANON_HOLDER:
            return SURFACE_TO_CANON_HOLDER[m.group(1)]
        return "i64"


    @classmethod
    def _split_functions(cls, script: str, lang: str) -> list[list[str]]:
        lines = [
            ln.strip() for ln in script.strip().splitlines()
            if ln.strip() and not ln.strip().startswith("//") and not ln.strip().startswith("#")
        ]
        funcs: list[list[str]] = []
        cur: list[str] = []
        for ln in lines:
            if cls.HEADER_RE.match(ln) and cur:
                funcs.append(cur)
                cur = [ln]
            else:
                cur.append(ln)
        if cur:
            funcs.append(cur)
        return funcs

    @classmethod
    def _normalize_func_lines(cls, fn_lines: list[str], lang: str) -> tuple[str, list[HolderDecl], str, str]:
        header = fn_lines[0]
        m = cls.HEADER_RE.match(header)
        func_name = m.group(1) if m else "f"
        raw_params = m.group(2) if m else ""
        param_decls = cls._parse_param_decls(raw_params)
        ret_holder = cls._extract_return_holder(header)

        body_lines: list[str] = []
        indent = 0
        for raw in fn_lines[1:]:
            ln = raw.replace("$", "") if lang == "php" else raw
            ln = ln.rstrip(";").strip()
            if ln == "else":
                indent = max(0, indent - 1)
                body_lines.append("    " * indent + "else:")
                indent += 1
                continue
            if ln == "}" or ln.startswith("}") or ln == "end":
                indent = max(0, indent - 1)
                if "else" in ln:
                    body_lines.append("    " * indent + "else:")
                    indent += 1
                continue
            ln = re.sub(
                r"^(int64_t|uint64_t|int32_t|uint32_t|int16_t|uint16_t|int8_t|uint8_t|long|int|uint)\s+([A-Za-z_]\w*)\s*=\s*",
                r"\2: \1 = ",
                ln,
            )
            ln = re.sub(
                r"^var\s+([A-Za-z_]\w*)\s+(int64|uint64|int32|uint32|int16|uint16|int8|uint8|int|uint)\s*=\s*",
                r"\1: \2 = ",
                ln,
            )
            ln = re.sub(
                r"^(?:var|let\s+mut|let)\s+([A-Za-z_]\w*)\s*:\s*([A-Za-z0-9_]+)\s*=\s*",
                r"\1: \2 = ",
                ln,
            )
            ln = re.sub(
                r"^(?:var|let\s+mut|let)\s+([A-Za-z_]\w*)\s*=\s*",
                r"\1 = ",
                ln,
            )
            ln = ln.replace(":=", "=")
            ln = re.sub(r"\b(\d+)L\b", r"\1", ln)
            ln = _normalize_inline_cond_and_div(ln, lang)
            ln = ln.replace("&&", " and ").replace("||", " or ")
            if ln.startswith("if ") or ln.startswith("if("):
                cond = re.sub(r"^if\s*(.*?)\s*(?:\{|:)?$", r"\1", ln)
                body_lines.append("    " * indent + f"if {cond}:")
                indent += 1
            elif ln.startswith("while ") or ln.startswith("while("):
                cond = re.sub(r"^while\s*(.*?)\s*(?:\{|:)?$", r"\1", ln)
                body_lines.append("    " * indent + f"while {cond}:")
                indent += 1
            else:
                body_lines.append("    " * indent + ln)
        return func_name, param_decls, ret_holder, "\n".join(body_lines)


    @classmethod
    def parse(cls, script: str, lang: str) -> URLedger:
        ur_funcs: list[URFunc] = []
        if lang == "python":
            norm_py = "\n".join(_normalize_inline_cond_and_div(ln, "python") for ln in script.strip().splitlines())
            mod = ast.parse(norm_py)
            for fn_node in mod.body:
                if not isinstance(fn_node, ast.FunctionDef):
                    continue
                params: list[HolderDecl] = []
                for a in fn_node.args.args:
                    h_type = ast.unparse(a.annotation) if a.annotation else "i64"
                    params.append(HolderDecl.from_type(a.arg, h_type))
                ret_h = SURFACE_TO_CANON_HOLDER.get(ast.unparse(fn_node.returns), "i64") if fn_node.returns else "i64"
                locals_map: dict[str, HolderDecl] = {}
                known = {p.name: p.holder for p in params}
                body = [cls._conv_stmt(s, lang, known, locals_map) for s in fn_node.body]
                ur_funcs.append(URFunc(fn_node.name, lang, params, locals_map, ret_h, body))
        else:
            for fn_lines in cls._split_functions(script, lang):
                fn_name, params, ret_h, py_body = cls._normalize_func_lines(fn_lines, lang)
                mod = ast.parse(py_body)
                locals_map = {}
                known = {p.name: p.holder for p in params}
                body = [cls._conv_stmt(s, lang, known, locals_map) for s in mod.body]
                ur_funcs.append(URFunc(fn_name, lang, params, locals_map, ret_h, body))

        main_fn = ur_funcs[-1]
        return URLedger(
            func_name=main_fn.func_name,
            source_lang=lang,
            params=main_fn.params,
            locals=main_fn.locals,
            return_holder=main_fn.return_holder,
            body=main_fn.body,
            functions=ur_funcs,
        )

    @classmethod
    def _conv_stmt(cls, node: ast.stmt, lang: str, known: dict[str, str], locals_map: dict[str, HolderDecl]) -> Any:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            tgt = node.target.id
            expr = cls._conv_expr(node.value, lang, False, known)
            ann_str = ast.unparse(node.annotation).strip()
            h = SURFACE_TO_CANON_HOLDER.get(ann_str, getattr(expr, "holder", "i64"))
            is_decl = tgt not in known
            known[tgt] = h
            locals_map[tgt] = HolderDecl.from_type(tgt, h)
            return URAssign(target=tgt, holder=h, expr=expr, is_decl=is_decl)
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            tgt = node.targets[0].id
            expr = cls._conv_expr(node.value, lang, False, known)
            h = getattr(expr, "holder", "i64")
            is_decl = tgt not in known
            if is_decl:
                known[tgt] = h
                locals_map[tgt] = HolderDecl.from_type(tgt, h)
            return URAssign(target=tgt, holder=known[tgt], expr=expr, is_decl=is_decl)
        if isinstance(node, ast.If):
            return URIf(
                cond=cls._conv_expr(node.test, lang, False, known),
                then_body=[cls._conv_stmt(s, lang, known, locals_map) for s in node.body],
                else_body=[cls._conv_stmt(s, lang, known, locals_map) for s in node.orelse],
            )
        if isinstance(node, ast.While):
            return URWhile(
                cond=cls._conv_expr(node.test, lang, False, known),
                body=[cls._conv_stmt(s, lang, known, locals_map) for s in node.body],
            )
        if isinstance(node, ast.Return):
            return URReturn(expr=cls._conv_expr(node.value, lang, False, known))
        raise ValueError(f"Unsupported stmt: {ast.dump(node)}")


    @classmethod
    def _conv_expr(cls, node: ast.AST, lang: str, guarded_ctx: bool = False, known: dict[str, str] | None = None) -> Any:
        known = known or {}
        if isinstance(node, ast.Constant):
            return URConst(value=int(node.value), holder="i64")
        if isinstance(node, ast.Name):
            return URVar(name=node.id, holder=known.get(node.id, "i64"))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Constant):
                return URConst(value=-int(node.operand.value), holder="i64")
            arg = cls._conv_expr(node.operand, lang, guarded_ctx, known)
            return URHiOpCall(build_ur_node(lang, "neg", arg.holder, True), [arg], "neg", arg.holder)
        if isinstance(node, ast.IfExp):
            cond = cls._conv_expr(node.test, lang, True, known)
            then_e = cls._conv_expr(node.body, lang, True, known)
            else_e = cls._conv_expr(node.orelse, lang, True, known)
            return URHiOpCall(build_ur_node(lang, "ite", then_e.holder, True), [cond, then_e, else_e], "ite", then_e.holder)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = node.func.id
            if fn == "ite" and len(node.args) == 3:
                args = [cls._conv_expr(a, lang, True, known) for a in node.args]
                return URHiOpCall(build_ur_node(lang, "ite", "i64", True), args, "ite")
            if fn in ("trunc_div", "trunc_rem", "pc_trunc_div", "pc_trunc_rem") and len(node.args) == 2:
                op_norm = "trunc_div" if "div" in fn else "trunc_rem"
                args = [cls._conv_expr(a, lang, True, known) for a in node.args]
                return URHiOpCall(build_ur_node(lang, op_norm, "i64", True), args, op_norm)
            args = [cls._conv_expr(a, lang, guarded_ctx, known) for a in node.args]
            return URCall(func_name=fn, args=args, holder="i64")
        if isinstance(node, ast.BoolOp):
            op_sym = "&&" if isinstance(node.op, ast.And) else "||"
            cur = cls._conv_expr(node.values[0], lang, guarded_ctx, known)
            for v in node.values[1:]:
                rhs = cls._conv_expr(v, lang, guarded_ctx, known)
                cur = URHiOpCall(build_ur_node(lang, op_sym, "i64", True), [cur, rhs], op_sym)
            return cur
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            cmp_map = {
                ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<",
                ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
            }
            op_sym = cmp_map[type(node.ops[0])]
            lhs = cls._conv_expr(node.left, lang, guarded_ctx, known)
            rhs = cls._conv_expr(node.comparators[0], lang, guarded_ctx, known)
            return URHiOpCall(build_ur_node(lang, op_sym, lhs.holder, True), [lhs, rhs], op_sym)
        if isinstance(node, ast.BinOp):
            bin_map = {
                ast.Add: "+", ast.Sub: "-", ast.Mult: "*",
                ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%",
                ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
                ast.LShift: "<<", ast.RShift: ">>",
            }
            op_sym = bin_map[type(node.op)]
            lhs = cls._conv_expr(node.left, lang, guarded_ctx, known)
            rhs = cls._conv_expr(node.right, lang, guarded_ctx, known)
            is_guarded = guarded_ctx or (op_sym in ("<<", ">>") and _is_bitmask_63(rhs))
            if guarded_ctx and op_sym in ("/", "//"):
                op_sym = "trunc_div"
            elif guarded_ctx and op_sym == "%":
                op_sym = "trunc_rem"
            return URHiOpCall(build_ur_node(lang, op_sym, lhs.holder, is_guarded), [lhs, rhs], op_sym, lhs.holder)
        raise ValueError(f"Unsupported expr: {ast.dump(node)}")



def link_ledgers(ledgers: list[URLedger]) -> URLedger:
    """Automatically link multiple URLedgers and splice URHolderCast nodes at holder boundaries."""
    all_funcs: list[URFunc] = []
    func_sig_map: dict[str, URFunc] = {}
    for ldg in ledgers:
        for fn in ldg.functions:
            all_funcs.append(fn)
            func_sig_map[fn.func_name] = fn

    bridge_events: list[dict[str, str]] = []

    def link_expr(e: Any, caller_fn: str, known_holders: dict[str, str]) -> Any:
        if isinstance(e, URConst):
            return e
        if isinstance(e, URVar):
            e.holder = known_holders.get(e.name, e.holder)
            return e
        if isinstance(e, URHolderCast):
            e.expr = link_expr(e.expr, caller_fn, known_holders)
            return e
        if isinstance(e, URHiOpCall):
            e.args = [link_expr(a, caller_fn, known_holders) for a in e.args]
            return e
        if isinstance(e, URCall):
            e.args = [link_expr(a, caller_fn, known_holders) for a in e.args]
            callee = func_sig_map.get(e.func_name)
            if callee is not None:
                e.holder = callee.return_holder
                bridged_args = []
                for idx, (arg_e, p_decl) in enumerate(zip(e.args, callee.params)):
                    src_h = getattr(arg_e, "holder", "i64")
                    dst_h = p_decl.holder
                    if src_h != dst_h:
                        cast_node = build_holder_cast_node(arg_e, src_h, dst_h)
                        bridge_events.append({
                            "site": f"{caller_fn} -> {callee.func_name}(arg {idx}: {p_decl.name})",
                            "from_lang": func_sig_map[caller_fn].source_lang if caller_fn in func_sig_map else "hub",
                            "to_lang": callee.source_lang,
                            "src_holder": src_h,
                            "dst_holder": dst_h,
                            "bridge_kind": cast_node.bridge_kind,
                            "riscv64_lo_op": cast_node.ur_node.units["riscv64"][0]["opcode"],
                        })
                        bridged_args.append(cast_node)
                    else:
                        bridged_args.append(arg_e)
                e.args = bridged_args
            return e
        return e

    def link_stmts(stmts: list[Any], fn: URFunc, known_holders: dict[str, str]) -> list[Any]:
        out = []
        for s in stmts:
            if isinstance(s, URAssign):
                s.expr = link_expr(s.expr, fn.func_name, known_holders)
                expr_h = getattr(s.expr, "holder", "i64")
                explicit_sub64 = s.holder in ("u32", "i32", "u16", "i16", "u8", "i8")
                if s.is_decl:
                    target_h = s.holder if explicit_sub64 else expr_h
                    s.holder = target_h
                    known_holders[s.target] = target_h
                    fn.locals[s.target] = HolderDecl.from_type(s.target, target_h)
                    if explicit_sub64 and isinstance(s.expr, URHiOpCall):
                        s.expr = build_holder_cast_node(s.expr, "i64", target_h)
                else:
                    target_h = known_holders.get(s.target, s.holder)
                    s.holder = target_h
                    if (target_h in ("u32", "i32", "u16", "i16", "u8", "i8") and isinstance(s.expr, URHiOpCall)):
                        s.expr = build_holder_cast_node(s.expr, "i64", target_h)
                out.append(s)
            elif isinstance(s, URIf):
                s.cond = link_expr(s.cond, fn.func_name, known_holders)
                s.then_body = link_stmts(s.then_body, fn, known_holders)
                s.else_body = link_stmts(s.else_body, fn, known_holders)
                out.append(s)
            elif isinstance(s, URWhile):
                s.cond = link_expr(s.cond, fn.func_name, known_holders)
                s.body = link_stmts(s.body, fn, known_holders)
                out.append(s)
            elif isinstance(s, URReturn):
                s.expr = link_expr(s.expr, fn.func_name, known_holders)
                expr_h = getattr(s.expr, "holder", "i64")
                if expr_h != fn.return_holder or (fn.return_holder in ("u32", "i32", "u16", "i16", "u8", "i8") and isinstance(s.expr, URHiOpCall)):
                    src_cast_h = "i64" if expr_h == fn.return_holder else expr_h
                    cast_node = build_holder_cast_node(s.expr, src_cast_h, fn.return_holder)
                    bridge_events.append({
                        "site": f"{fn.func_name} return",
                        "from_lang": fn.source_lang,
                        "to_lang": fn.source_lang,
                        "src_holder": expr_h,
                        "dst_holder": fn.return_holder,
                        "bridge_kind": cast_node.bridge_kind,
                        "riscv64_lo_op": cast_node.ur_node.units["riscv64"][0]["opcode"],
                    })
                    s.expr = cast_node
                out.append(s)
        return out

    for fn in all_funcs:
        kh = {p.name: p.holder for p in fn.params}
        fn.body = link_stmts(fn.body, fn, kh)

    main_fn = all_funcs[-1]
    return URLedger(
        func_name=main_fn.func_name,
        source_lang=main_fn.source_lang,
        params=main_fn.params,
        locals=main_fn.locals,
        return_holder=main_fn.return_holder,
        body=main_fn.body,
        functions=all_funcs,
        bridge_events=bridge_events,
    )



class LedgerToScript:
    """Walk a URLedger, canonicalize via Hub AutoPoly, and emit native target_lang source code."""

    @classmethod
    def canonicalize_expr(cls, expr: Any, target_lang: str) -> Any:
        from ..hub.autopoly import EquivalenceProver

        if isinstance(expr, (URVar, URConst)):
            return expr
        if isinstance(expr, URHolderCast):
            inner = cls.canonicalize_expr(expr.expr, target_lang)
            if expr.ur_node.meaning.get("unit_lean") is None:
                raise ValueError(
                    f"URHolderCast({expr.src_holder!r} -> {expr.dst_holder!r}) lacks Sail-derived 'unit_lean'; refusing fallback."
                )
            return URHolderCast(expr.ur_node, inner, expr.src_holder, expr.dst_holder, expr.bridge_kind)
        if isinstance(expr, URCall):
            return URCall(expr.func_name, [cls.canonicalize_expr(a, target_lang) for a in expr.args], expr.holder)
        if not isinstance(expr, URHiOpCall):
            return expr
        args = [cls.canonicalize_expr(a, target_lang) for a in expr.args]
        meaning = expr.ur_node.meaning
        if meaning.get("unit_lean") is None:
            raise ValueError(
                f"URHiOpCall({expr.op_symbol!r}) in canonicalize_expr lacks Sail-derived 'unit_lean'; refusing silent string-table fallback."
            )
        h = expr.holder
        if not meaning.get("guarded") and len(args) == 2:
            vocab_ops = (
                "trunc_div",
                "trunc_rem",
                "<<",
                ">>",
                "+",
                "-",
                "*",
                "&",
                "|",
                "^",
                "==",
                "!=",
                "<",
                "<=",
                ">",
                ">=",
                "&&",
                "||",
            )
            matched_op: str | None = None
            matched_cand: UniversalRichNode | None = None
            matched_proof: dict[str, Any] | None = None
            tier2_fallback: tuple[str, UniversalRichNode, dict[str, Any]] | None = None

            for cand_op in vocab_ops:
                cand = build_ur_node(target_lang, cand_op, h, True)
                proof = EquivalenceProver.prove_domain_range_partition(expr.ur_node, cand)
                if proof.get("equivalent"):
                    matched_op, matched_cand, matched_proof = cand_op, cand, proof
                    break
                if proof.get("tier") == "tier2_piecewise_hiop" and tier2_fallback is None:
                    tier2_fallback = (cand_op, cand, proof)

            if matched_cand is None and tier2_fallback is not None:
                matched_op, matched_cand, matched_proof = tier2_fallback

            if matched_op is not None and matched_cand is not None and matched_proof is not None:
                plan = matched_proof.get("composition_plan") or {}
                steps = matched_proof.get("residual_steps") or ()
                needs_mask63 = plan.get("kind") == "arg1_mask_63" or any(
                    st["guard"]["kind"] == "shift_out_of_bounds" for st in steps
                )
                eff_rhs = (
                    (
                        args[1]
                        if _is_bitmask_63(args[1])
                        else URHiOpCall(build_ur_node(target_lang, "&", h, True), [args[1], URConst(63, h)], "&", h)
                    )
                    if needs_mask63
                    else args[1]
                )
                base_call = URHiOpCall(matched_cand, [args[0], eff_rhs], matched_op, h)

                for pg in plan.get("explicit_point_guards") or ():
                    if pg.get("guard", {}).get("kind") == "int64_min_div_neg1":
                        min_val = int(pg["range"]["value"])
                        c_min = URHiOpCall(
                            build_ur_node(target_lang, "==", h, True), [args[0], URConst(min_val, h)], "==", h
                        )
                        c_neg1 = URHiOpCall(
                            build_ur_node(target_lang, "==", h, True), [args[1], URConst(-1, h)], "==", h
                        )
                        cond = URHiOpCall(build_ur_node(target_lang, "&&", h, True), [c_min, c_neg1], "&&", h)
                        base_call = URHiOpCall(
                            build_ur_node(target_lang, "ite", h, True),
                            [cond, URConst(min_val, h), base_call],
                            "ite",
                            h,
                        )

                if matched_proof.get("tier") == "tier2_piecewise_hiop":
                    orig_base = base_call
                    for step in steps:
                        gk = step["guard"]["kind"]
                        if gk == "eq_const" and step["guard"].get("arg") == 1 and step["guard"].get("value") == 0:
                            # Division-by-zero exception return piece from CPython trampoline; non-zero interior uses base/residual
                            continue
                        r_spec = step["range"]
                        rk = r_spec["kind"]
                        if rk == "base_op":
                            op_s = r_spec["op"]
                            rhs_k, rhs_v = r_spec["rhs"]
                            rhs_e = URConst(int(rhs_v), h) if rhs_k == "const" else args[int(rhs_v)]
                            val_call = URHiOpCall(
                                build_ur_node(target_lang, op_s, h, True), [orig_base, rhs_e], op_s, h
                            )
                        elif rk == "const":
                            val_call = URConst(int(r_spec["value"]), h)
                        elif rk == "arg":
                            val_call = args[int(r_spec["index"])]
                        elif rk == "base_const_arg1":
                            val_call = URHiOpCall(
                                matched_cand, [args[0], URConst(int(r_spec["const"]), h)], matched_op, h
                            )
                        else:
                            continue

                        if gk == "shift_out_of_bounds":
                            c_ge0 = URHiOpCall(
                                build_ur_node(target_lang, ">=", h, True), [args[1], URConst(0, h)], ">=", h
                            )
                            c_lt64 = URHiOpCall(
                                build_ur_node(target_lang, "<", h, True), [args[1], URConst(64, h)], "<", h
                            )
                            cond = URHiOpCall(build_ur_node(target_lang, "&&", h, True), [c_ge0, c_lt64], "&&", h)
                            base_call = URHiOpCall(
                                build_ur_node(target_lang, "ite", h, True), [cond, base_call, val_call], "ite", h
                            )
                        elif gk == "opp_sign_rem_nonzero":
                            xor_e = URHiOpCall(build_ur_node(target_lang, "^", h, True), [args[0], args[1]], "^", h)
                            c_sign = URHiOpCall(
                                build_ur_node(target_lang, "<", h, True), [xor_e, URConst(0, h)], "<", h
                            )
                            rem_call = URHiOpCall(
                                build_ur_node(target_lang, "trunc_rem", h, True), [args[0], args[1]], "trunc_rem", h
                            )
                            c_rem = URHiOpCall(
                                build_ur_node(target_lang, "!=", h, True), [rem_call, URConst(0, h)], "!=", h
                            )
                            cond = URHiOpCall(build_ur_node(target_lang, "&&", h, True), [c_sign, c_rem], "&&", h)
                            base_call = URHiOpCall(
                                build_ur_node(target_lang, "ite", h, True), [cond, val_call, base_call], "ite", h
                            )
                        elif gk == "int64_min_div_neg1":
                            min_val = -9223372036854775808
                            c_min = URHiOpCall(
                                build_ur_node(target_lang, "==", h, True), [args[0], URConst(min_val, h)], "==", h
                            )
                            c_neg1 = URHiOpCall(
                                build_ur_node(target_lang, "==", h, True), [args[1], URConst(-1, h)], "==", h
                            )
                            cond = URHiOpCall(build_ur_node(target_lang, "&&", h, True), [c_min, c_neg1], "&&", h)
                            base_call = URHiOpCall(
                                build_ur_node(target_lang, "ite", h, True), [cond, val_call, base_call], "ite", h
                            )
                return base_call

        return URHiOpCall(build_ur_node(target_lang, expr.op_symbol, h, True), args, expr.op_symbol, h)

    @staticmethod
    def _format_target_hiop(op_symbol: str, lang: str, lhs_s: str, rhs_s: str, third_s: str) -> str:
        if op_symbol == "ite":
            if lang == "python":
                return f"({rhs_s} if {lhs_s} else {third_s})"
            if lang == "rust":
                return f"(if {lhs_s} {{ {rhs_s} }} else {{ {third_s} }})"
            if lang == "go":
                return f"func() int64 {{ if {lhs_s} {{ return {rhs_s} }} else {{ return {third_s} }} }}()"
            return f"({lhs_s} ? {rhs_s} : {third_s})"
        if op_symbol == "&&":
            return f"({lhs_s} and {rhs_s})" if lang == "python" else f"({lhs_s} && {rhs_s})"
        if op_symbol == "||":
            return f"({lhs_s} or {rhs_s})" if lang == "python" else f"({lhs_s} || {rhs_s})"
        if op_symbol == "neg":
            return f"-{lhs_s}"
        if op_symbol in ("trunc_div", "/", "//"):
            return f"int({lhs_s} / {rhs_s})" if lang == "python" else f"({lhs_s} / {rhs_s})"
        if op_symbol in ("trunc_rem", "%"):
            return f"({lhs_s} - (int({lhs_s} / {rhs_s}) * {rhs_s}))" if lang == "python" else f"({lhs_s} % {rhs_s})"
        return f"({lhs_s} {op_symbol} {rhs_s})"

    @classmethod
    def _format_holder_cast(cls, dst_holder: str, lang: str, arg_s: str) -> str:
        if dst_holder == "u32":
            return cls._format_target_hiop("&", lang, arg_s, "4294967295", "0")
        if dst_holder == "u16":
            return cls._format_target_hiop("&", lang, arg_s, "65535", "0")
        if dst_holder == "u8":
            return cls._format_target_hiop("&", lang, arg_s, "255", "0")
        if dst_holder in ("i32", "i16", "i8"):
            mask_s, sign_s = (
                ("4294967295", "2147483648")
                if dst_holder == "i32"
                else (("65535", "32768") if dst_holder == "i16" else ("255", "128"))
            )
            masked = cls._format_target_hiop("&", lang, arg_s, mask_s, "0")
            xored = cls._format_target_hiop("^", lang, masked, sign_s, "0")
            return cls._format_target_hiop("-", lang, xored, sign_s, "0")
        return arg_s

    @classmethod
    def _emit_expr(cls, expr: Any, lang: str) -> str:
        from ..hub.autopoly import AutoPoly

        if isinstance(expr, URConst):
            return str(expr.value)
        if isinstance(expr, URVar):
            return f"${expr.name}" if lang == "php" else expr.name
        if isinstance(expr, URCall):
            args_s = ", ".join(cls._emit_expr(a, lang) for a in expr.args)
            return f"{expr.func_name}({args_s})"
        if isinstance(expr, URHolderCast):
            arg_s = cls._emit_expr(expr.expr, lang)
            cand_hiop = dict(expr.ur_node.hiop)
            cand_hiop["lang"] = lang
            cand_hiop["target_code"] = cls._format_holder_cast(expr.dst_holder, lang, arg_s)
            cand = UniversalRichNode(hiop=cand_hiop, units=expr.ur_node.units, meaning=expr.ur_node.meaning)
            return AutoPoly().emit_target_code(
                expr.ur_node, lang, arg_s, "0", candidate_target_nodes=[cand]
            )["code"]
        if isinstance(expr, URHiOpCall):
            lhs_s = cls._emit_expr(expr.args[0], lang) if len(expr.args) >= 1 else "0"
            rhs_s = cls._emit_expr(expr.args[1], lang) if len(expr.args) >= 2 else "0"
            third_s = cls._emit_expr(expr.args[2], lang) if len(expr.args) >= 3 else "0"
            base_cand = build_ur_node(lang, expr.op_symbol, expr.holder, True)
            cand_hiop = dict(base_cand.hiop)
            cand_hiop["target_code"] = cls._format_target_hiop(expr.op_symbol, lang, lhs_s, rhs_s, third_s)
            cand = UniversalRichNode(hiop=cand_hiop, units=base_cand.units, meaning=base_cand.meaning)
            return AutoPoly().emit_target_code(
                expr.ur_node, lang, lhs_s, rhs_s, candidate_target_nodes=[cand], third=third_s
            )["code"]
        raise ValueError(f"Unknown expr: {expr}")

    @classmethod
    def _emit_stmt(cls, stmt: Any, lang: str, indent: int = 1) -> list[str]:
        pad = "    " * indent
        semi = ";" if lang in ("c", "cpp", "rust", "typescript", "java", "csharp", "dart", "php") else ""
        if isinstance(stmt, URAssign):
            rhs = cls._emit_expr(cls.canonicalize_expr(stmt.expr, lang), lang)
            tgt = f"${stmt.target}" if lang == "php" else stmt.target
            if stmt.is_decl:
                if lang in ("c", "cpp"): return [f"{pad}int64_t {tgt} = {rhs};"]
                if lang == "go": return [f"{pad}{tgt} := {rhs}"]
                if lang == "rust": return [f"{pad}let mut {tgt}: i64 = {rhs};"]
                if lang == "typescript": return [f"{pad}let {tgt}: number = {rhs};"]
                if lang in ("java", "csharp"): return [f"{pad}long {tgt} = {rhs};"]
                if lang == "dart": return [f"{pad}int {tgt} = {rhs};"]
                if lang == "swift": return [f"{pad}var {tgt}: Int64 = {rhs}"]
            return [f"{pad}{tgt} = {rhs}{semi}"]
        if isinstance(stmt, URIf):
            c = cls._emit_expr(cls.canonicalize_expr(stmt.cond, lang), lang)
            if lang == "python":
                out = [f"{pad}if {c}:"]
                for s in stmt.then_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                if stmt.else_body:
                    out.append(f"{pad}else:")
                    for s in stmt.else_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                return out
            if lang == "ruby":
                out = [f"{pad}if {c}"]
                for s in stmt.then_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                if stmt.else_body:
                    out.append(f"{pad}else")
                    for s in stmt.else_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                out.append(f"{pad}end")
                return out
            out = [f"{pad}if ({c}) {{"]
            for s in stmt.then_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
            if stmt.else_body:
                out.append(f"{pad}}} else {{")
                for s in stmt.else_body: out.extend(cls._emit_stmt(s, lang, indent + 1))
            out.append(f"{pad}}}")
            return out
        if isinstance(stmt, URWhile):
            c = cls._emit_expr(cls.canonicalize_expr(stmt.cond, lang), lang)
            if lang == "python":
                out = [f"{pad}while {c}:"]
                for s in stmt.body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                return out
            if lang == "ruby":
                out = [f"{pad}while {c}"]
                for s in stmt.body: out.extend(cls._emit_stmt(s, lang, indent + 1))
                out.append(f"{pad}end")
                return out
            out = [f"{pad}while ({c}) {{"]
            for s in stmt.body: out.extend(cls._emit_stmt(s, lang, indent + 1))
            out.append(f"{pad}}}")
            return out
        if isinstance(stmt, URReturn):
            r = cls._emit_expr(cls.canonicalize_expr(stmt.expr, lang), lang)
            return [f"{pad}return {r}{semi}"]
        raise ValueError(f"Unknown stmt: {stmt}")


    @classmethod
    def emit_func(cls, fn: URFunc, target_lang: str) -> str:
        p_names = [p.name for p in fn.params]
        if target_lang in ("c", "cpp"):
            hdr = f"int64_t {fn.func_name}({', '.join('int64_t ' + n for n in p_names)}) {{"
        elif target_lang == "go":
            hdr = f"func {fn.func_name}({', '.join(n + ' int64' for n in p_names)}) int64 {{"
        elif target_lang == "rust":
            hdr = f"fn {fn.func_name}({', '.join(n + ': i64' for n in p_names)}) -> i64 {{"
        elif target_lang == "typescript":
            hdr = f"function {fn.func_name}({', '.join(n + ': number' for n in p_names)}): number {{"
        elif target_lang in ("java", "csharp"):
            hdr = f"long {fn.func_name}({', '.join('long ' + n for n in p_names)}) {{"
        elif target_lang == "dart":
            hdr = f"int {fn.func_name}({', '.join('int ' + n for n in p_names)}) {{"
        elif target_lang == "swift":
            hdr = f"func {fn.func_name}({', '.join('_ ' + n + ': Int64' for n in p_names)}) -> Int64 {{"
        elif target_lang == "php":
            hdr = f"function {fn.func_name}({', '.join('int $' + n for n in p_names)}): int {{"
        elif target_lang == "ruby":
            hdr = f"def {fn.func_name}({', '.join(p_names)})"
        else:
            hdr = f"def {fn.func_name}({', '.join(p_names)}):"
        lines = [hdr]
        for s in fn.body:
            lines.extend(cls._emit_stmt(s, target_lang, 1))
        if target_lang == "ruby":
            lines.append("end")
        elif target_lang != "python":
            lines.append("}")
        return "\n".join(lines)

    @classmethod
    def emit(cls, ledger: URLedger, target_lang: str) -> str:
        funcs = ledger.functions or [
            URFunc(ledger.func_name, ledger.source_lang, ledger.params, ledger.locals, ledger.return_holder, ledger.body)
        ]
        return "\n\n".join(cls.emit_func(fn, target_lang) for fn in funcs)


def _s64(v: int) -> int:
    v &= 0xFFFFFFFFFFFFFFFF
    return v - (1 << 64) if v >= (1 << 63) else v


def eval_ledger(ledger: URLedger, args: dict[str, int], entry_func: str | None = None) -> int:
    """Execute a multi-function URLedger directly on 64-bit two's-complement integers."""
    funcs = {fn.func_name: fn for fn in ledger.functions} if ledger.functions else {
        ledger.func_name: URFunc(ledger.func_name, ledger.source_lang, ledger.params, ledger.locals, ledger.return_holder, ledger.body)
    }
    target_fn = funcs[entry_func or ledger.func_name]

    def run_fn(fn: URFunc, fn_args: dict[str, int]) -> int:
        env = {k: _s64(v) for k, v in fn_args.items()}

        def ev_expr(e: Any) -> int:
            from ..hub import Hub

            if isinstance(e, URConst): return _s64(e.value)
            if isinstance(e, URVar): return env[e.name]
            if isinstance(e, URHolderCast):
                return Hub().eval_node(e.ur_node, ev_expr(e.expr), 0)
            if isinstance(e, URCall):
                callee = funcs[e.func_name]
                c_args = {p.name: ev_expr(a) for p, a in zip(callee.params, e.args)}
                return run_fn(callee, c_args)
            if isinstance(e, URHiOpCall):
                a_v = ev_expr(e.args[0]) if len(e.args) >= 1 else 0
                b_v = ev_expr(e.args[1]) if len(e.args) >= 2 else 0
                c_v = ev_expr(e.args[2]) if len(e.args) >= 3 else 0
                return Hub().eval_node(e.ur_node, a_v, b_v, c_v)
            raise ValueError(f"Cannot eval {e}")

        def ev_stmts(stmts: list[Any]) -> int | None:
            for s in stmts:
                if isinstance(s, URAssign):
                    env[s.target] = ev_expr(s.expr)
                elif isinstance(s, URIf):
                    r = ev_stmts(s.then_body if ev_expr(s.cond) != 0 else s.else_body)
                    if r is not None: return r
                elif isinstance(s, URWhile):
                    while ev_expr(s.cond) != 0:
                        r = ev_stmts(s.body)
                        if r is not None: return r
                elif isinstance(s, URReturn):
                    return ev_expr(s.expr)
            return None

        res = ev_stmts(fn.body)
        return 0 if res is None else res

    return run_fn(target_fn, args)
