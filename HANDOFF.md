# Session handoff — 2026-07-09 FRONTIER ALIGNMENT PHASE (read this block first)

STATUS: owner approved a two-item frontier-alignment plan this session. Item (1) is LANDED; item (2) is
QUEUED, not yet run.

(1) KT MISFIRE FIX -- LANDED (WFL_MixingCenter commit b70d65e, test sources only,
WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt): fixed the kt walker's
self-documented ANOMALY 1 settle-race misfires. Symptom, established by a read-only survey of a real
kt_walk.json: "Home" tab fired twice, "You" tab (present in the tree, structurally identical to the four
tabs that DID fire) never fired at all, and "Search wins"/"Browse programs" edges landed on a DIFFERENT
node's handler_kind than their own recorded label implies -- BFS coverage corrupted (kt "exhausted" at 21
states partly by burning budget on wrong/duplicate taps instead of the real frontier). Root cause: the
existing ANOMALY 1 settle fix (loop settling until two consecutive node-count reads agree) makes a SINGLE
enumeration's node COUNT stable within one mount, but "ONE FRESH APP MOUNT per replay" means every later
replay of a shared path prefix settles a BRAND NEW mount's tree from scratch -- a LazyColumn/LazyRow/
TabRow subcomposition can legitimately settle to a DIFFERENT stable item order across two independent
mounts of the identically-seeded state, so a bare ordinal captured at one enumeration silently drifted onto
the wrong node at fire time. Same class of fix as the py side's overlay-identity fix (never fire from a
stale position -- resolve by stable identity at the moment of firing). Fix: at fire time, after the settle
that precedes the tap, resolve the target by (label, handler_kind) within the JUST-settled enumeration --
the same join key walk_diff.py's align_edges() already uses -- not by raw ordinal position; ambiguous
matches (duplicate label+handler_kind) fall back to ordinal WITHIN the matching subset, logged loudly as
AMBIGUOUS-RESOLVE; a recorded target that no longer resolves at all is an honest edge error, never a fire
against whatever now occupies that ordinal. Applied at BOTH fire paths: the walk loop's primary fire site
and replayTo()'s per-step prefix replay (the latter carries the exposure across mounts, since it re-taps
recorded ordinals from a previous state's discovery on a fresh mount each time -- Frame's path is now a
List<PathStep> threading each step's recorded (label, handlerKind) forward for exactly this purpose).
ordinal's semantics in the persisted kt_walk.json WALK FORMAT are UNCHANGED -- ActionRec.ordinal still
records the enumeration index at RECORD time; only fire-time RESOLUTION now goes through identity first.
Every resolution logs to kt_activations.log as "RESOLVE ordinal=N -> label=... handler=... method=exact|
ambiguous|missing". The ANOMALY 1 comment block in WalkRecorderTest.kt was updated in place (history kept,
resolution appended) rather than replaced. UNVERIFIED ON HOST: this file has no Gradle/JVM in the authoring
sandbox (documented at the file's own header) -- syntactic care taken, checked against surrounding code
style, but not compiled; first host run is the real verification.

(2) BUDGET-PARITY EXHAUSTION RUNS -- QUEUED, not started this session. Purpose: re-run both engines'
walkers at matched step budgets now that (1) removes kt's misfire-driven budget waste, to get a genuine
apples-to-apples exhaustion comparison (kt's prior 21-state exhaustion was partly an artifact of the bug
just fixed, not a true structural ceiling).

CANONICAL ORDERING: held pending evidence -- not decided this session, no change.

SEED ROOTS: deferred. A structural-reachability survey found nothing currently unreachable from the
existing seed/boot state on either engine, so there is no known gap forcing new seed roots yet; revisit if
the queued exhaustion runs (item 2) surface one.

No PseudoCoup_v0 transpiler/tooling code was touched this session -- the fix is WFL_MixingCenter-only
(test sources). No background processes were started by this session; none were left running.

# Session handoff — 2026-07-08 ORACLE SCAN GAP CLOSED + T1 DIFFER ROWS CLASSIFIED (read this block first)

STATUS: both open items from the 165_py_walk_dense_linemaps.log full host walk (DevComms/hostruns/results/
165_py_walk_dense_linemaps.log, dense linemaps, 0 approximate mounts) are CLOSED this session.

(1) ORACLE SCAN GAP CLOSED (WFL_MixingCenter commit 30d726a): the log's 22 "ORACLE UNKNOWN" lines were all
ONE distinct coordinate (`ui/components/CompactControls.kt:118 kind=Text`), traced to a registry-scan gap,
NOT a misattribution or an out-of-scan-root file. Root cause: compose.py's `_composable(kind)` factory
(shared by BasicTextField/TextField/OutlinedTextField) special-cases a `decorationBox=` keyword by calling
the slot with a synthetic `_inner` that builds a bare `Node("Text")` the instant the slot's own lambda
invokes its `inner`/`innerTextField` parameter — there is genuinely no `Text(...)` token anywhere in app
source at that coordinate (CompactControls.py's `return inner()`, linemap-exact to kt:118); the name "Text"
is synthesized one frame away, inside the runtime. `oracle_registry.py`'s existing scan (`Call(func=Name(
PascalCase))`) can never discover this by construction — no widening of recognized call SHAPES would find
it, since app source calls a lowercase, parameter-bound name there. FIX: added a second registry-scan pass
keyed off the `decorationBox=` keyword itself (resolve its value to the slot body — inline Lambda or a
same-file nested def — find every call to that body's own first parameter recursively through nested
wrapper lambdas, register each resolved coordinate as "Text"). Registry 2272->2273 entries. Verified live:
sandboxed short walker.py boot (--steps 15 --resume) shows all previously-UNKNOWN CompactControls.kt:118
occurrences now print "ORACLE OK"; the repo's second decorationBox site (WorkoutExecutionScreen.py) also
resolves correctly. EXPECTED REMAINDER: 0 UNKNOWN for the boot-reachable subset this session verified; a
coordinate this fix does NOT and cannot cover is one where a live component's origin resolves to a kt
coordinate with NO backing composable declaration/primitive/decorationBox shape at all (a genuinely new,
different scan gap or a real identity.py misattribution) — none such were found in this log (all 22 lines
were the one decorationBox coordinate), but the next full host walk is what confirms 0 UNKNOWN at full
(non-boot-limited) coverage.

(2) T1 DENSITY-DIFFER ROWS CLASSIFIED (WFL_MixingCenter commit 3600e1e, render/walks/density_differ_analysis.md
2026-07-08 section): mount_diff_report.txt's T1 set is now 14 (coord,kind) rows (was 16), coverage having
grown 58->83 T1-matched coordinates. 7 rows are the already-classified B (real per-visit variation) rows
carried forward unchanged (ProgressScreen.kt:284, WflCard.kt:51/62/80, WinsHomeCard.kt:127/73/87). The 7 NEW
rows (WinsHomeCard.kt:71/74/83/92/166/167/172) were investigated with the same method (exact linemap hits,
per-STATE-block mount counts on both engines) and are ALL class B too — same already-documented root cause
(py's BFS-replay walk sampled 2 extra non-ANALYTICS `progress` sub-states kt's single-path walk never
reached; every one of the 7 mounts 1:1 with kt whenever WinsHomeCard actually renders). **NO CLASS-A ROW
FOUND** — 0 of 14 current T1 DENSITY-DIFFER rows show real twin divergence; nothing from this pass requires
owner escalation.

Sandbox process cleanup confirmed (ps aux showed no leftover xvfb/python3/walker.py processes after
verification runs). No PseudoCoup_v0 code was touched this session — both fixes are WFL_MixingCenter-only
(render/oracle_registry.py, render/walks/density_differ_analysis.md).

# Session handoff — 2026-07-08 LINEMAP DENSITY FIX (read this block first)

LINEMAP DENSITY FIX (tools/pseudokotlin/nodes/statements.py, `_distribute()`): the density-differ
analysis (render/walks/density_differ_analysis.md, rows 1/3/4/5/6/8/13/16) traced 9 of 16 T1
DENSITY-DIFFER rows to ONE transpiler gap -- `_distribute()` (used by `v_lambda`'s trailing
statement, `_receiver_scope`'s apply/run trailing statement, and if/when branch trailing
statements) returned its rendered line WITHOUT the `#@@KTSRC <n>` marker that `stmt_lines()`
already applies to every other statement, so the LAST statement of any multi-statement lambda body
(the common composable-nesting shape, e.g. WinsHomeCard's "Log a win" button subtree, or
AppTopBar's two sibling Texts) had no linemap entry and fell back to identity.py's nearest-line
guess, silently crediting several distinct composable calls to one earlier, unrelated coordinate.
Fix: `_distribute()` now calls `self._kt_tag(...)` on both of its terminal return paths (the
`_stmt_shaped` case and the plain `lead+expr` case), tagging with the trailing node's own line —
same marker/strip/JSON format as everywhere else, no format change, no regression to the block-form
if/when/try paths (those already tag every branch statement via `_branch`->`render_statements`).
Verified: WinsHomeCard.py.linemap.json entries 33->49 (lines 27-31, the "Log a win" subtree, now
each map to their own kt line: 98/92/83/74/71 instead of all falling back to 97); AppNavigation.py
line 379 (second sibling Text) now kt:1012 and line 380 (Column wrapper) now kt:1006, instead of
both collapsing onto line 378's kt:1007 (row 1's exact case). Sandbox short walker.py runs
(steps=8, reset) on the SAME route sequence: pre-fix 165/283 MOUNT lines carried the "~" approximate
marker (58.3%); post-fix 0/362 in a longer-reaching run of the same walk. HOST RE-WALK PENDING: the
3767-approximate count from hostrun 164 was measured against a full walker.py budget on real device
state; a fresh full host walk (not just this sandboxed short smoke check) is needed to get the real
post-fix approximate-mount count for the record. PseudoCoup_v0 commits: "linemap density: every
composable-call line gets its own entry (...)" (transpiler fix, tools/pseudokotlin only) then
"handoff: linemap density fix, host re-walk pending" (this entry). WFL_MixingCenter's regenerated
.py/.py.linemap.json build outputs were NOT committed (left uncommitted per standing build-output
policy — re-running `build_mixingcenter.py` regenerates them identically).

