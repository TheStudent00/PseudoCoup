# UI layout ledger -- CompactControls

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable CompactMultiSelectDropdown
  - Box  <container>   size: w=wrap(rel) h=wrap(rel)
    - Row  <container> [0/2]   size: w=fill(rel) h=wrap(rel)
        pad=horizontal = 12.dp, vertical = 6.dp (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: border, clickable
      - Text  <leaf> [0/2]   size: w=weight(1f)(rel) h=wrap(rel)
      - Icon  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
    - DropdownMenu  <container> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - DropdownMenuItem  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable CompactDropdown
  - Box  <container>   size: w=wrap(rel) h=wrap(rel)
    - RoundedCornerShape  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
    - Row  <container> [1/3]   size: w=wrap(rel) h=wrap(rel)
        children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=if (bordered) Arrangement.SpaceBetween else Arrangement.Start (rel)
      - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
      - Icon  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
    - DropdownMenu  <container> [2/3]   size: w=wrap(rel) h=wrap(rel)
      - DropdownMenuItem  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable CompactValueField
  - BasicTextField  <leaf>   size: w=wrap(rel) h=wrap(rel)

## @Composable LabeledField
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
    - FieldLabel  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable FieldLabel
  - Text  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=bottom = 4.dp (abs)

---
summary: 5 composables, 17 widget nodes
