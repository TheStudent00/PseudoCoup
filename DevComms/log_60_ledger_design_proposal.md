# log_60 — DESIGN PROPOSAL (for review): the Kotlin⟷PseudoCoup correspondence LEDGER

Date: 2026-06-26
Type: design proposal. This is the **design-review step** required by log_58 req #5 ("Propose the
design first … Get it reviewed, THEN implement. Do not bulk-implement before the design is approved").
Implementer: Claude. Operating rules: log_55 (siloed, never `--snapshot`, ongoing, no sleight-of-hand,
per-change loop). **Nothing has been implemented yet** — this log carries the plan and two open
decisions for the reviewer to rule on. The eventual implementation report will be a separate log.

## What the ledger must fix (confirmed against live matcher output)

`align.py` reverse-engineers the KT↔PC mapping heuristically and fails where the hand-port renamed an
object. The side-by-side then shows "no Kotlin source" rows that are really false-negatives. Three
seed cases, verified by running `python3 tools/dualgraph/align.py <slug>` today:

```
onboarding:  KT widget:LinearProgressIndicator .FLAG   ⟷  PC progress .progress              [kind alias]
programs:    KT widget:ProgramCard .FLAG (×2)           ⟷  PC widget:program_card (×2)          [kind alias]
paths:       KT button 'Add a second path' *click       ⟷  PC widget:button '+ Add a second path' [per-instance; label differs only by "+ "]
```

## Why the EXISTING rename machinery doesn't cover this

There is already a rename mechanism — `ingest.MappingTable.KNOWN_CUSTOM` / `NEEDS_WIDGET`, consulted in
`kotlin_tree.py:_custom_name` (line 148). It has two limits that ARE the false-negative class:

1. **It only renames a KT custom composable → PC `widget:<name>`.** It cannot express a cross-boundary
   alias like KT `widget:LinearProgressIndicator` → PC **`progress` primitive**: once either side is a
   `widget:`, `align._score` requires `a.kind == b.kind` (align.py:90), so widget↔primitive never pairs.
2. **It is shared with the real transpiler** (kotlin_tree.py header: "the SAME MappingTable the weak
   transpiler uses"). Editing it to fix a *matcher* false-negative would change transpiler behavior —
   wrong layer.

So new correspondences belong in a **matcher-only ledger** consulted by `align.py` BEFORE its
heuristics. This also delivers log_55's directive to stop hand-patching `_score` per rename (the button
fix at align.py:87 is meant to be the last such patch).

## Proposed design

### File: `tools/dualgraph/ledger.json`
Sits next to `align.py`; JSON to match the rest of the toolchain; every entry carries a `why` plus a
Kotlin `ref` (file:line) so the reviewer can confirm each claim **by eye, without running anything**.
Two sections = the two granularities log_58 req #2 requires:

```json
{
  "kind_aliases": [
    {"kt": "widget:LinearProgressIndicator", "pc": "progress",
     "why": "Compose Material linear progress = PC progress primitive",
     "ref": "WFL/.../ui/onboarding/OnboardingScreen.kt:NN"},
    {"kt": "widget:ProgramCard", "pc": "widget:program_card",
     "why": "PC renamed the ProgramCard composable to program_card",
     "ref": "WFL/.../ui/programs/ProgramsScreen.kt:NN"}
  ],
  "instances": [
    {"kt_kind": "button", "kt_label": "Add a second path",
     "pc_kind": "widget:button", "pc_label": "+ Add a second path",
     "why": "same CTA; PC prefixes a literal '+'",
     "ref": "WFL/.../ui/paths/PathsScreen.kt:NN"}
  ]
}
```

### Matcher integration (smallest possible change to `align.py`)
- Load the ledger once at import. **Missing file → empty ledger → zero behavior change**, so the loader
  can land before any entries exist (safe, reviewable in isolation).
- Add `_ledger_score(a, b)` consulted at the **top of `_score`**, before the existing text/early-return
  logic. `_score` is only ever called as `_score(kt, pc)` from `_align_pairs`, so the check is
  directional and unambiguous (a = Kotlin, b = PseudoCoup).
