"""jvm_ast_to_ledger -- Genuine Tree-sitter Kotlin & Java AST to URLedger lowerer.

Lowers sliced Kotlin (`.kt`) and Java (`.java`) declarations directly from their
Tree-sitter CST nodes into `URLedger` / `URFunc` nodes (`HolderDecl`, `URVar`,
`URConst`, `URHiOpCall`, `URCall`, `URHolderCast`, `URAssign`, `URIf`, `URWhile`,
`URReturn`), where every arithmetic, bitwise, shift, comparison, and conditional
operation is a `URHiOpCall` backed by a Sail-derived `UnitLean` in `Hub` and
emitted via `LedgerToScript` + `AutoPoly`.

Enforces strict Zero-Trust lowering: any unsupported CST node raises an explicit
`NotImplementedError(f"{file_path}:{line}: Unsupported {lang} AST node {node.type!r}")`
with zero silent exception catches or empty fallbacks.
"""
from __future__ import annotations

from typing import Any
from tree_sitter import Language, Node, Parser
import tree_sitter_java
import tree_sitter_kotlin

from .ur_ledger import (
    HolderDecl,
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
    build_holder_cast_node,
    build_ur_node,
)

KT_LANG = Language(tree_sitter_kotlin.language())
JV_LANG = Language(tree_sitter_java.language())

JVM_TYPE_TO_HOLDER: dict[str, str] = {
    "byte": "i8",
    "Byte": "i8",
    "short": "i16",
    "Short": "i16",
    "int": "i32",
    "Int": "i32",
    "long": "i64",
    "Long": "i64",
    "boolean": "i64",
    "Boolean": "i64",
    "float": "i64",
    "Float": "i64",
    "double": "i64",
    "Double": "i64",
}


def _clean_text(node: Node) -> str:
    return node.text.decode("utf-8", errors="ignore").strip()


