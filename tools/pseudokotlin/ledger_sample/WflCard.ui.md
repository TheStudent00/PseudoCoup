# UI layout ledger -- WflCard

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable WflCardTitle
  - Text[text]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    WflCardTitle/Text[text]

## @Composable WflCard
  - RoundedCornerShape[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - BorderStroke[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Card[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - Card[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    WflCard/RoundedCornerShape[0]
    WflCard/BorderStroke[1]
    WflCard/Card[2]
    WflCard/Card[3]

---
summary: 2 composables, 5 widget nodes
