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

# Names that must never be qualified onto an apply/run/with receiver (they are globals, not receiver
# members): Python builtins + every runtime-provided wrapper name (listOf, JSONObject, require, …).
# Cached once -- registry.provided() walks the wrapper modules.
_GLOBAL_NAMES = None


def _global_names():
    global _GLOBAL_NAMES
    if _GLOBAL_NAMES is None:
        import builtins
        import registry
        _GLOBAL_NAMES = set(dir(builtins)) | set(registry.provided())
    return _GLOBAL_NAMES


class KtToPy(Expressions, Statements, Declarations, Visitor):
    def __init__(self):
        self._members = set()    # current class's member names -> self.x resolution
        self._scopes = []        # stack of local-name sets (params/locals shadow members)
        self._loop_vars = []     # stack of for-loop variable names -> bind per-iteration in captured lambdas
        self._num_types = set()  # numeric wrapper types used in this file -> `from runtime.numbers import …`
        self._delegated = set()  # local `val/var x by D` names -> read/write through `x.value`
        self._hoist = []         # pending helper defs (multi-statement lambdas), flushed
        self._lam = 0            #   before the statement that produced them
        self._static_members = set()  # companion members -> ClassName.x resolution
        self._static_class = None     # the enclosing class name for those
        self._ext_patches = []        # `Recv.fn = fn` lines, flushed at module end
        self._nested_aliases = []     # `Inner = Outer.Inner` lines, flushed at module end
        self._nested_alias_names = set()  # the names those aliases bind -> a default that refs one is forward
        self._enum_types = set()      # enum class names -> their members/extensions see name/ordinal
        self._implicit_recv = []      # stack of apply/run/with receiver temps -> bare member calls bind here
        self._top_level = set()       # this file's top-level decl names -> never an implicit-receiver member
        self._GLOBALS = _global_names()

    def transpile(self, source: bytes) -> str:
        tree = parse(source)
        self._scan_enums(tree.root_node)     # order-independent: an extension may precede its enum
        self._scan_top_level(tree.root_node)
        return self.visit(tree.root_node)

    def _scan_top_level(self, root):
        # top-level fun/val/class/object names -> excluded from implicit-receiver qualification (a bare
        # `helper()` inside an apply on another object is the top-level helper, not a receiver method).
        for c in root.named_children:
            if c.type in ("function_declaration", "property_declaration",
                          "class_declaration", "object_declaration"):
                nm = self._name_of(c, deep=(c.type == "property_declaration"))
                if nm:
                    self._top_level.add(nm)

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
