"""
declarations.py — module / function / class / property handlers. Statement-shaped
nodes return a (possibly multi-line) Python STRING; block bodies indent + join their
children. Member/scope state (`self._members`, `self._scopes`) drives `this.x`/member
resolution in the identifier handler.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind  # noqa: E402
from util import block as _block  # noqa: E402

_TOP_DECLS = {"class_declaration", "object_declaration", "function_declaration",
              "property_declaration"}


class Declarations:
    @kind("source_file")
    def v_source_file(self, node):
        parts = [self.visit(c) for c in self.named(node) if c.type in _TOP_DECLS]
        return "\n\n\n".join(p for p in parts if p)

    @kind("function_declaration")
    def v_function_declaration(self, node):
        name = self._name_of(node) or "unknown_func"
        params = []
        in_class = node.parent is not None and node.parent.type == "class_body"
        if in_class:
            params.append("self")
        pnode = next((c for c in node.children if c.type == "function_value_parameters"), None)
        if pnode:
            for p in pnode.named_children:
                if p.type == "parameter":
                    pid = self._name_of(p)
                    if pid:
                        params.append(pid)
        body_node = next((c for c in node.children
                          if c.type in ("function_body", "block")), None)
        self._scopes.append(set(params[1:] if in_class else params))
        body = self._render_function_body(body_node)
        self._scopes.pop()
        return f"def {name}({', '.join(params)}):\n{body}"

    @kind("class_declaration")
    def v_class_declaration(self, node):
        name = self._name_of(node) or "UnknownClass"
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
        props, methods = [], []
        if body_node:
            for c in body_node.named_children:
                if c.type == "property_declaration":
                    nm = self._name_of(c, deep=True)
                    if nm:
                        self._members.add(nm)
                    props.append(c)
                elif c.type == "function_declaration":
                    nm = self._name_of(c)
                    if nm:
                        self._members.add(nm)
                    methods.append(c)

        lines = []
        init_body = [f"self.{p} = {p}" for p in ctor_params]
        self._scopes.append(set(ctor_params))
        init_body += [self._render_property(p, as_self=True) for p in props]
        self._scopes.pop()
        if ctor_params or props:
            args = ", ".join(["self"] + ctor_params)
            lines.append(f"def __init__({args}):\n{_block(init_body)}")
        lines += [self.visit(m) for m in methods]
        self._members = prev

        body = _block(lines) if lines else _block([])
        return f"class {name}:\n{body}"

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
                return _block([f"return {self.visit(kids[0])}"]) if kids else _block([])
            inner = self.named(body_node)                          # function_body -> block
            if inner and inner[0].type == "block":
                body_node = inner[0]
        # body_node is now a block: render its statements
        stmts = [self.visit(c) for c in self.named(body_node)]
        return _block(stmts)

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
