# UI layout ledger (KIT side) -- gym_list

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Gym profiles]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No gyms yet. Tap + to add one.]  <leaf>   size: wrap(rel)  style=empty_body(abs)
  - Overlay[2]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    gym_list/Row[0]
    gym_list/Row[0]/Button[←]
    gym_list/Row[0]/Column[1]
    gym_list/Row[0]/Column[1]/Text[Gym profiles]
    gym_list/Column[1]
    gym_list/Column[1]/Text[No gyms yet. Tap + to add one.]
    gym_list/Overlay[2]
    gym_list/Overlay[2]/Button[+]

---
## cross-side compare: Compose GymListScreen <-> kit gym_list
- matched (by content anchor): 2
    = Gym profiles
    = No gyms yet. Tap + to add one.
- Compose-only (in design, MISSING from kit): 14
    KT  ${equipmentList.size} items
    KT  ${type.emoji} ${type.displayNa…
    KT  Active
    KT  Add gym
    KT  Back
    KT  Delete gym
    KT  Equipment
    KT  No equipment listed
    KT  Set active
    KT  equipmentNames
    KT  gym.name
    KT  label
    KT  null
    KT  value
- kit-only (ADDED by the wrapping): 2
    PY  +
    PY  ←
