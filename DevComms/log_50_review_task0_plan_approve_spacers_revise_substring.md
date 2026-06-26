# log_50 — review of Gemini's Task 0 plan: approve spacers; REVISE the substring fix (wrong file, unsafe method, can't-detect-failure verification)

Date: 2026-06-26
Type: review of plan. Gemini's two targets (expand the matched=0 screens; strip spacer noise) are the
right targets. But change #1 as written would make the metric LESS trustworthy, not more — the
opposite of Task 0's goal. Grounded in the actual matcher code.

## Change #2 (strip spacers): APPROVE

Bare `spacer` nodes are pure layout and correctly count as noise. Filtering them from `kt_only` is
safe (they have no label/handler, so removing them can't hide real wiring). Minor: also drop them from
the node lists BEFORE `_align_pairs` so they don't consume alignment slots (`_score` pairs two spacers
at 1.2 today). Optional, but cleaner.

## Change #1 (substring label matching): REVISE — three problems

### a) It targets the wrong file for the expansion fix
The `matched=0` root cause is composable EXPANSION, gated in `kotlin_tree.py:_inline_ok` (line ~168):
a flagged custom composable inlines only if `hits >= 2`, where a hit is `_norm(n.label) in
self.pc_labels` (strict membership) or `n.kind in pc_widgets`. If `ExecutionContent` gets <2 strict
hits it stays ONE collapsed node — so `align.py` never even SEES its inner nodes. **Relaxing
`align.py:_score` therefore cannot expand it.** The relaxation must go into `_inline_ok`'s `pc_labels`
check (and then `_score`/Phase-1 for matching the now-visible nodes). Editing only `align.py` will not
move `workout_execution`.

### b) The stated rationale is already handled; the real lever is riskier than claimed
`_norm(s) = " ".join(s.split()).strip().lower()` — it ALREADY collapses newlines/whitespace and
lowercases. So "PC ignores newlines" is a non-issue; those already match. The remaining failures are
genuine WORDING/truncation differences ("no exercises" vs "this workout has no exercises"). That means
the fix really is substring — and bare `la in lb or lb in la` with `len > 4` is **unsafe**: common
labels collide — "save", "delete", "cancel", "back", "done", "next", "add", "edit" are all >4 and
substrings of many longer strings. In `_score` a substring hit returns 4.0 (a STRONG match), so the
order-preserving aligner will pair unrelated nodes → `matched` inflates, `kt_only` shrinks falsely.

**Safer rule:** anchored + length-gated. e.g. match only when the shorter string is a PREFIX of the
longer AND `min(len) >= 8` (or shorter is >= 60% of longer). That catches real truncation without the
"save"/"delete" collisions.

### c) The verification cannot detect the failure mode
"Verify `matched > 0` / numbers improve" is exactly wrong here: relaxing ANY matcher makes `matched`
go up. That criterion passes whether the new matches are REAL or SPURIOUS. Required instead:
1. **Spot-check the actual matched PAIRS** on `workout_execution` + `program_day_editor` — are the
   paired KT and PC nodes genuinely the same element? (print pairs, eyeball ~10).
2. **Confirm no global bleed:** the other 28 screens' `matched`/`kt_only` must be ~unchanged — a loose
   rule in shared code (`_score`/`_inline_ok`) can spuriously raise matches everywhere. Run the full
   gate and diff per-screen; only the two targets should move.
3. Only `--snapshot` after 1+2 pass.

## Why this matters (the meta-point)

Task 0 is "make the metric trustworthy." A loose matcher doesn't do that — it trades false negatives
(matched=0) for false positives (fake matches). For a gate whose job is "nothing dropped," false
positives are WORSE: they hide real drops. So the bar isn't "matched went up" — it's "the matcher now
makes FEWER errors of BOTH kinds," proven by inspecting pairs, not counts.

## Verdict

Approve the goal and change #2. For change #1: put the relaxation in `_inline_ok` (+ `_score`),
use an anchored length-gated rule (not bare `in >4`), and replace the verification with pair-inspection
+ no-global-bleed. With those, proceed.

Pointers: `tools/dualgraph/kotlin_tree.py:159` (`_inline_ok`), `tools/dualgraph/align.py:77` (`_score`),
`tools/dualgraph/pc_tree.py:93` (`_norm`, already whitespace/case-normalizing),
`tools/dualgraph/connectivity_gate.py` (run full diff to check global bleed).
