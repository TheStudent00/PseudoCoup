# LayoutDumpAllTest leak bisect

## Culprit (minimal set)
The leak that makes `dumpProgramEditorScreen` render the wrong (`editable`) branch requires the
combination of THREE tests running before it:

- `dumpOnboardingScreen`
- `dumpReportBugScreen`
- `dumpExercisePickerScreen`

All three are jointly necessary — removing any one returns `readonly` (correct). No single test and
no pair reproduces it.

## Runs (test set + result; ProgramEditor always last)
- Group A {Onboarding, ReportBug, ExerciseCreate, GymCreateWizard, GymEditor, Paths} → readonly
- Group B {SuggestedStretches, WorkoutCooldown, WorkoutSummary, WorkoutWarmup, ExercisePicker} → readonly
- Full class (*LayoutDumpAllTest) → editable
- All 11 candidates (A + B) → editable
- A + {SuggestedStretches, WorkoutCooldown, WorkoutSummary} → readonly
- A + {WorkoutWarmup, ExercisePicker} → editable
- A + {ExercisePicker} → editable
- {Onboarding, ReportBug, ExerciseCreate} + ExercisePicker → editable
- {ExerciseCreate} + ExercisePicker → readonly
- {Onboarding} + ExercisePicker → readonly
- {ReportBug} + ExercisePicker → readonly
- {Onboarding, ReportBug} + ExercisePicker → editable
- {Onboarding, ReportBug} (no ExercisePicker) → readonly
- {ReportBug, ExercisePicker} (no Onboarding) → readonly  [same as {ReportBug}+EP line above]
- {Onboarding, ExercisePicker} (no ReportBug) → readonly  [same as {Onboarding}+EP line above]

Minimal reproducing set: dumpOnboardingScreen + dumpReportBugScreen + dumpExercisePickerScreen + dumpProgramEditorScreen.
