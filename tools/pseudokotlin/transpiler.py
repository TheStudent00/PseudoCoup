"""
transpiler.py — the Kotlin→Python transpiler proper. KtToPy is a Visitor; its
handlers (added in P1, each `@kind(...)`-decorated, ported deliberately from the
donor `tools/transpiler/literal_transpiler.py`) are the ROUTED set.

P0: no handlers yet — `_route` is empty on purpose, so the coverage report shows the
entire construct surface as UNROUTED (the worklist). The spine, the registry, and
the gate exist before a single handler is written.
"""
from dispatch import Visitor


class KtToPy(Visitor):
    pass  # handlers land in P1
