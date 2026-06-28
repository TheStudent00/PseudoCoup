# Fidelity ledger -- SampleProgramData

Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read
statically; Python shape read by introspecting the exec'd module. Behaviour is
proven separately by oracle.py; this is the shape/wiring half.

## object SampleProgramData  ==  class SampleProgramData + SampleProgramData=SampleProgramData()   [object->instance]
- connects(1deg) KT: ContractionFocus, DayType, DeloadType, ExerciseSeedData, MacrocycleEntity, MacrocycleGoal, MesocycleEntity, MesocycleStatus, MesocycleType, MicrocycleEntity, MicrocycleStatus, MicrocycleType, ProgramDayEntity, ProgramEntity, ProgramExerciseEntity, ProgramSetEntity, ProgressionType, SampleProgramSpecs, SetType, TrainingExperience, label
- connects(1deg) PY: ContractionFocus, DayType, DeloadType, ExerciseSeedData, MacrocycleEntity, MacrocycleGoal, MesocycleEntity, MesocycleStatus, MesocycleType, MicrocycleEntity, MicrocycleStatus, MicrocycleType, ProgramDayEntity, ProgramEntity, ProgramExerciseEntity, ProgramSetEntity, ProgressionType, SampleProgramSpecs, SetType, TrainingExperience, label   [match]
- attrs 3/3
  - nested data class Bundle  ==  class Bundle   [attrs 7/7]
  - nested class WkX  ==  class WkX   [attrs 7/7]
  - nested class SlotX  ==  class SlotX   [attrs 7/7]
  - nested class DayX  ==  class DayX   [attrs 4/4]

---
## summary
- frames: 1 top + 0 top-level fun · object->instance 1 · nested classes 4
- methods: exact 13 · overload-split 0 · extension-hoist 0 · missing 0
- connectivity (1deg sets match both sides): all frames match
- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)
