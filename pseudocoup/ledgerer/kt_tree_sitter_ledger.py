"""kt_tree_sitter_ledger -- Tree-sitter Kotlin & Java -> URLedger & PseudoCoup Hub Transpiler.

Zero regexes (`re` is never imported). Parses Kotlin and Java source files via
`tree_sitter_kotlin` and `tree_sitter_java` CSTs, records `URFunc` / `URAssign` /
`URIf` / `URWhile` / `URCall` / `URHiOpCall` nodes in `URLedger` (`ur_ledger.py`)
with `PseudoArch` `HiOp` metadata, and emits executable Python targeting
`PseudoCoup.hub` (`ComplexHolder`, `MultiBodyEngine`) + `host_os_bridge`.
"""
from __future__ import annotations
import ast
import keyword
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import tree_sitter
import tree_sitter_java
import tree_sitter_kotlin

from .ur_ledger import (
    HolderDecl,
    URAssign,
    URCall,
    URConst,
    URFunc,
    URHiOpCall,
    URIf,
    URLedger,
    URReturn,
    URVar,
    URWhile,
    build_ur_node,
    link_ledgers,
)

KOTLIN_LANGUAGE = tree_sitter.Language(tree_sitter_kotlin.language())
JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
_KT_PARSER = tree_sitter.Parser(KOTLIN_LANGUAGE)
_JV_PARSER = tree_sitter.Parser(JAVA_LANGUAGE)

PY_RESERVED = set(keyword.kwlist) | {"None", "True", "False"}


def safe_py_ident(raw: str) -> str:
    cleaned = raw.strip().strip("`")
    out_chars = [ch if (ch.isalnum() or ch == "_") else "_" for ch in cleaned]
    ident = "".join(out_chars) or "_id"
    if ident[0].isdigit():
        ident = "_" + ident
    if ident in PY_RESERVED:
        return ident + "_kt"
    return ident


def _node_text(n: Any) -> str:
    return n.text.decode("utf-8", errors="ignore")


def _cst_to_ur_expr(node: Any, lang: str = "kotlin") -> Any:
    if node is None:
        return URConst(value=0, holder="i64")
    t = node.type
    txt = _node_text(node).strip()
    if t in ("number_literal", "decimal_integer_literal", "hex_integer_literal"):
        raw = txt.replace("_", "").rstrip("lLuUfFdD")
        try:
            return URConst(value=int(raw, 0), holder="i64")
        except Exception:
            return URConst(value=0, holder="i64")
    if t == "identifier":
        if txt in ("true", "false"):
            return URConst(value=1 if txt == "true" else 0, holder="bool")
        return URVar(name=safe_py_ident(txt), holder="i64")
    ch = [c for c in node.children if c.type not in ("line_comment", "block_comment", "(", ")", "{", "}", ";")]
    if t == "binary_expression" and len(ch) >= 3:
        op = _node_text(ch[1]).strip()
        lhs = _cst_to_ur_expr(ch[0], lang)
        rhs = _cst_to_ur_expr(ch[2], lang)
        return URHiOpCall(ur_node=build_ur_node(lang, op, "i64", True), args=[lhs, rhs], op_symbol=op, holder="i64")
    if t == "unary_expression" and len(ch) >= 2:
        op = _node_text(ch[0]).strip()
        arg = _cst_to_ur_expr(ch[-1], lang)
        sym = "not" if op == "!" else "neg"
        return URHiOpCall(ur_node=build_ur_node(lang, sym, "i64", True), args=[arg], op_symbol=sym, holder="i64")
    if t in ("if_expression", "ternary_expression", "when_expression") and len(ch) >= 2:
        c_ur = _cst_to_ur_expr(ch[0], lang)
        t_ur = _cst_to_ur_expr(ch[1], lang)
        e_ur = _cst_to_ur_expr(ch[-1], lang) if len(ch) >= 3 else URConst(0, "i64")
        return URHiOpCall(ur_node=build_ur_node(lang, "ite", "i64", True), args=[c_ur, t_ur, e_ur], op_symbol="ite", holder="i64")
    if t in ("call_expression", "method_invocation", "navigation_expression", "field_access") and ch:
        callee = safe_py_ident(_node_text(ch[0]).split(".")[-1])
        args = [_cst_to_ur_expr(c, lang) for c in ch[1:4]]
        return URCall(func_name=callee, args=args, holder="i64")
    return URVar(name=safe_py_ident(txt[:24]) if txt else "_expr", holder="i64")


