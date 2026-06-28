# UI layout ledger -- WeightRepsInput

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable RepsInput
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = 16.dp (abs)
    - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
    - Row  <container> [2/3]   size: w=fill(rel) h=wrap(rel)
        children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
      - FilledIconButton  <container> [0/3]   size: w=56.dp(abs) h=56.dp(abs)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/3]   size: w=160.dp(abs) h=wrap(rel)
      - FilledIconButton  <container> [2/3]   size: w=56.dp(abs) h=56.dp(abs)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable WeightInput
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = 16.dp (abs)
    - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
    - Row  <container> [2/3]   size: w=fill(rel) h=wrap(rel)
        children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
      - FilledIconButton  <container> [0/3]   size: w=56.dp(abs) h=56.dp(abs)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Column  <container> [1/3]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalAlignment=Alignment.CenterHorizontally (rel)
        - Text  <leaf> [0/2]   size: w=160.dp(abs) h=wrap(rel)
        - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - FilledIconButton  <container> [2/3]   size: w=56.dp(abs) h=56.dp(abs)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 20 widget nodes
