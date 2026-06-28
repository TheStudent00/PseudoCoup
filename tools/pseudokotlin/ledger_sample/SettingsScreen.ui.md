# UI layout ledger -- SettingsScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable NotificationRow
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.itemGap (abs)
    - Text  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        pad=top = 1.dp, bottom = 8.dp (abs)
    - SingleChoiceSegmentedButtonRow  <container> [2/3]   size: w=fill(rel) h=wrap(rel)
      - SegmentedButton  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable SettingsRow
  - Row  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.itemGap (abs) · children: verticalAlignment=Alignment.CenterVertically (rel) · non-layout: then, clickable
    - Column  <container> [0/1]   size: w=weight(1f)(rel) h=wrap(rel)
        pad=end = 12.dp (abs)
      - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

## @Composable SectionHeader
  - Text  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=start = WflTheme.tokens.screenMargin, top = 20.dp, bottom = WflTheme.tokens.itemGap (abs)

## @Composable SettingsScreen
  - AlertDialog  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - LaunchedEffect  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
  - Column  <container> [0/4]   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel)
    - Column  <container> [0/2]   size: w=fill(rel) h=fill(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.Center (rel)
      - CircularProgressIndicator  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Column  <container> [1/2]   size: w=fill(rel) h=fill(rel)
        pad=bottom = 32.dp (abs) · non-layout: verticalScroll
      - SectionHeader  <leaf> [0/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [1/28]   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf> [0/1]   size: w=140.dp(abs) h=wrap(rel)
      - HorizontalDivider  <leaf> [2/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container> [3/28]   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf> [0/1]   size: w=140.dp(abs) h=wrap(rel)
      - SectionHeader  <leaf> [4/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [5/28]   size: w=wrap(rel) h=wrap(rel)
        - CompactDropdown  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [6/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container> [7/28]   size: w=wrap(rel) h=wrap(rel)
        - CompactDropdown  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [8/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [9/28]   size: w=wrap(rel) h=wrap(rel)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [10/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container> [11/28]   size: w=wrap(rel) h=wrap(rel)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [12/28]   size: w=wrap(rel) h=wrap(rel)
      - NotificationRow  <leaf> [13/28]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [14/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf> [15/28]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [16/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf> [17/28]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [18/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - NotificationRow  <leaf> [19/28]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [20/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [21/28]   size: w=wrap(rel) h=wrap(rel)
        - CircularProgressIndicator  <leaf> [0/2]   size: w=20.dp(abs) h=20.dp(abs)
        - Icon  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - HorizontalDivider  <leaf> [22/28]   size: w=wrap(rel) h=wrap(rel)
          pad=horizontal = WflTheme.tokens.screenMargin (abs)
      - SettingsRow  <container> [23/28]   size: w=wrap(rel) h=wrap(rel)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [24/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [25/28]   size: w=wrap(rel) h=wrap(rel)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf> [26/28]   size: w=wrap(rel) h=wrap(rel)
      - SettingsRow  <container> [27/28]   size: w=wrap(rel) h=wrap(rel)
        - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 4 composables, 56 widget nodes
