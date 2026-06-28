# PseudoUI 1:1 verify -- gym_list: IR bound to the TRANSPILED viewmodel

The screen's IR (mechanical) interpreted against the TRANSPILED GymListViewModel + entities
+ GymType (1:1 with Kotlin), over the seeded data. The binding spec is now the KOTLIN
expressions themselves (mechanical Kt->Py), not reshaping judgments.

## result
- resolved dynamic values matching hand-built: 4/4
    OK   T: 'Home Gym'
    OK   T: '🏠 Home Gym'
    OK   T: '2 items'
    OK   T: 'Olympic Bar, Adjustable Dumbbe…'
- unresolved IR exprs: 0

## the collapse (the point of path c)
- reshaped spec (kit VM):  10 entries that RE-MAP Compose->kit
    e.g. activeGym?.id==id  ->  item.isActive   (per-row flag)
         gymWithEquipment.equipment  ->  vm.equipment_for(id)   (separate query)
- 1:1 spec (transpiled VM): the SAME 10 expressions, but each is
    the Kotlin source syntactically Kt->Py'd (identity of shape):
         activeGym?.id==id  ->  vm.activeGym.value.id == gw.profile.id
         gymWithEquipment.equipment  ->  gymWithEquipment.equipment   (identity)

## the only non-1:1 seams (fixed, not per-screen)
- reactive shim: Flow/stateIn/viewModelScope/launch -> synchronous pull (~8 lines).
- Room DAO -> InMemoryDb adapter: getAllWithEquipment bundles profile+equipment and
  lifts gymType int -> GymType enum (the storage boundary the kit reshaped away).
