# log_123 — breadth #1: MutableStateFlow → State (the reactive UI-flag seam, grows once)

Date: 2026-06-28
Type: feature (Bucket 3 breadth). The reactive infra a 2nd interactive screen needs. Follows log_120's
note of this as the latent reactive item.

## What & why

exercise_detail is the next interactive drop-in. Unlike gym_list (only DERIVED flows), it carries a
`MutableStateFlow` UI-FLAG: `excludePrompt` — the swap-confirm dialog state, set by `onToggleExcluded()`,
cleared by `confirmSwapNow()/Later()`. The latent gap (flagged log_120): the shim's
`MutableStateFlow.value` was a DEAD attribute — writing it changed nothing observable, so the dialog
would never repaint. Closing it is the **MutableStateFlow → State** mapping, and it's FIXED INFRA
(grows once, reused by every UI-flag/search screen — exercise_detail, exercise_picker, ...).

## Fix

Both shims (`pseudoui_run._reactive_ns` for verify, `generated/reactive_shim.py` for the app):
`MutableStateFlow.value` is now a PROPERTY whose SETTER requests a repaint
(`reactive.invalidate()`, lazy+guarded so the shim still imports in the sandbox), and only when the
value actually CHANGES — mirroring PseudoCoup's `State.set()`. Reads stay plain. `SharedFlow.emit`
stays a no-op (nav events ride `NAV_HANDLERS`, not flow collection).

## Verified

- micro-test: `MutableStateFlow(None)`; `.value='PROMPT'` → dirty True → flush → **1 repaint**;
  unchanged write → dirty False (no spurious repaint).
- no regression: gym_list `--app` **10/10**; `test_gym_list_gen` **5/5** (render + 4 handlers +
  re-render); exercise_detail `--app` unchanged (8 shared); app smoke **30/30**.

## exercise_detail status (characterized, for the next step)

`--app`: 8 shared / 2 gen-only / 2 hb-only; `--auto` dynamic 4/5, unresolved 3.
- hb-only 2 = the benign kit glyphs `⋮`/`♡` (same as gym_list).
- unresolved 3 `'body'` exprs = the CONDITIONAL sections
  `if (!exercise.{instructions,cues,videoLink}.isNullOrBlank())` — skipped for the seeded Squat (blank
  fields), so hand-built skips them too. Not divergence — guard-resolution gaps. Render essentially
  matches.

## Next (to finish the drop-in)

`NAV_HANDLERS["exercise_detail"]` (onNavigateBack, onNavigateToEdit) + capture the overflow-menu /
dialog onClicks in the IR + an interaction test (fire `onToggleExcluded` → `excludePrompt` set →
dialog renders, proving this seam end-to-end) + vendor + route. The reactive seam itself is done; the
remainder is per-screen wiring (~the gym_list shape).
