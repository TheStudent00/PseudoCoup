# PseudoUI generated kit screen -- exercise_picker  (from Compose ExercisePickerScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (22 calls)
```python
ui.define_box("exercise_picker_z00_launchedeffect", "content", "V")
ui.define_box("exercise_picker_z01_scaffold", "content", "V")
ui.define_box("exercise_picker_z02_column", "exercise_picker_z01_scaffold", "V")
ui.define_box("exercise_picker_z03_searchbar", "exercise_picker_z02_column", "V")
ui.define_text("exercise_picker_z04_search_exercises", "exercise_picker_z03_searchbar", "Search exercises…")
ui.define_box("exercise_picker_z05_row", "exercise_picker_z02_column", "H")
ui.define_box("exercise_picker_z06_filterchip", "exercise_picker_z05_row", "V")
ui.define_text("exercise_picker_z07_favorites", "exercise_picker_z06_filterchip", "Favorites")
ui.define_box("exercise_picker_z08_filterchip", "exercise_picker_z05_row", "V")
ui.define_text("exercise_picker_z09_all_muscles", "exercise_picker_z08_filterchip", "All muscles")
ui.define_box("exercise_picker_z10_filterchip", "exercise_picker_z05_row", "V")
ui.define_text("exercise_picker_z11_group_displaynam", "exercise_picker_z10_filterchip", "group.displayName()")
ui.define_box("exercise_picker_z12_lazycolumn", "exercise_picker_z02_column", "V")
ui.define_text("exercise_picker_z13_no_exercises_fou", "exercise_picker_z12_lazycolumn", "No exercises found.")
ui.define_box("exercise_picker_z14_exercisepickerro", "exercise_picker_z12_lazycolumn", "V")
ui.define_box("exercise_picker_z15_listitem", "exercise_picker_z14_exercisepickerro", "V")
ui.define_text("exercise_picker_z16_exercise_name", "exercise_picker_z15_listitem", "exercise.name")
ui.define_text("exercise_picker_z17_muscles", "exercise_picker_z15_listitem", "muscles")
ui.define_icon("exercise_picker_z18_remove_from_favo", "exercise_picker_z15_listitem", "Remove from favourites|Add to …")
ui.define_box("exercise_picker_z19_topappbar", "exercise_picker_z01_scaffold", "V")
ui.define_text("exercise_picker_z20_add_exercise", "exercise_picker_z19_topappbar", "Add exercise")
ui.define_icon("exercise_picker_z21_back", "exercise_picker_z19_topappbar", "Back")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_scaffold]  <container>
    - Column[z02_column]  <container>
      - Column[z03_searchbar]  <container>
        - Text[Search exercises…]  <leaf>
      - Row[z05_row]  <container>
        - Column[z06_filterchip]  <container>
          - Text[Favorites]  <leaf>
        - Column[z08_filterchip]  <container>
          - Text[All muscles]  <leaf>
        - Column[z10_filterchip]  <container>
          - Text[group.displayName()]  <leaf>
      - Column[z12_lazycolumn]  <container>
        - Text[No exercises found.]  <leaf>
        - Column[z14_exercisepickerro]  <container>
          - Column[z15_listitem]  <container>
            - Text[exercise.name]  <leaf>
            - Text[muscles]  <leaf>
            - Icon[Remove from favourites|Add to …]  <leaf>
    - Column[z19_topappbar]  <container>
      - Text[Add exercise]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (ExercisePickerScreen)
- distinct leaf signatures matched: 8/8 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 22 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (exercise_picker_screen.py)
- leaf signatures shared:        2
- generated-only (other states / not in this trace): 6
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Back
    GEN-only I:·DYN·
    GEN-only T:All muscles
    GEN-only T:Favorites
    GEN-only T:No exercises found.
    GEN-only T:Search exercises…
