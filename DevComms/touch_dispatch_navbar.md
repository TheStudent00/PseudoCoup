# Touch dispatch + NavigationBar geometry — general fixes

File fence honored: all edits in `render/kivy_kit.py` only. Throwaway gate script lives in `/tmp`
(`/tmp/realtap_gate.py`), shots in `layout_inspect/shots/navfix_*`.

## Root Cause 1 — touch dispatch was a kind whitelist

- CAUSE: the only place taps bound was the Button factory (`b.bind(on_press=…)`), serving `BUTTON_KINDS`.
  Every other interactive node — a clickable Card/Row/ListItem/NavigationBarItem (`Modifier.clickable` /
  an `onClick` param) — rendered but was DEAD to real touches even though `node.handlers["onClick"]` was
  recorded. The interaction oracle fired handlers directly, so touch dispatch was never exercised.
- GENERAL FIX (one shared layer): `to_widget()` — the single choke point where every Node becomes a widget
  — now calls `_bind_click(w, node)`. Any node carrying a callable `onClick` gets a real touch binding on
  its built widget, routed through the existing `_fire(handler)` (state write → one recompose). No
  per-screen / per-name code; it keys purely off `handlers["onClick"]`.
- Mechanism (`_click_down` / `_click_up`, using `touch.ud`):
  - Fire on a REAL tap only: touch-down records the down position; touch-up fires only if the finger is
    still inside the widget AND total travel ≤ `_TAP_SLOP` (12px). A scroll/drag past the slop is not a
    tap → no fire.
  - No double-fire (innermost wins): Kivy dispatches a touch parent-BEFORE-child, so on touch-down each
    colliding clickable writes itself to `touch.ud['_click_target']` — the LAST writer is the deepest
    (innermost) widget under the finger. On touch-up a widget fires only if it IS that recorded target,
    then returns `True` to consume the release so no ancestor re-fires. Buttons keep their `on_press` but
    ALSO run `_click_down` (they claim on the way down), so an enclosing clickable Card defers to a tapped
    inner Button instead of double-firing. Clickable-in-clickable: the inner one is the later writer → it
    wins.
  - Coexists with ScrollView: touch-down never consumes (returns `False`), so the ScrollView still
    receives the touch and can pan; a pan moves the touch past the slop → the row's `_click_up` declines.

## Root Cause 2 — NavigationBar had no M3 spec geometry

- CAUSE: `NavigationBar` was in `ROW_KINDS` only, so wrap-by-default shrank it — items packed left at
  natural width (see `navfix_before0001.png`).
- GENERAL FIX (same spec tables TopAppBar uses; `TOPBAR_KINDS`/`NAVBAR_H` precedent):
  - `NAVBAR_H = 80`; in `_to_widget_impl`, a `NavigationBar` with no explicit height gets
    `st["height"] = 80`, `fill_x = True`, and each item `size_hint_y = 1` (items fill the bar height).
  - `NavigationBar` added to `EQUAL_DIVIDE_KINDS` → items divide the width EQUALLY (`size_hint_x = 1`).
  - `NavigationBarItem` M3 treatment: default cross-alignment center + arrangement center → icon above
    label, centered horizontally and vertically in the 80dp bar. Container stays transparent (paint layer
    is a no-op unless theme colors paint it).

## Gate outputs (verbatim)

1. fidelity — `cd ~/Programming/PseudoCoup/tools/pseudokotlin && python3 fidelity.py`:
   `FIDELITY ALL: 377/377 components within tolerance (28 screens)`

2. interact — `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py`:
   `INTERACT: 513 fired, 513 ok, 0 failures across 27 screens`

3. REAL-TAP gate — `xvfb-run -a python3 /tmp/realtap_gate.py` (boots the full app, settles, pushes genuine
   synthetic touches via `EventLoop.post_dispatch_input` begin/update/end at nav-item centers):
   ```
   start route: today
   Progress center px: (288, 40) size: (82, 80)
   after tap Progress -> route: progress
   You center px: (371, 40)
   after tap You -> route: settings
   dragging clickable NavigationBarItem(Progress) at (288, 40) (route before: today)
   route after drag: today
   === REAL-TAP GATE RESULTS ===
     [PASS] tap Progress -> progress
     [PASS] tap You -> settings
     [PASS] scroll-drag over clickable does NOT navigate
   GATE: GREEN
   ```
   A real tap at the Progress item center navigates to `progress`; at the You item center navigates to
   `settings`; a 140px vertical pan across the same clickable item does NOT navigate (route stays `today`)
   — proving the tap-vs-scroll discrimination is real. (The Today screen exposes no clickable content
   Card/Row, so the drag test falls back to a clickable nav item, which is an equivalent real clickable.)

4. Visual — `layout_inspect/shots/`:
   - `navfix_before0001.png`: nav items packed to the left at natural width.
   - `navfix_after0001.png`: nav bar spans the full 412px width, 80dp tall, 5 items (Home / Program /
     Paths / Progress / You) evenly spaced with icon above label centered.

## Notes / boundaries

- The bottom nav bar appears only after the app's flows settle (`showBottomBar = currentRoute in
  bottomNavRoutes`, computed in `AppNavigation` before `NavHost` seeds the start route). That gate lives in
  `runtime/navigation.py` / the transpiled screen, OUTSIDE the kit fence — it self-resolves on the settle
  recompose, so it did not block any gate and was left untouched.
- Not committed/pushed.
</content>