# Session handoff — 2026-07-08 LATE update (COMPONENT IDENTITY SYSTEM; successor model: read this block fully)

OWNER'S STANDING SPEC (verbatim intent, non-negotiable): zero opaqueness. Every UI component and every
activator carries an identity tag; a live runtime log announces what is what (mounts, activations); every
entry cross-checks against the Oracle ledger AT RUNTIME, so a one-sided "empty" entry is impossible to
assert — the system itself names what is at each position on both engines or names the ledger entry that
failed to appear. Also: communication per the owner's saved protocol (direct answer first, keep their
words, anchor every abstraction, no jargon, ask before ontology/naming choices), delegate heavy work to
Sonnet subagents, commit small and often (high-resolution chronology; sandbox commits, owner pushes).

THE IDENTITY SYSTEM AS BUILT (all committed, WFL_MixingCenter master):
- Shared identity key: Kotlin source coordinate (File.kt:line) of the composable call that produced a
  component. Python gets it via the transpiler's linemaps (<file>.py.linemap.json, generated line -> kt
  line); Kotlin gets it via Compose's composition source information.
- render/identity.py: hooks Node construction (di.install pattern), stack-walks to the transpiled call
  site, linemap-translates to kt coordinate, stores node.origin. NOTE: found compose.py defines
  _call_site() twice (late-binding bug, node.src untrustworthy) — identity.py does its own walk.
