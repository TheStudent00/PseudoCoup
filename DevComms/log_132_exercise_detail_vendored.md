# log_132 — exercise_detail VENDORED: 2nd interactive drop-in (transpiled VM + enum lift)

Date: 2026-06-29
Type: milestone. A 2nd screen vendored + proven in the app env (after gym_list).

## What's vendored (`vendor_exercise_detail.py` → WFL_PseudoCoup/src/generated)

- `exercise_enums_kt.py` — transpiled MovementPattern/EquipmentType/MuscleGroup/WeightUnit.
- `exercise_detail_kt.py` — transpiled ExerciseDetailViewModel + ExcludePrompt (1:1 Kotlin).
- `exercise_detail_backend.py` — an ExerciseEntity enum-lift PROXY (int→enum, incl. List<MuscleGroup>) +
  the adapter (savedStateHandle→selected id; mutating actions → app ExerciseRepository) + make_vm.
- `ui/exercise_detail_screen_gen.py` — the generated screen.

## Verified in the app env (`tools/test_exercise_detail_gen.py`, RESULT MATCH)

- renders the seeded Back Squat content — **7 leaves shared** with the hand-built (title, chips,
  section labels, Movement & equipment body).
- `editCurrent()` → the navigateToEdit SharedFlow → `_nav_edit` → `navigate('exercise_create')`.
- `excludePrompt` set → the AlertDialog renders (Already in your program / Got it / Cancel).
- `confirmSwapLater()` → dialog dismissed (MutableStateFlow→State repaint).
- app smoke 30/30 (the vendored files are present; exercise_detail not yet routed).

## Two render differences from the hand-built (not bugs in the VM/nav/dialog)

1. The generated is MORE faithful to the original Compose: it expands the overflow menu (Duplicate &
   Edit / Never program this) where the hand-built collapses to a `⋮` glyph. Back is text vs a button.
2. **A real generator blemish:** 2 stray `None` leaves under the section labels. Root cause: the custom
   `DetailSection(title, content: @Composable)` composable is MISRESOLVED to a DIFFERENT overload
   `DetailSection(title, body: String)` (in CycleDetailDialog.kt). `_comp_defs` is a global name→def
   map, so the `body: String` version overwrites the content-slot one → the content slot becomes an
   unbound `body` text leaf (None). This is the "unresolved 3 body exprs" of log_125.

## Next

Fix the composable overload misresolution (file-aware `_comp_defs`: prefer the same-file / content-slot
definition) → cleans the render → then ROUTE exercise_detail via ExerciseDetailScreenGen (like gym_list
log_118). The VM/nav/dialog vertical is proven; only the DetailSection slot resolution stands between
here and a clean routed drop-in.
