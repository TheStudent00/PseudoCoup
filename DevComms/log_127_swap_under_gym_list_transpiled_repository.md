# log_127 — swap-under: gym_list runs on the TRANSPILED GymRepository (loop closed)

Date: 2026-06-28
Type: feature — the foundation-integration milestone. Closes the "are the screens on a real floor?"
loop the user raised.

## What

gym_list's generated screen previously bound a transpiled VM to a HAND-WRITTEN repo adapter (`_GymRepo`
calling `GymService`). It now runs on the **TRANSPILED GymRepository** (KtToPy of `GymRepository.kt`) —
the real Kotlin repository LOGIC — over thin DAO bridges to the app store.

Trace now: Compose → transpiled `GymListViewModel` → **transpiled `GymRepository`** → DAO bridges
(`GymProfileDao`/`GymEquipmentDao` → app `GymProfileRepository`/`GymEquipmentRepository` → InMemoryDb).

## Why this is the CORRECT/complete trace for the vertical

Every piece with real Kotlin LOGIC is now transpiled (VM + Repository). The only hand-written part is
the Room→DB bridge — and that is unavoidable: Kotlin `@Dao` interfaces have NO portable body (Room
generates the SQL impl), so there's nothing to transpile there. The bridge IS the right boundary.
What now traces that didn't before: `setActive` (deactivateAll+activate in a withTransaction),
`deleteGym` (getById.first()+delete), `getActive`/`getById`/`getAllWithEquipment` delegation.

## How (reproducible via vendor_gym_list.py)

(a) emits `generated/gym_repository_kt.py` (transpiled GymRepository + `System`/`UUID` shims + entity
imports); (b) replaced the `_GymRepo` adapter with `_ProfileDao`/`_EquipmentDao` bridges (camelCase
Kotlin DAO names, Flow-wrapped lazy reads, int→enum lift, mutations → `invalidate`) +
`_Database.withTransaction(block)=block()`; (c) `make_vm` wires
`GymRepository(_Database(), _ProfileDao(db), _EquipmentDao(db))`. Also synced the script's
`reactive_shim` StateFlow to the State-backed (MutableStateFlow→State) version so a regen does not
revert log_123.

## Verified

- `test_gym_list_gen`: render **10/10** MATCH + all **4 handlers** (incl. delete THROUGH the transpiled
  repo) + re-render after delete. **5/5.**
- app smoke **30/30**.
- proof the transpiled repo is in the path: `GymRepository.__module__ == generated.gym_repository_kt`;
  `setActive` body contains `deactivateAll`; `deleteGym` body contains `getById`.

## Net

One full screen vertical now traces to Kotlin for ALL its logic (VM + Repository), with only the
unavoidable Room→DB boundary hand-bridged. The "are we building on a real floor?" question is answered
for gym_list: **yes — the logic floor is transpiled-from-Kotlin.**
