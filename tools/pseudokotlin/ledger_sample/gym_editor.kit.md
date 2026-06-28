# UI layout ledger (KIT side) -- gym_editor

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Edit gym]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Save]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Gym name]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Name]  <leaf>   size: wrap(rel)
  - Text[Equipment]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Divider[3]  <leaf>   size: wrap(rel)
  - Column[4]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No equipment added yet.]  <leaf>   size: wrap(rel)  style=empty_title(abs)
  - Spacer[5]  <leaf>   size: wrap(rel)
  - Overlay[6]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)
  - Zone[7]  <leaf>   size: wrap(rel)

  ids:
    gym_editor/Row[0]
    gym_editor/Row[0]/Button[←]
    gym_editor/Row[0]/Column[1]
    gym_editor/Row[0]/Column[1]/Text[Edit gym]
    gym_editor/Row[0]/Button[Save]
    gym_editor/Column[1]
    gym_editor/Column[1]/Text[Gym name]
    gym_editor/Column[1]/TextField[Name]
    gym_editor/Text[Equipment]
    gym_editor/Divider[3]
    gym_editor/Column[4]
    gym_editor/Column[4]/Text[No equipment added yet.]
    gym_editor/Spacer[5]
    gym_editor/Overlay[6]
    gym_editor/Overlay[6]/Button[+]
    gym_editor/Zone[7]

---
## cross-side compare: Compose GymEditorScreen <-> kit gym_editor
- STRUCTURAL leaf match (LCS, dynamic-aware): 7/53 Compose leaves aligned to kit (13%)
- static content matched (by literal): 4
    = Equipment
    = Gym name
    = No equipment added yet.
    = Save
- Compose leaves NOT aligned: 46  ·  kit leaves not aligned: 1
- (raw content-anchor only: Compose-only 24, kit-only 4)
