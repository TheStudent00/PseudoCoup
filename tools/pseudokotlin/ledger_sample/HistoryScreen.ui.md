# UI layout ledger -- HistoryScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable StatLabel
  - Text[text]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    StatLabel/Text[text]

## @Composable CardioCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
      - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Top, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text[cardio.type.displayName()]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - Text[Cardio]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[formatSessionDate(cardio.start…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[3]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    CardioCard/WflCard
    CardioCard/WflCard/Column[0]
    CardioCard/WflCard/Column[0]/Row[0]
    CardioCard/WflCard/Column[0]/Row[0]/Text[cardio.type.displayName()]
    CardioCard/WflCard/Column[0]/Row[0]/Text[Cardio]
    CardioCard/WflCard/Column[0]/Text[formatSessionDate(cardio.start…]
    CardioCard/WflCard/Column[0]/Spacer[2]
    CardioCard/WflCard/Column[0]/Row[3]
    CardioCard/WflCard/Column[0]/Row[3]/StatLabel
    CardioCard/WflCard/Column[0]/Row[3]/StatLabel
    CardioCard/WflCard/Column[0]/Row[3]/StatLabel
    CardioCard/WflCard/Column[0]/Row[3]/StatLabel

## @Composable SessionCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
      - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Top, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text[Ad-hoc Workout]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - Surface[1]  <container>   size: w=wrap(rel) h=wrap(rel)
          - Text[1 PR|${session.prCount} PRs]  <leaf>   size: w=wrap(rel) h=wrap(rel)
              pad=horizontal = 6.dp, vertical = 2.dp (abs)
      - Text[formatSessionDate(session.star…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[3]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(16.dp) (rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - StatLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SessionCard/WflCard
    SessionCard/WflCard/Column[0]
    SessionCard/WflCard/Column[0]/Row[0]
    SessionCard/WflCard/Column[0]/Row[0]/Text[Ad-hoc Workout]
    SessionCard/WflCard/Column[0]/Row[0]/Surface[1]
    SessionCard/WflCard/Column[0]/Row[0]/Surface[1]/Text[1 PR|${session.prCount} PRs]
    SessionCard/WflCard/Column[0]/Text[formatSessionDate(session.star…]
    SessionCard/WflCard/Column[0]/Spacer[2]
    SessionCard/WflCard/Column[0]/Row[3]
    SessionCard/WflCard/Column[0]/Row[3]/StatLabel
    SessionCard/WflCard/Column[0]/Row[3]/StatLabel
    SessionCard/WflCard/Column[0]/Row[3]/StatLabel

## @Composable WeekHeader
  - Surface[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 12.dp (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
      - Text[label]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[formatVolume(totalVolumeKg, un…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    WeekHeader/Surface[0]
    WeekHeader/Surface[0]/Row[0]
    WeekHeader/Surface[0]/Row[0]/Text[label]
    WeekHeader/Surface[0]/Row[0]/Text[formatVolume(totalVolumeKg, un…]

## @Composable HistoryScreen
  - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
    - CircularProgressIndicator[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Box[1]  <container>   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - Text[No workouts yet]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[Completed sessions and cardio …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - LazyColumn[2]  <container>   size: w=fill(rel) h=fill(rel)
    - WeekHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - SessionCard  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 4.dp (abs)
    - CardioCard  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 16.dp, vertical = 4.dp (abs)
    - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    HistoryScreen/Box[0]
    HistoryScreen/Box[0]/CircularProgressIndicator[0]
    HistoryScreen/Box[1]
    HistoryScreen/Box[1]/Column[0]
    HistoryScreen/Box[1]/Column[0]/Text[No workouts yet]
    HistoryScreen/Box[1]/Column[0]/Text[Completed sessions and cardio …]
    HistoryScreen/LazyColumn[2]
    HistoryScreen/LazyColumn[2]/WeekHeader
    HistoryScreen/LazyColumn[2]/SessionCard
    HistoryScreen/LazyColumn[2]/CardioCard
    HistoryScreen/LazyColumn[2]/Spacer[3]

---
summary: 5 composables, 40 widget nodes
