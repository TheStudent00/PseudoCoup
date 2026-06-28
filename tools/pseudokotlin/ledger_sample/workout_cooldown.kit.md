# UI layout ledger (KIT side) -- workout_cooldown

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Slow walk]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=cfv_col(abs)
    - Text[🌙]  <leaf>   size: wrap(rel)  style=cfv_emoji(abs)
    - Text[Nicely done]  <leaf>   size: wrap(rel)  style=cfv_headline(abs)
    - Text[Take a breath — you're all wra…]  <leaf>   size: wrap(rel)  style=cfv_subtext(abs)
    - Button[Finish]  <leaf>   size: wrap(rel)  style=cfv_primary(abs)

  ids:
    workout_cooldown/Row[0]
    workout_cooldown/Row[0]/Button[←]
    workout_cooldown/Row[0]/Column[1]
    workout_cooldown/Row[0]/Column[1]/Text[Slow walk]
    workout_cooldown/Column[1]
    workout_cooldown/Column[1]/Text[🌙]
    workout_cooldown/Column[1]/Text[Nicely done]
    workout_cooldown/Column[1]/Text[Take a breath — you're all wra…]
    workout_cooldown/Column[1]/Button[Finish]

---
## cross-side compare: Compose WorkoutCooldownScreen <-> kit workout_cooldown
- STRUCTURAL leaf match (LCS, dynamic-aware): 6/44 Compose leaves aligned to kit (13%)
- static content matched (by literal): 3
    = Finish
    = Nicely done
    = 🌙
- Compose leaves NOT aligned: 38  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 26, kit-only 3)
