# Fidelity ledger -- RestartEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object RestartEngine  ==  class RestartEngine + RestartEngine=RestartEngine()   [object->instance]
- connects(1deg) KT: ActivityLevel, BodyFeeling, BreakReason, RestartLevel
- connects(1deg) PY: ActivityLevel, BodyFeeling, BreakReason, RestartLevel   [match]
- attrs 4/4
  - nested data class RestartInput  ==  class RestartInput   [attrs 5/5]
  - nested data class RestartOutput  ==  class RestartOutput   [attrs 4/4]
  - nested data class Breakdown  ==  class Breakdown   [attrs 6/6]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 3
- methods: exact 11 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
