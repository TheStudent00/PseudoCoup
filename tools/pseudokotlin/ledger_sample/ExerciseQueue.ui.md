# UI layout ledger -- ExerciseQueue

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable ExerciseQueue
  - LaunchedEffect[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Column[1]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text[UP NEXT]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp (abs)
    - LazyRow[1]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - FilterChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ExerciseQueue/LaunchedEffect[0]
    ExerciseQueue/Column[1]
    ExerciseQueue/Column[1]/Text[UP NEXT]
    ExerciseQueue/Column[1]/LazyRow[1]
    ExerciseQueue/Column[1]/LazyRow[1]/FilterChip[0]

---
summary: 1 composables, 5 widget nodes
