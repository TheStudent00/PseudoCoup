# log_70 — Track A4: size/position (layout) extraction — INFORMATIONAL

Date: 2026-06-26
Type: reviewer-owned oversight increment (log_65 Track A, item 4 — the last). Tools only —
NO screen changes. Connectivity 220/451 = 49% and edge-mismatches 25 both UNCHANGED.

## The decision (flagged for the reviewer in log_65 A4): INFORMATIONAL, not gated

Layout is shown as a coarse cross-check but does NOT gate. Rationale:
- The Flutter **goldens already guard exact visual layout** (pixel-level); a second, fuzzier
  layout gate would duplicate them and risk false regressions they catch better.
- The matcher's `normalize()` collapses transparent layout containers (lifting their
  children), so the main direction-carriers are intentionally dropped from the comparison —
  making layout a poor gate signal but a fine annotation on the nodes that survive (cards,
  clickable boxes, weighted/filled leaves).
- Keeping it out of the gate means A4 provably cannot move the connectivity/edge baseline
  (verified: gate identical before/after).

## What is extracted (compact, cross-comparable)

`Node.layout` (new additive slot) — a dict with optional keys: `dir` ('H'|'V'|'box'),
`w` (flex weight), `fill` ('width'|'height'|'size'), `scroll` (bool).

- **PC** (`pc_tree._pc_layout`): from the kit define_* params —
  `define_box(…, orient, …, weight)` → dir + w; `define_layout_zone(…, is_horizontal,
  width_hint, …, scrollable)` → dir + w + scroll. Reads positional OR keyword args.
- **KT** (`kotlin_tree._layout_of`): direction from the container callee (Column/LazyColumn→V,
  Row/FlowRow/LazyRow→H, Box→box; Lazy*→scroll); weight/fill/scroll parsed from the Compose
  `modifier` text (`.weight(1f)`, `.fillMaxWidth/Size/Height`, `.verticalScroll`).

## Where it shows

`align._desc` appends a `{dir w= fill scroll}` token, so layout appears in BOTH the
side-by-side (matched rows + gap rows) and the gate's per-screen gap listing. The
`build_sidebyside` header bar now states the hints are **INFORMATIONAL ONLY (not gated)**.

Examples (real): KT `box {V fill:size scroll}` (a LazyColumn filling the screen) vs PC
`box .gym_card {V}`, `box .gym_top {H}`, `box .gym_del_row {H}` — direction agreement is now
eyeballable per row.

## Limits (stated honestly, not hidden)

- No absolute x/y or exact dp sizes — only axis + flex weight + fill mode + scroll. Exact
  geometry is the goldens' job.
- Layout on transparent (role-less, non-clickable) containers is dropped by `normalize()`
  before display, by design — it shows on the surviving structural nodes only.
- Widget-helper internals (PC `widget:*`, KT mapped customs) carry no layout (opaque units).

## Verification

- `connectivity_gate.py` → 220/451 = 49%, edge-mismatches 25, **no regression** (layout is read
  by neither `_score` nor `edge_status`). `smoke_screens.py` → 30/30. `test_ledger.py` → pass.
- `build_sidebyside.py` regenerated `uimap/sidebyside.html`; layout tokens render in matched
  rows; INFORMATIONAL header present.

## Track A complete

A1 handler resolution (log_67) → A2 handler-name ledger (log_68) → A3 edge gate + edge
baseline (log_69) → A4 layout informational (this). The oversight now verifies, per screen:
objects present (connectivity), wired the same way (edge gate), and — informationally —
laid out on the same axis. Remaining backlog: Track B (object ledger sweep) and Track C
(genuine screen gaps), both implementer work per the log_66 silo.
