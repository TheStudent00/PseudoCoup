# log_113 — general int→enum auto-lift: the recurring enum gate, mechanised

Date: 2026-06-28
Type: milestone. The highest-leverage scaling gate from log_112, generalised.

## Direct answer

The enum content that was unresolved on exercise_detail now resolves — via a GENERAL int→enum lift
driven by the Kotlin entity's field types, not a per-screen hand-lift:

```
exercise_detail (AUTO):  before -> shared 7, hb-only 3, dynamic 3/4, unresolved 7
                          now    -> shared 8, hb-only 2, dynamic 4/5, unresolved 6
  newly resolved:  'Squat · Barbell'   (movementPattern.displayName() · equipmentType.displayName())
  remaining hb-only: '⋮' '♡'  (kit menu/favorite glyphs)   ·  dynamic MISS: a closed-dropdown item
```

gym_list (10/10) and paths (3/3) unchanged — no regression.

## What the lift does (general, entity-driven)

The kit stores enum fields as INTS; the Kotlin code calls `x.displayName()`/`.emoji`. The lift:

1. parses the Kotlin entity (e.g. `ExerciseEntity.kt`) for enum-typed constructor fields —
   `movementPattern: MovementPattern`, `equipmentType: EquipmentType`,
   `primaryMuscleGroups: List<MuscleGroup>`, … (a type is "enum" if `enum class X` exists in `X.kt`);
2. transpiles each enum class once (cached) — they carry `.entries` + `.displayName()` like Kotlin;
3. wraps the kit entity in a proxy that, on access to an enum field, returns
   `EnumCls.entries[int(kitValue)]` (or a list of them) — so `x.displayName()` runs.

No per-screen code: gym_list lifted ONE field (gymType) by hand in its adapter; this lifts ALL of a
screen's entity enums automatically from the Kotlin declarations. (gym_list's adapter could now drop
its hand-lift in favour of `_lift(profile, "GymProfileEntity")`.)

## A third transpiler bug found (worked around narrowly)

The transpiled enum METHOD bodies reference the enum's implicit `name`/`ordinal` properties WITHOUT
`self.` — e.g. `displayName` becomes `return KtList(name.split("_"))…`, raising
`NameError: name 'name'`. The lift produced the correct enum objects, but the method crashed.

Confirmed it's the only bare `name` in a transpiled enum (every stored `.name` uses a dot), so
`_enum_class` qualifies `name`→`self.name` / `ordinal`→`self.ordinal` as a NARROW, documented
workaround. The real fix belongs in the transpiler (qualify implicit enum properties inside member
functions) — the third transpiler gap this sequence surfaced, after `!x.isNullOrBlank()` precedence
(log_112) and the multi-statement `combine` lambda.

## Where this leaves the sequence

The UI generator + its supporting lifts now cover: structure, control flow, transpiled viewmodels,
transpiler-emitted bindings, runnable emit, the representation map, AND the general enum lift. Two
screen shapes verify end-to-end (gym_list list 4/4; exercise_detail detail 4/5 with only glyph/
dropdown residue). The remaining gates are squarely in the TRANSPILER (three concrete bugs) and the
path-(c) app migration. The enum lift was the last big UI-side data-shape lift; from here, broader
coverage is bought by fixing the transpiler bugs (each unblocks many screens) rather than per-screen
work.
