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
        op = next((c.type for c in node.children if c.type in _OP_TOKENS), None)
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
        return f"{fn}({self._render_args(args_node)})"

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
