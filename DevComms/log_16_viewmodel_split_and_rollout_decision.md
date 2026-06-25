# log_16 — the ViewModel split: pilot done, and the rollout decision (transpiler vs hand-port)

Date: 2026-06-25
Type: decision support. The per-screen ViewModel split is agreed and piloted; this records the
finding that changes HOW to roll it out, with the evidence, so the call is made on facts.

## Bottom line

1. **Decided + piloted.** PseudoCoup will adopt the Compose split it had fused away: a stateless
   screen (rendering) + a stateful per-screen **ViewModel** (state + actions). `report_bug` is
   ported and verified end-to-end; committed `a750aef`.
2. **The rollout finding.** The other 29 ViewModels are NOT plain classes — they are reactive
   (`MutableStateFlow`/`combine`/`stateIn`) and logic-heavy (up to 1311 lines), and there is **no
   Kotlin→Python logic transpiler** (the 39 services were hand-ported; the ingest tool only
   recovers UI *structure*). So "transpiler-first" for the VMs is a major build, not a quick win.
3. **The reframe that matters.** The fidelity payoff (resolving the ~551 screen→ViewModel flags)
   comes from the vms EXISTING and the screens being WIRED — not from the transpiler. Hand-porting
   the vms gets the same payoff.
4. **Recommendation: hand-port the 30 vms in parallel waves** (the proven method — how the services
   and report_bug's vm were built), simple→complex. The transpiler is an optional, partial-payoff
   detour. Decision is yours; options + tradeoffs below.

## Why the split (recap from the discussion)

Compose UI is functions; the classes live behind it — one **ViewModel** per screen (30 of them,
each via `hiltViewModel()`, scoped to the nav destination) holding that screen's state + actions.
PseudoCoup fused state+logic+rendering into one screen class. Of the transpiler's flags across all
30 generated screens, **~97% are the screen reaching across to its ViewModel**:

```
screen ↔ ViewModel / state / nav   (the wiring seam)
    state reads   (viewModel.state.X)               132
    state lists   (a runtime collection)            275
    actions / nav (onClick → a ViewModel method)    144     = 551
view-structure    (a Compose element with no map)    19
```

PseudoCoup deleted that seam, so those 551 reaches had no target and were hand-wired or omitted
(e.g. the notification badge — `appViewModel.unreadCount`). Give PC the ViewModels and they land.

## The pilot (report_bug) — proven, committed `a750aef`

`src/viewmodel/report_bug_view_model.py` mirrors the Kotlin `ReportBugViewModel` field-for-field
(state + actions, pure — no kit, no router); the screen reads it and remounts after an action.

```
Python smoke      30/30 build (seeding intact)
vm prefill        reporter_name = 'Tester'   (the SEEDED user — proves load() runs post-seed)
transpile → Dart  viewmodel_report_bug_view_model.dart emitted clean (143 modules)
flutter analyze   0 errors  (the new vm file: 0 warnings)
```

**One pattern emerged that applies to every vm — `load()`.** PseudoCoup constructs every screen
(now every vm) at router-startup, BEFORE the DB is seeded. A vm that fetches in `__init__` creates a
default user and makes the app seed skip the real one — breaking seeding app-wide. So the vm's data
fetch is deferred to `load()`, called once from `build()`. This is faithful to Compose anyway (a
ViewModel loads on screen-enter, not at construction).

## The finding, with evidence

### These vms are reactive + logic-heavy

Sizes (lines), a slice of the 30:

```
GymListViewModel             32     (simplest)
PathsViewModel               88
ReportBugViewModel           94     (the pilot — atypically simple)
GymEditorViewModel          112
ProgramEditorViewModel      316
OnboardingViewModel         516
TodayViewModel              707
WorkoutExecutionViewModel  1311     (largest)
```

State idioms across the 30: **81 `MutableStateFlow`, 28 `combine(`, 18 `stateIn(`** — only **2 of
30** use a `data class UiState` like report_bug did. The dominant shape is reactive flows that fuse
repo data with UI state. Example — `PathsViewModel`:

```kotlin
val activePaths = repository.activePaths.stateIn(scope, …, emptyList())   // derived from a repo flow
private val _pickerState = MutableStateFlow<PathPickerState?>(null)        // mutable UI state
fun togglePathSelection(pathId: String) {                                  // REAL logic:
    _pickerState.update { state ->
        val maxAllowed = if (state.isAddingSecond) 1 else 2                //   set-ops + when-branches
        val updated = when { pathId in selected -> selected - pathId; … }
        state.copy(selectedPathIds = updated)
    }
}
fun enrollAndFinish() { … selectedPathIds.forEach { repository.enroll(it, …) } … }  // loop + repo calls
```

`activePaths`/the setters are mechanical; `togglePathSelection`/`enrollAndFinish` are real logic.

### There is no Kotlin→Python logic transpiler

- The **ingest** tool (`tools/ingest`) recovers UI *structure* and FLAGs logic — it does not
  transpile method bodies.
- **PseudoDart** transpiles Python→Dart (forward), not Kotlin→Python.
- The **39 domain services** in `src/domain/` are **hand-written** disciplined-Python ports (see the
  porting-decisions docstring in `user_service.py`), not auto-transpiled.

So auto-transpiling the vms means transpiling arbitrary Kotlin statement/expression logic to Python
— a tool that does not exist. A *weak* vm transpiler could scaffold the state-shape + setters +
`load()` and FLAG every real method body: roughly **90% auto for a simple vm (report_bug), ~20% for
Today/WorkoutExecution.**

## The decision

The destination is the same in all three — vms exist, screens wired, the 551 flags resolve. They
differ in how the vms are produced:

```
(a) HAND-PORT, parallel waves  — mirror each Kotlin vm → a PC …ViewModel, wire its screen, verify.
    proven (= how the 39 services + report_bug went). parallelizes across sub-agents like the
    earlier reconciliation waves. no tooling detour. RECOMMENDED.

(b) WEAK VM TRANSPILER first    — auto-scaffold state-shape + setters + load(), FLAG the logic;
    hand-fill the flags. saves boilerplate on simple vms, ~20% on the big ones; adds a tool to
    build/maintain. partial payoff.

(c) FULL LOGIC TRANSPILER       — a real Kotlin→Python statement/expression compiler. largest build
    by far; would also benefit future ports. not justified by 30 one-off vms.
```

Recommendation: **(a)**. The proven method, lowest risk, same fidelity payoff, and the per-screen
logic is exactly the kind the project already hand-ported successfully. I'd run simple→complex,
supervise each wave, and halt if a vm comes out significantly off.

## Also in scope (one extra piece)

`AppViewModel` — the single app-scoped vm (notifications/`unreadCount`, crash prompt, celebration,
onboarding gate). Minority industrial pattern, but WFL uses it and it backs the notification badge
PC is currently missing. One shared instance the router owns and hands to screens (like `db`).
Folds in as one item; gives the badge for free.

## Pointers

- pilot: `WFL_PseudoCoup/src/viewmodel/report_bug_view_model.py`, `src/ui/report_bug_screen.py` (commit `a750aef`)
- the 551-flag breakdown + transpiler boundary: log_15
- Kotlin vms: `~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/**/*ViewModel.kt`
- hand-port reference (how the logic layer was built): `src/domain/user_service.py` docstring
