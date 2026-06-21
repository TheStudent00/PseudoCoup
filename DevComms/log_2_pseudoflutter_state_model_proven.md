# log_2 — PseudoFlutter: the state model, demonstrated end-to-end

Date: 2026-06-21
Type: progress (the worked example from log_1 is built and verified). Where log_1
*agreed* the three decisions on paper, this log records that decision 2 (the two
kinds of state) and the theme-as-data spine are now **shown working** across six
components, each rendered identically on Flutter and Kivy from one source.

## What got built

Starting from the agreed `pill_button` worked example, the kit now has six
components, each verified by an actual side-by-side PNG (`PseudoFlutter/comparisons/`):

    pill_button           leaf control; kit-owned press highlight
    card                  titled container; non-hugging layout role
    collapsible_section   compound + stateful; kit-owned collapse
    nav                   segmented control; app-state selection (present)
    toggle                switch; boolean app state (present)
    progress_bar          pure app-state render; no event out at all

Each renders **structurally identical** on the two engines from one intent call +
one token table. The only cross-engine difference anywhere is where a body string
word-wraps — a font-metric artifact, not a structural or token divergence.

## Decision 2 is the spine, and it held

log_1 split state into *kit-owned UI-local* vs *app state via present*, and bet that
this is what keeps the app platform-agnostic. The six components were chosen to land
on both sides of that line and stress it:

    KIT-OWNED (UI-local)              the app never holds this bool/int
      pill_button   pressed           setState (Flutter) / on_press (Kivy)
      collapsible_section  open       setState (Flutter) / on_release (Kivy)

    APP STATE (present)              the app holds it; kit renders + reports
      nav      selected: int          on_select(i)  -> app updates -> re-presents
      toggle   value: bool            on_change(!v)  -> app updates -> re-presents
      progress_bar  value: 0..1       (no event — pure render)

The payoff is visible in the goldens: `nav` rendered twice (selected=0, selected=2)
and `toggle` twice (on/off) show the highlight/knob is a **pure function of the value
passed in** — the kit owns nothing. `progress_bar` is the limit case: state in, no
event out, kit owns nothing at all. Meanwhile `collapsible_section` rendered both
states from internal state the app cannot see. Same boundary, both sides, exactly as
decision 2 predicted. The reactive-vs-imperative gap (Flutter setState vs Kivy
canvas redraw) stayed entirely inside each kit; no app intent encodes it.

## Decision 1's open question, resolved in practice

log_1 left a gut-check open: do role-named numbers feel right, or too indirect? In
build, this became `tokens.json` — ONE table both kits load (`Tokens.load` in Dart,
`Tokens(...)` in Kivy). Every proportion is a fraction of a content width
(`pill.height = 0.13`, `card.pad = 0.05`); colours are `RRGGBB`; per-instance scale
(`contentWidth`) and derived values (a radius = height/2) are computed, not stored.

The verdict from using it: not too indirect — and load-bearing. Because both engines
read the *same file*, "they happen to match" became "they cannot drift": change
`0.13` once and both move together. That is the mechanism that makes the structural
identity in every golden a guarantee rather than a coincidence. Role-as-data earned
its place.

## How it's verified (and why that matters)

One fixed home, one driver: `tools/compare.py <component>` runs the Flutter golden
(`flutter test --update-goldens`), the Kivy headless render (`xvfb` + `export_to_png`),
and composites a labelled side-by-side into `comparisons/<component>.png`. This was
set up deliberately before fanning out — PyHaxeUI/WFL's comparison images scattered
because nothing fixed where they lived, and that disorganization was its own drag.

## Status / next

The intention-based process from log_1 is no longer theory — leaf, container,
compound-stateful, and all three present shapes (selection / boolean / pure value)
are built and verified.

Done since this log was opened (same run):

    - DONE  full screen from one intent, verified side-by-side (comparisons/screen.png)
            — the six co-lay-out in a shared content column, identically on both engines.
    - DONE  text_field — string app state the user edits; the first component whose
            editing behaviour (Kivy TextInput vs Flutter TextField) genuinely diverges,
            so it lives inside the kit behind the same present contract.
    - DONE  the ship path: example/app_demo.py (the whole screen as intent) transpiles
            through PseudoDart to example/app_demo.gen.dart, which **type-checks against
            the kit** (`dart analyze` → no issues). One Python source now drives both the
            Kivy debug render AND a Dart program that compiles against Flutter. (This also
            caught a real parity bug — Tokens(420) vs Tokens.load(420) — the analyzer
            holding both kits to the same intent.)

Remaining:

    - drive a LIVE Flutter app from app_demo.gen.dart (so far the Dart is emitted and
      analyzed, but not yet pumped into a running Flutter widget tree end-to-end);
    - widen the kit toward the ~20-30 components a real screen needs (list_row, slider,
      dropdown, …), each via the same compare.py side-by-side.
