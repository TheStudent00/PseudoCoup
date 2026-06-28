# UI layout ledger -- ExerciseCreateScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable SeedSourceDropdown
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
    - LabeledField  <container> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - CompactDropdown  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
    - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable EnumDropdown
  - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
    - CompactDropdown  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)

## @Composable MuscleSelector
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
    - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - CompactMultiSelectDropdown  <leaf> [1/3]   size: w=fill(rel) h=wrap(rel)
    - Text  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)

## @Composable CompactToggle
  - Row  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalAlignment=Alignment.CenterVertically (rel)
    - Text  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
    - Switch  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
        non-layout: scale

## @Composable ExerciseCreateScreen
  - LaunchedEffect  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
  - Scaffold  <container> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn  <container> [0/1]   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(20.dp) (rel)
      - LabeledField  <container> [0/12]   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [1/12]   size: w=wrap(rel) h=wrap(rel)
      - MuscleSelector  <leaf> [2/12]   size: w=wrap(rel) h=wrap(rel)
      - MuscleSelector  <leaf> [3/12]   size: w=wrap(rel) h=wrap(rel)
      - EnumDropdown  <leaf> [4/12]   size: w=wrap(rel) h=wrap(rel)
      - EnumDropdown  <leaf> [5/12]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [6/12]   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - CompactToggle  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
        - CompactToggle  <leaf> [1/2]   size: w=weight(1f)(rel) h=wrap(rel)
      - SeedSourceDropdown  <leaf> [7/12]   size: w=wrap(rel) h=wrap(rel)
      - OutlinedTextField  <leaf> [8/12]   size: w=fill(rel) h=wrap(rel)
      - OutlinedTextField  <leaf> [9/12]   size: w=fill(rel) h=wrap(rel)
      - LabeledField  <container> [10/12]   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
      - Spacer  <leaf> [11/12]   size: w=wrap(rel) h=wrap(rel)

---
summary: 5 composables, 32 widget nodes
