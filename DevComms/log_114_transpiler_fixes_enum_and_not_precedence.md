# log_114 — transpiler fixes: enum `name`/`ordinal` self-qualify + `!`-precedence/isNullOrBlank

Date: 2026-06-28
Type: transpiler fixes (2 of the 3 gates from log_112/113). Regression guard: the oracle
(`oracle.py --all`) stayed ALL GREEN (11/11 engines) through every change.

## Direct answer

Two real transpiler bugs the UI sequence surfaced are now fixed in the transpiler itself (not
worked around). exercise_detail's unresolved bindings dropped 7 → 3, and the enum-lift workaround
is gone:

```
exercise_detail (AUTO):  unresolved 7 -> 3   (the 3 isNullOrBlank conds now resolve)
  remaining 3: a composable slot param `body` + the `showDeleteDialog` remember-state (benign)
gym_list 10/10 · paths 3/3 · gym_list --emit 10/10   (no regressions)
oracle: ALL GREEN (11/11)
```

## Fix 1 — enum `name`/`ordinal` not qualified with `self.`

`fun MovementPattern.displayName() = name.split('_')…` transpiled to `KtList(name.split…)` —
bare `name`, a NameError, because the implicit enum property wasn't resolved to `self.name`.
The enum's `displayName` is an EXTENSION declared BEFORE the enum, so `_TYPE_FIELDS` wasn't
populated yet. Fix:
- `transpiler.py`: an order-independent pre-scan collects enum type names (`_enum_types`).
- `declarations.py`: an enum class body, and an extension whose receiver is an enum, add
  `name`/`ordinal` to `self._members` → `v_identifier` qualifies them to `self.name`/`self.ordinal`
  (locals still shadow via `_scopes`).

Now `displayName` -> `KtList(self.name.split("_"))…`. This replaced the narrow `name->self.name`
regex workaround in pseudoui_run's `_enum_class` (now removed); exercise_detail still resolves
'Squat · Barbell'.

## Fix 2 — `!recv.f()` precedence + `isNullOrBlank` mapping

`!exercise.instructions.isNullOrBlank()` transpiled to `(not exercise.instructions).isNullOrBlank()`
— the `!` landed on the receiver. Two causes:
- `isNullOrBlank`/`isNullOrEmpty` weren't in the stdlib-method map → added
  (`{r} is None or len({r}.strip()) == 0`).
- The grammar binds a leading `!`/`-`/`+` TIGHTLY (`!a.b.f()` parses as `((!a).b.f)()`) but it
  MEANS the whole postfix expr. The old quirk-handler lifted it one navigation level early, so
  chains embedded a stray `(not …)`. Fix: a `_leading_prefix` helper finds the prefix at the
  chain's leftmost leaf (stopping at parentheses — `(!x).f()` stays explicit); `v_navigation` and
  `v_call` strip the prematurely-lifted prefix off the visited receiver (`_strip_prefix`) and
  re-wrap the whole expression. Verified across direct / chained / deep-chained / unit-ext /
  stdlib-prop / safe-call / explicit-paren cases:

```
!a.isNullOrBlank()                     -> (not (a is None or len(a.strip()) == 0))
!a.b.c.isEmpty()                       -> (not (len(a.b.c) == 0))
!a.b.c.d.isNotEmpty()                  -> (not (len(a.b.c.d) != 0))
(!x).foo()                             -> ((not x)).foo()        # explicit parens preserved
-obj.v.method()                        -> -obj.v.method()
a.b.c() / x?.foo() / 16.dp / xs.size   -> unchanged (no regression)
```

## Remaining

The third gate — a multi-statement `combine` lambda emitted as `combine(…, _lam1)` with no `_lam1`
def (exercise_picker's VM won't construct) — is the hardest (lambda hoisting into an argument
position) and is the next transpiler target. The two fixes here pay off across every screen that
uses an enum `displayName()`/`emoji` or a negated nullable-string check.
