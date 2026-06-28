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
- matched (by content anchor): 3
    = Finish
    = Nicely done
    = 🌙
- Compose-only (in design, MISSING from kit): 26
    KT  ${state.activity.emoji} ${stat…
    KT  +1 min
    KT  Back to workout|Back to cooldo…
    KT  Compared to when you started
    KT  ConditioningCatalog.COOLDOWN_W…
    KT  Cooldown|Cooldown
    KT  Done — wrap up
    KT  Forgot something? Back to work…
    KT  Got it
    KT  How are you feeling?
    KT  I'm done
    KT  Start ${activity.name}
    KT  Take a few minutes to come dow…
    KT  Why cool down?
    KT  Your muscles are warmest right…
    KT  activity.emoji
    KT  activity.name
    KT  activity.tagline
    KT  formatMinutes(activity.default…
    KT  formatTime(state.remainingSeco…
- kit-only (ADDED by the wrapping): 3
    PY  Slow walk
    PY  Take a breath — you're all wra…
    PY  ←
