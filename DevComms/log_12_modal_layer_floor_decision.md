# log_12 — the kit can't open a modal layer; how the primitive set grows to cover it is yours to decide

Date: 2026-06-24
Type: decision request. One fork. Everything around it is mine and already moving.

## Bottom line (read this first)

- Re-deriving the WFL screens by faithful transcription (log earlier this session)
  surfaced one thing the kit **cannot express today**: a **modal layer** — a menu, a
  dialog, or a bottom-sheet.
- It shows up on ~half the screens, so it gets decided once, not per screen.
- It's a **floor** decision — it adds a name to the primitive set every kit implements —
  so it's yours, not mine to improvise.
- Three shapes below. **My lean: one primitive, `define_layer`.** Reasons + honest cost
  named. The call is yours.
- Nothing else in the transcription is a decision: ~40 `widgets.py` compose functions and
  ~100 theme roles are mechanical and already mine. This is the only gate.

## Glossary

```
modal layer
    a panel that floats ABOVE the normal screen, over a scrim, and dismisses.
    the scrim is the dimmed backdrop that catches the outside tap.
    three placements in WFL:
        menu    — small panel pinned to a trigger (the ⋮ on a program card)
        dialog  — a centered card (the "Discard this workout?" confirm)
        sheet   — a panel on the bottom edge that slides up (the welcome-back sheet)

define_layer
    the proposed primitive for it. a new method on the UI floor, alongside
    define_box / define_overlay. example tied to context:
        ui.define_layer("swap_dlg", "app_root", "center", "dialog_card")
        widgets.dialog(ui, owned, ..., "swap_dlg", "Swap exercise?", ...)
```

## The gap, anchored

The floor today is these `define_*` methods on the `UI` object (the kit), addressed by
string id, holding no widget — `define_box`, `define_text`, `define_button`,
`define_marker`, `define_icon`, `define_zone`, `define_layout_zone`, `define_divider_zone`,
`define_input_zone`, `define_overlay`.

`define_overlay` floats one zone over the root — it was built for the FAB (the `+`). What a
menu/dialog/sheet needs that it does **not** give:

```
need                        define_overlay gives        gap
----                        --------------------        ---
a scrim (dim backdrop          no scrim                 outside-tap dismiss
 that catches outside tap)                              has nowhere to live
placed panel:                  one fixed spot           can't anchor to a ⋮,
 anchored / centered / bottom  (the FAB corner)         can't center, can't sit bottom
dismiss on backdrop tap        no                       every modal re-wires it
```

So `define_overlay` can float a zone, but it isn't a modal layer. There is no primitive
that says "dim the screen, place this panel, dismiss on outside tap."

## Where it's needed (so "half the screens" isn't hand-waving)

```
menu     Programs (⋮ Edit/Duplicate/Archive/Delete), Exercise detail (⋮),
         Workout execution (set-type dropdown)
dialog   delete-confirm, swap-confirm, discard-workout, name-a-program input
sheet    Today welcome-back, Path picker, Plate calculator, Log-a-win
```

All three are the same shape underneath: scrim + a placed, dismissible panel. They differ
only in **where the panel sits** (pinned to a trigger / centered / bottom) and whether it
slides.

## The fork — same modal, three ways the floor can grow

This mirrors log_9's "same card, two ways." Here it's the same dialog, three ways.

```
Way 1 — one primitive, a mode picks the placement
    ui.define_layer("swap_dlg", "app_root", "center", "dialog_card")
    ui.define_layer("type_menu", "set_row", "anchor", "menu")
    ui.define_layer("welcome",   "app_root", "bottom", "sheet")
    # one new floor name. each kit writes ONE render path that branches on the mode.

Way 2 — three primitives, one per placement
    ui.define_dialog("swap_dlg", "dialog_card")
    ui.define_menu("type_menu", "set_row", "menu")
    ui.define_sheet("welcome", "sheet")
    # three new floor names. each kit writes THREE render paths.

Way 3 — no new primitive, hand-build per screen
    ui.define_box("scrim", "app_root", "V", "scrim", 0.0)   # full-screen dim box
    ui.define_box("panel", "scrim", "V", "dialog_card", 0.0)
    # ...manual centering, manual dismiss wiring, manual z-order — every modal, every screen.
    # (still needs define_overlay generalized from "one FAB" to "any floated zone" first.)
```

## The cost of each, named honestly

- **Way 1** — smallest growth: one name on the floor, one render path per kit (and per
  future target). The mode string (`center` / `anchor` / `bottom`) is a little overloaded —
  the kit branches on it. Consistent with how the floor already works: `define_box` already
  takes a mode (`"H"`/`"V"`), `define_layout_zone` already takes a behavior flag (scrollable).
- **Way 2** — most explicit at the call site, but three names on the floor and three render
  paths in **every** kit. Every future target pays for three, not one.
- **Way 3** — the floor stays frozen, but the work moves **into every screen**: the scrim,
  the centering, the dismiss, the z-order, re-done 10+ times. This is exactly the tradeoff
  log_11 named — a layer cost paid once in the kit vs. paid many times in the app. Highest
  fidelity risk, because the fragile part (placement + dismiss) is hand-repeated.

## My lean, and what's yours

I'd take **Way 1** — one `define_layer`, mode picks placement. It grows the primitive set by
exactly one name, keeps one render path per kit, and reads like the primitives already there.

That said: this is the floor, and the floor is your ontology. If you want the three explicit
names (Way 2), or want the kit frozen and the modals hand-built (Way 3), say so and I build to
it. The transcription is blocked on nothing else — the moment you pick, I add the primitive to
both kits (Flutter + Kivy), then run the screens through faithfully, verifying each against the
original on the live 2-way.

## Status (so the decision has its footing)

- Live 2-way is up: original WFL and our Flutter app are **both installed APKs on
  emulator-5554**, not screenshots.
- 10 screens analyzed into transcription specs at `WFL_PseudoCoup/DevComms/transcribe_specs/`.
  The modal-layer gap is the one recurring blocker across them; charts (Progress) are the one
  separate fidelity gap, handled on their own.
