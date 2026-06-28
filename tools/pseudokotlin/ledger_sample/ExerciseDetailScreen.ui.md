# UI layout ledger -- ExerciseDetailScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable DetailSection
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
    - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable ExerciseDetailContent
  - LazyColumn  <container>   size: w=fill(rel) h=fill(rel)
      children: verticalArrangement=Arrangement.spacedBy(WflTheme.tokens.sectionGap) (rel)
    - FlowRow  <container> [0/9]   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
      - SuggestionChip  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip  <leaf> [3/4]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [1/9]   size: w=wrap(rel) h=wrap(rel)
      - FlowRow  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
        - AssistChip  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [2/9]   size: w=wrap(rel) h=wrap(rel)
      - FlowRow  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
        - SuggestionChip  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [3/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - HorizontalDivider  <leaf> [4/9]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [5/9]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [6/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [7/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container> [8/9]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable ExerciseDetailScreen
  - LaunchedEffect  <leaf> [0/5]   size: w=wrap(rel) h=wrap(rel)
  - LaunchedEffect  <leaf> [0/5]   size: w=wrap(rel) h=wrap(rel)
  - Scaffold  <container> [0/5]   size: w=wrap(rel) h=wrap(rel)
    - ExerciseDetailContent  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog  <leaf> [0/5]   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog  <leaf> [0/5]   size: w=wrap(rel) h=wrap(rel)

---
summary: 3 composables, 30 widget nodes
