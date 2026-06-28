# UI layout ledger (KIT side) -- progress

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=tab_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Analytics]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Bests]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[History]  <leaf>   size: wrap(rel)  style=tab_off(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No workouts yet]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Completed sessions and cardio …]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    progress/Row[0]
    progress/Row[0]/Column[0]
    progress/Row[0]/Column[0]/Button[Analytics]
    progress/Row[0]/Column[1]
    progress/Row[0]/Column[1]/Button[Bests]
    progress/Row[0]/Column[2]
    progress/Row[0]/Column[2]/Button[History]
    progress/Column[1]
    progress/Column[1]/Text[No workouts yet]
    progress/Column[1]/Text[Completed sessions and cardio …]

---
## cross-side compare: Compose ProgressScreen <-> kit progress
- matched (by content anchor): 2
    = Completed sessions and cardio …
    = No workouts yet
- Compose-only (in design, MISSING from kit): 61
    KT  $it bpm
    KT  ${cardio.durationMinutes} min
    KT  ${session.setCount} sets
    KT  %.1f km
    KT  1 PR|${session.prCount} PRs
    KT  Ad-hoc Workout
    KT  Best
    KT  Cardio
    KT  Exercise
    KT  Foundational total · best e1RM…
    KT  How you feel after training
    KT  Keep setting PRs on your main …
    KT  Last 30 days
    KT  Last 7 days
    KT  Lifting and cardio combined.
    KT  Log a few sets to start tracki…
    KT  Log a win
    KT  Log your first workout to see …
    KT  More than the numbers — the re…
    KT  No bests yet
- kit-only (ADDED by the wrapping): 3
    PY  Analytics
    PY  Bests
    PY  History
