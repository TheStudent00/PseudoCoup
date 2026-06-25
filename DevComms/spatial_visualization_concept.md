# Spatial Validation and Interactive Runtime HTML Roadmap

**Date:** 2026-06-25
**Topic:** Extracting bounds and rendering spatial UI Wireframes
**Status:** Deferred

## Concept
The dynamic UI mapping spider (`tools/dynamic_mapper/spider.py`) currently focuses on logical component connectivity. However, Maestro exposes complete layout bounding boxes for every UI element (`[x1, y1][x2, y2]`). 

We designed a proposal to intercept this spatial data and construct an interactive web-based visualization.

## Technical Details
1. **Parser Extension**: Update `StateParser.parse_ui_hierarchy()` to use Regex to capture element bounds: `\[(\d+),(\d+)\]\[(\d+),(\d+)\]`.
2. **State Contract**: Expand `SemanticState` to store `ui_elements` alongside logical `ui_buttons`. To prevent infinite state explosion in the graph due to fractional rendering variations, `ui_elements` (bounds) would be specifically excluded from the state identity hash.
3. **Frontend Integration**: Create a companion `uimap/runtime.html` that uses `mermaid.js` to render the runtime flowchart. When a node is clicked, a side-panel renders an interactive wireframe of the device screen (e.g. 320x640px) populated with absolute-positioned div blocks based on the JSON bounds.

## Why it was deferred
While spatially exact mapping is valuable, we determined that the fundamental issue blocking the project is logical wiring failures caused by the Kotlin-to-PseudoCoup transpiler. Before worrying about visual parity (whether a button is 10px to the left), we must guarantee logical parity (whether tapping the button actually advances the state machine correctly). 

This plan is logged here so it can be resumed once the underlying transpiler routing gaps have been closed using our "Tracer Dye" execution strategy.
