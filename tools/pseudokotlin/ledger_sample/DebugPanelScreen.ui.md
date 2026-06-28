# UI layout ledger -- DebugPanelScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable ChipButton
  - OutlinedButton[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text[label]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ChipButton/OutlinedButton[0]
    ChipButton/OutlinedButton[0]/Text[label]

## @Composable Section
  - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=top = 8.dp (abs)
  ids:
    Section/Text[title]

## @Composable DebugPanelScreen
  - AlertDialog[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Column[1]  <container>   size: w=fill(rel) h=fill(rel)
      pad=16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel) · non-layout: verticalScroll
    - Text[Debug Panel]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[Debug builds only. Shifts the …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
      - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
        - Text[Effective now]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[nowLabel]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[Offset: ${if (offsetDays >= 0)…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[it]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[it]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - FlowRow[5]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[6]  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[Reset to real time]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[Then advance time to cross a g…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[9]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Seed completed session (today)]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[10]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Seed completed session (20 day…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[11]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Arm block-completion celebrati…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[12]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Clear all sessions]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[14]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Maintenance — 14 days]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[15]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Deload level — 14 days]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[16]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Snail's pace — 14 days]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[17]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Bodyweight-only — 7 days]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[19]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Send test diagnostics (GitHub …]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[20]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Refresh DB info]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[21]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Check & repair program data]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[22]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Re-sync curated programs (keep…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[24]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Wipe & re-seed database]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton[25]  <container>   size: w=fill(rel) h=wrap(rel)
      - Text[Simulate crash (kills the app)]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    DebugPanelScreen/AlertDialog[0]
    DebugPanelScreen/Column[1]
    DebugPanelScreen/Column[1]/Text[Debug Panel]
    DebugPanelScreen/Column[1]/Text[Debug builds only. Shifts the …]
    DebugPanelScreen/Column[1]/WflCard
    DebugPanelScreen/Column[1]/WflCard/Column[0]
    DebugPanelScreen/Column[1]/WflCard/Column[0]/Text[Effective now]
    DebugPanelScreen/Column[1]/WflCard/Column[0]/Text[nowLabel]
    DebugPanelScreen/Column[1]/WflCard/Column[0]/Text[Offset: ${if (offsetDays >= 0)…]
    DebugPanelScreen/Column[1]/WflCard/Column[0]/Text[it]
    DebugPanelScreen/Column[1]/Text[it]
    DebugPanelScreen/Column[1]/Section
    DebugPanelScreen/Column[1]/FlowRow[5]
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/FlowRow[5]/ChipButton
    DebugPanelScreen/Column[1]/OutlinedButton[6]
    DebugPanelScreen/Column[1]/OutlinedButton[6]/Text[Reset to real time]
    DebugPanelScreen/Column[1]/Section
    DebugPanelScreen/Column[1]/Text[Then advance time to cross a g…]
    DebugPanelScreen/Column[1]/Button[9]
    DebugPanelScreen/Column[1]/Button[9]/Text[Seed completed session (today)]
    DebugPanelScreen/Column[1]/Button[10]
    DebugPanelScreen/Column[1]/Button[10]/Text[Seed completed session (20 day…]
    DebugPanelScreen/Column[1]/Button[11]
    DebugPanelScreen/Column[1]/Button[11]/Text[Arm block-completion celebrati…]
    DebugPanelScreen/Column[1]/OutlinedButton[12]
    DebugPanelScreen/Column[1]/OutlinedButton[12]/Text[Clear all sessions]
    DebugPanelScreen/Column[1]/Section
    DebugPanelScreen/Column[1]/Button[14]
    DebugPanelScreen/Column[1]/Button[14]/Text[Maintenance — 14 days]
    DebugPanelScreen/Column[1]/Button[15]
    DebugPanelScreen/Column[1]/Button[15]/Text[Deload level — 14 days]
    DebugPanelScreen/Column[1]/Button[16]
    DebugPanelScreen/Column[1]/Button[16]/Text[Snail's pace — 14 days]
    DebugPanelScreen/Column[1]/Button[17]
    DebugPanelScreen/Column[1]/Button[17]/Text[Bodyweight-only — 7 days]
    DebugPanelScreen/Column[1]/Section
    DebugPanelScreen/Column[1]/Button[19]
    DebugPanelScreen/Column[1]/Button[19]/Text[Send test diagnostics (GitHub …]
    DebugPanelScreen/Column[1]/OutlinedButton[20]
    DebugPanelScreen/Column[1]/OutlinedButton[20]/Text[Refresh DB info]
    DebugPanelScreen/Column[1]/OutlinedButton[21]
    DebugPanelScreen/Column[1]/OutlinedButton[21]/Text[Check & repair program data]
    DebugPanelScreen/Column[1]/OutlinedButton[22]
    DebugPanelScreen/Column[1]/OutlinedButton[22]/Text[Re-sync curated programs (keep…]
    DebugPanelScreen/Column[1]/Section
    DebugPanelScreen/Column[1]/OutlinedButton[24]
    DebugPanelScreen/Column[1]/OutlinedButton[24]/Text[Wipe & re-seed database]
    DebugPanelScreen/Column[1]/OutlinedButton[25]
    DebugPanelScreen/Column[1]/OutlinedButton[25]/Text[Simulate crash (kills the app)]

---
summary: 3 composables, 58 widget nodes
