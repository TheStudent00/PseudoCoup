# log_19 — review of the IR pivot (log_18), and a grounded Phase-1 connectivity probe

Date: 2026-06-25
Type: review + prototype. Responds to log_18's "Kotlin → literal Python IR → PseudoCoup"
proposal, corrects its framing, and grounds the debate in a working static probe.

## The direction is right — log_18 found the real architecture

PC was hand-derived from Kotlin by interpretation in one leap, so there's no faithful
intermediate to verify connectivity against. That is the root of the gap/trust problem.
log_18's core move — **separate language translation from paradigm interpretation via a
faithful IR** — is correct, and the `ingest.py` diagnosis is accurate (`KNOWN_CUSTOM` /
`NAV_RESOLUTION` are real hardcoded maps).

## Three framing corrections before anyone builds on it

1. **The IR doesn't ELIMINATE paradigm interpretation — it RELOCATES it to Phase 2.**
   "Phase 1 = zero paradigm shift" is true only for syntax (`class→class`, `when→if/elif`).
   The hard paradigm — `MutableStateFlow` / `combine` / `flatMapLatest` / `@Composable`
   recompose — has NO literal Python; translating it "1:1" requires *deciding* what it
   becomes, and that decision IS the interpretation. It moves into Phase 2 (still a win:
   in-language, ast-based, checkable), it doesn't vanish.

2. **"Mathematically ensure every edge is preserved" is too strong.** Phase 2 deliberately
   reshapes (reactive → State/recompose; `@Composable` → `Screen.build()`) — lossy-by-design
   paradigm work. A reshaping transform can't *guarantee* preservation; the IR makes it
   **checkable** (every edge present to diff against). Reframe: verifiable connectivity, not
   a mathematical guarantee.

3. **"Fully-wired" conflates connectivity with execution.** Phase 1 can be fully-wired for
   *connectivity* (reference edges preserved) without being *executable* (no reactive
   runtime). Scope the IR to **connectivity fidelity, not execution fidelity** — then the
   "rebuild Compose's recompose engine in Python" wall disappears, and you still get the
   verifiable graph you want.

## One factual flag + the big positive it missed

- **PC has no `ComponentManager`** (grepped — doesn't exist). Phase 2's target is the real
  architecture: `Screen.build()` + the kit + the existing `router` + the 27 `viewmodel/*.py`
  with `State`/`recompose`.
- **The Phase 2 transform spec already exists, empirically.** The 26-screen ViewModel rollout
  IS the literal-Python→PC transformation, and its rules held with ZERO exceptions across all
  26 screens incl. the 1311-line one: `MutableStateFlow→State`, `combine/flatMapLatest→method
  read each build`, `viewModelScope/suspend→dropped`, `action→invalidate()`, `init→load()`,
  `@Composable→Screen.build()`. Phase 2 is the most-derisked part, not the unknown.

## tree-sitter feasibility (Gemini's open question): yes, with one caveat

The existing `tree_sitter` + `tree_sitter_kotlin` bindings (already in `ingest`) carry this —
proven by the probe below. Control-flow / classes / expressions are tractable. The roadblock
is **completeness**: a partial literal translator that silently drops unhandled nodes
reintroduces the exact gap that broke `ingest`. It must be complete OR mark untranslatable
nodes explicitly (e.g. coroutines/`Flow`) — never drop silently.

## Grounded prototype: `tools/connectivity/probe.py` (Level 1, static)

Rather than argue, I built the Level-1 check on one screen: treat the Kotlin VM as the
fully-connected REFERENCE (state fields + actions + the screen's wiring are static
references), then VERIFY PC preserves each edge. Result on `report_bug`:

```
STATE fields            5/5  preserved   description, severity, reporterName→reporter_name, …
ACTIONS / derived       6/6  preserved   canSubmit→can_submit, resetSubmission→reset_submission, …
SCREEN→vm action edges  3/5  preserved   ← 2 REAL, NAMED gaps:
     GAP  onReporterNameChange   PC has the vm method; the screen never wires the name field to it
     GAP  resetSubmission        PC has reset_submission; the screen has no "Try again"→reset edge
```

So PC's `report_bug` VM is connectivity-complete (11/11 nodes), but the *screen* drops two
edges the Kotlin screen has — and the probe names them precisely. This is the definitive,
name-level check the dual-tree map could only approximate heuristically. It directly answers
"dishonesty is still possible": the gaps are provable, not asserted.

## Recommendation: sequence it (verify-first), don't big-bang

1. Phase 1 scoped to **connectivity** → the fully-connected Kotlin reference (resolve
   references, skip the runtime). The probe is the seed of this.
2. **Verify the existing hand-built PC** (it passes 65/65 goldens — don't throw it away)
   edge-by-edge → definitively enumerate every connectivity gap, cheaply.
3. Only then consider Phase 2 (transform IR→PC) using the proven rollout rules — as a
   CHECKED transform, edge-by-edge, not a claimed-automatic one.

## Pointers
- probe: `WFL_PseudoCoup/tools/connectivity/probe.py` (run: `python3 tools/connectivity/probe.py [slug]`)
- the proven Phase-2 rules: log_16 (economics), log_17 (the State model + the 6 rules)
- the heuristic predecessor this makes definitive: the uimap dual-tree (`PseudoCoup/uimap/`)
