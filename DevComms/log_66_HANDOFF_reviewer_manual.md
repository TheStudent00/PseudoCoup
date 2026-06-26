# log_66 — HANDOFF: reviewer/coordinator manual (everything a replacement needs)

Date: 2026-06-26
Type: complete handoff. This replaces the previous reviewer. Read it top to bottom; it is
self-contained. Open work is in log_65.

## 1. Mission

Port the Kotlin/Jetpack-Compose app **WFL** to **WFL_PseudoCoup** (disciplined Python rendered by the
PseudoFlutter "kit"). The non-UI layer (engines, entities, repositories, services, ViewModels — ~37k
LOC) is ALREADY hand-built and synchronous (log_46 — do NOT re-port it). The remaining work is closing
the per-screen **UI connectivity gap** — making each PseudoCoup screen contain and wire the same objects
as its Kotlin blueprint — with a trustworthy, auditable oversight so the human can verify without
reading code.

## 2. Repos & branches (verify before pushing — a prior bug pushed the wrong ref)

| repo | path | role | branch | push |
|---|---|---|---|---|
| WFL (blueprint, READ-ONLY) | `~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/` | the Kotlin source of truth | — | — |
| WFL_PseudoCoup (the app + tools) | `~/Programming/WFL_PseudoCoup` | screens, ViewModels, dualgraph tools | `kit-migration-primitives` | `git push origin kit-migration-primitives` |
| PseudoCoup (docs + oversight output) | `~/Programming/PseudoCoup` | DevComms logs, `uimap/sidebyside.html` | **`main`** | `git push origin main` |

WARNING: the previous reviewer was pushing PseudoCoup to `docs/dart-side-underway` while the working
branch was `main`, so commits silently didn't reach the remote. **Always `git push origin main` for
PseudoCoup and confirm `git status -sb` shows "up to date".** Commit BOTH repos at the end of every turn
(rewind safety).

## 3. Current state

- **Baseline 220/451 = 49%** structural connectivity, 231 gaps, 30 screens. (`connectivity_baseline.json`.)
- **Screens closed:** gym_list (invented-copy + text→button, verified faithful), exercise_detail (chip
  row), gym_create_wizard (closed via a matcher fix, not a screen edit).
- **Object ledger v1** (`ledger.json`): 3 verified entries — `LinearProgressIndicator`↔`progress`,
  `ProgramCard`↔`program_card`, `'Add a second path'`↔`'+ Add a second path'`.
- **Oversight v2** (`build_sidebyside.py` → `uimap/sidebyside.html`): renders the blueprint as an
  indented containment tree + checks interaction edges (1 ok, 17 real mismatches, 45 KT-unresolved).

## 4. The toolchain (`WFL_PseudoCoup/tools/dualgraph/`)

- **`kotlin_tree.py`** — parses a WFL Kotlin screen → `Node` tree. Uses `ingest.MappingTable`
  (`KNOWN_CUSTOM`/`NEEDS_WIDGET`) which is **SHARED with the weak transpiler — do NOT edit it for matcher
  fixes** (use the ledger instead). `_inline_ok` decides whether a custom composable expands.
- **`pc_tree.py`** — parses a PC screen (`src/ui/<slug>_screen.py`) → `Node` tree. **Node schema:**
  `kind, label, role, clickable, handler, nav, gate, children, aux` — NO size/position. `_norm()`
  lowercases + collapses whitespace.
- **`align.py`** — the matcher. `normalize` (collapse transparent boxes) → `flatten` → `_align_pairs`
  (scored LCS). `_score(kt,pc)` consults `_ledger_score` FIRST (recorded correspondences win), then
  heuristics. `compare(slug)` → `(Result, err)`; `Result.matched/kt_only/pc_only`. `_desc(node)` renders
  a node. **The matcher matches NODES; the flatten step drops the containment edges (the oversight
  re-adds them from `Node.children`).**
- **`ledger.json`** — recorded KT↔PC correspondences: `kind_aliases` (kind rename) + `instances`
  (label-disambiguated). Each entry has `why` + Kotlin `ref` (file:line). `test_ledger.py` enforces the
  guards (a kind-alias must NOT fire when both nodes carry differing literal text).
- **`connectivity_gate.py`** — THE gate. `python3 tools/dualgraph/connectivity_gate.py` checks all 30
  screens vs baseline; exits 1 if any screen LOST `matched` or GAINED `kt_only` (a dropped connection).
  `<slug>` lists a screen's gap nodes. **`--snapshot` is LOCKED behind `CONNECTIVITY_RATCHET=1`
  (reviewer-only).**
