# UI layout ledger -- ProgramEndDecision

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable DecisionCard
  - Surface  <container>   size: w=fill(rel) h=wrap(rel)
      non-layout: clickable
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
      - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable ProgramEndDecision
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
    - Text  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
    - DecisionCard  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
    - DecisionCard  <leaf> [3/4]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 9 widget nodes
