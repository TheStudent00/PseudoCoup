# UI layout ledger -- LogCardioScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable CardioDatePickerDialog
  - DatePickerDialog  <container>   size: w=wrap(rel) h=wrap(rel)
    - DatePicker  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable LogCardioScreen
  - LaunchedEffect  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
  - AlertDialog  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
  - Scaffold  <container> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - Column  <container> [0/1]   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp, vertical = 8.dp (abs) · non-layout: verticalScroll
      - Text  <leaf> [0/22]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [1/22]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [2/22]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [3/22]   size: w=wrap(rel) h=wrap(rel)
      - FlowRow  <container> [4/22]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
        - FilterChip  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [5/22]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [6/22]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [7/22]   size: w=wrap(rel) h=wrap(rel)
      - OutlinedButton  <container> [8/22]   size: w=fill(rel) h=wrap(rel)
        - Icon  <leaf> [0/3]   size: w=18.dp(abs) h=18.dp(abs)
        - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [2/3]   size: w=weight(1f)(rel) h=wrap(rel)
      - CardioDatePickerDialog  <leaf> [9/22]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [10/22]   size: w=wrap(rel) h=wrap(rel)
      - LabeledField  <container> [11/22]   size: w=wrap(rel) h=wrap(rel)
        - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
      - Spacer  <leaf> [12/22]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [13/22]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [14/22]   size: w=wrap(rel) h=wrap(rel)
      - SingleChoiceSegmentedButtonRow  <container> [15/22]   size: w=fill(rel) h=wrap(rel)
        - SegmentedButton  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [16/22]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [17/22]   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(12.dp) (rel)
        - LabeledField  <container> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
          - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
        - LabeledField  <container> [1/2]   size: w=weight(1f)(rel) h=wrap(rel)
          - CompactValueField  <leaf> [0/1]   size: w=fill(rel) h=wrap(rel)
      - Spacer  <leaf> [18/22]   size: w=wrap(rel) h=wrap(rel)
      - OutlinedTextField  <leaf> [19/22]   size: w=fill(rel) h=wrap(rel)
      - Spacer  <leaf> [20/22]   size: w=wrap(rel) h=wrap(rel)
      - Button  <container> [21/22]   size: w=fill(rel) h=wrap(rel)
        - CircularProgressIndicator  <leaf> [0/2]   size: w=20.dp(abs) h=20.dp(abs)
        - Text  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

---
summary: 2 composables, 40 widget nodes
