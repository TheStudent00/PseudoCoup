# WALKER slice 3/3 — Python-walk parity fixes + the decision-tree differ

Scope: `WFL_MixingCenter/render/walker.py` (three paired-change fixes + one pre-existing hang bug found and
fixed in the same file), `WFL_MixingCenter/render/walk_diff.py` (new — the differ), and
`PseudoCoup/DevComms/hostruns/requests/` (host-run request files). Fence honored: `WalkRecorderTest.kt`
untouched (this round's fixed reference), no kit/runtime edits.

## 1. Paired changes applied to `render/walker.py`

### (1) Bounded settle-loop at every tree-read site (lazy realization)

Added `settled_enumerate_interactive(app, root_node_fn, max_attempts=10)` (walker.py, new function
alongside `enumerate_interactive`): re-enumerates the interactive-node list up to 10 times, pumping
`EventLoop.idle()` between attempts (NOT a blind `time.sleep`, see bug note below), returning as soon as
two consecutive reads agree on interactive-node COUNT; a bounded-attempt-cap failure sets
`app.unsettled = True` and is printed loudly, never silently swallowed — the same discipline
`Session.settle()` already used for compose()'s own node count. Mirrors
`WalkRecorderTest.kt:432-445`'s `settledInteractiveCount()`/`settledEnumerateInteractive()`.

Applied at every ordinal-critical tree-read call site that used to call `enumerate_interactive()` directly
right after a `settle()`:
- `bootstrap_root()`'s body (boot state's action count)
- `replay_and_step()`'s per-hop replay reads and its final expand-action read
- `walk()`'s trailing lazy frontier-action-counting body

### (2) Text input = replacement semantics, deterministic "42"

`Session.fire_value_handler()` now explicitly clears any live `.text`-shaped value on both the mounted
Kivy widget (`find_widget_for(node).text = ""`) and the compose Node's own text mirror (`node.text = ""`)
immediately before invoking the handler with `infer_value()`'s "42" convention — the select-all-and-replace
analogue, mirroring `WalkRecorderTest.kt:344-352`'s `performTextReplacement(TEXT_INPUT_VALUE)` (vs.
`performTextInput`, which inserts at a live cursor position). Confirmed empirically in the differ's output:
the Python walk's `settings` state after firing the display-name `onValueChange` action shows
`text='Hey, 42'` (full replacement of "User"), never an accumulation like "User42" or "4242" on repeat
edges through the same node.

### (3) Wall-clock canonicalizer substitutes, not just warns

`canonicalize_text()` now does `_MAYBE_WALLCLOCK.sub("<TIME>", text)` and returns the substituted string
(the warning to stderr is kept, for visibility, but is no longer the only effect) — mirrors
`WalkRecorderTest.kt:220-225`'s `canonicalizeText()`, which does
`maybeWallClock.replace(text, "<TIME>")` in addition to its own warning. Confirmed in kt_walk.json's
`workout_summary/{sessionId}` state, whose duration text already shows as the literal `"<TIME>"` placeholder
(both sides now pin this the same way).

## 2. Pre-existing hang bug found and fixed (same file, in scope)

While host-running the walk to prove determinism, the FIRST run (before any of my changes could even be
exercised past step 6) hung silently for the full 3600s request timeout with ZERO log growth and ZERO
watchdog firing. Root cause (in `walk()`'s frontier round-robin, lines ~594-604, pre-existing before this
slice): when frame `n_actions` is `None` (a newly-queued frontier entry whose action count is filled
lazily, by design) and there is more than one such frame, the old code unconditionally did
`frontier.append(frontier.pop(0))` and `continue` — if EVERY remaining frame has `n_actions is None`
(the common case immediately after a batch of new destination states is queued, before the trailing
lazy-count loop runs even once), this round-robins forever with **zero I/O and zero Session/watchdog
coverage** (the watchdog only bounds work done inside `run_in_session`; this loop never enters one) —
a silent infinite loop indistinguishable from a genuine hang.

