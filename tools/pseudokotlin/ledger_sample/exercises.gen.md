# PseudoUI generated kit screen -- exercises  (from Compose ExercisesScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (33 calls)
```python
ui.define_box("exercises_z00_box", "content", "V")
ui.define_box("exercises_z01_scaffold", "exercises_z00_box", "V")
ui.define_box("exercises_z02_lazycolumn", "exercises_z01_scaffold", "V")
ui.define_box("exercises_z03_primaryscrollabl", "exercises_z02_lazycolumn", "V")
ui.define_box("exercises_z04_tab", "exercises_z03_primaryscrollabl", "V")
ui.define_text("exercises_z05_t_label", "exercises_z04_tab", "t.label")
ui.define_box("exercises_z06_searchbar", "exercises_z02_lazycolumn", "V")
ui.define_text("exercises_z07_search_exercises", "exercises_z06_searchbar", "Search exercises…")
ui.define_box("exercises_z08_box", "exercises_z02_lazycolumn", "V")
ui.define_text("exercises_z09_no_exercises_fou", "exercises_z08_box", "No exercises found.")
ui.define_box("exercises_z10_sectionheader", "exercises_z02_lazycolumn", "V")
ui.define_box("exercises_z11_row", "exercises_z10_sectionheader", "H")
ui.define_text("exercises_z12_label_count", "exercises_z11_row", "$label · $count")
ui.define_icon("exercises_z13_collapse_expand", "exercises_z11_row", "Collapse|Expand")
ui.define_box("exercises_z14_exerciselistitem", "exercises_z02_lazycolumn", "V")
ui.define_box("exercises_z15_row", "exercises_z14_exerciselistitem", "H")
ui.define_box("exercises_z16_column", "exercises_z15_row", "V")
ui.define_text("exercises_z17_exercise_name", "exercises_z16_column", "exercise.name")
ui.define_text("exercises_z18_muscles_exercise", "exercises_z16_column", "$muscles · ${exercise.equipmen…")
ui.define_icon("exercises_z19_remove_from_favo", "exercises_z15_row", "Remove from favorites|Add to f…")
ui.define_box("exercises_z20_sectionheader", "exercises_z02_lazycolumn", "V")
ui.define_box("exercises_z21_row", "exercises_z20_sectionheader", "H")
ui.define_text("exercises_z22_label_count", "exercises_z21_row", "$label · $count")
ui.define_icon("exercises_z23_collapse_expand", "exercises_z21_row", "Collapse|Expand")
ui.define_box("exercises_z24_exerciselistitem", "exercises_z02_lazycolumn", "V")
ui.define_box("exercises_z25_row", "exercises_z24_exerciselistitem", "H")
ui.define_box("exercises_z26_column", "exercises_z25_row", "V")
ui.define_text("exercises_z27_exercise_name", "exercises_z26_column", "exercise.name")
ui.define_text("exercises_z28_muscles_exercise", "exercises_z26_column", "$muscles · ${exercise.equipmen…")
ui.define_icon("exercises_z29_remove_from_favo", "exercises_z25_row", "Remove from favorites|Add to f…")
ui.define_box("exercises_z30_topappbar", "exercises_z01_scaffold", "V")
ui.define_text("exercises_z31_exercises", "exercises_z30_topappbar", "Exercises")
ui.define_icon("exercises_z32_new_exercise", "exercises_z30_topappbar", "New exercise")
```

## generated tree
  - Column[box]  <container>
    - Column[scaffold]  <container>
      - Column[lazycolumn]  <container>
        - Column[primaryscrollabl]  <container>
          - Column[tab]  <container>
            - Text[t.label]  <leaf>
        - Column[searchbar]  <container>
          - Text[Search exercises…]  <leaf>
        - Column[box]  <container>
          - Text[No exercises found.]  <leaf>
        - Column[sectionheader]  <container>
          - Row[row]  <container>
            - Text[$label · $count]  <leaf>
            - Icon[Collapse|Expand]  <leaf>
        - Column[exerciselistitem]  <container>
          - Row[row]  <container>
            - Column[column]  <container>
              - Text[exercise.name]  <leaf>
              - Text[$muscles · ${exercise.equipmen…]  <leaf>
            - Icon[Remove from favorites|Add to f…]  <leaf>
        - Column[sectionheader]  <container>
          - Row[row]  <container>
            - Text[$label · $count]  <leaf>
            - Icon[Collapse|Expand]  <leaf>
        - Column[exerciselistitem]  <container>
          - Row[row]  <container>
            - Column[column]  <container>
              - Text[exercise.name]  <leaf>
              - Text[$muscles · ${exercise.equipmen…]  <leaf>
            - Icon[Remove from favorites|Add to f…]  <leaf>
      - Column[topappbar]  <container>
        - Text[Exercises]  <leaf>
        - Icon[New exercise]  <leaf>

---
## verify vs Compose source (ExercisesScreen)
- distinct leaf signatures matched: 6/6 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 33 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (exercises_screen.py)
- leaf signatures shared:        3
- generated-only (other states / not in this trace): 3
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:New exercise
    GEN-only I:·DYN·
    GEN-only T:No exercises found.
