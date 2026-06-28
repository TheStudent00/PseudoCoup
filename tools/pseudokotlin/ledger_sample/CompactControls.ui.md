# UI layout ledger -- CompactControls

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable CompactMultiSelectDropdown
  - Box[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
        pad=horizontal = 12.dp, vertical = 6.dp (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: border, clickable
      - Text[, ]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
      - Icon[desc=Change]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DropdownMenu[1]  <container>   size: w=wrap(rel) h=wrap(rel)
      - DropdownMenuItem[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    CompactMultiSelectDropdown/Box[0]
    CompactMultiSelectDropdown/Box[0]/Row[0]
    CompactMultiSelectDropdown/Box[0]/Row[0]/Text[, ]
    CompactMultiSelectDropdown/Box[0]/Row[0]/Icon[desc=Change]
    CompactMultiSelectDropdown/Box[0]/DropdownMenu[1]
    CompactMultiSelectDropdown/Box[0]/DropdownMenu[1]/DropdownMenuItem[0]

## @Composable CompactDropdown
  - Box[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - RoundedCornerShape[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Row[1]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=if (bordered) Arrangement.SpaceBetween else Arrangement.Start (rel)
      - Text[label(selected)]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Icon[desc=Change]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - DropdownMenu[2]  <container>   size: w=wrap(rel) h=wrap(rel)
      - DropdownMenuItem[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    CompactDropdown/Box[0]
    CompactDropdown/Box[0]/RoundedCornerShape[0]
    CompactDropdown/Box[0]/Row[1]
    CompactDropdown/Box[0]/Row[1]/Text[label(selected)]
    CompactDropdown/Box[0]/Row[1]/Icon[desc=Change]
    CompactDropdown/Box[0]/DropdownMenu[2]
    CompactDropdown/Box[0]/DropdownMenu[2]/DropdownMenuItem[0]

## @Composable CompactValueField
  - BasicTextField[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    CompactValueField/BasicTextField[0]

## @Composable LabeledField
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - FieldLabel  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    LabeledField/Column[0]
    LabeledField/Column[0]/FieldLabel

## @Composable FieldLabel
  - Text[text]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      pad=bottom = 4.dp (abs)
  ids:
    FieldLabel/Text[text]

---
summary: 5 composables, 17 widget nodes