- render/oracle_registry.py: the Oracle — 1658 composable call sites scanned from 253 transpiled files;
  {kt_coordinate: composable_name}. Walker verifies every mounted widget against it live: "ORACLE OK" /
  "ORACLE UNKNOWN origin=..." lines. PROVEN: full 50-step walk (hostrun 150) = 0 UNKNOWN.
- kivy_kit.py MOUNT/UNMOUNT + walker.py ACTIVATE lines all carry origin=<kt coord> (IDENTITY_LOG flag,
  on for walker runs, off for fidelity/interact to keep their parsed stdout clean).
- Kotlin half: WFL/app/src/test/.../walk/SourceProbe.kt wraps AppNavigation in the walk test, reads
  currentComposer.compositionData (public API reproduction of Layout Inspector's Inspectable; the
  currentComposer read must stay OUTSIDE try/catch — Compose compiler rule, cost us hostrun 149).
  WalkRecorderTest emitMountLog() dumps "MOUNT engine=kt origin=File.kt:line kind=..." per settled state
  + origin= on ACTIVATE lines, all into WFL/app/build/walks/kt_activations.log (gradle swallows test
  stdout — the file IS the nothing-hidden log). CHANNELS lines = per-node semantics action/property dump.
- render/mount_diff.py: the coordinate-join instrument. Parses both identity logs, normalizes kt bare
  filenames -> registry paths (unique-basename index; ambiguity reported never guessed), filters non-app
  frames, reports per-route and global: both / py-only / kt-only coordinates, each named with registry
  entry + log evidence. Output: render/walks/mount_diff_report.txt.

