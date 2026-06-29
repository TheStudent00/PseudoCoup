# log_121 — the reactivity model: true vs false reactive, why it redraws everything, and Kobweb

Date: 2026-06-28
Type: explainer (communication protocol). Grounds the imperative/reactive thread + the staleness bug
(log_120). Answers a sharpened set of user questions; architecture calls left to the user.

## Direct answer — your model, checked

Your mental model is essentially right. Three sharpenings:

1. "Kotlin is reactive; an object intended to be reactive must be wrapped in MutableStateFlow."
   Close. The Kotlin LANGUAGE isn't reactive — COMPOSE's reactivity comes from observable wrappers,
   and you opt in by wrapping. In WFL's viewmodels that wrapper is `MutableStateFlow`/`StateFlow`.
   A plain `val x` is not reactive; `MutableStateFlow(x)` is. So: yes, reactivity is opt-in via a
   wrapper.

2. "PseudoCoup is false-reactive, never true-reactive unless explicitly wired; `State` is the
   special object wired into the targets." CORRECT, and it's the crux. `State` is the SINGLE
   observable primitive, and the transpiler wires it at BOTH ends: incoming
   `MutableStateFlow(x) -> State(x)`; outgoing `State -> the target's native reactive primitive`
   (Dart ValueNotifier/setState, etc.). Nothing is reactive unless it is a `State`.

3. "False-reactive because when it re-draws, it re-draws everything." CONFIRMED, literally. The
   recompose host is `router.remount_current()`, which is `_teardown_current(); _mount(current)` —
   it tears the WHOLE current screen's zones down and re-runs the screen's `build()` from scratch.
   Any one `State.set()` in an event => the entire visible screen rebuilt. (The `if zone_id in
   self._zones: return` guards in the kit are within-ONE-build idempotency, not cross-rebuild
   reconciliation — teardown already removed the zones, so everything is recreated.)

## Glossary

