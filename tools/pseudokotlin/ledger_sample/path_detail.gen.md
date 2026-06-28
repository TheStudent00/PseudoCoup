# PseudoUI generated kit screen -- path_detail  (from Compose PathDetailScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (38 calls)
```python
ui.define_box("path_detail_z00_scaffold", "content", "V")
ui.define_box("path_detail_z01_column", "path_detail_z00_scaffold", "V")
ui.define_text("path_detail_z02_path_not_found", "path_detail_z01_column", "Path not found.")
ui.define_box("path_detail_z03_lazycolumn", "path_detail_z00_scaffold", "V")
ui.define_text("path_detail_z04_definition_tagli", "path_detail_z03_lazycolumn", "definition.tagline")
ui.define_box("path_detail_z05_row", "path_detail_z03_lazycolumn", "H")
ui.define_box("path_detail_z06_suggestionchip", "path_detail_z05_row", "V")
ui.define_text("path_detail_z07_definition_minse", "path_detail_z06_suggestionchip", "${definition.minSessionsPerWee…")
ui.define_box("path_detail_z08_suggestionchip", "path_detail_z05_row", "V")
ui.define_text("path_detail_z09_definition_targe", "path_detail_z08_suggestionchip", "~${definition.targetMinutesPer…")
ui.define_box("path_detail_z10_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z11_column", "path_detail_z10_detailsection", "V")
ui.define_text("path_detail_z12_the_evidence", "path_detail_z11_column", "The evidence")
ui.define_spacer_zone("path_detail_z13_spacer", "path_detail_z11_column")
ui.define_text("path_detail_z14_body", "path_detail_z11_column", "body")
ui.define_text("path_detail_z15_definition_evide", "path_detail_z10_detailsection", "definition.evidenceSummary")
ui.define_box("path_detail_z16_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z17_column", "path_detail_z16_detailsection", "V")
ui.define_text("path_detail_z18_why_it_works", "path_detail_z17_column", "Why it works")
ui.define_spacer_zone("path_detail_z19_spacer", "path_detail_z17_column")
ui.define_text("path_detail_z20_body", "path_detail_z17_column", "body")
ui.define_text("path_detail_z21_definition_educa", "path_detail_z16_detailsection", "definition.educationalCopy")
ui.define_box("path_detail_z22_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z23_column", "path_detail_z22_detailsection", "V")
ui.define_text("path_detail_z24_modality", "path_detail_z23_column", "Modality")
ui.define_spacer_zone("path_detail_z25_spacer", "path_detail_z23_column")
ui.define_text("path_detail_z26_body", "path_detail_z23_column", "body")
ui.define_text("path_detail_z27_definition_modal", "path_detail_z22_detailsection", "definition.modalityNotes")
ui.define_box("path_detail_z28_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z29_column", "path_detail_z28_detailsection", "V")
ui.define_text("path_detail_z30_research", "path_detail_z29_column", "Research")
ui.define_spacer_zone("path_detail_z31_spacer", "path_detail_z29_column")
ui.define_text("path_detail_z32_body", "path_detail_z29_column", "body")
ui.define_box("path_detail_z33_column", "path_detail_z28_detailsection", "V")
ui.define_text("path_detail_z34_citation", "path_detail_z33_column", "citation")
ui.define_box("path_detail_z35_topappbar", "path_detail_z00_scaffold", "V")
ui.define_text("path_detail_z36_text", "path_detail_z35_topappbar", "")
ui.define_icon("path_detail_z37_back", "path_detail_z35_topappbar", "Back")
```

## generated tree
  - Column[z00_scaffold]  <container>
    - Column[z01_column]  <container>
      - Text[Path not found.]  <leaf>
    - Column[z03_lazycolumn]  <container>
      - Text[definition.tagline]  <leaf>
      - Row[z05_row]  <container>
        - Column[z06_suggestionchip]  <container>
          - Text[${definition.minSessionsPerWee…]  <leaf>
        - Column[z08_suggestionchip]  <container>
          - Text[~${definition.targetMinutesPer…]  <leaf>
      - Column[z10_detailsection]  <container>
        - Column[z11_column]  <container>
          - Text[The evidence]  <leaf>
          - Spacer[z13_spacer]  <leaf>
          - Text[body]  <leaf>
        - Text[definition.evidenceSummary]  <leaf>
      - Column[z16_detailsection]  <container>
        - Column[z17_column]  <container>
          - Text[Why it works]  <leaf>
          - Spacer[z19_spacer]  <leaf>
          - Text[body]  <leaf>
        - Text[definition.educationalCopy]  <leaf>
      - Column[z22_detailsection]  <container>
        - Column[z23_column]  <container>
          - Text[Modality]  <leaf>
          - Spacer[z25_spacer]  <leaf>
          - Text[body]  <leaf>
        - Text[definition.modalityNotes]  <leaf>
      - Column[z28_detailsection]  <container>
        - Column[z29_column]  <container>
          - Text[Research]  <leaf>
          - Spacer[z31_spacer]  <leaf>
          - Text[body]  <leaf>
        - Column[z33_column]  <container>
          - Text[citation]  <leaf>
    - Column[z35_topappbar]  <container>
      - Text[z36_text]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (PathDetailScreen)
- distinct leaf signatures matched: 7/7 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 38 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (path_detail_screen.py)
- leaf signatures shared:        2
- generated-only (other states / not in this trace): 5
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Back
    GEN-only T:Modality
    GEN-only T:Research
    GEN-only T:The evidence
    GEN-only T:Why it works
