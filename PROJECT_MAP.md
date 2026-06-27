# PROJECT_MAP — what is what across ~/Programming

Status: **first pass, 2026-06-26**, written from filesystem + VCS evidence (timestamps,
structure, diffs, READMEs). Where a claim is inferred rather than confirmed it is marked
`(inferred)`. This is the umbrella's index — correct it as we settle the structure. Author:
the dualgraph reviewer/coordinator (see `DevComms/log_66`).

Reason it exists: the WFL→target work spread across several sibling repos and the faithful
"WFL Python" got duplicated and drifted. This is the single place that says where each thing
lives and what it's for.

---

## 1. The intended pipeline

```
WFL (Kotlin)                      the original app — SOURCE OF TRUTH
   │
   │  (A) Kotlin → Python transpiler        "1:1 faithful, API calls in wrappers"
   │      transpiler:  PseudoCoup/tools/transpiler  (+ dynamic_mapper, connectivity)
   │      output:      PseudoCoup/build/literal/  (28 .py — the transpiled Python)
   ▼
WFL Python  (canonical, 1:1 with Kotlin — INVARIANT: nothing in it lacks a Kotlin equivalent)
   │      INTENDED HOME ⇒ ~/Programming/WFL_MixingCenter   (new, currently EMPTY)
   │      seeded from the transpiled Python "before PseudoCoup anything"; the dualgraph
   │      oversight gates it: drive sidebyside.html to ZERO "— no Kotlin source —" rows.
   │      ONLY THEN start swapping in PseudoUI (the partial UI solutions).
   │
   ├─ (B1) Python → Dart   via PseudoDart;  UI kit = PseudoFlutter   ⇒ target port WFL_PseudoCoup
   └─ (B2) Python → Haxe   via PyHaxe;      UI kit = PyHaxeUI(+Android/iOS) ⇒ target port WFL_PyHaxe
```

`PseudoUI` is not a repo — it's the **partial UI solutions** (the `src/ui` screens built on a
target's kit) that get swapped into the WFL Python to make it a runnable app.

---

## 2. WFL pipeline repos (the ones this work touches)

| repo | role | target | status | branch / last-active |
|---|---|---|---|---|
| **WFL** | original Kotlin/Compose app — source of truth | — | reference, read-only | `main` / 2026-06-16 |
| **WFL_MixingCenter** | **intended canonical WFL Python center** (1:1 w/ Kotlin) | none yet | **EMPTY — not yet seeded, not a git repo** | — |
| **WFL_PseudoCoup** | Dart-target port: WFL Python (`src`, 243 .py: engine/domain/data/viewmodel + ui/35) + the **dualgraph oversight tools** | Dart | **most advanced & active**; has the 27 viewmodels | `kit-migration-primitives` / 2026-06-26 |
| **WFL_PyHaxe** | Haxe-target port: WFL Python + Haxe UI | Haxe | older/partial — **no viewmodel layer**; ui differs | `master` / 2026-06-19 |
| **PseudoCoup** (this repo) | umbrella/meta (thesis, decisions, index) **+ the Kotlin→Python transpiler** (`tools/transpiler`, output `build/literal`) + the older mapper sandbox (`core`, `interactive_map`, `runtime_uimap`, `run_mapper.sh`, `uimap`) + DevComms logs + `uimap/sidebyside.html` | — | docs active; K→Py sandbox last 2026-06-25 | `main` / 2026-06-26 |

### The transpiled Python (the MixingCenter seed) — key observation
`PseudoCoup/build/literal/` has **28** transpiled `.py` files. `WFL_PseudoCoup/src` has **243**
hand-built `.py`. So the transpiler covered only a fraction; the rest of the WFL Python was
hand-built in the target port (per DevComms). Seeding WFL_MixingCenter "from the transpiled
Python" therefore starts from the **small faithful core (28)**, not the large hand-built tree —
a decision to confirm (see §5).

---

## 3. Shared toolchain repos

| repo | role | last-active |
|---|---|---|
| **PseudoDart** | Python→Dart linter+transpiler (the Dart target compiler) | 2026-06-24 |
| **PseudoFlutter** | Dart UI kit (the "PseudoFlutter kit"); app writes intent, kit renders | 2026-06-23 |
| **PyHaxe** | Python→Haxe linter+transpiler | 2026-06-17 |
| **PyHaxeUI** / **-Android** / **-iOS** | Haxe UI kit + native Android/iOS kits | 2026-06-19/20 |
| **PseudoSyntax** | disciplined-Python notation/discipline layer `(inferred — has src/)` | 2026-06-24 |

---

## 4. The dualgraph oversight (where "— no Kotlin source —" comes from)

Lives in **`WFL_PseudoCoup/tools/dualgraph/`** (output rendered to
**`PseudoCoup/uimap/sidebyside.html`**). It statically compares each Kotlin screen against its
PC counterpart:
- **kt_only** = Kotlin object with no PC equivalent (rendered `— not built in PC —`).
- **pc_only** = PC object with **no Kotlin source** (rendered **`— no Kotlin source —`**) ← the
  rows the MixingCenter must drive to **zero** for 1:1 faithfulness.
- Plus the edge check (is a matched object wired the same way) added in DevComms log_67–70.

It currently points at **`WFL_PseudoCoup/src/ui`**. For the MixingCenter plan it must be
re-pointed at **WFL_MixingCenter** (see §5). Today it reports 220/451 connectivity with 231
kt_only and a pc_only set — but that is measuring the Dart port's UI, not the MixingCenter.

---

## 5. Current reality vs intended — the mess, and the open decisions

**Confirmed mess:** the faithful WFL Python (which should be ONE canonical source) exists only as
**copies inside the target ports**, and they have **diverged**: of the domain files,
**56 identical · 123 different · 27 only in WFL_PseudoCoup** (the viewmodels). There is no single
source of truth today; WFL_PseudoCoup is merely the furthest along.

**Open decisions (to settle before building):**
1. **Seed source for WFL_MixingCenter** — the 28-file transpiled `build/literal`, or a
   re-run/extended transpilation, or a cleaned extract of WFL_PseudoCoup/src? (User said "starts
   with the transpiled Python, before PseudoCoup anything" ⇒ leaning `build/literal`.)
2. **Re-point the oversight** at WFL_MixingCenter (vs WFL Kotlin) and shift the goal from "close
   kt_only" to **"zero `— no Kotlin source —`"** (pc_only).
3. **Reconcile the 123 diverged domain files** — is the drift intended (target discipline) or
   accidental? Determines whether targets sync FROM the center or keep copies.
4. **Init WFL_MixingCenter as a git repo** (currently a bare empty dir).

---

## 6. Other repos under ~/Programming (appear unrelated to the WFL/PseudoCoup pipeline)

Not characterized in depth; listed for completeness — flag any that ARE related:
`GUI4GUI` / `GUI4GUI-Android` (a GUI editor + Android target), `StressTestingBot`, `ToDo`,
`flutter` (the Flutter SDK checkout), and the math/proof set `Lean`, `MathematicsVisualizer`,
`MathScratchpad`, `LambdaSeriesProof`, `LambdaSNR`.
