# log_78 — pseudokotlin P1 batch 1: routine tier transpiles + compiles

Date: 2026-06-27
Type: implementation. Continuation of log_77 (P0). First slice of P1 handlers, plus
the WFL-copy task and the "invariant not a goal" correction.

## Done this turn

1. **WFL copy → `WFL_MixingCenter/WFL/`** (separate repo, pushed): source-only copy of
   the WFL Kotlin app (278 .kt, buildable via gradle wrapper, no .git/build). This is
   the working copy to refactor for transpilability, verified by WFL's own tests
   (anti-slop oracle). Upstream `~/Programming/WFL` stays untouched truth. README added.
2. **Correction (PROJECT_MAP §1/§5):** "every Python artifact traces to Kotlin" is an
   **invariant enforced by the map·wrap·fail contract**, NOT a goal — a `— no Kotlin
   source —` row is a defect, not a milestone. Same category error as the old "done"
   definition.
3. **P1 batch 1** — 27 handlers, gate green, real Kotlin → compiling idiomatic Python.

## P1 batch 1 detail

Ported from the donor under map·wrap·fail, **structure-aware**, names verified against
the live grammar (`parse.named_kinds()` = 114). Handlers (27): identifier · this/super ·
number/float/char/string literals (f-string interpolation) · binary · unary (incl. `!!`
drop) · in/is · parenthesized · navigation (**16.dp → dp(16)** via receiver-kind check) ·
call · index · as · if (ternary | if-stmt by shape) · for · while · assignment ·
return · throw · source_file · function_declaration · class_declaration ·
property_declaration.

Verified (`tests/test_nodes.py`, all green): a function with if/else, a class whose
method members resolve to `self.x`, a for-loop with `+=`, and `16.dp → dp(16)` — each
transpiles AND `py_compile`s.

```
class Point(val x: Int, val y: Int) { fun dist(): Int { return x*x + y*y } }
  ->
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def dist(self):
        return self.x * self.x + self.y * self.y
```

## The discipline earned its keep (three bugs the gate/compile caught, not eyeballing)

- **Grammar-name drift:** the donor's grammar used `integer_literal`/`jump_expression`/
  `simple_identifier`; this one uses `number_literal`/`return_expression`+`throw_expression`/
  `identifier`. I added a gate test `test_no_handler_for_unknown_kind` (routed ⊆ grammar)
  that flags any handler targeting a non-existent kind — caught all 22 stale names.
- **Double-classification:** `source_file` was both ROUTED and CONTAINER — the
  consistency test failed until fixed.
- **Descent bugs:** `function_body → block` and `primary_constructor → class_parameters →
  class_parameter` both needed an extra descent the first pass missed; the compile +
  member-resolution goldens caught them.

## Status / next

`coverage.py`: **114 kinds · 27 ROUTED · 39 container · 48 UNROUTED.** The 48 are P1
batch 2 + P2: `when_expression`/`when_entry`, `lambda_literal`, `try_expression`/`catch`/
`finally`, `object_declaration`/`companion_object`/`object_literal`, `range_expression`,
`infix_expression`, `collection_literal`, getters/setters, `secondary_constructor`,
`callable_reference`, type nodes (for annotations), etc. Drive UNROUTED → 0, then P2 runs
the real WFL corpus to surface what only real files exercise.
