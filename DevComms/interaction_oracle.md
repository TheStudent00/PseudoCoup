# Interaction Oracle -- 27 screens swept in 107.6s

Per-screen handler sweep (each handler fired on a fresh seeded DB + fresh compose):

| screen | handlers | ok | fail | note |
| --- | ---: | ---: | ---: | --- |
| ExerciseDetailScreen | 13 | 13 | 0 |  |
| ExercisesScreen | 9 | 9 | 0 |  |
| GymListScreen | 5 | 5 | 0 |  |
| HistoryScreen | 0 | 0 | 0 |  |
| LogCardioScreen | 21 | 18 | 3 |  |
| ProgramsScreen | 1 | 1 | 0 |  |
| ProgressScreen | 5 | 5 | 0 |  |
| SettingsScreen | 21 | 21 | 0 |  |
| TodayScreen | 1 | 1 | 0 |  |
| WinsListScreen | 10 | 10 | 0 |  |
| OnboardingScreen | 0 | 0 | 0 | EXCLUDED: no ViewModel/first-run flow to seed here; the walk.py front-door harness covers onboarding by firing its real advance/choice buttons in sequence |
| SessionDetailScreen | 1 | 1 | 0 |  |
| ReportBugScreen | 7 | 7 | 0 |  |
| ExerciseCreateScreen | 101 | 101 | 0 |  |
| GymCreateWizardScreen | 5 | 5 | 0 |  |
| GymEditorScreen | 4 | 4 | 0 |  |
| PathDetailScreen | 1 | 1 | 0 |  |
| PathsScreen | 1 | 1 | 0 |  |
| SuggestedStretchesScreen | 27 | 27 | 0 |  |
| WorkoutCooldownScreen | 9 | 4 | 5 |  |
| WorkoutExecutionScreen | 39 | 32 | 7 |  |
| WorkoutSummaryScreen | 2 | 2 | 0 |  |
| WorkoutWarmupScreen | 10 | 10 | 0 |  |
| ExercisePickerScreen | 211 | 211 | 0 |  |
| MyProgramScreen | 1 | 1 | 0 |  |
| ProgramDayEditorScreen | 1 | 1 | 0 |  |
| ProgramEditorScreen | 2 | 2 | 0 |  |
| UpdateProgramWizardScreen | 5 | 5 | 0 |  |

**INTERACT: 513 fired, 498 ok, 15 failures across 27 screens**

## Failure catalog (grouped by exception signature)

### [5] TypeError @ WorkoutCooldownScreen.py:33 :: ConditioningFinishedView() got an unexpected keyword argument '?'
```
TypeError: ConditioningFinishedView() got an unexpected keyword argument 'content'
```
**Hypothesis:** TRANSPILER gap. Firing an activity/finish handler advances the ConditioningStage to FINISHED; the re-compose then calls ConditioningFinishedView(..., content=<trailing lambda>), but the transpiled def for that composable does not declare the `content` slot param -> unexpected-kwarg. Trailing-lambda slot not emitted on the callee's signature.
- WorkoutCooldownScreen :: 🚶 / Slow walk / 4 min / A few easy minu… :: onClick
- WorkoutCooldownScreen :: 🫁 / Box breathing / 4 min / In 4, hold … :: onClick
- WorkoutCooldownScreen :: 🧘 / Gentle yoga flow / 6 min / Child's … :: onClick
- WorkoutCooldownScreen :: 🎶 / Slow dance / 4 min / One slow song … :: onClick
- WorkoutCooldownScreen :: Done — wrap up :: onClick

### [2] AttributeError @ WorkoutExecutionScreen.py:598 :: '?' object has no attribute '?'
```
AttributeError: 'str' object has no attribute 'text'
```
**Hypothesis:** INSTRUMENT limitation. Same as :596 -- TextFieldValue-typed field fed a bare string by the generic value-inference rule.
- WorkoutExecutionScreen :: 6 :: onValueChange
- WorkoutExecutionScreen :: 12 :: onValueChange

