# UI layout ledger (KIT side) -- onboarding

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Progress[0]  <leaf>   size: wrap(rel)
  - Column[1]  <container>   size: wrap(rel)  style=wiz_scaffold(abs)
    - Text[What should we call you?]  <leaf>   size: wrap(rel)  style=wiz_title(abs)
    - Text[Even just initials work.]  <leaf>   size: wrap(rel)  style=wiz_subtitle(abs)
    - Column[2]  <container>   size: wrap(rel)  style=wiz_content(abs)
      - Column[0]  <container>   size: wrap(rel)  style=labeled_field(abs)
        - Text[Your name]  <leaf>   size: wrap(rel)  style=field_label(abs)
        - TextField[Your name]  <leaf>   size: wrap(rel)
    - Button[Continue]  <leaf>   size: wrap(rel)  style=wiz_primary(abs)

---
## cross-side compare: Compose OnboardingScreen <-> kit onboarding
- distinct widget signatures matched: 4/53 = 7%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 1
    PY  F:Your name
