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


class Declarations:
    @kind("source_file")
    def v_source_file(self, node):
        parts = [self.visit(c) for c in self.named(node) if c.type in _TOP_DECLS]
        return "\n\n\n".join(p for p in parts if p)

    @kind("function_declaration")
    def v_function_declaration(self, node):
        in_class = node.parent is not None and node.parent.type == "class_body"
        return self._function(node, with_self=in_class)

    def _function(self, node, with_self, decorator=""):
        name = self._name_of(node) or "unknown_func"
        params = ["self"] if with_self else []
        pnode = next((c for c in node.children if c.type == "function_value_parameters"), None)
        if pnode:
            for p in pnode.named_children:
                if p.type == "parameter":
                    pid = self._name_of(p)
                    if pid:
                        params.append(pid)
        body_node = next((c for c in node.children
                          if c.type in ("function_body", "block")), None)
        self._scopes.append(set(params[1:] if with_self else params))
        body = self._render_function_body(body_node)
        self._scopes.pop()
        head = f"{decorator}\n" if decorator else ""
        return f"{head}def {name}({', '.join(params)}):\n{body}"

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
        props, getters, methods, nested, comps, inits = [], [], [], [], [], []
        if body_node:
            for c in body_node.named_children:
                if c.type == "property_declaration":
                    nm = self._name_of(c, deep=True)
                    if nm:
                        self._members.add(nm)
                    if any(k.type == "getter" for k in c.children):   # computed property
                        getters.append(c)
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
        init_body = [f"self.{p} = {p}" for p in ctor_params]
        init_body += [self._render_property(p, as_self=True) for p in props]
        for ini in inits:                                  # init { … } -> __init__ body
            blk = next((k for k in ini.named_children if k.type == "block"), None)
            if blk is not None:
                init_body += self.render_statements(self.named(blk))
        self._scopes.pop()

        lines = []
        if ctor_params or props or inits:
            args = ", ".join(["self"] + ctor_params)
            lines.append(f"def __init__({args}):\n{_block(init_body)}")
        lines += [self.visit(m) for m in methods]
        lines += [self._render_getter(g) for g in getters]  # computed props -> @property
        lines += [self.visit(n) for n in nested]
        for comp in comps:                                 # companion -> static members
            lines += self._render_companion(comp, name)
        self._members = prev

        body = _block(lines) if lines else _block([])
        return f"class {name}:\n{body}"

    def _render_getter(self, prop):
        name = self._name_of(prop, deep=True) or "_prop"
        getter = next((c for c in prop.children if c.type == "getter"), None)
        body_node = next((c for c in getter.named_children
                          if c.type in ("function_body", "block")), None) if getter else None
        self._scopes.append(set())
        body = self._render_function_body(body_node)
        self._scopes.pop()
        return f"@property\ndef {name}(self):\n{body}"

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

    def _render_function_body(self, body_node):
        if body_node is None:
            return _block([])
        if body_node.type == "function_body":
            if any(c.type == "=" for c in body_node.children):     # `= expr` body
                kids = self.named(body_node)
                if not kids:
                    return _block([])
                before = len(self._hoist)
                v = self.visit(kids[0])
                hoist = self._hoist[before:]
                del self._hoist[before:]
                return _block(hoist + [f"return {v}"])
            inner = self.named(body_node)                          # function_body -> block
            if inner and inner[0].type == "block":
                body_node = inner[0]
        # body_node is now a block: render its statements (hoist-aware)
        return _block(self.render_statements(self.named(body_node)))

    def _render_property(self, node, as_self):
        name = self._name_of(node, deep=True) or "_"
        target = f"self.{name}" if (as_self and name in self._members) else name
        # value is the named child after the variable_declaration
        kids = self.named(node)
        val_node = None
        for i, c in enumerate(kids):
            if c.type == "variable_declaration" and i + 1 < len(kids):
                val_node = kids[i + 1]
                break
        if val_node is None:
            return f"{target} = None"
        if val_node.type == "when_expression":
            return self._when(val_node, f"{target} = ")
        if val_node.type == "if_expression" and self._if_is_block(val_node):
            return self._if(val_node, f"{target} = ")
        return f"{target} = {self.visit(val_node)}"
