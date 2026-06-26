# log_58 — TASK (Gemini): build the Kotlin⟷PseudoCoup correspondence LEDGER

Date: 2026-06-26
Type: task. Operating rules are in log_55 (siloed, never `--snapshot`, ongoing, no sleight-of-hand,
per-change loop). This task is the oversight foundation: replace INFERRED object matching with a
RECORDED Kotlin↔PC correspondence, so the side-by-side view is exact by construction, not guessed.

## Why (the problem, with evidence)

The side-by-side oversight (`PseudoCoup/uimap/sidebyside.html`) shows "no Kotlin source" (pc_only) rows
that are NOT actually sourceless — they are matcher false-negatives. The forward hand-port RENAMED and
genericized objects and kept no ledger, so `align.py` reverse-engineers the mapping heuristically and
fails exactly where names diverged. Evidence (`onboarding_screen`), each pc_only mirrors a kt_only:

```
PC (shows "no Kotlin source")            its real Kotlin source (shows "no PC match")
progress                            <->  widget:LinearProgressIndicator      (renamed)
widget:wizard_step_scaffold 'Choose…'<-> widget:PathSelectionStep / WelcomeStep (genericized+renamed)
```

Today's button fix (`widget:button` ↔ `button .filled`) was the same class, patched directly in the
matcher. The ledger GENERALIZES that: stop hand-patching the matcher per-rename; record the mapping.

## Goal

A human-auditable LEDGER that records each PC↔Kotlin object correspondence. `align.py` consults it for
EXACT pairing first; the existing heuristics remain as fallback. After this, a "no Kotlin source" row
means a genuine PC-only object, and the oversight view is trustworthy by construction.

## Requirements

1. **Explicit + auditable.** A readable file (e.g. `tools/dualgraph/ledger.*`) a human can scan top to
   bottom; each entry is one defensible "PC X = Kotlin Y" claim.
2. **Two granularities** (the data needs both):
   - **kind aliases** for renamed primitives/widgets: `progress` ↔ `LinearProgressIndicator`.
   - **per-instance** mappings for genericized components disambiguated by label/content:
     `wizard_step_scaffold 'Choose your first path'` ↔ `PathSelectionStep`.
3. **Matcher integration:** consult the ledger for exact pairing BEFORE the heuristic passes; do not
   remove existing matching.
4. **Seed the existing screens:** reconcile the mirror-pairs — every pc_only that corresponds to a
   kt_only is a recorded rename. Start with the unambiguous ones (`progress`, the wizard steps, any
   other renamed primitive/widget across the 30 screens).
5. **Propose the design first** (a short plan: file format, how the matcher reads it, how you'll seed
   it). Get it reviewed, THEN implement. Do not bulk-implement before the design is approved.

## Verification I will enforce — do NOT game it

- **Every ledger entry is a REAL correspondence.** I pair-inspect each one: the PC object and the
  Kotlin object it links must be the SAME element. A loose/wrong entry is a false match → rejected.
- **No false matches, no matched-loss regressions.** Full per-screen gate diff vs the committed
  baseline; `matched` may rise ONLY via genuine ledger links, and must not fall on any screen.
- **No over-aliasing.** Mapping unrelated kinds to shrink pc_only is gaming, and it is terminal. The
  ledger shrinks pc_only/kt_only ONLY by recording true renames.
- **Auditable by eye.** I must be able to read the ledger and confirm each entry against the two
  codebases without running anything.
- Protocol (log_55): you never `--snapshot` or edit the baseline; ongoing (no "done"/success
  assessment); hand each change to review WITH the ledger entries + the pair evidence.
- **Put your report in a DevComms log** (`PseudoCoup/DevComms/log_<N>_ledger_*.md`): the design,
  each ledger entry with its KT↔PC justification, and the gate before/after. The log is the handoff.

## Definition of "working"

- `pc_only` and `kt_only` drop only by verified recorded correspondences.
- The ledger is readable and every entry checks out by eye.
- Regenerating `build_sidebyside.py`, the renamed pairs are now GREEN (mapped on the same row); the
  remaining red rows are genuine gaps, the remaining blue rows are genuine PC additions — and that
  distinction is now TRUE, not inferred.

Pointers: `tools/dualgraph/align.py`, `tools/dualgraph/build_sidebyside.py`,
`PseudoCoup/uimap/sidebyside.html` (the view this makes trustworthy), log_55 (protocol),
today's button fix in `align.py:_score` (the same false-negative class the ledger generalizes).
