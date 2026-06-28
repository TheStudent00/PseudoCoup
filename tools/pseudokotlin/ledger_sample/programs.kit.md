# UI layout ledger (KIT side) -- programs

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Programs]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No programs yet.]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Tap + to build your first prog…]  <leaf>   size: wrap(rel)  style=empty_body(abs)
  - Overlay[2]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    programs/Row[0]
    programs/Row[0]/Button[←]
    programs/Row[0]/Column[1]
    programs/Row[0]/Column[1]/Text[Programs]
    programs/Column[1]
    programs/Column[1]/Text[No programs yet.]
    programs/Column[1]/Text[Tap + to build your first prog…]
    programs/Overlay[2]
    programs/Overlay[2]/Button[+]

---
## cross-side compare: Compose ProgramsScreen <-> kit programs
- matched (by content anchor): 3
    = No programs yet.
    = Programs
    = Tap + to build your first prog…
- Compose-only (in design, MISSING from kit): 26
    KT  Active
    KT  Archive
    KT  Back
    KT  Cancel
    KT  Create
    KT  Create program
    KT  Delete
    KT  Delete program?
    KT  Duplicate
    KT  Edit
    KT  New program
    KT  Program name
    KT  Program options
    KT  Recommended for your paths
    KT  Swap
    KT  Swap for this program|Join pro…
    KT  Swap to ${program.name}?
    KT  Switching programs will restar…
    KT  This will permanently remove t…
    KT  desc
- kit-only (ADDED by the wrapping): 2
    PY  +
    PY  ←
