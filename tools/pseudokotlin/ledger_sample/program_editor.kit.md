# UI layout ledger (KIT side) -- program_editor

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Program details]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Swap]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Text[No program selected.]  <leaf>   size: wrap(rel)  style=section_header(abs)

  ids:
    program_editor/Row[0]
    program_editor/Row[0]/Button[←]
    program_editor/Row[0]/Column[1]
    program_editor/Row[0]/Column[1]/Text[Program details]
    program_editor/Row[0]/Button[Swap]
    program_editor/Text[No program selected.]

---
## cross-side compare: Compose ProgramEditorScreen <-> kit program_editor
- STRUCTURAL leaf match (LCS, dynamic-aware): 4/74 Compose leaves aligned to kit (5%)
- static content matched (by literal): 2
    = Program details
    = Swap
- Compose leaves NOT aligned: 70  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 52, kit-only 2)
