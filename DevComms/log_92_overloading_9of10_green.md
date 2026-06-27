# log_92 — method overloading: AutoregulationEngine 59/59, 9/10 engines green

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_91.

## 9/10 engines green; 148/151 methods; 0 FAILs

Method overloading — the last AutoregulationEngine blocker — is done, and it's a general
feature. Kotlin same-name/different-signature methods (Python keeps only the last `def`)
are rendered as `_name__i` impls plus a wrapper `name(self, *args, **kwargs)` that
dispatches by the runtime type at the first param position where the signatures differ
(domain-class guards before primitives; the last variant is the fallback). The two
`seedWeightFromRelated` overloads (2nd param `SeedRelationship` vs `Double`) now resolve,
and variant 1's delegation flows back through the wrapper correctly.

**AutoregulationEngine 57→59/59 — EQUIVALENT both sides (JVM-verified).** The largest
engine (59 methods), now behaviorally identical to the Kotlin.

Green (9/10): AutoregulationEngine, Calibration, CardioRecovery, NotificationTriggers,
PathDefinition, Periodization, Restart, Substitution, Warmup.

## The one wall: SampleProgramData (1/4) — `+=` element-vs-collection needs types

SampleProgramData is a single 320-line deeply-nested data builder. ~16 distinct edge cases
were fixed for it this session (each a general transpiler improvement), but it hits a
genuine **type-inference wall**:

```
groups   += mutableListOf(a, partner)   // List<List<Int>> += List<Int> -> APPEND (1 elem)
programSets += seedSets(...)            // List<T>        += List<T>    -> EXTEND (addAll)
microcycles += micro(...)               // List<T>        += T          -> APPEND
```

Kotlin's `MutableList.plusAssign` is overloaded on `(element: T)` vs `(elements: Iterable<T>)`
and resolved by STATIC TYPE. The runtime `KtList.__iadd__` heuristic (collection RHS →
extend) is correct for the 2nd and 3rd but wrong for the 1st (`List<List<X>> += List<X>`),
and there is no syntactic signal to disambiguate. A runtime element-type sniff fails on the
first add to an empty list-of-lists. Resolving it correctly requires type inference.

Hacking the heuristic would risk a SILENT wrong result — the exact failure mode the
0-FAILs negative-control discipline exists to prevent. So this is a principled stop: the
honest statement is "9/10 engines verified equivalent; the 10th needs type inference for
one Kotlin operator overload."

## Net
From this session: oracle reach 5 → 148 passing methods, 1 → 9 green engines, 0 behavioral
divergences throughout. Six engines cross-checked EQUIVALENT on the JVM (including the
largest). The transpiler now covers a broad, real slice of Kotlin — judged at every step
by runtime behavior, not compile-clean.
