# Touch z-order fix — status, root cause, and outstanding verification

## Root cause

Kivy dispatches a touch parent-before-child. `_bind_click`'s original rule was plain "last claimant
wins" (whichever clickable's `on_touch_down` ran LAST, in tree/mount order, claimed the touch). That is
correct WITHIN one visual layer (it gives innermost-wins: a tapped inner Button correctly beats an
enclosing clickable Card). It is WRONG BETWEEN layers: a Scaffold's `content` slot and its
`bottomBar`/`topBar`/`floatingActionButton`/`snackbarHost` slots are SIBLING subtrees, and `_scaffold()`
mounts them in dict-bucket order, not real screen z-order. In actual Compose, bars and the FAB are drawn
ON TOP of the content and must hit-test first regardless of mount order — a long scrolled Card sitting
visually UNDER the bottom NavigationBar must never steal a tap that lands on the bar's screen region just
because its subtree happened to be walked later in mount order. Window-level popups (DropdownMenu /
ModalBottomSheet / AlertDialog, built by `_build_overlay`/`_Overlay`) are separate Kivy Windows layered on
top of everything and must always win over both content and bars.

## The fix — exact location

File: `WFL_MixingCenter/render/kivy_kit.py` (paths checked: both
`/home/lucas/Programming/WFL_MixingCenter/render/kivy_kit.py` and the transpiler-adjacent copy under
`WFL_PseudoCoup_Briefing/WFL_MixingCenter/render/kivy_kit.py` carry the same fixed code — confirmed
identical at the lines below).

- Lines 916–930: section marker `# ---- Z-ORDER LAYER (hit-test ranking ABOVE tree order) ----`,
  documents the bug and the fix rationale inline.
- Line 929: `_LAYER_CONTENT, _LAYER_BAR, _LAYER_OVERLAY = 0, 1, 2` — the three-tier layer scheme.
- Line 930: `_BAR_SLOTS = {"topBar", "bottomBar", "snackbarHost", "floatingActionButton"}`.
- Lines 933–954: `_click_layer(w)` — derives a clickable widget's layer from the `slot` prop
  `_scaffold()` already stamps on a Scaffold's direct children (bar slots → layer 1, everything else,
  including plain `content` slot children → layer 0), falling back to walking the widget's Kivy `parent`
  chain for a marked ancestor slot (so a `NavigationBarItem` nested inside `NavigationBar` inside the
  `bottomBar` slot correctly inherits layer 1 even though the slot prop only lives on the Scaffold's
  direct child). Any `_Overlay` instance (a Window popup panel) always returns `_LAYER_OVERLAY` (2),
  checked both for the widget itself and while walking its ancestor chain.
- Lines 957–971: `_click_down(w, touch)` — on touch-down, computes `layer = _click_layer(w)` and only
  overwrites `touch.ud['_click_target']` if `layer >= touch.ud.get('_click_layer')` (a lower layer never
  displaces a higher one's existing claim; ties keep the old last-claimant-wins/innermost-wins behaviour
  inside one layer). Still never consumes the DOWN event (`return False`) so children continue to see it.
- Lines 973–986: `_click_up(w, handler, touch)` — unchanged tap-vs-scroll logic (fires only if `w` is
  still the recorded claimant, finger stayed inside the widget, and total travel ≤ `_TAP_SLOP` = 12px).
- Lines 989–999: `_bind_click(w, node)` — unchanged wiring; the comment at (now) line 1003 in the
  Programming-mount copy notes claims are scoped "within its layer."

This matches, and supersedes, the earlier (already-shipped, already-verified) fix documented in
`touch_dispatch_navbar.md` (which introduced `_bind_click`/`_click_down`/`_click_up` themselves, gated
GREEN previously at interact 513/513, fidelity 377/377, and a REAL-TAP gate of 3/3 PASS). This later
z-order layer is an ADDITIVE refinement on top of that same mechanism — not a rewrite — dealing with the
cross-layer stacking gap the first pass didn't cover.

