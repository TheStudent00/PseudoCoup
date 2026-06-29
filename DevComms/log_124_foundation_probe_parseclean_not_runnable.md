# log_124 — foundation probe: "compile-clean" is PARSE-clean, not runnable

Date: 2026-06-28
Type: measurement / reality-check. Answers the user's "are we getting ahead of the foundation?" — yes,
with numbers. Triggered by the Bucket-3 sequencing concern (PROGRESS.md).

## The question

PseudoUI breadth (gym_list, exercise_detail) binds a generated screen to a TRANSPILED VM but calls the
HAND-BUILT domain (`WFL_PseudoCoup/src/domain`) underneath. Would Track B's TRANSPILED domain
(`WFL_MixingCenter`) actually RUN under a screen — i.e., does "192/254 compile-clean" mean runnable?

## The probe — transpiled GymRepository (the gym domain our proven screen uses)

```
1) COMPILE: OK                                      <- this is what "192/254" counts
2) IMPORT FAILS: ModuleNotFoundError: No module named 'core.flow'
```

It fails at IMPORT — before construct, before run. And the source shows it could never run anyway:
- `def __init__(self): pass` — the `@Inject constructor(private val profileDao…)` was DROPPED, so the
  DAO fields are never set;
- every real dependency is a `# TODO_RAW_IMPORT` stub (Room, DAOs, entities, `UUID`, `javax.inject`);
- method bodies call unbound names: `profileDao.getAll()`, `UUID.randomUUID()`, `System.currentTimeMillis()`.

## The gap, quantified (254 transpiled files)

- **201 / 254 (79%)** have unresolved imports (`TODO_RAW_IMPORT`).
- **19 / 20 repositories** have an empty `__init__(self)` — DI params dropped, cannot be wired.
- the runtime modules the code imports (`core.flow`) DON'T EXIST (`core/` has debug/time/wear/… but no `flow`).

## What it means

"192/254 compile-clean" = PARSE-clean scaffolding, NOT runnable code. The runtime-PROVEN frontier is
the **11 oracle engines** (self-contained logic, run-equivalence verified). The DB-backed domain
(repositories/services — the layer the UI actually needs) parses but does not run: dropped DI,
unresolved imports, missing runtime. This is exactly WHY the PseudoUI generator binds to the hand-built
domain via adapters — the transpiled repository layer isn't runnable, so there was no alternative.

**Conclusion:** yes, the UI/breadth work is ahead of the foundation. It proves the UI MECHANISM on a
hand-built stand-in floor. The traced floor requires the parse-clean → runnable jump: restore DI
constructors, resolve the `TODO_RAW_IMPORT`s, supply the runtime modules (`core.flow`, …), and the
Room→DB boundary. That jump — not more UI — is the real ceiling.

## Honest correction to the dashboard

Track B's headline "192/254 compile-clean" OVERSTATES the runnable foundation. Re-stated: 192/254
**parse-clean**; runnable frontier = **11 engines** (oracle); DB-backed domain **not yet runnable**
(79% TODO imports, 19/20 dropped-DI). PROGRESS.md / .html updated accordingly.
