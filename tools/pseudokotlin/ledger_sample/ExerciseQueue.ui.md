# UI layout ledger -- ExerciseQueue

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable ExerciseQueue
  - LaunchedEffect  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
  - Column  <container> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp (abs)
    - LazyRow  <container> [1/2]   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - FilterChip  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 1 composables, 5 widget nodes
