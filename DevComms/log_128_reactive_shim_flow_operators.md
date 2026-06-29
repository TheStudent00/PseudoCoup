# log_128 — reactive shim: pull-model Flow operators (foundation runtime coverage)

Date: 2026-06-28
Type: feature (runtime-shim coverage). Follows log_126's finding that the 14→20 runnable gap was
runtime-shim coverage, not transpiler bugs.

## What

The reactive shim's `Flow`/`StateFlow` only had `stateIn`/`collectAsState`/`value`/`first`. Real WFL
VMs and repositories use Flow OPERATORS: `flatMapLatest` (19 uses), `map`/`filter` on flows,
`distinctUntilChanged` (6), `take`/`drop`/`debounce`, `collectLatest`, `mapLatest`, `onEach`. Added a
`_FlowOps` mixin to BOTH shims (vendored `reactive_shim` + `pseudoui_run` sandbox), plus
`StateFlow.update` and module-level `flowOf`/`emptyFlow`.

## Semantics (honest)

Pull-model approximations (no backpressure / timing): `map`/`mapLatest`/`flatMapLatest` transform the
LATEST emission; `filter` yields the value or None; `distinctUntilChanged`/`take`/`drop`/`debounce`/
`flowOn`/`catch` are identity (a pull always reads the latest value); `collect`/`collectLatest` run
`f(latest)`. Enough to RUN flow-chaining VMs; not a faithful streaming model.

## Verified

- no regression: gym_list **5/5** (`test_gym_list_gen`), smoke **30/30**, `--app` **10/10**,
  exercise_detail `--auto` 8 shared.
- runnable-domain re-measure (real shim Flow + Flow-returning stub DAOs): **CONSTRUCT 19/20** (was 17),
  **RAN ≥1 method 16/20** (was 14).

## Net

The reactive shim is now flow-operator-complete enough for the real VMs/repositories — a prerequisite
for swap-unders beyond gym_list. Runnable-domain floor: **16/20 repositories run**, up from 14/20.
