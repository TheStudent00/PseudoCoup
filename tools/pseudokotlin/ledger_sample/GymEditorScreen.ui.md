# UI layout ledger -- GymEditorScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable AddEquipmentDialog
  - AlertDialog[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    AddEquipmentDialog/AlertDialog[0]

## @Composable EquipmentRow
  - ListItem[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    EquipmentRow/ListItem[0]

## @Composable GymEditorScreen
  - LaunchedEffect[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Scaffold[1]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=innerPadding (rel) · children: contentAlignment=Alignment.Center (rel)
      - CircularProgressIndicator[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn[1]  <container>   size: w=fill(rel) h=fill(rel)
        pad=innerPadding (rel) · children: verticalArrangement=Arrangement.spacedBy(WflTheme.tokens.itemGap) (rel)
      - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
          pad=vertical = WflTheme.tokens.itemGap (abs)
        - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Text[Equipment]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=top = WflTheme.tokens.itemGap, bottom = 4.dp (abs)
      - HorizontalDivider[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[No equipment added yet.]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=vertical = 8.dp (abs)
      - Row[4]  <container>   size: w=fill(rel) h=wrap(rel)
          pad=vertical = WflTheme.tokens.itemGap (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: clickable
        - Text[type.displayName()]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=Collapse|Expand]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - EquipmentRow  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[6]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - AddEquipmentDialog  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    GymEditorScreen/LaunchedEffect[0]
    GymEditorScreen/Scaffold[1]
    GymEditorScreen/Scaffold[1]/Box[0]
    GymEditorScreen/Scaffold[1]/Box[0]/CircularProgressIndicator[0]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/LabeledField
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/LabeledField/CompactValueField
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Text[Equipment]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/HorizontalDivider[2]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Text[No equipment added yet.]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Row[4]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Row[4]/Text[type.displayName()]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Row[4]/Icon[desc=Collapse|Expand]
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/EquipmentRow
    GymEditorScreen/Scaffold[1]/LazyColumn[1]/Spacer[6]
    GymEditorScreen/AddEquipmentDialog

---
summary: 3 composables, 18 widget nodes
