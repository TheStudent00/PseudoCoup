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
- matched (by content anchor): 1
    = Let's go →
- Compose-only (in design, MISSING from kit): 91
    KT  ${definition.minSessionsPerWee…
    KT  ${lift.label} (${weightUnit.na…
    KT  ${path.minSessionsPerWeek}–${p…
    KT  ${program.totalWeeks} week${if…
    KT  ${selected.size} item${if (sel…
    KT  A bit about your body
    KT  Always included
    KT  Are you training right now?
    KT  Back
    KT  Back to options
    KT  Bodyweight (${weightUnit.name.…
    KT  Calibrate with us
    KT  Choose your first path
    KT  Configure equipment later
    KT  Continue
    KT  Continue →
    KT  Done selecting
    KT  Enter what you can — leave any…
    KT  Enter your numbers
    KT  Enter your numbers|Calibrate w…
- kit-only (ADDED by the wrapping): 3
    PY  Tap below and we'll set up you…
    PY  We'll load a starter program t…
    PY  You're all set