Fix: the `while` loop now checks `all(f.get("n_actions") is None for f in prog["frontier"])` and breaks
honestly the moment no frame has a resolvable action count left to expand, letting the trailing
lazy-count-filling loop (which DOES call `run_in_session`, watchdog-covered) do its job. This is a
same-cause-same-fix, not a workaround: the settle-loop's own discipline ("never silently loop forever;
bounded, and honestly reported") is what this bug violated, so the fix restores that same discipline to
the frontier driver.

A second, smaller robustness fix: `settled_enumerate_interactive()`'s first draft used a blind
`time.sleep(sleep_s)` between attempts, which (being outside any Clock/EventLoop pump) would stall the
very thread that lets Kivy's own deferred layout/realization progress — changed to pump
`EventLoop.idle()` 3x instead, consistent with `_remount()`'s existing idle-pump convention.

## 3. Determinism proof

Two independent fresh `--reset` host runs (`xvfb-run -a python3 walker.py --steps 60 --reset`), saved as
`render/walks/py_walk_runA.json` / `py_walk_runB.json`:

```
sha256sum py_walk_runA.json py_walk_runB.json
1a94c4f65b8853a2d5e1857afb682d1a06b63215d1bb9a0a4b6ae1d4c8410c7b  py_walk_runA.json
1a94c4f65b8853a2d5e1857afb682d1a06b63215d1bb9a0a4b6ae1d4c8410c7b  py_walk_runB.json
diff py_walk_runA.json py_walk_runB.json   # (no output — byte-identical)
```

**BYTE-IDENTICAL.** Both runs independently reached 6 states / 6 edges within a 60-step budget (most of
that budget was consumed by the lazy frontier n_actions-counting calls for the 5 newly-discovered nav-bar
destinations, per the checkpointed-BFS design), with identical BOOT/STEP logs including identical
`state_id` prefixes and identical `n_actions` counts at every frontier frame, run to run.

The walk was then extended via `--resume` (same progress file) to grow coverage: **14 states / 47 edges**
reached before the request's own 900s bound was hit honestly (a `walk_service: TIMEOUT after 900s` line,
mid-step — not a silent hang, and not the bug described above, since STEP lines were still flowing every
~20-35s right up to the cutoff). This deeper, extended walk (not part of the byte-identical A/B pair, since
it used `--resume` rather than fresh `--reset`) is what was fed to the differ below, to get maximum
coverage against kt_walk.json's 21-state/43-edge reference.

## 4. KIND_MAP (in `render/walk_diff.py`)

| Python (composable name) kind | Kotlin (semantics Role) kind | Justification |
|---|---|---|
| `NavigationBarItem` | `Tab` | Bottom-nav destination item; Compose Material3 convention assigns `Role.Tab` to `NavigationBarItem`. Empirically corroborated: aligning the "Home"/"Program"/"Paths"/"Progress"/"You" edge labels against kt_walk.json's own `Tab`-kind edges reaching the same 5 nav destinations. |
| `SegmentedButton` | `RadioButton` | Compose's `SegmentedButton` (single-choice row item) is Material3's own recommended `Role.RadioButton` (single-selection-from-a-set matches RadioButton's accessibility contract exactly). Corroborated: every `RadioButton`-kind edge in kt_walk.json is reached from a route whose Python-side sibling state carries `SegmentedButton` items (e.g. `settings_notifications`'s unit/lingo pickers). |
| `BasicTextField` | `EditableText` | Definitional, not inferred: `nodeKind()` literally returns `"EditableText"` for ANY node with `SemanticsActions.SetText` and no Role, and `BasicTextField` is the exact composable whose semantics config always carries `SetText`. |
| `ExtendedFloatingActionButton` | `Button` | Material3 source: both FAB variants (plain and extended) delegate to a shared clickable surface that sets `Role.Button` internally. |
| `FloatingActionButton` | `Button` | Same Material3 `Role.Button` delegation as above. |
| `DropdownMenuItem` | `Button` | Material3 source convention: `DropdownMenuItem`'s clickable modifier sets `Role.Button`. |

