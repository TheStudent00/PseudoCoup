# UI layout ledger -- RestTimerOverlay

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable RestTimerOverlay
  - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
      children: contentAlignment=Alignment.Center (rel) · non-layout: background
    - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
        children: horizontalAlignment=Alignment.CenterHorizontally (rel)
      - Box[0]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: contentAlignment=Alignment.Center (rel)
        - Box[0]  <leaf>   size: w=220.dp(abs) h=220.dp(abs)
        - Column[1]  <container>   size: w=wrap(rel) h=wrap(rel)
            children: horizontalAlignment=Alignment.CenterHorizontally (rel)
          - Text[formatRestTime(restState.remai…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
          - Text[REST]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[2]  <container>   size: w=wrap(rel) h=wrap(rel)
          children: horizontalArrangement=Arrangement.Center (rel)
        - OutlinedButton[0]  <container>   size: w=wrap(rel) h=48.dp(abs)
          - Text[SKIP]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - OutlinedButton[2]  <container>   size: w=wrap(rel) h=48.dp(abs)
          - Text[+30 sec]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    RestTimerOverlay/Box[0]
    RestTimerOverlay/Box[0]/Column[0]
    RestTimerOverlay/Box[0]/Column[0]/Box[0]
    RestTimerOverlay/Box[0]/Column[0]/Box[0]/Box[0]
    RestTimerOverlay/Box[0]/Column[0]/Box[0]/Column[1]
    RestTimerOverlay/Box[0]/Column[0]/Box[0]/Column[1]/Text[formatRestTime(restState.remai…]
    RestTimerOverlay/Box[0]/Column[0]/Box[0]/Column[1]/Text[REST]
    RestTimerOverlay/Box[0]/Column[0]/Spacer[1]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]/OutlinedButton[0]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]/OutlinedButton[0]/Text[SKIP]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]/Spacer[1]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]/OutlinedButton[2]
    RestTimerOverlay/Box[0]/Column[0]/Row[2]/OutlinedButton[2]/Text[+30 sec]

---
summary: 1 composables, 14 widget nodes
