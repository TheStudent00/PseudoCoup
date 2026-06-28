# UI layout ledger (KIT side) -- exercises

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Exercises]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[+]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Row[1]  <container>   size: wrap(rel)  style=tab_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[All]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Built-in]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Custom]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[3]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Favorites]  <leaf>   size: wrap(rel)  style=tab_off(abs)
  - Row[2]  <container>   size: wrap(rel)  style=search_field(abs)
    - Text[⌕]  <leaf>   size: wrap(rel)  style=search_glyph(abs)
    - Text[Search exercises…]  <leaf>   size: weight(1.0)(rel)  style=search_ph(abs)
  - Column[3]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No exercises found.]  <leaf>   size: wrap(rel)  style=empty_title(abs)

  ids:
    exercises/Row[0]
    exercises/Row[0]/Button[←]
    exercises/Row[0]/Column[1]
    exercises/Row[0]/Column[1]/Text[Exercises]
    exercises/Row[0]/Button[+]
    exercises/Row[1]
    exercises/Row[1]/Column[0]
    exercises/Row[1]/Column[0]/Button[All]
    exercises/Row[1]/Column[1]
    exercises/Row[1]/Column[1]/Button[Built-in]
    exercises/Row[1]/Column[2]
    exercises/Row[1]/Column[2]/Button[Custom]
    exercises/Row[1]/Column[3]
    exercises/Row[1]/Column[3]/Button[Favorites]
    exercises/Row[2]
    exercises/Row[2]/Text[⌕]
    exercises/Row[2]/Text[Search exercises…]
    exercises/Column[3]
    exercises/Column[3]/Text[No exercises found.]

---
## cross-side compare: Compose ExercisesScreen <-> kit exercises
- STRUCTURAL leaf match (LCS, dynamic-aware): 10/18 Compose leaves aligned to kit (55%)
- static content matched (by literal): 3
    = Exercises
    = No exercises found.
    = Search exercises…
- Compose leaves NOT aligned: 8  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 8, kit-only 7)
