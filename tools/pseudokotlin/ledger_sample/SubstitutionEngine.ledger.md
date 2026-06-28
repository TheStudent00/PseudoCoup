# Fidelity ledger -- SubstitutionEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object SubstitutionEngine  ==  class SubstitutionEngine + SubstitutionEngine=SubstitutionEngine()   [object->instance]
- connects(1deg) KT: --
- connects(1deg) PY: --   [match]
- attrs 6/6
  - nested data class ExerciseProfile  ==  class ExerciseProfile   [attrs 7/7]
  - nested data class SubstitutionMatch  ==  class SubstitutionMatch   [attrs 5/5]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 2
- methods: exact 2 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
