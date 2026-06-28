# Fidelity ledger -- CalibrationEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object CalibrationEngine  ==  class CalibrationEngine + CalibrationEngine=CalibrationEngine()   [object->instance]
- connects(1deg) KT: AutoregulationEngine, ConfidenceTier, MovementPattern, StrengthGainProfile, TrainingExperience
- connects(1deg) PY: AutoregulationEngine, ConfidenceTier, MovementPattern, StrengthGainProfile, TrainingExperience   [match]
- attrs 2/2
  - nested enum class CalibrationMethod  ==  class CalibrationMethod   [attrs 5/5]
  - nested data class CalibrationSeed  ==  class CalibrationSeed   [attrs 3/3]
  - nested data class UntrainedStandard  ==  class UntrainedStandard   [attrs 2/2]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 3
- methods: exact 6 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
