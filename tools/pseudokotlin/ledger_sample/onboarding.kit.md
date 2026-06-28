# UI layout ledger (KIT side) -- onboarding

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Progress[0]  <leaf>   size: wrap(rel)
  - Column[1]  <container>   size: wrap(rel)  style=wiz_scaffold(abs)
    - Text[You're all set]  <leaf>   size: wrap(rel)  style=wiz_title(abs)
    - Text[We'll load a starter program t…]  <leaf>   size: wrap(rel)  style=wiz_subtitle(abs)
    - Column[2]  <container>   size: wrap(rel)  style=wiz_content(abs)
      - Text[Tap below and we'll set up you…]  <leaf>   size: wrap(rel)  style=note(abs)
    - Button[Let's go →]  <leaf>   size: wrap(rel)  style=wiz_primary(abs)

  ids:
    onboarding/Progress[0]
    onboarding/Column[1]
    onboarding/Column[1]/Text[You're all set]
    onboarding/Column[1]/Text[We'll load a starter program t…]
    onboarding/Column[1]/Column[2]
    onboarding/Column[1]/Column[2]/Text[Tap below and we'll set up you…]
    onboarding/Column[1]/Button[Let's go →]

---
## cross-side compare: Compose OnboardingScreen <-> kit onboarding
- STRUCTURAL leaf match (LCS, dynamic-aware): 4/237 Compose leaves aligned to kit (1%)
- static content matched (by literal): 1
    = Let's go →
- Compose leaves NOT aligned: 233  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 91, kit-only 3)
