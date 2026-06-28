# UI layout ledger -- HistoryScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable StatLabel
  - Text  <leaf>   size: w=wrap(rel) h=wrap(rel)

## @Composable CardioCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
      - Row  <container> [0/4]   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Top, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
        - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [3/4]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - StatLabel  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf> [3/4]   size: w=wrap(rel) h=wrap(rel)

## @Composable SessionCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
      - Row  <container> [0/4]   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Top, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
        - Surface  <container> [1/2]   size: w=wrap(rel) h=wrap(rel)
          - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
              pad=horizontal = 6.dp, vertical = 2.dp (abs)
      - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [3/4]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - StatLabel  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)

## @Composable WeekHeader
  - Surface  <container>   size: w=wrap(rel) h=wrap(rel)
    - Row  <container> [0/1]   size: w=fill(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
      - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable HistoryScreen
  - Box  <container> [0/3]   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
    - CircularProgressIndicator  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
  - Box  <container> [0/3]   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
    - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
  - LazyColumn  <container> [0/3]   size: w=fill(rel) h=fill(rel)
    - WeekHeader  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
    - SessionCard  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 4.dp (abs)
    - CardioCard  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 4.dp (abs)
    - Spacer  <leaf> [3/4]   size: w=wrap(rel) h=wrap(rel)

---
summary: 5 composables, 40 widget nodes
