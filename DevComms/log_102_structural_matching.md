# log_102 — structural (dynamic-aware) matching: gym_list card reproduces faithfully

Date: 2026-06-28
Type: implementation. gym_list vertical slice, step 2 (the compare that makes dynamic rows count).

## The problem it fixes

Content-anchor matching can't join dynamic content: the kit renders the RESOLVED value
(`Home Gym`), Compose holds the BINDING (`gym.name`) — same widget, different string. So the
gym card (all bindings) scored ~0 on content even though it's faithful.

## Structural LCS over leaf sequences

`kit_ledger` now computes a **longest-common-subsequence of the two leaf-widget sequences**
(pre-order Text/Button/Icon/Input). The match predicate is dynamic-aware:
- a **static** Compose leaf (a pure string literal) matches by **content**;
- a **dynamic** leaf (a binding) matches by **type + order** only.

So a faithfully-reproduced dynamic row counts. `ui_ledger.collect_ids` now flags each leaf
static/dynamic (a pure `"…"` literal vs a binding/expression).

## gym_list result

```
STRUCTURAL leaf match (LCS): 16/30 Compose leaves aligned (53%)   [was 5 by content anchor]
kit leaves NOT aligned:      1                                    [the key number]
static content matched:      5  (Equipment · Delete gym · Set active · Gym profiles · No equipment listed)
```

The decisive figure is **1 unaligned kit leaf**: the kit adds essentially nothing Compose
doesn't have — it's a **faithful subset**. The 14 unaligned *Compose* leaves are not missing
widgets; they are (a) conditional variants Compose captures statically but one trace doesn't hit
(both `Set active` AND `✓ Active`), (b) representation differences (`Back`/`Add gym` icons vs the
kit's `←`/`+` glyphs), and (c) the template-once-vs-two-rendered-cards counting asymmetry. So
**gym_list's kit faithfully reproduces the Compose card.**

## At scale (still a lower bound — only gym_list is seeded)

Aggregate structural leaf match 252/2016 = 12%, but per-screen where a screen traces fully it's
meaningful: workout_warmup 20/31 = 64%, gym_list 16/30 = 53%. The drag is un-seeded screens
under-rendering their dynamic rows + Compose static-parse capturing every conditional state
(workout_execution: 558 Compose leaves vs a one-path trace). Seeding more screens lifts it.

## Next

gym_list is structurally green-ish (faithful subset). To CLOSE the slice: verify gym_list's
logic (oracle/fuzz on the gym service/repo) so behaviour is proven too — then the slice is done
end-to-end, and the Compose-node -> kit-define_* mapping it taught is ready to encode as the
generator (PseudoUI).
