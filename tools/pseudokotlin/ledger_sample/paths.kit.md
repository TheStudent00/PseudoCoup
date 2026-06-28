# UI layout ledger (KIT side) -- paths

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Column[0]  <container>   size: wrap(rel)  style=cta_empty(abs)
    - Text[Start with your why.]  <leaf>   size: wrap(rel)  style=cta_title(abs)
    - Text[A Path connects your training …]  <leaf>   size: wrap(rel)  style=cta_body(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=cta_btn(abs)
      - Text[Find your path]  <leaf>   size: wrap(rel)  style=cta_btn_label(abs)

---
## cross-side compare: Compose PathsScreen <-> kit paths
- distinct widget signatures matched: 3/13 = 23%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