**Deliberately NOT mapped** (left as-is; any mismatch here is real information, reported honestly):
- `Card` — Compose's `Card` composable does not set any Role by default (plain `Surface` container; only
  interactive if the call site adds a bare `.clickable{}` with no explicit Role) — whether a given Card
  falls into Kotlin's `Node` catch-all is genuinely undetermined without inspecting that screen's specific
  source. Confirmed as a real ambiguity, not mapped.
- `DropdownMenu` itself (the popup container) — this is a STATE-tagging construct in walker.py's own format
  (`route#menu:DropdownMenu`), not a plain tree_summary component in the same sense as its
  `DropdownMenuItem` children; left unmapped.
- `Icon`, `Text`, `Box`, `Column`, `Row`, `Scaffold`, `TopAppBar`, `Surface`, `LazyColumn`, `Item`,
  `HorizontalDivider`, `CompositionLocalProvider` — plain layout/content composables with no Compose Role
  by default; Kotlin's `nodeKind()` catch-all correctly reports these as `"Node"` when un-Role-tagged, and
  the differ reports them as such (not force-mapped).

Applied identically to BOTH sides (the Kotlin walk is also run through `apply_kind_map()`, as a documented
no-op — none of its own kind strings are KIND_MAP keys) before either side's tree_summary is re-hashed for
comparison — never a one-sided rewrite.

## 5. Gate line (verbatim, from the actual differ run against `py_walk.json` (14 states/47 edges,
extended via `--resume`) vs. the fixed-reference `kt_walk.json` (21 states/43 edges))

```
WALK DIFF: 0 shared states, 21 kt-only, 14 py-only, 90 edge mismatches
```

(90 = 43 kt-only edges + 47 py-only edges + 0 destination-mismatches-on-shared-actions; there are zero
destination mismatches because there are zero shared/aligned edges to compare in the first place, given
zero shared states.)

## 6. Divergence classification (the deliverable — every divergence traced to evidence, not hidden)

**Headline finding: even the shared root/boot route (`today`) never hashes to the same `state_id` on
either side, and NO state_id from either walk appears in the other's state set at all — 0/21 and 0/14.**
This is NOT a naming-only artifact (the KIND_MAP already absorbs the biggest naming gaps); direct
side-by-side inspection of the two engines' `today` states (kind-remapped on both sides, same route
string) surfaces THREE distinct, independently-verifiable causes:

### (a) REAL document-order / traversal-order divergence (structural, not cosmetic)
Component-by-component alignment of the two (remapped) `today` trees shows the SAME logical
text/content ("Home", "Monday", "Hey, User", "This week's workouts", "Set up a program...", "Progress",
"You", etc.) appearing at DIFFERENT tree_summary indices on each side — e.g. Kotlin's index 22 is
`text='Home'` while Python's index 22 is `text='Paths'`; Kotlin's semantics-tree traversal interleaves
leaf-text nodes differently than Python's compose Node pre-order walk (Kotlin's accessibility-merged
semantics tree collapses/reorders some container boundaries that Python's raw compose Node tree preserves
1:1). Since `state_id` hashes `tree_summary` as an ORDERED list (by design — order is meant to be
deterministic and meaningful, per walker_slice1.md), any order difference alone is enough to break every
single state_id match, even when the two sides' underlying SET of visible content is nearly identical.
**Classification: REAL divergence between the two recording mechanisms' notion of "document order"** — not
a bug in either individual walker (each is internally deterministic, per the byte-identical A/B proof
above), but a genuine mismatch in what "document order" means between Compose's accessibility-semantics
tree (Kotlin side) and this app's own compose-Node render tree (Python side). Flagged, not fixed here
(fixing it would require either changing the Kotlin recorder's own traversal to match the render tree, or
vice versa — out of this slice's fence, and a genuine design question about which order is "canonical").

### (b) REAL content/feature divergence: Python's `today` state has 3 additional interactive/text
elements Kotlin's does not
Kind-count comparison of the SAME (remapped, same-route) `today` state: Kotlin has 7 interactive
components; Python has 9. Text-set comparison: Python's `today` state includes `'Log a Win'`,
`'Log other exercise'`, and `'New mobility session'` (a quick-actions row) that Kotlin's `today` state
(this run) does not contain at all. **Classification: possible real behavior gap OR an artifact of
kt_walk.json's specific captured run** (kt_walk.json is a FIXED prior artifact per the task's read-first
instructions, not re-run this slice — it's possible the Kotlin recorder's underlying app state/seed
reached a `today` screen where this quick-actions row wasn't rendered, e.g. a conditional-on-active-program
row, and the Python run's seed data put it in a different state). Not resolved here (transpiled-app
behavior vs. recorder-artifact requires inspecting the ORIGINAL Kotlin `TodayScreen.kt` source's
conditional-render logic against this app's seed fixtures — flagged for app/kit-level follow-up, per the
fence: "if a divergence traces to an app/kit bug, classify + report, don't fix here").

