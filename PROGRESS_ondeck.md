# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The instrumented data-layer suite is COMPLETE (4/4). The "complete the transpiler / foundation solid" goal
is largely met: all five gates green, grammar fully routed, data layer runs end-to-end. The next phase is
the UI (the plan's step 2) — an architecture call worth confirming before diving in.

- [domain] Broaden runnable coverage — point the oracle at more of the foundation (more repositories / use-cases / unit tests). Running real code is what surfaced the braceless-loop, nested-lambda, and companion-member bugs; more of it will find more. High yield, low risk.
- [ui] Bring one screen into the foundation — the plan's step 2: validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. Confirm the approach first (user's architecture call).
- [extern] Default-import stdlib names — grow kotlin_rt as they surface (several landed with backup/migration: runCatching, synchronized, trimIndent, trimMargin). Low priority, demand-driven.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side).
- [numeric] Unsigned wrappers (UInt/ULong) + `ushr` — DEFERRED: unused anywhere in the foundation today (0 references). Do it only if a UI/new file needs it.

Recently shipped:
- Data layer COMPLETE (4/4 instrumented): MigrationTest green — MigrationTestHelper over sqlite3 recreates each old schema from Room's exported JSON, replays all 39 migrations (v1/v17/v24/v30 → v40), validates the result. Plus the backup round-trip (3/4) before it.
- 4 general transpiler bugs surfaced by running that real code: braceless-loop bodies dropped (74 files), nested-lambda hoist scope, companion-member access, bare `$name` interpolation. Plus receiver-lambda scope functions (apply/with/run).
