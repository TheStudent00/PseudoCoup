# UI layout ledger -- PathDetailScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable DetailSection
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text[title]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    DetailSection/Column[0]
    DetailSection/Column[0]/Text[title]
    DetailSection/Column[0]/Spacer[1]

## @Composable PathDetailScreen
  - Scaffold[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Column[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=24.dp (abs)
      - Text[Path not found.]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - LazyColumn[1]  <container>   size: w=fill(rel) h=fill(rel)
        children: verticalArrangement=Arrangement.spacedBy(24.dp) (rel)
      - Text[definition.tagline]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[1]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.spacedBy(8.dp) (rel)
        - SuggestionChip[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - SuggestionChip[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
        - Text[definition.evidenceSummary]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
        - Text[definition.educationalCopy]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
        - Text[definition.modalityNotes]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - DetailSection  <container>   size: w=wrap(rel) h=wrap(rel)
        - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
            children: verticalArrangement=Arrangement.spacedBy(8.dp) (rel)
          - Text[citation]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    PathDetailScreen/Scaffold[0]
    PathDetailScreen/Scaffold[0]/Column[0]
    PathDetailScreen/Scaffold[0]/Column[0]/Text[Path not found.]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/Text[definition.tagline]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/Row[1]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/Row[1]/SuggestionChip[0]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/Row[1]/SuggestionChip[1]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection/Text[definition.evidenceSummary]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection/Text[definition.educationalCopy]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection/Text[definition.modalityNotes]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection/Column[0]
    PathDetailScreen/Scaffold[0]/LazyColumn[1]/DetailSection/Column[0]/Text[citation]

---
summary: 2 composables, 20 widget nodes
