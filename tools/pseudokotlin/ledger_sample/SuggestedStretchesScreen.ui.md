# UI layout ledger -- SuggestedStretchesScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable StretchCard
  - Surface  <container>   size: w=fill(rel) h=wrap(rel)
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=WflTheme.tokens.cardPadding (abs)
      - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
          pad=top = 2.dp (abs)
      - Text  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)
          pad=top = 8.dp (abs)

## @Composable MuscleChips
  - FlowRow  <container>   size: w=wrap(rel) h=wrap(rel)
      children: horizontalArrangement=Arrangement.spacedBy(6.dp) (rel)
    - Surface  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = 8.dp, vertical = 4.dp (abs)

## @Composable SuggestedStretchesScreen
  - Scaffold  <container>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn  <container> [0/1]   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - Spacer  <leaf> [0/8]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/8]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [2/8]   size: w=wrap(rel) h=wrap(rel)
          pad=top = 4.dp, bottom = 4.dp (abs)
      - MuscleChips  <leaf> [3/8]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [4/8]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [5/8]   size: w=wrap(rel) h=wrap(rel)
          pad=vertical = 16.dp (abs)
      - StretchCard  <leaf> [6/8]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [7/8]   size: w=wrap(rel) h=wrap(rel)

---
summary: 3 composables, 18 widget nodes
