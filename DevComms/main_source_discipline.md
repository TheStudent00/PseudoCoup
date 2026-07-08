# Main-source discipline plan (WFL Kotlin app)

2026-07-07. Decision: instead of absorbing every WFL source awkwardness in tooling (recorder merges,
clock monkeypatches, text canonicalization), discipline the main source where the pattern itself is the
problem. Trigger: the walker slice-3 empty-edge-label issue (unmerged clickable semantics) and the
Resume/WorkoutExecutionViewModel float*NoneType crash (transpiler's synthetic `else: None` on exhaustive
`when`). Scope agreed with user: Tiers 1+2+3 now; Tier 4 deferred.

LAW for every edit here: appearance and function of the running app UNCHANGED. Semantics/labels/locale
pins and clock seams only. Anything that would change rendered pixels or behavior is out of scope.

## Tier 1a — merged semantics on container clickables

Problem: 52 `.clickable` sites across 16 files; zero `onClickLabel` / `semantics(mergeDescendants=true)`
anywhere. ~30 are containers (Row/Column/Box) wrapping child `Text`: Compose does not merge child text
into the clickable node, so the Kotlin walk recorder sees an interactive node with an empty label.
`walk_diff.py` joins edges on (label, handler_kind) — empty labels break kt/py edge alignment.

Fix mechanism (uniform): add `Modifier.semantics(mergeDescendants = true) {}` to the clickable
container's modifier chain (before `.clickable`). No visual change; the accessibility/semantics tree now
carries the merged child text on the interactive node, which is also a real accessibility improvement.

Order of work (shared components first — one edit fixes many call sites):
    ui/components/WflSectionHeader.kt:36        (reused across many screens)
    ui/components/CompactControls.kt:158,162,215 (dropdown rows)
    ui/exercises/ExercisesScreen.kt:193,223      (duplicated SectionHeader pattern + list item)
Then per-site (container-wrapping-Text list, ~25 more):
    ui/programs/UpdateProgramWizardScreen.kt:718,748
    ui/programs/components/RoadmapView.kt:273,303,334,389
    ui/programs/ExercisePickerScreen.kt:177
    ui/programs/ProgramEditorScreen.kt:329
    ui/settings/SettingsScreen.kt:383
    ui/today/TodayScreen.kt:745,865
    navigation/AppNavigation.kt:955
    ui/celebration/ProgramEndDecision.kt:84
    ui/execution/WorkoutExecutionScreen.kt:938,1235,1382,1531
    ui/gym/GymEditorScreen.kt:170
    ui/execution/components/ExerciseManagementDialogs.kt:114,201,365,601
Skip (no text to merge / deliberate scrims): TodayScreen.kt:439, GlitterBurstStar.kt:179,
WorkoutExecutionScreen.kt:393,438, ExercisesScreen.kt:251 (icon has own contentDescription).

Relation to existing recorder merge: WalkRecorderTest.kt's `subtreeText()` (mirrors interact.py
`_subtext()`) STAYS — it is the alignment mechanism. Tier 1a makes the underlying semantics tree carry
the labels natively so both recorders depend less on the mirror being perfect.

## Tier 1b — displayed-date reads pinned to TimeProvider

The two reads the walker actually sees on screen (the rest of the currentTimeMillis sites are audit
fields — Tier 4):
    navigation/AppNavigation.kt:994  AppTopBar: LocalDate.now().dayOfWeek... (also Locale.getDefault())
    ui/today/TodayScreen.kt:128      LocalDate.now().get(WeekFields.ISO.weekOfWeekBasedYear())
Fix: derive both from the injected TimeProvider (it is the app's declared single source of "now") —
plumbed through the ViewModel already present on each screen, not a new global. This closes the open
HANDOFF decision ("pin AppTopBar's LocalDate.now(), user's call") — user approved 2026-07-07.
Consequence: walker/_pin_time_provider and WalkRecorderTest pinClock() then pin these reads too — walks
agree regardless of calendar day.

## Tier 2 — locale pins

    ui/settings/SettingsScreen.kt:170   String.format("%.1f", it) → explicit Locale.US (Python twin is
                                        always period-decimal; comma-locale devices silently diverge)
    navigation/AppNavigation.kt:994     Locale.getDefault() day name → explicit locale (same edit as 1b)
    ui/wins/WinsListScreen.kt:236,275   date formatter + lowercase sort key → explicit locale
No visible change on en_US devices; deterministic everywhere else.

## Tier 3 — transpiler: raise on synthetic when-else (PseudoCoup tooling, not WFL source)

Problem class (proved by the Resume bug): Kotlin's exhaustive `when` over an enum needs no else — the
compiler enforces totality. The transpiler emits `else: <result> = None` for that "impossible" branch, so
any Python-side gap (enum identity break, Stub leak, future enum value) becomes silent None-arithmetic
(`TypeError: float * NoneType`) far from the cause. 15 such blocks in engine/ alone (RestartEngine 3
multiplier tables, PeriodizationEngine 6, CalibrationEngine.coldStartSeed, CardioRecoveryEngine
fitnessScale/intensityFactor...).

Fix: the transpiler's synthetic exhaustive-else emits
    raise RuntimeError(f"unreachable when-branch: <fn> got {<subject>!r}")
instead of None. Kotlin source unchanged (exhaustiveness there is a feature). Every impossible branch
now fails loud with a name at the site, instead of surfacing as anonymous arithmetic downstream.
Requires re-transpile + engine oracle re-run to confirm no legitimate path relied on the None.

## Verification (after all tiers)

1. Kotlin: full test suite (160/160 expected unchanged) — semantics modifiers and locale pins must not
   alter behavior.
2. Re-transpile the touched files (Tier 1/2 edits change Kotlin source → py twins must be regenerated);
   datalayer/engine oracles re-run (Tier 3 changes emitted code shape).
3. Fidelity gauge 423/423 — expected UNCHANGED (semantics edits don't move pixels). Any diff = a Tier 1a
   edit broke the LAW; revert that site.
4. Interact gauge 1410/1410 + shell 6.
5. Re-record BOTH walk baselines; walk_diff expected: kt empty-label edge mismatches drop substantially
   (from the 37-edge-mismatch pool); same-day-only agreement caveat gone.

## Tier 4 — deferred

- `System.currentTimeMillis()` → TimeProvider sweep (~38 sites, 16 in ProgramRepository.kt). Mechanical;
  also makes DebugTimeProvider time-travel actually reach audit timestamps. Do as its own slice.
- Timer tick seam for `delay(1_000L)` countdown loops + PR/mid-microcycle flash timers
  (WorkoutExecution/Warmup/Cooldown VMs) — only matters once the walker reaches those screens.
- UUID PKs: keep; comparators normalize/ignore ID fields (already required).
- GlitterBurstStar (Random + wall-clock animation): exclude from comparison, don't discipline.

## Chronology

Work committed in small steps (sandbox can commit, not push — user pushes). One commit per tier-step,
message names the tier and the sites touched.
