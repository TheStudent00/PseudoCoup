# log_3 — PseudoFlutter: the present / reactive boundary, demonstrated

Date: 2026-06-21
Type: progress (the last untested part of the state model is now shown working).
log_2 proved state flowing *in* at construction (kit-owned vs app-state-via-present).
This proves a state *update* flowing *through* `present` — the imperative-vs-reactive
point the handoff (section 2) settled on paper but nothing had exercised.

## What this closes

The handoff settled, in one line, the thing that could have been an architectural
wall: imperative-vs-reactive is a **transpiler/kit detail, not a wall** — on a
reactive target the `present` call "routes into a state-set" and the framework does
the update; "reactivity is one more mechanism the kit hides." That was agreed but
never built for PseudoFlutter. Every prior side-by-side passed app state *in at
construction* and rendered once; none updated state after the fact. This log builds
`present` and shows the update path on both engines from one source.

## The canonical example, both engines

Straight from the handoff: a `Count: N` zone over an Increment button
(`example/counter_demo.py`). The app holds its own state and, on tap, runs:

    def on_increment() -> None:
        state.n = state.n + 1
        present("count", "Count: " + str(state.n))

`comparisons/counter.png` is a 2x2 — columns are the engines, rows are before/after
the tap:

                  Flutter (ship · reactive)     Kivy (debug · imperative)
    before tap          Count: 0                      Count: 0
    after  tap          Count: 1                      Count: 1

Same source, same transition. The Flutter column is the **machine-generated**
`build_counter()` driven by a real `tester.tap()`; the Kivy column runs the same
`on_increment()` handler. The point is what differs UNDERNEATH and nowhere else:

    present() on Kivy   (imperative)  -> sets the bound Label's text directly.
                                          the APP performed the update.
    present() on Flutter (reactive)   -> text_zone is a ValueListenableBuilder;
                                          present() sets a ValueNotifier and the
                                          FRAMEWORK rebuilds. the app named no widget.

The reactive-vs-imperative difference is confined to the two `present` bodies in the
two kits. The app's `present("count", ...)` is byte-for-byte the same call; it does
not encode which model is underneath. That is exactly the handoff's resolution,
now standing up instead of asserted.

## Why this was the right thing to prove next

It was the one remaining claim in the whole state model that was theory. log_1
*decided* the two-kinds-of-state split; log_2 *showed* both kinds at construction;
the open edge was "when state changes, does the same source update the same way on a
reactive engine and an imperative one?" If that had cracked, the portability thesis
cracks with it — the app would have to know which model it's on. It didn't crack.

## Mechanism notes (for the next session)

- `present`/`text_zone` are kit primitives, added to both kits. `set_theme` clears
  the zone registry so each app start is fresh.
- `text_zone(zone_id, value)` registers a zone; `present(zone_id, value)` updates it.
  A zone is addressed by a string id — the imperative kit needs the name to find the
  widget; the reactive kit uses it to find the notifier. The app writes the id either
  way, which keeps the two paths source-identical.
- `counter_demo.py` transpiles through PseudoDart and `dart analyze`s clean; the
  Flutter side of the 2x2 runs that generated Dart, not hand-written calls.

## Status / next

The state model is now proven end-to-end: kit-owned UI-local state, app-state-in at
construction, AND app-state-update through `present` on both a reactive and an
imperative engine. Remaining (unchanged in spirit from log_2):

    - a STANDALONE runnable Flutter app (the generated Dart already executes and is
      now even tap-driven under the test harness; this packages it as an app window);
    - teach the emitter the kit's return types so build_* comes back `Widget`, not
      `dynamic` (runs either way; a typing nicety);
    - widen the kit toward the ~20-30 components a real screen needs.
