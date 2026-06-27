# log_67 — Track A1: Kotlin onClick handler resolution (oversight)

Date: 2026-06-26
Type: reviewer-owned oversight increment (log_65 Track A, item 1). Tools only — NO screen
or ledger changes. Baseline unchanged: 220/451 = 49%.

## What this fixes

The side-by-side edge check could not verify ~half the interaction edges: the Kotlin
extractor resolved only `onClick = { method() }` (first body call). Everything else read as
`*click->?`. A sweep across all 30 screens (350 clickable raw calls) found **223 unresolved**:

| form | n | example |
|---|---:|---|
| value-reference `onClick = <name>` | 178 | `onClick = onNavigateBack`, `onClick = viewModel::save` |
| empty `onClick = {}` (no-op) | 9 | decorative `SuggestionChip(onClick = {}, …)` |
| local-state lambda `onClick = { x = … }` | 36 | `{ showMenu = true }`, `{ quantity++ }` |

The 178 value-refs (the dominant case) had the handler name sitting unused in `call.named`;
the 9 empty chips were being mis-marked interactive (false "unresolved" noise); the 36 toggles
are real interactions but to *local UI state*, not a method/nav edge.

## The model (four interaction kinds)

A click handler now resolves to `(clickable, target, htype)`:
- **`ref`** — passed by value (`onNavigateBack`, `viewModel::save` → `save`). Receiver prefix dropped.
- **`call`** — a method/callback invoked in the lambda (`{ vm.save() }` → `save`), skipping focus
  preludes (`focusManager.clearFocus()`) and descending scope wrappers (`launch { … }`).
- **`assign`** — a local UI-state mutation (`{ showMenu = true }` → `showMenu`). Not a cross-object edge.
- **empty `{}`** — a no-op; **not interactive** (no edge).

## Changes (all additive; transpiler behavior unchanged)

- `tools/ingest/ingest.py` — `Call.click_meta` (new slot): per click/tap lambda, `(kind, target)`
  from a new `_classify_lambda` (+ `_callee_tail` / `_first_ifbody_call` / `_first_assign_target`
  helpers, `_SCOPE_VERBS` / `_SKIP_CALLS` sets). Populated only for click/tap-named lambdas.
  Nothing existing reads these fields — the weak transpiler is untouched (and `MappingTable` was
  not edited, per the silo rule).
- `tools/dualgraph/pc_tree.py` — `Node.htype` (new slot, default `None`); PC handlers tagged `ref`.
- `tools/dualgraph/kotlin_tree.py` — `_is_clickable` rewritten to the four-case resolver
  (+ `_clean_ref`); a `_set_click` helper replaces four duplicated click-attach blocks; empty
  `{}` no longer marks a node clickable; nav resolution still runs for `ref`/`call` (not `assign`).
- `tools/dualgraph/build_sidebyside.py` — `edge_status`/`edge_label` gain a `local` status (KT
  toggles local state; PC wires it too → not a disagreement) and treat empty `{}` as a non-edge.

## Results (matched-pair edge statuses, was → now)

| status | before (log_66) | after |
|---|---:|---:|
| ok (wired the same) | 1 | **10** |
| KT-unresolved | 45 | **4** |
| EDGE? mismatch | 17 | 41 |
| local UI state | — | 1 |
| (non-interactive) | — | 164 |

The mismatch count rose because resolution makes the *real* divergences visible instead of
hiding them behind `?`. They split three ways: (a) **name-divergence of the SAME edge** —
`onNavigateToDetail`↔`exercise_detail`, `onNext`↔`gym_editor`, `onSave`↔`on_compute` — these are
exactly what the **handler-name ledger (Track A2)** will reconcile; (b) the 4 genuine unresolved
tail (`section_header_collapsible` etc.); (c) any true disagreements, which A3's gate will key on.
Resolution accuracy fix: focus preludes are skipped, so the calibrate CTA reads `onSave`, not
`clearFocus` (0 `clearFocus` left in the oversight).

## Verification

- `connectivity_gate.py` → 220/451 = 49%, **no regression** (only the 9 empty-chip `clickable`
  flips touch the matcher's `_score`; they cost zero `matched`).
- `test_ledger.py` → all guards pass. `smoke_screens.py` → 30/30. Goldens not implicated (no
  screen files changed). `build_sidebyside.py` regenerated `uimap/sidebyside.html`.

## Next (log_65 Track A)

A2 handler-name ledger (reconcile `onNavigateToDetail`↔`exercise_detail` etc.) → A3 wire
edge-verification into the gate + ratchet an edge baseline → A4 size/position extraction.
