# log_122 — BACKLOG: efficient near-true-reactivity (reconciled redraw) — NOT implemented

Date: 2026-06-28
Type: backlog / tracked future work (so we don't forget). Builds on log_121's reactivity model.

## Status: NOT implemented (confirmed both kits)

On any `State` change (or a bare `invalidate()`), the recompose host is `remount_current()`, which is
`_teardown_current(); _mount(current_screen_id)` — it tears the WHOLE current screen's zones down and
re-runs the screen's `build()` from scratch. Verified identical in:
- `WFL_PseudoCoup/src/ui/app_router.py` (Kivy kit)
- `WFL_PseudoCoup/app_flutter/lib/ui_app_router.dart` (Flutter kit) — which also drives one global
  `revision` ValueNotifier (`_bump()`), so a `ValueListenableBuilder` rebuilds the whole retained tree.

So today: false-reactive, **redraw-everything** — one repaint per event, but it rebuilds the entire
current screen.

## What we want

Efficient near-true-reactivity: on a change, update only the zone(s) that consumed the changed data +
their subtree, not the whole screen. SAFE despite z-order worries because the kit's hosts
(Kivy/Flutter/DOM) are RETAINED-mode — the host compositor owns overlap / z-order / reflow, so a
single-zone update re-composites correctly. ("Redraw the stack above it" is an IMMEDIATE-mode concern;
it does not apply here.)

## Design — two routes, both KIT-ONLY (no screen or `State` changes)

1. **RECONCILE (React/DOM style — the natural fit, do this first).** On recompose, DON'T teardown.
   Re-run `build()` fully (cheap — it only issues `define_*` commands + reads data), and DIFF the
   re-issued tree against the retained one:
   - existing ids stay — the `if zone_id in self._zones: return` (kit.py) / `if (zones.containsKey(id))
     return;` (kit.dart) idempotency guards are ALREADY exactly this (the half-built seed);
   - changed text/content updates in place (`present()` / set text);
   - zones not re-issued this pass get removed.
   Net: `build()` re-runs wholesale (cheap), but only the changed NATIVE widgets are touched. The
   change lives in `remount_current` (stop tearing down) + `define_*`/`present` (update-in-place +
   add a stale-removal pass) in BOTH kits.

2. **SCOPED recompose (Compose style — more faithful, more work).** Track which zones read which
   `State`, and re-run only the affected subtree's build closure. Needs read-dependency tracking +
   `build()` split into independently-runnable pieces.

Start with (1): smaller change, the guards already exist, and the retained zone tree is its substrate.
Full reactivity model + glossary in log_121.

## Note for whoever picks this up

It is a correctness-preserving optimization: the visible result must be identical to today's
teardown+rebuild (which is the reference). Guard it the way log_120 guarded the staleness fix — a test
that mutates state, recomposes, and asserts the tree matches a full-rebuild of the same state, while
checking far fewer native widgets were recreated.