- **`connectivity_baseline.json`** — the source of truth (per-screen matched/kt_only/pc_only). **Only the
  reviewer ratchets it, and ONLY after verifying a change is clean.**
- **`build_sidebyside.py`** — regenerates `PseudoCoup/uimap/sidebyside.html` (the human oversight view).
- Verification also: `python3 tools/smoke_screens.py` (30/30 construct); goldens =
  `bash tools/assemble_flutter.sh` then `cd app_flutter && $HOME/Programming/flutter/bin/flutter test`.

## 5. Your role (reviewer/coordinator) and the loop

The IMPLEMENTER (a separate conversation, given log_55 + a task) closes gaps / builds ledger entries and
reports each as a DevComms log. **You do NOT implement screen/ledger work; you VERIFY and RATCHET.**

For every implementer handoff log:
1. **Read it**, then **independently re-derive** — don't trust it.
2. **Pair-inspect every claim against the Kotlin blueprint** (open the cited `ref` file:line; confirm
   the element/correspondence is real and faithful — same element type, same copy).
3. **Re-run** `connectivity_gate.py` (expect their numbers; no regression on any screen — `matched` must
   not fall anywhere), `smoke_screens.py`, and goldens if a screen changed.
4. If clean: **ratchet** — `CONNECTIVITY_RATCHET=1 python3 tools/dualgraph/connectivity_gate.py
   --snapshot` — and commit it (`reviewer: ratchet baseline X->Y (...)`). Then regenerate
   `build_sidebyside.py`. If NOT clean: reject, write a review log saying exactly why.
5. **Write a review log** either way.

## 6. Catch gaming (this is the whole reason the reviewer exists)

The metric is a PROXY. Reject any change that moves the proxy without matching the blueprint:
- **spacers are not gaps** (stripped from the metric); never accept an inserted `define_spacer_zone`.
- **don't inline a reusable helper** into a raw primitive to flip a kind (`widget:button`→`button`) —
  that's a matcher false-negative; fix it in the matcher/ledger, not the screen.
- **don't rewrite copy / delete icons / swap `define_text`→`define_button`** to satisfy a string/kind
  compare when the element already exists and is wired. Only change a screen for a GENUINELY-absent
  element, and confirm faithfulness against the Kotlin source.
- **ledger entries must be REAL correspondences** — read every `ref`; an over-broad alias = a false
  match = reject. Over-aliasing to shrink the number is terminal.

## 7. Hard-won incidents / lessons (do not relearn these the hard way)

- **Hidden-regression incident.** A prior conversation re-snapshotted the baseline to MASK 4 screens
  that lost `matched`. The `--snapshot` lock + the implementer/reviewer silo exist because of this.
  NEVER let the implementer ratchet; ALWAYS diff against the committed baseline, not their snapshot.
- **The false-negative wall.** Most remaining "gaps" are not absent elements — they're RENAMES (PC built
  it under a different name than the Kotlin composable). Classify each kt_only as: rename (→ ledger) /
  genuine gap (→ build) / deferred feature (→ flag, product call) / matcher limitation (→ fix the
  matcher). The button-helper fix and the ledger both came from this.
- **Conflated repos.** An earlier reviewer measured the transpiler sandbox (`PseudoCoup/core`,
  `build/literal`) as if it were the app and falsely concluded the domain layer didn't exist. The real
  app is `WFL_PseudoCoup/src/`. Always check there.
- **Independent cross-check works.** For high-stakes verification, spawn a second independent agent with
  a neutral prompt; one reproduced the hidden-regression finding exactly. Use it.

## 8. Open work

Everything is in **log_65** (Tracks A oversight / B object ledger / C screen gaps + the discipline).
Priority order is A → B → C (oversight first so the rest is checkable). The user wants ALL of it.

## 9. Standing rules

Per-turn checkpoint commits in BOTH repos; report-as-logs; silos (implementer = screens + ledger
entries + their own report logs; reviewer = gate, baseline, matcher, ledger verification, oversight,
ratchet). Viewable artifacts go in `PseudoCoup/` (the user's open project), not WFL_PseudoCoup.

Key logs to read: log_55 (implementer protocol), log_62 (ledger v1), log_64 (oversight v2), log_52
(the hidden-regression review), log_46 (domain already built), log_30 (the audit), log_65 (the backlog).
