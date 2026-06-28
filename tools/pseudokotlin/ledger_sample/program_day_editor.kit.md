# UI layout ledger (KIT side) -- program_day_editor

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No exercises yet.]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Tap + to add from the library.]  <leaf>   size: wrap(rel)  style=empty_body(abs)
  - Overlay[2]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    program_day_editor/Row[0]
    program_day_editor/Row[0]/Button[←]
    program_day_editor/Row[0]/Column[1]
    program_day_editor/Row[0]/Column[1]/Text[0]
    program_day_editor/Column[1]
    program_day_editor/Column[1]/Text[No exercises yet.]
    program_day_editor/Column[1]/Text[Tap + to add from the library.]
    program_day_editor/Overlay[2]
    program_day_editor/Overlay[2]/Button[+]

---
## cross-side compare: Compose ProgramDayEditorScreen <-> kit program_day_editor
- STRUCTURAL leaf match (LCS, dynamic-aware): 4/101 Compose leaves aligned to kit (3%)
- static content matched (by literal): 0
- Compose leaves NOT aligned: 97  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 27, kit-only 4)