## What is verified, with real numbers

1. **Sandbox Kotlin test suite** — run directly by me in this pass:
   `cd /tmp/gh/Programming/PseudoCoup/tools/pseudokotlin && python3 run_kotlin_tests.py`
   → **`RESULT: 160/160 pass`** (verbatim, all 6 suites: ReadinessProgressionGateTest 9/9,
   RestartEngineTest 17/17, SubstitutionEngineTest 5/5, WarmupEngineTest 12/12, PathDefinitionTest 5/5,
   SampleProgramDataTest 4/4). This suite doesn't touch `kivy_kit.py` at all (it's pure Kotlin domain
   logic), so it was never at risk from this change, but it's a real, fresh, verbatim-confirmed number
   from this session.

2. **`interact.py`** (host run `090_interact`, already completed and on disk before this session —
   re-inspected, not re-run, since the host loop was not consuming): verbatim tail —
   `INTERACT: 1410 fired, 1410 ok, 0 failures across 27 screens + shell(6 handlers)`.
   Matches the expected 1410/1410 exactly.

3. **`fidelity.py`** (host run `092_fidelity`, already completed and on disk before this session —
   re-inspected, not re-run): verbatim tail —
   `FIDELITY ALL: 423/423 components within tolerance (28 screens)`.
   Matches the expected 423/423 exactly. (Full per-screen breakdown also on disk in
   `hostruns/results/092_fidelity.log` and cross-confirmed in `fidelity_423_closeout.md`.)

