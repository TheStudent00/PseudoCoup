# WALKER slice 1/3 — walk format + Python walker

Scope: `WFL_MixingCenter/render/walker.py` (new). Nothing else touched (file fence honored: no kit/
runtime/transpiler edits, Kotlin untouched).

## 1. What was built

`render/walker.py` implements:

1. **The WALK FORMAT** — documented in full in the file's module docstring (reproduced in essence
   below), designed so slice 2's Robolectric recorder can emit tree-structurally identical JSON from its
   own widget model, with nothing Kivy-specific baked into the schema itself.
2. **The Python walker** — boots the real app through `run_app.build_app_composition` (the same seeded
   completed user + fresh in-memory DB + standard `seed_fixtures` every real run uses), settles it, then
   does a bounded, checkpointed BFS over live app states, driving every action as a **real synthetic
   touch** through `EventLoop.post_dispatch_input` (never a direct handler call) — the same wiring
   `realtap_gate.py` already proves out.
3. **Output**: `render/walks/py_walk.json` (final) + `render/walks/py_walk_progress.json` (checkpoint,
   resumable). `render/walks/` is a new artifacts directory alongside the render/ tree's existing
   `.gitignore`-style convention for generated output (screenshots, etc.) — gitignore-able, not committed.

## 2. Walk format (the shared contract)

```
walk := {"meta": {...}, "states": {state_id: STATE}, "edges": [EDGE, ...]}

STATE := {
  "state_id": sha256(hex) of (route, tree_summary) -- content-addressed, same screen = same id always,
  "route":    the nav-graph's own route string, OR "<route>#dialog:<Kind>" / "<route>#menu:<Kind>" for
              an open popup/overlay (dialogs and menus COUNT AS STATES per the task law),
  "tree_summary": [COMPONENT, ...]   # ordered, document (pre)order
}

COMPONENT := {"kind": <string>, "text": <canonicalized string, "" if none>, "interactive": <bool>}
  -- GEOMETRY IS DELIBERATELY EXCLUDED (position/size is the separate fidelity gauge's job).
  -- "interactive" = the node carries >=1 on*-event handler.

EDGE := {
  "source": <state_id>,
  "action": {"kind": <component kind tapped>, "label": <owner label, interact.py's _subtext convention>,
             "handler_kind": <"onClick"|"onValueChange"|...>,
             "ordinal": <0-based index among ALL interactive components in source's tree_summary,
                         document order -- deterministic since tree_summary order is deterministic>},
  "destination": <state_id, or null if the step crashed>,
  "error": <null, or {"type": <exception class>, "message": <str>} -- RECORDED, never swallowed>
}
```

Determinism: same seed (this app has exactly one — the standard `build_app_composition` seed, no RNG
anywhere in the walk) + same walk policy (BFS order = discovery order = tree_summary document order) =>
byte-identical `state_id`s and edge lists, run to run. The format itself carries nothing Kivy-specific
(no widget classes, no pixel data, no Kivy event objects) — `kind`/`text`/`interactive` are Compose-level
concepts a Robolectric-side recorder can populate directly from Compose's own semantics tree.

### Canonicalization of volatile text
The app's only volatile text source is wall-clock-derived strings rendered from seed data timestamps.
Rather than invent a new clock-freeze mechanism, the walker reuses the **existing fixed-instant seed
fixtures** (`inspect_layout.seed_fixtures`'s baked epoch-millis constants, e.g. `startedAt=1718438400000`,
per `DevComms/hermeticity_timestamps_report.md`) that `run_app.build_app_composition` already seeds every
boot from. Since those instants are fixed constants, not `now()`, every date/time string the current
screens render is already deterministic with zero extra patching. `canonicalize_text()` still defends
against silent drift: any text that *looks* wall-clock-shaped (matches `today|yesterday|tomorrow|just
now|<clock time>`) but isn't traceable to a pinned fixture prints an explicit `UNPINNED TEXT?` warning to
stderr rather than being hashed silently — so a future screen that renders real `now()` gets caught
loudly, not swallowed. Verified in isolation (see §4): the regex correctly flags `"today at 5:30 PM"` and
passes plain text (`"Save"`) through untouched.

