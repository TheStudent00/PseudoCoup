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
- matched (by content anchor): 2
    = Program details
    = Swap
- Compose-only (in design, MISSING from kit): 52
    KT   — ${macro.durationLabel}
    KT   — ${phase.durationLabel}
    KT  ${phase.label} · ${phase.typeL…
    KT  ${selectedPathIds.size} select…
    KT  Add
    KT  Add day
    KT  Add week
    KT  All days and exercises in this…
    KT  All exercises in this day will…
    KT  Back
    KT  Cancel
    KT  Clone
    KT  Close
    KT  Collapse|Expand
    KT  Completed
    KT  Day name (e.g. Push A)
    KT  Description
    KT  Join
    KT  Linked paths
    KT  No details for this cycle yet.
- kit-only (ADDED by the wrapping): 2
    PY  No program selected.
    PY  ←
