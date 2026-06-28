# log_101 — gym_list vertical slice: the faithful seeded trace works

Date: 2026-06-28
Type: implementation milestone. First step of the gym_list vertical slice (the agreed path:
prove the verified loop closes end-to-end on one screen, then mechanize the rest).

## Seeded trace: the kit renders real rows through the REAL data path

The at-scale compare (log_100) was confounded by an empty mock VM -> dynamic rows didn't render.
Fixed for gym_list with a **faithful seeded trace**: a real `InMemoryDb` is seeded with two
`GymProfileEntity` via the real `GymProfileRepository`, the screen is built with the real
`GymListViewModel(db)` (NOT mocked), so `vm.gyms()` flows through the actual
repository -> service -> VM path. Only the kit UI (recording) and the router (navigation) are
stubbed.

Result: 4 nodes -> **26 nodes**, with real gym cards:
```
Column[gym_card]
  Row[gym_top]  -> Text[Home Gym] (weight 1) + Text[✓ Active]
  Text[🏠 Home Gym]            (gym_type)
  Text[Equipment] · Text[0 items] · Text[No equipment listed]
  Row[gym_del]  -> Button[Delete gym]
```
The dynamic list structure now renders through the genuine data path — the harness every later
screen reuses (per-screen seeders in `SEEDERS`).

## The asymmetry this surfaces — and the next step

Dynamic content can't be joined by content anchor: the kit renders the RESOLVED value
(`Home Gym`), Compose holds the BINDING (`gym.name`). Same widget, different string. So the
gym-card compare needs **structural matching** — match the card's widget tree/shape and
size/positioning, treating a resolved-literal node and a binding node as equivalent when they
sit at the same path and type. Static chrome still joins by content anchor (already works).

That structural compare for the dynamic rows is the next slice step, then: verify gym_list's
logic (oracle/fuzz on the gym service/repo), and the slice is closed end-to-end — at which
point the Compose-tree -> kit-define_* mapping it taught becomes the seed of the generator
(PseudoUI).
