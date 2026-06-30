# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

- [data] BackupRepositoryRoundTripTest — build the backup feature surface (column-introspective JSON dump/restore engine + a Cursor API), and fix the stale constructor arg in the Kotlin copy. Moves the data metric 2/4 → 3/4.
- [data] MigrationTest — wire Room's MigrationTestHelper (schema-version test infrastructure). Moves data 3/4 → 4/4.
- [numeric] Unsigned wrappers (UInt/ULong) + `ushr` — the one numeric class still bare; closes the last fidelity gap in runtime/numbers.py.
- [extern] Default-import stdlib names (e.g. `runCatching`) — a known gap class the extern checklist doesn't track (it lists explicit imports only); grow kotlin_rt as they surface.
- [ui] Bring one screen into the foundation — validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. This is the plan's step 2.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side; the inference/explicit convergence noted in the architecture).
