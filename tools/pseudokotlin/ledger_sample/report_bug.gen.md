# PseudoUI generated kit screen -- report_bug  (from Compose ReportBugScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (48 calls)
```python
ui.define_box("report_bug_z00_scaffold", "content", "V")
ui.define_box("report_bug_z01_resultmessage", "report_bug_z00_scaffold", "V")
ui.define_box("report_bug_z02_column", "report_bug_z01_resultmessage", "V")
ui.define_text("report_bug_z03_thanks", "report_bug_z02_column", "Thanks! 🙌")
ui.define_spacer_zone("report_bug_z04_spacer", "report_bug_z02_column")
ui.define_text("report_bug_z05_your_report_and_", "report_bug_z02_column", "Your report and diagnostics we…")
ui.define_spacer_zone("report_bug_z06_spacer", "report_bug_z02_column")
ui.define_button("report_bug_z07_done", "report_bug_z02_column", "Done")
ui.define_box("report_bug_z08_resultmessage", "report_bug_z00_scaffold", "V")
ui.define_box("report_bug_z09_column", "report_bug_z08_resultmessage", "V")
ui.define_text("report_bug_z10_reporting_not_se", "report_bug_z09_column", "Reporting not set up yet")
ui.define_spacer_zone("report_bug_z11_spacer", "report_bug_z09_column")
ui.define_text("report_bug_z12_this_build_has_n", "report_bug_z09_column", "This build has no report desti…")
ui.define_spacer_zone("report_bug_z13_spacer", "report_bug_z09_column")
ui.define_button("report_bug_z14_back", "report_bug_z09_column", "Back")
ui.define_box("report_bug_z15_resultmessage", "report_bug_z00_scaffold", "V")
ui.define_box("report_bug_z16_column", "report_bug_z15_resultmessage", "V")
ui.define_text("report_bug_z17_couldn_t_send", "report_bug_z16_column", "Couldn't send")
ui.define_spacer_zone("report_bug_z18_spacer", "report_bug_z16_column")
ui.define_text("report_bug_z19_something_went_w", "report_bug_z16_column", "Something went wrong sending t…")
ui.define_spacer_zone("report_bug_z20_spacer", "report_bug_z16_column")
ui.define_button("report_bug_z21_try_again", "report_bug_z16_column", "Try again")
ui.define_box("report_bug_z22_reportform", "report_bug_z00_scaffold", "V")
ui.define_box("report_bug_z23_column", "report_bug_z22_reportform", "V")
ui.define_text("report_bug_z24_tell_us_what_wen", "report_bug_z23_column", "Tell us what went wrong — what…")
ui.define_spacer_zone("report_bug_z25_spacer", "report_bug_z23_column")
ui.define_input_zone("report_bug_z26_what_happened", "report_bug_z23_column", "", "What happened?")
ui.define_spacer_zone("report_bug_z27_spacer", "report_bug_z23_column")
ui.define_text("report_bug_z28_how_bad_is_it", "report_bug_z23_column", "How bad is it?")
ui.define_spacer_zone("report_bug_z29_spacer", "report_bug_z23_column")
ui.define_box("report_bug_z30_singlechoicesegm", "report_bug_z23_column", "V")
ui.define_box("report_bug_z31_segmentedbutton", "report_bug_z30_singlechoicesegm", "V")
ui.define_text("report_bug_z32_option_label", "report_bug_z31_segmentedbutton", "option.label")
ui.define_spacer_zone("report_bug_z33_spacer", "report_bug_z23_column")
ui.define_box("report_bug_z34_labeledfield", "report_bug_z23_column", "V")
ui.define_box("report_bug_z35_column", "report_bug_z34_labeledfield", "V")
ui.define_box("report_bug_z36_fieldlabel", "report_bug_z35_column", "V")
ui.define_text("report_bug_z37_your_name_option", "report_bug_z36_fieldlabel", "Your name (optional)")
ui.define_box("report_bug_z38_compactvaluefiel", "report_bug_z34_labeledfield", "V")
ui.define_input_zone("report_bug_z39_field", "report_bug_z38_compactvaluefiel", "", "")
ui.define_spacer_zone("report_bug_z40_spacer", "report_bug_z23_column")
ui.define_box("report_bug_z41_surface", "report_bug_z23_column", "V")
ui.define_text("report_bug_z42_we_detected_a_cr", "report_bug_z41_surface", "We detected a crash on your la…")
ui.define_spacer_zone("report_bug_z43_spacer", "report_bug_z23_column")
ui.define_button("report_bug_z44_send_report", "report_bug_z23_column", "Send report")
ui.define_box("report_bug_z45_topappbar", "report_bug_z00_scaffold", "V")
ui.define_text("report_bug_z46_report_a_bug", "report_bug_z45_topappbar", "Report a bug")
ui.define_icon("report_bug_z47_back", "report_bug_z45_topappbar", "Back")
```

