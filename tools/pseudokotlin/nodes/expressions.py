"""
expressions.py — expression handlers. Each returns a Python expression STRING it
guarantees parses (MAP), routes a no-Python-equivalent to a shim (WRAP, e.g.
16.dp -> dp(16)), or raises Untranspilable (FAIL). Node-kind names are this
grammar's actual named kinds (verified against parse.named_kinds()).
"""
import keyword
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind, Untranspilable  # noqa: E402
from util import block as _block  # noqa: E402

_PY_KEYWORDS = frozenset(keyword.kwlist)
_BINOP = {"&&": "and", "||": "or", "===": "is", "!==": "is not"}
_OP_TOKENS = {"+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=",
              "&&", "||", "===", "!==", "&", "|", "^", "<<", ">>"}
_UNIT_EXT = {"dp": "dp", "sp": "sp", "em": "em"}
_NUMBER_KINDS = {"number_literal", "float_literal"}


class Expressions:
    # ---- atoms ----------------------------------------------------------- #
    @kind("identifier")
    def v_identifier(self, node):
        t = self.text(node)
        const = {"null": "None", "true": "True", "false": "False"}
        if t in const:
            return const[t]
        if t in self._members and not any(t in s for s in self._scopes):
            return f"self.{t}"
        return t

    @kind("this_expression")
    def v_this(self, node):
        return "self"

    @kind("super_expression")
    def v_super(self, node):
        return "super()"

    @kind("number_literal", "float_literal")
    def v_number(self, node):
        return self.text(node).replace("_", "").rstrip("LFfuU") or "0"

    @kind("character_literal")
    def v_char(self, node):
        return self.text(node).replace("'", '"', 2)

    @kind("string_literal", "multiline_string_literal")
    def v_string(self, node):
        return self._string_to_fstring(node)

    # ---- operators ------------------------------------------------------- #
    @kind("binary_expression")
    def v_binary(self, node):
        kids = self.named(node)
        left, right = self.visit(kids[0]), self.visit(kids[-1])
        op = next((c.type for c in node.children
                   if c.type in _OP_TOKENS or c.type == "?:"), None)
        if op == "?:":                                  # elvis: a ?: b
            return f"({left} if {left} is not None else {right})"
        if op is None:
            raise Untranspilable(node, "binary expression without a known operator")
        return f"{left} {_BINOP.get(op, op)} {right}"

    @kind("unary_expression")
    def v_unary(self, node):
        s = self.visit(self.named(node)[0])
        ops = [c.type for c in node.children if not c.is_named]
        if "!!" in ops:
            return s                       # not-null assert -> drop
        if "!" in ops:
            return f"(not {s})"
        if "-" in ops:
            return f"-{s}"
        if "+" in ops:
            return f"+{s}"
        raise Untranspilable(node, f"unsupported unary operator {ops}")

    @kind("in_expression")
    def v_in(self, node):
        kids = self.named(node)
        neg = any(c.type == "!in" for c in node.children)
        return f"({self.visit(kids[0])} {'not in' if neg else 'in'} {self.visit(kids[-1])})"

    @kind("is_expression")
    def v_is(self, node):
        kids = self.named(node)
        neg = any(c.type == "!is" for c in node.children)
        call = f"isinstance({self.visit(kids[0])}, {self.visit(kids[-1])})"
        return f"(not {call})" if neg else call

    @kind("parenthesized_expression")
    def v_paren(self, node):
        return f"({self.visit(self.named(node)[0])})"

    # ---- access / call --------------------------------------------------- #
    @kind("navigation_expression")
    def v_navigation(self, node):
        kids = self.named(node)
        recv = kids[0]
        sel = self.text(kids[-1]) if len(kids) > 1 else ""
        if recv.type in _NUMBER_KINDS and sel in _UNIT_EXT:      # WRAP: 16.dp -> dp(16)
            return f"{_UNIT_EXT[sel]}({self.visit(recv)})"
        left = self.visit(recv)
        attr = sel + "_" if sel in _PY_KEYWORDS else sel
        if any(c.type == "?." for c in node.children):
            return f"({left}.{attr} if {left} is not None else None)"
        return f"{left}.{attr}"

    @kind("call_expression")
    def v_call(self, node):
        kids = self.named(node)
        fn = self.visit(kids[0])
        args_node = next((c for c in node.children if c.type == "value_arguments"), None)
        args = self._render_args(args_node)
        trailing = next((c for c in node.named_children
                         if c.type in ("annotated_lambda", "lambda_literal")), None)
        if trailing is not None:                       # `xs.map { v -> v*2 }`
            lam = trailing
            if lam.type == "annotated_lambda":
                lam = next((c for c in lam.named_children if c.type == "lambda_literal"), lam)
            lam_str = self.visit(lam)
            args = f"{args}, {lam_str}" if args else lam_str
        return f"{fn}({args})"

    @kind("collection_literal")
    def v_collection(self, node):
        return "[" + ", ".join(self.visit(c) for c in self.named(node)) + "]"

    @kind("range_expression")
    def v_range(self, node):
        kids = self.named(node)
        return f"range({self.visit(kids[0])}, {self.visit(kids[-1])} + 1)"

    @kind("infix_expression")
    def v_infix(self, node):
        kids = self.named(node)
        left, right = kids[0], kids[-1]
        op = self.text(kids[1])                         # the middle identifier
        l, r = self.visit(left), self.visit(right)
        if op == "to":
            return f"({l}, {r})"
        if op == "until":
            return f"range({l}, {r})"
        if op == "downTo":
            return f"range({l}, {r} - 1, -1)"
        if op == "step" and left.type == "range_expression":
            rk = self.named(left)
            return f"range({self.visit(rk[0])}, {self.visit(rk[-1])} + 1, {r})"
        return f"{l}.{op}({r})"                          # generic infix -> method

    @kind("lambda_literal")
    def v_lambda(self, node):
        pnode = next((c for c in node.named_children if c.type == "lambda_parameters"), None)
        params = []
        if pnode is not None:
            for vd in pnode.named_children:
                pid = next((c for c in vd.children if c.type == "identifier"), None)
                if pid is not None:
                    params.append(self.text(pid))
        ps = ", ".join(params) if params else "it=None"
        body = [c for c in self.named(node) if c.type != "lambda_parameters"]
        if not body:
            return f"(lambda {ps}: None)"
        if len(body) == 1 and self.is_value(body[0]):
            return f"(lambda {ps}: {self.visit(body[0])})"
        # multi-statement (or statement-bodied) lambda has no Python lambda form ->
        # hoist a named def; the suite renderer flushes it before the using statement.
        self._lam += 1
        name = f"_lam{self._lam}"
        *head, last = body
        lines = self.render_statements(head)
        before = len(self._hoist)
        last_s = self.visit(last)
        lines += self._hoist[before:]
        del self._hoist[before:]
        lines.append(f"return {last_s}" if self.is_value(last) else last_s)
        self._hoist.append(f"def {name}({ps}):\n{_block(lines)}")
        return name

    @kind("callable_reference")
    def v_callable_ref(self, node):
        return self.text(node).replace("::", ".").lstrip(".")

    @kind("qualified_identifier")
    def v_qualified(self, node):
        return self.text(node)

    @kind("spread_expression")
    def v_spread(self, node):
        kids = self.named(node)
        return f"*{self.visit(kids[0])}" if kids else "*[]"

    @kind("annotated_expression")
    def v_annotated_expr(self, node):
        return self.visit(self.named(node)[-1])         # strip annotation

    @kind("labeled_expression")
    def v_labeled_expr(self, node):
        return self.visit(self.named(node)[-1])         # strip label

    @kind("index_expression")
    def v_index(self, node):
        kids = self.named(node)
        idxs = ", ".join(self.visit(k) for k in kids[1:]) or "0"
        return f"{self.visit(kids[0])}[{idxs}]"

    @kind("as_expression")
    def v_as(self, node):
        return self.visit(self.named(node)[0])   # Python is dynamic: `x as T` -> x

    # ---- helpers --------------------------------------------------------- #
    def _render_args(self, args_node):
        if not args_node:
            return ""
        parts = []
        for a in args_node.named_children:
            if a.type != "value_argument":
                continue
            kids = a.named_children
            if any(c.type == "=" for c in a.children) and len(kids) > 1:
                parts.append(f"{self.text(kids[0])}={self.visit(kids[-1])}")
            elif kids:
                parts.append(self.visit(kids[-1]))
        return ", ".join(parts)

    def _string_to_fstring(self, node):
        segs, interp = [], False
        for c in node.children:
            if c.type in ('"', '"""', "'"):
                continue
            if c.type == "interpolation":
                interp = True
                inner = next((k for k in c.named_children), None)
                segs.append("{" + (self.visit(inner) if inner else "") + "}")
            else:
                segs.append(self.text(c).replace("{", "{{").replace("}", "}}"))
        body = "".join(segs)
        if not interp:
            return '"' + body.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if '"' not in body:
            return 'f"' + body + '"'
        if "'" not in body:
            return "f'" + body + "'"
        return 'f"""' + body + '"""'
