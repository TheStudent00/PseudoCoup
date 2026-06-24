# log_13 — direction snapshot, and the ingest transpiler (Kotlin → PseudoCoup) as the mirror of PseudoDart

Date: 2026-06-24
Type: direction note. Records where the WFL conversion actually stands after this session,
and a strategic option raised by the owner — kept for the verification trail, and possibly
for use while finishing.

## Bottom line (read this first)

- The WFL screens were authored by **interpretation**, not **transcription** of the original
  Compose tree. Proven on the workout-execution screen against its blueprint. The gap is
  pervasive, not cosmetic (whole sections / menus / sheets / charts / a wizard missing).
- Direction now: re-derive each screen by **faithful transcription** from the Compose
  blueprint. Plan in 5 phases (below). One floor decision settled in log_12: a single
  `define_layer` primitive for modal layers.
- New option on the table (owner-raised): a **weak transpiler, Kotlin/Compose →
  PseudoCoup-Python**. It is the *mirror* of PseudoDart and would make the interpretation
  boundary provable. Recommended scope: a **fidelity tool** (scaffold + verification oracle),
  not a one-shot generator the project is bet on. Decision is the owner's.

## State snapshot (so verification later has its footing)

```
2-way                 original WFL + our Flutter app are BOTH installed APKs on emulator-5554
                      (not screenshots). original = com.sara.workoutforlife;
                      ours = com.example.wfl_pseudocoup_flutter.
diagnosis             screens are interpretations. evidence: workout_execution_screen.py vs
                      execution/WorkoutExecutionScreen.kt + components/WeightRepsInput.kt.
specs                 10 of 30 transcription specs written, read-only, durable, at
                      WFL_PseudoCoup/DevComms/transcribe_specs/.
floor decision        define_layer(id, sup, anchor, style); anchor = center|bottom|trigger.
                      look (scrim dim + panel chrome) is theme-as-data (roles). log_12.
untouched + sound     ported logic (oracles 65/65), the router, the kit's string-id floor.
```

## The 5-phase plan (current)

1. Land `define_layer` in both kits (Flutter `kit.dart`, Kivy `kit.py`) + roles
   (`scrim`/`dialog_card`/`sheet`/`menu`). Prove on the 2-way. ← gate.
2. Finish the spec pass (remaining 20 screens) into `transcribe_specs/`.
3. Build the shared infra once: faithful `widgets.py` sub-composables (each ↔ one Compose
   `@Composable`) + all theme roles. Central, not per-screen-parallel (shared files).
4. Transcribe screens, `workout_execution` first as the proof, reconciled on the 2-way.
5. Verify each: 2-way visual + oracles / smoke / `flutter analyze` / goldens. Charts on
   Progress are the one known fidelity gap (approximate, flagged).

## The option: a weak Kotlin → PseudoCoup ingest transpiler

The project is already a transpiler pipeline. PseudoDart emits PseudoCoup-Python → Dart (a
Python-AST walk in `PseudoDart/src/pseudodart/dart_emitter.py`). The proposed tool is the
mirror — a Kotlin/Compose **CST** walk emitting PseudoCoup-Python — with PseudoCoup-Python
as the pivot language:

```
Kotlin/Compose  --[ingest: the new tool]-->  PseudoCoup-Python  --[PseudoDart]-->  Dart
                                                   |  and runs directly on the Kivy kit
```

Why it is worth recording as a real direction, not a passing idea:

- **It makes interpretation provable.** Machine-emitted code is faithful by construction;
  whatever the tool **flags as unmapped** is the entire interpretation surface — named and
  small. That is the question that started this whole thread, automated.
- **On-brand.** It is the symmetric half the pipeline was missing, not a bolt-on. A Kotlin
  frontend to a Dart backend is exactly the shape of project this already is.

What it gives, and does not (the seam is the **composable body vs the ViewModel/repo**, not
"view vs wiring"):

- **Gives:** the view structure (containers, order, components, labels, weights, roles) **and
  the wiring skeleton** — click attachments (`onClick = { viewModel.logCurrentSet() }` →
  `on_click(id, on_log_set)`), callback names (→ named stubs), state-read bindings
  (`Text(uiState.workoutName)` → `define_text(..., _workout_name(), role)`), control flow
  (`when`/`repeat`/`forEach` that gate the structure), and navigation (destinations resolve
  from `AppNavigation.kt`, the NavHost → `router.navigate(...)`). All of it is inside the
  `@Composable` body, which the tool reads.
- **Does not give:** the handler **bodies** and the `uiState` **computation** — what
  `logCurrentSet()` does, which service produces `workoutName`. Those live in the ViewModel /
  repos the tool doesn't read — and they are exactly the part the existing 30 screens already
  have **correct** (logic ported, oracle-verified). So the tool emits a *wired* screen with
  named stubs, and we bind the stubs to the handlers we already have; the name-mapping
  (`logCurrentSet` ↔ `on_log_set`) is small and the existing screens establish it.
