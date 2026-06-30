# log_134 — render remainders (9 screens), root causes

Render is **20/29** screens. This logs the **9 that don't render**, each with its actual error, the
confirmed cause, and the fix. Headline: **none of the 9 is a translation bug** — every file compiles
(254/254) and loads (87/87), so the generated Python is valid; all 9 fail at *run* time, inside the
render harness or an empty wrapper.

Terms used below:
- render harness — the test that calls a screen function and counts the UI-tree nodes it emits.
  It is `compose.render` plus `_composable.make` in `tools/pseudokotlin/runtime/compose.py`.
- content slot — a lambda that builds child UI: `content=`, `title=`, `text=`, `label=`.
- event handler — an `on…`-named lambda that runs on user action: `onClick=`, `onValueChange=`, `onDone=`.
- state stub — what `remember { mutableStateOf("") }` becomes today: an inert stand-in whose `.value`
  reads back as another stub (no real Compose state yet).

---

## Group 1 — harness fires event handlers (6 screens)

Screens: `GymEditorScreen` · `ProgramDayEditorScreen` · `ProgramEditorScreen` · `ProgramsScreen`
· `TodayScreen` · `WinsListScreen`

- error (example): `AttributeError: 'NoneType' object has no attribute 'strip'`
  @ `ui/programs/ProgramsScreen.py:129`
- cause: `_composable.make` calls **every** callable keyword argument, not just content slots —
  `runtime/compose.py:65-67`. So an event handler runs during a static render. The chain in
  `ProgramsScreen`:
    - `name = remember((lambda it=None: mutableStateOf("")))`        — `ProgramsScreen.py:121` (a state stub)
    - `onValueChange=_lam42`, where `_lam42` is `name.value = it`     — `ProgramsScreen.py:126-127`
    - the harness calls `_lam42()` with the default `it=None`         → `name.value` is now `None`
    - `enabled=(len(name.value.strip()) != 0)` then reads it          — `ProgramsScreen.py:129` → crash
- not: a transpiler bug (the Python is correct), not an empty wrapper (the state stub returns a stub,
  not None — the None is written *by the harness calling the handler*).
- fix: in `_composable.make`, skip `on…`-named callable kwargs (they are events, not content).
  Content slots still render.
- verified: with that skip, render goes **20/29 → 26/29** — all 6 recover. Patch tested in-memory,
  not yet committed.

## Group 2 — a platform stub is missing an attribute (2 screens)

Screens: `DebugPanelScreen` · `SettingsScreen`

- error: `AttributeError: type object 'ActivityResultContracts' has no attribute 'CreateDocument'`
  @ `ui/debug/DebugPanelScreen.py:11`, `ui/settings/SettingsScreen.py:12`
- cause: `ActivityResultContracts` is a *blessed* platform stand-in (a real no-op class, not the
  permissive autostub Stub), so reading an attribute it doesn't define raises instead of yielding
  another stub.
- not: a transpiler bug. The transpiled `ActivityResultContracts.CreateDocument(...)` is the right
  shape; only the stand-in is too strict.
- fix: make that blessed stand-in permissive (yield a stub on any attribute), like the autostub Stub.
- verified: not yet (small; expected +2).

## Group 3 — renders, but thin (1 screen)

Screen: `HistoryScreen`

- symptom: renders fewer than 3 nodes (the harness's floor for "rendered").
- cause: not yet diagnosed — needs a look at what the screen emits under stub inputs.
- fix: TBD after diagnosis.

---

## Roll-up

| group | screens | confirmed cause | fix | verified |
|---|---|---|---|---|
| 1 | 6 | harness fires `on…` event handlers during render | skip `on…` kwargs in `_composable.make` | yes → +6 (26/29) |
| 2 | 2 | blessed `ActivityResultContracts` stand-in too strict | make it permissive | no (expect +2) |
| 3 | 1 | thin render, undiagnosed | TBD | no |

If groups 1 and 2 land: **28/29**. Group 3 is the only one needing investigation.

None of the 9 is transpiler work. The transpiler side is green (parse 254/254, load 167/167 + 87/87,
oracle 11/11, data 4/4, 0 grammar kinds unrouted); these remainders live in the render harness and the
platform stand-ins.
