"""
transpiler.py — the Kotlin→Python transpiler. KtToPy mixes the handler concerns
(each a set of @kind-decorated methods) into the Visitor; __init_subclass__ collects
them into the _route registry. Handlers are ported deliberately from the donor
(tools/transpiler/literal_transpiler.py) under the map·wrap·fail contract.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dispatch import Visitor  # noqa: E402
from parse import parse  # noqa: E402
from nodes.expressions import Expressions  # noqa: E402
from nodes.statements import Statements  # noqa: E402
from nodes.declarations import Declarations  # noqa: E402


# statement-shaped node kinds whose value is not an expression (can't be `return`ed)
_STMT_KINDS = {"assignment", "property_declaration", "for_statement",
               "while_statement", "do_while_statement", "return_expression",
               "throw_expression"}


class KtToPy(Expressions, Statements, Declarations, Visitor):
    def __init__(self):
        self._members = set()    # current class's member names -> self.x resolution
        self._scopes = []        # stack of local-name sets (params/locals shadow members)
        self._hoist = []         # pending helper defs (multi-statement lambdas), flushed
        self._lam = 0            #   before the statement that produced them
        self._static_members = set()  # companion members -> ClassName.x resolution
        self._static_class = None     # the enclosing class name for those
        self._ext_patches = []        # `Recv.fn = fn` lines, flushed at module end
        self._nested_aliases = []     # `Inner = Outer.Inner` lines, flushed at module end

    def transpile(self, source: bytes) -> str:
        tree = parse(source)
        return self.visit(tree.root_node)

    def render_statements(self, nodes) -> list:
        """Render statement nodes to lines, flushing each statement's hoisted helper
        defs (e.g. multi-statement lambdas) immediately BEFORE that statement."""
        lines = []
        for c in nodes:
            lines += self.stmt_lines(c)
        return lines

    def stmt_lines(self, node) -> list:
        before = len(self._hoist)
        s = self.visit(node)
        out = self._hoist[before:]
        del self._hoist[before:]
        if s:
            out.append(s)
        return out

    @staticmethod
    def is_value(node) -> bool:
        return node.type not in _STMT_KINDS
