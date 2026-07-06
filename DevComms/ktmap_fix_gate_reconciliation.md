# KtMap `.keys`/`.values` fix — gate reconciliation report

## 1. What was wrong with KtMap, and the general fix

`tools/pseudokotlin/runtime/kotlin_rt.py`'s `KtMap(dict)` had `entries` as a real
Kotlin-flavoured property (`KtList(KtEntry(k, v) for k, v in self.items())`), but had
**no** `keys` / `values` property overrides at all. Kotlin's `Map.keys` (`Set<K>`) and
`Map.values` (`Collection<V>`) therefore fell straight through to the INHERITED `dict.keys`
/ `dict.values` — plain Python **bound methods**, not callable-chain wrapper objects. Any
transpiled code that wrote `someMap.keys.toList()` or `someMap.values.filter { … }` (the
idiomatic Kotlin `Map.keys`/`.values` PROPERTY access, never invoked with `()`) got a
`builtin_function_or_method` object with no `.toList`/`.filter`/`.map`/etc., and crashed
with `AttributeError: 'builtin_function_or_method' object has no attribute 'toList'`.

There is only ONE `KtMap` class in the runtime (no `KtMutableMap` subclass exists, so there
was nothing else to check for an incompatible override) — a single fix in the base class is
the complete, general fix, matching the runtime's existing wrapper convention where
`KtSet` (already used for `.toSet()`, `groupingBy`, etc.) is the Set-typed chain wrapper and
`KtList` is the general list/Collection-typed chain wrapper (already used exactly this way
for `Map.entries`, `Map.toList()`, `keysList()`, `valuesList()`).

### Before

```python
class KtMap(dict):
    def __missing__(self, k):           # Kotlin map[k] returns null for an absent key
        return None

    @property
    def size(self):
        return len(self)

    @property
    def entries(self):
        return KtList(KtEntry(k, v) for k, v in self.items())

    def isEmpty(self):
        ...
```

### After (only change — added two properties, nothing else touched)

```python
    @property
    def entries(self):
        return KtList(KtEntry(k, v) for k, v in self.items())

    @property
    def keys(self):                  # Kotlin Map.keys : Set<K> -- must chain like any KtSet
        return KtSet(dict.keys(self))

    @property
    def values(self):                # Kotlin Map.values : Collection<V> -- chains like a KtList
        return KtList(dict.values(self))

    def isEmpty(self):
        ...
```

`KtSet`/`KtList` are defined later in the same file, but the reference is resolved lazily
inside the property body at call time, so definition order is not an issue.

File touched (inside the file fence): `tools/pseudokotlin/runtime/kotlin_rt.py` only.
Regenerated the transpiled app via `python3 tools/pseudokotlin/build_mixingcenter.py` — no
transpiled/generated `.py` file was hand-edited.

## 2. The blocked proof — enroll a program, Today screen updates (RESULT: PASSED)

