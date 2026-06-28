# UI layout ledger -- WflSectionHeader

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable WflSectionHeader
  - Row  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.rowVertical (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: clickable
    - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - Icon  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)

---
summary: 1 composables, 3 widget nodes