KT LINE-NUMBER DEFECT = DIAGNOSED AND PARKED (2026-07-08, WFL_MixingCenter commits through c688f54): kt
Group.location systematically misattributes app-level conditional/nested composable call groups to the
nearest ANCESTOR group that carries a source location, rather than the call's own frame — this is Compose's
own ui-tooling-data SourceInformation parser/slot-walk behavior, not a bug in this repo's traversal or in
WalkRecorderTest.kt's print format (confirmed, not guessed, via GROUPDUMP hostrun 156: a raw, unfiltered
per-group name/loc/box/children dump showed `name=Scaffold loc=AppNavigation.kt:249` while the file's only
real `Scaffold(...)` call is at line 385 — line 249 is the enclosing function body's first executable
region; library-internal frames are unaffected and resolve correctly, e.g. `Surface@Scaffold.kt:96`; test-
harness caller frames are also correct, e.g. `AppNavigation@WalkRecorderTest.kt:765`). Reimplementing
Compose's own slot-walk to fix this is out of scope — kt line-exact coordinates are PARKED as unattainable.
What both engines DO prove correctly without exception: FILE and COMPOSABLE NAME. The agreement gauge is
therefore render/mount_diff.py's TIER 2, now COUNT-BASED: for every (file, composable-name) pair, the
MULTISET COUNT of mount occurrences is compared between engines (per route where both engines have route
data, else globally), reported as AGREE / COUNT MISMATCH / py-only / kt-only, with a registry distinct-
call-site count alongside as context (not an equality target). Tier 1 line-exact join is kept in the report,
labeled, and stays the aspirational (currently ~0, by the parked defect) finer-grained measure.
STATUS UPDATE (2026-07-08, WFL_MixingCenter commit fa11c79): kt mount undercount (~1/100th of py's per
mount_diff's count tier; 138-group GROUPDUMP hostrun 156 mostly childCount=1 wrapper chains) root-caused
separately from the line-attribution defect above — SourceProbe.kt only ever read the ROOT composition's
CompositionData, and anything mounted via SubcomposeLayout (Scaffold's own internal slots, LazyColumn/
LazyRow item subcompositions, etc.) composes into its OWN CompositionData with no edge from the root's
Group tree. Fix implemented: SourceProbe now also provides androidx.compose.runtime.tooling.
LocalInspectionTables (a synchronized MutableSet<CompositionData>) around content() via
CompositionLocalProvider; verified directly against ComposerImpl.startRoot() runtime source that every
(sub)composition unconditionally registers its own compositionData into that set when non-null, the same
bridge ui-tooling's own Inspectable uses. WalkRecorderTest's emitMountLog/emitGroupDump now walk root data
plus every registered table (deduped by identity, "TABLE k/N" headers); GROUPDUMP cap raised 3000->6000.
STATUS: subcomposition capture VERIFIED on host (242 tables, T1exact 0->67); mount_diff refined (vocabulary
filter, per-route counts). GRANULARITY PARITY (commits 231bf79/153f03d): py now dumps its mount set ONCE
per settled state under a STATE header (per-creation lines behind IDENTITY_LOG_VERBOSE) -- recompose churn
had inflated py counts ~35-40x; oracle_registry is coordinate->[names] (518/1658 coordinates carry multiple
same-line composables; flat dict had silently dropped primitives). Hostruns 159 (py walk, new format) + 160
(mount_diff) run -- FIRST directly-comparable count run showed raw per-route mount counts still 0 count-agree
(py's BFS-replay walk redumps the same route many more times than kt's single-visit walk -- 137 STATE dumps
across 17 py states vs 21 dumps across 21 kt states -- so raw counts were never comparable, only the VISIT-
NORMALIZED rate is). FIX (WFL_MixingCenter commit 9e233bc): mount_diff's verdicts are now DENSITY-based --
(mounts of a pair/coordinate on route R) / (STATE dumps that engine recorded on route R), compared as an
EXACT fractions.Fraction (no float, no tolerance/epsilon). STATUS UPDATE (2026-07-08, latest run): "MOUNT
DIFF: T1: 62 matched, 19 density-agree, 16 density-differ / T2 24 density-agree, 18 density-differ, 13
not-comparable, 38 py-only, 298 kt-only pairs" -- density comparison surfaces real agreement (0->19 T1,
0->24 T2) that raw counts could never show; remaining DIFFER cases are genuine per-visit rendering variation
(e.g. LazyColumn item counts differing by visit), not noise -- see mount_diff.py's "DENSITY VERDICTS" comment.
DENSITY-DIFFER ANALYSIS (2026-07-08, render/walks/density_differ_analysis.md, WFL_MixingCenter commit
3b691d0): all 16 T1 DENSITY-DIFFER rows investigated row-by-row against raw log evidence + kt/py source --
result: 0 real twin divergence (A), 7 real per-visit variation (B, rows 7/9/10/11/12/14/15 -- entirely
traced to py's BFS-replay walk sampling 2 extra `progress` tab sub-states kt's single-path walk never
reached, plus row 10's genuine hasAnyMetric-gated conditional content), 9 instrument artifact (C, rows
1/2/3/4/5/6/8/13/16 -- two flavors: kt-side Compose runtime frames [`<get-colorScheme>`,
`rememberComposableLambda`] sharing an "enclosing group location" with the real call, and py-side
identity.py's nearest-line fallback silently miscrediting multiple distinct composables sharing one
collapsed/unmapped python line onto one kt coordinate). ARTIFACT FIXES COMMITTED (WFL_MixingCenter commits
19143bc/893650b): (1) identity.py's resolve_kt_coord() now marks every fallback-resolved coordinate with a
trailing "~" (e.g. "AppNavigation.kt:414~") so approximate attributions are visibly distinguished from exact
linemap hits, never silently conflated -- verified live via a sandbox boot dump showing both forms on real
MOUNT lines. (2) mount_diff.py: approximate ("~") coordinates now participate in T2 (file+name) but are
excluded from T1 (line-exact) density material entirely, with their own "py approximate-coordinate mounts: N"
context count; T1 density is now keyed by (coordinate, kind) instead of coordinate alone, so linemap-collapse
rows compare each kind's own rate independently instead of summing unrelated composables together (same-line,
same-kind siblings remain mutually indistinguishable -- an inherent limit of the coordinate format, not
claimed to be solved); kt-side true-infrastructure kinds (remember, rememberComposableLambda,
collectAsStateWithLifecycle, `<get-...>`) are now excluded from coord_route_counts regardless of vocabulary
status, fixing the row-2/row-8 runtime-frame-doubles-the-real-call's-count defect. Re-run against current
logs: T1 DENSITY-DIFFER dropped from 16 to 9 (coord,kind) keys, all of them B-classified rows plus residual
same-kind-sibling ambiguity (e.g. AppNavigation.kt:1007's two Text calls) -- exactly as the analysis
predicted. CAVEAT: this re-run used the PRE-FIX py_activations.log (walker.py has not been re-run since the
identity.py fix), so it carries no "~" markers yet (0 approximate mounts reported) and the row-1/13-style
same-kind-sibling miscredits are still baked into that log's raw MOUNT lines; full effect of the marking fix
(further T1 differ reduction, nonzero approximate-mount context count) needs a FRESH host walker.py run,
which is PENDING (not performed in this session, sandboxed boot-only verification was substituted per task
scope).

WALK DIFF STATE (hostrun 153): mutual territory 4 shared / 4 kt-only / 10 py-only / 69 edge mismatches;
COVERAGE GAP kt-only routes [execution, exercise_detail, exercises, gym_list, settings_notifications,
wins, cooldown, summary] (13 states), py-only [programs, settings] (3). Owner-approved policy: coverage
gaps are never counted as mismatches. Dismiss parity done (kt recorder ranks Dismiss above OnClick; differ
aligns onDismissRequest on handler alone — labels structurally can't match). Numeric text canonicalized
('42'=='42.0'). Ledger-join reporting: every one-sided state resolves to nearest counterpart with overlap
ratio + RESOLVED PAIRs; UNRESOLVED is loud. Max overlap 0.83 -> remaining unshared states differ by real
content, mostly reachability.

NEXT STEPS QUEUE (after the kt location fix): (a) frontier/BFS alignment so both walkers spend budgets on
the same territory (owner approved scoped-diff-first, then alignment); (b) named seed roots for
unreachable screens (Onboarding, ReportBug-crash, WorkoutWarmup) — same seed both engines; (c) make
mount_diff a tracked gate once kt locations are line-exact; (d) owner decision pending: ~61 pre-existing
uncommitted WFL files (mostly regenerated py twins from the T3 transpiler fix — build output awaiting
gate acceptance) — commit or hold; (e) PseudoDart phase per original HANDOFF (discipline-checker gauge
first — note the identity/type discussion: transpiler preserves type ANNOTATIONS/wrappers (Int32/Float32
on values) but variables are unenforced names; owner is aware and parked local-variable annotations until
it bites).

OPERATIONAL (successor model, learn from this session's scars): hostrun loop = write request JSON to
DevComms/hostruns/requests/NNN_name.json {"id","cwd","cmd","timeout"}, owner runs tools/walk_service.py,
read results/NNN.log+.json. A request with NO result file gets re-run on service restart — never leave a
--reset walk request dangling (it wiped 99 steps of progress once; delete/park request files after
failures). Sandbox bash: 45s hard cap per call, background processes are reaped, host paths differ from
Read/Edit paths (see Shell access mapping). Git in mounted repos: stale .lock files appear when a call is
killed mid-git — rm -f .git/*.lock and retry; NEVER bypass with write-tree/commit-tree (an agent's manual
ref writes desynced the index and silently reverted 11 files in a later commit — always `git status` +
`git diff HEAD --stat` after agent commits). Kivy runs in-sandbox (pip install kivy --break-system-packages,
xvfb-run -a, apt libmtdev1); loader needs ~/Programming symlinks (ln -s /sessions/<s>/mnt/X ~/Programming/X).
Repo renamed PseudoCoup->PseudoCoup_v0 2026-07-08; if GitHub repo renamed too: git remote set-url.

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
