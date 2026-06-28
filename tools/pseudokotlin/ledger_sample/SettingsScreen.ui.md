# UI layout ledger -- SettingsScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable NotificationRow
  - Column[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.itemGap (abs)
    - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[subtitle]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=top = 1.dp, bottom = 8.dp (abs)
    - SingleChoiceSegmentedButtonRow[2]  <container>   size: w=fill(rel) h=wrap(rel)
      - SegmentedButton[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    NotificationRow/Column[0]
    NotificationRow/Column[0]/Text[title]
    NotificationRow/Column[0]/Text[subtitle]
    NotificationRow/Column[0]/SingleChoiceSegmentedButtonRow[2]
    NotificationRow/Column[0]/SingleChoiceSegmentedButtonRow[2]/SegmentedButton[0]

## @Composable SettingsRow
  - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.itemGap (abs) · children: verticalAlignment=Alignment.CenterVertically (rel) · non-layout: clickable, then
    - Column[0]  <container>   size: w=weight(1f)(rel) h=wrap(rel)
        pad=end = 12.dp (abs)
      - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[subtitle]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SettingsRow/Row[0]
    SettingsRow/Row[0]/Column[0]
    SettingsRow/Row[0]/Column[0]/Text[title]
    SettingsRow/Row[0]/Column[0]/Text[subtitle]

## @Composable SectionHeader
  - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=start = WflTheme.tokens.screenMargin, top = 20.dp, bottom = WflTheme.tokens.itemGap (abs)
  ids:
    SectionHeader/Text[title]

## @Composable SettingsScreen
  - AlertDialog[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - LaunchedEffect[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Column[3]  <container>   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel)
    - Column[0]  <container>   size: w=fill(rel) h=fill(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.Center (rel)
      - CircularProgressIndicator[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Column[1]  <container>   size: w=fill(rel) h=fill(rel)
        pad=bottom = 32.dp (abs) · non-layout: verticalScroll
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf>   size: w=140.dp(abs) h=wrap(rel)
      - HorizontalDivider[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf>   size: w=140.dp(abs) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactDropdown  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[6]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactDropdown  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[10]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - NotificationRow  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[14]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[16]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[18]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - CircularProgressIndicator[0]  <leaf>   size: w=20.dp(abs) h=20.dp(abs)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider[22]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container>   size: w=wrap(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SettingsScreen/AlertDialog[0]
    SettingsScreen/AlertDialog[1]
    SettingsScreen/LaunchedEffect[2]
    SettingsScreen/Column[3]
    SettingsScreen/Column[3]/Column[0]
    SettingsScreen/Column[3]/Column[0]/CircularProgressIndicator[0]
    SettingsScreen/Column[3]/Column[1]
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/CompactValueField
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[2]
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/CompactValueField
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/CompactDropdown
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[6]
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/CompactDropdown
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[10]
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/NotificationRow
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[14]
    SettingsScreen/Column[3]/Column[1]/NotificationRow
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[16]
    SettingsScreen/Column[3]/Column[1]/NotificationRow
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[18]
    SettingsScreen/Column[3]/Column[1]/NotificationRow
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/CircularProgressIndicator[0]
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]
    SettingsScreen/Column[3]/Column[1]/HorizontalDivider[22]
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]
    SettingsScreen/Column[3]/Column[1]/SectionHeader
    SettingsScreen/Column[3]/Column[1]/SettingsRow
    SettingsScreen/Column[3]/Column[1]/SettingsRow/Icon[desc=null]

---
summary: 4 composables, 56 widget nodes
