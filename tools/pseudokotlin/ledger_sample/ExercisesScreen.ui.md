# UI layout ledger -- ExercisesScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable ExerciseListItem
  - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=start = WflTheme.tokens.screenMargin, end = WflTheme.tokens.itemGap (abs) · children: verticalAlignment=Alignment.CenterVertically (rel) · non-layout: clickable
    - Column[0]  <container>   size: w=weight(1f)(rel) h=wrap(rel)
        pad=vertical = WflTheme.tokens.itemGap (abs)
      - Text[exercise.name]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[$muscles · ${exercise.equipmen…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Icon[desc=Remove from favorites|Add to f…]  <leaf>   size: w=24.dp(abs) h=24.dp(abs)
        pad=WflTheme.tokens.itemGap (abs) · non-layout: clickable
  ids:
    ExerciseListItem/Row[0]
    ExerciseListItem/Row[0]/Column[0]
    ExerciseListItem/Row[0]/Column[0]/Text[exercise.name]
    ExerciseListItem/Row[0]/Column[0]/Text[$muscles · ${exercise.equipmen…]
    ExerciseListItem/Row[0]/Icon[desc=Remove from favorites|Add to f…]

## @Composable SectionHeader
  - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.rowVertical (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: clickable
    - Text[$label · $count]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Icon[desc=Collapse|Expand]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SectionHeader/Row[0]
    SectionHeader/Row[0]/Text[$label · $count]
    SectionHeader/Row[0]/Icon[desc=Collapse|Expand]

## @Composable ExercisesScreen
  - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
    - Scaffold[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
        - PrimaryScrollableTabRow[0]  <container>   size: w=fill(rel) h=wrap(rel)
          - Tab[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - SearchBar[1]  <leaf>   size: w=fill(rel) h=wrap(rel)
            pad=horizontal = WflTheme.tokens.screenMargin, vertical = 4.dp (abs)
        - Box[2]  <container>   size: w=fill(rel) h=wrap(rel)
            pad=WflTheme.tokens.blockGap (abs) · children: contentAlignment=Alignment.Center (rel)
          - Text[No exercises found.]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - ExerciseListItem  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - ExerciseListItem  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ExercisesScreen/Box[0]
    ExercisesScreen/Box[0]/Scaffold[0]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/PrimaryScrollableTabRow[0]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/PrimaryScrollableTabRow[0]/Tab[0]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/SearchBar[1]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/Box[2]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/Box[2]/Text[No exercises found.]
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/SectionHeader
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/ExerciseListItem
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/SectionHeader
    ExercisesScreen/Box[0]/Scaffold[0]/LazyColumn[0]/ExerciseListItem

---
summary: 3 composables, 20 widget nodes
