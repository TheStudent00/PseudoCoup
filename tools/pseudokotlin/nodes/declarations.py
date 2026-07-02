"""
declarations.py — module / function / class / property handlers. Statement-shaped
nodes return a (possibly multi-line) Python STRING; block bodies indent + join their
children. Member/scope state (`self._members`, `self._scopes`) drives `this.x`/member
resolution in the identifier handler.
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind, Untranspilable  # noqa: E402
from util import block as _block  # noqa: E402
import resolve   # noqa: E402  (the resolve phase: a file's import table)
import datalayer  # noqa: E402  (the Room map stage: @Entity schema + @Dao bodies)
from nodes.expressions import _WRAP_NUMERICS  # noqa: E402  (the wrap dial, shared with v_number)

# Kotlin DECLARED scalar numeric type -> its fixed-width wrapper. This is the declared-type counterpart of
# the suffix-driven literal wrapping in v_number: coercing a typed param/var at its boundary makes a chain
# that never touches a literal (e.g. a value straight off a DAO) still carry Kotlin's width semantics.
# Double stays bare float (faithful); Short/Byte/unsigned have no wrapper yet, so they're left bare.
_NUM_WRAPPER = {"Int": "Int32", "Long": "Int64", "Float": "Float32"}

_TOP_DECLS = {"class_declaration", "object_declaration", "function_declaration",
              "property_declaration"}
# class-body members still needing design work -- fail loudly, never drop
_OOP_DEFER = {"secondary_constructor", "object_literal"}
# JUnit lifecycle annotations preserved as decorators (kotlin_rt tags them) so the
# oracle runs real @Test methods, not private helpers. Others are still dropped.
_JUNIT_ANN = {"Test", "Before", "After", "BeforeEach", "AfterEach", "Ignore", "Disabled"}
# Receiver types that map to Python builtins -> cannot be monkey-patched, so an
# extension function on them is NOT registered onto the receiver (a separate bucket).
_BUILTIN_RECVRS = {"List", "MutableList", "Set", "MutableSet", "Map", "MutableMap",
                   "Collection", "Iterable", "Sequence", "Array", "String",
                   "CharSequence", "Int", "Long", "Double", "Float", "Boolean",
                   "Char", "Byte", "Short", "Number", "Comparable", "Any", "Pair"}
# Kotlin type -> Python type for overload isinstance dispatch (a domain class maps to
# itself). Int/Long stay int; Double/Float stay float -- distinguishable at runtime.
_PYTYPE = {"Double": "float", "Float": "float", "Int": "int", "Long": "int",
           "String": "str", "CharSequence": "str", "Char": "str", "Boolean": "bool",
           "List": "list", "MutableList": "list", "Collection": "list", "Array": "list",
           "Set": "set", "MutableSet": "set", "Map": "dict", "MutableMap": "dict"}
# type (simple name) -> its instance member names, accumulated as classes are rendered.
# Lets an extension fn `fun Recv.f() = … bareField …` resolve bareField to self.field.
_TYPE_FIELDS = {}


class Declarations:
    @kind("source_file")
    def v_source_file(self, node):
        self._ext_patches, self._nested_aliases, self._nested_alias_names = [], [], set()
        self._runtime_imports = set()   # `from runtime.room import …` etc. added while visiting decls
        self._num_types = set()         # Int32/Int64/Float32 used by wrapped literals -> one import
        ext_imports = self._emit_imports(resolve.file_header(node))
        # top-level `const val`s are compile-time literals with no forward deps -> emit them FIRST, so a
        # class that uses one as a default arg (evaluated at def time in Python) sees it already bound.
        decls = [c for c in self.named(node) if c.type in _TOP_DECLS]
        is_const = lambda c: c.type == "property_declaration" and self._is_const(c)   # noqa: E731
        parts = [self.visit(c) for c in
                 [d for d in decls if is_const(d)] + [d for d in decls if not is_const(d)]]
        body = "\n\n\n".join(p for p in parts if p)
        # flush AFTER all decls so the referenced classes exist: nested-type aliases
        # (Inner = Outer.Inner, makes bare cross-file refs resolve) then ext patches.
        tail = self._nested_aliases + self._ext_patches
        if tail:
            body += ("\n\n\n" if body else "") + "\n".join(tail)
        num = [f"from runtime.numbers import {', '.join(sorted(self._num_types))}"] if self._num_types else []
        imports = num + sorted(self._runtime_imports) + ext_imports
        if imports:
            body = "\n".join(imports) + ("\n\n\n" + body if body else "")
        # `from __future__ import annotations` MUST lead the file: it makes every type hint a stored string
        # (never evaluated at runtime), so hints can't cause a NameError yet DI can still read the real types.
        return "from __future__ import annotations\n" + ("\n" + body if body else "")

    def _emit_imports(self, header):
        """Every EXTERNAL name a file imports -> `from runtime.autostub import <name>`. autostub is the one
        front door: it returns the real wrapper when a runtime module provides it, and an inert Stub
        otherwise -- so the name ALWAYS binds. A transpiled file therefore always LOADS (no NameError); an
        un-wrapped external (a compose widget) is inert, not a silent gap (it's recorded in the stub
        inventory). App imports stay in the flat namespace; androidx.room is handled by the data-layer map
        stage (it adds its own room imports)."""
        names = set()
        for used, fqn in header["imports"].items():
            if resolve.origin(fqn) in ("app", "androidx_room"):
                continue
            orig = fqn.rsplit(".", 1)[-1]                   # the bare name (real wrapper or stub provides it)
            names.add(orig if used == orig else f"{orig} as {used}")   # preserve `import … as …`
        if not names:
            return []
        return [f"from runtime.autostub import {', '.join(sorted(names))}"]

    @kind("function_declaration")
    def v_function_declaration(self, node):
        in_class = node.parent is not None and \
            node.parent.type in ("class_body", "enum_class_body")
        # extension fn `fun Recv.name(…)` -> the receiver becomes self (its `.` token
        # sits between the receiver type and the name); body `this` already -> self.
        recv = self._ext_receiver(node)
        fn = self._function(node, with_self=in_class or recv is not None)
        if recv is not None and not in_class:   # top-level extension: dispatch on the
            base = self._strip_pkg(recv.split("<")[0].strip())   # receiver -> patch it onto that class so
            if base and base not in _BUILTIN_RECVRS:    # `recv.name(...)` resolves (Kotlin
                nm = self._safe(self._name_of(node) or "unknown_func")  # ext semantics).
                self._ext_patches.append(f"{base}.{nm} = {nm}")   # flushed at module end
        return fn

    def _strip_pkg(self, name):
        """Drop a qualified type's leading package segments (the lowercase ones), so an extension receiver
        written fully-qualified (`com.sara.…MovementPattern`, `kotlin.String`) patches onto the simple name
        that lives in the flat namespace. A nested type (`Outer.Inner`) is kept intact (no lowercase head)."""
        parts = name.split(".")
        while len(parts) > 1 and parts[0][:1].islower():
            parts.pop(0)
        return ".".join(parts)

    def _ext_receiver(self, node):
        # extension fn `fun <user_type>.name(...)`: receiver is the user_type before the
        # `.` (a plain fn has no `.` child; its return type's user_type sits after `:`).
        if not any(c.type == "." for c in node.children):
            return None
        ut = next((c for c in node.children if c.type == "user_type"), None)
        return self.text(ut) if ut is not None else None

    def _function(self, node, with_self, decorator="", name=None):
        name = name or self._safe(self._name_of(node) or "unknown_func")
        pnode = next((c for c in node.children if c.type == "function_value_parameters"), None)
        names, parts, guards, coercions = self._collect_params(pnode) if pnode is not None \
            else ([], [], [], [])
        params = (["self"] if with_self else []) + parts
        body_node = next((c for c in node.children
                          if c.type in ("function_body", "block")), None)
        recv = self._ext_receiver(node)         # extension: receiver fields resolve to self
        prev_m = self._members
        if recv is not None:
            simple = recv.split("<")[0].strip().split(".")[-1]
            self._members = self._members | _TYPE_FIELDS.get(simple, set())
            if simple in self._enum_types:          # extension on an enum: name/ordinal -> self.*
                self._members = self._members | {"name", "ordinal"}
        own = set(names) | self._local_names(body_node)
        # a nested local fn mutating an enclosing fn's var needs `nonlocal` (Kotlin closes
        # over it). Methods/top-level fns have no enclosing fn scope -> no nonlocals.
        nonlocals = self._nonlocals(body_node, own)
        self._scopes.append(own)
        _saved_deleg = self._delegated                  # `by` delegates are function-local; inherit
        self._delegated = set(self._delegated)          # enclosing ones (closures), drop local on exit
        body = self._render_function_body(body_node, prefix=nonlocals + guards + coercions)
        self._delegated = _saved_deleg
        self._scopes.pop()
        self._members = prev_m
        decos = ([decorator] if decorator else []) + \
            [f"@{a}" for a in self._annotations(node) if a in _JUNIT_ANN]
        head = "".join(d + "\n" for d in decos)
        rt = self._return_type(node)                     # keep the return type (lets DI read what a recipe makes)
        return f"{head}def {name}({', '.join(params)}){f' -> {rt}' if rt else ''}:\n{body}"

    def _return_type(self, node):
        """The declared return type (the `user_type` after the parameter list, not the extension receiver),
        cleaned to a Python-safe identifier hint; None for constructors / complex types."""
        kids = list(node.children)
        vp = next((i for i, c in enumerate(kids) if c.type == "function_value_parameters"), None)
        if vp is None:
            return None
        for c in kids[vp + 1:]:
            if c.type in ("function_body", "block"):
                break
            if c.type in ("user_type", "nullable_type"):
                ut = c if c.type == "user_type" else next((k for k in c.children if k.type == "user_type"), None)
                if ut is not None:
                    return self._clean_type(self.text(ut))
        return None

    # ---- method overloading (Kotlin same-name, different signatures) ------- #
    def _render_overloads(self, name, variants):
        # render each variant as `_name__i`, then a wrapper `name` that dispatches by the
        # runtime type at the first param position where the signatures differ.
        safe = self._safe(name)
        impls = [self._function(v, with_self=True, name=f"_{safe}__{i}")
                 for i, v in enumerate(variants)]
        sigs = [self._param_types(v) for v in variants]
        return impls + [self._overload_wrapper(safe, sigs)]

    def _param_types(self, node):
        pnode = next((c for c in node.children
                      if c.type == "function_value_parameters"), None)
        out = []
        if pnode is not None:
            for p in pnode.named_children:
                if p.type == "parameter":
                    ut = next((c for c in p.children if c.type == "user_type"), None)
                    typ = self.text(ut).split("<")[0].strip() if ut is not None else None
                    out.append((self._name_of(p), typ))
        return out

    def _overload_wrapper(self, safe, sigs):
        n = len(sigs)
        # discriminating position: first index where the variants' types differ
        disc = next((d for d in range(max((len(s) for s in sigs), default=0))
                     if len({s[d][1] if d < len(s) else None for s in sigs}) > 1), None)
        order = sorted(range(n), key=lambda i: (   # specific (domain) types before general
            self._type_rank(sigs[i][disc][1]) if disc is not None and disc < len(sigs[i])
            else (len(sigs[i]), 99)))
        body = []
        for rank, i in enumerate(order):
            call = f"return self._{safe}__{i}(*args, **kwargs)"
            if rank == len(order) - 1:                       # last variant = fallback
                body.append(call)
            elif disc is not None and disc < len(sigs[i]):
                pname, typ = sigs[i][disc]
                body.append(f"if {self._type_guard(disc, pname, typ)}:\n    {call}")
            else:                                            # discriminate by arity
                body.append(f"if len(args) + len(kwargs) == {len(sigs[i])}:\n    {call}")
        return f"def {safe}(self, *args, **kwargs):\n{_block(body)}"

    def _type_guard(self, d, pname, typ):
        pt = _PYTYPE.get(typ, typ)
        checks = [f"(len(args) > {d} and isinstance(args[{d}], {pt}))"]
        if pname:
            checks.append(f"isinstance(kwargs.get('{self._safe(pname)}'), {pt})")
        return "(" + " or ".join(checks) + ")"

    @staticmethod
    def _type_rank(typ):
        # domain classes are specific (checked first); primitives are general (fallback)
        return (1, 0) if typ in _PYTYPE else (0, 0)

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

    def _num_wrapper_of(self, owner):
        """(wrapper_name, nullable) when `owner` (a parameter / class_parameter / variable_declaration)
        declares a scalar Int/Long/Float -> Int32/Int64/Float32; else None. Respects the wrap dial. A
        vararg / generic / collection / Double type is not a scalar wrappable number, so it's left bare."""
        if not _WRAP_NUMERICS or owner is None:
            return None
        mods = next((c for c in owner.children if c.type == "modifiers"), None)
        if mods is not None and "vararg" in self.text(mods).split():
            return None                              # `vararg xs: Int` -> xs is a tuple, not a number
        nullable = False
        ut = next((c for c in owner.children if c.type == "user_type"), None)
        if ut is None:                               # `Int?` parses as nullable_type wrapping user_type
            nt = next((c for c in owner.children if c.type == "nullable_type"), None)
            if nt is not None:
                ut = next((c for c in nt.children if c.type == "user_type"), None)
                nullable = True
        if ut is None:
            return None
        typ = self.text(ut).split("<")[0].strip()
        w = _NUM_WRAPPER.get(typ)
        return (w, nullable) if w is not None else None

    def _add_num_coercion(self, owner, safe_name, out):
        """Append a body-prefix line coercing a declared-numeric PARAM to its wrapper (`n = Int32(n)`), so
        a literal-free chain off it still carries Kotlin's width semantics. A nullable param is guarded."""
        w = self._num_wrapper_of(owner)
        if w is None:
            return
        wname, nullable = w
        self._num_types.add(wname)
        out.append(f"if {safe_name} is not None: {safe_name} = {wname}({safe_name})"
                   if nullable else f"{safe_name} = {wname}({safe_name})")

    def _collect_params(self, pnode):
        # A Kotlin default value is a SIBLING of its `parameter` (after a `=` token),
        # not a child. Walk all children, pairing each default to the prior parameter.
        # Defaults render in the enclosing scope (not the param scope). A default that
        # references `self.` is NOT def-time-safe in Python (the `def` runs during
        # class-body exec) -> emit a None sentinel + a body guard instead. Returns
        # (bare names for scope, signature parts, body-prefix guards, numeric coercions).
        names, sig, pending, coerce = [], [], False, []
        for c in pnode.children:
            if c.type == "parameter":
                pid = self._name_of(c)
                if pid:
                    names.append(pid)
                    sig.append([self._safe(pid), None, self._param_type(c)])   # keep the declared TYPE
                    self._add_num_coercion(c, self._safe(pid), coerce)
                pending = False
            elif c.type == "=":
                pending = True
            elif pending and c.is_named:
                if sig:
                    sig[-1][1] = self.visit(c)
                pending = False
        parts, guards = [], []
        pnames = {p for p, _, _ in sig}
        seen_default = False
        for p, d, t in sig:
            ann = f": {t}" if t else ""               # emit the Kotlin type as a Python hint (kept, not dropped)
            if d is None:
                # Kotlin allows a required param AFTER a defaulted one (caller names it);
                # Python forbids it -> force =None to keep the signature valid (valid calls
                # always pass it, so no behavioral divergence).
                parts.append(f"{p}{ann}=None" if seen_default else f"{p}{ann}")
            elif self._default_call_time(d, pnames):  # references self/another param ->
                parts.append(f"{p}{ann}=None")        # not def-time-safe; sentinel + guard
                guards.append(f"if {p} is None: {p} = {d}")
                seen_default = True
            else:
                parts.append(f"{p}{ann}={d}")
                seen_default = True
        return names, parts, guards, coerce

    def _param_type(self, param_node):
        """The declared type of a `parameter`, cleaned to a Python-safe hint. Emitted so DI can build by
        TYPE instead of guessing by name; generic ARGUMENTS are kept (Provider<SystemTimeProvider> ->
        Provider[SystemTimeProvider]) -- that inner type is information we have and DI needs (which thing a
        lazy holder holds). Function/complex types are left un-annotated."""
        ut = next((c for c in param_node.children if c.type == "user_type"), None)
        if ut is None:
            nt = next((c for c in param_node.children if c.type == "nullable_type"), None)
            ut = next((c for c in nt.children if c.type == "user_type"), None) if nt is not None else None
        if ut is None:
            return None
        return self._clean_type(self.text(ut))

    def _clean_type(self, text):
        """A Kotlin type -> a Python-safe hint string. Keeps generics as brackets, strips packages and
        nullability; falls back to the bare base name, then None, when the shape isn't clean identifiers."""
        if "->" in text or "(" in text:                 # a function type -> no hint
            return None
        t = text.replace("?", "").replace("<", "[").replace(">", "]").strip()
        t = re.sub(r"[A-Za-z_][\w.]*", lambda m: self._strip_pkg(m.group(0)), t)
        names = re.findall(r"[A-Za-z_][\w.]*", t)
        clean = (names and all(p.isidentifier() for n in names for p in n.split("."))
                 and t.count("[") == t.count("]") and re.fullmatch(r"[\w.\[\], ]+", t))
        if clean:
            return t
        base = t.split("[")[0].strip()                  # fall back: base identifier only (prior behavior)
        return base if base and all(p.isidentifier() for p in base.split(".")) else None

    def _nonlocals(self, body_node, own_locals):
        # names assigned in `body_node` that live in an ENCLOSING function scope (not
        # this fn's own locals/params) -> `nonlocal` declarations.
        if not self._scopes or body_node is None:
            return []
        enclosing = set().union(*self._scopes)
        captured = sorted((self._assigned_names([body_node]) & enclosing) - own_locals)
        return [f"nonlocal {n}" for n in captured]

    def _local_names(self, node):
        # Local `val`/`var` declarations (and for-loop variables) shadow class members,
        # so collect them into the function's scope -> a local `score` resolves to the
        # local, not a same-named `fun score(...)`. Stops at nested fn/lambda/class.
        out = set()
        if node is None:
            return out
        stop = ("lambda_literal", "function_declaration", "anonymous_function",
                "object_declaration", "class_declaration")

        def walk(n):
            for c in n.children:
                if c.type in stop:
                    continue
                if c.type == "property_declaration":
                    nm = self._name_of(c, deep=True)
                    if nm:
                        out.add(nm)
                    mvd = next((k for k in c.children
                                if k.type == "multi_variable_declaration"), None)
                    if mvd is not None:                  # destructuring `val (a, b) = …`
                        out.update(self._destructure_names(mvd))
                elif c.type == "for_statement":
                    var = next((k for k in c.children if k.type in
                                ("variable_declaration", "identifier")), None)
                    if var is not None:
                        out.add(self.text(var))
                walk(c)

        walk(node)
        return out

    def _is_const(self, prop):
        mods = next((c for c in prop.children if c.type == "modifiers"), None)
        return mods is not None and "const" in self.text(mods).split()

    def _ctor_default(self, class_param):
        # `val x: T = expr` -> the default is the named child after the `=` token.
        seen_eq = False
        for c in class_param.children:
            if c.type == "=":
                seen_eq = True
            elif seen_eq and c.is_named:
                return self.visit(c)
        return None

    def _default_call_time(self, default, pnames):
        # A default is NOT def-time-safe (the `def` runs during class-body exec) when it references self,
        # another parameter, or a nested class that is module-aliased only at the file's end (a forward
        # ref) -- Kotlin evaluates defaults per call, so these late-bind via a sentinel + a body guard.
        if "self." in default:
            return True
        refs = set(re.findall(r"[A-Za-z_]\w*", default))
        return bool(refs & pnames) or bool(refs & self._nested_alias_names)

    @kind("class_declaration")
    def v_class_declaration(self, node):
        name = self._name_of(node) or "UnknownClass"
        mods = next((c.text.decode() for c in node.children if c.type == "modifiers"), "")
        if "@Dao" in mods:                          # a DAO interface -> a class of generated query bodies
            self._runtime_imports.add("from runtime.room import Dao")
            return datalayer.dao_class(node, name)
        cls = self._render_class(node, name)
        if "@Entity" in mods:                       # an entity -> its data class + a room table registration
            self._runtime_imports.add("from runtime.room import Col, Entity")
            self._ext_patches.append(datalayer.entity_schema(node, name, datalayer.enums()))
        if "@Database" in mods:                     # the DB -> register entities + wire DAO accessors
            self._runtime_imports.add("from runtime.room import Database")
            self._ext_patches.extend(datalayer.database_patches(node, name))
        return cls

    @kind("object_declaration")
    def v_object_declaration(self, node):
        # Kotlin `object Foo {…}` is a singleton. Emit the class, then rebind the name to
        # a sole instance -> `Foo.x`/`Foo.f()` resolve. The instantiation is deferred to
        # module end (after nested-type aliases) so __init__ can reference the object's own
        # nested types (e.g. `val x = VolumeLandmark(...)` in the body).
        name = self._name_of(node) or "UnknownObject"
        cls = self._render_class(node, name)
        self._ext_patches.append(f"{name} = {name}()")
        return cls

    @kind("object_literal")
    def v_object_literal(self, node):
        # `object : Super(args), Iface { members }` (an anonymous object in expression position) ->
        # hoist a local class above and return an instance. _render_class now carries the supertypes and
        # bakes the super's constructor args into __init__ (a lone no-arg super is dropped; then the bare
        # instantiation inherits the parent constructor -- same effect).
        self._lam += 1
        cname = f"_Obj{self._lam}"
        self._hoist.append(self._render_class(node, cname))
        return f"{cname}()"

    def _delegation_bases(self, node):
        """The supertype names a class/object declaration lists after `:` (generics/packages stripped)."""
        dss = next((c for c in node.named_children if c.type == "delegation_specifiers"), None)
        out = set()
        for ds in (dss.named_children if dss is not None else []):
            if ds.type != "delegation_specifier":
                continue
            ci = next((c for c in ds.named_children if c.type == "constructor_invocation"), None)
            ut = next((c for c in (ci or ds).named_children if c.type == "user_type"), None)
            if ut is not None:
                out.add(self._strip_pkg(self.text(ut).split("<")[0].strip()))
        return out

    def _render_class(self, node, name):
        body_node = next((c for c in node.children
                          if c.type in ("class_body", "enum_class_body")), None)
        ctor_params, ctor_defaults, ctor_nodes, ctor_types = [], {}, {}, {}
        pc = next((c for c in node.children if c.type == "primary_constructor"), None)
        if pc is not None:
            cps = next((c for c in pc.named_children if c.type == "class_parameters"), None)
            container = cps if cps is not None else pc
            for pn in container.named_children:
                if pn.type == "class_parameter":
                    nm = self._name_of(pn)
                    if nm:
                        ctor_params.append(nm)
                        ctor_nodes[nm] = pn             # kept for declared-numeric coercion below
                        ctor_types[nm] = self._param_type(pn)   # keep the declared TYPE (for DI-by-type)
                        dflt = self._ctor_default(pn)   # `val x: T = expr` -> __init__ default
                        if dflt is not None:
                            ctor_defaults[nm] = dflt

        # Kotlin supertypes (`class X(...) : Base(args), Iface`): KEEP the hierarchy -- structure we have.
        # Bases go on the class line; a parent constructor invocation becomes `super().__init__(args)` at
        # the top of __init__ (Kotlin runs the parent's constructor before the child's body).
        bases, super_va, has_super_call = [], None, False
        dss = next((c for c in node.named_children if c.type == "delegation_specifiers"), None)
        for ds in (dss.named_children if dss is not None else []):
            if ds.type != "delegation_specifier":
                continue
            ci = next((c for c in ds.named_children if c.type == "constructor_invocation"), None)
            ut = next((c for c in (ci or ds).named_children if c.type == "user_type"), None)
            if ut is not None:
                bases.append(self._strip_pkg(self.text(ut).split("<")[0].strip()))
            if ci is not None and not has_super_call:
                has_super_call = True
                super_va = next((c for c in ci.named_children if c.type == "value_arguments"), None)

        prev = self._members
        self._members = set(ctor_params)
        if body_node is not None and body_node.type == "enum_class_body":
            self._members |= {"name", "ordinal"}   # implicit enum props: name.x -> self.name.x
        props, getters, lazies, methods, nested, comps, inits = [], [], [], [], [], [], []
        relocated = []                   # a nested child of THIS class (`object Idle : Screen(...)` inside
        entries = []                     # Screen): Python can't subclass mid-definition -> define at file end
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
                    recv = self._ext_receiver(c)
                    if recv is not None:        # member extension fn -> top-level def +
                        base = self._strip_pkg(recv.split("<")[0].strip())   # patch onto the receiver
                        fname = self._safe(self._name_of(c) or "fn")
                        self._ext_patches.append(self._function(c, with_self=True))
                        if base and base not in _BUILTIN_RECVRS:
                            self._ext_patches.append(f"{base}.{fname} = {fname}")
                    else:
                        nm = self._name_of(c)
                        if nm:
                            self._members.add(nm)
                        methods.append(c)
                elif c.type in ("class_declaration", "object_declaration"):
                    if name in self._delegation_bases(c):
                        relocated.append(c)      # inherits the class it sits inside -> file-end def
                    else:
                        nested.append(c)
                elif c.type == "companion_object":
                    comps.append(c)
                elif c.type == "anonymous_initializer":
                    inits.append(c)
                elif c.type in _OOP_DEFER:
                    raise Untranspilable(c, "class member needs the OOP-model pass")
                # else: enum_entry / modifiers / trivia -> consumed, not emitted

        for n in nested + relocated:        # nested classes are module-aliased at file end -> referencing
            nm = self._name_of(n)           # one in a default arg is a forward ref (late-bind it)
            if nm:
                self._nested_alias_names.add(nm)
        self._scopes.append(set(ctor_params))
        sig, guards, seen_default = ["self"], [], False
        safe_names = {self._safe(p) for p in ctor_params}
        for p in ctor_params:
            sp = self._safe(p)
            d = ctor_defaults.get(p)
            t = ctor_types.get(p)
            ann = f": {t}" if t else ""                      # keep the declared type as a hint (DI-by-type)
            if d is None:
                sig.append(f"{sp}{ann}=None" if seen_default else f"{sp}{ann}")   # required-after-default
            elif self._default_call_time(d, safe_names):    # sentinel for self/param refs
                sig.append(f"{sp}{ann}=None")
                guards.append(f"if {sp} is None: {sp} = {d}")
                seen_default = True
            else:
                sig.append(f"{sp}{ann}={d}")
                seen_default = True
        init_body = list(guards)
        if has_super_call:                                 # parent constructed first, after default-guards
            init_body.append(f"super().__init__({self._render_args(super_va)})")
        for p in ctor_params:                              # coerce a declared-numeric field to its
            sp = self._safe(p)                             # wrapper at construction, so every later
            w = self._num_wrapper_of(ctor_nodes.get(p))    # `self.x` read carries the width semantics
            if w is None:
                init_body.append(f"self.{sp} = {sp}")
            else:
                wname, nullable = w
                self._num_types.add(wname)
                init_body.append(f"self.{sp} = ({wname}({sp}) if {sp} is not None else None)"
                                 if nullable else f"self.{sp} = {wname}({sp})")
        class_attrs = []
        for p in props:
            if self._is_const(p):                          # `const val` is static -> a class-level attribute
                class_attrs.append(self._render_property(p, as_self=False))  # so Obj.CONST / Class.CONST work
                continue
            before = len(self._hoist)                      # flush hoists (e.g. a multi-statement
            line = self._render_property(p, as_self=True)  # `combine(…){ … }` lambda -> def _lamN)
            init_body += self._hoist[before:]              # before the assignment that uses them
            del self._hoist[before:]
            init_body.append(line)
        for ini in inits:                                  # init { … } -> __init__ body
            blk = next((k for k in ini.named_children if k.type == "block"), None)
            if blk is not None:
                init_body += self.render_statements(self.named(blk))
        self._scopes.pop()

        lines = list(class_attrs)                          # class-level consts first
        if init_body and init_body != ["super().__init__()"]:   # a lone no-arg super call = pure no-op
            lines.append(f"def __init__({', '.join(sig)}):\n{_block(init_body)}")
        # a kotlin `data class` gets copy(field=new) and VALUE equality (the reactive scheduler's
        # changed-check and UiState.copy(...) updates depend on both).
        mods_txt = next((c.text.decode() for c in node.children if c.type == "modifiers"), "")
        if "data" in mods_txt.split() and ctor_params:
            sps = [self._safe(p) for p in ctor_params]
            kw = ", ".join(f"{p!r}: self.{p}" for p in sps)
            lines.append("def copy(self, **_changes):\n" + _block(
                [f"_kw = {{{kw}}}", "_kw.update(_changes)", "return type(self)(**_kw)"]))
            mine = ", ".join(f"self.{p}" for p in sps) + ("," if len(sps) == 1 else "")
            theirs = ", ".join(f"other.{p}" for p in sps) + ("," if len(sps) == 1 else "")
            lines.append("def __eq__(self, other):\n" + _block(
                ["if type(other) is not type(self):", "    return NotImplemented",
                 f"return ({mine}) == ({theirs})"]))
            lines.append("def __hash__(self):\n" + _block(   # content hash; unhashable fields (a List)
                ["try:", f"    return hash((type(self), {mine}))",   # fall back to identity
                 "except TypeError:", "    return object.__hash__(self)"]))
        # a companion's members are in scope (unqualified) inside this class's methods -> resolve a bare
        # `USER_TABLES` to `ClassName.USER_TABLES`. Set BEFORE rendering methods; instance members win, so
        # drop any name that is also an instance member (Kotlin precedence).
        comp_members = self._companion_members(comps) - self._members
        prev_sm, prev_sc = self._static_members, self._static_class
        if comp_members:
            self._static_members, self._static_class = comp_members, name
        groups = {}                          # group by name -> Kotlin method overloading
        for m in methods:
            groups.setdefault(self._name_of(m), []).append(m)
        for mname, variants in groups.items():
            if len(variants) == 1:
                lines.append(self.visit(variants[0]))
            else:                            # >1 same-named -> type-dispatching wrapper
                lines += self._render_overloads(mname, variants)
        lines += [self._render_getter(g) for g in getters]  # computed props -> @property
        lines += [self._render_lazy(z) for z in lazies]     # by lazy -> cached @property
        for n in nested:                                    # alias nested types to module
            nm = self._name_of(n)                           # level: Inner = Outer.Inner
            if nm:
                self._nested_aliases.append(f"{nm} = {name}.{nm}")
        lines += [self.visit(n) for n in nested]
        for n in relocated:                 # a child of this class: define at file end (the parent exists
            nm = self._name_of(n)           # by then), run its own patches (e.g. singleton instantiation),
            before = len(self._ext_patches)                 # then attach it back as Outer.Child.
            src = self.visit(n)
            own = self._ext_patches[before:]
            del self._ext_patches[before:]
            self._ext_patches.append(src)
            self._ext_patches.extend(own)
            if nm:
                self._ext_patches.append(f"{name}.{nm} = {nm}")
        for comp in comps:                                 # companion -> static members
            lines += self._render_companion(comp, name)
        self._static_members, self._static_class = prev_sm, prev_sc
        _TYPE_FIELDS[name] = set(self._members)             # for extension-receiver lookup
        self._members = prev

        body = _block(lines) if lines else _block([])
        cls = f"class {name}({', '.join(bases)}):\n{body}" if bases else f"class {name}:\n{body}"
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
        out.append(f"{name}._entries = KtList([{listed}])")   # values()/entries()/valueOf
        out.append(f"{name}.values = staticmethod(lambda: {name}._entries)")
        out.append(f"{name}.entries = {name}._entries")
        out.append(f"{name}.valueOf = staticmethod("
                   f"lambda s: next(e for e in {name}._entries if e.name == s))")
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

    def _companion_members(self, comps):
        """Names a companion object declares (vals + functions) -> referenced unqualified from the enclosing
        class's methods, so a bare `USER_TABLES` / `helper()` resolves to ClassName.<name>."""
        out = set()
        for comp in comps:
            cbody = next((c for c in comp.named_children if c.type == "class_body"), comp)
            for c in cbody.named_children:
                nm = (self._name_of(c, deep=True) if c.type == "property_declaration"
                      else self._name_of(c) if c.type == "function_declaration" else None)
                if nm:
                    out.add(nm)
        return out

    def _render_companion(self, comp, cls_name):
        cbody = next((c for c in comp.named_children if c.type == "class_body"), comp)
        cprops = [c for c in cbody.named_children if c.type == "property_declaration"]
        cfuncs = [c for c in cbody.named_children if c.type == "function_declaration"]
        names = {self._name_of(p, deep=True) for p in cprops}
        names |= {self._name_of(f) for f in cfuncs}
        names.discard(None)
        prev_sm, prev_sc = self._static_members, self._static_class
        self._static_members, self._static_class = names, cls_name
        out = []
        for p in cprops:                                   # companion props -> class-level
            before = len(self._hoist)
            r = self._render_property(p, as_self=False)
            hoisted = self._hoist[before:]                    # e.g. an object-literal's lifted class
            del self._hoist[before:]                          # -> emit it before the use, not drop it
            if "=" in r and cls_name in r.split("=", 1)[1]:   # initializer references the
                self._ext_patches += hoisted                  # enclosing class -> defer to
                self._ext_patches.append(f"{cls_name}.{r}")   # module level (the class isn't
            else:                                             # bound during its own body)
                out += hoisted
                out.append(r)
            if self._is_const(p):       # `const val` is import-and-use-bare across files;
                cn = self._name_of(p, deep=True)              # alias it to the module level
                if cn:
                    self._ext_patches.append(f"{cn} = {cls_name}.{cn}")
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
        if deep:  # property_declaration -> variable_declaration -> id. Check this FIRST:
            vd = next((c for c in node.children if c.type == "variable_declaration"), None)
            if vd:  # a direct identifier here would be the VALUE (`var x = someVar`), not x
                pid = next((c for c in vd.children if c.type in ids), None)
                if pid is not None:
                    return self.text(pid)
        direct = next((c for c in node.children if c.type in ids), None)
        return self.text(direct) if direct is not None else None

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
        if deleg is not None:
            # `val/var x by D` at function scope (Compose `by remember`/`by collectAsState`, Kotlin
            # `by lazy`): bind x to the delegate object; every read/write of x then goes through
            # `x.value` (Kotlin reads a delegate via getValue/setValue, which for State/MutableState/
            # Lazy is `.value`). The read/write rewrite is in v_identifier via self._delegated.
            name = self._name_of(node, deep=True) or "_prop"
            expr = next((c for c in self.named(deleg)), None)
            val = self.visit(expr) if expr is not None else "None"
            line = f"{self._safe(name)} = {val}"
            self._delegated.add(name)
            return line
        mvd = next((c for c in node.children
                    if c.type == "multi_variable_declaration"), None)
        if mvd is not None:     # destructuring `val (a, b) = expr` -> a, b = expr
            target = ", ".join(self._safe(n) for n in self._destructure_names(mvd))
            decl = mvd
        else:
            name = self._name_of(node, deep=True) or "_"
            target = f"self.{self._safe(name)}" if (as_self and name in self._members) \
                else self._safe(name)
            decl = next((c for c in node.children
                         if c.type == "variable_declaration"), None)
        # value is the named child after the (multi_)variable_declaration
        kids = self.named(node)
        val_node = None
        for i, c in enumerate(kids):
            if c is decl and i + 1 < len(kids):
                val_node = kids[i + 1]
                break
        if val_node is None:
            return f"{target} = None"
        w = self._num_wrapper_of(decl) if mvd is None else None    # typed single-var -> wrap the RHS so a
        if w is not None and not w[1] and not self._renders_stmt(val_node):   # literal-free init carries
            wname = w[0]                                           # the width (nullable/block forms below)
            inner = self.visit(val_node)                          # may push hoists; the caller flushes
            self._num_types.add(wname)
            if inner.startswith(wname + "("):                     # value is already this wrapper (a same-
                return f"{target} = {inner}"                      # type literal) -> don't double-wrap
            return f"{target} = {wname}({inner})"
        return self._distribute(val_node, f"{target} = ")
