# log_55 — KICKOFF for a fresh implementer conversation (Claude or otherwise) — the ONE doc to hand over

Date: 2026-06-26
Type: self-contained kickoff. You are the IMPLEMENTER; a separate reviewer conversation verifies every
change and is the only one that ratchets the baseline. You are continuing a Kotlin(Compose)→Python
(`WFL_PseudoCoup`) port. Work in `~/Programming/WFL_PseudoCoup` (branch `kit-migration-primitives`).
Everything you need is here; log_53 (full protocol) and log_49 (full work-list) are deeper references.

## What you are doing (and NOT doing)

The non-UI layer is **already built** — 9 engines, 27 entities, repositories, 39 domain services, the
27 ViewModels (~37k LOC of synchronous Python). **Do not re-port domain or ViewModel logic.** Your job
is to **close per-screen UI gaps**: each PseudoCoup screen (`src/ui/*_screen.py`) implements a subset
of its Kotlin blueprint; you add the missing widgets and wire them to the EXISTING ViewModels/services,
**reusing** `src/ui/widgets.py` (73 components) + `src/kit.py` primitives.

## Current state (clean — verified)

- Repo: `~/Programming/WFL_PseudoCoup`, branch `kit-migration-primitives`. Gate is GREEN.
- Connectivity baseline: **211/578 (37%)**, just verified clean (0 regressions). It is the committed
  source of truth at `tools/dualgraph/connectivity_baseline.json`.
- Prior cleanup is DONE — there is no punch-list to redo. Start at the screen loop below.

## NON-NEGOTIABLE rules (a fresh read — these are enforced, not aspirational)

1. **You NEVER run `connectivity_gate.py --snapshot`, and you NEVER edit the baseline.** It is owned
   by the reviewer (the snapshot is now locked behind a token you do not have). You propose changes;
   the reviewer ratchets the baseline after verifying.
2. **Any screen's `matched` count dropping = STOP.** That is a dropped connection. Fix or revert before
   doing anything else. Never present a change where matched fell on any screen.
3. **Any `matched` increase must come with the actual KT↔PC pairs** (`align._desc(node)`) proving they
   are the same element, not spurious. Counts alone are rejected.
4. **This is an ongoing process — there is no "done" to declare, no success assessment to write.** You
   report the honest current state every step, including losses and unknowns. "The number went up" is
   not success.
5. **Everything you do is independently re-run and pair-inspected** (by a reviewer and a second
   independent agent). Honest failure costs nothing. Masking a regression, claiming a fix that doesn't
   survive re-run, or reporting inflated numbers ends the collaboration.
6. **Hygiene:** no stray/scratch files; one coherent commit per change; never leave work uncommitted.

## The per-change loop (every change, exactly this)

```
# 1. pick ONE screen; list its real gaps:
python3 tools/dualgraph/connectivity_gate.py <slug>        # e.g. exercise_create_screen
# 2. close the REAL gaps in src/ui/<slug>.py by REUSING widgets.py + kit, wired to src/viewmodel/<...>
# 3. verify connectivity maintained + improved:
python3 tools/dualgraph/connectivity_gate.py              # MUST exit 0; report the FULL per-screen delta
python3 tools/smoke_screens.py                            # 30/30 construct
$HOME/Programming/flutter/bin/flutter test app_flutter    # goldens
# 4. commit cleanly. Hand the change + the KT<->PC pair evidence to review. DO NOT snapshot.
```
Any matched drop on ANY screen in step 3 → STOP and fix. The reviewer ratchets the baseline if clean.

## Your first task (a fast win to prove the loop)

Start with **`gym_list_screen` (2 gaps)**, then `paths_screen` (2), `workout_warmup_screen` (2). Run
the loop above, close the gaps by reusing existing widgets wired to the existing VM, and hand it to
review with pair evidence. Then work up the list (bulk: `onboarding`, `workout_execution`, `calibrate`
— later). **Already done — skip:** `exercise_create`, `exercise_detail`, `gym_create_wizard`.

## Do NOT game the matcher (three ways people have tried — all rejected on review)

The gate is a *proxy* for "the PC screen has the same wired elements as the blueprint." Never contort
the code to move the proxy:

1. **Spacers are NOT gaps.** The metric strips `spacer` nodes (pure layout; spacing is guarded by the
   goldens, not connectivity). If a gap is a `spacer`, ignore it — never insert `define_spacer_zone`.
2. **Don't inline a reusable helper to flip a classification.** If a "gap" is really the same element
   already present and wired but *classified* differently (e.g. a `widgets.py` `button()` helper shows
   as `widget:button` while the blueprint's raw Button is `button .filled`), that is a **matcher
   false-negative, not a missing element**. Do NOT replace the helper with a raw primitive to satisfy
   the matcher — that degrades reuse for zero real gain. **Flag it to the reviewer to fix the matcher.**
   (This exact case — the button helper — is already fixed in the matcher as of baseline 214.)
3. **Don't rewrite copy or swap element types to make a string/kind line up.** If a gap is closed by
   editing user-facing text, deleting an icon, or changing a `define_text` into a `define_button` so
   the matcher's exact-string / kind comparison passes — and the element was already present and wired
   — that is gaming, and it is rejected. Only change a screen when the element is **genuinely absent**.
   When you do, **open the real Kotlin source and confirm faithfulness**: same copy, same element type
   the blueprint actually uses. Matching the proxy is not the goal; matching the blueprint is.

Close only REAL gaps: a genuinely-absent button/widget/text/icon/sheet/dialog. Moving the number
without adding a real, wired element is the gaming that ends the collaboration.

## Caveats already known (don't rediscover or paper over)

- `program_day_editor_screen` is matcher-blind (`matched=0`) — a tool limitation, not your fault and
  not yours to "fix" by forcing matches. Leave it; it's a separate careful task.
- Structural match ≠ behavior. Wiring a `button 'Delete'` node means wiring its REAL handler to the
  REAL service — not a stub that just makes the node appear. The gate can't see behavior; that's on you.

Full detail: log_53 (protocol), log_49 (work-list), log_54 (how this clean base was produced),
log_46 (why the domain is already built).
