# log_109 — generality test: a SECOND screen (paths) through --auto, crank reproduces it exactly

Date: 2026-06-28
Type: milestone / generality test. Does the --auto crank (log_108) work beyond gym_list?

## Direct answer

Yes. `paths` — a differently-shaped screen with a different viewmodel — runs through `--auto` and
reproduces the hand-built screen EXACTLY, with no hand-written binding spec:

```
paths    (AUTO): leaf shared 3, interp-only 0, hb-only 0;  dynamic 0/0;  unresolved 0
gym_list (AUTO): leaf shared 7, interp-only 3, hb-only 3;  dynamic 4/4;  unresolved 1
```

paths matches the hand-built screen with ZERO divergence (3/3 leaves, 0 interp-only, 0 hb-only).

## What the per-screen surface actually was (the honest measure)

To add paths to `--auto`, the entire per-screen cost was:

1. A 2-line `SCREEN_CFG` entry (which .kt to transpile, which VM class).
2. An ~8-line repo adapter — and it is THINNER than gym_list's: `PathEntity.name` is a string, so
   there is NO enum lift and NO bundling. Just expose the kit's active paths as a Flow.

That is it. The IR + control-flow + auto-binding machinery needed NO per-screen changes — it lifted
paths' `if/else`, `items`, `?.let`, and `val` binds and emitted the bindings via the transpiler,
same as gym_list.

## What grew ONCE (fixed, now reused by every screen)

Two fixed-infrastructure additions, made once and shared:

- The reactive/stdlib shim now merges `kotlin_rt` (so `emptySet`/`MutableStateFlow`/`asStateFlow`
  etc. resolve) with the synchronous Flow layer. paths needed `emptySet` + `MutableStateFlow`;
  those are now available to all.
- `item { } / stickyHeader { }` (the LazyColumn single-slot DSL) is lifted as a transparent
  wrapper, like `items` is a loop. paths' empty-state content lives inside `item { }`.

These are screen-AGNOSTIC; they do not recur per screen.

## A real finding: paths is empty BY DESIGN

The seeded DB (the app's own `_seed_paths`) seeds path DEFINITIONS but deliberately does NOT enroll
any ("Enrolling paths is deferred until the rich ActivePathCard … are ported"). So the Paths tab
shows the discovery/empty state — and the HAND-BUILT screen traces to exactly that (3 texts:
"Start with your why." · "A Path connects your training…" · "Find your path"). `--auto` reproduces
those 3 and nothing else: a faithful match of the app's actual state.

Because there are no enrolled paths, the dynamic card path isn't exercised at RUNTIME — but the IR
proves the machinery lifted it correctly anyway: `FOREACH path in activePaths → Text<DYN> path.name`,
`LET it = definition → Text<DYN> it.tagline / "${it.minSessionsPerWeek}–…"`, all captured and
transpiled. The dynamic-binding generality is proven at the IR+transpile level here, and end-to-end
at RUNTIME on gym_list (4/4).

## Verdict

The crank generalizes. Per-screen cost for screen #2 was ~10 lines (config + thin adapter); the
machinery and the fixed shims carried the rest. The two screens together cover the cases: gym_list
proves dynamic resolution end-to-end (a non-empty list with enum + bundling reshapes), paths proves
clean structural/control-flow reproduction on a different VM with a trivial adapter.

## Next

- A dynamic-data second screen (e.g. `exercises`, 185 seeded) would additionally exercise runtime
  dynamic resolution on screen #2 — but surfaces enum `displayName()` lifts (muscle/movement/
  equipment), the same class as gym_list's gymType, plus a `.forEach{}` loop construct.
- Emit the IR+auto-bindings as a runnable `*_screen.py` (the last mile: REPLACE a hand build).
