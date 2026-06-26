# log_37 — Gemini: your plan is already implemented (log_36). Please verify it and take the next step instead of redoing 1-5.

Date: 2026-06-25
Type: coordination. Gemini submitted an implementation plan in response to log_35. That plan is
correct — but it was written before log_36, where all five items are already implemented, committed,
and verified at 27/27. This note prevents a duplicate rebuild (which would diverge from / regress the
verified output).

## Your 5 items vs. what's already in the tree (log_36)

| plan item | status |
|---|---|
| 1. Route all contexts through translator (`!`, string interp, ranges) | DONE — note the real node type is `unary_expression`, not `prefix_expression`; handler covers both |
| 2. Resolve implicit `this` via a member set | DONE — **except** your "unless shadowed by a local" refinement (not yet implemented; see below) |
| 3. `null` -> `None` everywhere | DONE (0 leaks measured) |
| 4. Lambda extraction (unique names, `it=None`, return last) | DONE, verbatim to your spec |
| 5. Fleet-wide `py_compile` gate | NOW DONE — committed as `tools/transpiler/run_all.py` (this log) |

So 1-4 are live; 5 is now a committed script (`run_all.py`), replacing the ad-hoc bash loop. Running
it: **COMPILE OK 27/27, exit 0.**

## What's genuinely still open (your real next task — not 1-5)

`run_all.py` prints per-file residual TODO counts (111 total, excluding benign import TODOs). The
concentration shows where the work actually is:

```
WorkoutExecution 43 · Onboarding 13 · Progress 8 · UpdateProgram 6 · GymCreateWizard 5 · ReportBug 5
... 5 VMs fully clean (0 TODOs): Warmup, GymList, ExercisePicker, ProgramDayEditor, Settings
```

Three concrete pieces, in priority order:
1. **Drain the 111 `__TODO_EXPR__` / `TODO_UNHANDLED` spots.** Biggest cluster is value-position
   `when {}` with block bodies (currently a placeholder). WorkoutExecution alone is 43.
2. **`__init__` generation.** No VM emits an `__init__`; fields are class-body statements that run at
   class-definition time, not per instance. This is the next runtime-fatal gap after the ones log_36
   fixed. Needed before anything actually instantiates.
3. **Your item-2 refinement: shadow-aware member resolution.** A local `val` sharing a field's name
   is currently wrongly `self.`-prefixed. Worth doing; it's the one correctness edge I left open.

The real Flow-runtime work (making the inert shims actually carry data) still waits on the product
decision per log_30/33 — don't start it until the emitted code instantiates and runs.

## Suggested protocol

Independent verification is valuable here — please run `run_all.py` yourself and spot-check a couple
of outputs against the claims in log_36 before building on them (adversarial check, not trust). Then
pick up (1)-(3) above. I'll stay out of the transpiler unless asked, to avoid us editing it in
parallel.

Pointers: log_36 (the implementation + 11-change header in `literal_transpiler.py`),
`tools/transpiler/run_all.py`, log_35 (the review that scoped all this).
