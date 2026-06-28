# UI layout ledger (KIT side) -- workout_execution

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Workout]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Finish]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No exercises]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[This session has no exercises.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

---
## cross-side compare: Compose WorkoutExecutionScreen <-> kit workout_execution
- distinct widget signatures matched: 2/66 = 3%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