4. **Code re-inspection this session** (fresh read, not reused from memory): the layer-ranking logic in
   `_click_layer`/`_click_down` is internally consistent — no off-by-one in the tier constants, the
   "lower layer never displaces higher" guard reads correctly (`if prev is not None and layer < prev:
   return False`), the ancestor-walk correctly checks `_Overlay` both as `w` itself and while climbing
   `w.parent`, and `_click_up`'s unchanged tap/slop logic composes correctly with the new gating in
   `_click_down` (down decides the claimant via layer+innermost, up only checks "am I still that
   claimant" — no interaction bug spotted). No regression risk identified against `_leaf_button`'s
   SegmentedButton fix or `_leaf_label`'s size-banded `_SHAPER_CAL`, since neither touches the click/
   layer code path.

## What remains UNVERIFIED against the host loop

**`realtap_gate.py` — the actual real-touch (synthetic SDL touch-down/up dispatch) gate for this fix —
has NOT been confirmed GREEN in this session, and the two most recent completed attempts on disk both
FAILED, not passed:**

- Host run `091_realtap` (`hostruns/results/091_realtap.log`): fails partway through the 22-step
  scenario with
  ```
  after tap Program -> route: path_detail/path_self_directed
  AssertionError: Neither 'View other programs' nor 'Browse programs' button found
  ```
  at `realtap_gate.py:411`, in step `_s_programs_browse`. The script expected route `my_program` after
  tapping the "Program" nav item (post self-directed-path enrollment), but the app's real route lands on
  `path_detail/path_self_directed` instead — so `MyProgramScreen`'s expected button never renders, and
  the assertion fires before the z-order-specific steps later in the script are ever reached.
- Host run `093_realtap_settle` (`hostruns/results/093_realtap_settle.log`): identical failure, same
  route mismatch, same assertion, at `realtap_gate.py:444` (line shifted slightly, script was edited
  between runs, but the failure is the same one).

This failure is a NAVIGATION/ROUTING mismatch (wrong route reached after tapping "Program"), not
obviously the z-order fix itself — but it happens BEFORE the gate reaches any of the cross-layer tap
assertions (bar-vs-content, overlay-vs-bar) that this fix is actually meant to prove, so **the z-order
fix has no real-touch confirmation on record, positive or negative, in this session or the prior two
attempts.** Whether this routing mismatch is a pre-existing gap in the test scenario's setup, a
regression from an unrelated recent change, or something the z-order fix itself perturbed is UNKNOWN and
was not diagnosed further this session (out of scope without host access to run/inspect the live app).

- Queued host requests **`095_realtap`** (submitted 2026-07-07 02:19) and **`097_realtap`** (submitted
  2026-07-07 02:24), both `xvfb-run -a python3 realtap_gate.py`, are still sitting unconsumed in
  `DevComms/hostruns/requests/` as of this writeup (checked repeatedly between 02:36 and 02:38 EDT — no
  matching files ever appeared in `hostruns/results/`, and the last result of ANY kind the loop produced
  was `093_realtap_settle.log` at 02:10, over 25 minutes before this check). **The host runner loop was
  not consuming requests during this session.** A human should check
  `DevComms/hostruns/results/095_realtap.log` and `DevComms/hostruns/results/097_realtap.log` once the
  loop resumes — those are the two pending attempts that would give a REAL, fresh readout on this exact
  fix (whichever comes back, GREEN or another failure trace, is the next real data point).

- **2026-07-07, ~02:42–02:44 EDT: follow-up liveness re-check.** Re-scanned
  `DevComms/hostruns/results/` — still no `095_realtap.*` or `097_realtap.*` result files, and no new
  results of any kind beyond `093_realtap_settle.log` (02:10). Queued one fresh, minimal probe request to
  distinguish "loop is dead" from "loop is just busy on the two queued realtap runs":
  `DevComms/hostruns/requests/098_ping.json` =
  `{"id":"098_ping","cwd":"~/Programming/WFL_MixingCenter/render","cmd":["echo","ping"],"timeout":30}`.
  Polled `hostruns/results/` for a `098_ping.*` file across 4 rounds spanning ~02:42:11 to 02:44:31 EDT
  (roughly 2 minutes total, ~28–40s spacing) — **no `098_ping.json`/`.log` ever appeared.** A trivial
  `echo` with a 30s timeout should return almost instantly if anything were consuming the queue at all,
  so this rules out "just busy" as the explanation — **the host runner loop is confirmed still down /
  not polling this session.** Per the verification plan, stopped here rather than queuing
  `realtap_gate.py`, `interact.py`, or `fidelity.py` again, since doing so would only add more unconsumed
  files with no new information.

  **Status as of this update: `realtap_gate.py`, `interact.py`, and `fidelity.py` remain UNVERIFIED
  against the current z-order diff.** The only real, fresh, verbatim result obtained this session is
  sandbox Kotlin 160/160 (which doesn't touch `kivy_kit.py`); the cited interact 1410/1410 and fidelity
  423/423 numbers are still the OLD pre-fix runs (090, 092), not re-confirmed post-fix. Outstanding
  host-side request ids, all unconsumed as of this writeup: `095_realtap`, `097_realtap`, `098_ping`.
  Next session should check `hostruns/results/098_ping.log` first — if present and it echoes "ping", the
  loop has resumed and `095_realtap`/`097_realtap` results should be checked next (and a fresh
  `interact.py`/`fidelity.py` run queued for full re-confirmation); if `098_ping` is still absent, the
  loop needs human/operator intervention before any further verification of this fix is possible.

## Bottom line

- GREEN with real numbers: sandbox Kotlin tests 160/160 (run fresh this session); interact.py 1410/1410
  and fidelity.py 423/423 (both re-inspected from completed host runs 090/092, already on disk).
- NOT GREEN / UNVERIFIED: `realtap_gate.py` — the two most recent completed runs (091, 093) both FAILED
  on a routing mismatch before reaching the z-order-specific assertions; two newer queued attempts (095,
  097) are unconsumed because the host loop was not picking up jobs during this session. Do not read
  "interact 1410/1410 + fidelity 423/423" as proof the z-order fix itself is correct under real touch
  dispatch — those two gates don't exercise real SDL touch coordinates/layer stacking the way
  `realtap_gate.py` does; only the realtap gate does, and it has not produced a passing run since this
  fix was made.
