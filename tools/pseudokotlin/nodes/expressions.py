"""
expressions.py — expression handlers. Each returns a Python expression STRING it
guarantees parses (MAP), routes a no-Python-equivalent to a shim (WRAP, e.g.
16.dp -> dp(16)), or raises Untranspilable (FAIL). Node-kind names are this
grammar's actual named kinds (verified against parse.named_kinds()).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind, Untranspilable  # noqa: E402
from util import block as _block  # noqa: E402

_BINOP = {"&&": "and", "||": "or", "===": "is", "!==": "is not"}
_OP_TOKENS = {"+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=",
              "&&", "||", "===", "!==", "&", "|", "^", "<<", ">>"}
_UNIT_EXT = {"dp": "dp", "sp": "sp", "em": "em"}
_NUMBER_KINDS = {"number_literal", "float_literal"}

# Kotlin stdlib methods with no Python builtin -> rewritten at the CALL site (Python
# builtins can't carry them). recv + positional arg strings -> a Python expression.
# Scalar/string Kotlin stdlib methods with no Python builtin. Collection methods are
# NOT here -- they dispatch to the KtList/KtMap runtime types (kotlin_rt) so chains
# stay typed; only string/number ops and `.asSequence` (a no-op) live at the call site.
_STDLIB_METHODS = {
    "isEmpty":       lambda r, a: f"(len({r}) == 0)",     # works on str + any sized
    "isNotEmpty":    lambda r, a: f"(len({r}) != 0)",
    "isBlank":       lambda r, a: f"(len({r}.strip()) == 0)",
    "isNotBlank":    lambda r, a: f"(len({r}.strip()) != 0)",
    "coerceAtMost":  lambda r, a: f"min({r}, {a[0]})",
    "coerceAtLeast": lambda r, a: f"max({r}, {a[0]})",
    "coerceIn":      lambda r, a: f"max({a[0]}, min({r}, {a[1]}))",
    "roundToInt":    lambda r, a: f"roundToInt({r})",
    "roundToLong":   lambda r, a: f"roundToLong({r})",
    "asSequence":    lambda r, a: f"{r}",                 # lazy seq -> identity (iterable)
}
# Kotlin stdlib PROPERTIES (no call) rewritten at the navigation site. `size` falls
# back to len() for any sized receiver (KtList also has a .size property of its own).
_STDLIB_PROPS = {"size": lambda r: f"len({r})"}


class Expressions:
    # ---- atoms ----------------------------------------------------------- #
    @kind("identifier")
    def v_identifier(self, node):
        t = self.text(node)
        const = {"null": "None", "true": "True", "false": "False"}
        if t in const:
            return const[t]
        shadowed = any(t in s for s in self._scopes)
        if not shadowed and t in self._static_members:      # companion -> ClassName.x
            return f"{self._static_class}.{self._safe(t)}"
        if not shadowed and t in self._members:             # instance member -> self.x
            return f"self.{self._safe(t)}"
        return self._safe(t)

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
            if not self.is_value(kids[-1]):             # a ?: return/throw -> guard
                self._lam += 1                          # `val x = e ?: return d` becomes
                tmp = f"_elv{self._lam}"                # tmp = e; if tmp is None: <stmt>
                self._hoist.append(
                    f"{tmp} = {left}\nif {tmp} is None:\n{_block([right])}")
                return tmp
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
        # ++ / -- have no Python operator; render the mutation as an augmented
        # assignment STATEMENT (Python forbids the value-of-increment idiom, so the
        # pre/post distinction collapses -- faithful only in statement position).
        if "++" in ops:
            return f"{s} += 1"
        if "--" in ops:
            return f"{s} -= 1"
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
        safe_call = any(c.type == "?." for c in node.children)
        if sel in _STDLIB_PROPS and not safe_call:               # WRAP: xs.size -> len(xs)
            return _STDLIB_PROPS[sel](self.visit(recv))
        left = self.visit(recv)
        attr = self._safe(sel)
        if safe_call:
            return f"({left}.{attr} if {left} is not None else None)"
        return f"{left}.{attr}"

    @kind("call_expression")
    def v_call(self, node):
        kids = self.named(node)
        callee = kids[0]
        own_args = next((c for c in node.children if c.type == "value_arguments"), None)
        trailing = next((c for c in node.named_children
                         if c.type in ("annotated_lambda", "lambda_literal")), None)
        # `f(args) { lambda }` parses as (f(args))(lambda) -- the trailing lambda is an
        # EXTRA argument to the inner call, not a second call. Merge it in.
        if trailing is not None and callee.type == "call_expression" and own_args is None:
            in_args = self._render_args(next((c for c in callee.children
                                              if c.type == "value_arguments"), None))
            in_fn = self.visit(self.named(callee)[0])
            lam = self._lambda_str(trailing)
            return f"{in_fn}({f'{in_args}, {lam}' if in_args else lam})"
        if callee.type == "navigation_expression" \
                and not any(c.type == "?." for c in callee.children):
            nk = self.named(callee)
            sel = self.text(nk[-1]) if len(nk) > 1 else ""
            if sel in _STDLIB_METHODS:                  # WRAP: recv.coerceIn(...) -> min/max
                return _STDLIB_METHODS[sel](self.visit(nk[0]), self._arg_values(node))
        fn = self.visit(callee)
        args = self._render_args(own_args)
        if trailing is not None:                       # `xs.map { v -> v*2 }`
            lam = self._lambda_str(trailing)
            args = f"{args}, {lam}" if args else lam
        return f"{fn}({args})"

    def _lambda_str(self, trailing):
        lam = trailing
        if lam.type == "annotated_lambda":
            lam = next((c for c in lam.named_children if c.type == "lambda_literal"), lam)
        return self.visit(lam)

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
        return f"{l}.{self._safe(op)}({r})"              # generic infix -> method

    @kind("lambda_literal")
    def v_lambda(self, node):
        pnode = next((c for c in node.named_children if c.type == "lambda_parameters"), None)
        params = []
        if pnode is not None:
            for vd in pnode.named_children:
                pid = next((c for c in vd.children if c.type == "identifier"), None)
                if pid is not None:
                    params.append(self._safe(self.text(pid)))
        ps = ", ".join(params) if params else "it=None"
        body = [c for c in self.named(node) if c.type != "lambda_parameters"]
        if not body:
            return f"(lambda {ps}: None)"
        if len(body) == 1 and not self._renders_stmt(body[0]):   # pure expr body only
            return f"(lambda {ps}: {self.visit(body[0])})"
        # multi-statement (or statement-bodied) lambda has no Python lambda form ->
        # hoist a named def; the suite renderer flushes it before the using statement.
        self._lam += 1
        name = f"_lam{self._lam}"
        *head, last = body
        lines = self.render_statements(head)
        before = len(self._hoist)
        last_line = self._distribute(last, "return ")   # block-if/when/stmt-aware
        lines += self._hoist[before:]
        del self._hoist[before:]
        lines.append(last_line)
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
    def _arg_values(self, call_node):
        """Positional argument value strings (+ a trailing lambda) for a call -- used
        by the stdlib-method WRAP, which takes positional args only."""
        out = []
        an = next((c for c in call_node.children if c.type == "value_arguments"), None)
        if an is not None:
            for a in an.named_children:
                if a.type == "value_argument" and a.named_children:
                    out.append(self.visit(a.named_children[-1]))
        tl = next((c for c in call_node.named_children
                   if c.type in ("annotated_lambda", "lambda_literal")), None)
        if tl is not None:
            lam = tl if tl.type == "lambda_literal" \
                else next((c for c in tl.named_children if c.type == "lambda_literal"), tl)
            out.append(self.visit(lam))
        return out

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
