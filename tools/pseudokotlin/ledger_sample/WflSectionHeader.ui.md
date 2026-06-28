# UI layout ledger -- WflSectionHeader

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable WflSectionHeader
  - Row[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal = WflTheme.tokens.screenMargin, vertical = WflTheme.tokens.rowVertical (abs) · children: verticalAlignment=Alignment.CenterVertically, horizontalArrangement=Arrangement.SpaceBetween (rel) · non-layout: clickable
    - Text[$label · $count]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Icon[desc=Collapse|Expand]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    WflSectionHeader/Row[0]
    WflSectionHeader/Row[0]/Text[$label · $count]
    WflSectionHeader/Row[0]/Icon[desc=Collapse|Expand]

---
summary: 1 composables, 3 widget nodes
