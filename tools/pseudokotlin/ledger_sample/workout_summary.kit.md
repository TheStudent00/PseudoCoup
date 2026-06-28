# UI layout ledger (KIT side) -- workout_summary

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Workout complete]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Done]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No session]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[No session data found.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    workout_summary/Row[0]
    workout_summary/Row[0]/Button[←]
    workout_summary/Row[0]/Column[1]
    workout_summary/Row[0]/Column[1]/Text[Workout complete]
    workout_summary/Row[0]/Button[Done]
    workout_summary/Column[1]
    workout_summary/Column[1]/Text[No session]
    workout_summary/Column[1]/Text[No session data found.]

---
## cross-side compare: Compose WorkoutSummaryScreen <-> kit workout_summary
- matched (by content anchor): 2
    = Done
    = Workout complete
- Compose-only (in design, MISSING from kit): 17
    KT  ${summary.completedSets} sets
    KT  Duration
    KT  Edit workout
    KT  Exercise summary
    KT  Exercises
    KT  New estimated 1RM|New $it-rep …
    KT  Personal records
    KT  Volume
    KT  formatVolume(uiState.totalVolu…
    KT  formatWeight(pr.weightKg, unit)
    KT  label
    KT  pr.exerciseName
    KT  summary.exerciseName
    KT  topStr
    KT  uiState.exerciseSummaries.size…
    KT  value
    KT  —
- kit-only (ADDED by the wrapping): 3
    PY  No session
    PY  No session data found.
    PY  ←
