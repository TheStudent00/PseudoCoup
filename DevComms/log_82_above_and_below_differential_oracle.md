# log_82 — modeling from above AND below: the four-corner square as a differential oracle

Date: 2026-06-27
Type: **EXPLORATORY RESEARCH — not committed direction.** Conversational thread,
not an implementation. Captured verbatim-in-spirit so it can be re-entered later.

> ⚠️ **THREAD TO PULL ON.** The owner asked to log this in case the main line
> (handler-by-handler pseudokotlin → Python, the log_78–81 arc) stalls. This is a
> reframe of *what the transpiler is for*, not a new transpiler. If the main line is
> going fine, ignore this. If it isn't, start here.

---

## The seed idea (owner's, sharpened)

Don't model the Kt→Py mapping from one side. Model it from **above** (the two
high-level languages, whose structure we know) **and below** (the shared primitive
floor, which we also know), and let the floor *referee* the two high-level forms
against each other.

This started from a general claim about substrates: every language implementation
lowers to a small **universal operation core** — branch (`if`), call/return,
load/store, integer arithmetic, bitwise+shift (with the signed/unsigned right-shift
split that recurs *everywhere* — `ishr/iushr`, `SAR/SHR`, `ashr/lshr` — because
two's-complement forces it), compare, constant/immediate. ~7 categories, ~30–40 ops,
Turing-complete on its own. CPython bytecode, JVM bytecode, CIL, x86, LLVM IR, Wasm
all share this core and differ only by a *tax*: Python pays a **semantics tax**
(iterators, imports, dynamic dispatch), JVM/CIL an **object-model tax** (vtables,
casts, exceptions, GC refs), x86 a **physical-reality tax** (flags, atomics, SIMD,
interrupts). Wasm/LLVM IR are deliberate attempts to *be the intersection*.

## The four-corner square

```
        Kt Hi  ──────────────►  Py Hi
          │      (mechanized,      ▲
  known   │       minimally        │  derived
          ▼       authored)        │
        Kt Lo  ──────────────►  Py Lo
                (shared floor)
```

- **Kt Hi → Kt Lo** — known (kotlinc / our recorded lowering).
- **Kt Lo → Py Lo** — known *but partial*: the floors share the core-7 and diverge at
  the margins. **This is the only edge where irreducible warp lives.**
- **Kt Hi → Py Hi** — the transpiler. **Mechanized, minimally authored** (owner's
  correction — load-bearing, see below).
- **Py Lo → Py Hi** — derived. Lifting here is **not** ambiguous: in a transpiler the
  Lo is never *orphaned* (unlike decompilation), it carries the provenance we recorded,
  so the lift is a lookup, not a guess. (I got this wrong mid-conversation — claimed
  `when` vs if-chain vs `.map` are unrecoverable from below. They are recoverable
  *because we track the mapping*. The orphaned-binary assumption does not hold here.)

**Three edges known ⇒ the fourth is forced.** The square *closing* (route a construct
Kt Hi → Kt Lo → Py Lo → Py Hi and compare to the top edge) **is the correctness
condition.** Commutes → faithful. Doesn't → a defect localized to one cell.

## Why "mechanized, minimally authored" is the key move

If the top edge were *authored*, it'd be an independent oracle. Because it's
**mechanized**, it's a **second independent route** Kt Hi → Py Hi:

```
  direct  :  Kt Hi ─────────────────────────► Py Hi   (transpiler, AST→AST: idiomatic, fast, silently wrong)
  long way:  Kt Hi → Kt Lo → Py Lo ─────────► Py Hi   (semantics-grounded, idiom-blind)
```

Commutation is non-vacuous **only if the two routes are independent** — i.e. the direct
transpiler does NOT itself pass through the floor. For a source-to-source transpiler it
doesn't, so the square becomes a **differential test between an idiomatic route and a
semantic route.** The direct route is the only one that can be *silently* wrong (it
copies `/`→`/`); the long way is what catches it.

**"Minimally authored" = the authoring surface is exactly the handlers where the two
routes need reconciliation** — lambda-hoist (log_80), object/companion/init (log_81),
int-div. Those are the cells composition can't settle alone; everything else composes
for free. *This is why the work is a handler list and not a port.*

Caveats the relabel forces out:
- WFL-clean count (130→146→152) is the **direct route's coverage** — certifies
  *compiles*, which is necessary but **weaker than commutes**.
- If the mechanized top edge ever routed through the floor, commutation goes
  tautological and the only referee left is **behavioral** — run both Hi forms, diff
  output. *That is what the goldens / the state-trace oracle (log_80/81) are.*
- Full stack: **the square localizes a divergence; the goldens adjudicate whether there
  was one.** Coverage from the clean count, truth from the goldens.

## Measurement (the working example — real, this turn)

Same app, both sides. Kotlin = `WFL/{app,wear}/src/main/**.kt`. Python projection =
`WFL_PseudoCoup/src/**.py`. Keyword counts are clean; raw operator counts (`/`, arith)
are noisy — trust the constructs, not the operator totals.

| | Kotlin | Python projection |
|---|---|---|
| files / LOC | 261 / **44,040** | 243 / **56,173 (+28%)** |

The **+28% LOC is the warp made physical** — above-floor constructs unfold into extra
Python statements.

**Three-zone taxonomy, with evidence:**

| Zone | Kotlin (measured) | Landed as (Python) | Risk |
|---|---|---|---|
| **1 Direct** (re-spell, semantics survive) | if 1095, else 600, fun 1539, return 547, class 452, while 128, for( 52 | if 3376, def 2601, return 3176, class 511 | none |
| **2 Silent warp** (same token, diff semantics) | Int/Long 716 (wrap@2³¹ vs unbounded), `/` int-div (trunc vs float), `%` sign (trunc vs floor) | `//` only 41, hex masks only 3 → **overflow/int-div mostly DROPPED** | **high — invisible** |
| **3 Structural warp** (no Py primitive → becomes a pattern / dropped) | `?.`488 + `?:`480 + `!!`22 = 990, nullable `T?` 665, when 405, lambda arrows 1511, `.map/.filter/.fold` 376, data class 164, suspend 349, object/companion 149 | `is (not) None` **1152**, match 36 + elif 211, lambda **10**, comprehensions **2**, `@dataclass` **0**, async **gone** | medium — mechanical, lossy |

Cross-checks that make the story (warps are **conserved, not destroyed**):
- null-safety **990 ops + 665 nullable decls → 1152 explicit `is None` checks**: the
  guarantee moved from the type system into runtime statements. Biggest warp by mass.
- lambda **1511 arrows → 10 `lambda`**: ~99% hoisted to named defs (= log_80,
  generalized — Python's expression-only lambda can't hold a statement body).
- when **405 → 36 match + 211 elif**: lost exhaustiveness checking.
- `.map/.filter` **376 → 2 comprehensions**: became explicit `for` (Py for = 1045).
- data class **164 → 0 @dataclass**; suspend **349 → 0 async** (sync by design).

**Headline:** the primitive *floor* maps ~**100%**; the *structural vocabulary* is
≈**60% direct / 40% warp**; the warp is a thin **Zone-2 (silent, dangerous)** sliver +
a fat **Zone-3 (visible, mechanical)** mass. **Your commit history IS the Zone-3
handler list. Zone-2 is conspicuously absent from it — because Zone-2 compiles clean.**
That residue is exactly and only what from-above-alone and from-below-alone each miss,
and exactly what the commuting square catches.

Generalization: the **method** is general (any two Hi forms + a shared Lo → the floor
referees). The **density is the gap between the two languages' guarantee sets**, floor
held constant. Re-target WFL Kt → **Swift** and Zone 3 collapses (optionals, exhaustive
`switch`, value types) while Zone 2 *grows* (Swift traps on overflow where Kt wraps).
60/40 is a property of the Kt↔Py gap, not of WFL.

## If the main line stalls, pull here — concrete first step

Build the **bottom-edge commutation check** as a tiny prototype:
1. Take one WFL function we have on both sides (Kt + Py projection).
2. Lower each to a core-7 trace (the differential oracle, not just a compile target).
3. Diff. **Same op-shape / different values = Zone-2** (the dangerous silent ones —
   int-div, overflow). **Different op-shape = Zone-3** (expected; already handled).

That is the smallest thing that converts this from measured-conceptual into a tool that
sits on top of the core-7 IR and *finds the silent drops the compile gate can't*. It is
the same target as the P4 runtime oracle named in log_81's "Next" — approached from the
semantics side instead of the test side.

## Pointers
- Floor / IR direction: log_18 (IR transpiler architecture), log_12 (modal floor).
- Kt≠Py divergence already observed empirically: log_31.
- The handler arc this reframes: log_78–81 (P1 → lambda hoist → OOP-model pass).
- Verification ladder (tests → state-trace → symbolic): log_80 "Next", log_81 "Next".
