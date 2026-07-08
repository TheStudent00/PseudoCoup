# Session handoff — 2026-07-08 update (discipline slice + walker hermeticity; details in PROGRESS_ondeck.md)

REPO RENAMED: PseudoCoup -> PseudoCoup_v0 (user freed the name for a new public repo). All hardcoded
~/Programming/PseudoCoup path constants updated (render/ tooling, vendor scripts, walk_service usage
line). If the GitHub repo is also renamed: `git remote set-url origin .../PseudoCoup_v0.git`.

MAIN-SOURCE DISCIPLINE SLICE (DevComms/main_source_discipline.md; user-approved Tiers 1+2+3, all
landed + verified): T1a merged semantics on 26 container clickables (walker labels carry child text
natively); T1b AppTopBar day-name + TodayScreen week read TimeProvider (closes the AppNavigation.kt:994
open decision); T2 explicit locales (String.format weight, wins formatter/sort); T3 transpiler emits
raise (not None) for the synthetic exhaustive-when else, gated to value-consumed whens only. Runtime
grew Locale.US/ENGLISH as a real class + ktformat skips a leading Locale arg. Gates after: kotlin
green, fidelity 423/423, interact 1410/1410 + shell 6.

WALKER HERMETICITY (the big correction): di._DB was process-global while Session.build re-ran
load_ns() per episode -> later episodes read rows hydrated through the PREVIOUS namespace's enum
classes (identity mismatch -> synthetic when-else None). The "first real app bugs" note is REVISED:
Resume/WorkoutExecutionViewModel float*NoneType and the phantom "Workout in progress" states were
walker leakage, NOT app bugs (ModalBottomSheet dismiss LookupError remains open/real). Fix:
di.reset() per Session boot, closes old sqlite conn (a 100-episode walk otherwise OOMs — hostrun 119
died SIGKILL at 99/100). Crash tracebacks now print to walk logs (di.py + walker.py, log-only).
Second clock gap found+fixed: WalkRecorderTest bypasses Hilt, so FixedTimeModule never reached
Assembler-built ViewModels — Assembler gained an optional TimeProvider override (default unchanged).

WALK DIFF (hostrun 142, both walks clock-pinned, hermetic): 4 shared / 17 kt-only / 19 py-only /
122 edge mismatches (was 4/17/29/170). Bucket teardown (agent, 2026-07-08): unmapped overlay/container
kinds (py records DropdownMenu/ModalBottomSheet/Card; kt semantics tree has no such kinds) = 17/36
unshared states + 72/122 edge mismatches — DOMINANT remaining lever, currently deliberate KIND_MAP
policy, needs a user design decision; BFS reachability = 13 states + 21 edges; "42" vs "42.0" display
drift = downstream formatting, differ-canonicalization decision pending; kt 'Button' vs py
'FloatingActionButton' labels = 14 edges.

# Session handoff — 2026-07-07 update (walker era; read PROGRESS_ondeck.md top entries for full detail)

