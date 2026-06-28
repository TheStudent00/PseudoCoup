# UI layout ledger (KIT side) -- paths

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Column[0]  <container>   size: wrap(rel)  style=cta_empty(abs)
    - Text[Start with your why.]  <leaf>   size: wrap(rel)  style=cta_title(abs)
    - Text[A Path connects your training …]  <leaf>   size: wrap(rel)  style=cta_body(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=cta_btn(abs)
      - Text[Find your path]  <leaf>   size: wrap(rel)  style=cta_btn_label(abs)

  ids:
    paths/Column[0]
    paths/Column[0]/Text[Start with your why.]
    paths/Column[0]/Text[A Path connects your training …]
    paths/Column[0]/Column[2]
    paths/Column[0]/Column[2]/Text[Find your path]

---
## cross-side compare: Compose PathsScreen <-> kit paths
- STRUCTURAL leaf match (LCS, dynamic-aware): 3/45 Compose leaves aligned to kit (6%)
- static content matched (by literal): 3
    = A Path connects your training …
    = Find your path
    = Start with your why.
- Compose leaves NOT aligned: 42  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 25, kit-only 0)
