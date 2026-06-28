# log_98 — UI sizing/positioning extractor (bucket 3, the Kotlin side)

Date: 2026-06-27
Type: new tool (tools/pseudokotlin/ui_ledger.py) + samples. Builds the "if UI: sizing/
positioning (absolute/relative)" field the ledger record reserved (log_97).

## What it is

From the three ideas talked through this session, the layered build, starting with the
foundation: **Idea 1 (static layout policy) + Idea 3 (target-agnostic normalization).** It
reads each `@Composable`'s layout INTENT statically from the Compose `Modifier` chain and
container arguments — no rendering, no transpilation needed (so it works on the `ui/` files
even though most don't transpile yet). The GEOMETRY rung (Idea 2 — render both sides, diff the
boxes) sits above this and needs render harnesses; not built here.

Per widget node it captures, each tagged **abs** | **rel**:

```
size   w,h         fill / weight(n) / wrap   -> rel   ·  Ndp / token   -> abs
place  pad,offset  dp / token                -> abs
       align, arrangement, index-in-parent   -> rel   (position within the parent)
```

`abs`/`rel` is exactly your "absolute/relative": `48.dp` is a fixed measure; `fillMaxWidth()`,
`weight(1f)`, `wrapContent`, and alignment are parent-relative. The vocabulary is normalized
(target-agnostic) so the SAME schema later checks Compose<->Kivy and Kivy<->Flutter — the
pipeline is two hops, so the UI check can't be Compose-specific.

## Sample (WflSectionHeader)

```
## @Composable WflSectionHeader
  - Row  <container>   size: w=fill(rel) h=wrap(rel)
      pad=horizontal=screenMargin, vertical=rowVertical (abs) ·
      children: verticalAlignment=Center, horizontalArrangement=SpaceBetween (rel) ·
      non-layout: clickable
    - Text  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - Icon  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
```

The full containment tree, each node's size policy, padding (as design tokens, kept symbolic),
child alignment/arrangement, and index-in-parent. Non-layout modifiers (`clickable`, …) are
noted, not dropped.

## Coverage

Ran across 20 real WFL screens/components, 9 -> 242 widget nodes each (OnboardingScreen: 18
composables, 242 nodes), zero crashes. Handles nested `Box`/`Column`/`Row`, fixed dp
(16/48/56/220.dp -> abs), `weight(1f)` (-> rel), `fillMaxWidth/Size` (-> rel), `contentAlignment`
/`Arrangement`/`verticalAlignment` (-> rel), offsets (abs), and design tokens (abs, symbolic).
Samples in `ledger_sample/<Screen>.ui.md`.

## Where this sits / what's next

This is the **Kotlin side** of the UI ledger's sizing/positioning field, policy layer. Two
plug-in points use the same schema:
- **Python/kit side** — extract the same normalized descriptor from the kit's layout calls
  (Kivy/Flutter), then compare node-for-node. Pending a kit side worth comparing against (the
  wrapping needs to be cleaned up first — owner's call).
- **Rendered-geometry diff (Idea 2)** — render both at a reference canvas, compare bounding
  boxes (abs px + rel fraction). The ground-truth rung; needs a Compose render harness.
