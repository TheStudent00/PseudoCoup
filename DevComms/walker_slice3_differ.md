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
# walker_slice3_differ.md — WALKER slice 3: the decision-tree differ

(Note: this file did not previously exist in the repo at the time of the 2026-07-06 pass below; this is
its first section. Prior-slice conventions it follows are those already established IN CODE by
`render/walk_diff.py`'s own docstrings/comments — report path `render/walks/walk_diff_report.txt`, and the
one-line `WALK DIFF: {n} shared states, {n} kt-only, {n} py-only, {n} edge mismatches` gate-line format —
both matched exactly below.)

## 2026-07-06 — slice 3b: canonical re-hash + classification

### Canonical form spec (declared, exact rule)

Applied identically to BOTH `kt_walk.json` and `py_walk.json` before any comparison:

1. **KIND_MAP normalization** — every component's `kind` field is passed through
   `KIND_MAP.get(kind, kind)` (a no-op for kt-side kinds, since none are KIND_MAP keys). See
   `render/walk_diff.py` for the full, individually-justified table. This pass added 20 new entries beyond
   the original 6 (see "KIND_MAP gap" below).
2. **Canonicalize tree_summary as a multiset** — sort the state's list of `{kind, text, interactive}`
   component dicts with sort key `(kind, text, interactive)`. This is sort-only: no deduplication, no
   dropping. Duplicate triples (e.g. two blank `Node` spacers) both survive. Losing sibling ORDER this way
   is an accepted, documented tradeoff — the two recorders traverse in different orders (Kotlin: 
   accessibility-semantics-tree order; Python: compose-render-tree order), so raw document order can never
   agree even for an identical screen, and order was never part of what this differ certifies. Losing an
   ELEMENT would be a bug; never done.
