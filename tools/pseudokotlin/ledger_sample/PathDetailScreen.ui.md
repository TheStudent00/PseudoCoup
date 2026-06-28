# UI layout ledger -- PathDetailScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable DetailSection
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable PathDetailScreen
  - Scaffold  <container>   size: w=wrap(rel) h=wrap(rel)
    - Column  <container> [0/2]   size: w=fill(rel) h=fill(rel)
        pad=24.dp (abs)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn  <container> [1/2]   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(24.dp) (rel)
      - Text  <leaf> [0/6]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [1/6]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
        - SuggestionChip  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
        - SuggestionChip  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container> [2/6]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container> [3/6]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container> [4/6]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container> [5/6]   size: w=wrap(rel) h=wrap(rel)
        - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
            children: verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
          - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 20 widget nodes
