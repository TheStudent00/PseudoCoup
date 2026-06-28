# UI layout ledger (KIT side) -- report_bug

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Report a bug]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Tell us what went wrong — what…]  <leaf>   size: wrap(rel)  style=note(abs)
  - TextField[What happened?]  <leaf>   size: wrap(rel)
  - Text[How bad is it?]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[4]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Minor]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[Annoying]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[Blocking]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Column[5]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Your name (optional)]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Your name]  <leaf>   size: wrap(rel)
  - Column[6]  <container>   size: wrap(rel)  style=card(abs)
    - Text[Crash detected]  <leaf>   size: wrap(rel)  style=card_title(abs)
    - Text[We detected a crash on your la…]  <leaf>   size: wrap(rel)  style=card_body(abs)
  - Button[Send report]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Zone[8]  <leaf>   size: wrap(rel)

  ids:
    report_bug/Row[0]
    report_bug/Row[0]/Button[←]
    report_bug/Row[0]/Column[1]
    report_bug/Row[0]/Column[1]/Text[Report a bug]
    report_bug/Text[Tell us what went wrong — what…]
    report_bug/TextField[What happened?]
    report_bug/Text[How bad is it?]
    report_bug/Row[4]
    report_bug/Row[4]/Button[Minor]
    report_bug/Row[4]/Button[Annoying]
    report_bug/Row[4]/Button[Blocking]
    report_bug/Column[5]
    report_bug/Column[5]/Text[Your name (optional)]
    report_bug/Column[5]/TextField[Your name]
    report_bug/Column[6]
    report_bug/Column[6]/Text[Crash detected]
    report_bug/Column[6]/Text[We detected a crash on your la…]
    report_bug/Button[Send report]
    report_bug/Zone[8]

---
## cross-side compare: Compose ReportBugScreen <-> kit report_bug
- STRUCTURAL leaf match (LCS, dynamic-aware): 11/38 Compose leaves aligned to kit (28%)
- static content matched (by literal): 7
    = How bad is it?
    = Report a bug
    = Send report
    = Tell us what went wrong — what…
    = We detected a crash on your la…
    = What happened?
    = Your name (optional)
- Compose leaves NOT aligned: 27  ·  kit leaves not aligned: 2
- (raw content-anchor only: Compose-only 15, kit-only 6)
