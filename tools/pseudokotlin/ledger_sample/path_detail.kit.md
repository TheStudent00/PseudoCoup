# UI layout ledger (KIT side) -- path_detail

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Path not found.]  <leaf>   size: wrap(rel)  style=card_body(abs)

---
## cross-side compare: Compose PathDetailScreen <-> kit path_detail
- distinct widget signatures matched: 2/7 = 28%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
