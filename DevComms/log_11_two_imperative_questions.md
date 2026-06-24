# log_11 — two different "imperative" questions; the string-id screen shape is the sound one

Date: 2026-06-23 (rewritten same day — see "Record of swings" at the end)
Type: correction. Untangles a confusion I introduced in log_9 / log_10, then over-
corrected in the first draft of this log.

## Bottom line

- Two separate questions both get called "imperative." Keeping them apart is the key.
- **Q1 — how an update happens** (you call `present` vs the framework redraws): settled.
- **Q2 — how you write a screen** (string-id commands vs return-a-widget): the floor is
  **string-id commands** (Shape A). That is the sound choice, by the floor's own rule.
- The functional return-a-widget look (Shape B) was a drift that crept in through the
  demo code (and this session leaned all the way into it). It was never a recorded
  decision.

## Q1 — how an UPDATE happens (settled; handoff section 2)

```
imperative (Kivy):    you call   present("count", "Count: 4")   yourself.
reactive  (Flutter):  you change count; the framework redraws. you call nothing.
```

The app always writes `present(...)`. On a reactive target the transpiler routes that
into a framework state-set; the framework redraws. App source is identical. Not open.

## Q2 — how you WRITE a screen (the floor's rule decides it)

The same card, two ways:

```
Shape A (PyHaxeUI, and the WFL_PyHaxe screens):
	ui.set_component("slot", "card", {"title": "Hello"})
	# app passes a string id ("slot") + a name ("card") + props. holds no widget.

Shape B (what this session built):
	column([ card(title="Hello") ])
	# card(...) RETURNS a backend widget; the app holds it and composes a tree.
```

The floor's rule, stated in `PyHaxeUI_development_plan.md`:

> "Zones are addressed by string id, not by object handle.
>  App code never holds backend-defined widget references."

Shape A obeys it. Shape B breaks it — a returned `card(...)` is a Flutter `Widget`
(a backend object), and the app holds it and builds a Flutter tree. Holding widgets
and composing trees is **Flutter's own declarative idiom** — one backend's model. The
design deliberately kept that off the floor: string-id zones + commands are the floor;
even the widget-layer conveniences "produce the primitive calls," i.e. they lower to
string-id too. So Shape A is the screen shape; Shape B steps off the floor.

## Why A is sound (and B's cost)

- **A keeps one source across every backend.** A screen written in string-id commands
  runs on Haxe (PyHaxeUI), Dart (PseudoFlutter), and any future target, because each
  backend implements the same string-id floor. That is the thesis.
- **B is Flutter-native but Flutter-only at the source level.** It writes directly in
  Flutter's widget-tree model, so those screens don't run on the other backends without
  re-authoring. It works — it just isn't portable source.
- **A's real cost, named honestly:** on Flutter (a declarative framework) the kit holds
  a retained zone-tree and rebuilds it on `set_component` / `present` — a retained layer
  against the framework's grain. A one-time kit cost, paid so the same screens run
  everywhere. (The Kivy kit already is exactly this retained tree; `_ZoneBox` from log_4
  is a Flutter seed of it.)

## What this means for the screens and the kit

- The WFL screens (`WFL_PyHaxe/src/ui`, Shape A) are the source. They stay. They already
  transpile to Dart.
- PseudoFlutter is built as a `UI` class on Flutter that implements the string-id floor
  (`define_zone` / `set_component` / `on_click` / `present`) and draws each component
  kind with the component looks + tokens this session already produced.
- The session's Shape-B kit is not the contract. What carries from it: the component
  looks and the token table (now drawn *inside* `set_component`, not returned as values).

## Correction to the record

- **log_9 / log_10** said PseudoFlutter must be Shape A, but gave the weak reason ("so
  the existing screens run"). Right direction; the real reason is the floor's string-id
  rule above. log_10's plan (build the `UI` class) stands; its framing of the functional
  work as merely "a detour to reuse screens" undersells the reason.
- **log_11, first draft** said the functional shape was "decided in log_1-4." Wrong:
  log_1-4 decided roles, two-kinds-of-state, structure-invariant, and the present
  boundary — all about state and updates, never about return-a-widget vs string-id. The
  functional look came from the demo code, not a decision.

## Record of swings (so the oscillation is on the record)

log_9 → A. log_11 first draft → B. this rewrite → A. The first two anchored on weak
evidence (example syntax; "which lets the screens run"). The anchor that actually
settles it is the floor's stated rule — string id, no held references — which is
unambiguous and favors A. That is the anchor to use, not the example code's surface.
