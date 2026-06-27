# log_68 — Track A2: handler-name ledger (edge analogue of the object ledger)

Date: 2026-06-26
Type: reviewer-owned oversight increment (log_65 Track A, item 2). Tools + ledger data
only — NO screen changes. Baseline unchanged: 220/451 = 49%.

## Why

After A1 (log_67) resolved the interaction targets, 41 matched pairs read as `EDGE?` —
but most are not disagreements, they are **the same edge under diverging names**: a Kotlin
callback (`onNavigateToGymList`) vs the PC nav/handler it resolves to (`gym_list`). The
matcher's name-normalizer (`_enorm`, which strips on/handle + click/tap/pressed) already
collapses cosmetic diffs (`onSetActive`↔`on_set_active`); it cannot collapse a SEMANTIC
rename. The handler ledger records those confirmed correspondences so they stop reading as
defects, leaving only GENUINE source→target differences.

## Mechanism (the edge analogue of `kind_aliases`)

- `ledger.json` gains a `handler_aliases` array. Each entry: `{slug, kt, pc, why, ref}`.
- `align.py`: `_load_handler_aliases()` + `ledger_edge_match(slug, kt, pc)` — true iff a
  recorded alias links the matched pair's interaction targets (`kt.handler|nav` ↔
  `pc.handler|nav`). **Scoped by slug**, because a callback can mean different things on
  different screens (proof: `onModeSelect` at `OnboardingScreen.kt:756` matches PC
  `on_path_click` under `onboarding_screen` but a *different* PC object under
  `calibrate_screen`, which shares the file).
- `build_sidebyside.edge_status(kt, pc, slug)`: after the `_enorm` name check fails, consult
  the ledger → `ok`; else `warn`. It only ever SOFTENS a matched pair's verdict — it cannot
  create an object match, so the worst a bad entry could do is MASK one real edge
  disagreement (not invent a node match). Hence: every entry verified against the Kotlin
  source `ref`.
- `test_ledger.py`: handler-alias guards — required non-empty fields; fires on its own slug;
  does NOT fire on another slug (scoping); does NOT fire on a non-matching target.

## Entries (15, each pair-inspected against the cited Kotlin line)

Navigation renames (KT callback → PC nav destination): `you_screen`
onNavigateToGymList→gym_list, onNavigateToExercises→exercises, onNavigateToReportBug→
report_bug, onNavigateToDebugPanel→debug_panel; `my_program_screen` onNavigateToPrograms→
programs, onBrowse→programs; `exercises_screen` onNavigateToDetail→exercise_detail;
`gym_list_screen` onEdit→gym_editor.
Action renames: `workout_cooldown_screen` onWrapUp→on_done; `log_cardio_screen` onSave→on_log;
`calibrate_screen` onSave→on_compute.
Intra-screen interaction renames: `update_program_screen` selectTarget→on_muscle_click,
selectInjuryTarget→on_muscle_click, toggleExercise→on_exsel_click; `onboarding_screen`
onModeSelect→on_path_click.

## Deliberately NOT recorded (left as honest `warn` — not masked)

- **Wrong object-match, not a rename:** `debug_panel` `resetTime`↔`on_seed` ("Reset to real
  time" button matched PC's seed button) — the edge check correctly surfaces a questionable
  *object* pairing; aliasing it would hide that.
- **KT target wired INSIDE the composable** (no call-site onClick to resolve): ProgramCard,
  wins_home_card, several `you_screen` settings rows/section headers — these show `KT->?`;
  there is no KT name to alias. Resolving them needs cross-file composable inspection (out of
  scope; candidate for a later A1 extension).
- **Genuine one-half edges:** `you_screen` collapsible section headers are interactive in KT
  (expand/collapse) but plain headers in PC — a real simplification to flag, not a rename.
- **Conservatively skipped (semantic uncertainty):** gym_create_wizard onNext→gym_editor,
  today resumeSession→workout_warmup, update_program setAvoidExercise→on_open_avoid_replace.

## Results

| | A1 (log_67) | A2 (now) |
|---|---:|---:|
| ok (edge agrees) | 10 | **26** |
| EDGE? mismatch | 41 | **25** |
| KT-unresolved | 4 | 4 |
| local UI state | 1 | 1 |

15 entries resolved 16 matched-pair mismatches (onNavigateToDetail covers two `exercises`
list rows). The 25 remaining are the genuine cases above.

## Verification

- `test_ledger.py` → all guards pass (2 kind_aliases, 1 instance, **15 handler_aliases**).
- `connectivity_gate.py` → 220/451, **no regression** (handler ledger touches only edge
  display, not the matcher). `smoke_screens.py` → 30/30 (unchanged; no screen edits).
- `build_sidebyside.py` regenerated `uimap/sidebyside.html` (edge-mismatches now 25).

## Next

A3: wire edge-verification into `connectivity_gate.py` so a matched object wired to a
DIFFERENT target fails the gate; ratchet an edge baseline. Then A4 size/position.