### [1] AttributeError @ LogCardioViewModel.py:19 :: '?' object has no attribute '?'
```
AttributeError: 'str' object has no attribute 'filter'
```
**Hypothesis:** RUNTIME gap. Handler runs `value.filter(Char.isDigit)` on the argument; the value arrives as a bare python `str`, which has no Kotlin `String.filter` extension attached -> AttributeError. Real Kotlin String extensions are not mounted on builtin str.
- LogCardioScreen :: BasicTextField :: onValueChange

### [1] AttributeError @ LogCardioViewModel.py:23 :: '?' object has no attribute '?'
```
AttributeError: 'str' object has no attribute 'filter'
```
**Hypothesis:** RUNTIME gap. Same as :19 -- `value.filter{ c.isDigit() || c=='.' }` on a bare python str.
- LogCardioScreen :: BasicTextField :: onValueChange

### [1] AttributeError @ LogCardioViewModel.py:25 :: '?' object has no attribute '?'
```
AttributeError: 'str' object has no attribute 'filter'
```
**Hypothesis:** RUNTIME gap. Same as :19 -- `value.filter(Char.isDigit)` on a bare python str.
- LogCardioScreen :: BasicTextField :: onValueChange

### [1] NameError @ PlateCalculatorSheet.py:72 :: name '?' is not defined
```
NameError: name 'toLong' is not defined
```
**Hypothesis:** TRANSPILER gap. `Double.fmt()` emits a bare `toLong()` instead of `self.toLong()` -- the extension-receiver was dropped, so the name is undefined at call time (NameError). Surfaces when a target/bar adjust handler recomputes plate labels.
- WorkoutExecutionScreen :: IconButton :: onClick

### [1] AttributeError @ WorkoutExecutionScreen.py:596 :: '?' object has no attribute '?'
```
AttributeError: 'str' object has no attribute 'text'
```
**Hypothesis:** INSTRUMENT limitation (boundary with a real gap). The set-entry field's onValueChange expects a Compose TextFieldValue (`incoming.text`); the oracle passes the test string "42", which has no `.text`. A TextFieldValue-typed field needs a TextFieldValue, not a String.
- WorkoutExecutionScreen :: BasicTextField :: onValueChange

### [1] AttributeError @ ProgramExerciseWithSets.py:62 :: '?' object has no attribute '?'
```
AttributeError: 'KtMap' object has no attribute 'maxByOrNull'
```
**Hypothesis:** RUNTIME gap. `'KtMap' object has no attribute 'maxByOrNull'` -- `groupingBy{}.eachCount()` yields a KtMap, but the KtMap runtime wrapper does not expose the Kotlin `maxByOrNull` extension.
- WorkoutExecutionScreen :: Add set :: onClick

### [1] AttributeError @ ExerciseManagementDialogs.py:13 :: '?' object has no attribute '?'
```
AttributeError: 'bool' object has no attribute 'strip'
```
**Hypothesis:** RUNTIME gap. `'bool' object has no attribute 'strip'` at `query.value.strip()`: opening the Add-exercise dialog remembers `mutableStateOf("")`, but `.value` reads back a bool -- the mutableStateOf/remember State wrapper's `.value` is resolving to a boolean instead of the held string in this nested-dialog slot position.
- WorkoutExecutionScreen :: Add exercise :: onClick

### [1] AttributeError @ ExerciseManagementDialogs.py:177 :: '?' object has no attribute '?'
```
AttributeError: 'bool' object has no attribute 'exercise'
```
**Hypothesis:** RUNTIME gap. `'bool' object has no attribute 'exercise'`: same State.value-shape problem -- `confirmItem` (a remembered nullable state) reads back as a bool, so `.exercise` fails when the Remove-exercise handler opens the confirm dialog.
- WorkoutExecutionScreen :: Remove exercise :: onClick
