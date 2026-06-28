# UI layout ledger (KIT side) -- gym_create_wizard

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Add new gym]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)
    - Text[What equipment do you have?]  <leaf>   size: wrap(rel)  style=wiz_title(abs)
    - Text[Suggested equipment is pre-che…]  <leaf>   size: wrap(rel)  style=note(abs)
    - Column[2]  <container>   size: wrap(rel)  style=labeled_field(abs)
      - Text[Search all equipment]  <leaf>   size: wrap(rel)  style=field_label(abs)
      - TextField[1]  <leaf>   size: wrap(rel)
    - Row[3]  <container>   size: wrap(rel)  style=equip_chip_on(abs)
      - Text[✓]  <leaf>   size: wrap(rel)  style=equip_check(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Bodyweight]  <leaf>   size: wrap(rel)  style=equip_label_on(abs)
        - Text[Always included]  <leaf>   size: wrap(rel)  style=equip_locked(abs)
    - Row[4]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Dumbbell]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[5]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Barbell]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[6]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Kettlebell]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[7]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Bench]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[8]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Squat Rack]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[9]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Pull Up Bar]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[10]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Resistance Band]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Row[11]  <container>   size: wrap(rel)  style=equip_chip(abs)
      - Column[0]  <container>   size: weight(1.0)(rel)  style=equip_chip_col(abs)
        - Text[Cable Machine]  <leaf>   size: wrap(rel)  style=equip_label(abs)
    - Text[1 item selected]  <leaf>   size: wrap(rel)  style=equip_locked(abs)
    - Button[Done selecting]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Zone[2]  <leaf>   size: wrap(rel)

  ids:
    gym_create_wizard/Row[0]
    gym_create_wizard/Row[0]/Button[←]
    gym_create_wizard/Row[0]/Column[1]
    gym_create_wizard/Row[0]/Column[1]/Text[Add new gym]
    gym_create_wizard/Column[1]
    gym_create_wizard/Column[1]/Text[What equipment do you have?]
    gym_create_wizard/Column[1]/Text[Suggested equipment is pre-che…]
    gym_create_wizard/Column[1]/Column[2]
    gym_create_wizard/Column[1]/Column[2]/Text[Search all equipment]
    gym_create_wizard/Column[1]/Column[2]/TextField[1]
    gym_create_wizard/Column[1]/Row[3]
    gym_create_wizard/Column[1]/Row[3]/Text[✓]
    gym_create_wizard/Column[1]/Row[3]/Column[1]
    gym_create_wizard/Column[1]/Row[3]/Column[1]/Text[Bodyweight]
    gym_create_wizard/Column[1]/Row[3]/Column[1]/Text[Always included]
    gym_create_wizard/Column[1]/Row[4]
    gym_create_wizard/Column[1]/Row[4]/Column[0]
    gym_create_wizard/Column[1]/Row[4]/Column[0]/Text[Dumbbell]
    gym_create_wizard/Column[1]/Row[5]
    gym_create_wizard/Column[1]/Row[5]/Column[0]
    gym_create_wizard/Column[1]/Row[5]/Column[0]/Text[Barbell]
    gym_create_wizard/Column[1]/Row[6]
    gym_create_wizard/Column[1]/Row[6]/Column[0]
    gym_create_wizard/Column[1]/Row[6]/Column[0]/Text[Kettlebell]
    gym_create_wizard/Column[1]/Row[7]
    gym_create_wizard/Column[1]/Row[7]/Column[0]
    gym_create_wizard/Column[1]/Row[7]/Column[0]/Text[Bench]
    gym_create_wizard/Column[1]/Row[8]
    gym_create_wizard/Column[1]/Row[8]/Column[0]
    gym_create_wizard/Column[1]/Row[8]/Column[0]/Text[Squat Rack]
    gym_create_wizard/Column[1]/Row[9]
    gym_create_wizard/Column[1]/Row[9]/Column[0]
    gym_create_wizard/Column[1]/Row[9]/Column[0]/Text[Pull Up Bar]
    gym_create_wizard/Column[1]/Row[10]
    gym_create_wizard/Column[1]/Row[10]/Column[0]
    gym_create_wizard/Column[1]/Row[10]/Column[0]/Text[Resistance Band]
    gym_create_wizard/Column[1]/Row[11]
    gym_create_wizard/Column[1]/Row[11]/Column[0]
    gym_create_wizard/Column[1]/Row[11]/Column[0]/Text[Cable Machine]
    gym_create_wizard/Column[1]/Text[1 item selected]
    gym_create_wizard/Column[1]/Button[Done selecting]
    gym_create_wizard/Zone[2]

---
## cross-side compare: Compose GymCreateWizardScreen <-> kit gym_create_wizard
- matched (by content anchor): 4
    = Add new gym
    = Always included
    = Search all equipment
    = Suggested equipment is pre-che…
- Compose-only (in design, MISSING from kit): 17
    KT  ${selected.size} item${if (sel…
    KT  Back
    KT  Gym name
    KT  Saving...|Done selecting
    KT  Tell us about your gym
    KT  We'll pre-load the most common…
    KT  What does ${gymType.displayNam…
    KT  emoji
    KT  item.label
    KT  null
    KT  placeholder
    KT  subtitle
    KT  title
    KT  trailing
    KT  type.description
    KT  type.displayName
    KT  type.emoji
- kit-only (ADDED by the wrapping): 14
    PY  1 item selected
    PY  Barbell
    PY  Bench
    PY  Bodyweight
    PY  Cable Machine
    PY  Done selecting
    PY  Dumbbell
    PY  Kettlebell
    PY  Pull Up Bar
    PY  Resistance Band
    PY  Squat Rack
    PY  What equipment do you have?
    PY  ←
    PY  ✓
