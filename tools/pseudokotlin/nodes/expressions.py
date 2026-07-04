"""
expressions.py — expression handlers. Each returns a Python expression STRING it
guarantees parses (MAP), routes a no-Python-equivalent to a shim (WRAP, e.g.
16.dp -> dp(16)), or raises Untranspilable (FAIL). Node-kind names are this
grammar's actual named kinds (verified against parse.named_kinds()).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind, Untranspilable  # noqa: E402
from util import block as _block  # noqa: E402

# The wrap dial: emit Kotlin Int/Long/Float literals as fixed-width wrappers (fidelity-first). Flip to
# False to bare-emit for speed (the wrappers exist either way -- this only changes what `generate` emits).
_WRAP_NUMERICS = True

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
    "toIntOrNull":    lambda r, a: f"toIntOrNull({r})",     # runtime helpers (kotlin parse rules;
    "toLongOrNull":   lambda r, a: f"toLongOrNull({r})",    # None on bad grammar/overflow) -- a real
    "toDoubleOrNull": lambda r, a: f"toDoubleOrNull({r})",  # str has no such method to dispatch to
    "toFloatOrNull":  lambda r, a: f"toFloatOrNull({r})",
    # kotlin substring/remove family -> runtime helpers (a real str has no such methods)
    "substringAfter":      lambda r, a: f"substringAfter({r}, {', '.join(a)})",
    "substringBefore":     lambda r, a: f"substringBefore({r}, {', '.join(a)})",
    "substringAfterLast":  lambda r, a: f"substringAfterLast({r}, {', '.join(a)})",
    "substringBeforeLast": lambda r, a: f"substringBeforeLast({r}, {', '.join(a)})",
    "removeSurrounding":   lambda r, a: f"removeSurrounding({r}, {', '.join(a)})",
    "removePrefix":        lambda r, a: f"removePrefix({r}, {', '.join(a)})",
    "removeSuffix":        lambda r, a: f"removeSuffix({r}, {', '.join(a)})",
    "orEmpty":             lambda r, a: f"orEmpty({r})",     # a nullable-receiver extension: works ON null
    "toString":      lambda r, a: f"str({r})",
    # Kotlin String.format is PRINTF-style ("%.1f".format(x)); Python str.format is brace-style, so the
    # same name silently returns the template. Route through a receiver-aware runtime helper (other
    # receivers -- DateTimeFormatter/LocalDate -- keep their own .format).
    "format":        lambda r, a: f"ktformat({r}, {', '.join(a)})" if a else f"{r}.format()",
    "asSequence":    lambda r, a: f"{r}",                 # lazy seq -> identity (iterable)
    # ---- Kotlin String methods (names differ from Python's str) ---- #
    "lowercase":     lambda r, a: f"{r}.lower()",
    "uppercase":     lambda r, a: f"{r}.upper()",
    "trim":          lambda r, a: f"{r}.strip()",
    "trimStart":     lambda r, a: f"{r}.lstrip()",
    "trimEnd":       lambda r, a: f"{r}.rstrip()",
    "trimIndent":    lambda r, a: f"trimIndent({r})",
    "trimMargin":    lambda r, a: f"trimMargin({r}, {a[0]})" if a else f"trimMargin({r})",
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
    "takeIf":     lambda r, f, s: (f"({r} if {r} is not None and {f}({r}) else None)" if s
                                   else f"({r} if {f}({r}) else None)"),      # ?. -> block never sees null
    "takeUnless": lambda r, f, s: (f"({r} if {r} is not None and not {f}({r}) else None)" if s
                                   else f"({r} if not {f}({r}) else None)"),
    "also":       lambda r, f, s: (f"(({f}({r}), {r})[1] if {r} is not None else None)" if s
                                   else f"({f}({r}), {r})[1]"),               # run for effect, return recv
}

# Kotlin builder functions: `buildString { append… }` / `buildList { add… }`. The lambda's implicit
# receiver is a fresh builder the function makes; bare `append`/`add` bind to it (receiver scope), and the
# call yields the BUILT value. name -> (constructor expr, value the whole thing yields given the temp).
_BUILDERS = {
    "buildString": ("StringBuilder()", lambda r: f"{r}.toString()"),
    "buildList":   ("KtList()",        lambda r: r),
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
        return self._resolve_ident(t)

    def _resolve_ident(self, t):
        """A bare identifier -> its Python form: delegate `x.value`, companion `ClassName.x`, instance
        `self.x`, or plain. Shared by v_identifier and bare `$name` string interpolation."""
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
        # bare `this` inside apply/run/with is the scope receiver; `this@Class` (labeled) is the enclosing
        # object; a plain `this` elsewhere is self.
        if "@" not in self.text(node) and self._implicit_recv:
            return self._implicit_recv[-1]
        return "self"

    def _implicit_member(self, name):
        """The active apply/run/with receiver temp if a bare `name` (in call or assignment position) should
        bind to it -- i.e. it resolves nowhere else. Receiver methods/props are lowerCamel, so an uppercase
        name (a constructor / object / CONSTANT) is never treated as a receiver member."""
        if not self._implicit_recv or not name[:1].islower():
            return None
        if any(name in s for s in self._scopes):                    # a local / lambda param
            return None
        if name in self._members or name in self._static_members:   # the ENCLOSING object's member
            return None
        if name in self._top_level or name in self._GLOBALS:        # a top-level / runtime global
            return None
        return self._implicit_recv[-1]

    def _builder_scope(self, ctor, lam, finish):
        """buildString { append(x) } / buildList { add(x) }: the builder is the receiver. Make a fresh one,
        run the body with it pushed as the implicit receiver (so bare `append`/`add` bind to it), then yield
        the built value (`sb.toString()` for a string; the list itself). Hoisted, so it works in expression
        position. Same receiver-binding as apply/with/run -- here the receiver is CREATED, not an existing
        object."""
        self._lam += 1
        r = f"_recv{self._lam}"
        body = [c for c in self.named(lam) if c.type != "lambda_parameters"]
        self._implicit_recv.append(r)
        try:
            lines = self.render_statements(body)
        finally:
            self._implicit_recv.pop()
        self._hoist.append("\n".join([f"{r} = {ctor}"] + lines))
        return finish(r)

    def _receiver_scope(self, recv_str, lam, returns_recv):
        """x.apply { } / x.run { } / with(x) { }: bind x to a temp, run the body with that temp pushed as the
        implicit receiver (so the body's bare member calls/assignments bind to it), then yield x (apply) or
        the body's last value (run/with). Hoisted, so it works in expression position; an inline body means a
        `return` inside stays a real non-local return."""
        self._lam += 1
        r = f"_recv{self._lam}"
        body = [c for c in self.named(lam) if c.type != "lambda_parameters"]
        self._implicit_recv.append(r)
        try:
            if returns_recv or not body:
                lines = self.render_statements(body)
                value = r
            else:
                *head, last = body
                lines = self.render_statements(head)
                before = len(self._hoist)
                last_line = self._distribute(last, f"{r}_v = ")
                lines += self._hoist[before:]
                del self._hoist[before:]
                lines.append(last_line)
                value = f"{r}_v"
        finally:
            self._implicit_recv.pop()
        self._hoist.append("\n".join([f"{r} = {recv_str}"] + lines))
        return value

    @kind("super_expression")
    def v_super(self, node):
        return "super()"

    @kind("number_literal", "float_literal")
    def v_number(self, node):
        # the bare numeric value: strip Kotlin's type suffixes. For a hex literal F/f are DIGITS (not the
        # float suffix), so 0xFF38256E keeps them -- only L/u/U can trail hex.
        raw = self.text(node).replace("_", "")
        low = raw.lower()
        is_hex = low.startswith("0x")
        val = (raw.rstrip("LluU") if is_hex else raw.rstrip("LlFfuU")) or "0"
        # WRAP by Kotlin type (fidelity-first): Int->Int32 (overflow), Long->Int64, Float->Float32 (32-bit
        # rounding). Double stays bare float (faithful); unsigned has no wrapper yet so it stays bare too.
        # The wrappers' dunders propagate the type through expressions, so wrapping the literal leaves is
        # enough for most arithmetic. Flip _WRAP_NUMERICS to bare-emit for speed.
        if not _WRAP_NUMERICS or "u" in (low[2:] if is_hex else low):
            return val
        if low.endswith("f") and not is_hex:
            self._num_types.add("Float32"); return f"Float32({val})"
        if node.type == "float_literal":
            return val
        if low.endswith("l"):
            self._num_types.add("Int64"); return f"Int64({val})"
        self._num_types.add("Int32"); return f"Int32({val})"

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
        call = f"is_instance({self.visit(kids[0])}, {self.visit(kids[-1])})"   # kotlin `is T` -- T may be
        return f"(not {call})" if neg else call                                # an object SINGLETON

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

    def _fqn_simple(self, node):
        """If `node` is a fully-qualified PACKAGE reference used inline (`com.sara.…ScienceInfoDialog`,
        `androidx.compose.material3.TopAppBar`), the simple name it collapses to -- which lives in the flat
        namespace (app) or is served by autostub (external). None for an ordinary object-member access."""
        full = self.text(node)
        if (re.fullmatch(r"[\w.]+", full)
                and re.match(r"^(com|androidx|kotlinx|kotlin|java|javax|org|dagger|google)\.", full)):
            return self._strip_pkg(full)
        return None

    @kind("navigation_expression")
    def v_navigation(self, node):
        kids = self.named(node)
        recv = kids[0]
        sel = self.text(kids[-1]) if len(kids) > 1 else ""
        if sel == "class" and any(c.type == "::" for c in node.children):
            return f"kclass({self.visit(recv)})"        # Foo::class -> kclass(Foo) (.java/.kotlin -> Foo)
        fqn = self._fqn_simple(node)                     # com.sara.…Foo / androidx.…Bar -> the simple name
        if fqn is not None:
            return fqn
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
        # buildString { append… } / buildList { add… }: the builder is the receiver -- make one, bind the
        # body's bare members to it, yield the built value. (Bare callee, trailing lambda, no value args.)
        if (callee.type in ("identifier", "simple_identifier") and trailing is not None
                and own_args is None and self.text(callee) in _BUILDERS):
            ctor, finish = _BUILDERS[self.text(callee)]
            return self._builder_scope(ctor, self._lambda_node(trailing), finish)
        # `f(args) { lambda }` parses as (f(args))(lambda) -- the trailing lambda is an
        # EXTRA argument to the inner call, not a second call. Merge it in.
        if trailing is not None and callee.type == "call_expression" and own_args is None:
            inner = self.named(callee)[0]
            in_args_node = next((c for c in callee.children
                                 if c.type == "value_arguments"), None)
            # with(x) { … } parses as (with(x))(lambda) -> a receiver scope on x: the body's bare member
            # calls/assignments bind to x.
            if (inner.type in ("identifier", "simple_identifier") and self.text(inner) == "with"
                    and in_args_node is not None and not any("with" in s for s in self._scopes)):
                va = next((c for c in in_args_node.named_children if c.type == "value_argument"), None)
                if va is not None and va.named_children:
                    return self._receiver_scope(self.visit(va.named_children[-1]),
                                                self._lambda_node(trailing), returns_recv=False)
            in_args = self._render_args(in_args_node)
            in_fn = self.visit(inner)
            lam = self._lambda_str(trailing)
            return f"{in_fn}({self._join_trailing(in_args, lam, in_args_node, callee=in_fn)})"
        if callee.type == "navigation_expression":
            fqn = self._fqn_simple(callee)               # com.sara.…ScienceInfoDialog(args) -> the simple call
            if fqn is not None:
                args = self._render_args(own_args)
                if trailing is not None:
                    args = self._join_trailing(args, self._lambda_str(trailing), own_args, callee=fqn)
                return f"{fqn}({args})"
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
            if sel in ("apply", "run") and trailing is not None and not safe:   # receiver scope (this=recv)
                return _wrap(self._receiver_scope(recv, self._lambda_node(trailing),
                                                  returns_recv=(sel == "apply")))
            if sel in ("ifEmpty", "ifBlank") and trailing is not None:
                g = self._empty_guard(recv, sel, self._lambda_node(trailing))
                if g is not None:                            # `s.ifEmpty { continue }` -> guard
                    return _wrap(g)
                return _wrap(f"{sel}({recv}, {self._lambda_str(trailing)})")   # runtime helper (real str
                                                                               # has no such method)
            if sel in _SCOPE_FNS and trailing is not None:   # x.let { it… } -> f(x)
                lam = self._lambda_node(trailing)
                if self._has_nonlocal_return(lam):      # `x?.let { return it }` guard:
                    if sel == "let":                    # the return exits the ENCLOSING fn
                        return self._let_guard(nk[0], lam, safe)
                    raise Untranspilable(node, f"non-local return in {sel} {{ … }}")
                return _wrap(_SCOPE_FNS[sel](recv, self._lambda_str(trailing), safe))
            if sel in _STDLIB_METHODS:                  # WRAP: recv.coerceIn(...) -> min/max; a safe call
                inner = _STDLIB_METHODS[sel](recv, self._arg_values(node))   # keeps its not-None guard
                return _wrap(f"({inner} if {recv} is not None else None)" if safe else inner)
            # general method call -- build recv.sel(args) from the receiver+selector so the
            # navigation PROPERTY mappings (.first -> [0], .size -> len) don't fire on a
            # method CALL (`it.first()` is a method; `it.first` is the property).
            args = self._render_args(own_args)
            if sel == "filterIsInstance" and not args:   # reified type arg IS the argument:
                ta = next((c for c in node.children if c.type == "type_arguments"), None)
                ut = next((c for c in ta.named_children[0].named_children
                           if c.type == "user_type"), None) if ta and ta.named_children else None
                if ut is not None:                        # xs.filterIsInstance<T>() -> xs.filterIsInstance(T)
                    args = self._py_type_name(ut)
            if trailing is not None:
                lam = self._lambda_str(trailing)
                args = self._join_trailing(args, lam, own_args)
            call = f"{recv}.{self._safe(sel)}({args})"
            return _wrap(f"({call} if {recv} is not None else None)" if safe else call)
        fn = self.visit(callee)
        if callee.type in ("identifier", "simple_identifier"):   # bare call inside apply/run/with that is
            r = self._implicit_member(self.text(callee))         # a receiver method -> recv.method(...)
            if r is not None:
                fn = f"{r}.{self._safe(self.text(callee))}"
        args = self._render_args(own_args)
        if trailing is not None:                       # `xs.map { v -> v*2 }`
            lam = self._lambda_str(trailing)
            args = self._join_trailing(args, lam, own_args,
                                       callee=self.text(callee) if callee.type in
                                       ("identifier", "simple_identifier") else None)
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
        # a parameterless lambda's implicit `it`: if an ENCLOSING lambda bound `it`, kotlin's content
        # lambdas (receiver lambdas, no parameter) see THAT it -- so default to it (captured at def time),
        # not None. `definition?.let { ... Row { LabeledStat(it.min...) } ... }` reads the let's it inside.
        outer_it = any("it" in s for s in self._scopes)
        ps = ", ".join(params) if params else ("it=it" if outer_it else "it=None")
        body = [c for c in self.named(node) if c.type != "lambda_parameters"]
        if not body:
            return f"(lambda {ps}: None)"
        # the lambda's params shadow enclosing members in its body (a param `query` is the param,
        # NOT self.query). Push them as a local scope while rendering the body.
        self._scopes.append(scope)
        try:
            if not unpacks and len(body) == 1 and not self._renders_stmt(body[0]):
                before = len(self._hoist)
                expr = self.visit(body[0])                       # may itself hoist a nested def
                if len(self._hoist) == before:                   # nothing escaped -> a true one-liner
                    return f"(lambda {ps}{self._captured_loops(expr, scope)}: {expr})"
                del self._hoist[before:]                          # a nested def referenced THIS lambda's
                # params (e.g. `let { x -> ys.forEach { x… } }`) -> it would lose them if lifted out; fall
                # to the def form below so the nested def is emitted INSIDE this lambda, seeing its params.
            # multi-statement / destructuring / statement-bodied / hoist-producing -> a named def; the
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
            caps = self._captured_loops("\n".join(lines), scope)
            self._hoist.append(f"def {name}({ps}{caps}):\n{_block(nonlocals + lines)}")
            return name
        finally:
            self._scopes.pop()

    def _captured_loops(self, body_text, local):
        """Per-iteration capture: for each enclosing for-loop variable referenced in this lambda's body
        (and not shadowed by its own params), bind it as a default arg -- so a lambda made in a loop sees
        that iteration's value (Kotlin), not the final one (Python's late-bound default)."""
        out, seen = [], set()
        for v in (n for level in self._loop_vars for n in level):
            if v not in local and v not in seen and re.search(rf"\b{re.escape(v)}\b", body_text):
                seen.add(v)
                out.append(f", {v}={v}")
        return "".join(out)

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
        chk = f"is_instance({left}, {self._py_type_name(tn)})"
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

    def _join_trailing(self, args_str, lam, args_node, callee=None):
        # A trailing lambda after a named argument is positional-after-keyword (invalid Python), so give
        # it a name. Kotlin binds a trailing lambda to the callee's LAST parameter: for a same-file fn we
        # know that name (self._last_param); otherwise `content` (correct for the Compose surface). The
        # wrong few fail LOUDLY (unexpected-keyword), never silently. Only kicks in when a named argument
        # actually precedes the lambda.
        if self._has_named_arg(args_node):
            slot = self._last_param.get(callee, "content")
            return f"{args_str}, {slot}={lam}" if args_str else f"{slot}={lam}"
        return f"{args_str}, {lam}" if args_str else lam

    def _string_to_fstring(self, node):
        kids = [c for c in node.children if c.type not in ('"', '"""', "'")]
        segs, interp, i = [], False, 0
        while i < len(kids):
            c = kids[i]
            if c.type == "interpolation":                        # `${expr}`
                interp = True
                inner = next((k for k in c.named_children), None)
                segs.append("{" + (self.visit(inner) if inner else "") + "}")
            elif (c.type == "string_content" and self.text(c) == "$"
                  and i + 1 < len(kids) and kids[i + 1].type == "string_content"
                  and re.match(r"[A-Za-z_]", self.text(kids[i + 1]))):
                # Kotlin bare `$name` interpolation: this grammar splits it into a `$` token then the
                # content whose LEADING identifier is the variable; the rest of that content is literal
                # (`"$foo.bar"` is `${foo}` + ".bar"). Resolve the name the same way an identifier would.
                nxt = self.text(kids[i + 1])
                name = re.match(r"[A-Za-z_]\w*", nxt).group(0)
                interp = True
                resolved = "self" if name == "this" else self._resolve_ident(name)
                segs.append("{" + resolved + "}")
                rest = nxt[len(name):]
                if rest:
                    segs.append(rest.replace("{", "{{").replace("}", "}}"))
                i += 2
                continue
            else:
                segs.append(self.text(c).replace("{", "{{").replace("}", "}}"))
            i += 1
        body = "".join(segs)
        raw = any(c.type == '"""' for c in node.children)        # kotlin RAW string: backslash is literal
        if not interp:
            body = body.replace("{{", "{").replace("}}", "}")   # a PLAIN string keeps literal braces --
            esc = (body.replace("\\", "\\\\") if raw            # doubling is only f-string escaping.
                   else body.replace("\\$", "$"))               # regular: kotlin escapes (\n \t \") ARE
                                                                 # python escapes; \$ is a literal $
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
