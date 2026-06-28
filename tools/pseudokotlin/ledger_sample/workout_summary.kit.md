# UI layout ledger (KIT side) -- workout_summary

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Workout complete]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Done]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No session]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[No session data found.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

---
## cross-side compare: Compose WorkoutSummaryScreen <-> kit workout_summary
- distinct widget signatures matched: 3/9 = 33%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
