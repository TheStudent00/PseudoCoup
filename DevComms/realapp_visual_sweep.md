# Real-app visual sweep (report-only)

Date: 2026-07-05. Agent: visual QA. All 27 screens in `render/layout_screens.txt` were run
headless via `run_app.py` and each resulting PNG was eyeballed. Screenshots: `layout_inspect/shots/qa_<Screen>0001.png`.

Method: looking ONLY for gross breakage (black/empty screen, invisible text, bad clipping,
obviously wrong colors, unreadable controls). Pixel-level M3 spec is the geometry gauge's job, not this.

## Summary counts
- CRASH: 0
- BROKEN: 0
- MINOR: 8
- OK: 19
- Total: 27

No screen is black, empty, has invisible text, or badly clips content. Nothing a person would
call "broken on sight." The findings below are wrong-color / missing-glyph / fixture issues.

## Ranked findings (BROKEN/CRASH first — none — then MINOR)

| screen | verdict | note |
|---|---|---|
| ExercisesScreen | MINOR | **#1 to inspect.** Fixed TabRow (All/Built-in/Custom/Favorites) renders as a solid DARK-GRAY bar with white labels — clearly wrong color for this light/lavender theme. Readable, not broken, but visually jarring. |
| ProgressScreen | MINOR | Same dark-gray fixed TabRow bug (Analytics/Bests/History): full-width charcoal bar, white text. Same root cause as ExercisesScreen. |
| WorkoutWarmupScreen | MINOR | Leading icons missing — tofu boxes (□) at the left of every list item. Text + play triangles fine. |
| WorkoutCooldownScreen | MINOR | Same missing leading icons (□) on each item row. |
| GymCreateWizardScreen | MINOR | Missing icons (□) on the Home/Big Box/Strength Gym choice cards. |
| UpdateProgramWizardScreen | MINOR | Missing icons (□) on the 4 update-type cards (Vacation/Injury/Adapt/Life). |
| ExerciseCreateScreen | MINOR | "Unilateral" and "Compound" rows show labels but no visible checkbox/switch control next to them. |
| ProgramEditorScreen | MINOR | Small text overlap: a "Deload" label collides with the "Full Body B — Hinge" row in the progression tree. Everything still legible. |
| PathDetailScreen | MINOR/DATA | Renders "Path not found." — empty content, back arrow only. Likely a fixture/navArg not seeded for direct launch, not a render bug. Worth confirming it populates from real navigation. |
| TodayScreen | OK | Header card + FAB, readable. |
| ExerciseDetailScreen | OK | Chips + sections all fine (video URL wraps, but that's data). |
| GymListScreen | OK | Gym card, Active chip, Delete button, FAB. |
| HistoryScreen | OK | Cardio card readable. |
| LogCardioScreen | OK | Activity chips + fields + segmented intensity all fine. |
| ProgramsScreen | OK | Empty state. |
| SettingsScreen | OK | All rows, dropdowns, segmented control readable. |
| WinsListScreen | OK | Scrollable tab row here renders LIGHT/correct (contrast with Exercises/Progress). |
| OnboardingScreen | OK | Dumbbell icon + title + button. |
| SessionDetailScreen | OK | Stat cards + exercise list. |
| ReportBugScreen | OK | Text field + severity segmented + send button. |
| GymEditorScreen | OK | Name field + empty equipment + FAB. |
| PathsScreen | OK | Intro empty state. |
| SuggestedStretchesScreen | OK | Light tab chips + stretch list. |
| WorkoutExecutionScreen | OK | Dense set-logging screen, all controls readable (incl. red delete band). |
| WorkoutSummaryScreen | OK | Stat cards + exercise summary. |
| ExercisePickerScreen | OK | Light tab chips + list with heart favorites. |
| MyProgramScreen | OK | Empty state. |
| ProgramDayEditorScreen | OK | Superset groups readable. |

## Cross-cutting notes (one cause each)
- **Fixed TabRow color** (ExercisesScreen, ProgressScreen): the *fixed* TabRow renders dark
  gray while *scrollable* tab rows (WinsList, ExercisePicker, SuggestedStretches) render light.
  Strongly suggests one buggy fixed-TabRow container background. Fix moves both screens.
- **Missing leading list icons** (Warmup, Cooldown, GymCreateWizard, UpdateProgramWizard):
  same tofu-box symptom — a shared icon set / font glyph not resolving for these list/card items.
  Note: heart, play-triangle, back-arrow, chevron, FAB-plus, trash icons DO render, so it is a
  subset of glyphs, not the whole icon font.