## generated tree
  - Column[z00_scaffold]  <container>
    - Column[z01_resultmessage]  <container>
      - Column[z02_column]  <container>
        - Text[Thanks! 🙌]  <leaf>
        - Spacer[z04_spacer]  <leaf>
        - Text[Your report and diagnostics we…]  <leaf>
        - Spacer[z06_spacer]  <leaf>
        - Button[Done]  <leaf>
    - Column[z08_resultmessage]  <container>
      - Column[z09_column]  <container>
        - Text[Reporting not set up yet]  <leaf>
        - Spacer[z11_spacer]  <leaf>
        - Text[This build has no report desti…]  <leaf>
        - Spacer[z13_spacer]  <leaf>
        - Button[Back]  <leaf>
    - Column[z15_resultmessage]  <container>
      - Column[z16_column]  <container>
        - Text[Couldn't send]  <leaf>
        - Spacer[z18_spacer]  <leaf>
        - Text[Something went wrong sending t…]  <leaf>
        - Spacer[z20_spacer]  <leaf>
        - Button[Try again]  <leaf>
    - Column[z22_reportform]  <container>
      - Column[z23_column]  <container>
        - Text[Tell us what went wrong — what…]  <leaf>
        - Spacer[z25_spacer]  <leaf>
        - TextField[What happened?]  <leaf>
        - Spacer[z27_spacer]  <leaf>
        - Text[How bad is it?]  <leaf>
        - Spacer[z29_spacer]  <leaf>
        - Column[z30_singlechoicesegm]  <container>
          - Column[z31_segmentedbutton]  <container>
            - Text[option.label]  <leaf>
        - Spacer[z33_spacer]  <leaf>
        - Column[z34_labeledfield]  <container>
          - Column[z35_column]  <container>
            - Column[z36_fieldlabel]  <container>
              - Text[Your name (optional)]  <leaf>
          - Column[z38_compactvaluefiel]  <container>
            - TextField[z39_field]  <leaf>
        - Spacer[z40_spacer]  <leaf>
        - Column[z41_surface]  <container>
          - Text[We detected a crash on your la…]  <leaf>
        - Spacer[z43_spacer]  <leaf>
        - Button[Send report]  <leaf>
    - Column[z45_topappbar]  <container>
      - Text[Report a bug]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (ReportBugScreen)
- distinct leaf signatures matched: 13/14 = 92%
- generated signatures NOT in Compose (fabricated): 1
    GEN F:What happened?
- tree validity: 48 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (report_bug_screen.py)
- leaf signatures shared:        6
- generated-only (other states / not in this trace): 8
- hand-built-only (helper glyphs / human representation): 1
    HB-only  F:·DYN·
    GEN-only I:Back
    GEN-only T:Back
    GEN-only T:Couldn't send
    GEN-only T:Done
    GEN-only T:Reporting not set up yet
    GEN-only T:Thanks! 🙌
    GEN-only T:Try again
    GEN-only T:Your report and diagnostics we…
