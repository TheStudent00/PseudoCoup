# log_9 — two ways to write a screen, which one the Flutter kit must be, and where the project actually stands

Date: 2026-06-23
Type: orientation / correction. Consolidates a long back-and-forth into one place so
the explanation is not spread across messages.

## Bottom line (read this first)

- A WFL screen can be written two ways. They differ in exactly one thing.
- The project's screens are written **Way 1**: they talk to a kit that is a `UI` object.
- This session the Dart-side kit got built as **Way 2** (a different shape), with ~30
  screens written against it. Way 2 cannot run the Way-1 screens.
- Way 1 is the correct design for this project — by evidence, not preference (below).
- The core project is **not damaged**. The Way-2 work lives in a separate repo. What
  carries over from it: the look of each component + the token table. What is left:
  build the Dart-side kit as a `UI` object (Way 1) so the existing screens run.

## The two ways — same card, written twice

Way 1:
```python
def build(self, ui):
    ui.set_component("slot", "card", {"title": "Hello"})
```

Way 2:
```python
def build():
    return card(title="Hello")
```

The one difference:
- **Way 1** gives the kit a command — "put a card in this slot." Returns nothing.
  Talks to a `ui` object.
- **Way 2** makes the card and hands it back. Returns a value. No `ui` object.

Everything else — the data, the handlers, the component names — is the same.

## Way 1 in its context (the existing project: WFL_PyHaxe / WFL_PseudoCoup)

```
class AppRouter
	attributes:
		ui          # the kit — a UI object
		db          # the database
		today       # a TodayScreen
		...
	methods:
		navigate
		_mount      # calls screen.build(self.ui, CONTENT_ID, self)

class TodayScreen
	attributes:
		db
		owned_ids
	methods:
		build       # build(ui, content_zone, router) -> calls ui.set_component(...)
		on_day_click

class UI            # the kit. this is the `ui` handed into build.
	methods:
		define_zone
		set_component
		on_click
		present
		...
```

Flow:
```
AppRouter._mount()    --> TodayScreen.build(ui, content_zone, router)
TodayScreen.build()   --> UI.set_component("slot", "card", {"title": "Hello"})
```

Who fills in `UI` (the kit), one per platform:
```
UI (Kivy)       debug path.        exists -- WFL_PyHaxe/src/kit.py
UI (Android)    ship via Haxe.     exists -- PyHaxeUI-Android
UI (Flutter)    ship via Dart.     MISSING -- this is the gap.
```

## Way 2 in its context (what this session built, separate PseudoFlutter repo)

Not classes — plain functions plus a host:
```
function today_screen      # returns column([...])
function column            # returns a value
function card              # returns a value
function workout_row       # returns a value

host  (wfl_main.dart / run_wfl.py)
	takes the returned value and shows it
```

Flow:
```
host             --> today_screen()
today_screen()   --> column([ card(...), workout_row(...) ])   # a value, returned
```

There is no `ui` object. The screen is a value the host shows.

## Why Way 2 can't run the Way-1 screens

The Way-1 screen calls `ui.set_component(...)`. The Way-2 kit has no `ui` and no
`set_component` — only `card(...)` that returns a value. So the existing screens have
nothing to call.

## Why Way 1 is the correct design (evidence, not preference)

- `WFL_PyHaxe/src/kit.py` is a `UI` class with `define_zone` / `set_component` /
  `on_click` / `present`. The whole app is written to that object.
- The WFL_PseudoCoup README names the missing piece as "PseudoFlutter — the UI kit
  (the analog of PyHaxeUI)". Analog of PyHaxeUI = another `UI` class, same methods,
  drawing on Flutter.
- The screens + router already transpile to Dart clean (checked: `today_screen`,
  `you_screen`, `app_router` emit with no errors). They are written Way 1. To run
  them, the Dart kit must be a `UI`.

## State of the project right now

```
logic (data / domain / engine)    done. 53/53 oracles green in Dart. untouched.
screens + router (ui/)            exist, Way 1, transpile to Dart clean. untouched.
UI kit for Kivy   (kit.py)        exists (Way 1).
UI kit for Android (Haxe)         exists.
UI kit for Flutter (Dart)         MISSING   <-- the real remaining work.

this session's separate repo (PseudoFlutter):
	a Way-2 kit + ~30 Way-2 screens    wrong shape for the existing screens.
	component visuals + token table    reusable -- this is what a UI(Flutter) draws.
```

Nothing in the core (`WFL_PyHaxe`, `WFL_PseudoCoup`) was modified this session. The
Way-2 work is entirely inside the `PseudoFlutter` repo.

## What's left

Build the Dart-side kit as a `UI` class — `define_zone`, `set_component`, `on_click`,
`present`, drawing on Flutter — reusing the component look + tokens already made. When
`UI (Flutter)` exists, the existing Way-1 screens run on Flutter with no screen
rewrite. That is the project's stated remaining work, and it is the small/bounded job
(one kit), not 40 screen rewrites.
