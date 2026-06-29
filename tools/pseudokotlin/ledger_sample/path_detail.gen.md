# PseudoUI generated kit screen -- path_detail  (from Compose PathDetailScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (34 calls)
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
ui.define_text("path_detail_z14_definition_evide", "path_detail_z10_detailsection", "definition.evidenceSummary")
ui.define_box("path_detail_z15_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z16_column", "path_detail_z15_detailsection", "V")
ui.define_text("path_detail_z17_why_it_works", "path_detail_z16_column", "Why it works")
ui.define_spacer_zone("path_detail_z18_spacer", "path_detail_z16_column")
ui.define_text("path_detail_z19_definition_educa", "path_detail_z15_detailsection", "definition.educationalCopy")
ui.define_box("path_detail_z20_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z21_column", "path_detail_z20_detailsection", "V")
ui.define_text("path_detail_z22_modality", "path_detail_z21_column", "Modality")
ui.define_spacer_zone("path_detail_z23_spacer", "path_detail_z21_column")
ui.define_text("path_detail_z24_definition_modal", "path_detail_z20_detailsection", "definition.modalityNotes")
ui.define_box("path_detail_z25_detailsection", "path_detail_z03_lazycolumn", "V")
ui.define_box("path_detail_z26_column", "path_detail_z25_detailsection", "V")
ui.define_text("path_detail_z27_research", "path_detail_z26_column", "Research")
ui.define_spacer_zone("path_detail_z28_spacer", "path_detail_z26_column")
ui.define_box("path_detail_z29_column", "path_detail_z25_detailsection", "V")
ui.define_text("path_detail_z30_citation", "path_detail_z29_column", "citation")
ui.define_box("path_detail_z31_topappbar", "path_detail_z00_scaffold", "V")
ui.define_text("path_detail_z32_text", "path_detail_z31_topappbar", "")
ui.define_icon("path_detail_z33_back", "path_detail_z31_topappbar", "Back")
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
        - Text[definition.evidenceSummary]  <leaf>
      - Column[z15_detailsection]  <container>
        - Column[z16_column]  <container>
          - Text[Why it works]  <leaf>
          - Spacer[z18_spacer]  <leaf>
        - Text[definition.educationalCopy]  <leaf>
      - Column[z20_detailsection]  <container>
        - Column[z21_column]  <container>
          - Text[Modality]  <leaf>
          - Spacer[z23_spacer]  <leaf>
        - Text[definition.modalityNotes]  <leaf>
      - Column[z25_detailsection]  <container>
        - Column[z26_column]  <container>
          - Text[Research]  <leaf>
          - Spacer[z28_spacer]  <leaf>
        - Column[z29_column]  <container>
          - Text[citation]  <leaf>
    - Column[z31_topappbar]  <container>
      - Text[z32_text]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (PathDetailScreen)
- distinct leaf signatures matched: 7/7 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 34 nodes, 0 orphan parents

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
