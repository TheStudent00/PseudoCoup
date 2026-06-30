# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

BackupRepositoryRoundTripTest is decomposed into its real prerequisites. Receiver-lambdas (the deep blocker)
are now done; the remaining backup work is runtime wiring + the stale test arg.

- [runtime] Backup feature surface — json_rt (JSONArray, JSONObject.NULL, optJSONArray/optJSONObject, toString(indent), keys-chain), an Android Cursor (FIELD_TYPE_*, getType/use/columnNames/getColumnIndex/moveTo*/isNull/getLong/Int/Double/String) over sqlite3, Result + runCatching, a BuildConfig stub, and clearAllTables + .version + begin/set/endTransaction on the raw SupportSQLiteDatabase. apply now emits correctly, so this is the last code-level blocker.
- [data] Stale test arg — add `programSetDao = db.programSetDao()` to BackupRepositoryRoundTripTest; the copy's (and upstream's) instrumented test omits it but the real 9-param constructor requires it. Then re-run datalayer_oracle → data 2/4 → 3/4.
- [data] MigrationTest — wire Room's MigrationTestHelper (schema-version test infrastructure). data 3/4 → 4/4.
- [numeric] Unsigned wrappers (UInt/ULong) + `ushr` — the one numeric class still bare; closes the last fidelity gap in runtime/numbers.py.
- [ui] Bring one screen into the foundation — validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. The plan's step 2.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side).

Recently shipped:
- Receiver-lambda scope functions (`apply`/`with`/`run`): a body's bare member calls/assignments now bind to the receiver (`obj.apply { put(x) }` → `_r.put(x)`), with enclosing members / consts / top-level fns left alone. 5 foundation files corrected; the `apply` blocker for backup is gone.
- bare `$name` string interpolation (was leaking literal `$name` into SQL/log strings — 47 foundation files corrected).
