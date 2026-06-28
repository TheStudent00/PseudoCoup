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
- STRUCTURAL leaf match (LCS, dynamic-aware): 2/19 Compose leaves aligned to kit (10%)
- static content matched (by literal): 1
    = Path not found.
- Compose leaves NOT aligned: 17  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 14, kit-only 1)
