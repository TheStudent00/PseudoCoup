"""
dispatch.py — the routing core. ONE registry, ONE dispatch point.

A handler registers itself for one or more grammar node kinds with `@kind(...)`;
`Visitor.visit` looks the node's type up in the registry and calls it. The registry
(`_route`) is an explicit, introspectable dict — that is the whole point: the
coverage gate can diff its keys against the live grammar, which an if-chain's
branches can never be.

Per-handler contract — MAP · WRAP · FAIL, never emit-and-hope:
  - MAP  : return Python guaranteed to parse.
  - WRAP : `self.wrap(...)` into the shim registry when Kotlin has no Python
           equivalent (e.g. 16.dp -> dp(16)).
  - FAIL : raise Untranspilable. Unknown/parse-error nodes fail loudly.
"""


class Untranspilable(Exception):
    def __init__(self, node, why: str = ""):
        t = getattr(node, "type", "?")
        loc = getattr(node, "start_point", "?")
        super().__init__(f"{why or 'cannot transpile'} [{t} @ {loc}]")
        self.node = node


def kind(*types: str):
    """Register the decorated method as the handler for these grammar node kinds."""
    def deco(fn):
        fn._kinds = tuple(types)
        return fn
    return deco


class Visitor:
    """Base dispatcher. Subclasses add `@kind`-decorated handlers; the registry is
    rebuilt for each subclass from its (and its bases') decorated methods."""

    _route: dict = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        route = {}
        for base in reversed(cls.__mro__):           # bases first; subclass overrides
            for member in vars(base).values():
                for t in getattr(member, "_kinds", ()):
                    route[t] = member
        cls._route = route

    @classmethod
    def routed_kinds(cls) -> set:
        return set(cls._route)

    def visit(self, node):
        if node.type == "ERROR" or getattr(node, "is_missing", False):
            raise Untranspilable(node, "parser error / missing node")
        handler = self._route.get(node.type)
        if handler is None:
            return self.unrouted(node)
        return handler(self, node)

    def unrouted(self, node):
        """No handler for this kind. P0: always fails (no handlers yet). P1+: a
        kind reaches here only if it is neither handled nor classified — which the
        coverage gate forbids — so failing loudly is correct."""
        raise Untranspilable(node, "no handler registered")

    def wrap(self, *args, **kw):
        raise NotImplementedError("wrap registry arrives in P3 (the shim layer)")
