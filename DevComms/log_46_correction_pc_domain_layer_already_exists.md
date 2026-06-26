# log_46 — CORRECTION: PC's non-UI domain layer already exists. log_44/45 were wrong.

Date: 2026-06-25
Type: correction (I was wrong; the user caught it). log_44 and log_45 claimed the non-UI domain
layer (entities, DAOs, repositories, engines) has "0 Python equivalent" and "must be built". That is
false. PC already has it, hand-built, ~1:1 with WFL.

## The facts (directly measured in `WFL_PseudoCoup/src/`)

```
src/engine    9 files    4,075 LOC     (WFL engine/ = 9 files -> 1:1, names match exactly)
src/domain   39 files   15,732 LOC     (synchronous service layer)
src/data    131 files   17,409 LOC     (WFL data/ = 135 -> near parity)
              data/db/entity   27 files   (WFL = 27 -> 1:1)
              data/model       47 files
              data/repository  52 files
~37,000 LOC of already-written non-UI Python.
```

- `src/engine/autoregulation_engine.py` is **1,224 lines** and contains `compute_e1rm`,
  `suggest_raw_weight`, `predict_reps` — the exact functions log_45 said "do not exist."
- All 9 engines map by name: autoregulation, calibration, cardio_recovery, mobility_session_generator,
  notification_triggers, periodization, restart, substitution, warmup.
- Domain services are substantial, not stubs: autoregulation_service 1,369 LOC, restart_service 639,
  calibration_service 461.

## How log_44/45 got it wrong

The literal transpiler writes its output into `PseudoCoup/core/` + `PseudoCoup/build/literal/` — an
isolated sandbox that genuinely holds only `flow.py` + `coroutines.py`. I let that empty sandbox stand
in for the whole app and concluded "PC has no domain layer." The real app is the **other repo**,
`WFL_PseudoCoup/src/`, which I knew existed and failed to check. The "0 in Python" figure was the
opposite of true.

## The "flows" point was right too

The transpiler emits `combine(flowA, flowB, ...)` against the fake `core/flow.py` shim. But **PC does
not use flows.** It deliberately replaced Kotlin's reactive `Flow` with **synchronous services +
`State`/recompose**. The real `autoregulation_engine.py` / services are plain synchronous Python.
"A real `combine` that subscribes to N flows" describes the sandbox's fictional reactive runtime — a
paradigm PC discarded — not anything the real PC app needs.

## Corrected scope — what's actually NOT done

The expensive non-UI layer is **already built** (and the audit's ~30% in log_30 was VM-feature/screen
*surface* parity — a different axis from the domain layer, which is far more complete). What remains
for "more of WFL in PC" is mostly:
- **UI screens** for deferred features (Tier 3 -> the kit, hand-built);
- **ViewModels** for those features, wired to PC's **existing** synchronous services.

That is Path C, and PC already does exactly this by hand. The domain rebuild that log_44/45 implied is
not remaining work — it's done.

## What this means for the transpiler experiment

It has been operating in a sandbox **disconnected from the real, complete PC app** — re-deriving WFL
ViewModels in a Flow paradigm against fake shims, while PC already has the entire non-UI layer
hand-built in a synchronous paradigm. To plug transpiled VMs into the real app you'd have to convert
them off flows into PC's synchronous discipline — at which point it is what PC's hand-port already
produces. I'm not going to overstate the strategic conclusion having just been wrong about the facts,
but the user's instinct ("the non-UI stuff is already solved") is correct, and it materially changes
the fork in log_43: Path B's domain cost is largely already paid.

This log supersedes the domain-scope claims in log_44 and log_45. Those are wrong; this is measured.

Pointers (verifiable): `WFL_PseudoCoup/src/engine/autoregulation_engine.py` (1224 LOC),
`WFL_PseudoCoup/src/domain/`, `WFL_PseudoCoup/src/data/`; vs `PseudoCoup/core/` (the empty sandbox I
mistakenly measured).
