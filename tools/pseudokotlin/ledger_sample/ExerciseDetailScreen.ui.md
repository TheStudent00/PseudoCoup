# UI layout ledger -- ExerciseDetailScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable DetailSection
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: verticalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
    - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    DetailSection/Column[0]
    DetailSection/Column[0]/Text[title]

## @Composable ExerciseDetailContent
  - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
      children: verticalArrangement=Arrangement.spacedBy(WflTheme.tokens.sectionGap) (rel)
    - FlowRow[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
      - SuggestionChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SuggestionChip[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - FlowRow[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
        - AssistChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - FlowRow[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
        - SuggestionChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[${exercise.movementPattern.dis…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - HorizontalDivider[4]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Spacer[5]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[exercise.instructions]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[exercise.cues]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[exercise.videoLink]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ExerciseDetailContent/LazyColumn[0]
    ExerciseDetailContent/LazyColumn[0]/FlowRow[0]
    ExerciseDetailContent/LazyColumn[0]/FlowRow[0]/SuggestionChip[0]
    ExerciseDetailContent/LazyColumn[0]/FlowRow[0]/SuggestionChip[1]
    ExerciseDetailContent/LazyColumn[0]/FlowRow[0]/SuggestionChip[2]
    ExerciseDetailContent/LazyColumn[0]/FlowRow[0]/SuggestionChip[3]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/FlowRow[0]
    ExerciseDetailContent/LazyColumn[0]/DetailSection/FlowRow[0]/AssistChip[0]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/FlowRow[0]
    ExerciseDetailContent/LazyColumn[0]/DetailSection/FlowRow[0]/SuggestionChip[0]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/Text[${exercise.movementPattern.dis…]
    ExerciseDetailContent/LazyColumn[0]/HorizontalDivider[4]
    ExerciseDetailContent/LazyColumn[0]/Spacer[5]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/Text[exercise.instructions]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/Text[exercise.cues]
    ExerciseDetailContent/LazyColumn[0]/DetailSection
    ExerciseDetailContent/LazyColumn[0]/DetailSection/Text[exercise.videoLink]

## @Composable ExerciseDetailScreen
  - LaunchedEffect[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - LaunchedEffect[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Scaffold[2]  <container>   size: w=wrap(rel) h=wrap(rel)
    - ExerciseDetailContent  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog[4]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ExerciseDetailScreen/LaunchedEffect[0]
    ExerciseDetailScreen/LaunchedEffect[1]
    ExerciseDetailScreen/Scaffold[2]
    ExerciseDetailScreen/Scaffold[2]/ExerciseDetailContent
    ExerciseDetailScreen/AlertDialog[3]
    ExerciseDetailScreen/AlertDialog[4]

---
summary: 3 composables, 30 widget nodes
