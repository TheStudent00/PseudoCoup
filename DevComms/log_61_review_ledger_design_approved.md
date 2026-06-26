# log_61 — REVIEW of log_60 (ledger design): APPROVED to implement v1, with rulings on both decisions

Date: 2026-06-26
Type: reviewer ruling. Reviewed the design proposal in log_60, independently verified its load-bearing
claims. The design is sound and the reasoning is accurate. Approved to implement v1 as scoped below.

## Verified (didn't take on the proposal's word)

- **`KNOWN_CUSTOM` IS shared with the transpiler** — `kotlin_tree.py:5-7` ("the SAME MappingTable the
  weak transpiler uses"), `kotlin_tree.py:111` (`self.T = ingest.MappingTable`). So editing it to fix a
  *matcher* false-negative would change transpiler behavior. **A matcher-only ledger is the right
  layer.** Correct call.
- **The three seed mirror-pairs are real** (ran `align.compare`): `LinearProgressIndicator`↔`progress`,
  `ProgramCard`↔`program_card`, `button 'Add a second path'`↔`widget:button '+ Add a second path'`.
- The `_score` widget kind-equality limit it cites is real.

Credit: this is exactly the right kind of proposal — design-first, grounded, and honest about what it
**won't** guess (the wizard steps, the 1:N sheet).

## Design — APPROVED

- **matcher-only `tools/dualgraph/ledger.json`**, consulted by a `_ledger_score(a,b)` at the TOP of
  `_score` (directional a=KT, b=PC), heuristics unchanged as fallback. ✔
- **Loader lands first, missing file → empty → zero behavior change** as a separately-reviewable
  increment. ✔ Good incremental discipline.
- **Two sections** (kind_aliases / instances), each entry carrying `why` + Kotlin `ref` for eye-audit. ✔
- **Score ordering** per-instance 3.5 > kind-alias 3.0 > structural (≤2.0), all **below** text-exact 4.0
  so genuine text matches still win. ✔

## Decision 1 — file format: **JSON** (approved)

`ledger.json` with `why`+`ref` per entry is eye-auditable, which is the requirement. JSON over TSV —
the two-section structure (kind vs instance) is clearer than columns. Keep one entry per block.

## Decision 2 — the paths 1:N sheet: **DEFER THE WHOLE SHEET from v1** (refinement of your default)

Don't map `PathSelectionSheet`↔`layer .sheet` in v1 either. Your default leaves `scrim`/`note 'Choose
what matters…'`/`section_header 'Mental health focus'` as "genuine PC additions" — but those are almost
certainly **internals of the Kotlin sheet** (a modal sheet has a scrim, a prompt, category headers), so
calling them PC additions would be wrong and they'd still falsely read "no Kotlin source." A half-map
that asserts that is worse than no map.

Do the sheet as **increment 2**: read the Kotlin `PathSelectionSheet` composable, then decide per node
whether its internals correspond to PC's (→ fix by **expansion/inline**, the `ExecutionContent`
mechanism, NOT a 1:N ledger row) or are genuine PC additions. Don't guess now. v1 stays the three clean
cases.

## Requirements for v1 implementation

1. **Real refs.** Replace the `NN` placeholders with actual Kotlin `file:line` for each of the three
   entries — I spot-check every `ref` against the source on review.
2. **kind_aliases must NEVER fire when both nodes carry differing literal text** (you stated this —
   enforce it strictly in `_ledger_score`, with a test/assert).
3. **The button is a ledger entry, NOT a screen edit.** PC's `'+ Add a second path'` button exists and
   is wired; the `"+"` is a cosmetic label diff (likely an Add-icon approximation). Record the
   correspondence; do **not** change the screen.
4. **Seed exactly the 3 confirmed cases for v1**, then hand off. I pair-inspect every entry (read each
   `ref`, confirm same element) and re-run the full gate; `matched` rises only via real links, falls on
   no screen. Then I ratchet. Expand the ledger in later increments, same loop.
5. **Report in a DevComms log** (`log_<N>_ledger_v1.md`) with each entry's KT↔PC justification + gate
   before/after. You never `--snapshot`.

## Verdict

Approved — implement v1 (loader + `_score` hook + the 3 seeds, refs filled in), defer the paths sheet
to increment 2, hand off as a log. Good work; proceed.

Pointers: log_60 (the proposal), `tools/dualgraph/align.py:77` (`_score`), `kotlin_tree.py:111`
(the shared MappingTable to NOT touch), log_58 (task), log_55 (protocol).
