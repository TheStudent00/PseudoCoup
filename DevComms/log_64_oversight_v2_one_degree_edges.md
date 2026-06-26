# log_64 — oversight v2: one-degree separations now tracked (structural containment + edge checks)

Date: 2026-06-26
Type: reviewer-built oversight enhancement (the user asked to enhance the oversight BEFORE any more
ledger/screen work). Reviewer infrastructure, so I built it directly (the implementer shouldn't build
its own oversight). `tools/dualgraph/build_sidebyside.py` → `PseudoCoup/uimap/sidebyside.html`.

## What v1 did vs what was missing (the user's two observations — both correct)

- v1 showed object↔object mappings as a FLAT list. The AST already carried the one-degree edges
  (`Node.children` = containment; `Node.handler`/`nav` = interaction) but `align.flatten()` dropped the
  structural ones for display, and sizes/positions were never captured at all.

## What v2 adds

1. **Structural one-degree edges — shown.** The Kotlin blueprint renders as an INDENTED TREE; the
   indentation IS the containment graph (which object holds which). No longer a flat inventory.
2. **Interaction one-degree edges — shown AND checked.** For every matched pair the source→target edge
   (click `handler` / `nav`) is compared:
   - `⇒ name` (green): KT and PC wired to the same target.
   - `⇒ EDGE?` (red): KT and PC wired to DIFFERENT targets.
   - `(KT target unresolved)` (grey): KT is interactive but the extractor didn't resolve its handler —
     a `kotlin_tree` limitation, **separated out so it's not counted as a false disagreement**.

## Findings across the fleet (the honest numbers)

```
edge OK (agree):                    1
real edge-mismatches (both resolved, differ):  17   <- the spotlight
KT-unresolved (extractor gap, can't verify):   45
```

The 17 real mismatches are worth a look — genuinely useful oversight. Samples:
- `today` button: KT→`resumeSession` vs PC→`on_start_workout`  (possible real wiring difference)
- `exercises` list_row: KT→`onNavigateToDetail` vs PC→`on_item_click`  (same target, names diverge)
- `programs` ProgramCard: KT→`None` vs PC→`on_item_click`  (KT side didn't resolve the card's onClick)

## Honest limits (so this isn't oversold)

- **Edge-verification is a SPOTLIGHT, not a gate** — it is NOT wired into `connectivity_gate.py`.
  Two noise sources keep it from gating yet:
  1. **45 KT-unresolved.** `kotlin_tree` renders most onClick targets as `?`/None. Improving handler
     resolution there would unlock most of the edge checks.
  2. **Handler-name renames.** KT and PC handler names diverge the same way object names did
     (`onNavigateToDetail` vs `on_item_click`) — so some of the 17 are rename false-positives, not real
     differences. A clean gate would need a handler-name ledger (the edge analogue of log_62's object
     ledger).
- **Sizes/positions: still NOT tracked.** Confirmed: `pc_tree` captures zero layout (no
  direction/weight/size); the Node schema has no width/height/x/y. Adding them is a separate, bigger
  job — new extraction in BOTH `pc_tree` (kit zone params) and `kotlin_tree` (Compose `Modifier`), and
  it overlaps what the goldens already guard. Flagged for the user's decision; NOT done here.

## Status / next

Oversight now tracks both one-degree edge kinds (structural shown; interaction shown+checked). The
side-by-side regenerated at 220/451 with the tree + edge view. Suggested follow-ups, user's call:
(a) improve `kotlin_tree` handler resolution (cuts the 45 unresolved), (b) handler-name ledger to clean
the 17 down to real differences, (c) size/position extraction if connectivity should own layout. Then
resume the ledger/screen loop.

Pointers: `tools/dualgraph/build_sidebyside.py` (v2), `PseudoCoup/uimap/sidebyside.html`,
`pc_tree.py` (Node schema — no layout), log_63 (the task + status table), log_62 (object ledger).
