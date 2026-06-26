# log_57 — gym_create_wizard_screen gap closed

Date: 2026-06-26
Type: verification report

## The Gap
- **Screen**: `gym_create_wizard_screen`
- **Gap**: `button .filled *click->?`
- **Context**: The `connectivity_gate.py` tool reported 1 `kt_only` node for `gym_create_wizard_screen`.

## The Cause
The Kotlin blueprint uses a core `Button` composable for the "Done selecting" action inside `EquipmentStep`, which `kotlin_tree.py` extracts as `button .filled`. 

In PseudoCoup (`gym_create_wizard_screen.py`), the author used the custom `button` helper imported from `ui.widgets` (`button(ui, self.owned_ids, done_id, sup_zone_id, "Done selecting", "")`). `pc_tree.py` classifies all widget helpers with a `widget:` prefix, so it extracted this as `widget:button`. Because `widget:button` and `button` have different `kind` strings, `align.py` refused to match them, leaving the KT `.filled` button unmatched.

## The Fix
Replaced the custom `button(...)` helper call with the raw `ui.define_button(done_id, sup_zone_id, "Done selecting", "btn_filled")` primitive. `pc_tree.py` correctly maps `define_button` with a `btn_filled` role to the standard `button .filled` node, which perfectly aligns with the Kotlin blueprint's button.

## Verification
- **Gate Output**: `gym_create_wizard_screen: matched=10 kt_only=0 pc_only=4`
- **Smoke Tests**: `SWEEP: 30/30 screens rendered clean` (Pass)
- **Flutter Tests**: `All tests passed!` (Pass)

The change successfully closes the gap without regressions. The reviewer can now ratchet the baseline (`--snapshot`).
