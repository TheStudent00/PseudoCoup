# UI layout ledger -- RestTimerOverlay

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable RestTimerOverlay
  - Box  <container>   size: w=fill(rel) h=fill(rel)
      children: contentAlignment=Alignment.Center (rel) · non-layout: background
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally (rel)
      - Box  <container> [0/3]   size: w=wrap(rel) h=wrap(rel)
          children: contentAlignment=Alignment.Center (rel)
        - Box  <leaf> [0/2]   size: w=220.dp(abs) h=220.dp(abs)
        - Column  <container> [1/2]   size: w=wrap(rel) h=wrap(rel)
            children: horizontalAlignment=Alignment.CenterHorizontally (rel)
          - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
          - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [2/3]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.Center (rel)
        - OutlinedButton  <container> [0/3]   size: w=wrap(rel) h=48.dp(abs)
          - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
        - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        - OutlinedButton  <container> [2/3]   size: w=wrap(rel) h=48.dp(abs)
          - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 1 composables, 14 widget nodes
