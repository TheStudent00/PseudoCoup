# log_4 — PseudoFlutter: present generalized, app packaged, types tightened

Date: 2026-06-22
Type: progress. Three functionality items finished after the state model was proven
(log_3): the generalized `present`, the ship path packaged as a runnable app, and
return types. Plus an aside revisiting the parked inverse-transpile idea from the
vantage point of what now exists.

## 1. `present` generalized — the leaf-cheat is gone

Review caught a real soft spot in log_3's `present`: the counter updated via
`label.text = …` (Kivy) and `notifier.value = …` (Flutter), both of which ride a
host **observable cell** (a Kivy property / a ValueNotifier). For a text leaf that
hid the imperative trigger — it looked like "set state → auto re-render," which is
just borrowing reactivity.

Fixed by lifting `present` to its real abstraction:

    zone(id, render, data)     a named slot whose content is render(data)
    present(id, data)          re-run the registered render, re-mount the result

`render` is a function `data -> widget` the app names (no lambda — discipline holds).
`text_zone` is now the degenerate case (`render` = wrap-in-text), so even the counter
goes through render-and-remount, not a property poke. Proven at a non-text rung
(`example/tabs_demo.py`): `present("tabs", i)` re-drives a **nav's selection** — a
structural change no single property could carry, so the zone must re-run `render_tabs`
and re-mount. `comparisons/tabs.png` (2x2): tap Micro → both engines move the highlight
identically. Reactive (ValueNotifier rebuild) vs imperative (`_ZoneBox` child-swap)
stays confined to the two kit bodies; the app source is one.

The registered-render-function IS the thing that makes this work: nothing auto-fires
on a bare state change. The framework (reactive) or `present` itself (imperative)
re-runs the render. That is the honest shape.

## 2. The ship path packaged as a real app

- Return types: the app annotates `build_screen() -> Widget`, so the emitted Dart is
  `Widget build_screen()` (not `dynamic`). `Widget` is honest in both languages and
  imported from the kit; no kit-stub inference system needed — the emitter already
  honours return annotations.
- `example/main.dart` (`main()` + `runApp`) **builds and runs as a native Linux
  binary** from the machine-generated `build_screen()`. The launched app finds
  `tokens.json` and renders. The `linux/` runner is committed.
- Verification note worth keeping straight: the side-by-side goldens are made by
  **offscreen** rasterizers — `flutter test --update-goldens` (in-memory canvas) and
  Kivy `export_to_png` (FBO) — neither opens a GL window, which is why they work
  headless. The *windowed* binary uses real GL/GTK and screenshots black under Xvfb
  (no GPU/compositor) — an environment limit, not the app; it renders the same tree
  the golden already proves.
- Still open (parked, not urgent): a **web** build needs the token loader off
  `dart:io` (sync `File` read) onto a bundled asset + async `preload`. Desktop/mobile
  are unaffected.

## 3. Aside — inverse transpiling (Dart -> Python), revisited

Parked since log_0 ("would be cool, not a driver"). With the forward path now mature,
its shape is clearer:

- **Feasibility, for our own emitter's output: tractable.** Most forward transforms
  are either bijective (kwargs <-> named args, snake_case preserved, control flow,
  class shape) or *explicit-scaffolding* that Python leaves implicit and Dart spells
  out — `late int n` / annotations, `str()` -> `.toString()`, int->double `.toDouble()`,
  null-asserts, defensive parens. Inverting those is mostly **erasure**: strip the
  scaffolding back to loose Python. A handful are genuinely inferred (a `dynamic`
  where the Python had no annotation; the `from kit import` rewritten to Dart imports)
  — those recover a *semantically equivalent* disciplined Python, not byte-identical
  source.
- **Not in scope: arbitrary Dart.** Inversion only makes sense for Dart shaped like
  the emitter's output. General Flutter/Dart (mixins, extensions, direct widget
  classes) does not map back — the disciplined subset is the whole contract.
- **The real value is verification, not authoring.** "Author in Dart, render
  elsewhere" cuts against the one-notation thesis. But **round-trip testing** —
  Python -> Dart -> Python', check Python' is semantically equivalent — would be a
  strong correctness harness on the forward transpiler. That is the one slice worth
  building if we ever want a harder forward guarantee.
- The **vestigial-`present`** instinct (keep the call even when empty on reactive
  targets) is exactly the kind of seam that keeps inversion tractable, and this run's
  general `present` — explicit named render functions, explicit `present` calls — is
  highly reconstructible. So nothing built this run *closed off* inversion; if
  anything the explicit shapes keep the door open.

**Verdict: stays parked as a product feature.** Feasibility for our-own-output is now
clearly "mostly erasure rules"; the cheap, high-value form is a round-trip *test*, not
a Dart-authoring path. No action now.

## Status / next

Everything prioritized ahead of widening the kit is done (return types, runnable app,
general present); web is parked by owner choice. Next: **more generic components** with
clean Kivy<->Flutter overlap (slider, chip, stepper, fab, …), each via the same
`compare.py` side-by-side.
