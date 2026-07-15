# PseudoIR X1 → superseded by this PseudoCoup upgrade plan

Status date: 2026-07-14. Planning note only — no code changed to produce it.

## What X1 was

`/home/lucas/Programming/PseudoIR/v2/PLAN.md` (lines 76-77) carried a forward work-unit stub:

> ### X1 — Cross-pollination back to WFL_PseudoCoup (when its Phase 3 closes)
> The V3 transpiler's informal ops (`__range__`, `__spread__`, string-interp parts) migrate to
> registry references; its five ad-hoc hoisting mechanisms collapse into the R4 shared hoister. Do
> NOT do this mid-Phase-3 — it's a refactor of a working pipeline; sequence after WFL's
> zero-analyzer-error milestone.

X1 was described (never executed) as: migrate a V3 transpiler's informal operator markers to
`pseudoir.registry` references, and collapse its ad-hoc hoisting onto the R4 shared hoister
(`pseudoir.hoist`). It was previewed in `/home/lucas/Programming/PseudoIR/v2/pseudoir/INTEGRATION.md`
lines ~195-300 against `pseudocoup/egress/dart.py` (`DartEmitter.visit_BinaryOpNode` at dart.py:2179,
`_hoist_nested_classes` at dart.py:522 — line numbers refer to the VENDORED WFL copy at
`/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/egress/dart.py`, which is 3562 lines; base
PseudoCoup's `dart.py` is 411 lines and has no such methods).

## How this plan supersedes / realizes it

`/home/lucas/Programming/PseudoCoup/.planning/00_Upgrade_Plan.md` is the concrete realization of X1,
but scoped to the BASE PseudoCoup repo (`/home/lucas/Programming/PseudoCoup`) as the primary target
rather than the WFL vendored copy. The correspondence:

- X1's "informal ops → registry references" = this plan's **U2 (registry consultation in egress)**.
- X1's "ad-hoc hoisting → R4 shared hoister" = this plan's **U3 (hoister unification)**.
- Additional units this plan adds beyond X1's original two-sentence scope: **U1** (dependency
  wiring), **U4** (gate integration + the two-gates documentation), **U5** (base-vs-vendored
  divergence reconciliation), **U6** (verification / regression net).

Scope note: X1's original framing targeted the WFL vendored copy's large Dart emitter. This plan
targets BASE PseudoCoup (which is behind the vendored copy in Kotlin ingress / Dart egress — see
the divergence survey in `00_Upgrade_Plan.md`). The vendored copy's improvements are handled
separately by U5 (upstream-or-declare-app-specific), so this plan both realizes X1's registry/hoister
migration AND resolves the divergence X1 did not address.

## The X1 gating condition

X1 said "do NOT do this mid-Phase-3; sequence after WFL's zero-analyzer-error milestone." Per the
WFL Master Plan status, the coverage gate has been kept green (Ingest 0/325, Emit 0/325). This plan
does not touch the WFL vendored copy's live pipeline (U5 upstreams FROM it into base, it does not
edit the vendored copy), so the "don't refactor a working pipeline mid-Phase-3" hazard does not
apply to base PseudoCoup. If Dee wants the same migration applied to the VENDORED Dart emitter, that
is a separate, later effort still governed by X1's original gating condition.
