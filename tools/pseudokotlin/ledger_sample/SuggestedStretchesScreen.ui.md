# UI layout ledger -- SuggestedStretchesScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable StretchCard
  - Surface[0]  <container>   size: w=fill(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=WflTheme.tokens.cardPadding (abs)
      - Text[name]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[For your |, ]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=top = 2.dp (abs)
      - Text[it]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=top = 8.dp (abs)
  ids:
    StretchCard/Surface[0]
    StretchCard/Surface[0]/Column[0]
    StretchCard/Surface[0]/Column[0]/Text[name]
    StretchCard/Surface[0]/Column[0]/Text[For your |, ]
    StretchCard/Surface[0]/Column[0]/Text[it]

## @Composable MuscleChips
  - FlowRow[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: horizontalArrangement=Arrangement.spacedBy(6.dp) (rel)
    - Surface[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[muscle.displayName()]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = 8.dp, vertical = 4.dp (abs)
  ids:
    MuscleChips/FlowRow[0]
    MuscleChips/FlowRow[0]/Surface[0]
    MuscleChips/FlowRow[0]/Surface[0]/Text[muscle.displayName()]

## @Composable SuggestedStretchesScreen
  - Scaffold[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - Spacer[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[A few stretches for the whole …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[Hold each for 30–60 seconds wh…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=top = 4.dp, bottom = 4.dp (abs)
      - MuscleChips  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[4]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[No matching stretches found — …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=vertical = 16.dp (abs)
      - StretchCard  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[7]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SuggestedStretchesScreen/Scaffold[0]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Spacer[0]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Text[A few stretches for the whole …]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Text[Hold each for 30–60 seconds wh…]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/MuscleChips
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Spacer[4]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Text[No matching stretches found — …]
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/StretchCard
    SuggestedStretchesScreen/Scaffold[0]/LazyColumn[0]/Spacer[7]

---
summary: 3 composables, 18 widget nodes