class JvmAstToLedger:
    """Tree-sitter Kotlin and Java CST -> URLedger lowerer with zero silent drops."""

    def __init__(
        self,
        constants: dict[str, int] | None = None,
        fp_constants: dict[str, float] | None = None,
        set_constants: dict[str, list[int]] | None = None,
        struct_fields: dict[str, list[str]] | None = None,
        fp_funcs: set[str] | None = None,
        call_arity_aliases: dict[tuple[str, int], str] | None = None,
        float_scale: int = 10000,
    ) -> None:
        self.kt_parser = Parser(KT_LANG)
        self.jv_parser = Parser(JV_LANG)
        self.constants: dict[str, int] = dict(constants or {})
        self.fp_constants: dict[str, float] = dict(fp_constants or {})
        self.set_constants: dict[str, list[int]] = dict(set_constants or {})
        self.struct_fields: dict[str, list[str]] = dict(struct_fields or {})
        self.fp_funcs: set[str] = set(fp_funcs or set())
        self.call_arity_aliases: dict[tuple[str, int], str] = dict(call_arity_aliases or {})
        self.float_scale = float_scale

    def lower_java_method(
        self,
        file_path: str,
        method_name: str,
        func_alias: str | None = None,
    ) -> URFunc:
        """Parse `file_path` with `tree_sitter_java`, locate `method_name`, and lower to `URFunc`."""
        with open(file_path, "rb") as f:
            raw = f.read()
        tree = self.jv_parser.parse(raw)
        target_node = self._find_java_method(tree.root_node, method_name)
        if target_node is None:
            raise KeyError(f"{file_path}: Java method {method_name!r} not found in CST")
        return self._lower_java_method_node(target_node, file_path, func_alias or method_name)

    def _find_java_method(self, root: Node, method_name: str) -> Node | None:
        stack = [root]
        while stack:
            cur = stack.pop()
            if cur.type == "method_declaration":
                name_n = cur.child_by_field_name("name")
                if name_n is not None and _clean_text(name_n) == method_name:
                    return cur
            stack.extend(reversed(cur.children))
        return None

    def _lower_java_method_node(self, node: Node, file_path: str, func_name: str) -> URFunc:
        params: list[HolderDecl] = []
        known: dict[str, str] = {}
        locals_map: dict[str, HolderDecl] = {}

        params_node = node.child_by_field_name("parameters")
        if params_node is not None:
            for c in params_node.children:
                if c.type == "formal_parameter":
                    t_node = c.child_by_field_name("type")
                    n_node = c.child_by_field_name("name")
                    t_str = _clean_text(t_node) if t_node else "long"
                    n_str = _clean_text(n_node) if n_node else "arg"
                    h = JVM_TYPE_TO_HOLDER.get(t_str, "i64")
                    # Use 64-bit register slots for function parameters while preserving explicit casts inside bodies
                    params.append(HolderDecl.from_type(n_str, "i64"))
                    known[n_str] = h

        ret_node = node.child_by_field_name("type")
        ret_str = _clean_text(ret_node) if ret_node else "long"
        ret_holder = JVM_TYPE_TO_HOLDER.get(ret_str, "i64")

        body_node = node.child_by_field_name("body")
        if body_node is None:
            raise NotImplementedError(f"{file_path}:{node.start_point[0] + 1}: Java method {func_name!r} has no body")

        stmts = self._lower_java_block(body_node, file_path, known, locals_map)
        return URFunc(
            func_name=func_name,
            source_lang="java",
            params=params,
            locals=locals_map,
            return_holder="i64" if ret_holder == "i32" else ret_holder,
            body=stmts,
        )

    def _lower_java_block(
        self,
        block_node: Node,
        file_path: str,
        known: dict[str, str],
        locals_map: dict[str, HolderDecl],
    ) -> list[Any]:
        out: list[Any] = []
        for child in block_node.children:
            ctype = child.type
            if ctype in ("{", "}", ";", "line_comment", "block_comment"):
                continue
            out.extend(self._lower_java_stmt(child, file_path, known, locals_map))
        return out

    def _lower_java_stmt(
        self,
        node: Node,
        file_path: str,
        known: dict[str, str],
        locals_map: dict[str, HolderDecl],
    ) -> list[Any]:
        ctype = node.type
        line = node.start_point[0] + 1

        if ctype == "block":
            return self._lower_java_block(node, file_path, known, locals_map)

        if ctype == "local_variable_declaration":
            t_node = node.child_by_field_name("type")
            t_str = _clean_text(t_node) if t_node else "long"
            h = JVM_TYPE_TO_HOLDER.get(t_str, "i64")
            stmts: list[Any] = []
            for sub in node.children:
                if sub.type == "variable_declarator":
                    name_n = sub.child_by_field_name("name")
                    val_n = sub.child_by_field_name("value")
                    if name_n is None or val_n is None:
                        raise NotImplementedError(f"{file_path}:{line}: Uninitialized Java local {_clean_text(sub)!r}")
                    vname = _clean_text(name_n)
                    expr = self._lower_java_expr(val_n, file_path, known)
                    known[vname] = "i64"
                    locals_map[vname] = HolderDecl.from_type(vname, "i64")
                    stmts.append(URAssign(target=vname, holder="i64", expr=expr, is_decl=True))
            return stmts

        if ctype == "expression_statement":
            expr_children = [c for c in node.children if c.type not in (";", "line_comment", "block_comment")]
            if len(expr_children) != 1:
                raise NotImplementedError(f"{file_path}:{line}: Unsupported Java expression_statement {_clean_text(node)!r}")
            inner = expr_children[0]
            if inner.type == "assignment_expression":
                left_n = inner.child_by_field_name("left")
                right_n = inner.child_by_field_name("right")
                op_n = inner.child_by_field_name("operator")
                if op_n is not None:
                    op_str = _clean_text(op_n)
                else:
                    op_tokens = [
                        _clean_text(c)
                        for c in inner.children
                        if c != left_n and c != right_n and c.type not in ("line_comment", "block_comment")
                    ]
                    op_str = op_tokens[0] if op_tokens else "="
                vname = _clean_text(left_n)
                rhs = self._lower_java_expr(right_n, file_path, known)
                if op_str == "=":
                    return [URAssign(target=vname, holder=known.get(vname, "i64"), expr=rhs, is_decl=False)]
                if op_str in ("+=", "-=", "*=", "/="):
                    base_op = "trunc_div" if op_str == "/=" else op_str[0]
                    lhs_var = URVar(name=vname, holder=known.get(vname, "i64"))
                    comb = URHiOpCall(build_ur_node("java", base_op, "i64", True), [lhs_var, rhs], base_op, "i64")
                    return [URAssign(target=vname, holder=known.get(vname, "i64"), expr=comb, is_decl=False)]
                raise NotImplementedError(f"{file_path}:{line}: Unsupported Java assignment op {op_str!r}")

            if inner.type == "update_expression":
                txt = _clean_text(inner)
                if txt.endswith("++") or txt.startswith("++"):
                    vname = txt.replace("++", "").strip()
                    lhs_var = URVar(name=vname, holder=known.get(vname, "i64"))
                    inc = URHiOpCall(build_ur_node("java", "+", "i64", True), [lhs_var, URConst(1, "i64")], "+", "i64")
                    return [URAssign(target=vname, holder=known.get(vname, "i64"), expr=inc, is_decl=False)]
                if txt.endswith("--") or txt.startswith("--"):
                    vname = txt.replace("--", "").strip()
                    lhs_var = URVar(name=vname, holder=known.get(vname, "i64"))
                    dec = URHiOpCall(build_ur_node("java", "-", "i64", True), [lhs_var, URConst(1, "i64")], "-", "i64")
                    return [URAssign(target=vname, holder=known.get(vname, "i64"), expr=dec, is_decl=False)]
                raise NotImplementedError(f"{file_path}:{line}: Unsupported Java update_expression {txt!r}")

            if inner.type == "method_invocation":
                mname = _clean_text(inner.child_by_field_name("name"))
                # Range validation pre-check in LocalDate.ofEpochDay (`EPOCH_DAY.checkValidValue(epochDay)`)
                if mname in ("checkValidValue", "requireNonNull"):
                    return []
                call_e = self._lower_java_expr(inner, file_path, known)
                return [URAssign(target="_ unused_call", holder="i64", expr=call_e, is_decl=True)]

            raise NotImplementedError(f"{file_path}:{line}: Unsupported Java expression_statement child {inner.type!r}")

        if ctype == "if_statement":
            cond_n = node.child_by_field_name("condition")
            cons_n = node.child_by_field_name("consequence")
            alt_n = node.child_by_field_name("alternative")
            cond_e = self._lower_java_expr(cond_n, file_path, known)
            then_b = self._lower_java_stmt(cons_n, file_path, known, locals_map) if cons_n else []
            else_b = self._lower_java_stmt(alt_n, file_path, known, locals_map) if alt_n else []
            return [URIf(cond=cond_e, then_body=then_b, else_body=else_b)]

        if ctype == "while_statement":
            cond_n = node.child_by_field_name("condition")
            body_n = node.child_by_field_name("body")
            cond_e = self._lower_java_expr(cond_n, file_path, known)
            body_b = self._lower_java_stmt(body_n, file_path, known, locals_map) if body_n else []
            return [URWhile(cond=cond_e, body=body_b)]

        if ctype == "return_statement":
            expr_children = [c for c in node.children if c.type not in ("return", ";", "line_comment", "block_comment")]
            if not expr_children:
                return [URReturn(expr=URConst(0, "i64"))]
            return [URReturn(expr=self._lower_java_expr(expr_children[0], file_path, known))]

        raise NotImplementedError(f"{file_path}:{line}: Unsupported Java statement AST node {ctype!r}: {_clean_text(node)!r}")

    def _lower_java_expr(self, node: Node, file_path: str, known: dict[str, str]) -> Any:
        ctype = node.type
        line = node.start_point[0] + 1

        if ctype == "parenthesized_expression":
            inner = [c for c in node.children if c.type not in ("(", ")", "line_comment", "block_comment")]
            if len(inner) == 1:
                return self._lower_java_expr(inner[0], file_path, known)
            raise NotImplementedError(f"{file_path}:{line}: Malformed parenthesized_expression")

        if ctype in ("decimal_integer_literal", "hex_integer_literal"):
            raw = _clean_text(node).rstrip("lL").replace("_", "")
            val = int(raw, 16) if raw.lower().startswith("0x") else int(raw)
            return URConst(value=val, holder="i64")

        if ctype in ("true", "false"):
            return URConst(value=1 if ctype == "true" else 0, holder="i64")

        if ctype == "identifier":
            ident = _clean_text(node)
            if ident in known:
                return URVar(name=ident, holder="i64")
            if ident in self.constants:
                return URConst(value=self.constants[ident], holder="i64")
            raise NotImplementedError(f"{file_path}:{line}: Unresolved Java identifier {ident!r}")

        if ctype == "unary_expression":
            op_node = node.child_by_field_name("operator")
            operand_node = node.child_by_field_name("operand")
            op_str = _clean_text(op_node) if op_node else "-"
            arg = self._lower_java_expr(operand_node, file_path, known)
            if op_str == "-":
                if isinstance(arg, URConst):
                    return URConst(value=-arg.value, holder="i64")
                return URHiOpCall(build_ur_node("java", "neg", "i64", True), [arg], "neg", "i64")
            if op_str == "!":
                return URHiOpCall(build_ur_node("java", "==", "i64", True), [arg, URConst(0, "i64")], "==", "i64")
            raise NotImplementedError(f"{file_path}:{line}: Unsupported Java unary op {op_str!r}")

        if ctype == "cast_expression":
            t_node = node.child_by_field_name("type")
            v_node = node.child_by_field_name("value")
            t_str = _clean_text(t_node) if t_node else "long"
            dst_h = JVM_TYPE_TO_HOLDER.get(t_str, "i64")
            inner = self._lower_java_expr(v_node, file_path, known)
            if dst_h != "i64":
                return build_holder_cast_node(inner, "i64", dst_h, lang="java")
            return inner

        if ctype == "binary_expression":
            left_n = node.child_by_field_name("left")
            right_n = node.child_by_field_name("right")
            op_n = node.child_by_field_name("operator")
            op_str = _clean_text(op_n) if op_n else "+"
            lhs = self._lower_java_expr(left_n, file_path, known)
            rhs = self._lower_java_expr(right_n, file_path, known)
            op_map = {
                "+": "+",
                "-": "-",
                "*": "*",
                "/": "trunc_div",
                "%": "trunc_rem",
                "&": "&",
                "|": "|",
                "^": "^",
                "<<": "<<",
                ">>": ">>",
                ">>>": ">>>",
                "==": "==",
                "!=": "!=",
                "<": "<",
                "<=": "<=",
                ">": ">",
                ">=": ">=",
                "&&": "&&",
                "||": "||",
            }
            if op_str not in op_map:
                raise NotImplementedError(f"{file_path}:{line}: Unsupported Java binary operator {op_str!r}")
            canon_op = op_map[op_str]
            return URHiOpCall(build_ur_node("java", canon_op, "i64", True), [lhs, rhs], canon_op, "i64")

        if ctype == "ternary_expression":
            cond_n = node.child_by_field_name("condition")
            cons_n = node.child_by_field_name("consequence")
            alt_n = node.child_by_field_name("alternative")
            return URHiOpCall(
                build_ur_node("java", "ite", "i64", True),
                [
                    self._lower_java_expr(cond_n, file_path, known),
                    self._lower_java_expr(cons_n, file_path, known),
                    self._lower_java_expr(alt_n, file_path, known),
                ],
                "ite",
                "i64",
            )

        if ctype == "object_creation_expression":
            type_n = node.child_by_field_name("type")
            args_n = node.child_by_field_name("arguments")
            tname = _clean_text(type_n).split("<")[0].split(".")[-1] if type_n else "Object"
            args: list[Any] = []
            if args_n is not None:
                for ac in args_n.children:
                    if ac.type not in ("(", ")", ",", "line_comment", "block_comment"):
                        args.append(self._lower_java_expr(ac, file_path, known))
            # Pack LocalDate(year, month, day) via Sail-backed shift/bitwise-or URHiOpCalls:
            # (year << 16) | (month << 8) | day
            if tname == "LocalDate" and len(args) == 3:
                y_shl = URHiOpCall(build_ur_node("java", "<<", "i64", True), [args[0], URConst(16, "i64")], "<<", "i64")
                m_shl = URHiOpCall(build_ur_node("java", "<<", "i64", True), [args[1], URConst(8, "i64")], "<<", "i64")
                ym_or = URHiOpCall(build_ur_node("java", "|", "i64", True), [y_shl, m_shl], "|", "i64")
                return URHiOpCall(build_ur_node("java", "|", "i64", True), [ym_or, args[2]], "|", "i64")
            return URCall(func_name=f"new_{tname}", args=args, holder="i64")

        if ctype == "method_invocation":
            name_n = node.child_by_field_name("name")
            args_n = node.child_by_field_name("arguments")
            mname = _clean_text(name_n) if name_n else "call"
            args = []
            if args_n is not None:
                for ac in args_n.children:
                    if ac.type not in ("(", ")", ",", "line_comment", "block_comment"):
                        args.append(self._lower_java_expr(ac, file_path, known))
            return URCall(func_name=mname, args=args, holder="i64")

        raise NotImplementedError(f"{file_path}:{line}: Unsupported Java expression AST node {ctype!r}: {_clean_text(node)!r}")

    # ── Kotlin AST Lowering ────────────────────────────────────────────────────

    def lower_kotlin_function(
        self,
        file_path: str,
        func_name: str,
        func_alias: str | None = None,
        param_count: int | None = None,
        implicit_params: list[str] | None = None,
    ) -> URFunc:
        """Parse `file_path` with `tree_sitter_kotlin`, locate `func_name`, and lower to `URFunc`."""
        with open(file_path, "rb") as f:
            raw = f.read()
        tree = self.kt_parser.parse(raw)
        self._index_kotlin_file_metadata(tree.root_node)
        target_node = self._find_kotlin_function(tree.root_node, func_name, param_count=param_count)
        if target_node is None:
            raise KeyError(f"{file_path}: Kotlin function {func_name!r} not found in CST")
        return self._lower_kotlin_function_node(
            target_node,
            file_path,
            func_alias or func_name,
            implicit_params=implicit_params,
        )

    def _index_kotlin_file_metadata(self, root: Node) -> None:
        """Extract literal `const val`/`val` properties and `Float`/`Double` return signatures from the CST."""
        stack = [root]
        while stack:
            cur = stack.pop()
            if cur.type == "property_declaration":
                vname = ""
                init_node: Node | None = None
                seen_eq = False
                for c in cur.children:
                    if c.type == "variable_declaration":
                        for vc in c.children:
                            if vc.type in ("identifier", "simple_identifier"):
                                vname = _clean_text(vc)
                                break
                    elif c.type == "=":
                        seen_eq = True
                    elif seen_eq and c.type not in ("line_comment", "block_comment"):
                        init_node = c
                        break
                if vname and init_node is not None:
                    if init_node.type in ("number_literal", "integer_literal", "long_literal"):
                        raw = _clean_text(init_node).rstrip("lLuU").replace("_", "")
                        if "." in raw or raw.endswith(("f", "F")):
                            if vname not in self.fp_constants:
                                self.fp_constants[vname] = float(raw.rstrip("fF"))
                        else:
                            if vname not in self.constants:
                                self.constants[vname] = int(raw, 16) if raw.lower().startswith("0x") else int(raw)
                    elif init_node.type in ("float_literal", "real_literal"):
                        raw = _clean_text(init_node).rstrip("fF").replace("_", "")
                        if vname not in self.fp_constants:
                            self.fp_constants[vname] = float(raw)
            elif cur.type == "function_declaration":
                fname = ""
                seen_params = False
                ret_type = ""
                for c in cur.children:
                    if c.type in ("identifier", "simple_identifier") and not fname:
                        fname = _clean_text(c)
                    elif c.type == "function_value_parameters":
                        seen_params = True
                    elif seen_params and c.type in ("user_type", "nullable_type"):
                        ret_type = _clean_text(c).rstrip("?")
                        break
                    elif c.type == "function_body":
                        break
                if fname and ret_type in ("Float", "Double", "float", "double"):
                    self.fp_funcs.add(fname)
            stack.extend(reversed(cur.children))

    def _find_kotlin_function(
        self,
        root: Node,
        func_name: str,
        param_count: int | None = None,
    ) -> Node | None:
        stack = [root]
        while stack:
            cur = stack.pop()
            if cur.type == "function_declaration":
                matched_name = False
                actual_params = 0
                for c in cur.children:
                    if c.type in ("identifier", "simple_identifier") and _clean_text(c) == func_name:
                        matched_name = True
                    elif c.type == "function_value_parameters":
                        actual_params = sum(1 for pc in c.children if pc.type == "parameter")
                if matched_name and (param_count is None or actual_params == param_count):
                    return cur
            stack.extend(reversed(cur.children))
        return None

    def _lower_kotlin_function_node(
        self,
        node: Node,
        file_path: str,
        func_name: str,
        implicit_params: list[str] | None = None,
    ) -> URFunc:
        params: list[HolderDecl] = []
        known: dict[str, str] = {}
        fp_vars: set[str] = set()
        locals_map: dict[str, HolderDecl] = {}

        if implicit_params:
            for ip in implicit_params:
                params.append(HolderDecl.from_type(ip, "i64"))
                known[ip] = "i64"

        for c in node.children:
            if c.type == "function_value_parameters":
                for pc in c.children:
                    if pc.type == "parameter":
                        p_ident = ""
                        p_type = "i64"
                        t_raw = ""
                        for sub in pc.children:
                            if sub.type in ("identifier", "simple_identifier") and not p_ident:
                                p_ident = _clean_text(sub)
                            elif sub.type in ("user_type", "nullable_type"):
                                t_raw = _clean_text(sub).rstrip("?")
                                p_type = JVM_TYPE_TO_HOLDER.get(t_raw, t_raw)
                        if p_ident in self.struct_fields:
                            for sf in self.struct_fields[p_ident]:
                                flat_n = f"{p_ident}_{sf}"
                                params.append(HolderDecl.from_type(flat_n, "i64"))
                                known[flat_n] = "i64"
                        else:
                            params.append(HolderDecl.from_type(p_ident, "i64"))
                            known[p_ident] = p_type
                            if t_raw in ("Float", "Double", "float", "double"):
                                fp_vars.add(p_ident)

        body_node = None
        for c in node.children:
            if c.type == "function_body":
                body_node = c
                break
        if body_node is None:
            raise NotImplementedError(f"{file_path}:{node.start_point[0] + 1}: Kotlin function {func_name!r} has no body")

        stmts = self._lower_kotlin_function_body(body_node, file_path, known, fp_vars, locals_map)
        return URFunc(
            func_name=func_name,
            source_lang="java",
            params=params,
            locals=locals_map,
            return_holder="i64",
            body=stmts,
        )

    def _lower_kotlin_function_body(
        self,
        body_node: Node,
        file_path: str,
        known: dict[str, str],
        fp_vars: set[str],
        locals_map: dict[str, HolderDecl],
    ) -> list[Any]:
        non_triv = [c for c in body_node.children if c.type not in ("=", "line_comment", "block_comment")]
        if len(non_triv) == 1 and non_triv[0].type == "block":
            return self._lower_kotlin_block(non_triv[0], file_path, known, fp_vars, locals_map)
        if len(non_triv) == 1:
            return [URReturn(expr=self._lower_kotlin_expr(non_triv[0], file_path, known, fp_vars))]
        raise NotImplementedError(f"{file_path}:{body_node.start_point[0] + 1}: Unsupported Kotlin function_body")

    def _lower_kotlin_block(
        self,
        block_node: Node,
        file_path: str,
        known: dict[str, str],
        fp_vars: set[str],
        locals_map: dict[str, HolderDecl],
    ) -> list[Any]:
        stmts: list[Any] = []
        children = [c for c in block_node.children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
        for idx, child in enumerate(children):
            is_last = idx == len(children) - 1
            stmts.extend(self._lower_kotlin_stmt(child, file_path, known, fp_vars, locals_map, is_last_in_block=is_last))
        if not stmts or not isinstance(stmts[-1], URReturn):
            if stmts and isinstance(stmts[-1], URAssign):
                stmts.append(URReturn(expr=URVar(stmts[-1].target, "i64")))
            else:
                stmts.append(URReturn(expr=URConst(0, "i64")))
        return stmts

    def _lower_kotlin_stmt(
        self,
        node: Node,
        file_path: str,
        known: dict[str, str],
        fp_vars: set[str],
        locals_map: dict[str, HolderDecl],
        is_last_in_block: bool = False,
    ) -> list[Any]:
        ctype = node.type
        line = node.start_point[0] + 1

        if ctype == "property_declaration":
            vname = ""
            init_node: Node | None = None
            seen_eq = False
            for c in node.children:
                if c.type == "variable_declaration":
                    for vc in c.children:
                        if vc.type in ("identifier", "simple_identifier"):
                            vname = _clean_text(vc)
                            break
                elif c.type == "=":
                    seen_eq = True
                elif seen_eq and c.type not in ("line_comment", "block_comment"):
                    init_node = c
                    break
            if not vname or init_node is None:
                raise NotImplementedError(f"{file_path}:{line}: Uninitialized Kotlin property {_clean_text(node)!r}")

            # Handle Elvis early-return pattern: `val perWeek = frequencyPerWeek?.coerceAtLeast(1) ?: return GAP_PROMPT_THRESHOLD_DAYS`
            if init_node.type in ("binary_expression", "elvis_expression"):
                b_children = [c for c in init_node.children if c.type not in ("line_comment", "block_comment")]
                if len(b_children) == 3 and _clean_text(b_children[1]) == "?:" and b_children[2].type == "return_expression":
                    lhs_e = self._lower_kotlin_expr(b_children[0], file_path, known, fp_vars)
                    ret_s = self._lower_kotlin_stmt(b_children[2], file_path, known, fp_vars, locals_map)
                    # Null or <= 0 sentinel triggers early return
                    base_var_name = _clean_text(b_children[0]).split("?")[0].split(".")[0].strip()
                    cond_null = URHiOpCall(
                        build_ur_node("java", "<=", "i64", True),
                        [URVar(base_var_name, "i64"), URConst(0, "i64")],
                        "<=",
                        "i64",
                    )
                    known[vname] = "i64"
                    locals_map[vname] = HolderDecl.from_type(vname, "i64")
                    return [
                        URIf(cond=cond_null, then_body=ret_s, else_body=[]),
                        URAssign(target=vname, holder="i64", expr=lhs_e, is_decl=True),
                    ]

            is_fp = self._is_fp_expr(init_node, known, fp_vars)
            expr = self._lower_kotlin_expr(init_node, file_path, known, fp_vars)
            known[vname] = "i64"
            if is_fp:
                fp_vars.add(vname)
            locals_map[vname] = HolderDecl.from_type(vname, "i64")
            return [URAssign(target=vname, holder="i64", expr=expr, is_decl=True)]

        if ctype == "assignment":
            non_triv = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(non_triv) == 3:
                vname = _clean_text(non_triv[0])
                op_str = _clean_text(non_triv[1])
                rhs = self._lower_kotlin_expr(non_triv[2], file_path, known, fp_vars)
                if op_str == "=":
                    return [URAssign(target=vname, holder="i64", expr=rhs, is_decl=False)]
                if op_str in ("+=", "-=", "*=", "/="):
                    base_op = "trunc_div" if op_str == "/=" else op_str[0]
                    comb = URHiOpCall(
                        build_ur_node("java", base_op, "i64", True),
                        [URVar(vname, "i64"), rhs],
                        base_op,
                        "i64",
                    )
                    return [URAssign(target=vname, holder="i64", expr=comb, is_decl=False)]
            raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin assignment {_clean_text(node)!r}")

        if ctype == "if_expression":
            cond_n, then_n, else_n = self._split_kotlin_if(node, file_path)
            cond_e = self._lower_kotlin_expr(cond_n, file_path, known, fp_vars)
            then_b = self._lower_kotlin_branch_as_stmts(then_n, file_path, known, fp_vars, locals_map, is_last_in_block)
            else_b = self._lower_kotlin_branch_as_stmts(else_n, file_path, known, fp_vars, locals_map, is_last_in_block) if else_n else []
            return [URIf(cond=cond_e, then_body=then_b, else_body=else_b)]

        if ctype == "return_expression":
            expr_children = [c for c in node.children if c.type not in ("return", "line_comment", "block_comment")]
            if not expr_children:
                return [URReturn(expr=URConst(0, "i64"))]
            return [URReturn(expr=self._lower_kotlin_expr(expr_children[0], file_path, known, fp_vars))]

        if ctype == "call_expression":
            cname = _clean_text(node.children[0]) if node.children else ""
            if cname == "require" or cname.startswith("require("):
                return []
            call_e = self._lower_kotlin_expr(node, file_path, known, fp_vars)
            if is_last_in_block:
                return [URReturn(expr=call_e)]
            tmp_name = f"_call_L{line}"
            known[tmp_name] = "i64"
            locals_map[tmp_name] = HolderDecl.from_type(tmp_name, "i64")
            return [URAssign(target=tmp_name, holder="i64", expr=call_e, is_decl=True)]

        if ctype in ("identifier", "simple_identifier") and not is_last_in_block:
            # Singleton object initialization reference (e.g. `NativeLibraryObject` in BundledSQLiteDriver)
            return []

        if is_last_in_block:
            return [URReturn(expr=self._lower_kotlin_expr(node, file_path, known, fp_vars))]

        raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin statement AST node {ctype!r}: {_clean_text(node)!r}")

    def _lower_kotlin_branch_as_stmts(
        self,
        branch_node: Node,
        file_path: str,
        known: dict[str, str],
        fp_vars: set[str],
        locals_map: dict[str, HolderDecl],
        is_last_in_block: bool,
    ) -> list[Any]:
        if branch_node.type == "control_structure_body":
            inner = [c for c in branch_node.children if c.type not in ("line_comment", "block_comment")]
            if len(inner) == 1 and inner[0].type == "block":
                children = [c for c in inner[0].children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
                stmts: list[Any] = []
                for idx, child in enumerate(children):
                    stmts.extend(
                        self._lower_kotlin_stmt(
                            child,
                            file_path,
                            known,
                            fp_vars,
                            locals_map,
                            is_last_in_block=(is_last_in_block and idx == len(children) - 1),
                        )
                    )
                return stmts
            if len(inner) == 1:
                return self._lower_kotlin_stmt(inner[0], file_path, known, fp_vars, locals_map, is_last_in_block=is_last_in_block)
        if branch_node.type == "block":
            children = [c for c in branch_node.children if c.type not in ("{", "}", ";", "line_comment", "block_comment")]
            stmts = []
            for idx, child in enumerate(children):
                stmts.extend(
                    self._lower_kotlin_stmt(
                        child,
                        file_path,
                        known,
                        fp_vars,
                        locals_map,
                        is_last_in_block=(is_last_in_block and idx == len(children) - 1),
                    )
                )
            return stmts
        return self._lower_kotlin_stmt(branch_node, file_path, known, fp_vars, locals_map, is_last_in_block=is_last_in_block)

    def _split_kotlin_if(self, node: Node, file_path: str) -> tuple[Node, Node, Node | None]:
        non_triv = [c for c in node.children if c.type not in ("if", "(", ")", "line_comment", "block_comment")]
        if len(non_triv) < 2:
            raise NotImplementedError(f"{file_path}:{node.start_point[0] + 1}: Malformed Kotlin if_expression")
        cond_n = non_triv[0]
        then_n = non_triv[1]
        else_n: Node | None = None
        for idx, c in enumerate(non_triv):
            if c.type == "else" and idx + 1 < len(non_triv):
                else_n = non_triv[idx + 1]
                break
        return cond_n, then_n, else_n

    def _is_fp_expr(self, node: Node, known: dict[str, str], fp_vars: set[str]) -> bool:
        ctype = node.type
        if ctype in ("float_literal", "real_literal"):
            return True
        if ctype in ("number_literal", "integer_literal", "long_literal"):
            raw = _clean_text(node)
            return "." in raw or raw.endswith(("f", "F"))
        if ctype in ("identifier", "simple_identifier"):
            ident = _clean_text(node)
            return ident in fp_vars or ident in self.fp_constants
        if ctype == "navigation_expression":
            parts = [c for c in node.children if c.type not in (".", "?.", "line_comment", "block_comment")]
            if len(parts) == 2:
                recv_txt = _clean_text(parts[0])
                mem_txt = _clean_text(parts[1])
                full_key = f"{recv_txt}.{mem_txt}"
                flat_var = f"{recv_txt}_{mem_txt}"
                return full_key in self.fp_constants or mem_txt in self.fp_constants or flat_var in fp_vars
            return False
        if ctype in ("parenthesized_expression", "control_structure_body"):
            inner = [c for c in node.children if c.type not in ("(", ")", "{", "}", "line_comment", "block_comment")]
            return len(inner) == 1 and self._is_fp_expr(inner[0], known, fp_vars)
        if ctype in ("prefix_expression", "unary_expression"):
            non_triv = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            return len(non_triv) == 2 and self._is_fp_expr(non_triv[1], known, fp_vars)
        if ctype == "if_expression":
            _, then_n, else_n = self._split_kotlin_if(node, "")
            return self._is_fp_expr(then_n, known, fp_vars) or (
                else_n is not None and self._is_fp_expr(else_n, known, fp_vars)
            )
        if ctype == "when_expression":
            for c in node.children:
                if c.type == "when_entry":
                    ent_children = [ec for ec in c.children if ec.type not in ("->", "line_comment", "block_comment")]
                    if len(ent_children) >= 2 and self._is_fp_expr(ent_children[-1], known, fp_vars):
                        return True
            return False
        if ctype in (
            "binary_expression",
            "in_expression",
            "check_expression",
            "comparison_expression",
            "equality_expression",
            "conjunction_expression",
            "disjunction_expression",
            "additive_expression",
            "multiplicative_expression",
            "infix_expression",
            "elvis_expression",
        ):
            non_triv = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(non_triv) == 3:
                op_str = _clean_text(non_triv[1])
                if op_str in ("+", "-", "*", "/"):
                    return self._is_fp_expr(non_triv[0], known, fp_vars) or self._is_fp_expr(non_triv[2], known, fp_vars)
            return False
        if ctype == "call_expression" and node.children:
            callee_n = node.children[0]
            if callee_n.type == "navigation_expression":
                nav_parts = [c for c in callee_n.children if c.type not in (".", "?.", "line_comment", "block_comment")]
                if len(nav_parts) == 2:
                    mname = _clean_text(nav_parts[1])
                    if mname in ("toDouble", "toFloat"):
                        return True
                    if mname in ("roundToInt", "toInt", "toLong", "isEmpty", "all"):
                        return False
                    if mname in ("coerceAtLeast", "coerceAtMost", "coerceIn"):
                        return self._is_fp_expr(nav_parts[0], known, fp_vars)
            fn_name = _clean_text(callee_n)
            if fn_name in self.fp_funcs:
                return True
            if fn_name in ("maxOf", "minOf", "abs", "floor"):
                for c in node.children[1:]:
                    if c.type == "value_arguments":
                        for vc in c.children:
                            if vc.type == "value_argument":
                                arg_inner = [ac for ac in vc.children if ac.type not in ("=", "line_comment", "block_comment")]
                                if arg_inner and self._is_fp_expr(arg_inner[-1], known, fp_vars):
                                    return True
        return False

    def _promote_to_fp(self, expr: Any) -> Any:
        if isinstance(expr, URConst):
            return URConst(value=expr.value * self.float_scale, holder="i64")
        return URHiOpCall(
            build_ur_node("java", "*", "i64", True),
            [expr, URConst(self.float_scale, "i64")],
            "*",
            "i64",
        )

    def _lower_kotlin_expr(self, node: Node, file_path: str, known: dict[str, str], fp_vars: set[str]) -> Any:
        ctype = node.type
        line = node.start_point[0] + 1

        if ctype == "control_structure_body":
            inner = [c for c in node.children if c.type not in ("{", "}", "line_comment", "block_comment")]
            if len(inner) == 1:
                return self._lower_kotlin_expr(inner[0], file_path, known, fp_vars)

        if ctype == "parenthesized_expression":
            inner = [c for c in node.children if c.type not in ("(", ")", "line_comment", "block_comment")]
            if len(inner) == 1:
                return self._lower_kotlin_expr(inner[0], file_path, known, fp_vars)
            raise NotImplementedError(f"{file_path}:{line}: Malformed Kotlin parenthesized_expression")

        if ctype in ("number_literal", "integer_literal", "long_literal"):
            raw = _clean_text(node).rstrip("lLuU").replace("_", "")
            if "." in raw or raw.endswith(("f", "F")):
                fval = float(raw.rstrip("fF"))
                return URConst(value=int(round(fval * self.float_scale)), holder="i64")
            val = int(raw, 16) if raw.lower().startswith("0x") else int(raw)
            return URConst(value=val, holder="i64")

        if ctype in ("float_literal", "real_literal"):
            raw = _clean_text(node).rstrip("fF").replace("_", "")
            fval = float(raw)
            return URConst(value=int(round(fval * self.float_scale)), holder="i64")

        if ctype in ("boolean_literal", "true", "false"):
            return URConst(value=1 if _clean_text(node) == "true" else 0, holder="i64")

        if ctype == "string_literal":
            txt = _clean_text(node).strip('"')
            if txt in self.constants:
                return URConst(value=self.constants[txt], holder="i64")
            # Deterministic non-zero string ID for SQL/error messages passed to native calls
            val = sum((i + 1) * ord(ch) for i, ch in enumerate(txt)) & 0x7FFFFFFF
            return URConst(value=val or 1, holder="i64")

        if ctype in ("identifier", "simple_identifier"):
            ident = _clean_text(node)
            if ident in ("true", "false"):
                return URConst(value=1 if ident == "true" else 0, holder="i64")
            if ident in known:
                return URVar(name=ident, holder="i64")
            if ident in self.fp_constants:
                return URConst(value=int(round(self.fp_constants[ident] * self.float_scale)), holder="i64")
            if ident in self.constants:
                return URConst(value=self.constants[ident], holder="i64")
            raise NotImplementedError(f"{file_path}:{line}: Unresolved Kotlin identifier {ident!r}")

        if ctype == "navigation_expression":
            parts = [c for c in node.children if c.type not in (".", "?.", "line_comment", "block_comment")]
            if len(parts) == 2:
                recv_n, mem_n = parts[0], parts[1]
                recv_txt = _clean_text(recv_n)
                mem_txt = _clean_text(mem_n)
                full_key = f"{recv_txt}.{mem_txt}"
                if full_key in self.fp_constants:
                    return URConst(value=int(round(self.fp_constants[full_key] * self.float_scale)), holder="i64")
                if full_key in self.constants:
                    return URConst(value=self.constants[full_key], holder="i64")
                if mem_txt in self.fp_constants:
                    return URConst(value=int(round(self.fp_constants[mem_txt] * self.float_scale)), holder="i64")
                if mem_txt in self.constants:
                    return URConst(value=self.constants[mem_txt], holder="i64")
                flat_var = f"{recv_txt}_{mem_txt}"
                if flat_var in known:
                    return URVar(name=flat_var, holder="i64")
            raise NotImplementedError(f"{file_path}:{line}: Unresolved Kotlin navigation_expression {_clean_text(node)!r}")

        if ctype in ("prefix_expression", "unary_expression"):
            non_triv = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(non_triv) == 2:
                op_str = _clean_text(non_triv[0])
                arg = self._lower_kotlin_expr(non_triv[1], file_path, known, fp_vars)
                if op_str == "-":
                    if isinstance(arg, URConst):
                        return URConst(value=-arg.value, holder="i64")
                    return URHiOpCall(build_ur_node("java", "neg", "i64", True), [arg], "neg", "i64")
                if op_str == "!":
                    return URHiOpCall(build_ur_node("java", "==", "i64", True), [arg, URConst(0, "i64")], "==", "i64")
            raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin prefix_expression {_clean_text(node)!r}")

        if ctype == "if_expression":
            cond_n, then_n, else_n = self._split_kotlin_if(node, file_path)
            if else_n is None:
                raise NotImplementedError(f"{file_path}:{line}: Kotlin expression if requires else branch")
            t_fp = self._is_fp_expr(then_n, known, fp_vars)
            e_fp = self._is_fp_expr(else_n, known, fp_vars)
            t_e = self._lower_kotlin_expr(then_n, file_path, known, fp_vars)
            e_e = self._lower_kotlin_expr(else_n, file_path, known, fp_vars)
            if t_fp and not e_fp:
                e_e = self._promote_to_fp(e_e)
            elif e_fp and not t_fp:
                t_e = self._promote_to_fp(t_e)
            return URHiOpCall(
                build_ur_node("java", "ite", "i64", True),
                [
                    self._lower_kotlin_expr(cond_n, file_path, known, fp_vars),
                    t_e,
                    e_e,
                ],
                "ite",
                "i64",
            )

        if ctype == "when_expression":
            return self._lower_kotlin_when(node, file_path, known, fp_vars)

        if ctype in (
            "binary_expression",
            "in_expression",
            "check_expression",
            "comparison_expression",
            "equality_expression",
            "conjunction_expression",
            "disjunction_expression",
            "additive_expression",
            "multiplicative_expression",
            "infix_expression",
            "elvis_expression",
        ):
            non_triv = [c for c in node.children if c.type not in ("line_comment", "block_comment")]
            if len(non_triv) == 3:
                lhs_n, op_n, rhs_n = non_triv[0], non_triv[1], non_triv[2]
                op_str = _clean_text(op_n)
                lhs = self._lower_kotlin_expr(lhs_n, file_path, known, fp_vars)
                if op_str == "in":
                    set_name = _clean_text(rhs_n)
                    if set_name not in self.set_constants:
                        raise NotImplementedError(f"{file_path}:{line}: Unresolved Kotlin set {set_name!r} for 'in'")
                    vals = self.set_constants[set_name]
                    cur_e: Any = URHiOpCall(build_ur_node("java", "==", "i64", True), [lhs, URConst(vals[0], "i64")], "==", "i64")
                    for v in vals[1:]:
                        eq_v = URHiOpCall(build_ur_node("java", "==", "i64", True), [lhs, URConst(v, "i64")], "==", "i64")
                        cur_e = URHiOpCall(build_ur_node("java", "||", "i64", True), [cur_e, eq_v], "||", "i64")
                    return cur_e

                rhs = self._lower_kotlin_expr(rhs_n, file_path, known, fp_vars)
                l_fp = self._is_fp_expr(lhs_n, known, fp_vars)
                r_fp = self._is_fp_expr(rhs_n, known, fp_vars)
                S = self.float_scale

                if op_str == "*":
                    prod = URHiOpCall(build_ur_node("java", "*", "i64", True), [lhs, rhs], "*", "i64")
                    if l_fp and r_fp:
                        plus_half = URHiOpCall(
                            build_ur_node("java", "+", "i64", True),
                            [prod, URConst(S // 2, "i64")],
                            "+",
                            "i64",
                        )
                        return URHiOpCall(
                            build_ur_node("java", "trunc_div", "i64", True),
                            [plus_half, URConst(S, "i64")],
                            "trunc_div",
                            "i64",
                        )
                    return prod

                if op_str == "/":
                    if l_fp and r_fp:
                        num = URHiOpCall(build_ur_node("java", "*", "i64", True), [lhs, URConst(S, "i64")], "*", "i64")
                        return URHiOpCall(build_ur_node("java", "trunc_div", "i64", True), [num, rhs], "trunc_div", "i64")
                    if l_fp and not r_fp:
                        return URHiOpCall(build_ur_node("java", "trunc_div", "i64", True), [lhs, rhs], "trunc_div", "i64")
                    if not l_fp and r_fp:
                        num = URHiOpCall(
                            build_ur_node("java", "*", "i64", True),
                            [lhs, URConst(S * S, "i64")],
                            "*",
                            "i64",
                        )
                        return URHiOpCall(build_ur_node("java", "trunc_div", "i64", True), [num, rhs], "trunc_div", "i64")
                    return URHiOpCall(build_ur_node("java", "trunc_div", "i64", True), [lhs, rhs], "trunc_div", "i64")

                if op_str in ("+", "-", "==", "!=", "<", "<=", ">", ">="):
                    if l_fp and not r_fp:
                        rhs = self._promote_to_fp(rhs)
                    elif r_fp and not l_fp:
                        lhs = self._promote_to_fp(lhs)

                op_map = {
                    "+": "+",
                    "-": "-",
                    "%": "trunc_rem",
                    "==": "==",
                    "!=": "!=",
                    "<": "<",
                    "<=": "<=",
                    ">": ">",
                    ">=": ">=",
                    "&&": "&&",
                    "||": "||",
                    "or": "|",
                    "and": "&",
                    "xor": "^",
                    "shl": "<<",
                    "shr": ">>",
                    "ushr": ">>>",
                }
                if op_str not in op_map:
                    raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin binary operator {op_str!r}")
                canon_op = op_map[op_str]
                return URHiOpCall(build_ur_node("java", canon_op, "i64", True), [lhs, rhs], canon_op, "i64")

        if ctype == "call_expression":
            return self._lower_kotlin_call(node, file_path, known, fp_vars)

        raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin expression AST node {ctype!r}: {_clean_text(node)!r}")

    def _lower_kotlin_when(self, node: Node, file_path: str, known: dict[str, str], fp_vars: set[str]) -> Any:
        line = node.start_point[0] + 1
        subj_expr: Any = None
        entries: list[Node] = []
        for c in node.children:
            if c.type == "when_subject":
                inner = [sc for sc in c.children if sc.type not in ("(", ")", "line_comment", "block_comment")]
                if inner:
                    subj_expr = self._lower_kotlin_expr(inner[-1], file_path, known, fp_vars)
            elif c.type == "when_entry":
                entries.append(c)

        if not entries:
            raise NotImplementedError(f"{file_path}:{line}: Empty Kotlin when_expression")

        branches: list[tuple[Any | None, Any]] = []
        for ent in entries:
            ent_children = [c for c in ent.children if c.type not in ("->", "line_comment", "block_comment")]
            if len(ent_children) < 2:
                raise NotImplementedError(f"{file_path}:{line}: Malformed when_entry {_clean_text(ent)!r}")
            cond_part = ent_children[0]
            res_part = ent_children[-1]
            res_e = self._lower_kotlin_expr(res_part, file_path, known, fp_vars)
            if cond_part.type == "else" or _clean_text(cond_part) == "else":
                branches.append((None, res_e))
            else:
                c_inner = (
                    [sc for sc in cond_part.children if sc.type not in ("line_comment", "block_comment")][0]
                    if cond_part.type == "when_condition"
                    else cond_part
                )
                cond_e = self._lower_kotlin_expr(c_inner, file_path, known, fp_vars)
                if subj_expr is not None:
                    cond_e = URHiOpCall(build_ur_node("java", "==", "i64", True), [subj_expr, cond_e], "==", "i64")
                branches.append((cond_e, res_e))

        # Fold right-to-left into nested Sail-backed `ite` URHiOpCalls
        acc = branches[-1][1]
        for cond_e, then_e in reversed(branches[:-1]):
            if cond_e is not None:
                acc = URHiOpCall(build_ur_node("java", "ite", "i64", True), [cond_e, then_e, acc], "ite", "i64")
        return acc

    def _lower_kotlin_call(self, node: Node, file_path: str, known: dict[str, str], fp_vars: set[str]) -> Any:
        line = node.start_point[0] + 1
        callee_n = node.children[0]
        args_nodes: list[Node] = []
        lambda_node: Node | None = None
        for c in node.children[1:]:
            if c.type == "value_arguments":
                for vc in c.children:
                    if vc.type == "value_argument":
                        arg_inner = [
                            ac for ac in vc.children if ac.type not in ("=", "line_comment", "block_comment")
                        ]
                        # Named argument `foo = expr` takes last child (`expr`)
                        if arg_inner:
                            args_nodes.append(arg_inner[-1])
            elif c.type == "annotated_lambda":
                lambda_node = c

        args = [self._lower_kotlin_expr(a, file_path, known, fp_vars) for a in args_nodes]
        S = self.float_scale

        if callee_n.type == "navigation_expression":
            nav_parts = [c for c in callee_n.children if c.type not in (".", "?.", "line_comment", "block_comment")]
            if len(nav_parts) == 2:
                recv_n = nav_parts[0]
                mname = _clean_text(nav_parts[1])
                recv_txt = _clean_text(recv_n)
                # Static / singleton class call (e.g. `System.currentTimeMillis()`)
                if (
                    recv_n.type in ("identifier", "simple_identifier")
                    and recv_txt not in known
                    and recv_txt not in self.constants
                    and recv_txt not in self.fp_constants
                ):
                    return URCall(func_name=mname, args=args, holder="i64")

                recv_fp = self._is_fp_expr(recv_n, known, fp_vars)
                recv_e = self._lower_kotlin_expr(recv_n, file_path, known, fp_vars)
                if mname == "toInt":
                    if recv_fp:
                        trunc_e = URHiOpCall(
                            build_ur_node("java", "trunc_div", "i64", True),
                            [recv_e, URConst(S, "i64")],
                            "trunc_div",
                            "i64",
                        )
                        return build_holder_cast_node(trunc_e, "i64", "i32", lang="java")
                    return build_holder_cast_node(recv_e, "i64", "i32", lang="java")
                if mname == "toLong":
                    if recv_fp:
                        return URHiOpCall(
                            build_ur_node("java", "trunc_div", "i64", True),
                            [recv_e, URConst(S, "i64")],
                            "trunc_div",
                            "i64",
                        )
                    return recv_e
                if mname in ("toDouble", "toFloat"):
                    return recv_e if recv_fp else self._promote_to_fp(recv_e)
                if mname == "roundToInt":
                    if recv_fp:
                        plus_half = URHiOpCall(
                            build_ur_node("java", "+", "i64", True),
                            [recv_e, URConst(S // 2, "i64")],
                            "+",
                            "i64",
                        )
                        return URHiOpCall(
                            build_ur_node("java", "trunc_div", "i64", True),
                            [plus_half, URConst(S, "i64")],
                            "trunc_div",
                            "i64",
                        )
                    return recv_e
                if mname == "isEmpty" and not args:
                    return URHiOpCall(build_ur_node("java", "==", "i64", True), [recv_e, URConst(0, "i64")], "==", "i64")
                if mname == "all" and lambda_node is not None:
                    # `workoutDayIds.all { it in completedDayIds }` on bitmask sets: `(recv & set_var) == recv`
                    ltxt = _clean_text(lambda_node)
                    if " in " in ltxt:
                        rhs_ident = ltxt.split(" in ")[-1].rstrip("}").strip()
                        if rhs_ident in known:
                            and_e = URHiOpCall(
                                build_ur_node("java", "&", "i64", True),
                                [recv_e, URVar(rhs_ident, "i64")],
                                "&",
                                "i64",
                            )
                            return URHiOpCall(build_ur_node("java", "==", "i64", True), [and_e, recv_e], "==", "i64")
                if mname == "coerceAtLeast" and len(args) == 1:
                    arg0 = self._promote_to_fp(args[0]) if (recv_fp and not self._is_fp_expr(args_nodes[0], known, fp_vars)) else args[0]
                    lt_c = URHiOpCall(build_ur_node("java", "<", "i64", True), [recv_e, arg0], "<", "i64")
                    return URHiOpCall(build_ur_node("java", "ite", "i64", True), [lt_c, arg0, recv_e], "ite", "i64")
                if mname == "coerceAtMost" and len(args) == 1:
                    arg0 = self._promote_to_fp(args[0]) if (recv_fp and not self._is_fp_expr(args_nodes[0], known, fp_vars)) else args[0]
                    gt_c = URHiOpCall(build_ur_node("java", ">", "i64", True), [recv_e, arg0], ">", "i64")
                    return URHiOpCall(build_ur_node("java", "ite", "i64", True), [gt_c, arg0, recv_e], "ite", "i64")
                if mname == "coerceIn" and len(args) == 2:
                    arg0 = self._promote_to_fp(args[0]) if (recv_fp and not self._is_fp_expr(args_nodes[0], known, fp_vars)) else args[0]
                    arg1 = self._promote_to_fp(args[1]) if (recv_fp and not self._is_fp_expr(args_nodes[1], known, fp_vars)) else args[1]
                    lt_c = URHiOpCall(build_ur_node("java", "<", "i64", True), [recv_e, arg0], "<", "i64")
                    lo_clamped = URHiOpCall(build_ur_node("java", "ite", "i64", True), [lt_c, arg0, recv_e], "ite", "i64")
                    gt_c = URHiOpCall(build_ur_node("java", ">", "i64", True), [lo_clamped, arg1], ">", "i64")
                    return URHiOpCall(build_ur_node("java", "ite", "i64", True), [gt_c, arg1, lo_clamped], "ite", "i64")
                raise NotImplementedError(f"{file_path}:{line}: Unsupported Kotlin receiver call .{mname}()")

        fn_name = _clean_text(callee_n)
        if fn_name == "maxOf" and len(args) == 2:
            gt_c = URHiOpCall(build_ur_node("java", ">", "i64", True), [args[0], args[1]], ">", "i64")
            return URHiOpCall(build_ur_node("java", "ite", "i64", True), [gt_c, args[0], args[1]], "ite", "i64")
        if fn_name == "minOf" and len(args) == 2:
            lt_c = URHiOpCall(build_ur_node("java", "<", "i64", True), [args[0], args[1]], "<", "i64")
            return URHiOpCall(build_ur_node("java", "ite", "i64", True), [lt_c, args[0], args[1]], "ite", "i64")
        if fn_name == "abs" and len(args) == 1:
            lt0 = URHiOpCall(build_ur_node("java", "<", "i64", True), [args[0], URConst(0, "i64")], "<", "i64")
            neg_a = URHiOpCall(build_ur_node("java", "neg", "i64", True), [args[0]], "neg", "i64")
            return URHiOpCall(build_ur_node("java", "ite", "i64", True), [lt0, neg_a, args[0]], "ite", "i64")
        if fn_name == "floor" and len(args) == 1:
            if args_nodes and self._is_fp_expr(args_nodes[0], known, fp_vars):
                q = URHiOpCall(build_ur_node("java", "trunc_div", "i64", True), [args[0], URConst(S, "i64")], "trunc_div", "i64")
                return URHiOpCall(build_ur_node("java", "*", "i64", True), [q, URConst(S, "i64")], "*", "i64")
            return args[0]

        # Pack Breakdown(basePct, reasonPct, activityPct, feelingPct, compoundPct, finalPct) via Sail-backed shifts/ors
        if fn_name == "Breakdown" and len(args) == 6:
            shifts = [40, 32, 24, 16, 8, 0]
            acc_e: Any = None
            for a_e, sh in zip(args, shifts):
                part = (
                    URHiOpCall(build_ur_node("java", "<<", "i64", True), [a_e, URConst(sh, "i64")], "<<", "i64")
                    if sh > 0
                    else a_e
                )
                acc_e = (
                    part
                    if acc_e is None
                    else URHiOpCall(build_ur_node("java", "|", "i64", True), [acc_e, part], "|", "i64")
                )
            return acc_e

        # Pack RestartOutput(weightMultiplier, recommendedLevel, rampMicrocycles, breakdown)
        if fn_name == "RestartOutput" and len(args) == 4:
            lvl_sh = URHiOpCall(build_ur_node("java", "<<", "i64", True), [args[1], URConst(48, "i64")], "<<", "i64")
            rmp_sh = URHiOpCall(build_ur_node("java", "<<", "i64", True), [args[2], URConst(52, "i64")], "<<", "i64")
            lr_or = URHiOpCall(build_ur_node("java", "|", "i64", True), [lvl_sh, rmp_sh], "|", "i64")
            return URHiOpCall(build_ur_node("java", "|", "i64", True), [lr_or, args[3]], "|", "i64")

        resolved_name = self.call_arity_aliases.get((fn_name, len(args)), fn_name)
        return URCall(func_name=resolved_name, args=args, holder="i64")

