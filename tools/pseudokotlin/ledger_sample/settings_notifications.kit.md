# UI layout ledger (KIT side) -- settings_notifications

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Notifications]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Notifications]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Row[2]  <container>   size: wrap(rel)  style=settings_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=settings_col(abs)
      - Text[Workout reminders]  <leaf>   size: wrap(rel)  style=settings_title(abs)
      - Text[Remind you when it's time to l…]  <leaf>   size: wrap(rel)  style=settings_sub(abs)
  - Row[3]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Push]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[In-app]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[None]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Divider[4]  <leaf>   size: wrap(rel)
  - Row[5]  <container>   size: wrap(rel)  style=settings_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=settings_col(abs)
      - Text[Microcycle reminders]  <leaf>   size: wrap(rel)  style=settings_title(abs)
      - Text[Only 1 more workout left to hi…]  <leaf>   size: wrap(rel)  style=settings_sub(abs)
  - Row[6]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Push]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[In-app]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[None]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Divider[7]  <leaf>   size: wrap(rel)
  - Row[8]  <container>   size: wrap(rel)  style=settings_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=settings_col(abs)
      - Text[Mesocycle reminders]  <leaf>   size: wrap(rel)  style=settings_title(abs)
      - Text[Peak week push and upcoming de…]  <leaf>   size: wrap(rel)  style=settings_sub(abs)
  - Row[9]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Push]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[In-app]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[None]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Divider[10]  <leaf>   size: wrap(rel)
  - Row[11]  <container>   size: wrap(rel)  style=settings_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=settings_col(abs)
      - Text[Log a victory]  <leaf>   size: wrap(rel)  style=settings_title(abs)
      - Text[Prompts to record qualitative …]  <leaf>   size: wrap(rel)  style=settings_sub(abs)
  - Row[12]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Push]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[In-app]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[None]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)

  ids:
    settings_notifications/Row[0]
    settings_notifications/Row[0]/Button[←]
    settings_notifications/Row[0]/Column[1]
    settings_notifications/Row[0]/Column[1]/Text[Notifications]
    settings_notifications/Text[Notifications]
    settings_notifications/Row[2]
    settings_notifications/Row[2]/Column[0]
    settings_notifications/Row[2]/Column[0]/Text[Workout reminders]
    settings_notifications/Row[2]/Column[0]/Text[Remind you when it's time to l…]
    settings_notifications/Row[3]
    settings_notifications/Row[3]/Button[Push]
    settings_notifications/Row[3]/Button[In-app]
    settings_notifications/Row[3]/Button[None]
    settings_notifications/Divider[4]
    settings_notifications/Row[5]
    settings_notifications/Row[5]/Column[0]
    settings_notifications/Row[5]/Column[0]/Text[Microcycle reminders]
    settings_notifications/Row[5]/Column[0]/Text[Only 1 more workout left to hi…]
    settings_notifications/Row[6]
    settings_notifications/Row[6]/Button[Push]
    settings_notifications/Row[6]/Button[In-app]
    settings_notifications/Row[6]/Button[None]
    settings_notifications/Divider[7]
    settings_notifications/Row[8]
    settings_notifications/Row[8]/Column[0]
    settings_notifications/Row[8]/Column[0]/Text[Mesocycle reminders]
    settings_notifications/Row[8]/Column[0]/Text[Peak week push and upcoming de…]
    settings_notifications/Row[9]
    settings_notifications/Row[9]/Button[Push]
    settings_notifications/Row[9]/Button[In-app]
    settings_notifications/Row[9]/Button[None]
    settings_notifications/Divider[10]
    settings_notifications/Row[11]
    settings_notifications/Row[11]/Column[0]
    settings_notifications/Row[11]/Column[0]/Text[Log a victory]
    settings_notifications/Row[11]/Column[0]/Text[Prompts to record qualitative …]
    settings_notifications/Row[12]
    settings_notifications/Row[12]/Button[Push]
    settings_notifications/Row[12]/Button[In-app]
    settings_notifications/Row[12]/Button[None]
