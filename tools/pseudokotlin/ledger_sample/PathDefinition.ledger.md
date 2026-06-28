# Fidelity ledger -- PathDefinition

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## enum class PathCategory  ==  class PathCategory   [enum class (exact)]
- connects(1deg) KT: displayName
- connects(1deg) PY: displayName   [match]
- attrs 6/6

## data class PathDefinition  ==  class PathDefinition   [data class (exact)]
- connects(1deg) KT: FocusArea, GoalType, PathCategory, PathLever
- connects(1deg) PY: PathCategory, PathLever   [relocated to another frame: FocusArea, GoalType]
- attrs 18/18

---
## summary
- frames: 2 top + 0 top-level fun · object->instance 0 · nested classes 0
- methods: exact 0 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
