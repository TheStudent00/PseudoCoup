# UI layout ledger -- PathSelectionSheet

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable PathCard
  - WflCard  <container>   size: w=fill(rel) h=wrap(rel)
    - Row[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        pad=16.dp (abs) · children: verticalAlignment=Alignment.Top (rel)
      - Column[0]  <container>   size: w=weight(1f)(rel) h=wrap(rel)
        - Text[definition.name]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[definition.tagline]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Text[${definition.minSessionsPerWee…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Surface[2]  <container>   size: w=28.dp(abs) h=28.dp(abs)
        - Box[0]  <container>   size: w=wrap(rel) h=wrap(rel)
            children: contentAlignment=Alignment.Center (rel)
          - Icon[desc=null]  <leaf>   size: w=16.dp(abs) h=16.dp(abs)
  ids:
    PathCard/WflCard
    PathCard/WflCard/Row[0]
    PathCard/WflCard/Row[0]/Column[0]
    PathCard/WflCard/Row[0]/Column[0]/Text[definition.name]
    PathCard/WflCard/Row[0]/Column[0]/Spacer[1]
    PathCard/WflCard/Row[0]/Column[0]/Text[definition.tagline]
    PathCard/WflCard/Row[0]/Column[0]/Spacer[3]
    PathCard/WflCard/Row[0]/Column[0]/Text[${definition.minSessionsPerWee…]
    PathCard/WflCard/Row[0]/Spacer[1]
    PathCard/WflCard/Row[0]/Surface[2]
    PathCard/WflCard/Row[0]/Surface[2]/Box[0]
    PathCard/WflCard/Row[0]/Surface[2]/Box[0]/Icon[desc=null]

## @Composable SectionHeader
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - HorizontalDivider[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=top = 8.dp, bottom = 16.dp (abs)
    - Text[category.displayName]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    SectionHeader/Column[0]
    SectionHeader/Column[0]/HorizontalDivider[0]
    SectionHeader/Column[0]/Text[category.displayName]

## @Composable PathSelectionSheet
  - Scaffold[0]  <container>   size: w=fill(rel) h=fill(rel)
    - LazyColumn[0]  <container>   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
      - Text[subtitle]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - SectionHeader  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Column[2]  <container>   size: w=wrap(rel) h=wrap(rel)
        - PathCard  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - LabeledField  <container>   size: w=wrap(rel) h=wrap(rel)
          - CompactValueField  <leaf>   size: w=fill(rel) h=wrap(rel)
  ids:
    PathSelectionSheet/Scaffold[0]
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Text[subtitle]
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/SectionHeader
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Column[2]
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Column[2]/PathCard
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Column[2]/Spacer[1]
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Column[2]/LabeledField
    PathSelectionSheet/Scaffold[0]/LazyColumn[0]/Column[2]/LabeledField/CompactValueField

---
summary: 3 composables, 24 widget nodes
