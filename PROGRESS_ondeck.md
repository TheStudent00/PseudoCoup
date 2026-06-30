# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

- [data] MigrationTest — wire Room's MigrationTestHelper (schema-version test infrastructure: open the DB at an old version, run the migrations, assert the new schema). Moves data 3/4 → 4/4 (the last instrumented test).
- [numeric] Unsigned wrappers (UInt/ULong) + `ushr` — the one numeric class still bare; closes the last fidelity gap in runtime/numbers.py.
- [extern] Default-import stdlib names (e.g. `runCatching`) — a known gap class the extern checklist doesn't track (it lists explicit imports only); grow kotlin_rt as they surface. (Several landed with backup: runCatching, synchronized, Result.)
- [ui] Bring one screen into the foundation — validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. The plan's step 2.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side).

Recently shipped:
- Backup feature (data 2/4 → 3/4): BackupRepositoryRoundTripTest runs green — full export → clearAllTables → import round-trip over a sqlite3 Cursor + org.json, plus newer-schema rejection. Runtime: Cursor / Result / runCatching / JSON NULL+optJSON / BuildConfig / clearAllTables / version / transactions.
- 3 transpiler bugs the backup test surfaced (each a general fix): braceless-loop bodies were dropped to `pass` (74 files corrected), nested-lambda hoist lost the outer param, companion members weren't reachable from methods.
- Receiver-lambda scope functions (`apply`/`with`/`run`); bare `$name` string interpolation.
