# UI layout ledger (KIT side) -- workout_execution

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Finish]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No exercises]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[This session has no exercises.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    workout_execution/Row[0]
    workout_execution/Row[0]/Button[←]
    workout_execution/Row[0]/Column[1]
    workout_execution/Row[0]/Column[1]/Text[0]
    workout_execution/Row[0]/Button[Finish]
    workout_execution/Column[1]
    workout_execution/Column[1]/Text[No exercises]
    workout_execution/Column[1]/Text[This session has no exercises.]

---
## cross-side compare: Compose WorkoutExecutionScreen <-> kit workout_execution
- matched (by content anchor): 1
    = Finish
- Compose-only (in design, MISSING from kit): 119
    KT   Superset $groupLabel
    KT   · 
    KT  $setNumber${'a' + entry.entryI…
    KT  ${DEFAULT_HOLD_SECONDS}s$perSi…
    KT  ${displayTarget.fmt()} $unitLa…
    KT  ${formatWeightField(uiState.pe…
    KT  ${item.completedSetsCount} set…
    KT  ${loggedHold.durationSeconds ?…
    KT  ${plan.pctOfWorking}%
    KT  ${row.count} × ${row.weight.fm…
    KT  ${uiState.pendingHoldSeconds}s…
    KT  ${warmupPct ?: 0}%|?
    KT  (${(row.count * row.weight).fm…
    KT  +
    KT  +${|.format(remainder)} $unitL…
    KT  +30s
    KT  Add exercise
    KT  Add set
    KT  BAR
    KT  Back
- kit-only (ADDED by the wrapping): 3
    PY  No exercises
    PY  This session has no exercises.
    PY  ←