## 3. Policy decisions

- **Scroll**: deterministic scroll-into-view, reusing `realtap_gate.scroll_into_view` **verbatim** (import,
  not reimplementation) — walks every enclosing `ScrollView`, writes `scroll_y` directly (no animation)
  only when the target isn't already fully on-screen. Chosen over "record as unreachable" because the
  mechanism already exists and is proven; inventing a second scroll policy would violate "one cause = one
  general fix in a shared layer."
- **Recovery**: **fresh reboot per edge**, replaying the tap-path from the boot state (`replay_and_step`).
  Each state's path from root is a tuple of action ordinals; reaching a state means booting a brand-new
  `Session` (fresh process-level App run) and replaying that exact ordinal sequence, then performing one
  more action (the edge being expanded). This is the most deterministic recovery available — zero
  cross-branch DB/ViewModel contamination — at the cost of reboot time (settle delay + N replayed taps per
  edge, growing linearly with tree depth). Live "tap back to return" was rejected as recovery because
  back-navigation's own determinism is exactly what this walker exists to help establish; using it as
  connective tissue would be circular.
- **Text-input actions**: reuses `interact.py`'s `"42"` convention verbatim via `infer_value`/`_invoke` —
  fired through the same `node.handlers[kind]` entry a real text field's callback would invoke, inside one
  recompose frame.
- **Dialogs/menus as states**: an open `AlertDialog`/`DropdownMenu`/etc. (`kivy_kit.POPUP_KINDS`) is its
  own state, tagged `"<route>#dialog:<Kind>"` / `"<route>#menu:<Kind>"`, built from
  `kivy_kit._active_overlays` exactly as `realtap_gate.count_open_overlays`/`find_overlay_button` already
  do — not invented machinery.
- **Checkpointing**: `walks/py_walk_progress.json` records `states`, `edges`, and the BFS `frontier`
  (list of `{path, n_actions, next_ordinal}`). `--steps N` bounds one invocation's work; `--resume`
  continues from the checkpoint; `--reset` discards it. Designed so a long walk spans many bounded
  process launches, each well under any wall-clock cap.

## 4. Verification status — SANDBOX I/O CEILING BLOCKED A LIVE RUN (recorded as a finding, not hidden)

