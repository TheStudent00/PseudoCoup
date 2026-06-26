# log_43 — the fork, in plain terms: this is a product decision now, not a technical one

Date: 2026-06-25
Type: synthesis / decision aid. Written to make the choice legible, not to push one.

## The one-line version

The transpiler answered its *technical* question — **yes, WFL's Kotlin VM logic maps to faithful,
gate-verified Python.** What's left is a *product* choice: **how much of WFL do you want, and how
automated should the path be?** There are three honest answers, not two.

## What we now actually know (so the ground under the decision is solid)

- The hand-ported PC is **~30% of WFL** — faithful for what it built, golden-passing (log_30).
- The transpiler now turns **all 27 WFL VMs** into valid, instance-shaped Python with **no silent
  drops, enums present, lambdas captured** — i.e. the Kotlin→Python VM mapping is real and objectively
  verifiable (the gate proves it; that was the trust gap you kept naming).
- **But "valid Python" ≠ "runs."** Two things sit between the transpiled VMs and execution:
  1. the **domain layer** they import (entities, DAOs, repositories, engines) isn't on the Python
     side yet;
  2. the **Flow shims are inert** (no real reactivity).
- The **UI (Compose) was never a transpiler job** — that maps to the kit, which already exists for
  PC's screens.

## The three paths

### A — Stop here. Keep PC as the product.
- The transpiler stays a proven tool/artifact; PC ships as its current ~30%.
- **Cost:** ~nothing more. You keep a working, verified, golden-passing app.
- **Forgoes:** WFL's other ~70%, and any auto-sync with the Kotlin source.
- **Right if:** the current subset *is* the intended product.

### B — Full automated pipeline. Resurrect all of WFL through the transpiler.
- Make the output truly run: (1) transpile/stub the **entire data + engine layer** (the biggest
  mechanical surface — roughly half of WFL's 43k LOC), (2) build the **real Flow runtime** (the
  option-(a) reactive library from log_33), (3) still **hand-build the screens** against the kit.
- **Cost:** large — months-scale; the Flow runtime is genuinely new engineering.
- **Buys:** potentially *all* of WFL, mechanically kept **in sync** with the evolving Kotlin source,
  with reactive connectivity preserved literally.
- **Right if:** PC must continuously track a still-changing WFL Kotlin, and literal
  connectivity-preservation is a hard requirement.

### C — Hybrid. Use the transpiler as a hand-port accelerator.
- Don't automate the whole thing. To port a specific deferred WFL feature, run the transpiler on its
  VM to get a faithful skeleton, then hand-finish: drain the few TODOs, wire to PC's existing
  services, lower Flow→synchronous as PC already does, build the screen on the kit.
- **Cost:** incremental, per feature. **No** upfront Flow runtime, **no** full domain transpile.
- **Buys:** much faster hand-porting of the ~70%, on demand, matching PC's existing discipline.
- **Right if:** you want more of WFL but value control + low upfront cost over full automation.

## The pivot insight (this de-risks the whole decision)

The scary, expensive part — **the Flow runtime — is only required for Path B.** A and C keep PC's
synchronous lowering, which the log_30 audit already showed loses no *documented* behavior. So you do
**not** have to commit to the big build to get real value from the transpiler.

## How your original three reasons map onto the paths

You came into this driven by three things:

1. **"Hand-porting is slow / painful."** → **Path C** fixes this directly — the transpiler cuts the
   per-VM grind to a skeleton you finish.
2. **"I can't tell WFL-Kotlin from WFL-PC / can't verify you're not hiding things."** → **Already
   solved, independent of the fork.** The audit (log_30) + the transpiler + the gate are now an
   objective Kotlin↔Python diff. This reason is retired whichever path you pick.
3. **"Preserve connectivity."** → **Only Path B** preserves *reactive* connectivity literally. A and C
   lower it to synchronous pulls — which is exactly what PC does today, and what the audit showed
   keeps all documented behavior. So "connectivity" only forces Path B if you mean the *reactive
   machinery itself*, not the feature wiring.

## So the fork reduces to one prior question

**Do you actually want WFL's deferred ~70% in the product?**
- **No** → Path A.
- **Yes, as a one-time port** → Path C (best value; the transpiler earns its keep without the
  Flow-runtime megaproject).
- **Yes, and PC must keep tracking an evolving WFL Kotlin with reactivity intact** → Path B (the only
  path whose unique payoff — continuous literal sync — justifies its cost).

## My recommendation

Lean **C** unless you can state that "stay continuously in sync with an evolving WFL Kotlin" is a real
requirement — in which case **B**. Default to **A** if the current subset is genuinely the product.
I would not start B's Flow runtime or domain-transpile on momentum alone; it's a deliberate, sizable
commitment, and the other two paths are cheaper for almost every actual goal.

No work taken pending your call. Gate stays green as the regression guard.

Pointers: log_30 (the ~30% audit), log_31/33 (why the layers cost what they cost), log_42 (current
transpiler state).
