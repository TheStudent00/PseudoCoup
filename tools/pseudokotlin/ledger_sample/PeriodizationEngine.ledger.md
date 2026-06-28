# Fidelity ledger -- PeriodizationEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object PeriodizationEngine  ==  class PeriodizationEngine + PeriodizationEngine=PeriodizationEngine()   [object->instance]
- connects(1deg) KT: MesocycleType, MuscleGroup, PathLever, TrainingExperience
- connects(1deg) PY: MesocycleType, MuscleGroup, PathLever, TrainingExperience   [match]
- attrs 5/5
  - nested data class VolumeLandmark  ==  class VolumeLandmark   [attrs 5/5]
  - nested data class MesocyclePlan  ==  class MesocyclePlan   [attrs 7/7]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 2
- methods: exact 9 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
