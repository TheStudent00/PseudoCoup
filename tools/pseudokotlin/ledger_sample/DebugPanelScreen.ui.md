# UI layout ledger -- DebugPanelScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable ChipButton
  - OutlinedButton  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable Section
  - Text  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=top = 8.dp (abs)

## @Composable DebugPanelScreen
  - AlertDialog  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
  - Column  <container> [0/2]   size: w=fill(rel) h=fill(rel)
      pad=16.dp (abs) · children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel) · non-layout: verticalScroll
    - Text  <leaf> [0/26]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/26]   size: w=wrap(rel) h=wrap(rel)
    - WflCard  <container> [2/26]   size: w=fill(rel) h=wrap(rel)
      - Column  <container> [0/1]   size: w=wrap(rel) h=wrap(rel)
          children: verticalArrangement=Arrangement.spacedBy(4.dp) (rel)
        - Text  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
        - Text  <leaf> [3/4]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [3/26]   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf> [4/26]   size: w=wrap(rel) h=wrap(rel)
    - FlowRow  <container> [5/26]   size: w=wrap(rel) h=wrap(rel)
        children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
      - ChipButton  <leaf> [0/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [1/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [2/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [3/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [4/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [5/7]   size: w=wrap(rel) h=wrap(rel)
      - ChipButton  <leaf> [6/7]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [6/26]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf> [7/26]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [8/26]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [9/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [10/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [11/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [12/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf> [13/26]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [14/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [15/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [16/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [17/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf> [18/26]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [19/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [20/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [21/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [22/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - Section  <leaf> [23/26]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [24/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
    - OutlinedButton  <container> [25/26]   size: w=fill(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

---
summary: 3 composables, 58 widget nodes
