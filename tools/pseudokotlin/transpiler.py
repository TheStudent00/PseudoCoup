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
        self._delegated = set()  # local `val/var x by D` names -> read/write through `x.value`
        self._hoist = []         # pending helper defs (multi-statement lambdas), flushed
        self._lam = 0            #   before the statement that produced them
        self._static_members = set()  # companion members -> ClassName.x resolution
        self._static_class = None     # the enclosing class name for those
        self._ext_patches = []        # `Recv.fn = fn` lines, flushed at module end
        self._nested_aliases = []     # `Inner = Outer.Inner` lines, flushed at module end
        self._enum_types = set()      # enum class names -> their members/extensions see name/ordinal

    def transpile(self, source: bytes) -> str:
        tree = parse(source)
        self._scan_enums(tree.root_node)     # order-independent: an extension may precede its enum
        return self.visit(tree.root_node)

    def _scan_enums(self, node):
        if node.type == "class_declaration" and any(
                c.type == "enum_class_body" for c in node.children):
            nm = self._name_of(node)
            if nm:
                self._enum_types.add(nm)
        for c in node.children:
            self._scan_enums(c)

    def render_statements(self, nodes) -> list:
        """Render statement nodes to lines, flushing each statement's hoisted helper
        defs (e.g. multi-statement lambdas) immediately BEFORE that statement."""
        lines = []
        for c in nodes:
            lines += self.stmt_lines(c)
        return lines

    def stmt_lines(self, node) -> list:
        inc = self._maybe_increment(node)       # statement-position ++/-- -> clean `n += 1`
        if inc is not None:
            return [inc]
        before = len(self._hoist)
        # statement-position if/when render straight to a Python statement (no value temp); value
        # position goes through v_if/v_when, which hoist when needed.
        if node.type == "if_expression":
            s = self._if(node, "")
        elif node.type == "when_expression":
            s = self._when(node, "")
        else:
            s = self.visit(node)
        out = self._hoist[before:]
        del self._hoist[before:]
        if s:
            out.append(s)
        return out

    def _maybe_increment(self, node):
        """`n++`/`n--` in STATEMENT position -> `n += 1`/`n -= 1` (no temp); None
        otherwise (value position hoists a temp in v_unary)."""
        if node.type == "unary_expression":
            ops = [c.type for c in node.children if not c.is_named]
            if "++" in ops or "--" in ops:
                operand = self.visit(self.named(node)[0])
                return f"{operand} {'+=' if '++' in ops else '-='} 1"
        return None

    @staticmethod
    def is_value(node) -> bool:
        return node.type not in _STMT_KINDS
