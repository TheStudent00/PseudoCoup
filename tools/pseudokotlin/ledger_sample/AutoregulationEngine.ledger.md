# Fidelity ledger -- AutoregulationEngine

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object AutoregulationEngine  ==  class AutoregulationEngine + AutoregulationEngine=AutoregulationEngine()   [object->instance]
- connects(1deg) KT: ProgressionType, SetType
- connects(1deg) PY: ProgressionType, SetType   [match]
- attrs 18/18
  - overload-split  fun seedWeightFromRelated  ==  seedWeightFromRelated (wrapper) + _seedWeightFromRelated__0, _seedWeightFromRelated__1
  - extension-hoist  fun demoteOneStep  ==  top-level def demoteOneStep
  - nested enum class ConfidenceTier  ==  class ConfidenceTier   [attrs 4/4]
  - nested data class DeloadSessionSummary  ==  class DeloadSessionSummary   [attrs 6/6]
  - nested enum class DeloadRecommendation  ==  class DeloadRecommendation   [attrs 3/3]
  - nested data class ReadinessDay  ==  class ReadinessDay   [attrs 2/2]
  - nested enum class SeedConfidence  ==  class SeedConfidence   [attrs 2/2]
  - nested enum class SeedRelationship  ==  class SeedRelationship   [attrs 14/14]
  - nested data class SetInput  ==  class SetInput   [attrs 5/5]
  - nested data class SuggestionResult  ==  class SuggestionResult   [attrs 7/7]
  - nested data class RepRange  ==  class RepRange   [attrs 2/2]
  - nested enum class RepRangeFlag  ==  class RepRangeFlag   [attrs 2/2]
  - nested enum class MidMicrocycleFlag  ==  class MidMicrocycleFlag   [attrs 2/2]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 11
- methods: exact 21 · overload-split 1 · extension-hoist 1 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
