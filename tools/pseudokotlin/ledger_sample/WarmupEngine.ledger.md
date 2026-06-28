# Fidelity ledger -- WarmupEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object WarmupEngine  ==  class WarmupEngine + WarmupEngine=WarmupEngine()   [object->instance]
- connects(1deg) KT: AutoregulationEngine, TrainingExperience
- connects(1deg) PY: AutoregulationEngine, TrainingExperience   [match]
- attrs 5/5
  - nested data class WarmupSet  ==  class WarmupSet   [attrs 4/4]
  - nested data class WarmupInput  ==  class WarmupInput   [attrs 7/7]
  - nested data class Rung  ==  class Rung   [attrs 2/2]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 3
- methods: exact 5 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
