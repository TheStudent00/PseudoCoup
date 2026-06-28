# UI layout ledger -- PathSelectionSheet

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable PathCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Row  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=16.dp (abs) · children: verticalAlignment=Alignment.Top (rel)
      - Column  <container> [0/3]   size: w=weight(1f)(rel) h=wrap(rel)
        - Text  <leaf> [0/5]   size: w=wrap(rel) h=wrap(rel)
        - Spacer  <leaf> [1/5]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [2/5]   size: w=wrap(rel) h=wrap(rel)
        - Spacer  <leaf> [3/5]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [4/5]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
      - Surface  <container> [2/3]   size: w=28.dp(abs) h=28.dp(abs)
        - Box  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
            children: contentAlignment=Alignment.Center (rel)
          - Icon  <leaf> [0/1]   size: w=16.dp(abs) h=16.dp(abs)

## @Composable SectionHeader
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
    - HorizontalDivider  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
        pad=top = 8.dp, bottom = 16.dp (abs)
    - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable PathSelectionSheet
  - Scaffold  <container>   size: w=fill(rel) h=fill(rel)
    - LazyColumn  <container> [0/1]   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
      - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
      - Column  <container> [2/3]   size: w=wrap(rel) h=wrap(rel)
        - PathCard  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
        - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        - LabeledField  <container> [2/3]   size: w=wrap(rel) h=wrap(rel)
          - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)

---
summary: 3 composables, 24 widget nodes
