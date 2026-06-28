# UI layout ledger -- MyProgramScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

## @Composable NoProgram
  - Column  <container>   size: w=fill(rel) h=wrap(rel)
      pad=top = 48.dp (abs) · children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
    - Text  <leaf> [0/4]   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [1/4]   size: w=wrap(rel) h=wrap(rel)
    - Spacer  <leaf> [2/4]   size: w=wrap(rel) h=wrap(rel)
    - Button  <container> [3/4]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable ProgramRoadmapView
  - RoadmapView  <leaf>   size: w=wrap(rel) h=wrap(rel)

## @Composable EnrolledBadge
  - Surface  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 10.dp, vertical = 3.dp (abs)

## @Composable EnrolledProgramSpeedDial
  - Column  <container>   size: w=wrap(rel) h=wrap(rel)
      children: horizontalAlignment=Alignment.End, verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
    - ExtendedFloatingActionButton  <leaf> [0/2]   size: w=wrap(rel) h=wrap(rel)
    - FloatingActionButton  <container> [1/2]   size: w=wrap(rel) h=wrap(rel)
      - Icon  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)

## @Composable MyProgramScreen
  - Box  <container> [0/3]   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel)
    - Column  <container> [0/2]   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp (abs) · non-layout: verticalScroll
      - Spacer  <leaf> [0/12]   size: w=wrap(rel) h=wrap(rel)
      - NoProgram  <leaf> [1/12]   size: w=wrap(rel) h=wrap(rel)
      - ActiveAdaptationsBanner  <leaf> [2/12]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [3/12]   size: w=wrap(rel) h=wrap(rel)
      - Row  <container> [4/12]   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Bottom (rel)
        - Text  <leaf> [0/3]   size: w=weight(1f)(rel) h=wrap(rel)
        - Spacer  <leaf> [1/3]   size: w=wrap(rel) h=wrap(rel)
        - EnrolledBadge  <leaf> [2/3]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [5/12]   size: w=wrap(rel) h=wrap(rel)
      - Text  <leaf> [6/12]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [7/12]   size: w=wrap(rel) h=wrap(rel)
      - ProgramRoadmapView  <leaf> [8/12]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [9/12]   size: w=wrap(rel) h=wrap(rel)
      - OutlinedButton  <container> [10/12]   size: w=fill(rel) h=wrap(rel)
        - Text  <leaf> [0/1]   size: w=wrap(rel) h=wrap(rel)
      - Spacer  <leaf> [11/12]   size: w=wrap(rel) h=wrap(rel)
    - EnrolledProgramSpeedDial  <leaf> [1/2]   size: w=wrap(rel) h=wrap(rel)
        pad=16.dp (abs) · align=Alignment.BottomEnd (rel)
  - DayExercisesDialog  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)
  - ActiveAdaptationsSheet  <leaf> [0/3]   size: w=wrap(rel) h=wrap(rel)

---
summary: 5 composables, 34 widget nodes