- **Weak caveat:** complex view-local Kotlin (e.g. `totalSets = maxOf(prescribedSets, …)`) is
  flagged, not emitted. Simple reads/clicks transpile; gnarly inline computation flags.

"Weak" is load-bearing:

- It maps the Composables it knows — Column→`define_box V`, Row→`define_box H`,
  Text→`define_text`, LazyColumn→`define_layout_zone scrollable`, `Modifier.weight`→weight,
  `MaterialTheme` style→role — and **flags** the rest: charts, custom composables, gestures,
  animations, remembered state.
- If it grows toward a full Kotlin compiler it costs more than the 30 hand-passes. The
  discipline is: map-or-flag, never interpret silently.

## How the option folds into the plan (does not replace it)

- The shared infra in phase 3 (faithful `widgets.py` + theme roles + `define_layer`) is the
  transpiler's **target vocabulary** — its emit language. Build it first either way; then the
  tool emits against a stable target.
- The 10 specs already written are hand-done transpiler output — they seed the **mapping
  table**. Not wasted.
- Once it runs it is a standing **verification oracle**: diff tool-output vs the finished
  screen; every difference is a transcription bug or a flagged interpretation. A continuous
  fidelity gate, stronger than eyeballing the 2-way. This is the "useful during verification"
  the owner flagged.

## Recommendation (decision is the owner's)

Build it scoped as a **fidelity tool** — scaffold generator + oracle — not a one-shot
generator the project is bet on. Do **not** halt or rebuild: the kit, the live 2-way, the
ported logic, and the specs all stand regardless of whether a screen's view is typed by hand
or emitted. The real variable is appetite: a weak Compose-subset ingest is a genuine if
bounded build (likely `tree-sitter-kotlin` + the mapping table) — worth it if we are
committing to fidelity across all 30 screens, overkill if only a few mattered.

Naming is the owner's. Structurally it is an **ingest frontend** (source → PseudoCoup),
opposite in direction to PseudoDart (PseudoCoup → target). "PseudoPy" is redundant — the
pivot language is just PseudoCoup-Python; the tool is a Kotlin reader for it.

## Verification logic — flag vs disagreement, and two blind spots (refines the oracle)

The oracle surfaces two different signals; keeping them apart is the point.

- **flag** — the tool *cannot map* a construct (chart, gesture, animation, remembered
  state). A "can't certify here" zone. Not itself an interpretation error.
- **disagreement** — the tool maps the construct and emits faithful code, but it *differs*
  from our existing screen.

Most interpretation issues surface as **disagreements, not flags**. Example — the set-editor:
the blueprint's three steppers map cleanly (Column + Row + ValueAdjusters → `define_box` +
…), so the tool emits them with **no flag**, and the gap from our cramped inline version is a
*disagreement*. So:

```
interp issue at a MAPPABLE construct    -> a DISAGREEMENT (tool emits faithful, we differ)
interp issue at an UNMAPPABLE construct -> hides inside a FLAG (tool can't tell)
```

i.e. every interpretation issue surfaces as a flag **or** a disagreement — flags alone would
miss the set-editor. (The owner's "(maybe)" hedge is correctly placed — see the blind spots.)

Two blind spots that **neither** flags nor disagreements catch (the false negatives):

1. **The mapping table itself.** The tool is faithful only relative to its
   Composable→primitive rules, which are human-authored interpretation. A rule wrong *the
   same way we'd have done by hand* gives tool-output == our-output (no disagreement) at a
   mappable construct (no flag) — systematic and invisible. The mapping table therefore gets
   its **own** review against blueprint semantics, separate from per-screen diffs. The oracle
   can't audit its own ruler.
2. **The handler bodies + data computation — NOT the wiring skeleton.** (Correcting an
   earlier overstatement that "the tool can't diff wiring fidelity at all.") The tool *does*
   recover and diff the wiring **skeleton** — click attachments, callback names, state-read
   bindings, control flow, navigation — because that lives in the `@Composable` body. The true
   blind spot is narrower: the handler **bodies** (`logCurrentSet()`'s DB/engine work) and the
   `uiState` **computation**, which live in the ViewModel/repo the tool doesn't read. Those are
   already covered by the **oracles**, so the blind spot is one we've separately closed.

Net: `(flags ∪ disagreements)` = the per-screen attention queue (view **and** wiring
skeleton); **plus** one review it structurally can't give you — the mapping table. The handler
bodies + data computation are the ViewModel/repo layer, already covered by the oracles.

Refines the log_12-era "don't halt or rebuild": the infrastructure (kit, ported logic, 2-way,
specs) stands, but each **disagreement** is a review trigger that resolves three ways — our
screen is wrong (revise it), the tool's mapping rule is wrong (fix the rule), or it is a
legitimate divergence (record why). A disagreement is a signal, not a verdict.
