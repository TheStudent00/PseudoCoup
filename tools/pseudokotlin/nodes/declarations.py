"""
declarations.py — module / function / class / property handlers. Statement-shaped
nodes return a (possibly multi-line) Python STRING; block bodies indent + join their
children. Member/scope state (`self._members`, `self._scopes`) drives `this.x`/member
resolution in the identifier handler.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind, Untranspilable  # noqa: E402
from util import block as _block  # noqa: E402

_TOP_DECLS = {"class_declaration", "object_declaration", "function_declaration",
              "property_declaration"}
# class-body members still needing design work -- fail loudly, never drop
_OOP_DEFER = {"secondary_constructor", "object_literal"}
# JUnit lifecycle annotations preserved as decorators (kotlin_rt tags them) so the
# oracle runs real @Test methods, not private helpers. Others are still dropped.
_JUNIT_ANN = {"Test", "Before", "After", "BeforeEach", "AfterEach", "Ignore", "Disabled"}


class Declarations:
    @kind("source_file")
    def v_source_file(self, node):
        parts = [self.visit(c) for c in self.named(node) if c.type in _TOP_DECLS]
        return "\n\n\n".join(p for p in parts if p)

    @kind("function_declaration")
    def v_function_declaration(self, node):
        in_class = node.parent is not None and \
            node.parent.type in ("class_body", "enum_class_body")
        # extension fn `fun Recv.name(…)` -> the receiver becomes self (its `.` token
        # sits between the receiver type and the name); body `this` already -> self.
        is_extension = any(c.type == "." for c in node.children)
        return self._function(node, with_self=in_class or is_extension)

    def _function(self, node, with_self, decorator=""):
        name = self._safe(self._name_of(node) or "unknown_func")
        pnode = next((c for c in node.children if c.type == "function_value_parameters"), None)
        names, parts, guards = self._collect_params(pnode) if pnode is not None \
            else ([], [], [])
        params = (["self"] if with_self else []) + parts
        body_node = next((c for c in node.children
                          if c.type in ("function_body", "block")), None)
        self._scopes.append(set(names))
        body = self._render_function_body(body_node, prefix=guards)
        self._scopes.pop()
        decos = ([decorator] if decorator else []) + \
            [f"@{a}" for a in self._annotations(node) if a in _JUNIT_ANN]
        head = "".join(d + "\n" for d in decos)
        return f"{head}def {name}({', '.join(params)}):\n{body}"

    def _annotations(self, node):
        mods = next((c for c in node.children if c.type == "modifiers"), None)
        if mods is None:
            return []
        out = []
        for a in mods.named_children:
            if a.type == "annotation":
                ut = next((k for k in a.named_children
                           if k.type in ("user_type", "constructor_invocation")), None)
                if ut is not None:
                    out.append(self.text(ut).split("(")[0].strip())
        return out

    def _collect_params(self, pnode):
        # A Kotlin default value is a SIBLING of its `parameter` (after a `=` token),
        # not a child. Walk all children, pairing each default to the prior parameter.
        # Defaults render in the enclosing scope (not the param scope). A default that
        # references `self.` is NOT def-time-safe in Python (the `def` runs during
        # class-body exec) -> emit a None sentinel + a body guard instead. Returns
        # (bare names for scope, signature parts, body-prefix guard lines).
        names, sig, pending = [], [], False
        for c in pnode.children:
            if c.type == "parameter":
                pid = self._name_of(c)
                if pid:
                    names.append(pid)
                    sig.append([self._safe(pid), None])
                pending = False
            elif c.type == "=":
                pending = True
            elif pending and c.is_named:
                if sig:
                    sig[-1][1] = self.visit(c)
                pending = False
        parts, guards = [], []
        for p, d in sig:
            if d is None:
                parts.append(p)
            elif "self." in d:                       # per-call default via sentinel
                parts.append(f"{p}=None")
                guards.append(f"if {p} is None: {p} = {d}")
            else:
                parts.append(f"{p}={d}")
        return names, parts, guards

    @kind("class_declaration")
    def v_class_declaration(self, node):
        return self._render_class(node, self._name_of(node) or "UnknownClass")

    @kind("object_declaration")
    def v_object_declaration(self, node):
        # Kotlin `object Foo {…}` is a singleton. Emit the class, then rebind the
        # name to a sole instance -> `Foo.x`/`Foo.f()` resolve, single-instance
        # semantics preserved, no extra instances constructible.
        name = self._name_of(node) or "UnknownObject"
        return f"{self._render_class(node, name)}\n{name} = {name}()"

    def _render_class(self, node, name):
        body_node = next((c for c in node.children
                          if c.type in ("class_body", "enum_class_body")), None)
        ctor_params = []
        pc = next((c for c in node.children if c.type == "primary_constructor"), None)
        if pc is not None:
            cps = next((c for c in pc.named_children if c.type == "class_parameters"), None)
            container = cps if cps is not None else pc
            for pn in container.named_children:
                if pn.type == "class_parameter":
                    nm = self._name_of(pn)
                    if nm:
                        ctor_params.append(nm)

        prev = self._members
        self._members = set(ctor_params)
        props, getters, lazies, methods, nested, comps, inits = [], [], [], [], [], [], []
        entries = []
        if body_node:
            for c in body_node.named_children:
                if c.type == "enum_entry":
                    entries.append(c)
                elif c.type == "property_declaration":
                    nm = self._name_of(c, deep=True)
                    if nm:
                        self._members.add(nm)
                    if any(k.type == "getter" for k in c.children):   # computed property
                        getters.append(c)
                    elif any(k.type == "property_delegate" for k in c.children):
                        lazies.append(c)                              # `by lazy { … }`
                    else:
                        props.append(c)
                elif c.type == "function_declaration":
                    nm = self._name_of(c)
                    if nm:
                        self._members.add(nm)
                    methods.append(c)
                elif c.type in ("class_declaration", "object_declaration"):
                    nested.append(c)
                elif c.type == "companion_object":
                    comps.append(c)
                elif c.type == "anonymous_initializer":
                    inits.append(c)
                elif c.type in _OOP_DEFER:
                    raise Untranspilable(c, "class member needs the OOP-model pass")
                # else: enum_entry / modifiers / trivia -> consumed, not emitted

        self._scopes.append(set(ctor_params))
        init_body = [f"self.{self._safe(p)} = {self._safe(p)}" for p in ctor_params]
        init_body += [self._render_property(p, as_self=True) for p in props]
        for ini in inits:                                  # init { … } -> __init__ body
            blk = next((k for k in ini.named_children if k.type == "block"), None)
            if blk is not None:
                init_body += self.render_statements(self.named(blk))
        self._scopes.pop()

        lines = []
        if ctor_params or props or inits:
            args = ", ".join(["self"] + [self._safe(p) for p in ctor_params])
            lines.append(f"def __init__({args}):\n{_block(init_body)}")
        lines += [self.visit(m) for m in methods]
        lines += [self._render_getter(g) for g in getters]  # computed props -> @property
        lines += [self._render_lazy(z) for z in lazies]     # by lazy -> cached @property
        lines += [self.visit(n) for n in nested]
        for comp in comps:                                 # companion -> static members
            lines += self._render_companion(comp, name)
        self._members = prev

        body = _block(lines) if lines else _block([])
        cls = f"class {name}:\n{body}"
        if entries:                          # enum entries -> class-level singletons
            cls += "\n" + self._render_enum_entries(node, name, entries)
        return cls

    def _render_enum_entries(self, node, name, entries):
        # each Kotlin enum entry is one instance of the class, bound as a class attr
        # (identity == matches Kotlin enum identity); .name/.ordinal set for the
        # common `entry.name`/`entry.ordinal`/`values()` accesses.
        out, names = [], []
        for e in entries:
            ename = self._name_of(e)
            if any(k.type == "class_body" for k in e.children):
                raise Untranspilable(e, "enum entry with a body (per-entry override)")
            args = self._render_args(next((k for k in e.named_children
                                           if k.type == "value_arguments"), None))
            out.append(f"{name}.{ename} = {name}({args})")
            names.append(ename)
        for i, en in enumerate(names):
            out.append(f'{name}.{en}.name = "{en}"')
            out.append(f"{name}.{en}.ordinal = {i}")
        listed = ", ".join(f"{name}.{en}" for en in names)
        out.append(f"{name}._entries = [{listed}]")   # backs values()/entries()
        return "\n".join(out)

    def _render_getter(self, prop):
        name = self._safe(self._name_of(prop, deep=True) or "_prop")
        getter = next((c for c in prop.children if c.type == "getter"), None)
        body_node = next((c for c in getter.named_children
                          if c.type in ("function_body", "block")), None) if getter else None
        self._scopes.append(set())
        body = self._render_function_body(body_node)
        self._scopes.pop()
        return f"@property\ndef {name}(self):\n{body}"

    def _render_ext_getter(self, prop, getter):
        # top-level computed property `val [Recv.]name get() = …` -> a function; an
        # extension property (receiver before the name, marked by a `.`) takes self.
        name = self._safe(self._name_of(prop, deep=True) or "_prop")
        params = ["self"] if any(c.type == "." for c in prop.children) else []
        body_node = next((c for c in getter.named_children
                          if c.type in ("function_body", "block")), None)
        self._scopes.append(set())
        body = self._render_function_body(body_node)
        self._scopes.pop()
        return f"def {name}({', '.join(params)}):\n{body}"

    def _render_lazy(self, prop):
        # `val x by lazy { … }` -> a @property that computes once and caches in
        # self._x. Single-threaded compute-on-first-access matches Kotlin lazy; only
        # `by lazy` is accepted -- any other delegate (Delegates.observable, …) fails
        # loudly rather than being silently mis-mapped.
        name = self._safe(self._name_of(prop, deep=True) or "_prop")
        deleg = next((c for c in prop.children if c.type == "property_delegate"), None)
        call = next((c for c in deleg.named_children
                     if c.type == "call_expression"), None) if deleg else None
        fn = next((c for c in call.named_children
                   if c.type == "identifier"), None) if call else None
        if call is None or fn is None or self.text(fn) != "lazy":
            raise Untranspilable(deleg or prop,
                                 "only `by lazy { … }` property delegation is supported")
        lam = next((c for c in call.named_children
                    if c.type in ("annotated_lambda", "lambda_literal")), None)
        if lam is not None and lam.type == "annotated_lambda":
            lam = next((c for c in lam.named_children
                        if c.type == "lambda_literal"), lam)
        cache = f"self._{name}"
        self._scopes.append(set())
        body = [c for c in self.named(lam)
                if c.type != "lambda_parameters"] if lam is not None else []
        if not body:
            compute = [f"{cache} = None"]
        else:
            *head, last = body
            compute = self.render_statements(head)
            before = len(self._hoist)
            line = self._distribute(last, f"{cache} = ") if self.is_value(last) \
                else self.visit(last)
            compute += self._hoist[before:]
            del self._hoist[before:]
            compute.append(line)
        self._scopes.pop()
        guard = [f'if not hasattr(self, "_{name}"):', _block(compute), f"return {cache}"]
        return f"@property\ndef {name}(self):\n{_block(guard)}"

    def _render_companion(self, comp, cls_name):
        cbody = next((c for c in comp.named_children if c.type == "class_body"), comp)
        cprops = [c for c in cbody.named_children if c.type == "property_declaration"]
        cfuncs = [c for c in cbody.named_children if c.type == "function_declaration"]
        names = {self._name_of(p, deep=True) for p in cprops}
        names |= {self._name_of(f) for f in cfuncs}
        names.discard(None)
        prev_sm, prev_sc = self._static_members, self._static_class
        self._static_members, self._static_class = names, cls_name
        out = [self._render_property(p, as_self=False) for p in cprops]   # class-level
        out += [self._function(f, with_self=False, decorator="@staticmethod")
                for f in cfuncs]
        self._static_members, self._static_class = prev_sm, prev_sc
        return out

    @kind("property_declaration")
    def v_property_declaration(self, node):
        return self._render_property(node, as_self=False)

    # ---- helpers --------------------------------------------------------- #
    def _name_of(self, node, deep=False):
        ids = ("simple_identifier", "identifier")
        direct = next((c for c in node.children if c.type in ids), None)
        if direct is not None:
            return self.text(direct)
        if deep:  # e.g. property_declaration -> variable_declaration -> id
            vd = next((c for c in node.children if c.type == "variable_declaration"), None)
            if vd:
                pid = next((c for c in vd.children if c.type in ids), None)
                return self.text(pid) if pid else None
        return None

    def _render_function_body(self, body_node, prefix=()):
        pre = list(prefix)                          # default-arg sentinel guards, etc.
        if body_node is None:
            return _block(pre or [])
        if body_node.type == "function_body":
            if any(c.type == "=" for c in body_node.children):     # `= expr` body
                kids = self.named(body_node)
                if not kids:
                    return _block(pre or [])
                before = len(self._hoist)
                line = self._distribute(kids[0], "return ")   # when/if -> distributed
                hoist = self._hoist[before:]
                del self._hoist[before:]
                return _block(pre + hoist + [line])
            inner = self.named(body_node)                          # function_body -> block
            if inner and inner[0].type == "block":
                body_node = inner[0]
        # body_node is now a block: render its statements (hoist-aware)
        return _block(pre + self.render_statements(self.named(body_node)))

    def _render_property(self, node, as_self):
        getter = next((c for c in node.children if c.type == "getter"), None)
        if getter is not None:  # top-level / extension computed property -> function
            return self._render_ext_getter(node, getter)
        deleg = next((c for c in node.children if c.type == "property_delegate"), None)
        if deleg is not None:   # `by lazy`/`by …` only modelled as a class member
            raise Untranspilable(deleg, "delegated property outside a class body")
        name = self._name_of(node, deep=True) or "_"
        target = f"self.{self._safe(name)}" if (as_self and name in self._members) \
            else self._safe(name)
        # value is the named child after the variable_declaration
        kids = self.named(node)
        val_node = None
        for i, c in enumerate(kids):
            if c.type == "variable_declaration" and i + 1 < len(kids):
                val_node = kids[i + 1]
                break
        if val_node is None:
            return f"{target} = None"
        return self._distribute(val_node, f"{target} = ")
