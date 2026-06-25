# log_30 — the real audit: PC is a deliberate ~30% partial port, not a silently-broken app (I was wrong about ~85%)

Date: 2026-06-25
Type: result + correction. Built and ran the hardened all-screens connectivity audit
(`tools/connectivity/audit.py`) to settle the log_20/21 dispute. It did not go the way I
predicted, and this records that honestly.

## Bottom line

- **I was wrong about the magnitude.** I expected the hardened number to jump to ~85% and
  show the audit was mostly a measurement artifact. It didn't: **hardened parity is 30.6%**
  (naive State-fields-only = 20.0%; crediting methods + name-normalization lifts it to 30.6%,
  not to 85%). Gemini's 26.89% was roughly right about the *number*.
- **But the cause is the opposite of Gemini's claim.** The misses are **deliberate, documented
  deferrals**, not silent transpiler-drops. Of 360 unmatched Kotlin VM nodes, **0 are
  undocumented silent drops** — every one sits on a screen the hand-porter FLAG-documented as a
  partial port (debug_panel has 12 FLAG/NOTE comments, today 16, workout_execution 7; the
  "silent" sample — `simulateCrash`, `exportThenReset`, nudges, `onDurationChange` — is all
  deferred features or mechanism differences).
- **A VM-rebuild does not recover this.** The gap is **unbuilt SCREEN features**, not
  mistranslated VM logic. Regenerating the VMs gives you VM code for features whose *screens*
  still don't exist. So "regenerate to recover the 465 dropped edges" is wrong on both counts.

## What the audit measures (the hardening from log_21/29)

1. credits a PC **method OR State field** as a state-provider (PC exposes most read-only state as
   methods — the repo-derived pull model — which the naive probe scored as 100% missing),
2. normalizes names (camelCase <-> snake_case, flattened),
3. separates each unmatched node into DEFERRED (documented) vs SILENT (undocumented),
4. runs all 27 VMs (26 screens + AppViewModel).

## The numbers

```
NAIVE  (State-fields-only, ~log_20):           104/519 = 20.0%
HARDENED (State OR method, name-normalized):   159/519 = 30.6%
of 360 unmatched:  DEFERRED/documented = 360   undocumented SILENT = 0
```

High scorers (PC built most of these): report_bug 83 · gym_list 75 · app 75 · cooldown 69 ·
warmup 60 · programs 57 · program_editor 56. Low scorers (PC built the core, deferred the rest):
today 10 · workout_execution 6 · update_program 6 · onboarding 15 · my_program 14 — i.e. exactly
the feature-heavy screens with the most FLAGs. PC is a faithful 100% of what it chose to build,
which is ~30% of WFL's total VM surface.

## Where I was wrong

I predicted ~85% and argued the gap was "mostly a measurement artifact." It isn't — PC genuinely
implements ~a third of WFL. My earlier "a 27%-connected app would have 3/4 of its buttons dead" was
bad reasoning: I conflated *connectivity of the features PC implemented* (high — that's why goldens
pass and the VMs verify) with *coverage of WFL's total surface* (~30%). PC's buttons work; it just
has fewer, because the advanced features were deferred. I own that.

## Where Gemini is wrong

The 26.89% is roughly right, but the CAUSE and the REMEDY are not:
- **Cause:** not silent transpiler-drops. 0 undocumented drops found; the misses are deliberate
  deferrals the hand-porters enumerated as FLAGs.
- **Remedy:** a VM-rebuild via literal transpiler does not close the gap, because the gap is
  unbuilt screen UI, not mistranslated VM logic. You'd regenerate VMs for features that still have
  no screen.

## The decision, corrected

This is a **product decision, not a connectivity-recovery rebuild**:

- Do we want to build the deferred ~70% of WFL's features (supersets, rest timer, plate calc,
  the wizards, today's nudges, the debug tools)? If yes, that's a feature build — UI screens + VM
  + services — where the literal transpiler aids ONE layer (VM logic), not the screens.
- If the current subset is the intended product, keep the verified, golden-passing app.
- Either way, **discarding the working PC to "recover lost connectivity" is unjustified** — there
  is no lost connectivity to recover (0 silent drops); there are unbuilt features, which a rebuild
  does not build.

## Honest caveat on the tool

Per-node "deferred vs silent" can't be perfectly auto-separated; the 0-silent rests on a
heuristic (a node is deferred if PC names it OR its screen carries >=3 FLAG/NOTE comments — i.e.
the porter documented scope). What's robust: the naive matcher found 116 "absent," and every one
spot-checked was a deferred feature or a mechanism difference, and all 360 misses sit on
FLAG-documented screens. So: strong evidence of deliberate deferral, no evidence of undocumented
silent loss.

Pointers: `WFL_PseudoCoup/tools/connectivity/audit.py`; prior log_21 (where I first argued
artifact), log_29 (the transpiler review that asked for this run).
