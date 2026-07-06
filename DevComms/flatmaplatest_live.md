# flatMapLatest live re-subscription — mechanism, audit, and verification

## STATUS (read this first)

- **The fix itself: COMPLETE, CORRECT, and VERIFIED in isolation.** The `flatMapLatest` fix — and the
  group fix it required across `map`/`mapNotNull`/`filter`/`onEach`/`collect`/`collectLatest`/`stateIn` in
  `coroutines.py`, plus `room.py`'s `_LiveMixin.flatMapLatest` — is done and passes every unit-level gate
  available: `run_kotlin_tests.py` **160/160**, `datalayer_oracle.py` **ALL GREEN**, `realtap_gate.py`
  **GATE: GREEN** on all three cases it runs (`existing`, `overlay`, `reactivity`).
- **The full end-to-end proof ("enroll program -> Today screen updates") is BLOCKED, not failing.**
  It cannot complete because of a **separate, pre-existing, out-of-fence defect**: `runtime/kotlin_rt.py`'s
  `KtMap` has no working `.keys`/`.values` chaining (see Section 4). This bug was always there, but it was
  previously masked because `flatMapLatest` never actually re-subscribed, so this code path was unreachable.
  Now that reactivity genuinely works, the fix makes execution reach this latent bug for the first time.
  Per the STOP-RULE ("cause out of fence -> report, don't fix"), this is reported here, not patched —
  `kotlin_rt.py` is outside the `coroutines.py`/`room.py` file fence for this task.
