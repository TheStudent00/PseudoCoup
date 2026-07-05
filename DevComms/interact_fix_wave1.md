# Interaction Oracle — Fix Wave 1

Result: **15 failures → 3**. The 3 remaining are all the instrument-side TextFieldValue
`.text` probes (out of scope per brief). All 5 app-side groups fixed. `run_kotlin_tests.py`
holds 160/160. No app-specific identifiers in the transpiler/runtime diff.

Files touched (all under `tools/pseudokotlin/`):
`build_mixingcenter.py`, `nodes/declarations.py`, `nodes/expressions.py`,
`runtime/compose.py`, `runtime/kotlin_rt.py`, `transpiler.py`.

---

## Group 1 — trailing-lambda slot dropped [5 hits]
`ConditioningFinishedView() got an unexpected keyword argument 'content'`

- **Cause:** Kotlin binds a trailing lambda to the callee's LAST parameter (here named
  `extra`). The transpiler only knew the last-param name for **same-file** callees
  (`self._last_param`); for a cross-file callee it defaulted the keyword to `content=`,
  which the callee doesn't declare → unexpected-kwarg.
- **General fix:** a project-wide `fn name → last-param name` registry
  (`expressions.GLOBAL_LAST_PARAM`), populated by a build pre-pass
  (`build_mixingcenter.scan_last_params`) that reuses the transpiler's own tree-sitter
  param scan (`KtToPy._scan_top_level`). `_join_trailing` now falls back to it before
  `content`. Moves every cross-file trailing-lambda-after-named-arg call, not just this one.
- **Files:** `nodes/expressions.py` (`GLOBAL_LAST_PARAM`, `_join_trailing`),
  `build_mixingcenter.py` (`scan_last_params` pre-pass).

## Group 2 — `String.filter{}` on a bare str [3 hits]
`'str' object has no attribute 'filter'`

- **Cause:** Kotlin CharSequence stdlib extensions (`filter`, `takeWhile`, `map`, `count`,
  …) are not methods on a Python `str` (and some — `count`/`index` — exist with a *different*
  meaning). `value.filter{…}` emitted a plain `value.filter(...)`.
- **General fix:** modeled on the existing `ktext` extension dispatcher. Added a
  `kstrext(recv, name, *args)` runtime dispatcher + a `_CHARSEQ_EXT` table of Kotlin
  CharSequence semantics. On a `str` it applies Kotlin semantics; on any collection the real
  member wins (Kotlin resolution rule), so `KtList`/`KtMap`/`KtSet` are unchanged. The
  transpiler routes the `_CHARSEQ_EXT_FNS` name set through `kstrext` at the method-call site.
- **Sub-finding (surfaced once filter ran):** `Char::isDigit` (→ `Char.isDigit`, undefined)
  and instance `c.isDigit()` (Python str has `isdigit`, not `isDigit`). Added a `Char`
  companion object in `kotlin_rt.py` for the method-reference form, and mapped the Char
  predicate/transform instance methods (`isDigit`→`isdigit`, `isLetter`→`isalpha`,
  `uppercaseChar`→`upper`, …) into `_STDLIB_METHODS`.
- **Files:** `runtime/kotlin_rt.py` (`kstrext`, `_CHARSEQ_EXT`, `Char`),
  `nodes/expressions.py` (`_CHARSEQ_EXT_FNS`, routing branch, Char method map).

## Group 3 — bare `toLong()` on implicit extension receiver [1 hit]
`NameError: name 'toLong' is not defined`

- **Cause:** inside a top-level extension body (`fun Double.fmt()`), Kotlin's `toLong()` is
  `this.toLong()`. The `.toLong()`→`int(recv)` rewrite only fires on an **explicit** receiver;
  a bare call emitted `toLong()` → undefined.
- **General fix:** a `self._ext_self` depth counter (set while rendering a top-level
  extension body in `declarations._function`). In `_call`, a bare identifier call whose name
  is a `_STDLIB_METHODS` key and isn't shadowed/local/top-level is rewritten as the same
  stdlib transform with receiver `self` (`toLong()` → `int(self)`). Covers every navigable
  stdlib method called bare-on-`this` in an extension, not just `toLong`.
- **Files:** `transpiler.py` (`_ext_self`), `nodes/declarations.py`,
  `nodes/expressions.py` (`_call`).

## Group 4 — `KtMap.maxByOrNull` missing [1 hit]
`'KtMap' object has no attribute 'maxByOrNull'`

- **Cause:** `groupingBy{}.eachCount()` yields a `KtMap`; the wrapper lacked `maxByOrNull`.
- **General fix:** added `maxByOrNull`/`minByOrNull`/`maxWithOrNull` to `KtMap`, selector
  applied over `KtEntry` entries, returning the entry (or `None` when empty) — matching Kotlin.
- **Files:** `runtime/kotlin_rt.py` (`KtMap`).

## Group 5 — remembered `State.value` reads back wrong type [2 hits]
`'bool' object has no attribute 'strip'` / `'bool' object has no attribute 'exercise'`

- **Cause (diagnosed + reproduced):** the composition slot table keyed `remember` values by
  **raw ordinal position** within a scope. When conditional content appears (a dialog opened
  by the fired handler) it inserts `remember` calls mid-tree, shifting the ordinals of every
  later `remember`; a later slot then reads back an earlier slot's value. With empty keys
  nothing forces a recompute, so `query.value` (a str state) resolved to a *different* call
  site's `bool` state. Minimal repro: a conditional `remember{mutableStateOf("")}` placed
  before an always-present `remember{mutableStateOf(False)}` returns `False` on the second
  compose. This was a general runtime bug affecting any screen with conditional remembered
  state — not dialog-specific.
- **General fix:** slots are now keyed by **call site** (source file+line of the
  remember/effect call) plus a per-site occurrence index (so loops still get distinct slots),
  which is Compose's own positional-memoization model. `Composition.slot` uses a
  `(site, occ)`-keyed dict; `_call_site()` walks to the nearest frame outside `compose.py`.
  Conditional content can no longer shift a slot onto a foreign call site.
- **Files:** `runtime/compose.py` (`slot`, `_call_site`, `Composition.__init__/compose`).

---

## Gate outputs (verbatim)

### `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py`
```
INTERACT: 513 fired, 510 ok, 3 failures across 27 screens

== failure groups ==
  [2] AttributeError @ WorkoutExecutionScreen.py:598 :: '?' object has no attribute '?'
  [1] AttributeError @ WorkoutExecutionScreen.py:596 :: '?' object has no attribute '?'
```
All 3 remaining are the TextFieldValue `.text` instrument-limitation probes (`'str' object
has no attribute 'text'`) the brief scoped out. NOTE: the brief predicted "drop to 2", but
the original catalog lists 3 of these `.text` probes (596×1 + 598×2), all labeled
instrument-side — so 3 is the correct instrument floor, not 2. No app-side failures remain.

### `cd ~/Programming/PseudoCoup/tools/pseudokotlin && python3 run_kotlin_tests.py`
```
RESULT: 160/160 pass
```

### App-identifier check (grep of transpiler/runtime diff)
```
CLEAN: no app-specific identifiers in transpiler/runtime diff
```
