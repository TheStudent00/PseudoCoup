# UI layout ledger (KIT side) -- my_program

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)
(partial trace -- build raised TypeError: int() argument must be a string, a bytes-like object or a real number, not '_Any' after the nodes below)

  - Column[0]  <container>   size: wrap(rel)  style=prog_header(abs)
    - Row[0]  <container>   size: wrap(rel)  style=prog_hdr_row(abs)
      - Text[0]  <leaf>   size: weight(1.0)(rel)  style=prog_hdr_title(abs)
      - Text[Enrolled]  <leaf>   size: wrap(rel)  style=enrolled_badge(abs)

  ids:
    my_program/Column[0]
    my_program/Column[0]/Row[0]
    my_program/Column[0]/Row[0]/Text[0]
    my_program/Column[0]/Row[0]/Text[Enrolled]

---
## cross-side compare: Compose MyProgramScreen <-> kit my_program
- matched (by content anchor): 1
    = Enrolled
- Compose-only (in design, MISSING from kit): 9
    KT  Browse programs
    KT  Close menu|Update program
    KT  Join a program to see your tra…
    KT  No program yet
    KT  Update program
    KT  View other programs
    KT  current.program.name
    KT  desc
    KT  null
- kit-only (ADDED by the wrapping): 0
