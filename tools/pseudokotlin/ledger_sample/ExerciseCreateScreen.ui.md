# UI layout ledger -- ExerciseCreateScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable SeedSourceDropdown
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
    - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
      - CompactDropdown  <leaf>   size: w=fill(rel) h=wrap(rel)
    - Text[For a new movement, we'll star…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SeedSourceDropdown/Column[0]
    SeedSourceDropdown/Column[0]/LabeledField
    SeedSourceDropdown/Column[0]/LabeledField/CompactDropdown
    SeedSourceDropdown/Column[0]/Text[For a new movement, we'll star…]

## @Composable EnumDropdown
  - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
    - CompactDropdown  <leaf>   size: w=fill(rel) h=wrap(rel)
  ids:
    EnumDropdown/LabeledField
    EnumDropdown/LabeledField/CompactDropdown

## @Composable MuscleSelector
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
    - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - CompactMultiSelectDropdown  <leaf>   size: w=fill(rel) h=wrap(rel)
    - Text[Select at least one primary mu…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    MuscleSelector/Column[0]
    MuscleSelector/Column[0]/Text[title]
    MuscleSelector/Column[0]/CompactMultiSelectDropdown
    MuscleSelector/Column[0]/Text[Select at least one primary mu…]

## @Composable CompactToggle
  - Row[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalAlignment=Alignment.CenterVertically (rel)
    - Text[label]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
    - Switch[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        non-layout: scale
  ids:
    CompactToggle/Row[0]
    CompactToggle/Row[0]/Text[label]
    CompactToggle/Row[0]/Switch[1]

## @Composable ExerciseCreateScreen
  - LaunchedEffect[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Scaffold[1]  <container>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(20.dp) (rel)
      - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Text[Name is required]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - MuscleSelector  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - MuscleSelector  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - EnumDropdown  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - EnumDropdown  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[6]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - CompactToggle  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - CompactToggle  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
      - SeedSourceDropdown  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - OutlinedTextField[8]  <leaf>   size: w=fill(rel) h=wrap(rel)
      - OutlinedTextField[9]  <leaf>   size: w=fill(rel) h=wrap(rel)
      - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Spacer[11]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ExerciseCreateScreen/LaunchedEffect[0]
    ExerciseCreateScreen/Scaffold[1]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/LabeledField
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/LabeledField/CompactValueField
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/Text[Name is required]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/MuscleSelector
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/MuscleSelector
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/EnumDropdown
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/EnumDropdown
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/Row[6]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/Row[6]/CompactToggle
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/Row[6]/CompactToggle
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/SeedSourceDropdown
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/OutlinedTextField[8]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/OutlinedTextField[9]
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/LabeledField
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/LabeledField/CompactValueField
    ExerciseCreateScreen/Scaffold[1]/LazyColumn[0]/Spacer[11]

---
summary: 5 composables, 32 widget nodes
