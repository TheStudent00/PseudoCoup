# UI layout ledger -- MyProgramScreen

Kotlin-side sizing/positioning, read statically from each Composable's Modifier
chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/
token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the
rendered-geometry diff plug into this same schema later.

Each node carries a content-anchored path-id (no source annotation needed): a custom
composable -> its name; Icon/Image -> [desc=…]; Text -> ["…"]; else Type[index]. The
full id is the path from the composable root -- a stable handle for the cross-side match.

## @Composable NoProgram
  - Column[0]  <container>   size: w=fill(rel) h=wrap(rel)
      pad=top = 48.dp (abs) · children: horizontalAlignment=Alignment.CenterHorizontally, verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
    - Text[No program yet]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Text[Join a program to see your tra…]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Spacer[2]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - Button[3]  <container>   size: w=wrap(rel) h=wrap(rel)
      - Text[Browse programs]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    NoProgram/Column[0]
    NoProgram/Column[0]/Text[No program yet]
    NoProgram/Column[0]/Text[Join a program to see your tra…]
    NoProgram/Column[0]/Spacer[2]
    NoProgram/Column[0]/Button[3]
    NoProgram/Column[0]/Button[3]/Text[Browse programs]

## @Composable ProgramRoadmapView
  - RoadmapView  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    ProgramRoadmapView/RoadmapView

## @Composable EnrolledBadge
  - Surface[0]  <container>   size: w=wrap(rel) h=wrap(rel)
    - Text[Enrolled]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=horizontal = 10.dp, vertical = 3.dp (abs)
  ids:
    EnrolledBadge/Surface[0]
    EnrolledBadge/Surface[0]/Text[Enrolled]

## @Composable EnrolledProgramSpeedDial
  - Column[0]  <container>   size: w=wrap(rel) h=wrap(rel)
      children: horizontalAlignment=Alignment.End, verticalArrangement=Arrangement.spacedBy(12.dp) (rel)
    - ExtendedFloatingActionButton[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - FloatingActionButton[1]  <container>   size: w=wrap(rel) h=wrap(rel)
      - Icon[desc=Close menu|Update program]  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    EnrolledProgramSpeedDial/Column[0]
    EnrolledProgramSpeedDial/Column[0]/ExtendedFloatingActionButton[0]
    EnrolledProgramSpeedDial/Column[0]/FloatingActionButton[1]
    EnrolledProgramSpeedDial/Column[0]/FloatingActionButton[1]/Icon[desc=Close menu|Update program]

## @Composable MyProgramScreen
  - Box[0]  <container>   size: w=fill(rel) h=fill(rel)
      pad=innerPadding (rel)
    - Column[0]  <container>   size: w=fill(rel) h=fill(rel)
        pad=horizontal = 16.dp (abs) · non-layout: verticalScroll
      - Spacer[0]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - NoProgram  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ActiveAdaptationsBanner  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[3]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Row[4]  <container>   size: w=fill(rel) h=wrap(rel)
          children: verticalAlignment=Alignment.Bottom (rel)
        - Text[current.program.name]  <leaf>   size: w=weight(1f)(rel) h=wrap(rel)
        - Spacer[1]  <leaf>   size: w=wrap(rel) h=wrap(rel)
        - EnrolledBadge  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[5]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Text[desc]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[7]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - ProgramRoadmapView  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[9]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - OutlinedButton[10]  <container>   size: w=fill(rel) h=wrap(rel)
        - Text[View other programs]  <leaf>   size: w=wrap(rel) h=wrap(rel)
      - Spacer[11]  <leaf>   size: w=wrap(rel) h=wrap(rel)
    - EnrolledProgramSpeedDial  <leaf>   size: w=wrap(rel) h=wrap(rel)
        pad=16.dp (abs) · align=Alignment.BottomEnd (rel)
  - DayExercisesDialog  <leaf>   size: w=wrap(rel) h=wrap(rel)
  - ActiveAdaptationsSheet  <leaf>   size: w=wrap(rel) h=wrap(rel)
  ids:
    MyProgramScreen/Box[0]
    MyProgramScreen/Box[0]/Column[0]
    MyProgramScreen/Box[0]/Column[0]/Spacer[0]
    MyProgramScreen/Box[0]/Column[0]/NoProgram
    MyProgramScreen/Box[0]/Column[0]/ActiveAdaptationsBanner
    MyProgramScreen/Box[0]/Column[0]/Spacer[3]
    MyProgramScreen/Box[0]/Column[0]/Row[4]
    MyProgramScreen/Box[0]/Column[0]/Row[4]/Text[current.program.name]
    MyProgramScreen/Box[0]/Column[0]/Row[4]/Spacer[1]
    MyProgramScreen/Box[0]/Column[0]/Row[4]/EnrolledBadge
    MyProgramScreen/Box[0]/Column[0]/Spacer[5]
    MyProgramScreen/Box[0]/Column[0]/Text[desc]
    MyProgramScreen/Box[0]/Column[0]/Spacer[7]
    MyProgramScreen/Box[0]/Column[0]/ProgramRoadmapView
    MyProgramScreen/Box[0]/Column[0]/Spacer[9]
    MyProgramScreen/Box[0]/Column[0]/OutlinedButton[10]
    MyProgramScreen/Box[0]/Column[0]/OutlinedButton[10]/Text[View other programs]
    MyProgramScreen/Box[0]/Column[0]/Spacer[11]
    MyProgramScreen/Box[0]/EnrolledProgramSpeedDial
    MyProgramScreen/DayExercisesDialog
    MyProgramScreen/ActiveAdaptationsSheet

---
summary: 5 composables, 34 widget nodes
