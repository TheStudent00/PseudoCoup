# UI layout ledger (KIT side) -- workout_warmup

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Warm up]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[?]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=prog_header(abs)
    - Text[Let's get you moving.]  <leaf>   size: wrap(rel)  style=prog_hdr_title(abs)
    - Text[Pick something fun for a few m…]  <leaf>   size: wrap(rel)  style=prog_hdr_body(abs)
  - Column[2]  <container>   size: wrap(rel)  style=cap_col(abs)
    - Row[0]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🕺]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Dance to a song]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[Put on one favourite track and…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[1]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[☀️]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Sun salutations]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[6–8 slow rounds — hips, should…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[2]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🤸]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Dynamic movement]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[Leg swings, arm circles, hip c…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[3]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🥊]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Shadow boxing]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[Light jabs and footwork — warm…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[4]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🚴]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Easy cardio]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[Bike, row, or treadmill at a c…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[5]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🚶]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Brisk walk]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[A quick walk to raise your tem…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
    - Row[6]  <container>   size: wrap(rel)  style=cap_card(abs)
      - Text[🏃]  <leaf>   size: wrap(rel)  style=cap_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)
        - Row[0]  <container>   size: wrap(rel)  style=cap_titlerow(abs)
          - Text[Light jog]  <leaf>   size: wrap(rel)  style=cap_name(abs)
        - Text[An easy jog in place or around…]  <leaf>   size: wrap(rel)  style=cap_tagline(abs)
      - Text[▶]  <leaf>   size: wrap(rel)  style=cap_play(abs)
  - Button[Skip warm-up]  <leaf>   size: wrap(rel)  style=btn_text(abs)

  ids:
    workout_warmup/Row[0]
    workout_warmup/Row[0]/Button[←]
    workout_warmup/Row[0]/Column[1]
    workout_warmup/Row[0]/Column[1]/Text[Warm up]
    workout_warmup/Row[0]/Button[?]
    workout_warmup/Column[1]
    workout_warmup/Column[1]/Text[Let's get you moving.]
    workout_warmup/Column[1]/Text[Pick something fun for a few m…]
    workout_warmup/Column[2]
    workout_warmup/Column[2]/Row[0]
    workout_warmup/Column[2]/Row[0]/Text[🕺]
    workout_warmup/Column[2]/Row[0]/Column[1]
    workout_warmup/Column[2]/Row[0]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[0]/Column[1]/Row[0]/Text[Dance to a song]
    workout_warmup/Column[2]/Row[0]/Column[1]/Text[Put on one favourite track and…]
    workout_warmup/Column[2]/Row[0]/Text[▶]
    workout_warmup/Column[2]/Row[1]
    workout_warmup/Column[2]/Row[1]/Text[☀️]
    workout_warmup/Column[2]/Row[1]/Column[1]
    workout_warmup/Column[2]/Row[1]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[1]/Column[1]/Row[0]/Text[Sun salutations]
    workout_warmup/Column[2]/Row[1]/Column[1]/Text[6–8 slow rounds — hips, should…]
    workout_warmup/Column[2]/Row[1]/Text[▶]
    workout_warmup/Column[2]/Row[2]
    workout_warmup/Column[2]/Row[2]/Text[🤸]
    workout_warmup/Column[2]/Row[2]/Column[1]
    workout_warmup/Column[2]/Row[2]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[2]/Column[1]/Row[0]/Text[Dynamic movement]
    workout_warmup/Column[2]/Row[2]/Column[1]/Text[Leg swings, arm circles, hip c…]
    workout_warmup/Column[2]/Row[2]/Text[▶]
    workout_warmup/Column[2]/Row[3]
    workout_warmup/Column[2]/Row[3]/Text[🥊]
    workout_warmup/Column[2]/Row[3]/Column[1]
    workout_warmup/Column[2]/Row[3]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[3]/Column[1]/Row[0]/Text[Shadow boxing]
    workout_warmup/Column[2]/Row[3]/Column[1]/Text[Light jabs and footwork — warm…]
    workout_warmup/Column[2]/Row[3]/Text[▶]
    workout_warmup/Column[2]/Row[4]
    workout_warmup/Column[2]/Row[4]/Text[🚴]
    workout_warmup/Column[2]/Row[4]/Column[1]
    workout_warmup/Column[2]/Row[4]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[4]/Column[1]/Row[0]/Text[Easy cardio]
    workout_warmup/Column[2]/Row[4]/Column[1]/Text[Bike, row, or treadmill at a c…]
    workout_warmup/Column[2]/Row[4]/Text[▶]
    workout_warmup/Column[2]/Row[5]
    workout_warmup/Column[2]/Row[5]/Text[🚶]
    workout_warmup/Column[2]/Row[5]/Column[1]
    workout_warmup/Column[2]/Row[5]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[5]/Column[1]/Row[0]/Text[Brisk walk]
    workout_warmup/Column[2]/Row[5]/Column[1]/Text[A quick walk to raise your tem…]
    workout_warmup/Column[2]/Row[5]/Text[▶]
    workout_warmup/Column[2]/Row[6]
    workout_warmup/Column[2]/Row[6]/Text[🏃]
    workout_warmup/Column[2]/Row[6]/Column[1]
    workout_warmup/Column[2]/Row[6]/Column[1]/Row[0]
    workout_warmup/Column[2]/Row[6]/Column[1]/Row[0]/Text[Light jog]
    workout_warmup/Column[2]/Row[6]/Column[1]/Text[An easy jog in place or around…]
    workout_warmup/Column[2]/Row[6]/Text[▶]
    workout_warmup/Button[Skip warm-up]

---
## cross-side compare: Compose WorkoutWarmupScreen <-> kit workout_warmup
- matched (by content anchor): 3
    = Let's get you moving.
    = Pick something fun for a few m…
    = Skip warm-up
- Compose-only (in design, MISSING from kit): 18
    KT  ${state.activity.emoji} ${stat…
    KT  +1 min
    KT  Back|Back to warm-ups
    KT  I'm done
    KT  Start ${activity.name}
    KT  Start workout
    KT  Warm up|Warm up
    KT  Why warm up?
    KT  You're warmed up
    KT  activity.emoji
    KT  activity.name
    KT  activity.tagline
    KT  formatMinutes(activity.default…
    KT  formatTime(state.remainingSeco…
    KT  it
    KT  state.activity.phase.label()
    KT  state.activity.tagline
    KT  💪
- kit-only (ADDED by the wrapping): 25
    PY  6–8 slow rounds — hips, should…
    PY  ?
    PY  A quick walk to raise your tem…
    PY  An easy jog in place or around…
    PY  Bike, row, or treadmill at a c…
    PY  Brisk walk
    PY  Dance to a song
    PY  Dynamic movement
    PY  Easy cardio
    PY  Leg swings, arm circles, hip c…
    PY  Light jabs and footwork — warm…
    PY  Light jog
    PY  Put on one favourite track and…
    PY  Shadow boxing
    PY  Sun salutations
    PY  Warm up
    PY  ←
    PY  ▶
    PY  ☀️
    PY  🏃
