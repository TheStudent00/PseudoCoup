# UI layout ledger -- WflCard

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable WflCardTitle
  - Text  <leaf>   size: w=wrap(rel) h=wrap(rel)

## @Composable WflCard
  - RoundedCornerShape  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - BorderStroke  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - Card  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - Card  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 5 widget nodes