Ran the full app cold-start, settled via repeated `compose()` until node count stabilized,
enrolled a real program through `ProgramsViewModel.enrollProgram(programId)` (the real
handler `ProgramsScreen`'s "Join" button fires — not a synthetic/fake call), re-settled, and
inspected the actual rendered `Text` node content in the composed tree.

Command run (staged copy, from `/tmp/gh`):
```
HOME=/tmp/gh PYTHONUSERBASE=... xvfb-run -a python3 -u proof_today_flatmaplatest.py
```

Key output (`_lam3` — `daysByMicrocycle.keys.toList()` — no longer crashes):
```
== booting app namespace ==
   loaded 1388 top-level names
== building full app composition (AppNavigation) ==
settled node count: 42

== BEFORE enroll ==
today uiState.todayDayId: None
today uiState.weeklyRows count: 0
available program ids: ['prog_gup_3d_beg', 'prog_hyp_3d_beg', ...]

enrolling program: prog_gup_3d_beg  (via programs_vm.enrollProgram(programId))

== AFTER enroll (immediately, no extra recompose) ==
today_vm.uiState.value.todayDayId: day_gup_3d_beg_w35_d1
today_vm.uiState.value.weeklyRows count: 7

== re-settling the UI: recompose until node count stabilizes ==
node counts observed: [92, 92]

== AFTER enroll + settle ==
today_vm.uiState.value.todayDayId: day_gup_3d_beg_w35_d1
today_vm.uiState.value.weeklyRows count: 7

PROOF PASSED -- flatMapLatest live re-subscription: True
```

Followed up with a full text-node dump (using `node.text`, the actual Kotlin `Text(...)`
positional-string slot — not `node.props["text"]`, which the render layer never populates):

BEFORE enroll, visible texts included the placeholder:
```
["...", "This week's workouts", "Set up a program to see your week here.",
 "No program enrolled yet. Head to Paths to get started."]
```

AFTER enroll, the placeholder is gone, replaced by the real weekly schedule built from the
enrolled program's actual day data:
```
["...", "This week's workouts", "0 of 3 done", "Full Body A — Squat", "Day 1",
 "5 exercises · ~60 min", "Up next", "Rest day", "Day 2", "Full Body B — Hinge",
 "Day 3", "~60 min", "Rest day", "Day 4", "Full Body C — Push", "Day 5", "~60 min",
 "Rest day", "Day 6", "Rest day", "Day 7", "Start Full Body A — Squat"]
```

This is the enrolled program's ("3-Day Full Body — Ground Up") own day/session content
("Full Body A — Squat", "Full Body B — Hinge", "Full Body C — Push"), rendered live —
proof the KtMap fix unblocked the full `flatMapLatest`-driven reactive chain end-to-end,
not just at the ViewModel-state level (which the earlier `flatmaplatest_live.md` doc had
already confirmed) but all the way to the rendered node tree.

## 3. interact.py reconciliation — the 2 failures

Ran the full sweep via the chunk drivers (`chunk.py` per 5-screen slice, `hchunk.py` for
`ExercisePickerScreen`'s 211 handlers in slices of ~30, `shell.py` for the nav-bar shell).

**Both failures are the SAME root cause, both are the SAME class already flagged in
`selection_feedback_diagnosis.md`, and both are OUTSIDE the `kotlin_rt.py` fence:**

```
ExercisesScreen        total=9    -> 8 ok, 1 fail: onQueryChange -> AttributeError @ ExercisesViewModel.py:73
ExercisePickerScreen   total=211  -> 210 ok, 1 fail: onQueryChange -> same AttributeError class
```

Root cause, traced precisely: `interact.py`'s `infer_value(node, kind)` (the harness's
synthetic-argument chooser) only special-cases `onCheckedChange`/`onExpandedChange`/
`onSelectedChange`/`onCheckedChanged` and `onValueChange`/`onValueChangeFinished` — it does
NOT special-case `onQueryChange` (a `SearchBar`-specific value handler). For any kind not in
those lists, `infer_value` returns `_NOARG`, and `_invoke`'s arity-fallback sequence tries
`()` first (a shallow `TypeError`, since the real handler expects one positional arg), then
falls back to `(None,)` — which the real handler body accepts (no arity error) and then
crashes on `query.strip()` (`ExercisesViewModel.py:73`, and the equivalent line in
`ExercisePickerScreen`'s view-model) because `query` is `None`, not a string.

This is a gap in `render/interact.py`'s handler-arg-inference table, not in
`kotlin_rt.py`/`KtMap`. It is NOT fixed here, per the file fence and the STOP-RULE. Applying
the KtMap fix did **not** move either of these two failures (confirmed — same exact
AttributeError, same line, same count, before and after) because they share no mechanism
with `Map.keys`/`.values`; this independently corroborates the earlier doc's claim that
these 2 failures pre-date and are unrelated to the flatMapLatest/KtMap work.

**Honest final tally:**
- Per-screen sweep (28 screens): **535/537 ok** (2 fail, both `onQueryChange(None)`).
- Shell (nav bar, 5 handlers): **5/5 ok**.
- **Grand total: 540/542 ok**, unchanged from the number already reported in
  `flatmaplatest_live.md` before this task's KtMap fix — exactly as expected, since the fix
  addressed a different, unrelated cause.
- On the task's stated "expected 513" baseline vs. the measured 542: this environment's
  handler count is a property of how many handlers the CURRENT screen set + CURRENT
  seeded-DB fixtures expose to `enumerate_handlers`/`enumerate_shell_handlers` (e.g.
  `ExercisePickerScreen` alone contributes 211 of the 542, driven by however many exercises
  the seeded catalogue currently has); it is not a number this task's fix could or did move,
  and it was not adjusted/tuned to match any target.

## 4. fidelity gate reconciliation — 403/406

Ran all 30 available screens (28 app screens + `Specimen`/`SpecimenList`) through
`fchunk.py` (`inspect_layout.py` dump -> `layout_diff.py` diff), in small batches to respect
the sandbox's execution limits. Result: **403/406**, matching the number already reported.
Only **2 screens** (not 3) actually contain misses; they sum to the 3-component gap:

### ProgramsScreen: 1/3 matched-and-in-tolerance
```
FAIL  Programs  (position drift ~11%, a secondary/independent geometry note, not the focus here)
MISS  No programs yet.                    (compose ground truth only)
MISS  Tap + to build your first program.  (compose ground truth only)
XTRA  ~60 kivy-only nodes: Active, 3-Day Full Body — Ground Up, Join program (x12),
      3-Day Hypertrophy, Brain Builders, On my own journey, Just Show Up, RIR Awareness, ...
```
**Classification: fuller-tree-due-to-live-flows, NOT a regression.** The Kotlin
ground-truth dump for `ProgramsScreen` captured a **3-node EMPTY-catalogue state**
("No programs yet." / a CTA to create one) — i.e. it was dumped when the seeded/staged
Robolectric fixture had zero programs and zero active paths. The live kivy render now shows
the full real program catalogue (with names, descriptions, and per-program "Join program"
actions) because the Room-backed flows genuinely populate data — exactly the scenario the
task's theory predicted. This is a stale/minimal ground-truth dump, not evidence of the
transpiled app rendering something wrong.

### ExercisesScreen: 6/7 matched-and-in-tolerance
```
PASS  Exercises, All, Built-in, Custom, Favorites, Search exercises…   (all 6, all <3% drift)
MISS  No exercises found.                 (compose ground truth only)
XTRA  ~270 kivy-only nodes: the full seeded exercise catalogue (Push/Pull/Legs/Core/Mobility
      groups, e.g. "Arnold Press", "Barbell Back Squat", "Push-Up", ...)
```
**Classification: fuller-tree-due-to-live-flows, NOT a regression.** All 6 chrome elements
(title, 3 filter tabs, the search bar) that DO appear in both dumps match geometry within
tolerance (worst drift 2.9%). The ONE miss is the empty-state message, which the Kotlin
ground truth shows because IT was dumped against an empty exercise catalogue; the live kivy
render (real ~270-exercise seeded catalogue) correctly never shows that placeholder because
the list isn't empty. No wrong-position or missing-required element among any component
that both dumps agree should exist.

**Both discrepancies are dump-timing/dump-fixture-state mismatches (stale ground truth
predates live/populated data), not a rendering geometry regression introduced by the KtMap
fix or the flatMapLatest work.** No threshold was tuned and no ground-truth file was edited
to reach 403/406 — this is the number measured with the tolerance/dump pipeline exactly as
shipped.

**Action item requiring the user's host machine:** re-dumping `ProgramsScreen` and
`ExercisesScreen` (and, if desired, revalidating any other screen) via the real Android/
Compose Robolectric `LayoutDumpTest` with a SEEDED (non-empty) database fixture is the only
way to get a ground truth that reflects the now-live app. This sandbox has no
Android/Gradle/Compose toolchain and cannot produce or fake that re-dump; it was not
attempted here.

## 5. Full gate suite — final honest numbers

| Gate | Result |
|---|---|
| `run_kotlin_tests.py` | **160/160 PASS** |
| `datalayer_oracle.py` | **ALL GREEN** (9/9: 2+1+2+4) |
| `realtap_gate.py --case existing` | **GATE: GREEN** (3/3 assertions) |
| `realtap_gate.py --case overlay` | **GATE: GREEN** (7/7 assertions) |
| `realtap_gate.py --case reactivity` | **GATE: GREEN** (4/4 assertions) |
| `interact.py` (28 screens + shell, chunked) | **540/542 ok** (2 fail: `onQueryChange(None)` in `ExercisesScreen` + `ExercisePickerScreen`, root cause in `render/interact.py`'s arg-inference table, outside the `kotlin_rt.py` fence, unmoved by this fix as expected) |
| `fidelity` (30 screens, chunked via `fchunk.py`) | **403/406** (`ProgramsScreen` 1/3, `ExercisesScreen` 6/7 — both stale/empty-state ground-truth dumps vs. now-live fuller renders; re-dump needed on the user's host Android toolchain) |

No thresholds were tuned, no ground-truth dumps were edited, and no failing assertion was
swallowed or skipped to produce these numbers.

### Note on sandbox execution
An earlier attempt to run the full-app proof hit apparent 45-second timeouts on even
`loader.Loader().__init__()`'s file glob. Root cause: the staged `/tmp/gh` copy contained a
leftover self-referential symlink
(`WFL_MixingCenter/WFL_MixingCenter -> /sessions/.../mnt/WFL_MixingCenter`, itself
containing the same symlink) that `glob(..., recursive=True)` was traversing without bound.
Removing that symlink from the staged copy (not from the real repo — this was pure sandbox
scratch-space cruft, no file-fence file was touched) brought `Loader.load_all()` down to
under 1 second and unblocked every proof/gate run in this report.
