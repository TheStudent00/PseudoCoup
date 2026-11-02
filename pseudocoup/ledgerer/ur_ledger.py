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


TIER1_EXACT_OPS = {
    "+", "-", "*", "&", "|", "^", "==", "!=", "<", "<=", ">", ">=",
    "ite", "&&", "||", "neg", "not", "trunc_div", "trunc_rem",
}


def build_ur_node(lang: str, op_symbol: str, holder: str = "i64", guarded: bool = False) -> UniversalRichNode:
    if op_symbol in TIER1_EXACT_OPS or guarded:
        meaning = {
            "tier": 1, "D_ok": "True", "D_trap": "False",
            "R_val": f"tier1_{op_symbol}_{holder}", "guarded": True,
        }
    elif op_symbol in ("<<", ">>"):
        r_val = f"saturate_64_{op_symbol}" if lang in ("go", "swift") else f"mask_63_{op_symbol}"
        meaning = {"tier": 2, "D_ok": "0 <= b < 64", "D_trap": "b < 0", "R_val": r_val, "guarded": False}
    elif op_symbol in ("/", "//", "%"):
        if lang in ("python", "ruby"):
            r_val = "floor_div" if op_symbol in ("/", "//") else "floor_mod"
        else:
            r_val = "trunc_div" if op_symbol in ("/", "//") else "trunc_rem"
        meaning = {"tier": 2, "D_ok": "b != 0", "D_trap": "b == 0", "R_val": r_val, "guarded": False}
    else:
        meaning = {"tier": 1, "D_ok": "True", "D_trap": "False", "R_val": op_symbol, "guarded": True}

    opcode_map = {
        "+": "add", "-": "sub", "*": "mul", "/": "div", "//": "div", "%": "rem",
        "trunc_div": "div", "trunc_rem": "rem",
        "&": "and", "|": "or", "^": "xor", "<<": "sll", ">>": "sra",
        "==": "seqz", "!=": "snez", "<": "slt", "<=": "slt", ">": "slt", ">=": "slt", "ite": "beq",
    }
    mnem = opcode_map.get(op_symbol, "add")
    return UniversalRichNode(
        hiop={"lang": lang, "operator": op_symbol, "holders": (holder, holder)},
        units={"riscv64": [{"opcode": mnem, "text": f"{mnem} a0, a0, a1"}]},
        meaning=meaning,
    )


def build_holder_cast_node(expr: Any, src_holder: str, dst_holder: str, lang: str = "hub") -> URHolderCast:
    sz1, _, sg1 = RISCV64_HOLDER_LAYOUT.get(src_holder, (8, 8, True))
    sz2, _, sg2 = RISCV64_HOLDER_LAYOUT.get(dst_holder, (8, 8, True))
    if src_holder == dst_holder:
        kind = "identity"
        lo_op = "mv"
    elif sz1 == sz2 and sg1 != sg2:
        kind = "rule3_reinterpretation_sext_zext"
        lo_op = "addiw" if (sz2 == 4 and sg2) else "slli;srli"
    else:
        kind = "width_conversion_trunc_ext"
        lo_op = "addiw" if (sz2 == 4 and sg2) else "andi"
    ur_node = UniversalRichNode(
        hiop={"lang": lang, "operator": f"cast_{src_holder}_to_{dst_holder}", "holders": (src_holder, dst_holder)},
        units={"riscv64": [{"opcode": lo_op, "text": f"{lo_op} a0, a0"}]},
        meaning={"tier": 1, "D_ok": "True", "D_trap": "False", "R_val": kind, "guarded": True},
    )
    return URHolderCast(ur_node=ur_node, expr=expr, src_holder=src_holder, dst_holder=dst_holder, bridge_kind=kind)



def _is_bitmask_63(expr_node: Any) -> bool:
    return (
        isinstance(expr_node, URHiOpCall)
        and expr_node.op_symbol == "&"
        and len(expr_node.args) == 2
        and isinstance(expr_node.args[1], URConst)
        and expr_node.args[1].value == 63
    )