CURRENT STATE: acceptance-drive bugs fixed (Room invalidation, live flow operators, fail-loud DI, M3
Defaults colors, density scaling via WFL_SCALE). The DECISION-TREE WALKER is live: render/walker.py
(Python side, real taps), WalkRecorderTest.kt (Kotlin side, Robolectric + Hilt, FixedTimeModule clock
pin), render/walk_diff.py (differ, format v2 = meaning-bearing nodes only, KIND collapse table).
It already found+we fixed: Modifier.clickable never promoted to handlers (whole class touch-dead),
touch z-order (bars must outrank content; Kivy Window is its own parent — cycle guard load-bearing).
GATES (all green, re-baselined): fidelity 423/423 (28 screens), interact 1410/1410 + shell 6,
realtap GREEN (5 case groups), kotlin tests 160/160, datalayer ALL GREEN.
WALK DIFF: 4 shared / 17 kt-only / 3 py-only / 37 edge mismatches — next work: kt empty edge labels
(unmerged semantics), deeper py coverage, extra seeded walk roots (Onboarding etc.), emulator walk
(dry-built, unexecuted: render/emu_walker.py + CommandReceiver.kt ported, debug-only manifest).
HOST LOOP: user runs `python3 tools/walk_service.py` on their machine; I write request JSONs to
DevComms/hostruns/requests/, read results/ — this is how ALL gradle/xvfb verification runs. The
Cowork sandbox caps every bash call at 45s; staging copy at /tmp/gh/Programming (beware rsyncing
the repos' self-symlinks into it — they hang recursive globs and parent walks).

# Original handoff — 2026-07-05 (for continuation in Claude Desktop Cowork)

You are continuing an ongoing engineering loop with Lucas. Read this file, then `PROGRESS_ondeck.md`
(top = newest state), then the memory files (they load automatically and carry the standing rules).
Work rounds end with: report → dashboard update (`PROGRESS_ondeck.md` edit + `python3
tools/pseudokotlin/track.py`) → commit-push of BOTH repos (PseudoCoup on main, WFL_MixingCenter on
master). Reports from delegated agents live in `DevComms/*.md` — that directory is the project's
paper trail; read the recent ones before assuming anything.

## Where the project stands: KtToPy is DONE pending user acceptance

The WFL Kotlin app (`~/Programming/WFL_MixingCenter/WFL/`) runs fully in Python/Kivy via the
KtToPy transpiler (`tools/pseudokotlin/`). Every measured gate is green:

| Gate | Command | Expected |
|---|---|---|
| Geometry (dump path vs real Compose) | `cd tools/pseudokotlin && python3 fidelity.py` | `377/377 (28 screens)` |
| Interaction + shell sweep | `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py` | `513/513 across 27 screens + shell(5 handlers)` |
| Real synthetic touches (nav bar) | `cd ~/Programming/WFL_MixingCenter/render && xvfb-run -a python3 realtap_gate.py` | `GATE: GREEN` |
| Kotlin unit tests in Python | `cd tools/pseudokotlin && python3 run_kotlin_tests.py` | `160/160 pass` |
| Domain corpus | `cd tools/pseudokotlin && python3 oracle.py --all` | 11/12 green (12th = LayoutDumpTest, ERR by design — needs real Compose) |
| DAO invariants | `cd tools/pseudokotlin && python3 datalayer_oracle.py` | ALL GREEN (9 invariants) |

The runnable app: `cd ~/Programming/WFL_MixingCenter/render && python3 run_app.py` — no arg boots
the WHOLE app (AppNavigation shell: bottom nav bar + NavHost, phone display 412x915 portrait,
seeded completed user, boots to Today; nav taps work with real touches). `run_app.py <ScreenName>`
runs one screen in isolation (names in `render/layout_screens.txt`). Fonts (Material icons +
NotoColorEmoji) are vendored in `render/assets/` — no OS package dependencies.

**The only open item: Lucas's acceptance drive.** He taps around the real app; anything that feels
un-Kotlin becomes the punch list. Minor known non-defects: ProgramEditor "Deload" label slightly
overlaps (within tolerance, legible); default launch has no enrolled program (Today shows the
empty state — could seed an enrolled program if he wants a richer demo).

## Next phase (after acceptance): Python → PseudoDart

Converting the Python output into "Python disciplined in Dart" (restrict to constructs that map
1:1 to Dart) so later conversions happen in an easy-to-run environment. Agreed shape, in order:
1. **Discipline-checker gauge first** (the measured instrument defining the discipline — analogous
   to fidelity.py; a number that can't be gamed). ~1 slice.
2. **Typed emission from Kotlin** — the transpiler sees Kotlin's types; emit them rather than
   reconstructing. ~1–2 slices.
3. **Static runtime twin** — the runtime's dynamism (autostub, loader __missing__, monkeypatching)
   is exactly what Dart forbids; replace with explicit typed modules. Hard part, ~2–4 slices.
4. UI can likely reuse the existing PseudoFlutter kit (WFL conversion prior art, 65/65 goldens).
Estimated 6–12 work rounds total. Key lesson to carry (memory: launcher-vs-instrument-path): every
gauge certifies only the path it measures — PseudoDart's checker must run against the same artifact
that executes.

## Standing law (also in memory files — they are binding)

- Zero hand-edits to transpiled WFL-Python; regenerate via `python3 tools/pseudokotlin/build_mixingcenter.py`.
- One cause = one general fix in a shared layer (kivy_kit / runtime / loader / differ / transpiler).
  A real fix moves a GROUP of failures. No per-screen/per-name patches.
- Never game a meter: no error-swallowing, threshold-tuning, or assert-free "passes".
- Kotlin in WFL_MixingCenter/WFL may be adjusted only if appearance/function is unchanged.
- Font/shaper bridges are the ONE sanctioned non-general area; every metric specimen-derived
  (dumpSpecimen/dumpSpecimenList), never inferred from mixed app screens.
- Instruments certify only what they measure: the fidelity gauge covers the DUMP path; the
  runnable app (run_app.py) is a separate wiring surface — eyeball it before trusting it.

## Delegation policy (memory: delegate-to-opus-tight-briefs)

Split work into small fenced sub-tasks for subagents; the orchestrator reviews, runs final gates,
and commits. **Sonnet by default** for scoped implementation with verifiable gates; **Opus only for
open-ended diagnosis**. Every brief carries: (1) the law verbatim, (2) an explicit file fence,
(3) exact verification gates with expected outputs, (4) a stop-rule ("cause out of fence → report,
don't fix"), (5) a DevComms report, and (6) "do the work in your own turn — your final reply is
the deliverable" (Sonnet once backgrounded its task and quit). Sequence agents sharing a file;
parallelize only disjoint fences. Hold commits while any agent is editing shared files.

## Command crib

- Full geometry gauge: `cd tools/pseudokotlin && python3 fidelity.py`
- Regenerate WFL-Python after transpiler/runtime edits: `python3 tools/pseudokotlin/build_mixingcenter.py`
- Regenerate auto layout tests after generator edits: `python3 tools/pseudokotlin/gen_layout_dumps.py`
- One screen's kivy dump: `cd ~/Programming/WFL_MixingCenter/render && python3 inspect_layout.py <ScreenName>`
- One screen's compose dump: `cd ~/Programming/WFL_MixingCenter/WFL && ./gradlew -p app testDebugUnitTest --tests '*LayoutDump*.dump<ScreenName>' --rerun` (use `--rerun` — gradle silently skips up-to-date tests)
- Screenshot a run: `SHOT=out.png xvfb-run -a python3 run_app.py [Screen]` (file gets a frame suffix: out0001.png)
- Dashboard: edit PROGRESS_ondeck.md, then `python3 tools/pseudokotlin/track.py` (never hand-edit PROGRESS.md/html)
- Headless probes of the full app MUST settle first (repeated `comp.compose()` until node count
  stabilizes) — the first compose renders a loading-spinner branch; reading too early gives a
  15-node tree and false "broken" conclusions (this burned us once).
