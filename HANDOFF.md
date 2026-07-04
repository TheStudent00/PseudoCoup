# Session handoff — 2026-07-04 (written by the outgoing Claude session for its successor)

You are continuing an ongoing autonomous engineering loop. Read this file, then
`PROGRESS_ondeck.md`, then proceed with the top on-deck item. The user says "proceed" and steps
away; work rounds end with a report, dashboard update (`PROGRESS_ondeck.md` edit + `python3
tools/pseudokotlin/track.py`), and a commit-push of BOTH repos (PseudoCoup on main,
WFL_MixingCenter on master). Memory files in the auto-memory directory carry the standing rules
(general-solve-first, communication protocol, render-count honesty, Kotlin adjustability); they
load automatically.

## The task

Complete the KtToPy transpiler (`tools/pseudokotlin/`) so the WFL Kotlin app runs in Python/Kivy
(`~/Programming/WFL_MixingCenter/`). The continue/shutdown criterion is the LAYOUT-FIDELITY
instrument: real Compose (Robolectric) vs the kivy kit, both dump component boxes, compared as
%-of-display at ±3% (`tools/pseudokotlin/fidelity.py` runs everything; per-screen diffs land in
`layout_inspect/*.diff.txt`).

Hard rules: zero hand-edits to transpiled WFL-Python (regenerate via
`tools/pseudokotlin/build_mixingcenter.py`); fixes go in shared layers (kivy_kit / compose runtime
/ loader / differ / transpiler); one cause = one general fix; never game the meter. Kotlin inside
WFL_MixingCenter/WFL may be adjusted only if appearance/function is unchanged. Font/shaper bridges
are the one sanctioned non-general area, and every text/list metric must be derived from the
specimen tests (dumpSpecimen / dumpSpecimenList in LayoutDumpTest.kt + their python halves in
render/inspect_layout.py), never from mixed app screens.

## State at handoff

- Dashboard: 254/344 components within tolerance across all 28 measurable screens (DebugPanel is
  dev-only, excluded). The original 20 screens are all at 100% (231/231) — do not regress them.
- The 8 newly measured screens seed program/session fixtures through the app's OWN repositories
  (SampleProgramRepository.seedIfNeeded + WorkoutExecutionRepository.startSessionFromProgramDay
  on BOTH engines — Kotlin side in the generated LayoutDumpAllTest assembler(seed=...), python
  side in inspect_layout.seed_fixtures). Deterministic ids: program `prog_gup_3d_beg`, day
  `day_gup_3d_beg_w1_d1`; sessionIds are per-engine (only rendered text must match).
- This round landed 6 general runtime/transpiler fixes (ktext extension dispatch + build pre-pass
  registry, Java printf ',' grouping, Room enum query params, Room aliased-star JOIN reads,
  combine(collection) overload, debounce/firstNotNullOfOrNull, IntrinsicSize non-numeric wrapper).
  All committed and pushed.

## Where I stopped mid-diagnosis (top on-deck item, freshest context)

ProgramEditorScreen is 0/34: the kivy JSON dump reports the whole Scaffold subtree as a 100x100
box at the bottom-left (Kivy never-laid-out defaults), yet a direct probe —
`kivy_kit.mount(build("ProgramEditorScreen").root)` — shows a CORRECT FloatLayout(size_hint=(1,1))
scaffold with proper slots. So the screen lays out fine; the DUMP pairs nodes to a wrong/unmounted
widget on this screen only.

Facts established (do not re-derive):
- The recorded node tree is correct: CompositionLocalProvider → Scaffold → {topBar, content} slots.
- `collect_widgets` (inspect_layout.py ~line 286) maps id(node)→widget by walking the MOUNTED tree
  reading the `_node` tag the kit stamps — so only mounted widgets can be in the registry.
- Yet the dumped scaffold geometry (100x100 at y=815 top-frame = bottom-left, w=100 defaults all
  the way down: Column w=100, Item w=68) is exactly an unmounted orphan's geometry.
- Two candidate mechanisms I had NOT yet distinguished:
  (a) `_scaffold()` in kivy_kit returns early — check whether the `w._node = node` stamping happens
      AFTER the early returns in `to_widget` (Scaffold/button/atom branches) or is skipped, and
      which widget instance ends up tagged with the Scaffold node on THIS screen vs a passing one
      (GymListScreen dumps Scaffold 411x915 correctly — diff what differs).
  (b) Something builds a SECOND widget tree whose widgets re-tag or shadow nodes (emit()'s
      render_node does NOT build widgets — checked — but check `live()`/`_ctx` and whether
      `Inspector.build()` mounts once; also whether a popup/dialog child (AlertDialog/Dialog in
      ProgramEditorScreen) causes a to_widget call on an already-realized subtree).
- Next probe I was about to run: replicate Inspector._go in a script — mount, settle a Clock
  frame, then print `reg[id(scaffold_node)]`, its `.parent` chain, `.size_hint`, `.pos`, and
  compare with the same probe on GymListScreen.

## Rest of the on-deck queue (also in PROGRESS_ondeck.md)

- WorkoutCooldownScreen 11/25, WorkoutExecutionScreen 1/2, ExercisePickerScreen 6/46,
  ProgramDayEditorScreen 0/1 — undiagnosed; diff files are in layout_inspect/.
- SessionDetailScreen 0/0 — neither engine pairs anything; check the completed-session fixture
  renders and whether the test needs a waitFor anchor.
- RAM: the user's machine crashed under the suite. Consider `--max-workers=1` +
  `org.gradle.jvmargs=-Xmx2g` for the gradle half of fidelity.py before running it again.

## Command crib

- Full gauge: `cd tools/pseudokotlin && python3 fidelity.py`
- Regenerate WFL-Python after transpiler/runtime edits: `python3 tools/pseudokotlin/build_mixingcenter.py`
- Regenerate the auto layout tests after generator edits: `python3 tools/pseudokotlin/gen_layout_dumps.py`
- One screen's kivy dump: `cd ~/Programming/WFL_MixingCenter/render && python3 inspect_layout.py <ScreenName>`
- One screen's compose dump: `cd ~/Programming/WFL_MixingCenter/WFL && ./gradlew -p app testDebugUnitTest --tests '*LayoutDump*.dump<ScreenName>'`
- Dashboard: edit PROGRESS_ondeck.md, then `python3 tools/pseudokotlin/track.py` (never hand-edit PROGRESS.md/html)
