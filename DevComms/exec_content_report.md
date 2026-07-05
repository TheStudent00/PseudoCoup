# WorkoutExecutionScreen — last 3 failing components (28/31)

## Outcome: handoff-diagnosis (root cause is in a READ-ONLY layer; no fence edit made)

## The 3 failures all trace to ONE cause
Diff (`layout_diff.py WorkoutExecutionScreen`) flags:
- `FAIL 12`  — compose x=74.7 y=24.2 h=5.2  vs kivy x=64.1 y=39.8 h=1.9
- `MISS 6`   — in compose only
- `MISS 12`  — in compose only

These are **not three independent problems**. They are the two big `ValueAdjuster`
fields of the in-progress set row (`InProgressSetRow`, WorkoutExecutionScreen.kt):
- RPE adjuster value `"6"`   (compose y=221, h=48)
- Reps adjuster value `"12"` (compose y=221, h=48)

Compose renders both. Kivy renders **neither** — the two `MISS` entries are those
values, and the `FAIL 12` is the matcher pairing compose's big adjuster `"12"` with a
leftover set-#2 preview `"12"` because the real one is absent. Fix the value rendering
and all three clear.

(The `XTRA` rows — "General notes…" placeholder and the two off-screen up-next pills at
x=545/717 w=0 — are kivy-only extras beyond the 31 compose components; they do not count
against the 28/31 and are a separate LazyRow-culling matter.)

## Named divergence
Not fixture drift, not a VM code path. The python VM state matches compose exactly
(probed via `seed_fixtures` + `viewmodel_for`):
`pendingReps=12`, `pendingEffortRir=4` (→ `EffortScale.editableValue` = **6**),
`currentSetNumber=1` in-progress. The plain-string copies of the same values render fine
(the top row `"6"`/`"12"` at y=172 PASS).

The failure is in how the adjuster's `BasicTextField` **value** is recorded:

1. `ValueAdjuster` (WorkoutExecutionScreen.kt ~1805) holds its text as a
   `TextFieldValue`: `remember { mutableStateOf(TextFieldValue(text = value)) }`, and
   passes that object as `BasicTextField(value = textFieldValueState, …)`.
2. `TextFieldValue` is a **discard-everything stub** — it is bound to the opaque
   `_UIChain` singleton `_UI` in `runtime/compose_ui.py` (line 77 name list). Proof:
   `TextFieldValue(text='6')` → `<ui>`, and `.text` → `<ui>`. The string `"6"` is
   destroyed at construction and is unrecoverable.
3. The recorder `runtime/compose.py` `_composable` only copies a field's value into
   `node.text` when `isinstance(v, str)` (line 129). A `TextFieldValue` fails that guard,
   so `node.text` stays `None` and the object lands in `node.props["value"]` (the opaque
   stub).
4. The `decorationBox` branch (compose.py 107-121) emits the inner value text as
   `str(_n.text) if _n.text else " "` — with `_n.text = None` it emits a single space,
   which is exactly the empty `BasicTextField` we see in the kivy dump (text=None, w≈4.2px,
   no value child).

So the recorded tree that `kivy_kit` lays out already has the value string erased. The
information is gone before the kit or the fixture can touch it.

## Why no fence fix
Fence = `kivy_kit.py`, `inspect_layout.py` (seed_fixtures), `gen_layout_dumps.py`.
The value is destroyed in `runtime/compose_ui.py` (the `TextFieldValue` stub) and
`runtime/compose.py` (the `isinstance(v, str)`-only value recording) — both READ-ONLY.
`node.props["value"]` holds only the opaque `_UI` stub, so there is no residual string for
a kit-side or fixture-side rule to recover. A kit special-case would be a per-name patch,
not a general fix. STOP-and-diagnose is the correct outcome here.

## Recommended fix (for the runtime owner, outside this fence)
General, one-cause / one-fix, moves every `TextFieldValue`-backed `BasicTextField`:
1. Make `TextFieldValue` a real lightweight class in `runtime/compose_ui.py` that retains
   `.text` (and `.selection`), instead of aliasing the `_UI` stub.
2. In `runtime/compose.py` `_composable`, extend the value/text branch (line 129) to
   unwrap a `TextFieldValue`: record `node.text = v.text` when `v` exposes `.text`.
Then the `decorationBox` inner (already correct) emits `"6"`/`"12"` at the field box, and
the kit's existing field/decoration path renders them — clearing `MISS 6`, `MISS 12`, and
`FAIL 12` together.

## Verification
- No edits made in-fence → no regression risk to WorkoutCooldownScreen (25/25),
  SessionDetailScreen (14/14), WorkoutSummaryScreen (2/2), SuggestedStretchesScreen (3/3).
- WorkoutExecutionScreen remains 28/31 (90%) pending the read-only runtime fix above.
