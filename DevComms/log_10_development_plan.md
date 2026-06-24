# log_10 — development plan: stand PseudoFlutter up as a UI class, run the real screens

Date: 2026-06-23
Type: development plan. Follows log_9 (establishes the kit must be a `UI` object).

## What was a detour, what carries over (honest accounting)

This session built the Dart-side kit Way 2 (functions returning values) and re-authored
~30 screens against it. Real detour: the screens already exist, written Way 1, already
running on Kivy + Haxe.

Redundant (set aside):
- the ~30 Way-2 screen files (golden tests + Kivy render scripts). The real screens
  already exist in `WFL_PyHaxe/src/ui`. (They did one useful job: they proved each
  component's look, pixel-matched 3-way. As app screens they are not used.)
- `wfl_app.py` — a demo app with its own router/nav. `app_router.py` already does this.

Carries over directly — the hard part, and it is done:
- the look of every component: the code that draws a card, a workout_row, the set
  table, the donut, chips, nav, fab, ... on BOTH Flutter and Kivy.
- the token table (`tokens.json` + `tokens.wfl.json`) — WFL's design language as data.
- the icon system, the font handling, and the 3-way (WFL Android | Flutter | Kivy)
  harness.

Net: the effort includes a detour, but the asset — component look + tokens, pixel-
verified — survives, and it is exactly what the `UI` kit draws. Not days of value lost;
days of a wrong wrapper around work that mostly holds.

## Target

```
PseudoFlutter = a hand-written Dart `UI` class + components, drawing on Flutter,
                resolving look from the token table.

The screens DON'T change. They already call ui.set_component(...). When UI(Flutter)
exists, the transpiled WFL app runs on Flutter.
```

The `UI` methods the screens call (from `WFL_PyHaxe/src/kit.py`):

```
class UI
	methods:
		define_zone
		define_layout_zone
		set_component       # kind + props -> draw the component's look into the zone
		on_click
		present
		remove_zone
		hide / show
		now_ms
		run
		dump_tree
```

## How set_component maps onto the look already built

```
ui.set_component(zone, "card", {...})         -->  draw the existing card look
ui.set_component(zone, "workout_row", {...})  -->  draw the existing workout_row look
ui.set_component(zone, "fab", {...})          -->  draw the existing fab look
... one branch per component kind ...
```

The function `card({title, body}) -> Widget` becomes the body of the "card" branch of
`set_component`; props come from the dict instead of named arguments. The drawing code
is reused; the wrapper changes.

## Plan (phased; each phase ends running real transpiled screens)

```
Phase 1 — the UI skeleton (Flutter)
	build the zone tree + define_zone / define_layout_zone / on_click / present /
	remove_zone / hide / show, and a root Flutter widget that walks the tree and
	rebuilds on change. set_component supports ONE kind ("card") to start.
	done when: a hand-written 3-line screen (one card) renders.

Phase 2 — the components
	implement set_component for every kind the screens use (card, list_row,
	workout_row, nav_item, button, fab, header, greeting_header, chip, set_row,
	donut, ... the ~25 generic kinds), each drawing the look already built,
	reading props.
	done when: each kind renders from a props dict.

Phase 3 — run the real app
	transpile WFL_PyHaxe (logic + ui + router + app_main) to Dart via
	WFL_PseudoCoup/tools/transpile.py. drop in UI(Flutter). run. every missing method
	or component kind shows up as a concrete gap; fill it.
	done when: the transpiled WFL app boots to Today on Flutter and navigates.

Phase 4 — match WFL, 3-way
	WFL Android | Flutter | Kivy of the SAME screens. fix every difference in the
	kit or the tokens (the shared place), never per-screen — the log_5 discipline.
	done when: no screen differs across the three.
```

## The Kivy debug path (so 3-way can be graded)

The 3-way needs Kivy to look good too. The existing Kivy kit (`WFL_PyHaxe/src/kit.py`)
draws the same components patchily. The same component look + tokens go into it so the
debug path matches the Flutter path.

## Open decisions (owner calls)

- Where the Dart `UI` kit lives — inside `WFL_PseudoCoup`, or a `PseudoFlutter` repo it
  depends on.
- Kivy debug visuals — improve `WFL_PyHaxe/src/kit.py` in place, or a refreshed kit fed
  the same look.
- Whether the 30 Way-2 screen goldens stay as a component-look test suite, or are
  removed.

## First concrete step

Phase 1, smallest slice: write the Dart `UI` class with `define_zone` + `set_component`
(card only) + a root widget, and render one transpiled screen reduced to a single card.
That proves the shape end-to-end before scaling to all components.