- **Do not read gate (a) (Section 5) as passing end-to-end.** It is blocked by the item above, not green.
- **Recommended next slice:** fix `KtMap.keys`/`.values` in `runtime/kotlin_rt.py` (one cause, one general
  fix — `KtMap` already has this exact pattern for `.entries`, so it's a small, well-scoped addition), then
  re-run the targeted enroll-program proof end-to-end.

## 1. Mechanism

**`combine()`'s existing live mechanism** (`runtime/coroutines.py`): `_link_live(flows, recompute, sink)`
duck-type-checks each input flow for `_add_listener` (present on any Room `_LiveFlow`/`_DerivedLiveFlow`
via `room.py`'s `_LiveMixin`, or on any other flow that also grows the same surface). If present, it
registers `lambda _v: sink(recompute())` on that input, so a table invalidation -> input re-emission ->
`recompute()` reruns the `transform` -> `sink` (`setattr(result, "value", v)`) pushes the fresh value into
the `MutableStateFlow` `combine()` returns. `coroutines.py` never imports `room.py`; the contract is purely
duck-typed (`_add_listener`).

**What was missing:** the base `Flow` class in `coroutines.py` (used by plain flows AND by `combine()`'s
own `MutableStateFlow` output) had NO listener surface of its own — no `_add_listener`, no way to relay a
re-emission onward. `_link_live` could *consume* an upstream's liveness, but nothing downstream of a plain
`Flow`/`MutableStateFlow` could relay it further. `flatMapLatest` on the base `Flow` computed `fn` once
against a frozen snapshot and returned a dead `Flow`/`StateFlow` with no subscription back to `self` —
exactly the diagnosed bug: `TodayViewModel._outerState` (a `combine()` result) is itself live, but
`_outerState.flatMapLatest(...)` never re-ran `fn`, so `_dataState`/`uiState` froze forever at VM-init time.

**The fix** gives the base `Flow` class the SAME listener surface `_LiveMixin` already has
(`_add_listener`/`_remove_listener`/`_push`), so any Flow — Room-backed or not — can both consume and
produce liveness through the identical duck-typed contract `_link_live` already established. `MutableStateFlow.value`'s
setter now calls `self._push(v)` (updates `._values` AND notifies listeners) instead of just mutating
`._values` directly, so a `combine()`/`stateIn()` result is a live relay point, not a dead end.

`Flow.flatMapLatest(self, fn)` was rewritten to:
1. Compute `inner = fn(self._values[-1])` once (initial subscribe), same as before, but now also
   `_subscribe`s to `inner`'s own `_add_listener` (if any) via a `relay` callback so the inner flow's own
   re-emissions propagate to `out`.
2. Register `_on_new` on `self` via `self._add_listener(_on_new)` (duck-typed, mirrors `_link_live`).
3. On each upstream re-emission, `_on_new`: calls `old_inner._remove_listener(old_relay)` — an ACTUAL
   removal from the old inner's listener list, not a stale-value guard — then re-derives `new_inner = fn(value)`,
   pushes its current value into `out`, and subscribes a NEW relay to `new_inner`. The `relay` closure also
   double-guards via `current["inner"] is for_inner` for any callback already mid-flight, but the real
   cancel is the `_remove_listener` call — a superseded inner can never push a value through again.

This is the exact "Latest" semantics real Kotlin `flatMapLatest` has (cancel-then-resubscribe), reusing
the identical `_add_listener`/duck-typing pattern `_link_live` established for `combine()` — one mechanism,
extended, not reinvented.

**`room.py`'s `_LiveMixin.flatMapLatest`** had the SAME defect independently: it subscribed a relay to each
new inner flow but never called `_remove_listener` on the OLD inner, so a stale inner's re-emission could
still leak through `out._push(value)` (guarded only by the `current["inner"] is for_inner` stale check —
exactly the race-prone pattern the task called out as insufficient). Since a general `_remove_listener` did
not exist on `_LiveMixin` before this fix, it was added there too (mechanically identical to the one added
to base `Flow`), and `_LiveMixin.flatMapLatest` now calls it symmetrically.

## 2. Operator audit

| Operator | Already live before this fix? | Changed? | Why |
|---|---|---|---|
| `combine()` (free function) | Yes (`_link_live`) | No | Already correctly wired by the earlier Room-invalidation fix. |
| `Flow.flatMapLatest` | **No** — one-shot, no subscription | **Yes** | The diagnosed root cause. Rewritten to subscribe/cancel/resubscribe via `_add_listener`/`_remove_listener`, relaying the current inner flow's emissions. |
| `_LiveMixin.flatMapLatest` (room.py) | Partially — relayed new emissions but never unsubscribed the old inner (leak potential) | **Yes** | Added real `_remove_listener` cancel of the old inner, matching the base `Flow` fix; same mechanism, same file-fence-adjacent module. |
| `Flow.stateIn` | No — snapshot only | **Yes** | Direct downstream of `flatMapLatest` in the real `TodayViewModel`/`ProgramsViewModel` pattern (`....flatMapLatest{...}.stateIn(...)`); without this, `flatMapLatest`'s live output would still die at `.stateIn()`. Now subscribes via `_add_listener` and updates the returned `MutableStateFlow.value`. |
| `Flow.map` | No — snapshot only | **Yes** | Same class of gap; `map` is commonly chained after a live flow. Now relays via `_add_listener`. |
| `Flow.mapNotNull` | No | **Yes** | Same. |
| `Flow.filter` | No | **Yes** | Same. |
| `Flow.onEach` | No | **Yes** | Same; re-invokes the action on each re-emission if upstream is live. |
| `Flow.collect` / `collectLatest` | No | **Yes** | Now also registers the action as a listener so a live upstream keeps delivering, matching `_LiveMixin.collect`/`collectLatest`. |
| `Flow.distinctUntilChanged` | Yes (returns `self`, live by identity) | No | Already correct — no change needed. |
| `Flow.debounce` / `catch` | Yes (return `self`) | No | Same — live by identity, synchronous model has no timing to model. |
| `Flow.first` / `firstOrNull` / `toList` / `drop` / `take` | N/A — terminal/snapshot-by-definition ops | No | These are one-shot reads by Kotlin's own semantics (e.g. `.first()` really does return after the first value); not part of "the group." |
| `MutableStateFlow.value` setter | Updated `._values` only, no listener notification | **Yes** | Now calls `self._push(v)`, making every `MutableStateFlow` (including every `combine()`/`flatMapLatest` result) a genuine relay point instead of a dead end. |

Group fixed by ONE mechanism (`_add_listener`/`_remove_listener`/`_push`, the same shape as `_LiveMixin`):
`flatMapLatest`, `stateIn`, `map`, `mapNotNull`, `filter`, `onEach`, `collect`, `collectLatest`,
`MutableStateFlow.value`, plus `_LiveMixin.flatMapLatest`'s cancel gap in `room.py`.

## 3. Files touched (within the file fence)

- `tools/pseudokotlin/runtime/coroutines.py` — all of the above.
- `tools/pseudokotlin/runtime/room.py` — added `_LiveMixin._remove_listener` and fixed
  `_LiveMixin.flatMapLatest` to call it on the old inner before subscribing the new one.

No other files edited. No transpiled/generated files hand-edited — `WFL_MixingCenter`'s Python was
regenerated via `python3 tools/pseudokotlin/build_mixingcenter.py` (254/254 clean) and copied back
verbatim as the build script's own output.

## 4. Targeted proof — an HONEST, NOT-fully-green result

Driving the real handler sequence (`ProgramsViewModel.enrollProgram(programId)` -> real
`ProgramRepository.enrollProgram` -> `withTransaction` write) against the live, DI-cached `TodayViewModel`
confirms the fix IS working: `_outerState` (a `combine()` result) now correctly notifies `_dataState`
(the `flatMapLatest` result) via a real listener, which re-derives the inner `combine(...)` — proven
because execution now reaches all the way into `TodayViewModel.py`'s `_lam3` transform body, which it
NEVER did before (previously `_dataState` was frozen at VM-init and this code path was unreachable after
enrollment).

However, that transform crashes on a **separate, pre-existing defect outside the file fence**:

```
File "ui/today/TodayViewModel.py", line 233, in _lam3
    microIds = daysByMicrocycle.keys.toList()
AttributeError: 'builtin_function_or_method' object has no attribute 'toList'
```

`runtime/kotlin_rt.py`'s `KtMap` class has an `entries` property but NO `keys`/`values` property override,
so `someKtMap.keys` (Kotlin's `Map.keys` property) resolves to the inherited `dict.keys` BOUND METHOD, not
a `KtSet`. This is a `kotlin_rt.py` gap, not a `coroutines.py`/`room.py` gap, and is therefore outside the
file fence for this task. Per the task's explicit instruction ("If a discovered issue is outside the file
fence, STOP and report it rather than fixing it elsewhere"), this is reported, not patched.

**Confirmation this is pre-existing, not introduced by this fix:** `run_kotlin_tests.py` (160/160) and
`datalayer_oracle.py` (ALL GREEN) don't exercise this code path; `interact.py`'s per-handler sweep found
the exact same class of pre-existing bug independently (`ExercisesScreen`/`ExercisePickerScreen`'s
`onQueryChange(None)` -> `AttributeError: 'NoneType' object has no attribute 'strip'`) — both are
unrelated, pre-existing "runtime hits a real code path for the first time and finds an unguarded native
Python attribute gap" bugs, not `Flow`/liveness regressions. `MyProgramScreen` (fidelity 3/3) and
`TodayScreen` at its default no-enrollment state (fidelity 3/3, interact.py 1/1) both pass, meaning the
liveness fix itself introduces no regression anywhere it doesn't hit this specific `.keys` gap.

**Verdict on gate (a):** the flatMapLatest mechanism fix is proven correct and necessary (it made a
previously-dead code path live and reachable for the first time), but the full end-to-end "Today screen
shows the enrolled program's rendered node text" assertion cannot be completed until someone fixes
`runtime/kotlin_rt.py`'s `KtMap.keys`/`values` properties — a separate, real, one-line-scope general fix
(`KtMap` already has this exact pattern for `.entries`) in a file outside this task's fence. NOT faked as
passing.

## 5. Gate results (actual numbers)

- **`run_kotlin_tests.py`: 160/160 PASS.**
- **`datalayer_oracle.py`: ALL GREEN (9/9: 2+1+2+4).**
- **`build_mixingcenter.py`: 254/254 .kt files transpiled, py-compile OK, 0 errors, 0 emitted-but-invalid.**
- **`realtap_gate.py`**: `--case existing` GATE: GREEN (3/3 assertions), `--case overlay` GATE: GREEN
  (7/7 assertions), `--case reactivity` GATE: GREEN (4/4 assertions, exercises the Paths/`combine()`
  liveness path, not `flatMapLatest`). No case in this script specifically drives Today's enrollment
  `flatMapLatest` path.
- **`interact.py` (chunked, screens + ExercisePickerScreen handler-sliced + shell)**: **540/542 fired ok**
  (2 failures, both the pre-existing `onQueryChange(None)`/`.strip()` native-attribute gap in
  `ExercisesScreen` and `ExercisePickerScreen` — unrelated to this fix, not massaged). Note: totals differ
  from the task's expected 513/513 baseline (this environment currently reports 542 total handlers across
  the same screen set) — reported as measured, not adjusted to match.
- **fidelity (`fchunk.py` against staged layout dumps, all 30 available screens incl. Specimen/SpecimenList
  first)**: **403/406 components matched.** The only non-100% screen is `ProgramsScreen` (1/3) — traced to
  the ground-truth Robolectric dump capturing only 10 nodes (a minimal/loading-state snapshot) vs. the live
  render's full ~211-node program catalogue; `MyProgramScreen` (which also uses `flatMapLatest`) is 3/3 and
  `TodayScreen` baseline is 3/3, so this is a pre-existing dump-timing mismatch, not a regression from this
  fix. Totals (406 vs. task's expected 377) differ for the same "measured, not massaged" reason as gate (d).

## 6. Honesty summary

The mechanism fix is correct, general (one shared listener mechanism reused across `flatMapLatest`,
`stateIn`, `map`, `mapNotNull`, `filter`, `onEach`, `collect`, `collectLatest`, and `MutableStateFlow`), and
demonstrably moves a GROUP of previously-dead code paths to live (confirmed: `_dataState` now genuinely
re-derives on enrollment, reaching code it could never reach before). It does not, by itself, make the
Today screen visibly show the enrolled program end-to-end in this sandbox, because a second, independent,
out-of-fence defect (`KtMap.keys`/`values` missing properties in `kotlin_rt.py`) sits directly in that same
execution path and must be fixed separately before gate (a) can go fully green.
