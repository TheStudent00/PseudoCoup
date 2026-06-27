# log_69 — Track A3: edge verification wired into the gate + edge baseline ratcheted

Date: 2026-06-26
Type: reviewer-owned oversight increment (log_65 Track A, item 3). Tools + baseline only —
NO screen changes. Connectivity unchanged: 220/451 = 49%.

## What this does

Turns the gate's guarantee from **"the same object is present"** into **"the same object is
wired the same way."** After A1 resolved interaction targets (log_67) and A2 reconciled the
same-edge renames (log_68), a residual `warn` means a matched object is genuinely wired to a
DIFFERENT target on the two sides (or one side is inert). The gate now treats a screen GAINING
such mismatches as a regression — exactly like gaining a `kt_only` gap.

## Changes

- **`align.py`** — `edge_status` + `_enorm` MOVED here from `build_sidebyside` so the gate and
  the human view share ONE definition of "wired the same way". New `edge_mismatches(slug, res)`
  returns the matched pairs whose edge status is `warn`.
- **`build_sidebyside.py`** — now imports `edge_status` from `align` (keeps only `edge_label`,
  the HTML rendering). No behavior change to the view.
- **`connectivity_gate.py`** — `measure()` records per-screen `edge_mismatch`; `totals()` sums
  it; the regression check FAILS a screen whose `edge_mismatch` rose; improvements include
  edge drops; `<slug>` now also lists the mismatched pairs; `--snapshot` writes the edge field.
  A screen whose baseline has NO `edge_mismatch` key is ungated on edges until ratcheted (safe
  rollout — no surprise failures on the old baseline).
- **`connectivity_baseline.json`** — RATCHETED (reviewer token `CONNECTIVITY_RATCHET=1`): the
  edge dimension locked in at its current clean state. `matched`/`kt_only`/`pc_only` are
  byte-for-byte unchanged; only `edge_mismatch` was added per screen. Total = **25**.

## Verification

- Ratchet: `snapshot written (30 screens): connectivity 220/451 = 49%  edge-mismatches 25`.
- Gate vs new baseline → **OK** (exit 0).
- **Regression sanity (proves the edge gate bites):** artificially lowering one screen's
  baseline `edge_mismatch` by 1 → gate prints `CONNECTIVITY/EDGE REGRESSION … edge? 6->7` and
  **exits 1**; restored baseline → exit 0. `--snapshot` without the token → still REFUSED
  (silo lock intact).
- `smoke_screens.py` → 30/30. `test_ledger.py` → all guards pass. `build_sidebyside.py` →
  unchanged output (25 mismatches), `uimap/sidebyside.html` already current.

## What the 25 baselined mismatches are (signal for the implementer, NOT masked)

The gate now records these as the ceiling to drive DOWN. Notable buckets the per-screen view
(`connectivity_gate.py <slug>`) exposes:
- **PC interaction not wired** — `you_screen` settings rows (Display name, Body weight, Effort
  scale, Weight unit) and collapsible section headers are tappable in the Kotlin blueprint but
  inert in PC. Real edge gaps to close.
- **KT target wired inside a composable** (`KT->?`): ProgramCard, wins_home_card — unresolvable
  at the call site (future A1 extension, cross-file).
- **Questionable object match** — `debug_panel` `resetTime`↔`on_seed` (the edge check flags a
  pairing that is likely wrong, not a rename).
- **Conservatively un-aliased** renames (onNext→gym_editor, resumeSession→workout_warmup,
  setAvoidExercise→on_open_avoid_replace) — left as `warn` pending firmer verification.

## Next

A4: size/position extraction into the Node schema + show in the side-by-side. Decision to make
with the reviewer (me): gate it or keep it informational — leaning informational (the Flutter
goldens already guard visual layout; a layout dimension on the hard gate risks false
regressions the goldens catch better).
