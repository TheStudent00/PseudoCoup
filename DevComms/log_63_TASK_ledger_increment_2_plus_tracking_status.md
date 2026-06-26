# log_63 — TASK: ledger increment 2 (renames + the paths sheet) + STATUS NOTE on edge/size tracking

Date: 2026-06-26
Type: task + status note. Operating rules: log_55 (siloed, never `--snapshot`, ongoing, per-change
loop, no sleight-of-hand). Report this increment in a DevComms log (`log_<N>_ledger_v2.md`). Reviewer
verifies every entry against the Kotlin source + the full gate before ratcheting. Baseline now 220/451.

## TASK — continue the ledger, one verified increment

1. **Sweep the fleet for kind-alias renames** the same class as v1 (`LinearProgressIndicator`↔`progress`,
   `ProgramCard`↔`program_card`). The strongest signal is a kt_only that MIRRORS a pc_only (same element,
   different name). Likely candidates seen in scouts: `CircularProgressIndicator`↔`progress` (appears on
   gym_editor / session_detail / workout_summary), other `*Card`/`*Row` composables ↔ PC `*_card`/`*_row`
   widgets. **Record ONLY after confirming each against the Kotlin source** (the `ref` file:line is
   mandatory and I read every one).
2. **The paths `PathSelectionSheet` (deferred from v1).** Read the Kotlin composable first. Then decide
   per internal node (`scrim` / `note 'Choose what matters…'` / `section_header 'Mental health focus'`)
   whether it corresponds to PC's — if so, fix by **expansion/inline** (the `ExecutionContent`/`_inline_ok`
   mechanism in `kotlin_tree.py`, so the KT sheet's internals appear and match PC's by text), NOT a 1:N
   ledger row. If a PC node is a genuine addition, leave it. Don't guess; show the Kotlin evidence.
3. Same guards as v1 (kind-alias suppressed on differing literal text; instances name both labels). Run
   `test_ledger.py` + the full gate; `matched` rises only via real links, falls on no screen. Hand off as
   a log with each entry's `ref` + gate before/after. Never `--snapshot`.

## STATUS NOTE — what the system tracks today (answering the oversight questions)

The user asked whether the tracking covers **one-degree separations (source object → target objects)**
and **sizes/positions**. Verified status:

| what | tracked? | where |
|---|---|---|
| object ↔ object mapping (the ledger's job) | yes | matched pairs + ledger.json |
| **interaction edges** (object → its click `handler` / `nav` target) | **yes, and shown** | `Node.handler`/`Node.nav`, rendered inline as `*click->…` in the side-by-side |
| **structural one-degree edges** (object → the objects it CONTAINS) | **captured, but dropped** | `Node.children` exists in the AST, but `align.flatten(normalize(...))` flattens it before matching, so the side-by-side shows a FLAT list, not the containment graph |
| **sizes** (width/height) | **no** | not in the Node schema at all |
| **positions** (x/y, relative/absolute, padding/weight/alignment) | **no** | only a `role` STYLE token (`btn_filled`, `card`); delegated to the goldens, not connectivity |

So: interaction one-degree edges are visible and auditable; structural one-degree edges are in the AST
but flattened away; sizes/positions are not captured anywhere on the connectivity axis (the goldens are
the only thing guarding visual layout).

### If the user wants these in the oversight, they are real additions (a separate task, not this one):
- **Structural one-degree edges:** render the side-by-side as the *tree* (don't flatten for display),
  or add a per-node "contains: [child kinds]" column, so containment is visible. The data already exists
  (`Node.children`); it's a display/verification change, low risk.
- **Edge verification (not just display):** make the gate FAIL when a matched pair's `handler`/`nav`
  targets disagree (KT button → `onDelete` vs PC button → something-else). Today they're shown, not
  enforced. This turns "same object present" into "same object wired the same way."
- **Sizes/positions:** larger — `pc_tree`/`kotlin_tree` would have to extract layout params (the kit's
  zone weights/direction; Compose `Modifier` size/arrangement) into the Node, and the view would show
  them. This overlaps what the goldens already guard; worth deciding whether connectivity should own it.

These are flagged for the user's decision; this increment does NOT do them.

Pointers: `tools/dualgraph/pc_tree.py` (Node schema, line ~64), `align.py` (`flatten`/`_desc`),
`build_sidebyside.py` (the flat render), `kotlin_tree.py` (`_inline_ok` for the sheet), log_62 (ledger v1).
