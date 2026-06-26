# log_59 — gym_list_screen gaps closed

Date: 2026-06-26
Type: implementer verification report (Claude conversation, per log_55 kickoff)

## The Gaps
- **Screen**: `gym_list_screen`
- **Gaps** (`connectivity_gate.py gym_list_screen` reported 2 `kt_only`):
  - `text 'No gyms yet. Tap + to add one.'`
  - `button 'Delete gym' *click->?`
- **Blueprint**: `WFL/app/.../ui/gym/GymListScreen.kt` (read in full before editing — both
  gaps are genuinely-absent elements, not matcher false-negatives).

## The Cause
1. **Empty state** (GymListScreen.kt:77-89). The blueprint renders the empty case as a
   `Box(fillMaxSize, contentAlignment = Center)` holding **one** muted `bodyMedium`
   `Text("No gyms yet. Tap + to add one.")`. PseudoCoup instead used the `empty_state()`
   widget, which emits a **bold title** "No gyms yet" + an **invented** body line
   "Tap + to add a gym profile." — copy that does not exist in the blueprint. The matcher
   (two text-bearing nodes only match on identical copy) saw `widget:empty_state 'No gyms
   yet'` vs `text 'No gyms yet. Tap + to add one.'` → no match.
2. **Delete** (GymListScreen.kt:247-262). The blueprint is a real `TextButton(onClick =
   onDelete)` containing a Delete `Icon` + `Text("Delete gym")`. PseudoCoup rendered it as
   a clickable `define_text("🗑 Delete gym", "gym_del")` — a text masquerading as a button
   (wrong kind, and the copy carried an emoji approximation of the decorative icon).

## The Fix (`src/ui/gym_list_screen.py` — reuse only, no domain/VM logic touched)
1. Replaced the `empty_state()` call with the blueprint's actual element: a centered
   `define_box(..., "empty", ...)` + a single `define_text(..., "No gyms yet. Tap + to add
   one.", "empty_body", ...)`. `empty_body` = muted (ON_VAR) centered wrapping line, matching
   the blueprint's `bodyMedium`/`onSurfaceVariant`. Dropped the now-unused `empty_state`
   import.
2. Changed `define_text("🗑 Delete gym", "gym_del")` → `define_button("Delete gym",
   "gym_del")`. `gym_del` = flat DANGER text colour (no background) = the blueprint's
   error-coloured TextButton look. Same zone id (`..._del`), same `on_click → on_delete_click
   → vm.delete` wiring preserved. Label is now exactly "Delete gym" (the blueprint's `Text`);
   the decorative Delete icon was previously approximated by a 🗑 emoji that rendered as a
   tofu box in the test font — removing it both matches the blueprint copy and cleans up the
   glyph artifact.

This is faithfulness, not gaming: in both cases the blueprint *actually uses* the element
type/copy now emitted (a single muted text; a real button), and PseudoCoup previously used a
different shape. Element types and copy were confirmed against the real Kotlin source.

## KT ↔ PC pair evidence (newly matched — same element, not spurious)
```
text   'No gyms yet. Tap + to add one.'          <->  text   'No gyms yet. Tap + to add one.' [branch]
button 'Delete gym' *click->onDelete             <->  button 'Delete gym' *click->on_delete_click [loop]
```

## Verification (NOT snapshotted — baseline ratchet is reviewer-only)
- **Gate**: `+ gym_list_screen: matched 9->11  kt_only 2->0`; full gate `connectivity
  216/451 = 48%`, **OK: no connectivity regression** (no other screen changed, no matched drop).
- **Smoke**: `SMOKE: 30/30 screens built`.
- **Flutter**: `SWEEP: 30/30 screens rendered clean`, `All tests passed!`. Golden
  `sweep_gym_list.png` updated (delete is now a button; 0.35% diff) — visually inspected the
  before/after render to confirm the change is faithful and nothing else moved.
- Committed + pushed `49eb614` on `origin/kit-migration-primitives`. Generated
  `app_flutter/lib/*.dart` is gitignored, so the commit is the `src/` change + the golden.

## Honest caveat (pre-existing — NOT changed by this commit)
The delete row renders **left-aligned**, though the blueprint `Row` is `Arrangement.End`
(right). This is a styling gap in `gym_del_row` (the row is wrap-width rather than
`fillMaxWidth`, so end-gravity has no space to push into). It predates this change, is
identical before/after, and is guarded by the goldens, not by connectivity. Left untouched to
avoid scope creep beyond the two connectivity gaps; flagged here for the record.

## Status
Ready for the reviewer to independently re-run and ratchet. Next queued per log_55:
`paths_screen` (2), `workout_warmup_screen` (2).
