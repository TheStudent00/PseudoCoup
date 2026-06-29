# log_125 — DI is already solved in KtToPy; the domain is mostly runnable (WFL_MixingCenter is stale)

Date: 2026-06-28
Type: measurement (follows log_124, and substantially UPDATES its gloom). Direction: user chose
"Foundation: start with DI".

## Finding — DI is already correct in the canonical transpiler

The broken `__init__(self): pass` in log_124 was STALE output from the OLD `literal_transpiler` (which
produced WFL_MixingCenter). The canonical transpiler **KtToPy** already handles the `@Inject constructor`
and member references correctly:

```python
def __init__(self, database, profileDao, equipmentDao):
    self.profileDao = profileDao ...
def getAll(self):
    return self.profileDao.getAll()          # bare `profileDao` -> self.profileDao, resolved
```

## Proof — KtToPy's GymRepository RUNS end-to-end

With a small runtime namespace (UUID/System/entity stubs):
`LOAD ok` · `CONSTRUCT (DI wired) ok` · `getAll() -> ['Home Gym','Work Gym']` ·
`createGym -> inserted GymProfileEntity{...}`. Read AND write paths execute.

## Quantified across all 20 repositories (KtToPy + kotlin_rt namespace)

- **LOAD ok: 14/20** (vs `literal_transpiler` / WFL_MixingCenter: ~1/20 had a usable constructor).
- **REAL transpiler bugs: just 2** — `AutoregulationRepository` L83 (syntax), `BackupRepository` L119
  (`continue` not properly in loop).
- The other 4 "failures" are unbound ENTITY names (`CardioSessionEntity`, `DirectiveSource`,
  `EquipmentType`, `ExerciseEntity`) — they resolve once the transpiled entities are imported. NOT bugs.

## So the parse-clean → runnable jump is SMALL and bounded

1. Use **KtToPy**, not `literal_transpiler` — regenerate WFL_MixingCenter (or just the domain).
2. Supply a domain **runtime namespace**: kotlin_rt (exists) + the transpiled entities + `UUID`/`System`/
   `Flow` shims (the `core.flow` analog).
3. Fix the **2 transpiler syntax bugs**.

Then re-measure. The DI restoration the user picked is effectively DONE; the foundation is far closer to
runnable than the "192/254 parse-clean / WFL_MixingCenter" picture implied. log_124's "doesn't run" was
true *of the stale artifact*, not of the canonical transpiler's capability.

## Next concrete step

Fix the 2 syntax bugs, then stand up the domain runtime namespace and re-run the 20-repo probe targeting
load → construct → **call a real method** (not just load), to get the true runnable count.