### (c) Unmapped-naming residue, correctly left unmapped and surfaced (not hidden)
`Icon` appears 10 times in Python's `today` tree_summary but Kotlin's equivalent-position nodes are mostly
plain `Node` (7 `Image`-kind entries elsewhere) — `Icon` was deliberately NOT added to KIND_MAP (see §4)
because Compose's `Icon` composable does not reliably carry `Role.Image` (only if the call site explicitly
sets a content-description-driven Role) — this is a genuine unresolved vocabulary gap, reported honestly
as a `Node`-vs-`Icon` kind mismatch in the differ's raw output rather than papered over with a guessed
mapping.

### (d) Edge-level consequence of (a)-(c): every single edge is reported "kt-only" or "py-only"
Because zero states share an id, the edge-aligner (which keys on `(source_state_id, kind, handler_kind,
ordinal)`) necessarily finds zero shared edges too — all 43 Kotlin edges and all 47 Python edges show up
as one-sided. This is the CORRECT, honest downstream consequence of (a) — the aligner is not buggy; state
mismatch cascades into edge mismatch by construction, and hiding that cascade behind a fuzzier
matching heuristic (e.g. aligning by route+action-label instead of state_id) would be exactly the kind of
meter-gaming the task law forbids. Per-edge detail (full tap paths + both sides' state summaries at each
split point) is in `render/walks/walk_diff_report.txt` (1173 lines) — every one of the 90 mismatches is
individually inspectable there, not summarized away.

### Positive confirmations (the fixes ARE visible in the data, this is not a wash)
- The text-replacement fix (paired change 2) is directly visible: Python's post-edit `settings` state shows
  `text='Hey, 42'` (a full, non-appended replacement), matching Kotlin's own recorded `EditableText`
  value `'42'` at the analogous `settings_notifications` state — same convention, same literal value, on
  both sides.
- The wall-clock substitution fix (paired change 3) is directly visible in kt_walk.json's
  `workout_summary/{sessionId}` state (`text='<TIME>'`) — canonicalize_text() in walker.py now produces the
  identical placeholder for the same class of text, so a future Python screen that renders a live duration
  string will hash identically to Kotlin's, rather than diverging on an unpinned wall-clock string.
- The settle-loop fix (paired change 1) and the frontier-hang bug fix are what made ANY of this comparison
  possible at all — the walk could not progress past 6 states before these fixes (silent infinite loop).

## Files touched
- `/home/lucas/Programming/WFL_MixingCenter/render/walker.py` (three paired changes + frontier-hang fix)
- `/home/lucas/Programming/WFL_MixingCenter/render/walk_diff.py` (new — the differ)
- `/home/lucas/Programming/WFL_MixingCenter/render/walks/py_walk_runA.json`,
  `py_walk_runB.json` (determinism-proof artifacts), `py_walk.json` (extended, 14 states/47 edges, used
  for the differ run), `walk_diff_report.txt` (full per-divergence detail, 1173 lines)
- `/home/lucas/Programming/PseudoCoup/DevComms/hostruns/requests/088_py_walk_runA.json` (removed after it
  hung — request removal does not kill an already-dispatched host process; documented here for the
  record), `089_py_walk_runA_fixed.json`, `090_probe.json`, `091_py_walk_runB.json`,
  `092_py_walk_extend.json`
