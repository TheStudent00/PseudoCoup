# PseudoUI runtime verify -- gym_list  (IR interpreted vs hand-built, same seeded data)

Interpreted the generated control-flow IR against the app's seeded InMemoryDb and
compared the RESOLVED leaves to the hand-built screen's runtime trace.

## dynamic values resolved by the interpreter (4/4 also in hand-built)
  OK   T: 'Home Gym'
  OK   T: '🏠 Home Gym'
  OK   T: '2 items'
  OK   T: 'Olympic Bar, Adjustable Dumbbe…'

## leaf agreement
- shared (type+content):  7
- interpreted-only:       3   (Compose representation, e.g. 'Active' icon-chip)
    INT I: 'Add gym'
    INT I: 'Back'
    INT T: 'Active'
- hand-built-only:        3   (kit glyphs/helpers, e.g. '✓ Active', '←', '+')
    HB  T: '+'
    HB  T: '←'
    HB  T: '✓ Active'

## unresolved IR exprs (would need a binding-spec entry): 0