def _normalize_inline_cond_and_div(ln: str, lang: str) -> str:
    """Normalize native inline conditionals (`? :`, Rust `if/else`, Go IIFE) into Python `IfExp`."""
    # Go IIFE: func() int64 { if COND { return THEN } else { return ELSE } }()
    ln = re.sub(
        r"func\(\)\s*\w+\s*\{\s*if\s+(.*?)\s*\{\s*return\s+(.*?)\s*\}\s*else\s*\{\s*return\s+(.*?)\s*\}\s*\}\(\)",
        r"(\2 if \1 else \3)",
        ln,
    )
    # Rust inline if: (if COND { THEN } else { ELSE })
    ln = re.sub(
        r"\(\s*if\s+(.*?)\s*\{\s*(.*?)\s*\}\s*else\s*\{\s*(.*?)\s*\}\s*\)",
        r"(\2 if \1 else \3)",
        ln,
    )
    # C/C++/Java/TS/C#/Dart/Swift/PHP/Ruby ternary: ((COND) ? (THEN) : (ELSE))
    if "?" in ln and ":" in ln:
        ln = _convert_balanced_ternary(ln)
    # Python/Ruby native truncated remainder `(a - (int(a / b) * b))` -> `trunc_rem(a, b)`
    ln = re.sub(r"\(\s*([A-Za-z0-9_]+)\s*-\s*\(\s*int\(\s*\1\s*/\s*([A-Za-z0-9_]+)\s*\)\s*\*\s*\2\s*\)\s*\)", r"trunc_rem(\1, \2)", ln)
    # Python/Ruby native truncated division `int(a / b)` -> `trunc_div(a, b)`
    ln = re.sub(r"int\(\s*([A-Za-z0-9_]+)\s*/\s*([A-Za-z0-9_]+)\s*\)", r"trunc_div(\1, \2)", ln)
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
            ln = _normalize_inline_cond_and_div(ln, lang)
            ln = ln.replace("&&", " and ").replace("||", " or ")
            if ln.startswith("if ") or ln.startswith("if("):
                cond = re.sub(r"^if\s*\(?(.*?)\)?\s*(?:\{|:)?$", r"\1", ln)
                body_lines.append("    " * indent + f"if {cond}:")
                indent += 1
            elif ln.startswith("while ") or ln.startswith("while("):
                cond = re.sub(r"^while\s*\(?(.*?)\)?\s*(?:\{|:)?$", r"\1", ln)
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
                if s.is_decl:
                    if s.holder in ("u32", "i32", "u16", "i16", "u8", "i8"):
                        target_h = s.holder
                    else:
                        target_h = expr_h
                    s.holder = target_h
                    known_holders[s.target] = target_h
                    fn.locals[s.target] = HolderDecl.from_type(s.target, target_h)
                    if (target_h in ("u32", "i32", "u16", "i16", "u8", "i8") and isinstance(s.expr, URHiOpCall)) or target_h != expr_h:
                        s.expr = build_holder_cast_node(s.expr, "i64", target_h)
                else:
                    target_h = known_holders.get(s.target, s.holder)
                    s.holder = target_h
                    if (target_h in ("u32", "i32", "u16", "i16", "u8", "i8") and isinstance(s.expr, URHiOpCall)) or target_h != expr_h:
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
        if isinstance(expr, (URVar, URConst)):
            return expr
        if isinstance(expr, URHolderCast):
            inner = cls.canonicalize_expr(expr.expr, target_lang)
            if expr.src_holder == expr.dst_holder or expr.dst_holder in ("i64", "u64"):
                return inner
            sz, _, signed = RISCV64_HOLDER_LAYOUT.get(expr.dst_holder, (8, 8, True))
            bits = sz * 8
            mask = URConst((1 << bits) - 1, expr.dst_holder)
            sign_bit = URConst(1 << (bits - 1), expr.dst_holder)

            def t1_c(op: str, *ops: Any) -> URHiOpCall:
                return URHiOpCall(build_ur_node(target_lang, op, expr.dst_holder, True), list(ops), op, expr.dst_holder)

            masked = t1_c("&", inner, mask)
            if not signed:
                return masked
            return t1_c("-", t1_c("^", masked, sign_bit), sign_bit)
        if isinstance(expr, URCall):
            return URCall(expr.func_name, [cls.canonicalize_expr(a, target_lang) for a in expr.args], expr.holder)
        if not isinstance(expr, URHiOpCall):
            return expr
        args = [cls.canonicalize_expr(a, target_lang) for a in expr.args]
        meaning = expr.ur_node.meaning
        if meaning.get("guarded", False):
            return URHiOpCall(build_ur_node(target_lang, expr.op_symbol, expr.holder, True), args, expr.op_symbol, expr.holder)

        r_val = meaning.get("R_val", "")
        a, b = args[0], args[1]
        c0 = URConst(0, "i64")
        c64 = URConst(64, "i64")
        c63 = URConst(63, "i64")
        c_min = URConst(-9223372036854775808, "i64")
        c_neg1 = URConst(-1, "i64")

        def t1(op: str, *ops: Any) -> URHiOpCall:
            return URHiOpCall(build_ur_node(target_lang, op, "i64", True), list(ops), op, "i64")

        if r_val == "saturate_64_<<":
            cond = t1("&&", t1(">=", b, c0), t1("<", b, c64))
            return t1("ite", cond, t1("<<", a, t1("&", b, c63)), c0)
        if r_val == "saturate_64_>>":
            cond = t1("&&", t1(">=", b, c0), t1("<", b, c64))
            return t1("ite", cond, t1(">>", a, t1("&", b, c63)), t1(">>", a, t1("&", c63, c63)))
        if r_val in ("mask_63_<<", "mask_63_>>"):
            return t1(expr.op_symbol, a, t1("&", b, c63))
        if r_val == "trunc_div":
            ovf = t1("&&", t1("==", a, c_min), t1("==", b, c_neg1))
            return t1("ite", ovf, c_min, t1("trunc_div", a, b))
        if r_val == "trunc_rem":
            ovf = t1("&&", t1("==", a, c_min), t1("==", b, c_neg1))
            return t1("ite", ovf, c0, t1("trunc_rem", a, b))
        if r_val == "floor_div":
            diff_sign = t1("&&", t1("<", t1("^", a, b), c0), t1("!=", t1("trunc_rem", a, b), c0))
            return t1("ite", diff_sign, t1("-", t1("trunc_div", a, b), URConst(1, "i64")), t1("trunc_div", a, b))
        if r_val == "floor_mod":
            diff_sign = t1("&&", t1("<", t1("^", a, b), c0), t1("!=", t1("trunc_rem", a, b), c0))
            return t1("ite", diff_sign, t1("+", t1("trunc_rem", a, b), b), t1("trunc_rem", a, b))
        return t1(expr.op_symbol, *args)


    @classmethod
    def _emit_expr(cls, expr: Any, lang: str) -> str:
        if isinstance(expr, URConst):
            return str(expr.value)
        if isinstance(expr, URVar):
            return f"${expr.name}" if lang == "php" else expr.name
        if isinstance(expr, URCall):
            args_s = ", ".join(cls._emit_expr(a, lang) for a in expr.args)
            return f"{expr.func_name}({args_s})"
        if isinstance(expr, URHiOpCall):
            op = expr.op_symbol
            if op == "neg":
                return f"(-{cls._emit_expr(expr.args[0], lang)})"
            if op == "ite":
                c, t, e = (cls._emit_expr(a, lang) for a in expr.args)
                if lang == "python":
                    return f"({t} if {c} else {e})"
                if lang == "rust":
                    return f"(if {c} {{ {t} }} else {{ {e} }})"
                if lang == "go":
                    return f"func() int64 {{ if {c} {{ return {t} }} else {{ return {e} }} }}()"
                return f"({c} ? {t} : {e})"
            if op == "trunc_div":
                a, b = cls._emit_expr(expr.args[0], lang), cls._emit_expr(expr.args[1], lang)
                if lang == "python":
                    return f"int({a} / {b})"
                return f"({a} / {b})"
            if op == "trunc_rem":
                a, b = cls._emit_expr(expr.args[0], lang), cls._emit_expr(expr.args[1], lang)
                if lang == "python":
                    return f"({a} - (int({a} / {b}) * {b}))"
                return f"({a} % {b})"
            a, b = cls._emit_expr(expr.args[0], lang), cls._emit_expr(expr.args[1], lang)
            if lang == "python" and op in ("&&", "||"):
                py_op = "and" if op == "&&" else "or"
                return f"({a} {py_op} {b})"
            return f"({a} {op} {b})"
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
            if isinstance(e, URConst): return _s64(e.value)
            if isinstance(e, URVar): return env[e.name]
            if isinstance(e, URHolderCast):
                ce = LedgerToScript.canonicalize_expr(e, "c")
                return ev_expr(ce)
            if isinstance(e, URCall):
                callee = funcs[e.func_name]
                c_args = {p.name: ev_expr(a) for p, a in zip(callee.params, e.args)}
                return run_fn(callee, c_args)
            if isinstance(e, URHiOpCall):
                ce = LedgerToScript.canonicalize_expr(e, "c") if not e.ur_node.meaning.get("guarded") else e
                op = ce.op_symbol
                if op == "neg": return _s64(-ev_expr(ce.args[0]))
                if op == "ite": return ev_expr(ce.args[1]) if ev_expr(ce.args[0]) != 0 else ev_expr(ce.args[2])
                if op == "&&": return 1 if (ev_expr(ce.args[0]) != 0 and ev_expr(ce.args[1]) != 0) else 0
                if op == "||": return 1 if (ev_expr(ce.args[0]) != 0 or ev_expr(ce.args[1]) != 0) else 0
                a, b = ev_expr(ce.args[0]), ev_expr(ce.args[1])
                if op == "+": return _s64(a + b)
                if op == "-": return _s64(a - b)
                if op == "*": return _s64(a * b)
                if op == "&": return _s64(a & b)
                if op == "|": return _s64(a | b)
                if op == "^": return _s64(a ^ b)
                if op == "<<": return _s64(a << (b & 63))
                if op == ">>": return _s64(a >> (b & 63))
                if op == "==": return 1 if a == b else 0
                if op == "!=": return 1 if a != b else 0
                if op == "<": return 1 if a < b else 0
                if op == "<=": return 1 if a <= b else 0
                if op == ">": return 1 if a > b else 0
                if op == ">=": return 1 if a >= b else 0
                if op == "trunc_div":
                    q = abs(a) // abs(b)
                    return _s64(-q if (a < 0) ^ (b < 0) else q)
                if op == "trunc_rem":
                    q = abs(a) // abs(b)
                    q = -q if (a < 0) ^ (b < 0) else q
                    return _s64(a - q * b)
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
