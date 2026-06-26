# log_62 — IMPLEMENTER REPORT: ledger v1 built (loader + _score hook + 3 seeds). Handoff to review.

Date: 2026-06-26
Type: implementer report (the handoff to review). Implements the design approved in log_61 (rulings:
JSON; defer the whole paths sheet to increment 2; seed exactly the 3 confirmed cases). Protocol log_55:
I did NOT `--snapshot`; the baseline is the reviewer's to ratchet. Nothing here changes any screen.

## What changed (3 files, all under tools/dualgraph — matcher-only, NOT the transpiler)

- **`ledger.json`** (new) — the recorded KT↔PC correspondences. Two sections (`kind_aliases`,
  `instances`), each entry carrying `why` + Kotlin `ref` for eye-audit.
- **`align.py`** — added `_load_ledger()` + `_ledger_score(a,b)`; consulted at the TOP of `_score`
  (`led = _ledger_score(a,b); if led>0: return led`). Heuristic passes unchanged below it. Missing
  ledger file → empty → zero behavior change.
- **`test_ledger.py`** (new) — enforces the no-gaming guards (log_61 req #2). 11 checks, all pass.

The existing `ingest.MappingTable` (KNOWN_CUSTOM/NEEDS_WIDGET, shared with the transpiler) was NOT
touched — confirmed in log_61.

## The 3 ledger entries, with KT↔PC pair evidence (verified via `align.compare`)

```
[kind alias]  KT widget:LinearProgressIndicator .FLAG   <->  PC progress .progress
              ref WFL/.../ui/onboarding/OnboardingScreen.kt:145
              why: Compose Material linear progress bar; PC built it as the `progress` primitive.
                   Crosses the widget->primitive boundary the heuristic can't (align.py:90).

[kind alias]  KT widget:ProgramCard .FLAG [loop] (×2)   <->  PC widget:program_card 'Swap for this program'
                                                              *click->program_editor [loop] (×2)
              ref WFL/.../ui/programs/ProgramsScreen.kt:155  (composable def at :246)
              why: PC renamed the ProgramCard composable to program_card. Flagged on KT because it is
                   not in KNOWN_CUSTOM; recorded here, not in the transpiler-shared table.

[per-instance] KT button 'Add a second path' *click->startAddSecond
               <-> PC widget:button '+ Add a second path' *click->on_add_second [branch]
              ref WFL/.../ui/paths/PathsScreen.kt:123  (handler startAddSecond at :112)
              why: same CTA, same handler (startAddSecond <-> on_add_second). PC prepends a literal '+'
                   (Add-icon approximation); labels differ only cosmetically. The button is already
                   built and wired — this is a RECORDED correspondence, NOT a screen edit (log_61 req #3).
```

## Gate: before → after (full run; no `--snapshot`)

```
BEFORE:  connectivity 216/451 = 48%   (baseline 48%)   OK: no regression
AFTER:   connectivity 220/451 = 49%   (baseline 48%)   OK: no connectivity regression
  + onboarding_screen: matched 8->9   kt_only 34->33   (progress alias)
  + paths_screen:      matched 5->6   kt_only  2->1    (Add-a-second-path)
  + programs_screen:   matched 3->5   kt_only  3->1    (ProgramCard ×2)
```

matched rose by **+4 on exactly the 3 seeded screens, via the recorded links only**; `kt_only` and
`pc_only` fell by the same on those screens; **no screen's matched fell** and no other screen moved.
Improvements present → reviewer may ratchet.

## Guard enforcement (log_61 req #2) — `python3 tools/dualgraph/test_ledger.py`

All 11 checks pass. The load-bearing one:
- a kind alias is **SUPPRESSED when both nodes carry differing literal text** (would pair two distinct
  labeled objects) — verified for both aliases.
- a kind alias fires only when text is compatible (both empty / equal); it is **directional** (a=KT,
  b=PC), so the reversed order does not pair.
- a per-instance entry pairs across the named cosmetic label diff, but **ignores** a node whose label
  doesn't match the record.
- ledger scores (3.5 / 3.0) stay **below** text-exact (4.0), so genuine text matches still win.

## Other verification

- `python3 tools/smoke_screens.py` → **30/30 screens built**. (No screen/lib/kit change; expected
  unaffected — run anyway.) Flutter goldens N/A for the same reason.
- Regenerated `PseudoCoup/uimap/sidebyside.html` → 220/451; the 4 renamed pairs now render GREEN on the
  same row instead of as false "no Kotlin source" / "not built in PC" rows.

## Deferred (per log_61), NOT done here — for increment 2

- **paths `PathSelectionSheet` (1:N).** Read the Kotlin composable, then decide per node whether its
  internals (scrim / note 'Choose what matters…' / section_header 'Mental health focus') correspond to
  PC's — fix by expansion/inline (the `ExecutionContent` mechanism), NOT a 1:N ledger row — or are
  genuine PC additions. Not guessed.
- **onboarding wizard steps.** PC has 2 `wizard_step_scaffold` nodes vs 8 KT `*Step` composables, so
  most of onboarding's 33 remaining kt_only are genuine gaps. Any true step rename needs confirming
  against `OnboardingScreen.kt` first. Not seeded.

## For the reviewer

Pair-inspect the 3 entries against the 3 `ref`s; re-run `connectivity_gate.py` (expect 220/451, no
regression) and `test_ledger.py` (expect all pass). If clean, ratchet the baseline. I have not, and will
not, `--snapshot`. Next increment continues the same loop.

Pointers: `tools/dualgraph/ledger.json`, `align.py` (`_ledger_score` + the `_score` hook at the top),
`test_ledger.py`, log_61 (the approval+rulings), log_60 (design), log_58 (task), log_55 (protocol).
