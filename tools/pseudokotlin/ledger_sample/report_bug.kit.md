# UI layout ledger (KIT side) -- report_bug

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Report a bug]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Tell us what went wrong — what…]  <leaf>   size: wrap(rel)  style=note(abs)
  - TextField[What happened?]  <leaf>   size: wrap(rel)
  - Text[How bad is it?]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[4]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Minor]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[Annoying]  <leaf>   size: wrap(rel)  style=seg_mid_on(abs)
    - Button[Blocking]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Column[5]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Your name (optional)]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Your name]  <leaf>   size: wrap(rel)
  - Column[6]  <container>   size: wrap(rel)  style=card(abs)
    - Text[Crash detected]  <leaf>   size: wrap(rel)  style=card_title(abs)
    - Text[We detected a crash on your la…]  <leaf>   size: wrap(rel)  style=card_body(abs)
  - Button[Send report]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Zone[8]  <leaf>   size: wrap(rel)

---
## cross-side compare: Compose ReportBugScreen <-> kit report_bug
- distinct widget signatures matched: 6/14 = 42%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 1
    PY  F:·DYN·
