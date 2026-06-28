# UI layout ledger (KIT side) -- program_editor

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Program details]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Swap]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Text[No program selected.]  <leaf>   size: wrap(rel)  style=section_header(abs)

---
## cross-side compare: Compose ProgramEditorScreen <-> kit program_editor
- distinct widget signatures matched: 3/31 = 9%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