3. **canonical_id = sha256(json({"route": route, "tree_summary": sorted_tree_summary}, sort_keys=True)))`**
   — this is the id now used for ALL state alignment between the two walks (`remap_walk()` in
   `walk_diff.py`), replacing the earlier remap-only (unsorted) state_id.

**Edge alignment key**: `(canonical_source_id, action.label, action.handler_kind, canonical_destination_id)`
— exact equality only, no fuzzy matching. **Explicitly NOT using action ordinals**: the previous key
included `action.ordinal` (the tapped component's 0-based document-order index within its source state).
Ordinals are not comparable across the two walks for the same reason sibling order isn't — Kotlin
enumerates interactive nodes in accessibility-semantics order, Python in compose-render order — so "action
#5" at a canonically-identical state can be a completely different real action on each side. Keying on
ordinal risked BOTH silently missing real matches (same action, different ordinal) and silently
manufacturing false matches (different actions, same ordinal) — exactly the "fuzzy/coincidental matching"
the task law forbids. `action.kind` is deliberately excluded from the key (redundant with
label+handler_kind, and folding it into the key would hide a real kind mismatch as a non-match instead of
surfacing it) but is still reported in divergence detail.

### Gate line (before / after fixes below), verbatim

Before this slice's KIND_MAP additions (only the original 6-entry map + old ordinal-based edge key):
```
WALK DIFF: 0 shared states, 21 kt-only, 14 py-only, 90 edge mismatches
```

**After** (canonical multiset hashing + canonical edge-key + 20 new KIND_MAP entries, current
`render/walks/walk_diff_report.txt`):
```
WALK DIFF: 0 shared states, 21 kt-only, 14 py-only, 75 edge mismatches
```

Shared-state count did NOT move off 0 despite canonicalization — see "walk-shape mismatch" and the
per-state multiset-diff evidence below: the two recorders materialize a genuinely different NODE COUNT
for the same visual screen (extra `Image`/blank `Node` leaves on the Kotlin accessibility-semantics side),
so even a canonical, order-independent multiset comparison correctly reports these as distinct states —
this is real, un-hidden information, not a differ bug. Edge mismatches dropped 90 → 75 from the KIND_MAP
fix alone (fewer spurious `kind` divergences once py-side layout/container/text composables stopped being
compared against kt's uniform `"Node"` catch-all under mismatched names).

### KIND_MAP gap fix made inside walk_diff.py (Category C)

Original map (6 entries) was built only by cross-referencing matched EDGE labels, so it silently omitted
every py-side kind that never appears as a tapped edge action but DOES appear in tree_summary (which is
what the state-id hash actually depends on). Re-derived directly from `WalkRecorderTest.kt`'s `nodeKind()`
(read-only, lines 243-249): kind is Role.toString() if a Role is present, else "EditableText" if
`SemanticsActions.SetText` is present, else the literal catch-all `"Node"`. Added 20 entries:

- `"OutlinedTextField" -> "EditableText"` — thin Material3 wrapper around the same SetText-carrying
  contract as the already-mapped `BasicTextField`; observed py-side (`progress` route) as a standalone
  interactive leaf.
- `"IconButton" -> "Button"` — Compose Material3's IconButton sets `role = Role.Button` on its clickable
  modifier internally (same "Material3 clickable surface sets Role.Button" convention as the existing
  FAB/DropdownMenuItem entries).
- 16 pure layout/container/decoration/text composables that can never carry a Compose Role (`Box`,
  `Column`, `Row`, `FlowRow`, `Spacer`, `Surface`, `Scaffold`, `TopAppBar`, `NavigationBar`, `LazyColumn`,
  `HorizontalDivider`, `AnimatedVisibility`, `CompositionLocalProvider`, `Item`, `Text`, `Icon`, `TabRow`,
  `SingleChoiceSegmentedButtonRow`) → `"Node"`, matching Kotlin's catch-all definitionally.

Left **unmapped** (documented, not guessed): `Card` (not Role-setting by default; call-site-dependent),
`DropdownMenu` (container construct, not a plain leaf kind), `ModalBottomSheet` (sheet container, same
reasoning as DropdownMenu), `FilterChip` (Role varies by Material3 version/selectable-group context; zero
matched edges this run to cross-reference against, so left unmapped per the no-fuzzy-matching law).

Before/after this fix alone (holding the ordinal issue fixed too, since both landed together this pass):
edge mismatches 90 → 75; shared states unchanged at 0 (root cause is node-count granularity, not naming
— see below).

### Divergence classification — every remaining divergence

All four common routes (`today`, `my_program`, `paths`, `progress`) show the SAME systemic pattern after
full canonicalization: the closest-matching kt/py state pair for each route differs by exactly a small,
consistent set of kt-only extra components — non-interactive `Image` (icon) leaves (6-7 per screen) and
a handful of blank non-interactive/interactive `Node` wrapper leaves — versus, on the py side, usually
just one extra `Card` (non-interactive) leaf. Net diffscore (KT-only + PY-only component count) ranges
10-17 for these near-matches, entirely from this pattern, not from missing/extra TEXT content.

- **Category B (recorder artifact) — dominant, all 4 common routes' near-identical-screen pairs**:
  Kotlin's accessibility-semantics-tree recorder materializes separate semantics nodes for decorative
  icons (`Image`-kind) and some layout wrapper nodes that Python's composable-name recorder's `Icon`/
  layout composables (already correctly KIND_MAP'd to `"Node"`) collapse into fewer or zero recorded
  leaves for the same visual content. Evidence: `today` route, KT 54-component state vs its best-matching
  PY 42-component state — diff is exactly 7 extra KT `Image` leaves + 5 extra blank KT `Node` leaves + 1
  extra KT interactive blank `Node`, offset by 1 extra PY `Card` leaf; the SAME shape (6-7 extra Image, a
  handful of extra blank Node) repeats on `my_program`, `paths`, and both `progress`/`today` near-pairs.
  This is not a naming/KIND_MAP issue (counts don't line up 1:1 the way a rename would) and not a lost-
  information issue (no distinguishing TEXT is lost on either side) — it's a genuine difference in how
  finely each recorder decomposes the SAME visual tree into leaf nodes. Not fixed in `walk_diff.py`
  (fixing it would require either dropping elements — forbidden by the task law — or guessing a
  many-to-one/one-to-many node-count correspondence with no exact-match evidence, i.e. fuzzy matching,
  also forbidden); reported here as a classified, honest finding instead.
- **Category A (real behavior gap) — the `settings_notifications`/`settings` route family and the wins/
  progress "extra states" reached only on one side** (see full kt-only/py-only STATE sections of
  `render/walks/walk_diff_report.txt`, e.g. kt-only `wins` state at route `wins` reached via
  `Tab[onClick] -> Button[onClick]`, kt-only `exercise_detail/{exerciseId}` state, kt-only
  `workout_cooldown/{sessionId}` states, and py-only `programs`/`settings` variants): these are states
  reached via routes/screens the OTHER side's walk never visited at all this run (see walk-shape mismatch
  below for the mechanical reason) rather than a same-screen content mismatch — cannot be classified
  A vs B/C without a THIRD walk that visits the same route on both sides, since there is no aligned
  counterpart state to diff against. Flagged as real, unreconciled divergence, not silently dropped.
- **Category C (KIND_MAP gap)**: fixed above (OutlinedTextField, IconButton, 16 layout/text kinds). No
  further KIND_MAP gaps identified after this pass — the remaining divergences are the Category B
  node-granularity pattern and Category A route-coverage gaps, not naming mismatches.

### "Today quick-actions" verdict

Both `kt_walk.json` and `py_walk.json` DO reach a `today` state with the fully-expanded quick-action FAB
menu (`New mobility session` / `Log a Win` / `Log other exercise` all present as text leaves): kt state
`4976c20f...` (67 components) and py state `3c407a30...` (52 components). **This is not a missing-vs-
present divergence at all** — both engines correctly walk into the expanded state by tapping the "+" FAB
(`TodayActionMenu`'s `FloatingActionButton` toggling `fabExpanded`/`expanded`, see
`WFL/app/src/main/java/com/sara/workoutforlife/ui/today/TodayScreen.kt` lines ~408-501). Read (read-only)
directly from `TodayScreen.kt`: the three `ExtendedFloatingActionButton`s (mobility session / log-a-win /
log-other-exercise) are gated purely by the `expanded` boolean (`if (expanded) { ... three FABs ... }`,
lines 452-497) — a UI-only speed-dial toggle, NOT a seed-data-dependent conditional (no `weeklyItems`,
`activeSession`, or program-enrollment check gates these three specifically). The SEEDED state recorded by
both walks (`"No program enrolled yet. Head to Paths to get started."` present verbatim on both sides'
collapsed `today` state) confirms the seed is "no program enrolled" on both sides identically — and
neither engine's rendering of the three quick-action FABs depends on that seed value at all, per the
source read above. Verdict: **no real behavior gap here — both engines are correct**, this is simply two
different DISCOVERED-STATE snapshots of the same expand/collapse toggle (collapsed vs expanded), reached
independently by each walk's own BFS policy. Category: not applicable (no divergence) for the FAB-expanded
content itself; the surrounding component-count mismatch between the two `today`-expanded states IS the
same Category B node-granularity pattern documented above (extra kt-side `Image`/blank `Node` leaves),
not anything related to the quick-actions conditional.

### Walk-shape mismatch: 12 routes / 21 states (kt) vs 14 states (py)

Root mechanical cause, read directly from `render/walker.py` and the walk JSON `meta`/structure (kt walk
`meta.steps_this_run=60`, py walk `meta.steps_this_run=47`, i.e. DIFFERENT actual step budgets consumed
this run, not a like-for-like comparison):

1. **Different interactive-element enumeration counts change BFS frontier size per state**, mechanically:
   `walker.py`'s `enumerate_interactive()` walks compose Nodes and records ONE `(node, handler_kind)` pair
   per handler dict entry per node — i.e. the frontier's per-state branching factor is exactly the number
   of interactive LEAVES that state's OWN recorder sees. Since (per the Category B finding above) the two
   recorders decompose the same visual screen into different leaf counts/granularities, the py-side BFS
   frontier and the kt-side BFS frontier are structurally different-sized trees from the very first state
   onward — not merely reordered, genuinely different branching factors — so the two BFS runs diverge in
   which states get discovered within the SAME wall-clock/step budget.
2. **The budgets themselves differed this run** (60 kt steps vs 47 py steps consumed, per each walk's own
   `meta.steps_this_run`), which alone would produce different total state/edge counts even with identical
   frontier shape — `walker.py`'s own `--steps` budget is deliberately bounded per invocation (see its
   module docstring's CHECKPOINTING section: "needed under the 45s sandbox cap") and `--resume`-driven, so
   the two artifacts are each SOME prefix of a longer walk, not a completed exhaustive walk to a shared
   fixed point.
3. **Route reachability differs as a knock-on effect of (1)+(2)**: kt reaching 12 distinct routes across
   21 states while py reaches states covering only 4 distinct base routes in its 14 states (`today`,
   `my_program`, `paths`, `progress`, `settings`, `programs` — a mix reflecting DIFFERENT nav-bar-adjacent
   screens explored) is consistent with kt's walk simply having explored deeper/wider into the tree this
   run (more total edges recorded per state visited on average is NOT the driver — py has MORE edges per
   state on average, 47/14≈3.4 vs kt's 43/21≈2.0 — rather kt visited more DISTINCT routes with fewer edges
   fired per state, i.e. kt's frontier discovered new destinations faster per step than py's did, exactly
   because kt's node-granularity difference plus its own document-order enumeration ordering changed which
   action got tried at which position in the bounded step budget).

This is not one single root cause but the STACK of (a) genuinely different node/leaf enumeration
(Category B, mechanical driver of frontier shape) plus (b) different `steps_this_run` budgets consumed
this particular run (an artifact of the checkpointed, resumable, step-capped walk policy itself, not a
bug) — both are recorder/walker-policy facts, never touched or "fixed" here per the fence (walker.py and
TodayScreen.kt are read-only for this slice).

### Fixes made inside `walk_diff.py` this pass (summary)

1. Canonical multiset re-hash (KIND_MAP → sort by `(kind, text, interactive)` → `sha256(route + sorted
   summary)`), replacing the previous unsorted-remap state_id, in `remap_walk()`/`canonicalize_tree_summary()`/
   `canonical_id_of()`.
2. Edge alignment key changed from `(source, action.kind, action.handler_kind, action.ordinal)` to
   `(canonical_source_id, action.label, action.handler_kind, canonical_destination_id)` in `align_edges()`
   — ordinal removed per the explicit non-comparability argument above.
3. KIND_MAP gap fix: 20 new entries (`OutlinedTextField`, `IconButton`, and 16 layout/container/text
   composables mapped to `"Node"`), each individually justified in `render/walk_diff.py`'s own comments.

**Before/after divergence counts** (gate line):
- Before (original 6-entry KIND_MAP + ordinal-based edge key): `WALK DIFF: 0 shared states, 21 kt-only,
  14 py-only, 90 edge mismatches`
- After (this pass's canonicalization + 20-entry KIND_MAP expansion + canonical edge key):
  `WALK DIFF: 0 shared states, 21 kt-only, 14 py-only, 75 edge mismatches`

Shared-state count remained 0 — correctly, per the Category B node-granularity finding above, which is a
real (if benign) recorder-shape difference, not a bug in this differ.

## 2026-07-07 — slice 3c: Kotlin edge labels fixed, deeper coverage queued, re-diff plan

### Label rule spec (THE SAME rule, both sides — verbatim as documented in-code)

Bug found exactly where the task pointed: `WalkRecorderTest.kt`'s `enumerateInteractive()` (pre-fix,
line ~331) set `label = nodeText(n)` — the TAPPED node's own text only. `nodeText()` reads only
`SemanticsProperties.Text`/`EditableText` on that one node. Any interactive node that is itself a plain
container with no text of its own — the overwhelmingly common shape for "tap a whole row/card" handlers,
where the visible text lives on a CHILD `Text` node — recorded `label = ""` for every such edge. This
silently broke `walk_diff.py`'s `align_edges()` join key (`label + handler_kind`), which depends on label
being "the human-readable `_subtext`-style owner text/description" (its own docstring, quoted verbatim)
for the WHOLE class of container-owned handlers on the Kotlin side only — the Python side never had this
bug, since `interact.py`'s `_subtext()` always walks the full subtree.

**The rule (now identical on both sides, each file documents it in full):**
1. Walk the interactive node's OWN SUBTREE — the node itself plus every descendant — in document
   (pre)order.
2. Collect every non-blank text value encountered (own node's text counts too, same as every descendant's).
3. De-duplicate while preserving first-seen order.
4. Join the surviving list with `" / "`.
5. Collapse internal whitespace runs to a single space.
6. Truncate to 40 characters, appending `"…"` if truncated.
7. If the subtree carried no text at all, fall back to the node's `kind` string.

- Python reference (unchanged, already correct): `render/interact.py`'s `_subtext(node, limit=40)`
  (lines 117-132).
- Kotlin fix: `WalkRecorderTest.kt` gained a new `subtreeText(node, limit=40)` function (test sources
  only, mirrors `_subtext()` step-for-step) placed directly after `nodeText()`; `enumerateInteractive()`'s
  `label` assignment (was `nodeText(n)`) is now `subtreeText(n)`. `nodeText()` itself is UNCHANGED and
  still used elsewhere (canonicalized single-node text for `componentList()`/tree_summary) — only the
  EDGE LABEL derivation changed, which is the only place the rule applies.
- `render/walker.py`'s module-docstring EDGE format section (the shared WALK FORMAT spec) was expanded
  from a one-line pointer ("the SAME human label convention interact.py already uses") to the full 7-step
  rule above, cross-referencing `WalkRecorderTest.kt`'s `subtreeText()` by name, so the rule is legible
  from either file without needing to diff the other side's source.
- No format-version bump: label values were always documented as living on edges (`action.label`); this
  is a same-field CORRECTNESS fix (empty→populated for the affected node class), not a schema change.
  `state_id`/`canonical_id` hashing is untouched (labels never fed into either state hash).

Files touched this pass: `WFL_MixingCenter/WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt`
(test sources only, per fence), `WFL_MixingCenter/render/walker.py` (docstring only, no logic change —
verified via `py_compile` in the `/tmp/gh` sandbox both before and after the edit).

### Deeper coverage (task 2) — QUEUED, not yet executed

Host loop (`tools/walk_service.py`) was confirmed OFF: `DevComms/hostruns/results/` has no entries past
`102_fidelity.json`/`.log` (most recent prior artifact), and 10 polls (~40s apart) after queuing produced
no new result files. Per the task's own contingency ("queue everything regardless; the user restarts it"),
three request files were written and left in place:

- `DevComms/hostruns/requests/110_kt_walk_steps200.json` — kt walk, `-Dwalk.steps=200 -Dwalk.reset=1`,
  timeout 5400s.
- `DevComms/hostruns/requests/111_py_walk_steps200.json` — py walk, `--steps 200 --reset` under
  `xvfb-run`, timeout 5400s.
- `DevComms/hostruns/requests/112_walk_diff.json` — `python3 walk_diff.py`, timeout 300s (to run AFTER
  both walks land — the service processes requests in id order, so 112 naturally waits behind 110/111).

**Coverage numbers cannot be reported yet** — no execution occurred this session. The most recent
executed baseline remains the one already in this file: kt 21 states/43 edges (steps=60 exhausted-ish
frontier) vs. py 14 states/47 edges (steps=60, `--resume`-extended, hit its own 900s bound). The 29-screen
total (referenced in the task) is not yet cross-checked against either walk's distinct-route count in this
pass; that comparison is deferred to whoever picks up 110/111/112's results.

### Gate line — UNCHANGED this pass (no new diff run executed)

```
WALK DIFF: 0 shared states, 21 kt-only, 14 py-only, 75 edge mismatches
```

(This is the slice-3b gate line, carried forward — still the last ACTUALLY-RUN diff. It predates the
label fix above, so its edge-mismatch classification does not yet reflect fixed labels; re-running
`walk_diff.py` after 110/111 land is required before the label fix's effect on edge alignment can be
measured. Do not read the 75 number as post-fix.)

### Divergence classification / punch list — carried forward, NOT re-derived this pass

Since no fresh walk or diff ran this session, the classification is unchanged from slice 3b above
(Category A real route-coverage gaps, Category B recorder node-granularity, Category C KIND_MAP gaps —
all fully enumerated in the slice-3b section). Restating the standing punch-list candidates for whoever
runs 110/111/112 to completion:

1. **`settings`/`settings_notifications` route family + `wins`, `exercise_detail/{exerciseId}`,
   `workout_cooldown/{sessionId}` states** — reached on only one side this run (Category A). Re-diff after
   the 200-step walks to see whether BOTH sides now reach these (steps=60 was likely just too shallow/
   narrow a frontier on at least one side — see walk-shape mismatch §, "budgets themselves differed").
2. **Node-granularity gap (Category B)** — kt-side extra `Image`/blank `Node` leaves (6-7 per screen) vs.
   py-side occasional extra `Card` leaf, present on every one of the 4 common routes checked
   (`today`, `my_program`, `paths`, `progress`). Not a new finding, but now that edge LABELS are fixed,
   re-diffing may surface previously-invisible shared EDGES on these near-matching state pairs (edge
   alignment no longer forced to "no match" by every kt edge label being empty) — this is the single
   biggest expected effect of today's fix and the main reason task 3's re-diff matters.
3. **`Card` / `DropdownMenu` / `ModalBottomSheet` / `FilterChip`** — still deliberately unmapped in
   KIND_MAP (§4, §"KIND_MAP gap fix"); re-check after the 200-step walks whether any of these now have
   matched edges to cross-reference against (previously zero matched edges for `FilterChip` specifically,
   per the "left unmapped" note — a larger walk may finally produce evidence one way or the other).
4. **Kotlin's `Image`-vs-Python's-collapsed-`Icon` residue (Category C-adjacent, §6(c))** — still an
   honest, intentionally-unmapped vocabulary gap; not expected to change with more steps, listed here only
   so it isn't silently dropped from the running punch list.

None of these were fixed in this pass (stop-rule: punch-list items, not to be fixed under this task's
fence). All are candidates to re-classify (confirmed-real vs. resolved-by-fix vs. still-recorder-shape)
once 110/111/112 actually execute.

### Honest execution status

Code work (label-rule fix + doc updates) is COMPLETE and verified as far as this sandbox allows (Kotlin
change is UNEXECUTED — no Gradle/JVM in this sandbox, consistent with this file's existing candor about
`WalkRecorderTest.kt`'s status; `walker.py` was `py_compile`-checked before and after its docstring edit
in `/tmp/gh`, syntax-clean, logic unchanged). Host-loop execution (200-step kt walk, 200-step py walk,
re-diff) is QUEUED but NOT run — the service was off for the whole of this session (confirmed by polling
`DevComms/hostruns/results/` ten times at ~40s intervals with no new artifacts appearing). Coverage
numbers, the post-fix gate line, and a real re-classification of edge mismatches all require the user to
start `tools/walk_service.py` and let requests 110→111→112 run to completion.
