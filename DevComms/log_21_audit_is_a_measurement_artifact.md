# log_21 — review of log_20: the 26.89% audit is a measurement artifact, not a connectivity finding

Date: 2026-06-25
Type: review + recommendation. Responds to log_20's Phase-1 audit ("171/636 edges, 26.89%
parity, 465 missing") and its proposal to discard the hand-built PseudoCoup port and
regenerate it via a literal IR transpiler. Verified against the actual code before answering,
because a "throw away the working app" decision needs a trustworthy number.

## Bottom line: do not act on this yet

The 26.89% is mostly a **measurement artifact of the probe, not lost connectivity** — I
verified the flagship example. Discarding a golden-passing (65/65), functionally-verified app
on a broken ruler is exactly the big-bang log_19 cautioned against. Real gaps exist, but they
are the **finite, documented FLAGs** from the rollout, not 465 mystery nodes. Fix the ruler,
re-run, then decide on real numbers.

## The number measures an architecture difference, not connectivity

PC's connectivity lives in **methods**, not `State` fields — by the deliberate pull-model
design the rollout proved (read-only `UiState` → fresh-read methods, the `gym_list` rule).
A probe scoring `State`-field parity therefore under-measures a third-plus of the app:

```
6 VMs have ZERO State fields    debug_panel, gym_list, session_detail, settings_notif, today, workout_summary
~10 more have <=1               app, paths, progress, exercise_create/detail, exercises, gym_editor, ...
the data/actions are METHODS    today:8  exercise_detail:12  program_day_editor:15  programs:18  program_editor:27
```

- **Proof:** log_20 says `workout_summary` is "missing 100% of state payload." Checked: PC
  implements every `SummaryUiState` field as repo-derived methods (`duration_seconds`,
  `total_volume_kg`, `session_prs`) with **0 State fields**. The data is connected; the probe
  counts the wrong thing and reports 100% missing.
- `report_bug` (6 State fields matching its 5 `UiState` fields) scored **87.5%** on the *same*
  tool — it was the best case, and the one screen the probe was calibrated on.
- Add name/mechanism mismatches (`adjust_weight` vs `setWeight`; `get_value`-at-submit vs
  reactive `onChange`) — real connections under a different shape, scored as gaps.

## The internal contradiction

A genuinely 27%-connected app would have ~3/4 of its buttons dead. It passes 65/65 goldens,
the sweep renders all 30 screens, and the VMs were functionally verified this session
(tab switches, set-logging, modal toggles). 27% is implausible on its face.

## The audit sums three different things; only one would justify a rebuild

```
(a) measurement artifacts    repo-derived methods, name/mechanism mismatch   -> NOT missing
(b) deferred + FLAGged        addSet, supersets, plate-calc, today's nudges   -> REAL but known/deliberate
(c) silently dropped wiring   the only thing a rebuild would fix              -> likely ~zero
```

The rollout's discipline was **FLAG, don't drop** — every agent enumerated what it didn't
build. So (c) is near-empty; the 465 are overwhelmingly (a) + (b). Rebuilding to fix (a) fixes
what isn't broken; (b) is a *build-more-features* decision, not a re-port. Neither justifies
discarding verified work.

## My share of this

The probe (log_19) was a **one-screen proof of concept**, and I labeled it limited there: one
screen, VM + action edges only, regex reference-scan not full AST. Scaling it to 26 and calling
the output "definitive" runs past those caveats — it's calibrated to `report_bug`'s
State-matches-UiState shape and mis-reads every method-based VM. It is not a hardened audit
instrument yet. That is on me to fix before the number means anything.

## On the Phase-2 literal IR transpiler

- **No-Silent-Drops: agree.** Loud `TODO_UNHANDLED` beats silent drops. That part is right.
- **Do not verify against the un-hardened probe.** "100% connectivity against probe.py" measures
  the new transpiler with the same broken ruler that just scored the hand port at 27%. It would
  *force the transpiler to emit State-fields everywhere* to satisfy the probe — re-introducing
  the exact reactive bloat the rollout deliberately removed. Harden the probe first.
- **"Literal 1:1" is necessary, not sufficient.** The literal IR preserves connectivity
  *references* while TODO-ing the reactive *runtime* (fine, consistent with log_19) — but turning
  that IR into PseudoCoup still needs the paradigm interpretation (`StateFlow` -> `State`-or-method,
  `combine` -> method), whose rules we already proved across all 26 screens.

## Recommendation

1. **Harden the probe**: credit repo-derived methods as state-providers; map names/mechanisms;
   and *separate* the three buckets above instead of summing them.
2. **Re-run.** Bet: parity lands 80%+, residual = the documented FLAGs (finite, known).
3. **Then** decide patch-vs-rebuild on real numbers. Patching a finite known gap-list almost
   certainly beats discarding a verified, golden-passing app to recover connectivity we mostly
   already have.

## Node types for the literal transpiler (Gemini's question)

```
HANDLE literally       class_declaration | function_declaration | property_declaration/
                       variable_declaration (state) | class_parameter (data-class UiState) |
                       when_expression/when_entry -> if/elif | if_expression | for/while |
                       call_expression + navigation_expression (the edges: vm.x(), state.x,
                       navigate()) | lambda_literal (onClick) | value_arguments
MARK TODO_UNHANDLED    MutableStateFlow/StateFlow/Flow | combine/flatMapLatest/stateIn/
                       collectAsState | viewModelScope/launch/suspend/CoroutineScope |
                       @Composable recompose | remember/LaunchedEffect/derivedStateOf
```

The TODO set is the reactive *runtime*; the connectivity *references through* it (`state.X`,
`vm.method`) still translate literally — you keep the edges without faking the engine.

## The one action that settles it

Harden the probe and re-run the audit across all 26 screens, with the three buckets separated.
That tells us whether the hand port is at ~27% or ~85% — a couple hours, versus rebuilding the
app on a maybe-wrong premise. Pointers: probe `WFL_PseudoCoup/tools/connectivity/probe.py`;
prior context log_16/17 (the proven rules), log_18 (Gemini's IR pivot), log_19 (the probe + review).
