# UI layout ledger (KIT side) -- path_detail

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Path not found.]  <leaf>   size: wrap(rel)  style=card_body(abs)

  ids:
    path_detail/Row[0]
    path_detail/Row[0]/Button[←]
    path_detail/Row[0]/Column[1]
    path_detail/Row[0]/Column[1]/Text[0]
    path_detail/Text[Path not found.]

---
## cross-side compare: Compose PathDetailScreen <-> kit path_detail
- matched (by content anchor): 1
    = Path not found.
- Compose-only (in design, MISSING from kit): 14
    KT  ${definition.minSessionsPerWee…
    KT  Back
    KT  Modality
    KT  Research
    KT  The evidence
    KT  Why it works
    KT  body
    KT  citation
    KT  definition.educationalCopy
    KT  definition.evidenceSummary
    KT  definition.modalityNotes
    KT  definition.tagline
    KT  title
    KT  ~${definition.targetMinutesPer…
- kit-only (ADDED by the wrapping): 1
    PY  ←
