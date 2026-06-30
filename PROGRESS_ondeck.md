# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

Investigating BackupRepositoryRoundTripTest showed it is NOT a quick wire-up — it sits on a core transpiler
gap. Decomposed into its real prerequisites (in order):

- [transpiler] Receiver-lambda scope functions — `obj.apply { put(x) }` / `with(o){…}` / `run{…}` currently emit a bare `put(x)` with the receiver lost (NameError at runtime). The blocker for backup, and broadly useful (apply is everywhere). Needs care: identifier resolution change, wide blast radius — verify all gates.
- [runtime] Backup feature surface — once apply works: json_rt (JSONArray, JSONObject.NULL, optJSONArray/optJSONObject, toString(indent), keys-chain), an Android Cursor (FIELD_TYPE_*, getType/use/columnNames/getColumnIndex/moveTo*/isNull/getLong/Int/Double/String) over sqlite3, Result + runCatching, a BuildConfig stub, and clearAllTables + .version + begin/set/endTransaction on the raw SupportSQLiteDatabase.
- [data] Stale test arg — add `programSetDao = db.programSetDao()` to BackupRepositoryRoundTripTest; the copy's (and upstream's) instrumented test omits it but the real 9-param constructor requires it. Then re-run datalayer_oracle → data 2/4 → 3/4.
- [data] MigrationTest — wire Room's MigrationTestHelper (schema-version test infrastructure). data 3/4 → 4/4.
- [numeric] Unsigned wrappers (UInt/ULong) + `ushr` — the one numeric class still bare; closes the last fidelity gap in runtime/numbers.py.
- [ui] Bring one screen into the foundation — validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. The plan's step 2.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side).

Recently shipped: bare `$name` string interpolation (was leaking literal `$name` into SQL/log strings — 47 foundation files corrected).
