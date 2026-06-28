# UI layout ledger -- WorkoutWarmupScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable WarmupSelecting
  - Column  <container>   size: w=fill(rel) h=fill(rel)
      pad=horizontal = 16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(16.dp) (rel) · non-layout: verticalScroll
    - Spacer  <leaf> [0/6]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/6]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [2/6]   size: w=wrap(rel) h=wrap(rel)
    - ConditioningActivityPicker  <leaf> [3/6]   size: w=wrap(rel) h=wrap(rel)
    - TextButton  <container> [4/6]   size: w=wrap(rel) h=wrap(rel)
        align=Alignment.CenterHorizontally (rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [5/6]   size: w=wrap(rel) h=wrap(rel)

## @Composable WorkoutWarmupScreen
  - Scaffold  <container>   size: w=wrap(rel) h=wrap(rel)
    - Column  <container> [0/1]   size: w=fill(rel) h=fill(rel)
        pad=innerPadding (rel)
      - WarmupSelecting  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
      - ConditioningTimerView  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
      - ConditioningFinishedView  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 13 widget nodes