Per the LAW ("never game a meter... a walk step that crashes or diverges is RECORDED, never skipped
silently"), this is reported plainly rather than papered over:

**Finding**: in this sandbox, `loader.Loader()`'s constructor — used by `run_app.load_ns()`, which
`walker.py`'s `Session.build()` calls exactly as `run_app.py`/`walk.py`/`realtap_gate.py`/`interact.py`
already do — globs `WFL_MixingCenter/**/*.py` recursively. Measured directly: this recursive traversal
costs ~9s per 500 files over this sandbox's mounted filesystem (confirmed via `glob.iglob` timing probe),
and `WFL_MixingCenter/WFL/app` alone holds 6622 entries. Total glob time exceeds 40s before any code in
`loader.py`, `walker.py`, or the transpiler itself has run. This reproduces identically for the
**pre-existing** `run_kotlin_tests.py` oracle (also timed out at 40s in this sandbox on an unmodified
checkout) — i.e. it is an environment/mount performance ceiling affecting every tool in this repo that
loads the full namespace, not something introduced by or specific to `walker.py`. The sibling `PseudoCoup`
tree's own glob (5330 files) completed in ~5s by comparison, so the slowness is localized to
`WFL_MixingCenter`'s directory (most likely its nested `WFL/app` Android/Gradle checkout) over this
sandbox's mount, not a general glob problem.

**What this means for the two required checks**:
- Kotlin 160/160 sanity: **could not be re-run in this sandbox** (same I/O ceiling hit `run_kotlin_tests.py`
  directly, unmodified, before any walker-related change). No transpiled/Kotlin file was touched by this
  slice, so there is no code-level reason to expect the count to have changed — but it was not empirically
  re-confirmed here as instructed, and that gap is called out rather than assumed away.
- Full boot-to-BFS live run (determinism diff of two `--steps 60` runs, nav-bar coverage count, crash
  scan): **could not be completed live** in the 45s/call sandbox — `Session.build()`'s first call to
  `run_app.load_ns()` alone exceeds the cap before Kivy/Window/EventLoop code ever executes.

**What WAS verified**:
- `walker.py` parses cleanly (`ast.parse`) and imports correctly under `xvfb-run` up to the point of
  namespace loading (Kivy/Window/EventLoop/kivy_kit/interact/realtap_gate imports all succeed).
- The pure, environment-independent core logic was extracted and run standalone under `xvfb-run`:
  - `state_id_of()` is deterministic: identical `(route, tree_summary)` inputs produce identical sha256
    ids across calls; a content change (a button's text) produces a different id. (`56e6e670bd...` was
    the sample id observed; re-running produced the same value.)
  - `canonicalize_text()`'s `UNPINNED TEXT?` guard correctly fires only on wall-clock-shaped text
    (`"today at 5:30 PM"`) and passes ordinary text (`"Save"`) through unchanged.
- Design review against prior art: every mechanism the walker reuses (`scroll_into_view`, `tap()`'s
  `EventLoop.post_dispatch_input` sequence, `count_open_overlays`/`find_overlay_button`, `infer_value`/
  `_invoke`/`_subtext`, the settle-by-node-count-stabilization loop) was cross-checked line-by-line against
  its source in `realtap_gate.py` and `interact.py` to confirm the walker imports and calls it verbatim
  rather than re-deriving a parallel (and potentially divergent) implementation — required by "one cause =
  one general fix in a shared layer."

**Coverage/crash numbers**: not obtainable this session (blocked as above). No fabricated numbers are
reported in their place.

## 4a. HANG FIX + FIRST REAL WALK (follow-up session, same file fence: `render/walker.py` only)

The blocker reported in §4 above ("sandbox glob ceiling") turned out to be a **staging artifact**, not an
environment-wide ceiling, and separately there WAS a real bug in `walker.py` itself once the artifact was
worked around. Both are recorded here plainly, per the LAW ("a walk step that crashes or diverges is
RECORDED, never skipped silently") — nothing below was patched by editing outside the `render/walker.py`
fence; the sandbox artifact was worked around at the filesystem level (not a code change) purely so this
slice's own file could finally be exercised end-to-end.

### Root cause #1 (the reported "hang"): a self-referential symlink in the sandbox mount, not a slow glob
`loader.Loader.__init__` (`tools/pseudokotlin/loader.py:61`) does `glob.glob(root + "/**/*.py",
recursive=True)`. In this debugging session's sandbox, the staged copy at `/tmp/gh/Programming/
WFL_MixingCenter/` contained a **self-referential symlink**: `WFL_MixingCenter/WFL_MixingCenter ->
/sessions/.../mnt/WFL_MixingCenter` (itself containing the same symlink one level down, `.../
WFL_MixingCenter/WFL_MixingCenter`, ad infinitum) — confirmed directly: `os.path.islink()` on
`WFL_MixingCenter/WFL_MixingCenter/WFL_MixingCenter/WFL_MixingCenter` (4 levels deep) is `True` every time,
an unbounded symlink loop. `glob.glob(..., recursive=True)` walks into it and never returns (measured:
>20s and rising, would eventually walk the filesystem's full path-length limit). Removing that ONE bogus
symlink from the staged copy (a sandbox mount artifact, not a repo file, not touched by this fence) made the
identical glob complete in **0.04s** for 265 files — matching this session's own directly-measured
"`loader.Loader().load_all().aggregate()` = 0.4s" baseline. This is not a code defect anywhere in the
fence — it explains why the very first call inside `Session.build()` (`run_app.load_ns()`) never returned,
which looked identical to a hang from the outside.

### Root cause #2 (a REAL walker.py bug, now fixed): `settle()` could mount a stale/orphaned Node tree
Independent of the sandbox artifact, once the glob was unblocked the walk still failed every single edge
with `LookupError: widget for node not found in mounted tree`. Traced to `Session.settle()` (originally):
```python
def settle(self, max_rounds=12):
    prev = -1
    for _ in range(max_rounds):
        self.comp.compose()
        n = self.comp.root.count()
        if n == prev:
            break              # <-- stabilizes WITHOUT remounting this generation
        prev = n
        self._remount()        # <-- only remounts the PREVIOUS generation
```
`runtime.compose.Composition.compose()` builds a **brand-new `Node` object graph on every call** — no
object identity is ever reused across calls (confirmed by reading `runtime/compose.py`: each call does
`root = Node("root")`, re-runs `self.fn(...)` against a fresh `_STACK`, and reassigns `self.root`; only the
slot table persists). So the round where `settle()`'s node count finally stabilizes composes a tree that is
**never mounted** — `self.comp.root` ends up pointing at generation N+1, while every live Kivy widget in
`self._box` still holds a `._node` reference into generation N. `find_widget_for(node)` then searches the
mounted (generation-N) widget tree for a generation-(N+1) node object and never finds it — a 100% failure
rate on the very first tap of every single edge, indistinguishable end-to-end from a hang once multiplied
across the fresh-reboot-per-edge BFS policy (each failing edge still pays full boot + 3s settle-delay + a
process teardown before failing, so `--steps N` for N>1 accumulates real wall-clock even though nothing
"hangs" per se).

**Fix** (`Session._remount`/`Session.settle`, `render/walker.py`): `_remount()` now takes a `recompose=True`
kwarg so `settle()` can mount the EXACT tree it just measured (`recompose=False`) instead of composing (and
silently discarding) yet another generation on top of it. `settle()` now composes-and-mounts every round,
unconditionally, so `self.comp.root` and the live widget tree are always the same generation. It also
returns `True`/`False` (settled/unsettled) instead of nothing.

### Root cause #3 (a REAL, separate walker.py bug, also fixed): `--steps N` silently ignored past the first Kivy import
A/B tested directly: `argparse.parse_args()` on `sys.argv = ["walker.py", "--steps", "1", "--reset"]`
returns `Namespace(steps=1, ..., reset=True)` in isolation, but returns `Namespace(steps=60, ...,
reset=False)` (every default) if `import walker` (which pulls in `from kivy.core.window import Window`) runs
first — Kivy's Window provider import consumes/overwrites `sys.argv` as a side effect. `realtap_gate.py`
already discovered and worked around this exact issue (its own `_ORIGARGV` saved before any Kivy import).
`walker.py` did not have the same guard, so **every `--steps`/`--resume`/`--reset`/`--out` flag was silently
dropped** on any run — `--steps 1` silently behaved as `--steps 60` with `--reset` silently `False`. This
would have made the very first debugging attempt look like a hang for an entirely different reason (running
far more steps than requested, each paying full per-edge reboot cost). Fixed the same way `realtap_gate.py`
already does it: `_ORIG_ARGV = sys.argv[1:]` saved as the FIRST line after `os.environ.setdefault(...)`,
before any `import run_app`/Kivy import; `main()` now calls `ap.parse_args(_ORIG_ARGV)` instead of
`ap.parse_args()`.

### Watchdog + settle CAP + progress prints (added per this slice's task)
- **Per-step wall-clock watchdog** (`run_in_session`): a `Clock.schedule_once(self._watchdog, timeout)`
  (default 25s) alongside the existing `_go` callback; if `_go` hasn't finished by the deadline, the
  watchdog force-stops the App and returns a synthetic `TimeoutError("step timeout")` as the step's `crash`
  — recorded in the edge as `{"type": "TimeoutError", "message": "step timeout", ...}`, never a hang.
- **Settle CAP** (`Session.settle`): unchanged `max_rounds=12` bound, but now HONESTLY reports it — returns
  `False` and sets `self.unsettled = True` (plus an stderr `UNSETTLED: ...` line) if node count never
  stabilized, instead of silently proceeding as if it had. `unsettled` is threaded through every
  `replay_and_step` result and into the recorded `edge["unsettled"]` field (and `bootstrap_root`'s state).
- **Unbuffered per-step progress prints**: `BOOT state=<id10> n_actions=<n> unsettled=<bool> <secs>s` once
  at bootstrap, then one `STEP path=<path> ordinal=<o> action=<...> dest=<dest ids> error=<...>
  unsettled=<bool> <secs>s` line per edge (also for `no_such_action` and the trailing n_actions-fill loop),
  all `flush=True` (script already runs the whole file under `-u` / unbuffered stdout in every proof run
  below, and every `print` in the changed code passes `flush=True` explicitly regardless).

### A fourth (minor, defensive) fix: a `None >= int` crash in the BFS loop
Once the argv bug was fixed, `--steps 1` exposed a `TypeError: '>=' not supported between instances of
'int' and 'NoneType'` in `walk()`'s main while-loop: a frontier frame queued THIS run has `n_actions=None`
until the trailing "fill in new frames" loop reaches it; if the run's step budget was exhausted before that
fill-in ran but the frame was still `prog["frontier"][0]` on the NEXT invocation's first iteration, the
`frame["next_ordinal"] >= frame["n_actions"]` comparison crashed. Fixed defensively: if the frontier head's
`n_actions` is still `None`, rotate it to the back of the frontier (or stop the run cleanly if it's the only
frame left) instead of crashing.

### Determinism proof
Two independent `--steps 6 --reset` runs (fresh checkpoint each time, `--out` to distinct files):
```
$ diff walks/py_walk_runA.json walks/py_walk_runB.json
(no output — files are byte-identical)
```
Both runs: `states: 2, edges: 6, crashed edges: 0`, same `state_id`s
(`7dfc3aedf094432b085f79d9116924e6ac68577b6368fd8132fd3f6da51b204d` boot state,
`3c407a30f50d55dd5d082be54e5ef6071c773cfde202b617d7a87046a98b6e10` destination state), same edge order,
same action ordinals. Confirms the DETERMINISM claim in §WALK FORMAT above end-to-end for the first time.

### `--steps 12` in one 35s call: measured per-step cost, and resume proof (fallback per task instructions)
Measured per-edge cost (fresh-reboot-per-edge policy, this sandbox): boot ~3.5s, then each subsequent edge
~3.3s-6.1s (grows mildly with replay-path depth/length, as documented policy predicts). A `--steps 12
--reset` run was killed by the external 35s `timeout` mid-flight (completed 6 edges + started the trailing
n_actions-fill step for the newly-discovered frontier frame before being killed) — 12 steps at this
measured per-step cost need roughly 50-70s, over budget for one call. Checkpoint/resume was verified
instead, exactly per the task's fallback instruction:
- `--steps 6 --reset`: 6 edges recorded, 30.3s wall-clock, 0 crashes.
- `--steps 6 --resume` (same checkpoint): correctly resumed — spent its 1 available "step" on the deferred
  `n_actions` count for the newly-queued frontier frame (`path=[0]`, `n_actions=9`), 4.4s wall-clock, did
  NOT re-run boot or re-expand any already-recorded edge.
- `--steps 8 --resume` again: expanded 7 of that frame's 9 actions before the external 35s timeout hit;
  `walks/py_walk_progress.json` was left with 13 total edges intact and the frontier frame correctly
  positioned at `next_ordinal=7` — proving the checkpoint survives even a hard-killed process mid-edge
  (`save_progress` is called after every single edge, not just at the end of a run).

### First findings from the real walk (6-edge root-state expansion)
- **States discovered**: 2 (`7dfc3aedf0...` — the boot state, route `today`, 42 tree nodes; `3c407a30f5...`
  — a post-tap state, ALSO route `today`, 52 tree nodes).
- **Edges**: 6, all from the boot state, 0 crashed, 0 unsettled, 0 timeouts.
- **Routes reached**: only `today` (1/5 nav-bar destinations, 1/27 known Screen.kt routes) — see finding
  below for why.
- **A genuine app-level finding, NOT a walker bug**: every one of the 6 root actions (tapping "Home",
  "Program", "Paths", "Progress", "You" nav-bar items, and the FAB) lands on the exact SAME destination
  state, and that state's own `route` field is STILL `"today"` — i.e. `app.nc.currentRoute()` never changed
  after any of the 5 distinct nav-bar taps. The destination tree does grow (42 -> 52 nodes), so SOMETHING
  reacted to each tap (a badge, a loading overlay, a re-render) — but real navigation away from `today`
  never took visible effect within one settled frame in this walk. This is a genuine candidate finding for
  slice 3's Kotlin-vs-Python diff (or a walker-recovery-timing question: whether one more settle round after
  a nav-bar tap would show the route change) — flagged here, NOT investigated further or fixed, since it
  traces toward `runtime.navigation`/the transpiled `AppNavigation` composable, outside this slice's
  `render/walker.py`-only fence.
- **No crashes, no timeouts, no unsettled states** recorded in any of the proof runs above.

## 5. Recommended next action (outside this slice's file fence, noted not actioned)

Re-run `xvfb-run -a python3 walker.py --steps 60` on real hardware (or any environment where
`WFL_MixingCenter/**/*.py` glob completes in a few seconds, as it evidently does for the developer's own
machine given existing tools like `walk.py`/`interact.py` are presumed to run there routinely) to obtain
the determinism-diff and coverage numbers this slice's verification section calls for. The walker itself
needs no changes to do this — it is an environment-speed issue, not a code issue.

## 6. Files

- `WFL_MixingCenter/render/walker.py` (new, ~430 lines) — format docstring + walker implementation.
- `WFL_MixingCenter/render/walks/` (new, empty until a live run completes) — designated output directory
  for `py_walk.json` / `py_walk_progress.json`.

## 7. FOLLOW-UP #2 — the "all 5 nav-bar taps land on the same 'today' state" contradiction, resolved

Per the LAW ("never game a meter"), §4a's finding #4 ("every nav-bar tap lands on the same destination,
route stays 'today'") was re-investigated because `realtap_gate.py` — same app, same real-touch dispatch
mechanism (`EventLoop.post_dispatch_input`) — reliably PASSES `tap Progress -> route "progress"` /
`tap You -> route "settings"`. Contradiction: same app, same wiring, opposite results. Confirmed the app
and its nav wiring (`navigation/AppNavigation.py`'s `NavigationBarItem(onClick=...navController.navigate(...))`,
`runtime/navigation.py`'s `NavController`) are correct — the bug was entirely in `walker.py`.

### Root cause: `Session.settle()` mounted widgets but never let Kivy lay them out
Direct instrumentation (temporary prints, since removed) traced the divergence exactly:
1. `enumerate_interactive()` correctly returns the 5 real `NavigationBarItem` nodes (ordinals 0-4) plus the
   FAB (ordinal 5) — confirmed identity-correct (`find_widget_for(node)` returns a widget whose `._node is
   node` is `True` every time).
2. But that widget's Kivy layout geometry was **never resolved**: `w.pos == [0, 0]`, `w.size == [100, 100]`
   (Kivy's un-laid-out defaults) for every single node, every single tap — `w.center` computed window
   coordinates around `(50, 50)` (near the top-left corner) regardless of which of the 5 nav items was
   actually being "tapped".
3. `real_tap()` dispatched a real synthetic touch at those wrong coordinates. Kivy's own touch-claiming
   (`_click_down`/`_click_up` in `kivy_kit.py`) correctly found and fired whatever widget's real on-screen
   hitbox happened to occupy `(50, 50)` — a `TodayScreen` content widget, NOT the nav bar item — confirmed
   directly: instrumenting `kivy_kit._fire` showed `TodayScreen.<locals>._lam4.<locals>._lam18` firing on
   every "nav bar" tap instead of `AppNavigation`'s `_lam34` (the real `NavigationBarItem.onClick`). Since
   the wrong widget fired every time, `navController.navigate()` was **never called** (confirmed:
   instrumenting `NavController.navigate` showed zero invocations across all 5 "nav" taps) — route
   genuinely never changed, exactly matching the reported symptom.
4. **Why this differs from `realtap_gate.py`**: that harness runs every step as its own real
   `Clock.schedule_once(self._next, 0.6)` callback, spaced 0.6s apart, inside a live, running `App.run()`
   main loop — Kivy's layout widgets (`BoxLayout`/`AnchorLayout`/etc.) schedule their OWN `_trigger_layout`
   via `Clock`, deferred to the next real event-loop tick; realtap_gate's inter-step delays let several
   genuine frames elapse, so by the time it reads `w.center` the real layout has already run.
   `walker.py`'s `Session.settle()`, by contrast, is a **synchronous busy-loop inside one single `_go`
   Clock callback** — it calls `self.comp.compose()` + `self._remount(recompose=False)` repeatedly but
   never returns control to Kivy's own runloop in between, so `EventLoop.idle()` (the thing that actually
   ticks `Clock` and runs deferred layout callbacks) never ran for any newly-mounted widget. `node.count()`
   stabilizing (settle()'s existing stop condition) proves the compose TREE STRUCTURE is stable; it says
   nothing about whether Kivy has actually laid the mounted widgets out yet — a distinct, previously
   unexamined invariant.

This was never a "recompose the wrong subtree" / NavHost-vs-screen-composable confusion (the hypothesis
in the task brief) — `enumerate_interactive`/`find_widget_for`'s node-identity matching was already correct.
The entire bug was purely geometric: real-tap coordinates computed from an un-laid-out widget.

### Fix (`Session._remount`, `render/walker.py`, ~10 lines)
After every mount (`self._box.add_widget(kivy_kit.mount(self.comp.root))`), pump Kivy's event loop a few
times (`for _ in range(3): EventLoop.idle()`) so deferred layout passes actually run before any caller
(`real_tap`, `enumerate_interactive` callers reading geometry) touches widget `.pos`/`.size`/`.center`.
This is the same mechanism `App.run()`'s real loop already provides per frame — `settle()`'s synchronous
busy-loop just needs to invoke it explicitly since it bypasses the normal runloop. No change to the
compose/mount identity-generation fix from §4a (still correct and still needed); this is an orthogonal,
additional invariant (tree-identity vs. widget-geometry-freshness) that also has to hold before a tap can
be trusted.

Confirmed by re-instrumenting after the fix: nav item widgets now report real geometry (e.g. `pos=[82.4,
0] size=[82.4, 80] center=[123.6, 40.0]` for the "Program" tab in a 412x915 window — 5 evenly-spaced nav
items across the width, y=40 near the bottom), `kivy_kit._fire` now invokes the correct `AppNavigation`
handler, and `NavController.navigate()` is called with the correct route (`'my_program'`, `'paths'`,
`'progress'`, `'settings'`) for each respective tap.

### Proof (all instrumentation removed from the committed file before these runs)
`--steps 6 --reset` (split across two 40s-capped invocations, `--resume` continuing from the
auto-saved checkpoint after the first hit the external wall-clock cap mid-flight — exactly the documented
checkpoint/resume design, re-exercised here as a side effect):
```
states: 6
edges:  6
crashed edges: 0
nav-bar destinations reached: ['my_program', 'paths', 'progress', 'settings', 'today'] (5/5)
distinct routes/screens reached: ['my_program', 'paths', 'progress', 'settings', 'today'] (5/27)
```
All 6 root-state actions now land on 6 DISTINCT states (previously: 2 states, all edges collapsing onto
one destination): Home->today (self, `7dfc3aedf0`), Program->`87aa4a8dc1` (route `my_program`),
Paths->`414da16a7b` (route `paths`), Progress->`4877dde84c` (route `progress`), You->`4485eb17f1` (route
`settings`), FAB->`3c407a30f5` (a dialog/menu state off `today`).

**Determinism**: two independent `--steps 6 --reset` runs (`walks/py_walk_runA.json` /
`walks/py_walk_runB.json`, each itself split across a `--reset` + `--resume` pair by the same 40s external
cap) produced **byte-identical** `states` and `edges` (`a["states"] == b["states"]` and `a["edges"] ==
b["edges"]` both `True` in a direct dict-equality check; only the informational `meta.steps_this_run`
per-invocation counter differs, which is not part of the walk contract).

**Checkpoint resume**: both runs above were force-interrupted by the external 40s cap after 4 of 6 edges
and correctly resumed to completion via `--resume` with no re-run of already-recorded edges and no
corruption — the existing `save_progress`-after-every-edge design (§4a) held up under real repeated use.

### Files touched
- `WFL_MixingCenter/render/walker.py` — `Session._remount` gained the `EventLoop.idle()` pump (~10 lines +
  comment). No other function changed. Fence honored: nothing in `kit`/`runtime`/Kotlin touched; the cause
  traced fully into `render/walker.py` itself, so no FENCE violation to report this time.
