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
    "isNullOrBlank": lambda r, a: f"({r} is None or len({r}.strip()) == 0)",
    "isNullOrEmpty": lambda r, a: f"({r} is None or len({r}) == 0)",
    "coerceAtMost":  lambda r, a: f"min({r}, {a[0]})",
    "coerceAtLeast": lambda r, a: f"max({r}, {a[0]})",
    "coerceIn":      lambda r, a: f"max({a[0]}, min({r}, {a[1]}))",
    "floorDiv":      lambda r, a: f"({r} // {a[0]})",     # Kotlin Int.floorDiv == Python // (both floor)
    "roundToInt":    lambda r, a: f"roundToInt({r})",
    "roundToLong":   lambda r, a: f"roundToLong({r})",
    "toDouble":      lambda r, a: f"float({r})",          # numeric conversions
    "toFloat":       lambda r, a: f"float({r})",
    "toInt":         lambda r, a: f"int({r})",
    "toLong":        lambda r, a: f"int({r})",
    "toString":      lambda r, a: f"str({r})",
    "asSequence":    lambda r, a: f"{r}",                 # lazy seq -> identity (iterable)
    # ---- Kotlin String methods (names differ from Python's str) ---- #
    "lowercase":     lambda r, a: f"{r}.lower()",
    "uppercase":     lambda r, a: f"{r}.upper()",
    "trim":          lambda r, a: f"{r}.strip()",
    "trimStart":     lambda r, a: f"{r}.lstrip()",
    "trimEnd":       lambda r, a: f"{r}.rstrip()",
    "startsWith":    lambda r, a: f"{r}.startswith({a[0]})",
    "endsWith":      lambda r, a: f"{r}.endswith({a[0]})",
    "contains":      lambda r, a: f"({a[0]} in {r})",     # str/collection membership
    "split":         lambda r, a: f"KtList({r}.split({a[0]}))",
    "substring":     lambda r, a: (f"{r}[{a[0]}:{a[1]}]" if len(a) > 1
                                   else f"{r}[{a[0]}:]"),
    "replaceFirstChar": lambda r, a: f"(({a[0]}({r}[0]) + {r}[1:]) if {r} else {r})",
    "toRegex":       lambda r, a: f"Regex({r})",
    # str.replace(Regex, repl) is a REGEX replace; replace(str, repl) is literal
    "replace":       lambda r, a: (f"({a[0]}.replace({r}, {a[1]}) "
                                   f"if isinstance({a[0]}, Regex) "
                                   f"else {r}.replace({a[0]}, {a[1]}))"),
}
# Kotlin stdlib PROPERTIES (no call) rewritten at the navigation site. `size` falls
# back to len() for any sized receiver (KtList also has a .size property of its own).
_STDLIB_PROPS = {
    "size": lambda r: f"len({r})",
    "first": lambda r: f"{r}[0]",       # range/list .first / Pair.first (a to b -> tuple)
    "second": lambda r: f"{r}[1]",      # Pair.second / Triple.second
    "third": lambda r: f"{r}[2]",       # Triple.third
    "last": lambda r: f"{r}[-1]",       # .last property (end/last element)
    "lastIndex": lambda r: f"(len({r}) - 1)",
    "indices": lambda r: f"KtList(range(len({r})))",
    "length": lambda r: f"len({r})",    # String.length
}

# Kotlin scope functions `x.let/also/takeIf/takeUnless { … }` -- the lambda (which uses
# `it`) is applied to the receiver. Handled at the call site (they apply to ANY type, so
# no runtime method works) and aware of `?.` safe-call. recv, lambda-str, is-safe-call.
_SCOPE_FNS = {
    "let":        lambda r, f, s: f"({f}({r}) if {r} is not None else None)" if s
                                  else f"{f}({r})",
    "takeIf":     lambda r, f, s: f"({r} if {f}({r}) else None)",
    "takeUnless": lambda r, f, s: f"({r} if not {f}({r}) else None)",
    "also":       lambda r, f, s: f"({f}({r}), {r})[1]",      # run for effect, return recv
}