true-reactive
    A change to a value propagates to the UI on its own, with fine-grained scope — the framework
    knows which view read which value and repaints only those. (Jetpack Compose's snapshot system.)
    WFL gets this on Android for free.

false-reactive (PseudoCoup's model)
    A change marks the frame dirty; after the event, the framework repaints by rebuilding the WHOLE
    current screen. No per-view dependency tracking. "Auto" (the handler doesn't call repaint
    itself) but COARSE (it redraws everything), and only the things you wired as `State` participate.
    e.g. `state.set(2)` in a tap handler -> dirty -> after the handler, `remount_current()` rebuilds
    the entire screen.

State  (src/reactive.py)
    The one observable primitive. Read `state.value`; write `state.set(v)` — a changed write calls
    `recompose.invalidate()`. It is the pivot the transpiler wires: `MutableStateFlow <-> State <->
    each target's reactive primitive`. (It uses an explicit `.set()` rather than `=`-interception so
    the Kt->Py map stays 1:1: Kotlin `_flow.value = x` transpiles to `state.set(x)`. Python COULD
    fire-on-assignment via a property setter / `__setattr__`; PseudoCoup chose not to, on purpose.)

recompose scheduler  (the dirty-flag + one choke point)
    `begin()` (clear dirty) -> handler runs -> `set()`/`invalidate()` may set dirty -> `flush()`
    (one repaint if dirty). The kit wraps EVERY event in begin/flush (`UI._deliver_event`), so N
    writes in a handler => exactly one repaint, after the handler returns. Repaint = rebuild the
    current screen.

invalidate()  (the no-State escape hatch)
    Mark dirty WITHOUT a State write — for VM actions that mutate the non-reactive data layer (the
    db), which "returns plain values and notifies no one" (its docstring). This is the path the
    generated gym_list uses: delete -> `invalidate()` -> rebuild -> `build()` re-reads. log_120's
    bug was that the re-read served a frozen snapshot; the lazy shim makes `build()` re-read FRESH,
    which is the only reason the reactive plumbing has anything new to draw.

## "Can it redraw only that layer and above, not everything?" — yes, and it's half-built

It can, and the retained zone tree is exactly the substrate. The scope you want is actually that
zone and the subtree BELOW it (the part that consumed the changed data); ancestors above don't
change. Two ways, both living ENTIRELY in the kit (no change to screens or to `State`):

- RECONCILE (React/DOM style — the natural fit): on recompose, DON'T teardown. Re-run `build()`
  fully (cheap — it only issues `define_*` commands + reads data), and let the kit DIFF the re-issued
  tree against the retained one: existing ids stay (the `if zone_id in self._zones: return` guard is
  already this), changed text/content updates in place (`present()`), and zones not re-issued get
  removed. Result: `build()` re-runs wholesale, but only the changed NATIVE widgets are touched.
- SCOPED recompose (Compose style): track which zones read which `State`, and re-run only the
  affected subtree's build closure. More faithful/efficient, but needs dependency tracking + `build()`
  split into independently-runnable pieces.

So today's teardown+rebuild is the SIMPLE-correct version; reconciliation is the efficiency upgrade,
and notably the retained-zone model (the "Kivy-on-Flutter" shape we discussed) is what makes it
possible — it is not just overhead, it is the diff substrate.

## Kobweb — what it is, and is it useful here

Kobweb = a Kotlin web framework on top of Compose HTML (Compose-for-Web), Next.js-style structure,
live reload. You write Compose-style Kotlin; Kotlin/JS compiles it and Compose HTML renders it to
the browser DOM.

Is it "a complete translation of the app into HTML/JS, easier to transpile"? Two honest halves
(correcting an earlier too-dismissive take of mine, which leaned on difficulty rather than the real
reason):

DIFFICULTY — for a WEB target it is plausibly MUCH EASIER than our path, not harder. Jetpack Compose
-> Compose HTML is a SAME-paradigm port (both are Compose: same @Composable, same state model, same
recomposition) — mostly remapping the component vocabulary (Column/Row/Material3 -> Div/CSS/Silk) —
versus our cross-paradigm Kotlin -> Python-imperative-kit. And Kotlin/JS compiles the viewmodels/
domain directly. If the goal is DESIGN-fidelity (theme/config) not API-fidelity, that port is far less
work for web. So the difficulty objection is weak; I had it wrong.

THE REAL REASON it doesn't fit — it BYPASSES THE LEDGER. The project's spine is traceability: every
transpiled object tagged/traced to Kotlin, no drift (the thing whose absence "could cause project
failure again"). A Kobweb port is an UNTRACED hand-port to Compose HTML — nothing guarantees the
Compose-HTML maps faithfully back to the WFL Kotlin. So Kobweb does NOT "complete" the ledger; it
SIDESTEPS it. The thesis is not "get WFL on a screen" — it is "get WFL onto targets WITH a verified
trace." Kobweb gives the former without the latter; it is close to the exact thing the ledger exists
to prevent. So whether it's worth it reduces to: would you accept an UNTRACED port for a web-only
target? Legitimate question, the user's call — but it is not free.

On ledger COMPLETENESS specifically: the ledger already does tree + connectivity (Kotlin<->Python
structure + 1-degree connections). Its gap is the GEOMETRY layer (rendered boxes — policy/intent yes,
pixels no). Kobweb would NOT close that for the real targets; and the rendered ground-truth ALREADY
exists in-repo: tools/dualtrace/capture.py dumps the ORIGINAL Android app's accessibility tree via
uiautomator. So the geometry ground-truth is the real WFL app, not Kobweb. Kobweb would be a NEW
untraced target needing its OWN ledger entry — adding to the surface, not closing it.

Where it IS worth a look: as a REFERENCE for the declarative-Compose -> retained-DOM reconciliation
(the fine-grained-redraw upgrade above) — the DOM is a retained mutate-in-place tree, the same shape
as our zones. Target decisions are the user's.
