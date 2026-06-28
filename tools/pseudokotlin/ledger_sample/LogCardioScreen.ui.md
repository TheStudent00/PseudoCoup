# UI layout ledger -- LogCardioScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable CardioDatePickerDialog
  - DatePickerDialog[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - DatePicker[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    CardioDatePickerDialog/DatePickerDialog[0]
    CardioDatePickerDialog/DatePickerDialog[0]/DatePicker[0]

## @Composable LogCardioScreen
  - LaunchedEffect[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Scaffold[2]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp, vertical = 8.dp (abs) · non-layout: verticalScroll
      - Text[Log cardio or other activity s…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[Activity]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - FlowRow[4]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
        - FilterChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[5]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[When]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[7]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - OutlinedButton[8]  <container>   size: w=fill(rel) h=wrap(rel)
        - Icon[desc=null]  <leaf>   size: w=18.dp(abs) h=18.dp(abs)
        - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[whenLabel(state.selectedDate, …]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
      - CardioDatePickerDialog  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[10]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Spacer[12]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[Intensity]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[14]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SingleChoiceSegmentedButtonRow[15]  <container>   size: w=fill(rel) h=wrap(rel)
        - SegmentedButton[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[16]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[17]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(12.dp) (rel)
        - LabeledField  <container>   size: w=weight(1f)(rel) h=wrap(rel)
          - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
        - LabeledField  <container>   size: w=weight(1f)(rel) h=wrap(rel)
          - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Spacer[18]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - OutlinedTextField[19]  <leaf>   size: w=fill(rel) h=wrap(rel)
      - Spacer[20]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Button[21]  <container>   size: w=fill(rel) h=wrap(rel)
        - CircularProgressIndicator[0]  <leaf>   size: w=20.dp(abs) h=20.dp(abs)
        - Text[Save]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    LogCardioScreen/LaunchedEffect[0]
    LogCardioScreen/AlertDialog[1]
    LogCardioScreen/Scaffold[2]
    LogCardioScreen/Scaffold[2]/Column[0]
    LogCardioScreen/Scaffold[2]/Column[0]/Text[Log cardio or other activity s…]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[1]
    LogCardioScreen/Scaffold[2]/Column[0]/Text[Activity]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[3]
    LogCardioScreen/Scaffold[2]/Column[0]/FlowRow[4]
    LogCardioScreen/Scaffold[2]/Column[0]/FlowRow[4]/FilterChip[0]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[5]
    LogCardioScreen/Scaffold[2]/Column[0]/Text[When]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[7]
    LogCardioScreen/Scaffold[2]/Column[0]/OutlinedButton[8]
    LogCardioScreen/Scaffold[2]/Column[0]/OutlinedButton[8]/Icon[desc=null]
    LogCardioScreen/Scaffold[2]/Column[0]/OutlinedButton[8]/Spacer[1]
    LogCardioScreen/Scaffold[2]/Column[0]/OutlinedButton[8]/Text[whenLabel(state.selectedDate, …]
    LogCardioScreen/Scaffold[2]/Column[0]/CardioDatePickerDialog
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[10]
    LogCardioScreen/Scaffold[2]/Column[0]/LabeledField
    LogCardioScreen/Scaffold[2]/Column[0]/LabeledField/CompactValueField
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[12]
    LogCardioScreen/Scaffold[2]/Column[0]/Text[Intensity]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[14]
    LogCardioScreen/Scaffold[2]/Column[0]/SingleChoiceSegmentedButtonRow[15]
    LogCardioScreen/Scaffold[2]/Column[0]/SingleChoiceSegmentedButtonRow[15]/SegmentedButton[0]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[16]
    LogCardioScreen/Scaffold[2]/Column[0]/Row[17]
    LogCardioScreen/Scaffold[2]/Column[0]/Row[17]/LabeledField
    LogCardioScreen/Scaffold[2]/Column[0]/Row[17]/LabeledField/CompactValueField
    LogCardioScreen/Scaffold[2]/Column[0]/Row[17]/LabeledField
    LogCardioScreen/Scaffold[2]/Column[0]/Row[17]/LabeledField/CompactValueField
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[18]
    LogCardioScreen/Scaffold[2]/Column[0]/OutlinedTextField[19]
    LogCardioScreen/Scaffold[2]/Column[0]/Spacer[20]
    LogCardioScreen/Scaffold[2]/Column[0]/Button[21]
    LogCardioScreen/Scaffold[2]/Column[0]/Button[21]/CircularProgressIndicator[0]
    LogCardioScreen/Scaffold[2]/Column[0]/Button[21]/Text[Save]

---
summary: 2 composables, 40 widget nodes
