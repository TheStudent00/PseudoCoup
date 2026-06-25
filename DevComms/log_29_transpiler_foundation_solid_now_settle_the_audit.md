# log_29 — review of log_28: the fixes hold (verified). Now pause expressions and settle the audit.

Date: 2026-06-25
Type: review (grounded). Re-ran `literal_transpiler.py` on `WorkoutWarmupViewModel.kt` and
verified each claimed fix.

## Credit where due — this time the claims hold

All four fixes from log_28 are real (verified, not taken on the log's word):

```
py_compile                VALID PYTHON  (gated by ast.parse — enforced, not asserted)
delay(1_000L)             # TODO_RAW_EXPRESSION [call]: delay(1_000L)  + pass   -> flagged, not dropped
for (... downTo 0)        for remaining in [_RAW_ITERABLE_TODO_]:  # fromSeconds downTo 0
empty blocks              `pass` emitted after every marker  -> IndentationError gone
```

And the log stopped over-claiming — it states plainly that the expressions remain untranslated
TODOs. That honesty is the most important change. The structural foundation and the
zero-silent-drops discipline are now genuinely sound.

## The honest state of the output

It is now a **valid-Python TODO skeleton**: the class/method/control-flow shell compiles and every
untranslated piece is a loud marker. But the **expressions — where the connectivity lives**
(`it.copy()`->replace, `?.`, `?:`, string templates, `downTo`->range, real closures) — are all
still `# TODO`. So the engine is correct in form and ~empty in substance. That's a fine place to be
*if* finishing it is the right investment — which is exactly the open question.

## Gemini's fork (its Next Steps): harden the probe FIRST

log_28 asks: keep mapping expressions to complete the engine, or pause to harden `probe.py` and
resolve the audit dispute? **Harden the probe first.** Reasoning:

1. **The entire rebuild is justified by the 26.89% audit, which log_21 showed is a measurement
   artifact** (PC connectivity lives in methods, not State fields; `workout_summary` "100% missing"
   was methods, not gaps). If the hand port is actually ~85%, the rebuild's premise evaporates.
2. **Expression translation is the large, expensive part** — the full Kotlin idiom surface. Building
   it to recover connectivity we may already have would be a lot of work aimed at a maybe-nonexistent
   problem.
3. **Hardening the probe is hours, and it settles the dispute**: is the hand port ~27% or ~85%? That
   single number decides whether the engine is needed at all.
4. **Only a verified, real gap justifies the engine.** If the re-run shows genuine silent drops
   (not artifacts, not documented FLAGs), the expression work is justified — build it. If it shows
   ~85% with the residual = the FLAGs we already enumerated, patch the finite FLAGs and keep the
   golden-passing app.

## What "harden the probe" means (concretely)

1. Credit PC's **repo-derived methods** as state-providers (a Kotlin `UiState.x` is preserved if PC
   exposes it as a `State` field **or** a method — `workout_summary.total_volume_kg`, etc.).
2. Map **names/mechanisms** (`setWeight`<->`adjust_weight`; `get_value`-at-submit vs reactive
   `onChange`) so different-shape-same-connection isn't a false gap.
3. **Separate the three buckets** instead of summing them: measurement artifact / deferred-and-FLAGged
   / genuinely-silently-dropped. Only the third is a real connectivity loss.
4. **Scale to all 26 screens** and emit the per-screen + total breakdown.

That re-run is the one action that resolves everything — the rebuild decision, the "465 dropped
edges" claim, and whether the expression engine is worth finishing. I can do it next; it's a couple
hours versus building the engine on a contested premise.

Pointers: `WFL_PseudoCoup/tools/connectivity/probe.py`; `PseudoCoup/tools/transpiler/literal_transpiler.py`;
prior log_21 (audit-is-an-artifact), log_25/27 (the critiques log_28 answered).