class Expressions:
    # ---- atoms ----------------------------------------------------------- #
    @kind("identifier")
    def v_identifier(self, node):
        t = self.text(node)
        # `continue`/`break` (label-less) parse as identifiers in this grammar -> emit the
        # Python loop statements verbatim, not a mangled identifier.
        const = {"null": "None", "true": "True", "false": "False",
                 "continue": "continue", "break": "break"}
        if t in const:
            return const[t]
        if t in self._delegated:                            # `val/var x by D` -> read/write via x.value
            return f"{self._safe(t)}.value"
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
        # strip Kotlin's numeric-type suffixes. For a hex literal, F/f are DIGITS (not the float
        # suffix), so a color like 0xFF38256E must keep them -- only L/u/U can trail hex.
        t = self.text(node).replace("_", "")
        return (t.rstrip("LuU") if t[:2].lower() == "0x" else t.rstrip("LFfuU")) or "0"

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
        op = next((c.type for c in node.children
                   if c.type in _OP_TOKENS or c.type == "?:"), None)
        # `func<Type>(args)` is a grammar ambiguity parsed as (func < Type) > (args);
        # it's really a generic call -- drop the type argument.
        if op == ">" and kids[0].type == "binary_expression" \
                and kids[-1].type == "parenthesized_expression" \
                and any(c.type == "<" for c in kids[0].children):
            fn = self.visit(self.named(kids[0])[0])
            inner = self.named(kids[-1])
            return f"{fn}({self.visit(inner[0]) if inner else ''})"
        left, right = self.visit(kids[0]), self.visit(kids[-1])
        if op == "?:":                                  # elvis: a ?: b
            rhs = kids[-1]                               # a ?: return/throw/continue/break -> guard
            cf = not self.is_value(rhs) or (             # (continue/break parse as identifiers, so
                rhs.type == "identifier"                 #  check text -- control flow is not a value
                and self.text(rhs) in ("continue", "break"))
            if cf:
                self._lam += 1                          # `val x = e ?: continue` becomes
                tmp = f"_elv{self._lam}"                # tmp = e; if tmp is None: <stmt>
                self._hoist.append(
                    f"{tmp} = {left}\nif {tmp} is None:\n{_block([right])}")
                return tmp
            return f"({left} if {left} is not None else {right})"
        if op is None:
            raise Untranspilable(node, "binary expression without a known operator")
        if op in ("+", "-") and kids[0].type == "character_literal":
            if op == "-" and kids[-1].type == "character_literal":   # Char - Char = Int
                return f"(ord({left}) - ord({right}))"
            sign = "+" if op == "+" else "-"                         # Char +/- Int = Char
            return f"chr(ord({left}) {sign} {right})"
        if op == "+":   # Kotlin "str" + any concatenates (coerces); Python str+int errors
            strs = ("string_literal", "multiline_string_literal")
            if kids[0].type in strs:
                return f"({left} + str({right}))"
            if kids[-1].type in strs:
                return f"(str({left}) + {right})"
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
        # ++ / -- in VALUE position (`${n++}`, `f(order++)`): Python has no value-of-
        # increment, so hoist `_inc = n; n += 1` (postfix returns old, prefix new) and
        # use the temp. Statement position is handled cleanly by _maybe_increment.
        if "++" in ops or "--" in ops:
            op = "+=" if "++" in ops else "-="
            prefix = node.children[0].type in ("++", "--")
            self._lam += 1
            tmp = f"_inc{self._lam}"
            self._hoist.append(f"{s} {op} 1\n{tmp} = {s}" if prefix
                               else f"{tmp} = {s}\n{s} {op} 1")
            return tmp
        raise Untranspilable(node, f"unsupported unary operator {ops}")

    @kind("in_expression")
    def v_in(self, node):
        kids = self.named(node)
        neg = any(c.type == "!in" for c in node.children)
        left, right = self.visit(kids[0]), kids[-1]
        if right.type == "range_expression":    # `x in a..b` is membership: a <= x <= b
            rk = self.named(right)               # (NOT iteration -- works for floats too)
            expr = f"({self.visit(rk[0])} <= {left} <= {self.visit(rk[-1])})"
            return f"(not {expr})" if neg else expr
        if right.type == "infix_expression" and self.text(self.named(right)[1]) == "until":
            rk = self.named(right)               # `x in a until b` -> a <= x < b
            expr = f"({self.visit(rk[0])} <= {left} < {self.visit(rk[-1])})"
            return f"(not {expr})" if neg else expr
        return f"({left} {'not in' if neg else 'in'} {self.visit(right)})"

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
    @staticmethod
    def _strip_prefix(x, pre):
        """undo a prematurely-lifted leading prefix on a visited receiver (so it can re-wrap the
        whole postfix expr at the top). `(not X)` -> X for `!`; a leading `-`/`+` -> dropped."""
        if pre == "!" and x.startswith("(not ") and x.endswith(")"):
            return x[5:-1]
        if pre in ("-", "+") and x.startswith(pre):
            return x[1:]
        return x

    @kind("navigation_expression")
    def v_navigation(self, node):
        kids = self.named(node)
        recv = kids[0]
        sel = self.text(kids[-1]) if len(kids) > 1 else ""
        safe_call = any(c.type == "?." for c in node.children)
        # grammar quirk: a leading `!`/`-`/`+` down the receiver chain parses as (!w).sel but
        # MEANS !(w.sel) -- the prefix binds looser than the dot. Strip + re-wrap at each level
        # so it bubbles to the outermost postfix expr.
        pre = self._leading_prefix(recv)
        base = self._navigate(recv, sel, safe_call, node, pre)
        return f"(not {base})" if pre == "!" else (f"{pre}{base}" if pre else base)

    def _navigate(self, recv, sel, safe_call, node, pre=None):
        left0 = lambda: self._strip_prefix(self.visit(recv), pre)   # noqa: E731
        if recv.type in _NUMBER_KINDS and sel in _UNIT_EXT:      # WRAP: 16.dp -> dp(16)
            return f"{_UNIT_EXT[sel]}({left0()})"
        if sel in _STDLIB_PROPS and not safe_call:               # WRAP: xs.size -> len(xs)
            return _STDLIB_PROPS[sel](left0())
        left = left0()
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
            in_args_node = next((c for c in callee.children
                                 if c.type == "value_arguments"), None)
            in_args = self._render_args(in_args_node)
            in_fn = self.visit(self.named(callee)[0])
            lam = self._lambda_str(trailing)
            return f"{in_fn}({self._join_trailing(in_args, lam, in_args_node)})"
        if callee.type == "navigation_expression":
            nk = self.named(callee)
            sel = self.text(nk[-1]) if len(nk) > 1 else ""
            safe = any(c.type == "?." for c in callee.children)
            # grammar quirk: a leading `!`/`-`/`+` anywhere down the receiver chain parses
            # tightly but MEANS the whole call -- `!a.b.f()` is `!(a.b.f())`. v_navigation lifts
            # it one level early; detect it at the chain's leftmost leaf, strip the (premature)
            # prefix off the visited receiver, and re-wrap the whole call. (No-op without one.)
            pre = self._leading_prefix(nk[0])

            def _wrap(x):
                return f"(not {x})" if pre == "!" else (f"{pre}{x}" if pre else x)

            recv = self._strip_prefix(self.visit(nk[0]), pre)
            if sel in ("ifEmpty", "ifBlank") and trailing is not None:
                g = self._empty_guard(recv, sel, self._lambda_node(trailing))
                if g is not None:                            # `s.ifEmpty { continue }` -> guard
                    return _wrap(g)
            if sel in _SCOPE_FNS and trailing is not None:   # x.let { it… } -> f(x)
                lam = self._lambda_node(trailing)
                if self._has_nonlocal_return(lam):      # `x?.let { return it }` guard:
                    if sel == "let":                    # the return exits the ENCLOSING fn
                        return self._let_guard(nk[0], lam, safe)
                    raise Untranspilable(node, f"non-local return in {sel} {{ … }}")
                return _wrap(_SCOPE_FNS[sel](recv, self._lambda_str(trailing), safe))
            if sel in _STDLIB_METHODS and not safe:     # WRAP: recv.coerceIn(...) -> min/max
                return _wrap(_STDLIB_METHODS[sel](recv, self._arg_values(node)))
            # general method call -- build recv.sel(args) from the receiver+selector so the
            # navigation PROPERTY mappings (.first -> [0], .size -> len) don't fire on a
            # method CALL (`it.first()` is a method; `it.first` is the property).
            args = self._render_args(own_args)
            if trailing is not None:
                lam = self._lambda_str(trailing)
                args = self._join_trailing(args, lam, own_args)
            call = f"{recv}.{self._safe(sel)}({args})"
            return _wrap(f"({call} if {recv} is not None else None)" if safe else call)
        fn = self.visit(callee)
        args = self._render_args(own_args)
        if trailing is not None:                       # `xs.map { v -> v*2 }`
            lam = self._lambda_str(trailing)
            args = self._join_trailing(args, lam, own_args)
        return f"{fn}({args})"

    def _leading_prefix(self, node):
        """the `!`/`-`/`+` at the leftmost leaf of a receiver chain (the grammar binds it tightly
        but it means the whole postfix expr). Stops at parentheses -- `(!x).f()` is explicit."""
        n = node
        while True:
            if n.type == "unary_expression":
                ops = [c.type for c in n.children if not c.is_named]
                return next((o for o in ("!", "-", "+") if o in ops), None)
            if n.type in ("navigation_expression", "call_expression") and self.named(n):
                n = self.named(n)[0]
            else:
                return None

    def _lambda_node(self, trailing):
        if trailing.type == "annotated_lambda":
            return next((c for c in trailing.named_children
                         if c.type == "lambda_literal"), trailing)
        return trailing

    def _lambda_str(self, trailing):
        return self.visit(self._lambda_node(trailing))

    def _has_nonlocal_return(self, node):
        # a `return` anywhere in an inline lambda body returns from the ENCLOSING fn;
        # stop at nested lambda/function boundaries (those have their own return scope).
        for c in node.children:
            if c.type == "return_expression":
                return True
            if c.type in ("lambda_literal", "function_declaration", "anonymous_function"):
                continue
            if self._has_nonlocal_return(c):
                return True
        return False

    def _let_guard(self, recv_node, lam, safe):
        # `recv[?].let { … return … }` -> evaluate recv once, bind the lambda param, run
        # the body as statements (its `return` is the enclosing fn's). Hoisted before the
        # using statement; the expression value is None (used in statement position).
        self._lam += 1
        tmp = f"_let{self._lam}"
        recv = self.visit(recv_node)
        pname = self._lambda_param(lam)
        body = [c for c in self.named(lam) if c.type != "lambda_parameters"]
        inner = [f"{pname} = {tmp}"] + self.render_statements(body)
        if safe:
            block = [f"{tmp} = {recv}", f"if {tmp} is not None:\n{_block(inner)}"]
        else:
            block = [f"{tmp} = {recv}", *inner]
        self._hoist.append("\n".join(block))
        return "None"

    def _empty_guard(self, recv, sel, lam):
        # `s.ifEmpty/ifBlank { continue/break/return/throw }` -> a guard: control flow can't be a
        # lambda value. Eval recv once into a temp; if it's empty, run the (control-flow) body; the
        # expression value is the temp (the non-empty receiver). Returns None for an ordinary
        # default-value lambda -- those keep the normal call form.
        body = [c for c in self.named(lam) if c.type != "lambda_parameters"]
        last = body[-1] if body else None
        is_cf = last is not None and (
            last.type in ("return_expression", "jump_expression", "throw_expression")
            or (last.type == "identifier" and self.text(last) in ("continue", "break")))
        if not is_cf:
            return None
        self._lam += 1
        tmp = f"_ife{self._lam}"
        test = f"not {tmp}.strip()" if sel == "ifBlank" else f"not {tmp}"   # ifEmpty: falsy = empty
        self._hoist.append(
            f"{tmp} = {recv}\nif {test}:\n{_block(self.render_statements(body))}")
        return tmp

    def _lambda_param(self, lam):
        pnode = next((c for c in lam.named_children
                      if c.type == "lambda_parameters"), None)
        if pnode is not None:
            pid = next((c for vd in pnode.named_children
                        for c in vd.children if c.type == "identifier"), None)
            if pid is not None:
                return self._safe(self.text(pid))
        return "it"

    @kind("collection_literal")
    def v_collection(self, node):
        return "[" + ", ".join(self.visit(c) for c in self.named(node)) + "]"

    @kind("range_expression")
    def v_range(self, node):
        kids = self.named(node)         # KtList so `(a..b).map { … }` works; iterates fine
        return f"KtList(range({self.visit(kids[0])}, {self.visit(kids[-1])} + 1))"

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
        params, unpacks, scope = [], [], set()
        if pnode is not None:
            for vd in pnode.named_children:
                if vd.type == "multi_variable_declaration":   # destructuring `(a, b)`:
                    dn = f"_d{len(unpacks)}"                   # bind a, b = _d (Python has no
                    names = [self._safe(t) for t in self._destructure_names(vd)]
                    params.append(dn)                         # destructuring lambda params)
                    unpacks.append(f"{', '.join(names)} = {dn}")
                    scope.update(names); scope.add(dn)
                else:
                    pid = next((c for c in vd.children if c.type == "identifier"), None)
                    if pid is not None:
                        nm = self._safe(self.text(pid))
                        params.append(nm); scope.add(nm)
        if not params:
            scope.add("it")
        ps = ", ".join(params) if params else "it=None"
        body = [c for c in self.named(node) if c.type != "lambda_parameters"]
        if not body:
            return f"(lambda {ps}: None)"
        # the lambda's params shadow enclosing members in its body (a param `query` is the param,
        # NOT self.query). Push them as a local scope while rendering the body.
        self._scopes.append(scope)
        try:
            if not unpacks and len(body) == 1 and not self._renders_stmt(body[0]):
                return f"(lambda {ps}: {self.visit(body[0])})"   # pure expr body, no unpacking
            # multi-statement / destructuring / statement-bodied -> hoist a named def; the
            # suite renderer flushes it before the using statement.
            self._lam += 1
            name = f"_lam{self._lam}"
            # Kotlin closures mutate captured outer variables; Python needs `nonlocal`. Any name
            # assigned in the body that lives in an ENCLOSING scope (outside this lambda) is
            # nonlocal (compute against the outer scopes, excluding this one).
            enclosing = set().union(*self._scopes[:-1]) if len(self._scopes) > 1 else set()
            lam_local = set(params) | self._local_names(node)
            captured = sorted((self._assigned_names(body) & enclosing) - lam_local)
            nonlocals = [f"nonlocal {n}" for n in captured]
            *head, last = body
            lines = list(unpacks) + self.render_statements(head)
            before = len(self._hoist)
            last_line = self._distribute(last, "return ")   # block-if/when/stmt-aware
            lines += self._hoist[before:]
            del self._hoist[before:]
            lines.append(last_line)
            self._hoist.append(f"def {name}({ps}):\n{_block(nonlocals + lines)}")
            return name
        finally:
            self._scopes.pop()

    def _assigned_names(self, nodes):
        # bare-identifier targets of assignments / ++ / -- in these nodes, not crossing
        # nested lambda/fn boundaries -- candidates for `nonlocal` when captured.
        out, stop = set(), ("lambda_literal", "function_declaration", "anonymous_function")

        def walk(n):
            if n.type == "assignment":
                lhs = self.named(n)[0]
                if lhs.type == "identifier":
                    out.add(self.text(lhs))
            elif n.type == "unary_expression":
                ops = [c.type for c in n.children if not c.is_named]
                if "++" in ops or "--" in ops:
                    operand = self.named(n)[0]
                    if operand.type == "identifier":
                        out.add(self.text(operand))
            for c in n.children:
                if c.type not in stop:
                    walk(c)

        for nd in nodes:
            walk(nd)
        return out

    def _destructure_names(self, mvd):
        out = []
        for c in mvd.named_children:
            if c.type == "variable_declaration":
                pid = next((k for k in c.children if k.type == "identifier"), None)
                if pid is not None:
                    out.append(self.text(pid))
        return out

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

    @kind("is_expression")
    def v_is(self, node):
        # `x is Type` / `x !is Type` -> isinstance(x, Type) / not isinstance(x, Type)
        left = self.visit(self.named(node)[0])
        tn = next((k for k in node.named_children if k.type == "user_type"), None)
        chk = f"isinstance({left}, {self._py_type_name(tn)})"
        return f"(not {chk})" if any(c.type == "!is" for c in node.children) else chk

    def _py_type_name(self, tn):
        """Python type name for a Kotlin user_type node (generics + qualifier stripped, primitives
        mapped) -- for isinstance() checks. e.g. `List<Foo>` -> `list`(no), `WeeklyRow.Rest` -> `Rest`."""
        typ = self.text(tn).split("<")[0].strip().rsplit(".", 1)[-1] if tn is not None else "object"
        return {"String": "str", "Int": "int", "Long": "int", "Double": "float", "Float": "float",
                "Boolean": "bool", "Char": "str"}.get(typ, self._safe(typ))

    def _has_named_arg(self, args_node):
        """True if any explicit argument is passed BY NAME (`name = value`)."""
        if not args_node:
            return False
        return any(a.type == "value_argument" and any(c.type == "=" for c in a.children)
                   and len(a.named_children) > 1 for a in args_node.named_children)

    def _join_trailing(self, args_str, lam, args_node):
        # A trailing lambda after a named argument is positional-after-keyword (invalid Python), so
        # give it a name. `content` is the correct slot name for most Compose calls; the wrong few
        # fail LOUDLY (unexpected-keyword) rather than silently, and get the real name when callee
        # signatures land. Only kicks in when a named argument actually precedes the lambda.
        if self._has_named_arg(args_node):
            return f"{args_str}, content={lam}" if args_str else f"content={lam}"
        return f"{args_str}, {lam}" if args_str else lam

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
            esc = body.replace("\\", "\\\\")
            if "\n" in esc:                              # Kotlin raw `"""…"""` spanning lines
                return '"""' + self._triple_safe(esc) + '"""'
            return '"' + esc.replace('"', '\\"') + '"'
        if "\n" in body:                                 # interpolated raw string spanning lines
            return 'f"""' + self._triple_safe(body) + '"""'
        if '"' not in body:
            return 'f"' + body + '"'
        if "'" not in body:
            return "f'" + body + "'"
        return 'f"""' + body + '"""'

    @staticmethod
    def _triple_safe(s):
        # make a body safe inside a Python `"""…"""`: neutralize an embedded `"""` and a trailing `"`.
        s = s.replace('"""', '\\"\\"\\"')
        return s[:-1] + '\\"' if s.endswith('"') else s