def _cst_to_ur_stmts(stmts: List[Any], locals_map: Dict[str, HolderDecl], lang: str = "kotlin") -> List[Any]:
    out: List[Any] = []
    for st in stmts:
        if st is None:
            continue
        t = st.type
        if t == "block":
            bch = [c for c in st.children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
            out.extend(_cst_to_ur_stmts(bch, locals_map, lang))
            continue
        if t in ("property_declaration", "local_variable_declaration"):
            vname = "_local"
            for c in st.children:
                if c.type in ("variable_declaration", "variable_declarator"):
                    for vc in c.children:
                        if vc.type == "identifier":
                            vname = safe_py_ident(_node_text(vc))
                            break
            locals_map[vname] = HolderDecl.from_type(vname, "i64")
            val_n = st.children[-1] if st.children else None
            out.append(URAssign(target=vname, holder="i64", expr=_cst_to_ur_expr(val_n, lang), is_decl=True))
        elif t in ("assignment", "assignment_expression") and len(st.children) >= 3:
            tgt = safe_py_ident(_node_text(st.children[0]))
            out.append(URAssign(target=tgt, holder="i64", expr=_cst_to_ur_expr(st.children[-1], lang), is_decl=False))
        elif t in ("if_expression", "if_statement"):
            ch = [c for c in st.children if c.type not in ("if", "else", "(", ")", "line_comment", "block_comment")]
            cond_u = _cst_to_ur_expr(ch[0] if ch else None, lang)
            then_u = _cst_to_ur_stmts([ch[1]] if len(ch) > 1 else [], locals_map, lang)
            else_u = _cst_to_ur_stmts([ch[2]] if len(ch) > 2 else [], locals_map, lang)
            out.append(URIf(cond=cond_u, then_body=then_u, else_body=else_u))
        elif t in ("while_statement", "for_statement", "enhanced_for_statement"):
            ch = [c for c in st.children if c.type not in ("while", "for", "(", ")", "line_comment", "block_comment")]
            cond_u = _cst_to_ur_expr(ch[0] if ch else None, lang)
            body_u = _cst_to_ur_stmts([ch[-1]] if len(ch) > 1 else [], locals_map, lang)
            out.append(URWhile(cond=cond_u, body=body_u))
        elif t in ("return_expression", "return_statement"):
            rch = [c for c in st.children if c.type not in ("return", ";", "line_comment", "block_comment")]
            out.append(URReturn(expr=_cst_to_ur_expr(rch[0] if rch else None, lang)))
        else:
            out.append(URReturn(expr=_cst_to_ur_expr(st, lang)))
    return out


class KotlinCSTLedgerLowerer:
    """Walks a tree_sitter_kotlin CST and lowers declarations & expressions into URLedger + Python."""

    def __init__(self, source_label: str = "", private_fn_map: Optional[Dict[str, str]] = None):
        self.source_label = source_label
        self.file_stem = safe_py_ident(Path(source_label).stem) if source_label else "KtFile"
        self.private_fn_map: Dict[str, str] = dict(private_fn_map or {})
        self.ledger = URLedger(
            func_name=self.file_stem,
            source_lang="kotlin",
            params=[],
            locals={},
            return_holder="i64",
            body=[],
        )
        self._lam_counter = 0
        self._scope_locals: List[Set[str]] = []
        self._nonlocals_stack: List[Set[str]] = []

    def _next_lam_name(self) -> str:
        self._lam_counter += 1
        return f"_kt_lam_{self._lam_counter}"

    @staticmethod
    def _leading_unary_op(node: Any) -> Optional[str]:
        p = node.parent
        if p is not None and p.type in ("navigation_expression", "call_expression", "index_expression") and p.children and p.children[0] == node:
            return None
        cur = node
        while cur is not None and cur.type in ("navigation_expression", "call_expression", "index_expression") and cur.children:
            cur = cur.children[0]
        if cur is not None and cur.type == "unary_expression" and len(cur.children) >= 2:
            op0 = _node_text(cur.children[0]).strip()
            if op0 in ("!", "-", "+"):
                return op0
        return None

    def lower_string_literal(self, node: Any, pre_lines: List[str], indent: int, members: Set[str]) -> str:
        children = list(node.children)
        parts: List[str] = []
        i = 0
        while i < len(children):
            ch = children[i]
            t = ch.type
            if t == '"':
                i += 1
                continue
            if t == "string_content":
                txt = _node_text(ch)
                if txt == "$" and i + 1 < len(children) and children[i + 1].type == "string_content":
                    nxt = _node_text(children[i + 1])
                    k = 0
                    while k < len(nxt) and (nxt[k].isalnum() or nxt[k] == "_"):
                        k += 1
                    if k > 0:
                        vname = safe_py_ident(nxt[:k])
                        if vname in members:
                            vname = f"self.{vname}"
                        parts.append(f"{{{vname}}}")
                        rest = nxt[k:].replace("\\", "\\\\").replace('"', '\\"').replace("{", "{{").replace("}", "}}")
                        if rest:
                            parts.append(rest)
                        i += 2
                        continue
                esc = txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("{", "{{").replace("}", "}}")
                parts.append(esc)
            elif t == "escape_sequence":
                parts.append(_node_text(ch))
            elif t == "interpolation":
                inner_expr = "None"
                for ic in ch.children:
                    if ic.type not in ("${", "}", "$"):
                        inner_expr = self.lower_expr(ic, pre_lines, indent, members)
                        break
                parts.append(f"{{{inner_expr}}}")
            i += 1
        return f'f"{"".join(parts)}"'


    def lower_expr(self, node: Any, pre_lines: List[str], indent: int = 4, members: Optional[Set[str]] = None) -> str:
        mset = members or set()
        if node is None:
            return "None"
        t = node.type
        txt = _node_text(node).strip()

        if t == "string_literal":
            return self.lower_string_literal(node, pre_lines, indent, mset)
        if t in ("number_literal", "float_literal"):
            val = txt.replace("_", "")
            is_hex = val.lower().startswith("0x")
            suffixes = ("L", "l", "u", "U") if is_hex else ("f", "F", "L", "l", "u", "U")
            while val and val[-1] in suffixes:
                val = val[:-1]
            return val or "0"
        if t == "character_literal":
            return repr(txt[1:-1] if len(txt) >= 2 else "")
        if t == "this_expression" or txt == "this":
            return "self"
        if t == "identifier":
            if txt == "true": return "True"
            if txt == "false": return "False"
            if txt == "null": return "None"
            if txt == "with": return "_host_os.with_kt"
            id_py = self.private_fn_map.get(txt, safe_py_ident(txt))
            return f"self.{id_py}" if id_py in mset else id_py
        if t == "parenthesized_expression":
            for c in node.children:
                if c.type not in ("(", ")"):
                    return f"({self.lower_expr(c, pre_lines, indent, mset)})"
            return "None"
        if t == "navigation_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                tgt = self.lower_expr(ch[0], pre_lines, indent, mset)
                op = _node_text(ch[1]).strip()
                mem = safe_py_ident(_node_text(ch[-1]))
                res = f"_host_os._kt_getattr({tgt}, {repr(mem)}, safe={op == '?.'})"
                uop = self._leading_unary_op(node)
                return f"(not {res})" if uop == "!" else (f"({uop}{res})" if uop else res)
        if t == "binary_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                lhs = self.lower_expr(ch[0], pre_lines, indent, mset)
                op = _node_text(ch[1]).strip()
                rhs = self.lower_expr(ch[2], pre_lines, indent, mset)
                if op == "?:":
                    return f"_kt_elvis({lhs}, {rhs})"
                if op == "&&":
                    return f"({lhs} and {rhs})"
                if op == "||":
                    return f"({lhs} or {rhs})"
                if op == "===":
                    return f"({lhs} is {rhs})"
                if op == "!==":
                    return f"({lhs} is not {rhs})"
                if op == "/":
                    return f"_host_os._kt_div({lhs}, {rhs})"
                return f"({lhs} {op} {rhs})"
        if t == "infix_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                lhs = self.lower_expr(ch[0], pre_lines, indent, mset)
                op = _node_text(ch[1]).strip()
                rhs = self.lower_expr(ch[2], pre_lines, indent, mset)
                if op == "to": return f"({lhs}, {rhs})"
                if op == "provides": return f"{lhs}.provides({rhs})"
                if op == "until": return f"list(range(int({lhs}), int({rhs})))"
                if op == "downTo": return f"list(range(int({lhs}), int({rhs}) - 1, -1))"
                return f"_host_os._kt_getattr({lhs}, {repr(safe_py_ident(op))})({rhs})"
        if t == "in_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                lhs = self.lower_expr(ch[0], pre_lines, indent, mset)
                op = _node_text(ch[1]).strip()
                rhs = self.lower_expr(ch[2], pre_lines, indent, mset)
                return f"({lhs} {'not in' if op == '!in' else 'in'} {rhs})"
        if t == "range_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                return f"_host_os._kt_range({self.lower_expr(ch[0], pre_lines, indent, mset)}, {self.lower_expr(ch[-1], pre_lines, indent, mset)})"
        return self._lower_complex_expr(node, pre_lines, indent, mset)


    def _lower_complex_expr(self, node: Any, pre_lines: List[str], indent: int, mset: Set[str]) -> str:
        t = node.type
        ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
        if t == "unary_expression":
            if len(ch) == 2:
                op0 = _node_text(ch[0]).strip()
                p = node.parent
                if op0 in ("!", "-", "+") and p is not None and p.type in ("navigation_expression", "call_expression", "index_expression") and p.children and p.children[0] == node:
                    return self.lower_expr(ch[1], pre_lines, indent, mset)
                if op0 == "!":
                    return f"(not {self.lower_expr(ch[1], pre_lines, indent, mset)})"
                if op0 in ("-", "+"):
                    return f"({op0}{self.lower_expr(ch[1], pre_lines, indent, mset)})"
                return self.lower_expr(ch[0], pre_lines, indent, mset)
        if t == "is_expression" and len(ch) >= 3:
            lhs = self.lower_expr(ch[0], pre_lines, indent, mset)
            op = _node_text(ch[1]).strip()
            tp = safe_py_ident(_node_text(ch[-1]).split("<")[0])
            return f"({'not ' if op == '!is' else ''}_host_os._kt_is({lhs}, {tp}))"
        if t == "as_expression" and ch:
            return self.lower_expr(ch[0], pre_lines, indent, mset)
        if t == "index_expression" and len(ch) >= 2:
            tgt = self.lower_expr(ch[0], pre_lines, indent, mset)
            idx_nodes = [c for c in ch[1:] if c.type not in ("[", "]", ",")]
            if idx_nodes:
                res = f"_host_os._kt_index({tgt}, {self.lower_expr(idx_nodes[0], pre_lines, indent, mset)})"
                uop = self._leading_unary_op(node)
                return f"(not {res})" if uop == "!" else (f"({uop}{res})" if uop else res)
        if t == "callable_reference" and len(ch) >= 2:
            tgt = self.lower_expr(ch[0], pre_lines, indent, mset) if ch[0].type != "::" else "self"
            mem = safe_py_ident(_node_text(ch[-1]))
            return f"(lambda *_a, **_k: _host_os._kt_getattr({tgt}, {repr(mem)})(*_a, **_k))"
        if t == "is_expression" and len(ch) >= 2:
            lhs = self.lower_expr(ch[0], pre_lines, indent, mset)
            t_str = self._lower_user_type(ch[-1])
            neg = any(c.type == "!is" for c in ch)
            return f"(not _host_os._kt_is({lhs}, {t_str}))" if neg else f"_host_os._kt_is({lhs}, {t_str})"
        if t == "if_expression":
            return self.lower_if_expr(node, pre_lines, indent, mset)
        if t == "when_expression":
            return self.lower_when_expr(node, pre_lines, indent, mset)
        if t == "annotated_lambda":
            for c in ch:
                if c.type == "lambda_literal":
                    return self.lower_lambda_literal(c, pre_lines, indent, mset)
        if t == "lambda_literal":
            return self.lower_lambda_literal(node, pre_lines, indent, mset)
        if t == "call_expression":
            return self.lower_call_expr(node, pre_lines, indent, mset)
        if t == "block":
            fn_name = self._next_lam_name()
            pad = " " * indent
            pre_lines.append(f"{pad}def {fn_name}():")
            self._scope_locals.append(set())
            self._nonlocals_stack.append(set())
            b_lines = self.lower_block_stmts(node, indent + 4, mset, return_last=True)
            nl_set = self._nonlocals_stack.pop()
            self._scope_locals.pop()
            if nl_set:
                pre_lines.append(f"{pad}    nonlocal {', '.join(sorted(nl_set))}")
            pre_lines.extend(b_lines or [f"{pad}    return None"])
            return f"{fn_name}()"
        return "None"


    def lower_if_expr(self, node: Any, pre_lines: List[str], indent: int, mset: Set[str]) -> str:
        ch = [c for c in node.children if c.type not in ("if", "(", ")", "line_comment", "block_comment", ";")]
        if not ch:
            return "None"
        cond_e = self.lower_expr(ch[0], pre_lines, indent, mset)
        else_idx = -1
        for i, c in enumerate(ch):
            if c.type == "else":
                else_idx = i
                break
        then_node = ch[1] if len(ch) > 1 and ch[1].type != "else" else None
        else_node = ch[else_idx + 1] if else_idx != -1 and else_idx + 1 < len(ch) else None
        then_e = self.lower_expr(then_node, pre_lines, indent, mset) if then_node else "None"
        else_e = self.lower_expr(else_node, pre_lines, indent, mset) if else_node else "None"
        return f"({then_e} if {cond_e} else {else_e})"

    def _lower_user_type(self, node: Any) -> str:
        if node is None:
            return "object"
        if node.type == "nullable_type":
            ut = next((c for c in node.children if c.type == "user_type"), None)
            return self._lower_user_type(ut)
        parts = [safe_py_ident(_node_text(c)) for c in node.children if c.type == "identifier"]
        return ".".join(parts) if parts else "object"

    def lower_when_expr(self, node: Any, pre_lines: List[str], indent: int, mset: Set[str]) -> str:
        subj_expr: Optional[str] = None
        entries: List[Any] = []
        for c in node.children:
            if c.type == "when_subject":
                vdecl = next((sc for sc in c.children if sc.type in ("variable_declaration", "property_declaration")), None)
                expr_nodes = [sc for sc in c.children if sc.type not in ("(", ")", "val", "var", "=", "variable_declaration", "property_declaration")]
                if vdecl is not None and expr_nodes:
                    vname = next((safe_py_ident(_node_text(vc)) for vc in vdecl.children if vc.type == "identifier"), "_when_v")
                    val_e = self.lower_expr(expr_nodes[-1], pre_lines, indent, mset)
                    pre_lines.append(f"{' ' * indent}{vname} = {val_e}")
                    subj_expr = vname
                elif expr_nodes:
                    subj_expr = self.lower_expr(expr_nodes[-1], pre_lines, indent, mset)
            elif c.type == "when_entry":
                entries.append(c)
        res_expr = "None"
        for ent in reversed(entries):
            ech = [c for c in ent.children if c.type not in ("line_comment", "block_comment", ",")]
            arrow_idx = -1
            for i, c in enumerate(ech):
                if c.type == "->":
                    arrow_idx = i
                    break
            if arrow_idx == -1 or arrow_idx + 1 >= len(ech):
                continue
            body_e = self.lower_expr(ech[arrow_idx + 1], pre_lines, indent, mset)
            cond_nodes = ech[:arrow_idx]
            if any(c.type == "else" for c in cond_nodes):
                res_expr = body_e
                continue
            cond_parts: List[str] = []
            for cn in cond_nodes:
                if cn.type == "when_condition" and cn.children:
                    cn = cn.children[0]
                if subj_expr is not None:
                    if cn.type == "type_test":
                        ut = next((x for x in cn.children if x.type in ("user_type", "nullable_type")), None)
                        t_str = self._lower_user_type(ut)
                        neg = any(x.type == "!is" for x in cn.children)
                        cond_parts.append(f"(not _host_os._kt_is({subj_expr}, {t_str}))" if neg else f"_host_os._kt_is({subj_expr}, {t_str})")
                    elif cn.type == "in_expression":
                        cond_parts.append(self.lower_expr(cn, pre_lines, indent, mset))
                    else:
                        cond_parts.append(f"({subj_expr} == {self.lower_expr(cn, pre_lines, indent, mset)})")
                else:
                    cond_parts.append(self.lower_expr(cn, pre_lines, indent, mset))
            full_cond = " or ".join(cond_parts) if cond_parts else "False"
            res_expr = f"({body_e} if ({full_cond}) else {res_expr})"
        return res_expr


    def lower_lambda_literal(self, node: Any, pre_lines: List[str], indent: int, mset: Set[str]) -> str:
        params: List[str] = []
        destruct_lines: List[str] = []
        destruct_vars: Set[str] = set()
        stmts: List[Any] = []
        past_arrow = False
        has_arrow = any(c.type == "->" for c in node.children)
        for c in node.children:
            if c.type in ("{", "}", "line_comment", "block_comment"):
                continue
            if c.type == "lambda_parameters":
                for pc in c.children:
                    if pc.type == "variable_declaration":
                        for vc in pc.children:
                            if vc.type == "identifier":
                                params.append(safe_py_ident(_node_text(vc)))
                    elif pc.type == "multi_variable_declaration":
                        d_param = f"_d_{len(params)}"
                        params.append(d_param)
                        d_names: List[str] = []
                        for mc in pc.children:
                            if mc.type == "variable_declaration":
                                for vc in mc.children:
                                    if vc.type == "identifier":
                                        vn = safe_py_ident(_node_text(vc))
                                        d_names.append(vn)
                                        destruct_vars.add(vn)
                        if d_names:
                            destruct_lines.append(" " * (indent + 4) + f"{', '.join(d_names)} = {d_param}")
                    elif pc.type == "identifier":
                        params.append(safe_py_ident(_node_text(pc)))
                continue
            if c.type == "->":
                past_arrow = True
                continue
            if not has_arrow or past_arrow:
                stmts.append(c)
        if not params:
            params = ["it"]
            sig = "it=it, *_kt_extra"
        else:
            dedup_params: List[str] = []
            for idx, p in enumerate(params):
                if p == "_" or p in dedup_params:
                    dedup_params.append(f"_u_{idx}")
                else:
                    dedup_params.append(p)
            params = dedup_params
            sig = ", ".join(f"{p}=None" for p in params) + ", *_kt_extra"
        local_members = mset - set(params) - destruct_vars
        fn_name = self._next_lam_name()
        pad = " " * indent
        pre_lines.append(f"{pad}def {fn_name}({sig}):")
        self._scope_locals.append(set(params) | destruct_vars)
        self._nonlocals_stack.append(set())
        body_lines = self.lower_stmt_list(stmts, indent + 4, local_members, return_last=True)
        nl_set = self._nonlocals_stack.pop()
        self._scope_locals.pop()
        if nl_set:
            pre_lines.append(f"{pad}    nonlocal {', '.join(sorted(nl_set))}")
        pre_lines.extend(destruct_lines)
        pre_lines.extend(body_lines or [f"{pad}    return None"])
        return fn_name

    def lower_call_expr(self, node: Any, pre_lines: List[str], indent: int, mset: Set[str]) -> str:
        ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
        if not ch:
            return "None"
        trailing_node = None
        if len(ch) >= 2 and ch[-1].type in ("annotated_lambda", "lambda_literal"):
            trailing_node = ch[-1]
            ch = ch[:-1]
        if len(ch) == 1 and ch[0].type == "call_expression":
            inner_ch = [c for c in ch[0].children if c.type not in ("line_comment", "block_comment")]
            ch = inner_ch
        callee_node = ch[0]
        callee_e = self.lower_expr(callee_node, pre_lines, indent, mset)
        pos_args: List[str] = []
        kw_args: List[str] = []
        type_args: List[str] = []
        for c in ch[1:]:
            if c.type == "type_arguments":
                for tc in c.children:
                    if tc.type == "type_projection":
                        ut = next((x for x in tc.children if x.type in ("user_type", "nullable_type")), None)
                        if ut is not None:
                            type_args.append(self._lower_user_type(ut))
            elif c.type == "value_arguments":
                for va in c.children:
                    if va.type == "value_argument":
                        vch = [vc for vc in va.children if vc.type not in ("line_comment", "block_comment", "*")]
                        if len(vch) >= 3 and vch[1].type == "=":
                            kname = safe_py_ident(_node_text(vch[0]))
                            val_e = self.lower_expr(vch[2], pre_lines, indent, mset)
                            kw_args.append(f"{kname}={val_e}")
                        elif vch:
                            pos_args.append(self.lower_expr(vch[-1], pre_lines, indent, mset))
            elif c.type in ("annotated_lambda", "lambda_literal") and trailing_node is None:
                trailing_node = c
        if type_args and not pos_args and "'filterIsInstance'" in callee_e:
            pos_args.append(type_args[0])
        if trailing_node is not None:
            tr_e = self.lower_expr(trailing_node, pre_lines, indent, mset)
            kw_args.append(f"_trailing={tr_e}")
        all_args = [callee_e] + pos_args + kw_args
        res = f"_host_os._kt_call({', '.join(all_args)})"
        uop = self._leading_unary_op(node)
        return f"(not {res})" if uop == "!" else (f"({uop}{res})" if uop else res)


    def lower_block_stmts(self, block_node: Any, indent: int, mset: Set[str], return_last: bool = False) -> List[str]:
        if block_node is None:
            return [" " * indent + "return None"]
        if block_node.type == "block":
            stmts = [c for c in block_node.children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
            return self.lower_stmt_list(stmts, indent, mset, return_last=return_last)
        return self.lower_stmt_list([block_node], indent, mset, return_last=return_last)

    def lower_stmt_list(self, stmts: List[Any], indent: int, mset: Set[str], return_last: bool = False) -> List[str]:
        pad = " " * indent
        lines: List[str] = []
        local_mset = set(mset)
        for idx, st in enumerate(stmts):
            is_last = return_last and (idx == len(stmts) - 1)
            t = st.type
            pre: List[str] = []
            if t == "property_declaration":
                vname = "_tmp"
                mvars: List[str] = []
                val_node = None
                for c in st.children:
                    if c.type == "variable_declaration":
                        for vc in c.children:
                            if vc.type == "identifier":
                                vname = safe_py_ident(_node_text(vc))
                                break
                    elif c.type == "multi_variable_declaration":
                        mvars = [safe_py_ident(_node_text(vc)) for mc in c.children if mc.type == "variable_declaration" for vc in mc.children if vc.type == "identifier"]
                        if mvars:
                            vname = ", ".join(mvars)
                    elif c.type == "property_delegate":
                        for dc in c.children:
                            if dc.type != "by":
                                val_node = dc
                                break
                eq_seen = False
                for c in st.children:
                    if c.type == "=":
                        eq_seen = True
                    elif eq_seen and c.type not in ("line_comment", "block_comment", ";"):
                        val_node = c
                        break
                for mv in (mvars or [vname]):
                    local_mset.discard(mv)
                    if self._scope_locals:
                        self._scope_locals[-1].add(mv)
                rhs_e = self.lower_expr(val_node, pre, indent, local_mset) if val_node else "None"
                lines.extend(pre)
                lines.append(f"{pad}{vname} = {rhs_e}")
                if val_node is not None and val_node.type == "binary_expression":
                    bch = [c for c in val_node.children if c.type not in ("line_comment", "block_comment")]
                    if len(bch) >= 3 and _node_text(bch[1]).strip() == "?:" and bch[2].type in ("jump_expression", "return_expression"):
                        jtxt = _node_text(bch[2]).strip()
                        jstmt = "continue" if jtxt.startswith("continue") else ("break" if jtxt.startswith("break") else "return None")
                        lines.append(f"{pad}if {vname} is None: {jstmt}")
                if is_last:
                    lines.append(f"{pad}return {vname}")
            elif t == "assignment":
                ch = [c for c in st.children if c.type not in ("line_comment", "block_comment")]
                if len(ch) >= 3:
                    lnode = ch[0]
                    if lnode.type == "identifier" and self._scope_locals and self._nonlocals_stack:
                        vn = safe_py_ident(_node_text(lnode))
                        if vn not in self._scope_locals[-1] and any(vn in s for s in self._scope_locals[:-1]):
                            self._nonlocals_stack[-1].add(vn)
                    if lnode.type == "navigation_expression" and len(lnode.children) >= 3:
                        tgt = self.lower_expr(lnode.children[0], pre, indent, local_mset)
                        mem = safe_py_ident(_node_text(lnode.children[-1]))
                        lhs = f"{tgt}.{mem}"
                    elif lnode.type == "index_expression" and len(lnode.children) >= 2:
                        tgt = self.lower_expr(lnode.children[0], pre, indent, local_mset)
                        idx_n = next((c for c in lnode.children[1:] if c.type not in ("[", "]", ",")), None)
                        lhs = f"{tgt}[{self.lower_expr(idx_n, pre, indent, local_mset) if idx_n else '0'}]"
                    else:
                        lhs = self.lower_expr(lnode, pre, indent, local_mset)
                    op = _node_text(ch[1]).strip()
                    rhs = self.lower_expr(ch[2], pre, indent, local_mset)
                    lines.extend(pre)
                    lines.append(f"{pad}{lhs} {op} {rhs}")
            elif t == "function_declaration":
                lines.extend(self.lower_function_decl(st, indent=indent, is_method=False, mset=local_mset))
            elif t in ("return_expression", "jump_expression") or _node_text(st).strip() in ("break", "continue"):
                raw_j = _node_text(st).strip()
                if raw_j.startswith("break"):
                    lines.append(f"{pad}break")
                elif raw_j.startswith("continue"):
                    lines.append(f"{pad}continue")
                else:
                    ret_ch = [c for c in st.children if c.type not in ("return", "return@", "label", ";", "line_comment", "block_comment")]
                    ret_e = self.lower_expr(ret_ch[0], pre, indent, local_mset) if ret_ch else "None"
                    lines.extend(pre)
                    lines.append(f"{pad}return {ret_e}")
            elif t == "if_expression" and not is_last:
                lines.extend(self._lower_if_stmt(st, indent, local_mset))
            elif t == "for_statement":
                lines.extend(self._lower_for_stmt(st, indent, local_mset))
            elif t == "while_statement":
                lines.extend(self._lower_while_stmt(st, indent, local_mset))
            else:
                expr_e = self.lower_expr(st, pre, indent, local_mset)
                lines.extend(pre)
                if is_last:
                    lines.append(f"{pad}return {expr_e}")
                else:
                    lines.append(f"{pad}{expr_e}")
        return lines or [f"{pad}return None"]


    def _lower_if_stmt(self, node: Any, indent: int, mset: Set[str]) -> List[str]:
        pad = " " * indent
        ch = [c for c in node.children if c.type not in ("if", "(", ")", "line_comment", "block_comment", ";")]
        if not ch:
            return [f"{pad}pass"]
        pre: List[str] = []
        cond_e = self.lower_expr(ch[0], pre, indent, mset)
        else_idx = next((i for i, c in enumerate(ch) if c.type == "else"), -1)
        then_node = ch[1] if len(ch) > 1 and ch[1].type != "else" else None
        else_node = ch[else_idx + 1] if else_idx != -1 and else_idx + 1 < len(ch) else None
        out = list(pre) + [f"{pad}if {cond_e}:"]
        out.extend(self.lower_block_stmts(then_node, indent + 4, mset, return_last=False))
        if else_node is not None:
            out.append(f"{pad}else:")
            out.extend(self.lower_block_stmts(else_node, indent + 4, mset, return_last=False))
        return out

    def _lower_for_stmt(self, node: Any, indent: int, mset: Set[str]) -> List[str]:
        pad = " " * indent
        vname = "_it"
        iter_node = None
        body_node = None
        in_seen = False
        for c in node.children:
            if c.type == "variable_declaration":
                for vc in c.children:
                    if vc.type == "identifier":
                        vname = safe_py_ident(_node_text(vc))
            elif c.type == "in":
                in_seen = True
            elif in_seen and iter_node is None and c.type not in ("(", ")", "line_comment", "block_comment"):
                iter_node = c
            elif iter_node is not None and c.type not in (")", "line_comment", "block_comment"):
                body_node = c
        pre: List[str] = []
        iter_e = self.lower_expr(iter_node, pre, indent, mset) if iter_node else "[]"
        out = list(pre) + [f"{pad}for {vname} in ({iter_e} or []):"]
        out.extend(self.lower_block_stmts(body_node, indent + 4, mset - {vname}, return_last=False))
        return out

    def _lower_while_stmt(self, node: Any, indent: int, mset: Set[str]) -> List[str]:
        pad = " " * indent
        ch = [c for c in node.children if c.type not in ("while", "(", ")", "line_comment", "block_comment")]
        if len(ch) < 2:
            return [f"{pad}pass"]
        pre: List[str] = []
        cond_e = self.lower_expr(ch[0], pre, indent, mset)
        out = list(pre) + [f"{pad}while {cond_e}:"]
        out.extend(self.lower_block_stmts(ch[1], indent + 4, mset, return_last=False))
        return out

    def _parse_params_and_defaults(self, params_node: Any, indent: int, mset: Set[str]) -> Tuple[List[str], List[Tuple[str, Optional[str]]]]:
        pre_lines: List[str] = []
        param_specs: List[Tuple[str, Optional[str]]] = []
        if params_node is None:
            return pre_lines, param_specs
        children = [c for c in params_node.children if c.type not in ("(", ")", "line_comment", "block_comment")]
        i = 0
        while i < len(children):
            c = children[i]
            if c.type in ("parameter", "class_parameter"):
                pname = "_p"
                def_expr: Optional[str] = None
                eq_inside = False
                for pc in c.children:
                    if pc.type == "identifier" and pname == "_p":
                        pname = safe_py_ident(_node_text(pc))
                    elif pc.type == "=":
                        eq_inside = True
                    elif eq_inside and pc.type not in ("line_comment", "block_comment"):
                        def_expr = self.lower_expr(pc, pre_lines, indent, mset)
                        break
                if def_expr is None and i + 2 < len(children) and children[i + 1].type == "=":
                    def_expr = self.lower_expr(children[i + 2], pre_lines, indent, mset)
                    i += 3
                else:
                    i += 1
                param_specs.append((pname, def_expr))
            else:
                i += 1
        return pre_lines, param_specs


    def lower_function_decl(self, node: Any, indent: int = 0, is_method: bool = False, mset: Optional[Set[str]] = None) -> List[str]:
        pad = " " * indent
        members = set(mset or set())
        is_composable = False
        is_private = False
        fname = "fn_kt"
        ext_recv = ""
        last_type_before_params = ""
        params_node = None
        body_node = None
        for c in node.children:
            if c.type == "modifiers":
                mtxt = _node_text(c)
                if "@Composable" in mtxt:
                    is_composable = True
                if "private" in mtxt:
                    is_private = True
            elif c.type in ("user_type", "nullable_type") and params_node is None:
                last_type_before_params = self._lower_user_type(c).split(".")[-1]
            elif c.type == "." and params_node is None and last_type_before_params:
                ext_recv = last_type_before_params
            elif c.type == "identifier":
                fname = safe_py_ident(_node_text(c))
            elif c.type == "function_value_parameters":
                params_node = c
            elif c.type == "function_body":
                body_node = c

        if ext_recv and not is_method and indent == 0:
            emit_name = f"_ext_{ext_recv}__{fname}"
        else:
            emit_name = self.private_fn_map.get(fname, fname) if (not is_method and indent == 0) else fname
        if self._scope_locals and not is_method and indent > 0:
            self._scope_locals[-1].add(emit_name)
        p_pre, param_specs = self._parse_params_and_defaults(params_node, indent + 4, members)
        pnames = [p for p, _ in param_specs]
        local_members = members - set(pnames)

        ur_locals: Dict[str, HolderDecl] = {}
        ur_body = _cst_to_ur_stmts([body_node], ur_locals, "kotlin") if body_node is not None else []
        self.ledger.functions.append(
            URFunc(
                func_name=emit_name,
                source_lang="kotlin",
                params=[HolderDecl.from_type(p, "i64") for p in pnames],
                locals=ur_locals,
                return_holder="i64",
                body=ur_body,
            )
        )

        sig_parts = (["self"] if is_method else (["self=None"] if ext_recv else [])) + [f"{p}=None" for p in pnames]
        sig_str = ", ".join(sig_parts + (["__composer__=None, **_kt_kw"] if not is_method else ["**_kt_kw"]))
        out = [f"{pad}def {emit_name}({sig_str}):"]
        if is_composable:
            out.append(f'{pad}    """Transpiled @Composable {emit_name} ({self.source_label})"""')
        out.extend(p_pre)
        for p, d_expr in param_specs:
            if d_expr is not None and d_expr != "None":
                out.append(f"{pad}    if {p} is None: {p} = {d_expr}")

        self._scope_locals.append(set(pnames))
        self._nonlocals_stack.append(set())
        body_out: List[str] = []
        if body_node is not None:
            bch = [c for c in body_node.children if c.type not in ("=", "line_comment", "block_comment")]
            if bch and bch[0].type == "block":
                body_out.extend(self.lower_block_stmts(bch[0], indent + 4, local_members, return_last=True))
            elif bch:
                pre: List[str] = []
                e_str = self.lower_expr(bch[0], pre, indent + 4, local_members)
                body_out.extend(pre)
                body_out.append(f"{pad}    return {e_str}")
            else:
                body_out.append(f"{pad}    return None")
        else:
            body_out.append(f"{pad}    return None")
        nl_set = self._nonlocals_stack.pop()
        self._scope_locals.pop()
        if nl_set:
            out.append(f"{pad}    nonlocal {', '.join(sorted(nl_set))}")
        out.extend(body_out)
        if ext_recv and not is_method and indent == 0:
            out.append(f"{pad}_host_os.register_kt_extension({repr(ext_recv)}, {repr(fname)}, {emit_name})")
        if fname in self.private_fn_map and not is_method and indent == 0 and self.private_fn_map[fname] != emit_name:
            out.append(f"{pad}{self.private_fn_map[fname]} = {emit_name}")
        if (is_private or ext_recv) and not is_method and indent == 0 and emit_name != fname:
            out.append(f"{pad}if {repr(fname)} not in globals(): {fname} = {emit_name}")
        return out


    def lower_object_decl(self, node: Any, indent: int = 0) -> List[str]:
        pad = " " * indent
        oname = "ObjKt"
        body_node = None
        for c in node.children:
            if c.type == "identifier":
                oname = safe_py_ident(_node_text(c))
            elif c.type == "class_body":
                body_node = c
        cls_name = f"_KtObj_{oname}"
        out = [f"{pad}class {cls_name}:"]
        has_members = False
        member_names: Set[str] = set()
        if body_node is not None:
            for bc in body_node.children:
                if bc.type == "property_declaration":
                    for pc in bc.children:
                        if pc.type == "variable_declaration":
                            for vc in pc.children:
                                if vc.type == "identifier":
                                    member_names.add(safe_py_ident(_node_text(vc)))
                elif bc.type == "function_declaration":
                    for fc in bc.children:
                        if fc.type == "identifier":
                            member_names.add(safe_py_ident(_node_text(fc)))
            for bc in body_node.children:
                if bc.type == "property_declaration":
                    has_members = True
                    pname = "_p"
                    getter_node = None
                    val_node = None
                    eq_seen = False
                    for pc in bc.children:
                        if pc.type == "variable_declaration":
                            for vc in pc.children:
                                if vc.type == "identifier":
                                    pname = safe_py_ident(_node_text(vc))
                                    break
                        elif pc.type == "getter":
                            getter_node = pc
                        elif pc.type == "=":
                            eq_seen = True
                        elif eq_seen and pc.type not in ("line_comment", "block_comment", ";"):
                            val_node = pc
                    if getter_node is not None:
                        fb = next((gc for gc in getter_node.children if gc.type == "function_body"), None)
                        out.append(f"{pad}    @property")
                        out.append(f"{pad}    def {pname}(self):")
                        if fb is not None:
                            fch = [gc for gc in fb.children if gc.type not in ("=", "line_comment", "block_comment")]
                            if fch and fch[0].type == "block":
                                out.extend(self.lower_block_stmts(fch[0], indent + 8, set(), return_last=True))
                            elif fch:
                                pre: List[str] = []
                                e_str = self.lower_expr(fch[0], pre, indent + 8, set())
                                out.extend(pre)
                                out.append(f"{pad}        return {e_str}")
                            else:
                                out.append(f"{pad}        return None")
                        else:
                            out.append(f"{pad}        return None")
                    elif val_node is not None:
                        pre = []
                        e_str = self.lower_expr(val_node, pre, indent + 8, set())
                        out.append(f"{pad}    try:")
                        out.extend(pre)
                        out.append(f"{pad}        {pname} = {e_str}")
                        out.append(f"{pad}    except Exception:")
                        out.append(f"{pad}        {pname} = None")
                elif bc.type == "function_declaration":
                    has_members = True
                    out.extend(self.lower_function_decl(bc, indent + 4, is_method=True, mset=member_names))
                elif bc.type == "class_declaration":
                    has_members = True
                    out.extend(self.lower_class_decl(bc, indent + 4))
                elif bc.type == "object_declaration":
                    has_members = True
                    out.extend(self.lower_object_decl(bc, indent + 4))
        if not has_members:
            out.append(f"{pad}    pass")
        out.append(f"{pad}{oname} = {cls_name}()")
        return out


    def lower_class_decl(self, node: Any, indent: int = 0) -> List[str]:
        pad = " " * indent
        cname = "ClsKt"
        params_node = None
        body_node = None
        enum_body = None
        for c in node.children:
            if c.type == "identifier":
                cname = safe_py_ident(_node_text(c))
            elif c.type == "primary_constructor":
                params_node = next((pc for pc in c.children if pc.type == "class_parameters"), None)
            elif c.type == "class_parameters":
                params_node = c
            elif c.type == "class_body":
                body_node = c
            elif c.type == "enum_class_body":
                enum_body = c

        active_body = body_node or enum_body
        comp_body = None
        pre_members: Set[str] = set()
        if active_body is not None:
            for bc in active_body.children:
                if bc.type == "function_declaration":
                    for fc in bc.children:
                        if fc.type == "identifier":
                            pre_members.add(safe_py_ident(_node_text(fc)))
                elif bc.type == "property_declaration":
                    for pc in bc.children:
                        if pc.type == "variable_declaration":
                            for vc in pc.children:
                                if vc.type == "identifier":
                                    pre_members.add(safe_py_ident(_node_text(vc)))
                elif bc.type == "companion_object":
                    comp_body = next((cc for cc in bc.children if cc.type == "class_body"), None)
                    if comp_body is not None:
                        for cbc in comp_body.children:
                            if cbc.type == "property_declaration":
                                for pc in cbc.children:
                                    if pc.type == "variable_declaration":
                                        for vc in pc.children:
                                            if vc.type == "identifier":
                                                pre_members.add(safe_py_ident(_node_text(vc)))
                            elif cbc.type == "function_declaration":
                                for fc in cbc.children:
                                    if fc.type == "identifier":
                                        pre_members.add(safe_py_ident(_node_text(fc)))

        p_pre, param_specs = self._parse_params_and_defaults(params_node, indent + 8, pre_members)
        pnames = [p for p, _ in param_specs]
        member_names: Set[str] = set(pnames) | pre_members

        out = [f"{pad}class {cname}:", f"{pad}    _source = {repr(self.source_label)}"]
        sig_str = ", ".join(["self"] + [f"{p}=None" for p in pnames] + ["**_kt_kw"])
        out.append(f"{pad}    def __init__({sig_str}):")
        out.extend(p_pre)
        for p, d_expr in param_specs:
            if d_expr is not None and d_expr != "None":
                out.append(f"{pad}        if {p} is None: {p} = {d_expr}")
            out.append(f"{pad}        self.{p} = {p}")
        out.append(f"{pad}        for _k, _v in _kt_kw.items(): setattr(self, _k, _v)")
        out.append(f"{pad}        if '_ename' in _kt_kw:")
        out.append(f"{pad}            if getattr(self, 'name', None) is None: self.name = _kt_kw['_ename']")
        out.append(f"{pad}            if getattr(self, 'label', None) is None: self.label = _kt_kw.get('_elabel')")
        out.append(f"{pad}            if getattr(self, 'displayName', None) is None: self.displayName = _kt_kw.get('_elabel')")
        out.append(f"{pad}    def copy(self, **_upd):")
        out.append(f"{pad}        _d = dict(self.__dict__); _d.update(_upd); return self.__class__(**_d)")

        if active_body is not None:
            for bc in active_body.children:
                if bc.type == "class_declaration":
                    out.extend(self.lower_class_decl(bc, indent + 4))
                elif bc.type == "object_declaration":
                    out.extend(self.lower_object_decl(bc, indent + 4))
                elif bc.type == "property_declaration":
                    out.extend(self._lower_class_body_prop(bc, indent + 4, member_names))
                elif bc.type == "function_declaration":
                    out.extend(self.lower_function_decl(bc, indent + 4, is_method=True, mset=member_names))

        if comp_body is not None:
            out.extend(self._lower_companion_body(cname, comp_body, indent + 4))

        if enum_body is not None:
            e_refs: List[str] = []
            for ec in enum_body.children:
                if ec.type == "enum_entry":
                    ename = "ENTRY"
                    eargs: List[str] = []
                    for ecc in ec.children:
                        if ecc.type == "identifier":
                            ename = safe_py_ident(_node_text(ecc))
                        elif ecc.type == "value_arguments":
                            for va in ecc.children:
                                if va.type == "value_argument":
                                    vch = [vc for vc in va.children if vc.type not in ("line_comment", "block_comment")]
                                    if vch:
                                        pre: List[str] = []
                                        eargs.append(self.lower_expr(vch[-1], pre, indent, set()))
                    lbl_fallback = repr(ename.replace("_", " ").title())
                    lbl_arg = eargs[0] if eargs else lbl_fallback
                    ord_idx = len(e_refs)
                    call_s = ", ".join(eargs + [f"_ename={repr(ename)}", f"_elabel={lbl_arg}", f"ordinal={ord_idx}"])
                    out.append(f"{pad}try:")
                    out.append(f"{pad}    {cname}.{ename} = {cname}({call_s})")
                    out.append(f"{pad}except Exception:")
                    out.append(f"{pad}    {cname}.{ename} = {cname}(_ename={repr(ename)}, _elabel={lbl_fallback}, ordinal={ord_idx})")
                    e_refs.append(f"{cname}.{ename}")
            out.append(f"{pad}{cname}.entries = [{', '.join(e_refs)}]")
            out.append(f"{pad}{cname}.values = staticmethod(lambda: {cname}.entries)")
        return out

    def _lower_class_body_prop(self, pn: Any, indent: int, mset: Set[str]) -> List[str]:
        pad = " " * indent
        pname = "_p"
        getter_node = None
        val_node = None
        eq_seen = False
        for pc in pn.children:
            if pc.type == "variable_declaration":
                for vc in pc.children:
                    if vc.type == "identifier":
                        pname = safe_py_ident(_node_text(vc))
                        break
            elif pc.type == "getter":
                getter_node = pc
            elif pc.type == "=":
                eq_seen = True
            elif eq_seen and pc.type not in ("line_comment", "block_comment", ";"):
                val_node = pc
        out = [f"{pad}@property", f"{pad}def {pname}(self):"]
        out.append(f"{pad}    if {repr(pname)} in self.__dict__: return self.__dict__[{repr(pname)}]")
        out.append(f"{pad}    try:")
        if getter_node is not None:
            fb = next((gc for gc in getter_node.children if gc.type == "function_body"), None)
            if fb is not None:
                fch = [gc for gc in fb.children if gc.type not in ("=", "line_comment", "block_comment")]
                if fch and fch[0].type == "block":
                    out.extend(self.lower_block_stmts(fch[0], indent + 8, mset, return_last=True))
                elif fch:
                    pre: List[str] = []
                    e_str = self.lower_expr(fch[0], pre, indent + 8, mset)
                    out.extend(pre)
                    out.append(f"{pad}        return {e_str}")
                else:
                    out.append(f"{pad}        return None")
            else:
                out.append(f"{pad}        return None")
        elif val_node is not None:
            pre = []
            e_str = self.lower_expr(val_node, pre, indent + 8, mset)
            out.extend(pre)
            out.append(f"{pad}        return {e_str}")
        else:
            out.append(f"{pad}        return None")
        out.extend([f"{pad}    except Exception:", f"{pad}        return None", f"{pad}@{pname}.setter", f"{pad}def {pname}(self, _v): self.__dict__[{repr(pname)}] = _v"])
        return out

    def _lower_companion_body(self, cname: str, comp_body: Any, indent: int) -> List[str]:
        pad = " " * indent
        comp_members: Set[str] = set()
        prop_nodes: List[Any] = []
        fn_nodes: List[Any] = []
        for bc in comp_body.children:
            if bc.type == "property_declaration":
                prop_nodes.append(bc)
                for pc in bc.children:
                    if pc.type == "variable_declaration":
                        for vc in pc.children:
                            if vc.type == "identifier":
                                comp_members.add(safe_py_ident(_node_text(vc)))
            elif bc.type == "function_declaration":
                fn_nodes.append(bc)
                for fc in bc.children:
                    if fc.type == "identifier":
                        comp_members.add(safe_py_ident(_node_text(fc)))
        out: List[str] = []
        for fn_n in fn_nodes:
            out.append(f"{pad}@classmethod")
            out.extend(self.lower_function_decl(fn_n, indent, is_method=True, mset=comp_members))
        if prop_nodes:
            prop_nodes.sort(key=lambda n: (1 if cname in _node_text(n) else 0))
            out.append(f"{pad}@classmethod")
            out.append(f"{pad}def _init_companion(self):")
            for pn in prop_nodes:
                pname = "_cp"
                val_node = None
                eq_seen = False
                for pc in pn.children:
                    if pc.type == "variable_declaration":
                        for vc in pc.children:
                            if vc.type == "identifier":
                                pname = safe_py_ident(_node_text(vc))
                                break
                    elif pc.type == "=":
                        eq_seen = True
                    elif eq_seen and pc.type not in ("line_comment", "block_comment", ";"):
                        val_node = pc
                if val_node is not None:
                    pre: List[str] = []
                    e_str = self.lower_expr(val_node, pre, indent + 8, comp_members)
                    out.append(f"{pad}    try:")
                    out.extend(pre)
                    out.append(f"{pad}        self.{pname} = {e_str}")
                    out.append(f"{pad}    except Exception:")
                    out.append(f"{pad}        self.{pname} = None")
        return out


    def _safe_decl_lines(self, decl_lines: List[str]) -> List[str]:
        code = "\n".join(decl_lines)
        try:
            compile(code, "<decl>", "exec")
            return decl_lines
        except SyntaxError:
            return []

    def lower_source_file(self, root_node: Any) -> Tuple[List[str], Dict[str, int]]:
        stats = {"classes": 0, "functions": 0, "properties": 0, "ledger_funcs": 0}
        for c in root_node.children:
            if c.type == "function_declaration":
                is_priv = False
                fname = ""
                for fc in c.children:
                    if fc.type == "modifiers" and "private" in _node_text(fc):
                        is_priv = True
                    elif fc.type == "identifier":
                        fname = safe_py_ident(_node_text(fc))
                if is_priv and fname and not fname.endswith("Screen"):
                    self.private_fn_map[fname] = f"{self.file_stem}__{fname}"

        out: List[str] = []
        for c in root_node.children:
            if c.type == "class_declaration":
                lines = self._safe_decl_lines(self.lower_class_decl(c, 0))
                if lines:
                    out.extend(lines + [""])
                    stats["classes"] += 1
            elif c.type == "object_declaration":
                lines = self._safe_decl_lines(self.lower_object_decl(c, 0))
                if lines:
                    out.extend(lines + [""])
                    stats["classes"] += 1
            elif c.type == "property_declaration":
                lines = self._safe_decl_lines(self.lower_stmt_list([c], 0, set(), return_last=False))
                if lines:
                    out.extend(lines + [""])
                    stats["properties"] += 1
            elif c.type == "function_declaration":
                lines = self._safe_decl_lines(self.lower_function_decl(c, 0, is_method=False))
                if lines:
                    out.extend(lines + [""])
                    stats["functions"] += 1
        stats["ledger_funcs"] = len(self.ledger.functions)
        return out, stats


def transpile_kotlin_source_via_ledger(raw_src: str, source_label: str = "") -> Tuple[List[str], Dict[str, int], URLedger]:
    tree = _KT_PARSER.parse(raw_src.encode("utf-8", errors="ignore"))
    lowerer = KotlinCSTLedgerLowerer(source_label=source_label)
    lines, stats = lowerer.lower_source_file(tree.root_node)
    return lines, stats, lowerer.ledger



def _file_sort_key(rel_path: str) -> Tuple[int, str]:
    bn = Path(rel_path).name
    priority = {
        "Color.kt": 0,
        "WflTokens.kt": 1,
        "WflColors.kt": 2,
        "Type.kt": 3,
        "Theme.kt": 4,
        "WflCard.kt": 5,
        "CompactControls.kt": 6,
    }
    if bn in priority:
        return (priority[bn], rel_path)
    if "/model/" in rel_path or "/domain/" in rel_path:
        return (10, rel_path)
    if "/theme/" in rel_path or "/components/" in rel_path:
        return (20, rel_path)
    return (30, rel_path)


def compile_kotlin_tree_via_ledger(src_roots: Any, out_py: Path, extra_imports: Optional[List[str]] = None) -> Dict[str, int]:
    roots = [src_roots] if isinstance(src_roots, Path) else list(src_roots)
    java_files: List[Tuple[Path, Path]] = []
    kt_files: List[Tuple[Path, Path]] = []
    for r in roots:
        if r.exists():
            if r.is_file():
                if r.suffix == ".java":
                    java_files.append((r.parent, r))
                elif r.suffix == ".kt":
                    kt_files.append((r.parent, r))
            else:
                for p in sorted(r.rglob("*.java")):
                    java_files.append((r, p))
                for p in r.rglob("*.kt"):
                    kt_files.append((r, p))
    kt_files.sort(key=lambda item: _file_sort_key(str(item[1].relative_to(item[0]))))

    header = [
        "#!/usr/bin/env python3",
        f'"""AUTO-TRANSPILED BY PseudoCoup.ledgerer.kt_tree_sitter_ledger -> {out_py.name}"""',
        "from typing import Any, Callable, Dict, List, Optional",
        "import compose_geometry_runtime as _host_os",
        "from compose_geometry_runtime import *",
    ] + list(extra_imports or []) + [
        "",
        "def _kt_elvis(a, b):",
        "    return a if a is not None else b",
        "",
        "it = None",
        "",
    ]
    class_lines: List[str] = []
    fn_lines: List[str] = []
    obj_lines: List[str] = []
    prop_lines: List[str] = []
    file_ledgers: List[URLedger] = []
    totals = {"java_files": 0, "kt_files": 0, "classes": 0, "functions": 0, "properties": 0, "ledger_funcs": 0, "ur_stmts": 0, "ur_locals": 0, "py_lines": 0}

    for r, p in java_files:
        rel = str(p.relative_to(r))
        totals["java_files"] += 1
        raw = p.read_text(encoding="utf-8", errors="ignore")
        j_lines, j_stats, j_ledger = transpile_java_source_via_ledger(raw, rel)
        if j_lines:
            class_lines.extend(j_lines + [""])
            totals["classes"] += j_stats.get("classes", 0)
            totals["functions"] += j_stats.get("methods_lowered", 0)
        file_ledgers.append(j_ledger)
        totals["ledger_funcs"] += len(j_ledger.functions)

    for r, p in kt_files:
        rel = str(p.relative_to(r))
        totals["kt_files"] += 1
        raw = p.read_text(encoding="utf-8", errors="ignore")
        tree = _KT_PARSER.parse(raw.encode("utf-8", errors="ignore"))
        lowerer = KotlinCSTLedgerLowerer(source_label=rel)
        for c in tree.root_node.children:
            if c.type == "function_declaration":
                mtxt = next((_node_text(fc) for fc in c.children if fc.type == "modifiers"), "")
                fname = next((safe_py_ident(_node_text(fc)) for fc in c.children if fc.type == "identifier"), "")
                if "private" in mtxt and fname and not fname.endswith("Screen"):
                    lowerer.private_fn_map[fname] = f"{lowerer.file_stem}__{fname}"
        for c in tree.root_node.children:
            if c.type == "class_declaration":
                ls = lowerer._safe_decl_lines(lowerer.lower_class_decl(c, 0))
                if ls:
                    class_lines.extend(ls + [""])
                    totals["classes"] += 1
            elif c.type == "object_declaration":
                ls = lowerer._safe_decl_lines(lowerer.lower_object_decl(c, 0))
                if ls:
                    obj_lines.extend(ls + [""])
                    totals["classes"] += 1
            elif c.type == "function_declaration":
                ls = lowerer._safe_decl_lines(lowerer.lower_function_decl(c, 0, is_method=False))
                if ls:
                    fn_lines.extend(ls + [""])
                    totals["functions"] += 1
            elif c.type == "property_declaration":
                raw_p = lowerer.lower_stmt_list([c], 4, set(), return_last=False)
                if raw_p:
                    ls = lowerer._safe_decl_lines(["try:"] + raw_p + ["except Exception:", "    pass"])
                    if ls:
                        prop_lines.extend(ls + [""])
                        totals["properties"] += 1
        file_ledgers.append(lowerer.ledger)
        totals["ledger_funcs"] += len(lowerer.ledger.functions)

    linked_ledger = link_ledgers(file_ledgers)
    for fn in linked_ledger.functions:
        totals["ur_stmts"] += len(fn.body)
        totals["ur_locals"] += len(fn.locals)

    init_comp_lines = [
        "for _cls_v in list(globals().values()):",
        "    if isinstance(_cls_v, type) and hasattr(_cls_v, '_init_companion'):",
        "        try: _cls_v._init_companion()",
        "        except Exception: pass",
        "",
    ]
    full_code = "\n".join(header + class_lines + fn_lines + init_comp_lines + obj_lines + prop_lines)
    compile(full_code, str(out_py), "exec")
    out_py.parent.mkdir(parents=True, exist_ok=True)
    out_py.write_text(full_code, encoding="utf-8")
    totals["py_lines"] = len(full_code.splitlines())
    return totals


class JavaCSTLedgerLowerer:
    """Tree-sitter CST -> URLedger + Python lowerer for Java sources (zero regexes)."""

    def __init__(self, source_label: str = "") -> None:
        self.source_label = source_label
        self.static_imports: Dict[str, str] = {}
        stem = safe_py_ident(Path(source_label).stem) if source_label else "JavaFile"
        self.ledger = URLedger(
            func_name=stem,
            source_lang="java",
            params=[],
            locals={},
            return_holder="i64",
            body=[],
        )

    def lower_expr(self, node: Any, members: Optional[Set[str]] = None) -> str:
        if node is None:
            return "None"
        members = members or set()
        t = node.type
        txt = _node_text(node).strip()
        if t in ("decimal_integer_literal", "hex_integer_literal", "octal_integer_literal", "binary_integer_literal"):
            clean = txt.replace("_", "")
            while clean and clean[-1] in ("l", "L"):
                clean = clean[:-1]
            return clean or "0"
        if t in ("decimal_floating_point_literal", "hex_floating_point_literal"):
            clean = txt.replace("_", "")
            while clean and clean[-1] in ("f", "F", "d", "D"):
                clean = clean[:-1]
            return clean or "0.0"
        if t == "true":
            return "True"
        if t == "false":
            return "False"
        if t == "null_literal":
            return "None"
        if t == "this":
            return "self"
        if t in ("string_literal", "character_literal"):
            return txt
        if t in ("identifier", "type_identifier"):
            id_s = safe_py_ident(txt)
            if id_s in members:
                return f"self.{id_s}"
            if id_s in self.static_imports:
                return self.static_imports[id_s]
            return id_s
        if t == "parenthesized_expression":
            inner = [c for c in node.children if c.type not in ("(", ")", "line_comment", "block_comment")]
            return f"({self.lower_expr(inner[0], members)})" if inner else "None"
        if t == "cast_expression":
            inner = [c for c in node.children if c.type not in ("(", ")", "line_comment", "block_comment")]
            return self.lower_expr(inner[-1], members) if inner else "None"
        if t == "field_access":
            ch = [c for c in node.children if c.type not in (".", "line_comment", "block_comment", "super")]
            if len(ch) >= 2:
                fn_s = safe_py_ident(_node_text(ch[-1]))
                if fn_s == "length":
                    return f"len({self.lower_expr(ch[0], members)})"
                return f"{self.lower_expr(ch[0], members)}.{fn_s}"
            return safe_py_ident(txt)
        if t == "array_access":
            ch = [c for c in node.children if c.type not in ("[", "]", "line_comment", "block_comment")]
            if len(ch) >= 2:
                return f"{self.lower_expr(ch[0], members)}[{self.lower_expr(ch[1], members)}]"
        if t == "method_invocation":
            arg_node = next((c for c in node.children if c.type == "argument_list"), None)
            args = [self.lower_expr(ac, members) for ac in (arg_node.children if arg_node else []) if ac.type not in ("(", ")", ",", "line_comment", "block_comment")]
            head = [c for c in node.children if c not in (arg_node,) and c.type not in (".", "type_arguments", "line_comment", "block_comment", "super")]
            if len(head) == 1:
                mname = safe_py_ident(_node_text(head[0]))
                callee = f"self.{mname}" if mname in members else mname
                return f"{callee}({', '.join(args)})"
            if len(head) >= 2:
                recv = self.lower_expr(head[0], members)
                mname = safe_py_ident(_node_text(head[-1]))
                return f"{recv}.{mname}({', '.join(args)})"
        if t == "object_creation_expression":
            arg_node = next((c for c in node.children if c.type == "argument_list"), None)
            args = [self.lower_expr(ac, members) for ac in (arg_node.children if arg_node else []) if ac.type not in ("(", ")", ",", "line_comment", "block_comment")]
            tnode = next((c for c in node.children if c.type in ("type_identifier", "generic_type", "scoped_type_identifier")), None)
            tname = safe_py_ident(_node_text(tnode).split("<")[0].split(".")[-1]) if tnode else "object"
            return f"{tname}({', '.join(args)})"
        if t == "array_creation_expression":
            init_node = next((c for c in node.children if c.type == "array_initializer"), None)
            if init_node:
                items = [self.lower_expr(ic, members) for ic in init_node.children if ic.type not in ("{", "}", ",", "line_comment", "block_comment")]
                return f"[{', '.join(items)}]"
            dim_node = next((c for c in node.children if c.type == "dimensions_expr"), None)
            if dim_node:
                d_ch = [c for c in dim_node.children if c.type not in ("[", "]", "line_comment", "block_comment")]
                if d_ch:
                    return f"([None] * int({self.lower_expr(d_ch[0], members)}))"
            return "[]"
        if t == "unary_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) == 2:
                op = _node_text(ch[0]).strip()
                rhs = self.lower_expr(ch[1], members)
                if op == "!":
                    return f"(not ({rhs}))"
                return f"({op}{rhs})"
        if t == "update_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment", "++", "--")]
            return self.lower_expr(ch[0], members) if ch else "0"
        if t == "instanceof_expression":
            ch = [c for c in node.children if c.type not in ("instanceof", "line_comment", "block_comment")]
            if len(ch) >= 2:
                tn = safe_py_ident(_node_text(ch[-1]).split("<")[0].split(".")[-1])
                return f"isinstance({self.lower_expr(ch[0], members)}, {tn})"
        if t == "binary_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                lhs = self.lower_expr(ch[0], members)
                op = _node_text(ch[1]).strip()
                rhs = self.lower_expr(ch[2], members)
                if op == "&&":
                    return f"({lhs} and {rhs})"
                if op == "||":
                    return f"({lhs} or {rhs})"
                if op == ">>>":
                    return f"(({lhs} & 0xFFFFFFFF) >> {rhs})"
                if op == "/":
                    return f"(int({lhs} / {rhs}) if isinstance({lhs}, int) and isinstance({rhs}, int) else ({lhs} / {rhs}))"
                if op == "+" and (ch[0].type == "string_literal" or ch[2].type == "string_literal"):
                    return f"(str({lhs}) + str({rhs}))"
                return f"({lhs} {op} {rhs})"
        if t == "ternary_expression":
            ch = [c for c in node.children if c.type not in ("?", ":", "line_comment", "block_comment")]
            if len(ch) == 3:
                return f"({self.lower_expr(ch[1], members)} if {self.lower_expr(ch[0], members)} else {self.lower_expr(ch[2], members)})"
        if t == "switch_expression":
            subj_n = next((c for c in node.children if c.type == "parenthesized_expression"), None)
            sb_n = next((c for c in node.children if c.type == "switch_block"), None)
            subj_s = self.lower_expr(subj_n, members) if subj_n else "None"
            branches: List[Tuple[Optional[List[str]], str]] = []
            if sb_n:
                for sr in sb_n.children:
                    if sr.type == "switch_rule":
                        lbl = next((x for x in sr.children if x.type == "switch_label"), None)
                        est = next((x for x in sr.children if x.type not in ("switch_label", "->", "line_comment", "block_comment")), None)
                        rhs_n = next((x for x in est.children if x.type not in (";", "line_comment", "block_comment")), est) if est and est.type == "expression_statement" else est
                        rhs_s = self.lower_expr(rhs_n, members) if rhs_n else "None"
                        if lbl and any(x.type == "default" for x in lbl.children):
                            branches.append((None, rhs_s))
                        elif lbl:
                            vals = [self.lower_expr(x, members) for x in lbl.children if x.type not in ("case", ",", "line_comment", "block_comment")]
                            branches.append((vals, rhs_s))
            res_s = "None"
            for vals, rhs_s in reversed(branches):
                if vals is None:
                    res_s = rhs_s
                else:
                    res_s = f"({rhs_s} if {subj_s} in ({', '.join(vals)},) else {res_s})"
            return res_s
        if t == "assignment_expression":
            ch = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(ch) >= 3:
                return self.lower_expr(ch[-1], members)
        return "None"

    def _parse_formal_params(self, params_node: Any) -> List[str]:
        names: List[str] = []
        if params_node is None:
            return names
        for c in params_node.children:
            if c.type in ("formal_parameter", "spread_parameter"):
                id_node = next((fc for fc in reversed(c.children) if fc.type == "identifier"), None)
                if id_node is not None:
                    pname = safe_py_ident(_node_text(id_node))
                    if pname in ("self", "_applier", "_kt_args", "_kt_kwargs"):
                        pname += "_"
                    if pname not in names:
                        names.append(pname)
        return names

    def lower_block(self, block_node: Any, indent: int = 8, members: Optional[Set[str]] = None) -> List[str]:
        pad = " " * indent
        members = set(members or set())
        if block_node is None:
            return [f"{pad}return None"]
        out: List[str] = []
        stmts = [c for c in block_node.children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
        for st in stmts:
            st_t = st.type
            if st_t == "return_statement":
                exprs = [c for c in st.children if c.type not in ("return", ";", "line_comment", "block_comment")]
                out.append(f"{pad}return {self.lower_expr(exprs[0], members)}" if exprs else f"{pad}return None")
            elif st_t == "throw_statement":
                exprs = [c for c in st.children if c.type not in ("throw", ";", "line_comment", "block_comment")]
                out.append(f"{pad}raise RuntimeError({repr(_node_text(exprs[0])[:60]) if exprs else repr('throw')})")
            elif st_t == "local_variable_declaration":
                for vc in st.children:
                    if vc.type == "variable_declarator":
                        vch = [x for x in vc.children if x.type not in ("=", "line_comment", "block_comment")]
                        if vch:
                            vname = safe_py_ident(_node_text(vch[0]))
                            members.discard(vname)
                            val_e = self.lower_expr(vch[-1], members) if len(vch) >= 2 else "None"
                            out.append(f"{pad}try: {vname} = {val_e}")
                            out.append(f"{pad}except Exception: {vname} = None")
            elif st_t == "if_statement":
                cond_node = next((c for c in st.children if c.type == "parenthesized_expression"), None)
                body_children = [c for c in st.children if c not in (cond_node,) and c.type not in ("if", "else", "line_comment", "block_comment")]
                cond_s = self.lower_expr(cond_node, members) if cond_node else "False"
                out.append(f"{pad}if {cond_s}:")
                if body_children:
                    b0 = body_children[0]
                    out.extend(self.lower_block(b0, indent + 4, members) if b0.type == "block" else [f"{pad}    pass"])
                else:
                    out.append(f"{pad}    pass")
                if len(body_children) >= 2:
                    b1 = body_children[1]
                    out.append(f"{pad}else:")
                    out.extend(self.lower_block(b1, indent + 4, members) if b1.type in ("block", "if_statement") else [f"{pad}    pass"])
            elif st_t == "while_statement":
                cond_node = next((c for c in st.children if c.type == "parenthesized_expression"), None)
                b_node = next((c for c in st.children if c.type == "block"), None)
                out.append(f"{pad}while {self.lower_expr(cond_node, members) if cond_node else 'False'}:")
                out.extend(self.lower_block(b_node, indent + 4, members) if b_node else [f"{pad}    break"])
            elif st_t == "for_statement":
                b_node = next((c for c in st.children if c.type == "block"), None)
                init_n = next((c for c in st.children if c.type == "local_variable_declaration"), None)
                bin_n = next((c for c in st.children if c.type == "binary_expression"), None)
                upd_n = next((c for c in st.children if c.type == "update_expression"), None)
                if init_n is not None and bin_n is not None and b_node is not None:
                    for vc in init_n.children:
                        if vc.type == "variable_declarator":
                            vch = [x for x in vc.children if x.type not in ("=", "line_comment", "block_comment")]
                            if vch:
                                vn = safe_py_ident(_node_text(vch[0]))
                                members.discard(vn)
                                out.append(f"{pad}{vn} = {self.lower_expr(vch[-1], members) if len(vch) >= 2 else '0'}")
                    out.append(f"{pad}while {self.lower_expr(bin_n, members)}:")
                    out.extend(self.lower_block(b_node, indent + 4, members))
                    if upd_n is not None:
                        utxt = _node_text(upd_n).strip()
                        uch = [x for x in upd_n.children if x.type not in ("line_comment", "block_comment", "++", "--")]
                        if uch:
                            out.append(f"{pad}    {self.lower_expr(uch[0], members)} {'+= 1' if '++' in utxt else '-= 1'}")
            elif st_t == "enhanced_for_statement":
                ids = [c for c in st.children if c.type == "identifier"]
                b_node = next((c for c in st.children if c.type == "block"), None)
                colon_seen = False
                iter_node = None
                for c in st.children:
                    if c.type == ":":
                        colon_seen = True
                    elif colon_seen and c.type not in (")", "block", "line_comment", "block_comment"):
                        iter_node = c
                        break
                vname = safe_py_ident(_node_text(ids[0])) if ids else "_it"
                members.discard(vname)
                out.append(f"{pad}for {vname} in ({self.lower_expr(iter_node, members) if iter_node else '[]'} or []):")
                out.extend(self.lower_block(b_node, indent + 4, members) if b_node else [f"{pad}    pass"])
            elif st_t == "try_statement":
                b_node = next((c for c in st.children if c.type == "block"), None)
                out.append(f"{pad}try:")
                out.extend(self.lower_block(b_node, indent + 4, members) if b_node else [f"{pad}    pass"])
                out.append(f"{pad}except Exception:")
                out.append(f"{pad}    pass")
            elif st_t == "expression_statement":
                ech = [c for c in st.children if c.type not in (";", "line_comment", "block_comment")]
                if ech and ech[0].type == "assignment_expression":
                    ach = [x for x in ech[0].children if x.type not in ("line_comment", "block_comment")]
                    if len(ach) >= 3:
                        op_s = _node_text(ach[1]).strip()
                        lhs_n = ach[0]
                        if lhs_n.type in ("identifier", "field_access", "array_access") and op_s in ("=", "+=", "-=", "*=", "%=", "|=", "&=", "^="):
                            out.append(f"{pad}{self.lower_expr(lhs_n, members)} {op_s} {self.lower_expr(ach[2], members)}")
                            continue
                if ech and ech[0].type == "update_expression":
                    utxt = _node_text(ech[0]).strip()
                    uch = [x for x in ech[0].children if x.type not in ("line_comment", "block_comment", "++", "--")]
                    if uch and uch[0].type in ("identifier", "field_access", "array_access"):
                        uop = "+= 1" if "++" in utxt else "-= 1"
                        out.append(f"{pad}{self.lower_expr(uch[0], members)} {uop}")
                        continue
                if ech:
                    out.append(f"{pad}try: {self.lower_expr(ech[0], members)}")
                    out.append(f"{pad}except Exception: pass")
        return out or [f"{pad}pass"]

    def lower_type_decl(self, node: Any, stats: Dict[str, int], indent: int = 0) -> List[str]:
        pad = " " * indent
        is_enum = node.type == "enum_declaration"
        id_node = next((c for c in node.children if c.type == "identifier"), None)
        cname = safe_py_ident(_node_text(id_node)) if id_node else "AnonJavaClass"
        body_node = next((c for c in node.children if c.type in ("class_body", "interface_body", "enum_body")), None)
        if body_node is None:
            return []
        stats["classes"] = stats.get("classes", 0) + 1
        base_names: List[str] = []
        for c in node.children:
            if c.type in ("superclass", "super_interfaces", "extends_interfaces"):
                for sc in c.children:
                    if sc.type in ("type_identifier", "generic_type", "type_list"):
                        for raw_t in _node_text(sc).split(","):
                            bname = safe_py_ident(raw_t.split("<")[0].split(".")[-1].strip())
                            if bname and bname not in ("Object", "Comparable", "Serializable", cname) and bname not in base_names:
                                base_names.append(bname)
        out: List[str] = []
        if base_names and indent == 0:
            b_list = ", ".join(repr(b) for b in base_names)
            out.append(f"{pad}_bases_{cname} = tuple(globals()[_b] for _b in ({b_list},) if isinstance(globals().get(_b), type))")
            out.append(f"{pad}class {cname}(*_bases_{cname}):")
        else:
            out.append(f"{pad}class {cname}:")
        out.append(f"{pad}    _source = {repr(self.source_label)}")

        decl_children: List[Any] = []
        enum_consts: List[Tuple[str, List[str]]] = []
        for bc in body_node.children:
            if bc.type == "enum_constant":
                ec_id = next((x for x in bc.children if x.type == "identifier"), None)
                ec_args_n = next((x for x in bc.children if x.type == "argument_list"), None)
                ec_args = [self.lower_expr(ac) for ac in (ec_args_n.children if ec_args_n else []) if ac.type not in ("(", ")", ",", "line_comment", "block_comment")]
                if ec_id:
                    enum_consts.append((safe_py_ident(_node_text(ec_id)), ec_args))
            elif bc.type == "enum_body_declarations":
                decl_children.extend(bc.children)
            else:
                decl_children.append(bc)

        member_names: Set[str] = set()
        prop_inits: List[Tuple[str, str]] = []
        static_inits: List[Tuple[str, str]] = []
        for dc in decl_children:
            if dc.type == "field_declaration":
                mods_n = next((x for x in dc.children if x.type == "modifiers"), None)
                is_static = "static" in (_node_text(mods_n) if mods_n else "") or node.type == "interface_declaration"
                for vc in dc.children:
                    if vc.type == "variable_declarator":
                        vch = [x for x in vc.children if x.type not in ("=", "line_comment", "block_comment")]
                        if vch:
                            fname = safe_py_ident(_node_text(vch[0]))
                            fval = self.lower_expr(vch[-1], member_names if is_static else set()).replace("self.", f"{cname}.") if len(vch) >= 2 else "None"
                            member_names.add(fname)
                            try:
                                p_node = ast.parse(fval, mode="eval").body
                                is_const = isinstance(p_node, ast.Constant) or (isinstance(p_node, ast.UnaryOp) and isinstance(p_node.operand, ast.Constant))
                                if is_const:
                                    out.append(f"{pad}    {fname} = {fval}")
                                    if not is_static:
                                        prop_inits.append((fname, fval))
                                else:
                                    out.append(f"{pad}    {fname} = None")
                                    if is_static and fval != "None":
                                        static_inits.append((fname, fval))
                            except SyntaxError:
                                out.append(f"{pad}    {fname} = None")
            elif dc.type == "method_declaration":
                mid = next((x for x in dc.children if x.type == "identifier"), None)
                if mid:
                    member_names.add(safe_py_ident(_node_text(mid)))

        ctors = [dc for dc in decl_children if dc.type == "constructor_declaration"]
        ctor_node = max(ctors, key=lambda dc: len(self._parse_formal_params(next((x for x in dc.children if x.type == "formal_parameters"), None)))) if ctors else None
        ctor_params: List[str] = []
        ctor_body_lines: List[str] = []
        if ctor_node is not None:
            cp_node = next((x for x in ctor_node.children if x.type == "formal_parameters"), None)
            cb_node = next((x for x in ctor_node.children if x.type == "constructor_body"), None)
            ctor_params = self._parse_formal_params(cp_node)
            member_names.update(ctor_params)
            if cb_node is not None:
                ctor_body_lines = self.lower_block(cb_node, indent + 8, member_names - set(ctor_params))

        init_sig = ", ".join(["self"] + [f"{p}=None" for p in ctor_params] + ["*_kt_args", "**_kt_kwargs"])
        out.append(f"{pad}    def __init__({init_sig}):")
        for p in ctor_params:
            out.append(f"{pad}        self.{p} = {p}")
        for pname, _ in prop_inits:
            out.append(f"{pad}        self.{pname} = getattr(self.__class__, {repr(pname)}, None)")
        out.extend(ctor_body_lines)
        out.append(f"{pad}        for _k, _v in _kt_kwargs.items():")
        out.append(f"{pad}            setattr(self, _k, _v)")

        if is_enum:
            out.append(f"{pad}    def ordinal(self): return getattr(self, '_ordinal', 0)")
            out.append(f"{pad}    def name(self): return getattr(self, '_name', '')")
            out.append(f"{pad}    def __repr__(self): return getattr(self, '_name', '')")
            member_names.update(("ordinal", "name"))

        zero_arg_getters: List[Tuple[str, str]] = []
        seen_methods: Set[str] = set()
        method_groups: Dict[str, List[Tuple[bool, List[str], List[str]]]] = {}
        for dc in decl_children:
            if dc.type == "method_declaration":
                mods_n = next((x for x in dc.children if x.type == "modifiers"), None)
                mtxt = _node_text(mods_n) if mods_n else ""
                is_static = "static" in mtxt
                is_native = "native" in mtxt
                mid = next((x for x in dc.children if x.type == "identifier"), None)
                if mid is None:
                    continue
                mname = safe_py_ident(_node_text(mid))
                seen_methods.add(mname)
                mp_node = next((x for x in dc.children if x.type == "formal_parameters"), None)
                mb_node = next((x for x in dc.children if x.type == "block"), None)
                mp_names = self._parse_formal_params(mp_node)
                ur_locals: Dict[str, HolderDecl] = {}
                ur_body = _cst_to_ur_stmts([mb_node], ur_locals, "java") if mb_node is not None else []
                self.ledger.functions.append(
                    URFunc(
                        func_name=f"{cname}.{mname}",
                        source_lang="java",
                        params=[HolderDecl.from_type(p, "i64") for p in mp_names],
                        locals=ur_locals,
                        return_holder="i64",
                        body=ur_body,
                    )
                )
                if is_native:
                    c_args = ", ".join(mp_names)
                    m_lines = [f"{pad}        return getattr(_host_os, {repr(mname)}, lambda *a, **kw: None)({c_args})"]
                    stats["external_funs"] = stats.get("external_funs", 0) + 1
                elif mb_node is not None:
                    m_lines = self.lower_block(mb_node, indent + 8, member_names - set(mp_names))
                else:
                    m_lines = [f"{pad}        return None"]
                if not is_static and not mp_names and mname.startswith("get") and len(mname) > 3 and mname[3].isupper():
                    prop_n = mname[3].lower() + mname[4:]
                    if prop_n not in member_names:
                        zero_arg_getters.append((prop_n, mname))
                method_groups.setdefault(mname, []).append((is_static, mp_names, m_lines))
                stats["methods_lowered"] = stats.get("methods_lowered", 0) + 1

        for mname, overloads in method_groups.items():
            if len(overloads) == 1:
                is_static, mp_names, m_lines = overloads[0]
                if is_static:
                    out.append(f"{pad}    @classmethod")
                sig_s = ", ".join(["self"] + [f"{p}=None" for p in mp_names] + ["*_kt_a", "**_kt_kw"])
                out.append(f"{pad}    def {mname}({sig_s}):")
                out.extend(m_lines)
            else:
                any_static = any(st for st, _, _ in overloads)
                for idx, (is_static, mp_names, m_lines) in enumerate(overloads):
                    if any_static:
                        out.append(f"{pad}    @classmethod")
                    sig_s = ", ".join(["self"] + [f"{p}=None" for p in mp_names] + ["*_kt_a", "**_kt_kw"])
                    out.append(f"{pad}    def _ov_{mname}_{idx}({sig_s}):")
                    out.extend(m_lines)
                if any_static:
                    out.append(f"{pad}    @classmethod")
                out.append(f"{pad}    def {mname}(self, *_a, **_kw):")
                specs = ", ".join(f"({len(mp)}, self._ov_{mname}_{idx})" for idx, (_, mp, _) in enumerate(overloads))
                out.append(f"{pad}        for _ar, _fn in [{specs}]:")
                out.append(f"{pad}            if _ar == len(_a):")
                out.append(f"{pad}                try: return _fn(*_a, **_kw)")
                out.append(f"{pad}                except Exception: pass")
                out.append(f"{pad}        for _ar, _fn in [{specs}]:")
                out.append(f"{pad}            try: return _fn(*_a, **_kw)")
                out.append(f"{pad}            except Exception: pass")
                out.append(f"{pad}        return None")

        for prop_n, getter_m in zero_arg_getters:
            if prop_n not in seen_methods:
                seen_methods.add(prop_n)
                out.append(f"{pad}    @property")
                out.append(f"{pad}    def {prop_n}(self): return self.{getter_m}()")

        if is_enum:
            out.append(f"{pad}    @classmethod")
            out.append(f"{pad}    def values(cls): return list(getattr(cls, '_ENUM_VALUES', []))")
            out.append(f"{pad}    @classmethod")
            out.append(f"{pad}    def valueOf(cls, s): return getattr(cls, str(s), None)")

        try:
            ast.parse("\n".join(out))
        except SyntaxError:
            out = [f"{pad}class {cname}:", f"{pad}    _source = {repr(self.source_label)}"]

        if is_enum and enum_consts:
            out.append(f"{pad}{cname}._ENUM_VALUES = []")
            for idx, (ec_name, ec_args) in enumerate(enum_consts):
                arg_s = ", ".join(ec_args + [f"_ordinal={idx}", f"_name={repr(ec_name)}"])
                out.append(f"{pad}{cname}.{ec_name} = {cname}({arg_s})")
                out.append(f"{pad}{cname}._ENUM_VALUES.append({cname}.{ec_name})")
            out.append(f"{pad}{cname}.entries = {cname}._ENUM_VALUES")

        static_block_lines: List[str] = []
        for dc in decl_children:
            if dc.type == "static_initializer":
                sb_n = next((x for x in dc.children if x.type == "block"), None)
                if sb_n is not None:
                    for sl in self.lower_block(sb_n, indent + 8, member_names):
                        static_block_lines.append(sl.replace("self.", f"{cname}."))

        if static_inits or static_block_lines:
            out.append(f"{pad}def _init_comp_{cname}():")
            for sf_name, sf_val in static_inits:
                out.append(f"{pad}    try: {cname}.{sf_name} = {sf_val}")
                out.append(f"{pad}    except Exception: pass")
            if static_block_lines:
                out.append(f"{pad}    try:")
                out.extend(static_block_lines)
                out.append(f"{pad}    except Exception: pass")
            out.append(f"{pad}{cname}._init_companion = staticmethod(_init_comp_{cname})")
            out.append(f"{pad}_init_comp_{cname}()")
        return out

    def lower_source_file(self, root: Any) -> Tuple[List[str], Dict[str, int]]:
        out: List[str] = []
        stats = {"classes": 0, "methods_lowered": 0, "external_funs": 0, "top_funs": 0, "ledger_funcs": 0}
        for c in root.children:
            if c.type == "import_declaration" and any(ic.type == "static" for ic in c.children):
                sc = next((ic for ic in c.children if ic.type == "scoped_identifier"), None)
                if sc is not None and not any(ic.type == "asterisk" for ic in c.children):
                    parts = [safe_py_ident(p.strip()) for p in _node_text(sc).split(".") if p.strip()]
                    if len(parts) >= 2:
                        self.static_imports[parts[-1]] = f"{parts[-2]}.{parts[-1]}"
        for c in root.children:
            if c.type in ("class_declaration", "interface_declaration", "enum_declaration"):
                lines = self.lower_type_decl(c, stats, indent=0)
                if lines:
                    out.extend(lines + [""])
        stats["ledger_funcs"] = len(self.ledger.functions)
        return out, stats


def transpile_java_source_via_ledger(raw_src: str, source_label: str = "") -> Tuple[List[str], Dict[str, int], URLedger]:
    tree = _JV_PARSER.parse(raw_src.encode("utf-8", errors="ignore"))
    lowerer = JavaCSTLedgerLowerer(source_label=source_label)
    lines, stats = lowerer.lower_source_file(tree.root_node)
    return lines, stats, lowerer.ledger
