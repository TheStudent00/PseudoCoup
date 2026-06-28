# UI layout ledger -- PathsScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable LabeledStat
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable ActivePathCard
  - WflCard  <container>   size: w=fill(rel) h=min = 240.dp(abs)
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=WflTheme.tokens.cardPadding (abs)
      - Row  <container> [0/9]   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
        - OutlinedButton  <container> [1/2]   size: w=wrap(rel) h=32.dp(abs)
          - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [1/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [2/9]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [3/9]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [4/9]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - LabeledStat  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
        - LabeledStat  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [5/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [6/9]   size: w=wrap(rel) h=wrap(rel)
          pad=bottom = 4.dp (abs)
      - Box  <container> [7/9]   size: w=fill(rel) h=wrap(rel)
        - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
        - Box  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
            non-layout: background
      - Spacer  <leaf> [8/9]   size: w=wrap(rel) h=wrap(rel)

## @Composable EmptyPathsState
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      pad=vertical = 48.dp, horizontal = 24.dp (abs) · children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(16.dp) (rel)
    - Text  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [3/4]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable PathsScreen
  - Box  <container>   size: w=fill(rel) h=fill(rel)
    - LazyColumn  <container> [0/2]   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
      - Text  <leaf> [0/4]   size: w=fill(rel) h=wrap(rel)
          pad=bottom = 4.dp (abs)
      - EmptyPathsState  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
      - ActivePathCard  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
      - Box  <container> [3/4]   size: w=fill(rel) h=wrap(rel)
          children: contentAlignment=Alignment.Center (rel)
        - Button  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
          - Icon  <leaf> [0/3]   size: w=16.dp(abs) h=16.dp(abs)
          - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
          - Text  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)
    - AnimatedVisibility  <container> [1/2]   size: w=fill(rel) h=fill(rel)
        pad=top = innerPadding.calculateTopPadding() (rel)
      - PathSelectionSheet  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 4 composables, 39 widget nodes
