# WFL → PseudoCoup — Progress Dashboard

Living status tracker. Complements `PROJECT_MAP.md` (which says **where** things live); this says
**what's done** and **what's next**. Update every working session.

**Last updated:** 2026-06-28 (PseudoUI generator + Kt→Py transpiler fixes thread; status reconciled
against log_96's track framing).

**Legend:** ✅ done/verified · 🟡 in progress · 🔵 backlog (wanted, not started) · ⏸️ deferred by plan ·
⬜ not started · ❓ unknown · ⛔ blocked

---

## The pipeline at a glance

```
WFL (Kotlin, SOURCE OF TRUTH)
   │  (A) Kt → Py transpiler  (1:1, "map·wrap·fail", everything traces to Kotlin)
   ▼
WFL Python (canonical 1:1)                         [WFL_MixingCenter]
   │  + the kit (imperative zone API) + screens (PseudoUI) + reactivity (State/recompose)
   ├─ (B1) Py → Dart  [PseudoDart] · kit = PseudoFlutter  ▶  WFL_PseudoCoup (Kivy + Flutter app)
   └─ (B2) Py → Haxe  [PyHaxe]     · kit = PyHaxeUI        ▶  WFL_PyHaxe
```

---

## The three tracks (the project's own framing, from log_96)

| Track | What it is | Status | The number that matters |
|-------|------------|:------:|-------------------------|
| **Track B** — transpiler center | Kt→Py of the whole app + verification ladder. **The documented current priority.** | 🟡 | WFL_MixingCenter (parse-clean 192/254) is STALE `literal_transpiler` output. Measured via the canonical **KtToPy**: repositories **20/20 parse**, **19/20 construct (DI)**, **16/20 run real methods** (log_126→128; was 14/20 before the Flow-operator shim) — vs literal_transpiler's ~1/20. 2 transpiler bugs FIXED + reactive shim now flow-operator-complete (oracle 11/11). gym_list's vertical runs on the **transpiled GymRepository** end-to-end (log_127 swap-under). Runnability ≠ correctness (oracle's separate ladder). |
| **Track A** — hand-built UI | ~30 screens hand-written on the kit (NOT transpiled). The mature baseline. | ✅ | ~30 screens; "65/65" = Track A's hand-built **assertion/coverage** count (NOT the 36 golden PNGs — those are the current visual baseline) |
| **Bucket 3** — PseudoUI swap-in | Make the literal WFL Python a *runnable app*: wire screens onto the kit + reactivity. **Officially deferred until non-UI closes.** | ⏸️→🟡 | gym_list is a complete generated drop-in (this session). **This is the deferred bucket — see the sequencing note below.** |

> ⚠️ **Sequencing reality (confirmed by probe, log_124):** the breadth work is genuinely *ahead of the
> foundation*. A generated screen binds to a transpiled VM but runs on the **hand-built** domain
> (`src/domain`) — because the **transpiled** domain (`WFL_MixingCenter`) does NOT run: it parses but
> 79% of files have unresolved imports, 19/20 repos dropped their DI constructors, and runtime modules
> are missing. So "192/254" is parse-clean scaffolding, not a runnable backend. The real ceiling is the
> **parse-clean → runnable jump** (restore DI, resolve imports, supply runtime, Room→DB boundary) — not
> more UI. UI breadth is valid as *mechanism-proof* but cannot trace end-to-end until that floor is real.

---

## Component status

| Component | Status | Where it stands | Proof / how to check |
|-----------|:------:|-----------------|----------------------|
| **Kt→Py transpiler** | 🟡 | `tools/pseudokotlin` (**KtToPy** = canonical/active; oracle uses it; all recent work). `tools/transpiler/literal_transpiler.py` = the original **donor** KtToPy was ported from (superseded, not retired; may still drive the 254-file batch seed — one residual ambiguity). 4 real bugs fixed this session. | `oracle.py --all` → ALL GREEN 11/11 engines |
| — verification ladder | 🟡 | compile-clean → oracle (runtime equiv, 11 engines) → fuzz (5000 cases, 0 div) → ledger (structural + UI). UI ledger **geometry layer** NOT built. | `oracle.py`, `fuzz.py`, `ledger.py`, `ui_ledger.py` |
| **The kit** (PseudoFlutter) | ✅ | Imperative zone API; Kivy (`kit.py`) + Flutter (`kit.dart`) backends; both retained-mode. | app smoke 30/30 |
| **Reactivity** (State/recompose) | ✅ (coarse) | Works; false-reactive = redraw-whole-screen per event. Correct, not efficient. | log_121; `reactive.py` |
| **Py→Dart** (PseudoDart) → Flutter | ✅ | `WFL_PseudoCoup/tools/transpile.py` → `app_flutter/lib`; **36 golden PNGs** (31 sweep + execution variants + demo). | `flutter test` from `app_flutter/` |
| **Py→Haxe** (PyHaxe) → WFL_PyHaxe | 🟡 (old) | **WFL_PyHaxe is older/partial — no viewmodel layer**, 580 `.hx`, last touched 2026-06-19; dormant for the main app port. PyHaxe transpiler more active but aimed at other reference targets. | `WFL_PyHaxe/DevComms/SESSION_STATUS.md` |

---

## PseudoUI generator — detail (this session = Bucket 3, logs 104–122)

| Layer | Status | Note |
|-------|:------:|------|
| Structure (Compose → kit `define_*`) | ✅ | 99% leaf coverage, 0 fabricated/orphan across 24 screens (log_105) |
| Control-flow IR + bind to TRANSPILED viewmodel | ✅ | `--1to1`/`--auto`; per-screen binding is mechanical Kt→Py (logs 106–108) |
| Generality (2nd/3rd screens) | 🟡 | paths 3/3, exercise_detail 4/5, exercise_picker renders 185 (logs 109–115) |
| Int→enum lift + emit runnable + representation map | ✅ | complete match on gym_list/paths (logs 110–113) |
| Vendored, routed by AppRouter, handlers, re-render fix | ✅ | logs 117–120; smoke 30/30 |
| **Net: gym_list = complete interactive drop-in** | ✅ | `WFL_PseudoCoup/tools/test_gym_list_gen.py` — 10/10 render + 4 handlers + re-render |

**Per-screen cost for the NEXT generated screen:** a DAO adapter + a nav map (~10–20 lines) +
`MutableStateFlow → State` for UI-flag screens. Everything else (IR/emit/transpiler) is screen-agnostic.

---

## Backlog (wanted, not started)

- 🟡 **Breadth** — 2nd interactive drop-in (exercise_detail). General mechanisms DONE: `MutableStateFlow → State` (log_123), nav map (log_129), **SharedFlow-mediated nav** (log_130, edit-nav fires via `vm.editCurrent()`). Remaining = PER-SCREEN: adapter methods for `delete`/`onToggleExcluded` repo calls, IR capture of the `excludePrompt?.let` AlertDialog, then vendor/route + swap-under the transpiled ExerciseRepository.
- 🔵 **Depth** — Python→Dart of the generated screen for Flutter PIXEL goldens (its runtime isn't Dart-transpilable yet).
- 🔵 **Efficient near-true-reactivity** (reconciled redraw) — kit-only, correctness-preserving, deferred (log_122).
- 🔵 **UI ledger geometry layer** (rendered-box diff; ground truth = original app via `WFL_PseudoCoup/tools/dualtrace`).
- 🔵 **Close Track B** — the `.dp`/`.sp` unit-literal blocker + the 62 failing files (the documented critical path).

---

## Resolved this update (were "open questions")

1. ✅ Canonical transpiler = **KtToPy** (`tools/pseudokotlin`); `literal_transpiler.py` is its donor.
2. ✅ Compile-clean = **192/254** (non-UI 162/167); no fresher run since 2026-06-26/27.
3. ✅ Haxe = **older/partial, dormant** (no VM layer, last 2026-06-19).
4. ✅ "65/65" = Track A assertion count, **not** the 36 golden PNGs.
5. ✅ "Python→PseudoCoup discipline" is **not a named stage** — it's **Bucket 3** (PseudoUI swap-in), officially deferred until non-UI closes.

**Still genuinely open:** does the 254-file batch seeder (`transpile_app.py`) still call `literal_transpiler`, or has it been repointed to KtToPy? (Minor; check if it matters.)
