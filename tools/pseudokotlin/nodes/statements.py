"""
statements.py — control flow. Statement-shaped nodes return a (multi-line) Python
string. `if` chooses its form from its OWN shape: simple branches -> ternary; block
branches -> an if-statement. Branch nodes in this grammar are a `block` or a single
statement node (there is no control_structure_body wrapper).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind  # noqa: E402
from util import block as _block  # noqa: E402


class Statements:
    @kind("if_expression")
    def v_if(self, node):
        kids = self.named(node)
        pc = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        if pc is not None:
            inner = self.named(pc)
            cond = self.visit(inner[0]) if inner else "True"
            branches = [k for k in kids if k is not pc]
        else:
            cond = self.visit(kids[0]) if kids else "True"
            branches = kids[1:]
        then_n = branches[0] if branches else None
        else_n = branches[1] if len(branches) > 1 else None

        if self._is_block(then_n) or self._is_block(else_n):
            out = [f"if {cond}:", self._suite(then_n)]
            if else_n is not None and else_n.type == "if_expression":
                out.append("el" + self.visit(else_n))          # else-if -> elif
            elif else_n is not None:
                out += ["else:", self._suite(else_n)]
            return "\n".join(out)
        then_e = self.visit(then_n) if then_n is not None else "None"
        else_e = self.visit(else_n) if else_n is not None else "None"
        return f"({then_e} if {cond} else {else_e})"

    @kind("for_statement")
    def v_for(self, node):
        var = next((c for c in node.children if c.type in
                    ("variable_declaration", "identifier")), None)
        var_txt = self.text(var) if var is not None else "item"
        body = next((c for c in node.children if c.type == "block"), None)
        it = self._loop_iterable(node, exclude=var)
        return f"for {var_txt} in {it}:\n{self._suite(body)}"

    @kind("while_statement")
    def v_while(self, node):
        cond = self._condition(node)
        body = next((c for c in node.children if c.type == "block"), None)
        return f"while {cond}:\n{self._suite(body)}"

    @kind("assignment")
    def v_assignment(self, node):
        kids = self.named(node)
        op = next((c.type for c in node.children
                   if c.type in ("=", "+=", "-=", "*=", "/=", "%=")), "=")
        return f"{self.visit(kids[0])} {op} {self.visit(kids[-1])}"

    @kind("return_expression")
    def v_return(self, node):
        kids = self.named(node)
        return f"return {self.visit(kids[0])}" if kids else "return"

    @kind("throw_expression")
    def v_throw(self, node):
        kids = self.named(node)
        return f"raise {self.visit(kids[0])}" if kids else "raise"

    # ---- helpers --------------------------------------------------------- #
    def _condition(self, node):
        pc = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        if pc is not None:
            inner = self.named(pc)
            return self.visit(inner[0]) if inner else "True"
        kids = self.named(node)
        return self.visit(kids[0]) if kids else "True"

    @staticmethod
    def _is_block(n):
        return n is not None and n.type == "block"

    def _suite(self, n):
        """Render a `block` or a single statement node as an indented Python suite."""
        if n is None:
            return _block([])
        if n.type == "block":
            return _block([self.visit(c) for c in self.named(n)])
        return _block([self.visit(n)])

    def _loop_iterable(self, node, exclude):
        kinds = ("call_expression", "navigation_expression", "identifier",
                 "binary_expression", "range_expression", "parenthesized_expression",
                 "index_expression")
        cand = next((c for c in node.children
                     if c.type in kinds and c is not exclude), None)
        return self.visit(cand) if cand is not None else "[]"
