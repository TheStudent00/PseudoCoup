# ≡KT module  java/com/sara/workoutforlife/engine/PeriodizationEngine.kt  ->  PeriodizationEngine.py
# connects(1deg): MesocycleType, MuscleGroup, PathLever, TrainingExperience

class PeriodizationEngine:
    """≡KT  object PeriodizationEngine  -> object->instance
    attrs (5/5): GENERAL_DEFAULT_LANDMARK, VOLUME_LANDMARKS, DEFAULT_VOLUME_WAVE_START_PCT, VOLUME_EMPHASIS_PCT_DROP, MIN_VOLUME_WAVE_START_PCT
    connects(1deg): MesocycleType, MuscleGroup, PathLever, TrainingExperience
    """
    def __init__(self):
        self.GENERAL_DEFAULT_LANDMARK = VolumeLandmark(mv=6, mev=10, mavLow=12, mavHigh=20, mrv=22)
        self.VOLUME_LANDMARKS = mapOf((MuscleGroup.CHEST, VolumeLandmark(8, 10, 12, 20, 22)), (MuscleGroup.UPPER_BACK, VolumeLandmark(8, 10, 14, 22, 25)), (MuscleGroup.LATS, VolumeLandmark(8, 10, 14, 22, 25)), (MuscleGroup.QUADRICEPS, VolumeLandmark(6, 8, 12, 18, 20)), (MuscleGroup.HAMSTRINGS, VolumeLandmark(4, 6, 10, 16, 20)), (MuscleGroup.GLUTES, VolumeLandmark(0, 4, 4, 12, 16)), (MuscleGroup.SIDE_DELTS, VolumeLandmark(8, 8, 16, 22, 26)), (MuscleGroup.REAR_DELTS, VolumeLandmark(8, 8, 16, 22, 26)), (MuscleGroup.BICEPS, VolumeLandmark(5, 8, 14, 20, 26)), (MuscleGroup.TRICEPS, VolumeLandmark(4, 6, 10, 14, 18)), (MuscleGroup.CALVES, VolumeLandmark(6, 8, 12, 16, 20)), (MuscleGroup.CORE, VolumeLandmark(0, 0, 16, 20, 25)), (MuscleGroup.OBLIQUES, VolumeLandmark(0, 0, 16, 20, 25)), (MuscleGroup.TRAPS, VolumeLandmark(0, 4, 12, 20, 26)), (MuscleGroup.FOREARMS, VolumeLandmark(2, 4, 10, 16, 25)))
        self.DEFAULT_VOLUME_WAVE_START_PCT = 60
        self.VOLUME_EMPHASIS_PCT_DROP = 10
        self.MIN_VOLUME_WAVE_START_PCT = 40
    def landmarkFor(self, muscle):
        """≡KT  fun landmarkFor  -> exact"""
        return (self.VOLUME_LANDMARKS[muscle] if self.VOLUME_LANDMARKS[muscle] is not None else self.GENERAL_DEFAULT_LANDMARK)
    def peakWeeklySets(self, muscle, experience):
        """≡KT  fun peakWeeklySets  -> exact"""
        lm = self.landmarkFor(muscle)
        if experience == TrainingExperience.BEGINNER:
            return lm.mavLow
        elif experience == TrainingExperience.INTERMEDIATE:
            return lm.mavHigh
        elif experience == TrainingExperience.ADVANCED:
            return lm.mrv
    def volumeWaveFraction(self, weekIndex, totalWorkingWeeks, startPct):
        """≡KT  fun volumeWaveFraction  -> exact"""
        start = max(0, min(startPct, 100)) / 100.0
        if totalWorkingWeeks <= 1:
            return 1.0
        last = totalWorkingWeeks - 1
        t = float(max(0, min(weekIndex, last))) / last
        return start + (1.0 - start) * t
    def setTargetForWeek(self, fullSets, weekIndex, totalWorkingWeeks, startPct):
        """≡KT  fun setTargetForWeek  -> exact"""
        if fullSets <= 0:
            return fullSets
        frac = self.volumeWaveFraction(weekIndex, totalWorkingWeeks, startPct)
        return max(roundToInt((fullSets * frac)), 1)
    def nextMesocyclePlan(self, completedType, authoredNextType, primaryLever, secondaryLever, experience):
        """≡KT  fun nextMesocyclePlan  -> exact"""
        type = (authoredNextType if authoredNextType is not None else self.alternate(completedType))
        baseRir = self.baseRirWindow(type)
        rirMin = baseRir[0]
        rirMax = baseRir[1]
        startPct = self.baseVolumeWaveStartPct(type)
        rotateCount = (0 if type == MesocycleType.MAINTENANCE else 1)
        if primaryLever == PathLever.VOLUME:
            startPct = max((startPct - self.VOLUME_EMPHASIS_PCT_DROP), self.MIN_VOLUME_WAVE_START_PCT)
        elif primaryLever == PathLever.RIR or primaryLever == PathLever.INTENSITY:
            rirMin = max((rirMin - 1), 0)
            rirMax = max((rirMax - 1), rirMin)
        elif primaryLever == PathLever.EXERCISE_ROTATION:
            if type != MesocycleType.MAINTENANCE:
                rotateCount = 2
        return MesocyclePlan(type=type, targetRirMin=rirMin, targetRirMax=rirMax, volumeWaveStartPct=startPct, rotateAccessoryCount=rotateCount, emphasizedLever=primaryLever, rationale=self.buildRationale(type, rirMin, rirMax, startPct, rotateCount, primaryLever, secondaryLever, authoredNextType != None))
    def alternate(self, completedType):
        """≡KT  fun alternate  -> exact"""
        if completedType == MesocycleType.ACCUMULATION:
            return MesocycleType.INTENSIFICATION
        elif completedType == MesocycleType.INTENSIFICATION:
            return MesocycleType.ACCUMULATION
        elif completedType == MesocycleType.REALIZATION:
            return MesocycleType.ACCUMULATION
        elif completedType == MesocycleType.MAINTENANCE:
            return MesocycleType.ACCUMULATION
    def baseRirWindow(self, type):
        """≡KT  fun baseRirWindow  -> exact"""
        if type == MesocycleType.ACCUMULATION:
            return (2, 3)
        elif type == MesocycleType.INTENSIFICATION:
            return (1, 2)
        elif type == MesocycleType.REALIZATION:
            return (0, 1)
        elif type == MesocycleType.MAINTENANCE:
            return (2, 3)
    def baseVolumeWaveStartPct(self, type):
        """≡KT  fun baseVolumeWaveStartPct  -> exact"""
        if type == MesocycleType.ACCUMULATION:
            return self.DEFAULT_VOLUME_WAVE_START_PCT
        elif type == MesocycleType.INTENSIFICATION:
            return 70
        elif type == MesocycleType.REALIZATION:
            return 80
        elif type == MesocycleType.MAINTENANCE:
            return 100
    def buildRationale(self, type, rirMin, rirMax, startPct, rotateCount, primary, secondary, authored):
        """≡KT  fun buildRationale  -> exact"""
        typeWord = (((lambda it=None: it.upper())(type.name.lower()[0]) + type.name.lower()[1:]) if type.name.lower() else type.name.lower())
        source = ("curator-authored" if authored else "alternated from the previous block")
        rir = ("$rirMin RIR" if rirMin == rirMax else "$rirMin–$rirMax RIR")
        if rotateCount == 0:
            rotation = "no accessory rotation"
        elif rotateCount == 1:
            rotation = "rotate 1 accessory/muscle"
        else:
            rotation = "rotate 2 accessories/muscle"
        return ("$typeWord block ($source): target $rir, volume wave starts at $startPct% of full working " + str(f"volume, $rotation. Emphasis: {primary.name.lower()} (then {secondary.name.lower()})."))
    class VolumeLandmark:
        """≡KT  data class VolumeLandmark  -> data class (exact)
        attrs (5/5): mrv, mavHigh, mavLow, mev, mv
        """
        def __init__(self, mv, mev, mavLow, mavHigh, mrv):
            self.mv = mv
            self.mev = mev
            self.mavLow = mavLow
            self.mavHigh = mavHigh
            self.mrv = mrv
    class MesocyclePlan:
        """≡KT  data class MesocyclePlan  -> data class (exact)
        attrs (7/7): rationale, emphasizedLever, rotateAccessoryCount, volumeWaveStartPct, targetRirMax, targetRirMin, type
        """
        def __init__(self, type, targetRirMin, targetRirMax, volumeWaveStartPct, rotateAccessoryCount, emphasizedLever, rationale):
            self.type = type
            self.targetRirMin = targetRirMin
            self.targetRirMax = targetRirMax
            self.volumeWaveStartPct = volumeWaveStartPct
            self.rotateAccessoryCount = rotateAccessoryCount
            self.emphasizedLever = emphasizedLever
            self.rationale = rationale


VolumeLandmark = PeriodizationEngine.VolumeLandmark
MesocyclePlan = PeriodizationEngine.MesocyclePlan
PeriodizationEngine = PeriodizationEngine()
