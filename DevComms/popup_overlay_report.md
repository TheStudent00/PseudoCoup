# Popup overlays: open-state rendering for the Kivy kit

Board item: "Popups render inline — DropdownMenu items should be hidden until opened." Closed-state exclusion
already existed (`to_widget` returns `None` for every `POPUP_KIND`, keeping them out of the measured layout).
This change adds the OPEN state: the *running* app now shows dialogs / bottom sheets / dropdown menus as
Window overlays when their controlling state is open, and dismisses them through the app's own handler.

Files touched (only these two, per the fence):
- `~/Programming/WFL_MixingCenter/render/kivy_kit.py`
- `~/Programming/WFL_MixingCenter/render/run_app.py`

## Mechanism

### Open-state detection (per kind)
The recorded node tree carries open-state two ways, so `_popup_open(node)` branches on kind:
- **FLAG kinds** — `DropdownMenu`, `ExposedDropdownMenuBox`. These compose ALWAYS and carry an `expanded`
  prop; closed == `expanded` False. Open only when `expanded` is a **real bool `True`** (or a resolved
  reactive `State` whose `.value` is a bool). Inert Compose stubs are truthy but unresolved, so requiring an
  actual bool avoids a false-open on every stubbed menu.
- **CONDITIONAL kinds** — `AlertDialog`, `BasicAlertDialog`, `Dialog`, `DatePickerDialog`, `ModalBottomSheet`.
  These come from `if (open) { AlertDialog(...) }`, so they compose ONLY when open — mere **presence** in the
  tree means open.
- **Ambient hosts** — `Snackbar`, `SnackbarHost`, `RichTooltip`, `TooltipBox` compose regardless and carry no
  clean open signal, so they are not overlaid this slice (they still stay out of the layout, unchanged).

`_collect_open_popups` walks the **full recorded tree** (not the widget tree, which drops popups) and gathers
open popup nodes; it does not descend into a *closed* popup (its subtree is hidden).

### Overlay attach / detach
- `_build_overlay(node)` builds the popup's slot children (title / text / confirmButton / … — all normal
  composables) through the **existing `to_widget`**, packs them into an anchored `BoxLayout` panel, and adds a
  full-Window `_Overlay` (a `FloatLayout` subclass) to `Window`. Anchoring by kind: dialogs centered ~85%
  width; bottom sheets full-width bottom-anchored; dropdown menus a small top-center panel (true
  trigger-anchoring is a later slice).
- The panel is surface-colored via `_theme_color("surface")` when the theme resolves it, else a neutral
  overlay-chrome fill so the popup is visible. That fallback and the dimming scrim are overlay **chrome the
  kit owns**, not invented app-palette colors (same status as any Kivy default) — we still never fabricate a
  color for app content.
- `_sync_overlays(root_node)` rebuilds the overlay set each frame: silently detach the previous layers
  (`Window.remove_widget`, no handler fired — the state already changed), then attach one layer per open
  popup. It is called from `mount()` exactly once, gated by `OVERLAYS_ENABLED`.

### Dismissal
`_Overlay.on_touch_down` — a tap **outside** the panel calls the popup's recorded
`onDismissRequest`/`onDismiss` through the existing `_fire()`. That runs the app handler inside one recompose
frame → the controlling state flips closed → `recompose` host = `run_app._remount` → `mount()` re-runs →
`_sync_overlays` finds the popup gone and tears the layer down. A re-entrancy guard (`_dismissing`) prevents
a double-fire during the remount that dismissal itself triggers.

### Dump isolation (the gate)
Overlays attach **only** when the module flag `kivy_kit.OVERLAYS_ENABLED` is True. `run_app.py` sets it right
after `import kivy_kit`; `inspect_layout` / `gen_layout_dumps` never touch it, so the flag stays False on the
measurement path and `_sync_overlays` is never reached there. The gate is an explicit, documented module flag
— not import-order magic — so the running-app and layout-dump paths can never cross. `to_widget` still returns
`None` for popup kinds, so even with overlays on, popups never enter the measured widget tree.

## Verification gates

1. **Fidelity** — `FIDELITY ALL: 377/377` (28 screens); `Specimen gate: 24/24`; `SpecimenList gate: 5/5`.
   Exactly the required numbers, unchanged from baseline.
2. **Walk** — `18` OK destinations, identical to the pre-change baseline (captured before editing).
3. **Overlay proof** — `/tmp/popup_proof.py` boots run_app's machinery (overlay flag on), fires the recorded
   `Restore from backup` `clickable` onClick, and observes:
   - overlays after open: **1**; `AlertDialog` present in recomposed tree: **True**
   - screenshot written to `~/Programming/PseudoCoup/layout_inspect/shots/popup_proof.png` — shows the
     centered "Restore from backup?" dialog (title, body text, "Choose file" / "Cancel") over a dimming scrim.
   - after firing `onDismissRequest` (tap-outside path via `overlay.dismiss()`): overlays remaining **0**.
   `RESULT {'opened': 1, 'dialog_in_tree': True, 'closed': 0}` → PROOF PASS.

Per project law: no commit / no push.
