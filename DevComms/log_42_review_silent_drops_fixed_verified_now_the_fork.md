# log_42 — review of log_41: verified good (not gamed). One latent bug, and we're now at the fork.

Date: 2026-06-25
Type: review (verified). Ran the gate + inspected output + checked against the Kotlin source and for
detector-gaming.

## Verified — all three findings genuinely fixed

Gate is legitimately **GREEN**: `compile 27/27 · rt-fatal 0 · silent-drops 0 · enum-refs 0 · exit 0`.
And it's real, not gamed:
- **Enums:** `ConditioningStage` now emits `SELECTING='SELECTING' · RUNNING · FINISHED` before `__init__`.
- **Lambda capture (finding #3):** `combine(self.programFlow, self.roadmapFlow,
  pathRepository.activePaths.map(_lambda_28).distinctUntilChanged(), _lambda_30).stateIn(...)` — the
  transforms are real `def _lambda_N`, captured in expression position. Spot-checked a body:
  `def _lambda_0(it=None): return it.day.id == dayId` — `it` bound, returns the value. Correct.
- **Not gamed:** zero `.map(None)` / `.map(__TODO_EXPR__)` — the gate wasn't passed by stubbing args.
- **Shim:** `Flow.map/.filter/.flatMapLatest/.stateIn` are now instance methods (resolves the
  free-fn-vs-method mismatch).
- **TODO 18 -> 46 is honest:** the drops became loud markers (unhandled-node / `__TODO_EXPR__`), not
  silence. Right direction.

Good work — this round is solid.

## One latent bug the gate can't catch (for when the Flow runtime lands)

`combine`'s transform is emitted **positionally** as the last arg, but the shim is
`def combine(*flows, transform)` — `transform` is **keyword-only** (after `*flows`). So
`combine(a, b, c, _lambda_30)` binds `_lambda_30` into `*flows` and leaves `transform` unset ->
`TypeError` the moment combine actually runs. It compiles, so neither py_compile nor the silent-drop
check sees it. 1-line shim fix (accept the transform positionally) when the Flow runtime work happens;
not urgent now since the shims don't execute yet.

## Where we actually are — the fork

The transpiler's **structure + expression layer is done enough**: 27/27 valid, instance-shaped, no
silent drops, enums present, lambdas captured. The residual 46 are bounded, loud, and visible.

What's left to reach "actually runs" is **not more expression handling** — it's two larger things:
1. **Domain-dependency stubbing.** The VMs import entities/enums/repositories/DAOs (and call
   `maxOf`, etc.) that don't exist on the Python side. Nothing instantiates end-to-end without them.
   Big surface (the whole `data/` + `engine/` layer), mostly mechanical.
2. **The real Flow runtime.** Make `combine`/`stateIn`/`map` actually carry data instead of returning
   inert `Flow()`. This is the option-(a) work — and it's **product-gated** (log_30/33).

Both loop back to the decision that's been open since log_30: **do we want to resurrect/extend WFL
through this transpile path, or was proving the mechanical mapping the goal?** The transpile
experiment has now answered the technical question it set out to — the VM-logic layer *does* map
cleanly to structurally-faithful, loud-about-gaps Python. Going further is a real build, not a
proof-of-concept, and it's worth a deliberate go/no-go rather than drifting into it.

No new work taken pending that call. Gate stays green; `run_all.py` is the regression guard.

Pointers: `tools/transpiler/run_all.py`, `core/flow.py` (combine signature), log_41 (impl), log_30/33
(the product decision this returns to).
