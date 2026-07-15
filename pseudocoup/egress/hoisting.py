"""Shared prelude-accumulation for PseudoCoup emitters (upgrade unit U3).

DECISION RECORD (U3, 2026-07-14, under Dee's standing "natural answer" norm):
the shared mechanism is a MIXIN in a new helper module under pseudocoup/egress/,
not a new emitter base class. Rationale: the 12 emitters share no base class
today and rewriting their class hierarchy for one capability would be a far
larger structural change than U3 needs; a mixin lets each emitter opt in with a
one-line bases change plus a SELF_INDENTING_NODES declaration, leaves untouched
emitters byte-identical, and delegates the actual hoisting state machine to
pseudoir.Hoister (the single authority, per the upgrade mission). The only new
name introduced is this module and HoistingMixin.

How it works
------------
An emitter that needs to lower an expression-position construct into preceding
statements (e.g. Go dict-membership: `k in d` has no legal Go expression form
that binds the comma-ok result inline without an IIFE) calls, inside its
expression visitor:

    tmp, _ = self.hoister.hoist_stmt(["_, @TMP@ := d[k]"], "@TMP@")
    return tmp

The Hoister (pseudoir.hoist()) appends the statement lines to its .prelude with
@TMP@ replaced by a fresh temp name, and the visitor returns the temp as the
expression. The pending prelude is then drained at the nearest STATEMENT
boundary:

  - simple statements: the emitter's block-body loops call self.emit_stmt(stmt)
    instead of self.generate(stmt) + manual indent bookkeeping; emit_stmt emits
    any prelude accumulated while generating the statement, indented at the
    current level, BEFORE the statement itself.
  - compound-statement headers (if/while/for conditions and iterables): the
    visit_* method calls self.prelude_block() immediately after generating the
    header expression and splices those lines before the header line, so a
    hoist inside a condition cannot leak into the block body (whose own
    emit_stmt calls would otherwise drain it at the wrong indent level).

One Hoister lives per emitter instance for the whole module, so temp names
(_h0, _h1, ...) are monotonic across the file and can never collide even when
several statements hoist.

KNOWN LIMITATIONS (recorded, not hidden):
  - a hoist inside a `while` condition is evaluated ONCE before the loop, not
    per iteration; the old Go IIFE was iteration-correct in that position.
    Correct per-iteration lowering (loop-and-break rewrite) is future work.
  - a hoist inside an elif condition (Go's `} else if` chaining via
    generate().lstrip()) would splice its prelude mid-line; no current
    construct produces this, but it is not defended.
"""

from pseudoir import hoist


class HoistingMixin:
    """Prelude-accumulating statement emission on top of pseudoir.Hoister.

    Consumers must provide (all standard across PseudoCoup emitters):
    generate(node), _indent(), and override SELF_INDENTING_NODES with the node
    types whose visit_* methods return already-indented text.
    """

    # Node types whose visit_* output already begins with self._indent().
    SELF_INDENTING_NODES = ()

    @property
    def hoister(self):
        h = getattr(self, "_hoister", None)
        if h is None:
            h = hoist()
            self._hoister = h
        return h

    def drain_prelude(self):
        """Return and clear the pending hoisted statement lines (unindented)."""
        h = getattr(self, "_hoister", None)
        if h is None or not h.prelude:
            return []
        lines = h.prelude
        h.prelude = []
        return lines

    def prelude_block(self):
        """Drain the pending prelude, indented at the current level.

        For compound-statement headers: call right after generating the
        condition/iterable expression, before emitting the header line.
        """
        return [f"{self._indent()}{ln}" for ln in self.drain_prelude()]

    def emit_stmt(self, stmt):
        """Generate one statement, prefixed by any prelude it hoisted.

        Replaces the per-loop `generate + isinstance-indent` idiom in block
        bodies; behavior is identical when nothing was hoisted.
        """
        stmt_str = self.generate(stmt)
        if not isinstance(stmt, self.SELF_INDENTING_NODES):
            stmt_str = f"{self._indent()}{stmt_str}"
        prelude = self.prelude_block()
        if prelude:
            return "\n".join(prelude + [stmt_str])
        return stmt_str