- The existing heuristic passes are **unchanged** — they remain the fallback (log_58 req #3).

### Anti-false-match guards (the no-gaming rails)
- **kind_aliases** fire only when text is compatible — NEVER when both nodes carry literal text that
  differs. Stops a generic alias from wrongly pairing two differently-labeled instances.
- **instances** name the exact labels, so they may override a text mismatch (the whole point of
  'Add a second path' ⟷ '+ Add a second path') — but only for that one recorded pair.
- Scores: per-instance 3.5, kind-alias 3.0 — above weak structural matches, **below** text-exact (4.0),
  so genuine text matches still win and the DP alignment stays correct.

### Seeding plan
1. Capture before-state: `python3 tools/dualgraph/align.py all`.
2. Per screen, find mirror-pairs (a pc_only that mirrors a kt_only).
3. Record ONLY correspondences confirmed against Kotlin source. Start with the three above plus any
   onboarding-step renames I can confirm by reading `OnboardingScreen.kt`.
4. Re-run the FULL per-screen gate: `matched` may rise only via real ledger links and must NOT fall on
   any screen; `pc_only`/`kt_only` shrink only by recorded true renames.
5. Hand off as `DevComms/log_<N>_ledger_*.md` with each entry's KT↔PC justification + the gate
   before/after. I never `--snapshot`; the reviewer ratchets.

### Expected gate effect of the three seeds (each: matched +1, kt_only −1, pc_only −1 on its screen)
- onboarding: matched 8→9, kt_only 34→33, pc_only 3→2 (progress alias)
- programs:   matched 3→5, kt_only 3→1, pc_only 11→9 (ProgramCard ×2)
- paths:      matched 5→6, kt_only 2→1, pc_only 10→9 (Add-a-second-path)
All improvements, no regressions on any screen.

## Cases I will NOT guess (flagged, not seeded blindly)
- **onboarding wizard steps.** PC has only **2** `wizard_step_scaffold` nodes ('Choose your first path',
  "You're all set") vs **8** KT `*Step` composables (Welcome/Experience/TrainingStatus/WeightUnit/
  Equipment/LearnToListenPrompt/PathSelection/ProgramSelection). So MOST of onboarding's 34 kt_only are
  **genuine gaps, not renames.** I will read `OnboardingScreen.kt` to confirm which 1–2 are true
  renames before recording any. No ambiguous step mapping goes in.
- **paths `PathSelectionSheet` is 1:N.** One KT composable that PC expanded into `layer .sheet` +
  `scrim` + `note` + `section_header`. A 1:1 ledger can't fully absorb it — see Decision 2.

## DECISIONS I NEED FROM THE REVIEWER

**Decision 1 — file format.** Default: `ledger.json` as above (matches toolchain, trivial to parse,
`why`/`ref` make it eye-auditable). Alternative: an aligned TSV if you want raw top-to-bottom
scannability over structure. **Pick one.**

**Decision 2 — the paths 1:N sheet.** Default for v1: map `widget:PathSelectionSheet` ⟷ the
representative `layer .sheet`, and LEAVE the explicit scrim/note/section_header as *genuine PC
additions* (they really are extra structure PC made explicit). True 1:N ledger support would be a
later, separate increment. **OK to defer 1:N, or do you want 1:N in v1?**

If the design (JSON, the `_score` integration point, the guards, deferring 1:N) is approved, I implement
the loader + `_score` hook, seed the three confirmed correspondences plus any I can confirm from
`OnboardingScreen.kt`, run the gate, and write the implementation handoff log. I will not snapshot.

Pointers: `tools/dualgraph/align.py` (`_score` at line 77, integration point), `kotlin_tree.py:148`
(`_custom_name` — the existing mapping it must NOT touch), `build_sidebyside.py` (the view this makes
trustworthy), log_58 (the task), log_55 (protocol).
