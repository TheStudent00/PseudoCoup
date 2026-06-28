# UI layout ledger (KIT side) -- my_program

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM -> dynamic list items are empty; static skeleton shown.)

  - Column[0]  <container>   size: wrap(rel)  style=hero(abs)
    - Text[No program yet]  <leaf>   size: wrap(rel)  style=hero_title(abs)
    - Text[Join a program to see your tra…]  <leaf>   size: wrap(rel)  style=hero_sub(abs)
  - Button[Browse programs]  <leaf>   size: wrap(rel)  style=btn_filled(abs)

  ids:
    my_program/Column[0]
    my_program/Column[0]/Text[No program yet]
    my_program/Column[0]/Text[Join a program to see your tra…]
    my_program/Button[Browse programs]

---
## cross-side compare: Compose MyProgramScreen <-> kit my_program
- matched (by content anchor): 3
    = Browse programs
    = Join a program to see your tra…
    = No program yet
- Compose-only (in design, MISSING from kit): 5
    KT  Close menu|Update program
    KT  Enrolled
    KT  View other programs
    KT  current.program.name
    KT  desc
- kit-only (ADDED by the wrapping): 0
