# UI layout ledger -- GymListScreen

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

## @Composable GymListItem
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=WflTheme.tokens.cardPadding (abs)
      - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel)
        - Text[gym.name]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - AssistChip[1]  <leaf>   size: w=wrap(rel) h=32.dp(abs)
        - OutlinedButton[2]  <container>   size: w=wrap(rel) h=32.dp(abs)
          - Text[Set active]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[${type.emoji} ${type.displayNa…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[4]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(WflTheme.tokens.screenMargin) (rel)
        - LabeledStat  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[5]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[Equipment]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=bottom = 4.dp (abs)
      - Box[7]  <container>   size: w=fill(rel) h=wrap(rel)
        - Text[equipmentNames]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Box[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
            non-layout: background
      - Text[No equipment listed]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=top = 4.dp (abs)
      - Spacer[9]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[10]  <container>   size: w=fill(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.End (rel)
        - TextButton[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
              pad=end = 4.dp (abs)
          - Text[Delete gym]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    GymListItem/WflCard
    GymListItem/WflCard/Column[0]
    GymListItem/WflCard/Column[0]/Row[0]
    GymListItem/WflCard/Column[0]/Row[0]/Text[gym.name]
    GymListItem/WflCard/Column[0]/Row[0]/AssistChip[1]
    GymListItem/WflCard/Column[0]/Row[0]/OutlinedButton[2]
    GymListItem/WflCard/Column[0]/Row[0]/OutlinedButton[2]/Text[Set active]
    GymListItem/WflCard/Column[0]/Spacer[1]
    GymListItem/WflCard/Column[0]/Text[${type.emoji} ${type.displayNa…]
    GymListItem/WflCard/Column[0]/Spacer[3]
    GymListItem/WflCard/Column[0]/Row[4]
    GymListItem/WflCard/Column[0]/Row[4]/LabeledStat
    GymListItem/WflCard/Column[0]/Spacer[5]
    GymListItem/WflCard/Column[0]/Text[Equipment]
    GymListItem/WflCard/Column[0]/Box[7]
    GymListItem/WflCard/Column[0]/Box[7]/Text[equipmentNames]
    GymListItem/WflCard/Column[0]/Box[7]/Box[1]
    GymListItem/WflCard/Column[0]/Text[No equipment listed]
    GymListItem/WflCard/Column[0]/Spacer[9]
    GymListItem/WflCard/Column[0]/Row[10]
    GymListItem/WflCard/Column[0]/Row[10]/TextButton[0]
    GymListItem/WflCard/Column[0]/Row[10]/TextButton[0]/Icon[desc=null]
    GymListItem/WflCard/Column[0]/Row[10]/TextButton[0]/Text[Delete gym]

## @Composable GymListScreen
  - Scaffold[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
      - Text[No gyms yet. Tap + to add one.]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn[1]  <container>   size: w=fill(rel) h=fill(rel)
        pad=innerPadding (rel) · children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
      - GymListItem  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    GymListScreen/Scaffold[0]
    GymListScreen/Scaffold[0]/Box[0]
    GymListScreen/Scaffold[0]/Box[0]/Text[No gyms yet. Tap + to add one.]
    GymListScreen/Scaffold[0]/LazyColumn[1]
    GymListScreen/Scaffold[0]/LazyColumn[1]/GymListItem

---
summary: 3 composables, 31 widget nodes
