# UI layout ledger -- PathsScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable LabeledStat
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text[label]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[value]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    LabeledStat/Column[0]
    LabeledStat/Column[0]/Text[label]
    LabeledStat/Column[0]/Text[value]

## @Composable ActivePathCard
  - WflCard  <container>   size: w=fill(rel) h=min = 240.dp(abs)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=WflTheme.tokens.cardPadding (abs)
      - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text[path.name]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - OutlinedButton[1]  <container>   size: w=wrap(rel) h=32.dp(abs)
          - Text[Leave path]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[it.tagline]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[4]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - LabeledStat  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - LabeledStat  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[5]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[The evidence]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=bottom = 4.dp (abs)
      - Box[7]  <container>   size: w=fill(rel) h=wrap(rel)
        - Text[it.evidenceSummary]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Box[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
            non-layout: background
      - Spacer[8]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ActivePathCard/WflCard
    ActivePathCard/WflCard/Column[0]
    ActivePathCard/WflCard/Column[0]/Row[0]
    ActivePathCard/WflCard/Column[0]/Row[0]/Text[path.name]
    ActivePathCard/WflCard/Column[0]/Row[0]/OutlinedButton[1]
    ActivePathCard/WflCard/Column[0]/Row[0]/OutlinedButton[1]/Text[Leave path]
    ActivePathCard/WflCard/Column[0]/Spacer[1]
    ActivePathCard/WflCard/Column[0]/Text[it.tagline]
    ActivePathCard/WflCard/Column[0]/Spacer[3]
    ActivePathCard/WflCard/Column[0]/Row[4]
    ActivePathCard/WflCard/Column[0]/Row[4]/LabeledStat
    ActivePathCard/WflCard/Column[0]/Row[4]/LabeledStat
    ActivePathCard/WflCard/Column[0]/Spacer[5]
    ActivePathCard/WflCard/Column[0]/Text[The evidence]
    ActivePathCard/WflCard/Column[0]/Box[7]
    ActivePathCard/WflCard/Column[0]/Box[7]/Text[it.evidenceSummary]
    ActivePathCard/WflCard/Column[0]/Box[7]/Box[1]
    ActivePathCard/WflCard/Column[0]/Spacer[8]

## @Composable EmptyPathsState
  - Column[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=vertical = 48.dp, horizontal = 24.dp (abs) · children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(16.dp) (rel)
    - Text[Start with your why.]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[A Path connects your training …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Spacer[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[3]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Find your path]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    EmptyPathsState/Column[0]
    EmptyPathsState/Column[0]/Text[Start with your why.]
    EmptyPathsState/Column[0]/Text[A Path connects your training …]
    EmptyPathsState/Column[0]/Spacer[2]
    EmptyPathsState/Column[0]/Button[3]
    EmptyPathsState/Column[0]/Button[3]/Text[Find your path]

## @Composable PathsScreen
  - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
    - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
      - Text[Paths are the why. Programs ar…]  <leaf>   size: w=fill(rel) h=wrap(rel)
          pad=bottom = 4.dp (abs)
      - EmptyPathsState  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ActivePathCard  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Box[3]  <container>   size: w=fill(rel) h=wrap(rel)
          children: contentAlignment=Alignment.Center (rel)
        - Button[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          - Icon[desc=null]  <leaf>   size: w=16.dp(abs) h=16.dp(abs)
          - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          - Text[Add a second path]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - AnimatedVisibility[1]  <container>   size: w=fill(rel) h=fill(rel)
        pad=top = innerPadding.calculateTopPadding() (rel)
      - PathSelectionSheet  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    PathsScreen/Box[0]
    PathsScreen/Box[0]/LazyColumn[0]
    PathsScreen/Box[0]/LazyColumn[0]/Text[Paths are the why. Programs ar…]
    PathsScreen/Box[0]/LazyColumn[0]/EmptyPathsState
    PathsScreen/Box[0]/LazyColumn[0]/ActivePathCard
    PathsScreen/Box[0]/LazyColumn[0]/Box[3]
    PathsScreen/Box[0]/LazyColumn[0]/Box[3]/Button[0]
    PathsScreen/Box[0]/LazyColumn[0]/Box[3]/Button[0]/Icon[desc=null]
    PathsScreen/Box[0]/LazyColumn[0]/Box[3]/Button[0]/Spacer[1]
    PathsScreen/Box[0]/LazyColumn[0]/Box[3]/Button[0]/Text[Add a second path]
    PathsScreen/Box[0]/AnimatedVisibility[1]
    PathsScreen/Box[0]/AnimatedVisibility[1]/PathSelectionSheet

---
summary: 4 composables, 39 widget nodes
