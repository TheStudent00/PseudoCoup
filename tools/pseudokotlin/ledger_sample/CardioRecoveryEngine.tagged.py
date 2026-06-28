# ≡KT module  java/com/sara/workoutforlife/engine/CardioRecoveryEngine.kt  ->  CardioRecoveryEngine.py
# connects(1deg): CardioIntensity, CardioType, TrainingExperience

class CardioRecoveryEngine:
    """≡KT  object CardioRecoveryEngine  -> object->instance
    attrs (15/15): BASE_ECCENTRIC, BASE_CONCENTRIC, BASE_WALK, INTENSITY_LOW, INTENSITY_MODERATE, INTENSITY_HIGH, DURATION_REFERENCE_MINUTES, DURATION_CAP, FULL_WEIGHT_HOURS, WINDOW_HOURS, FITNESS_SCALE_BEGINNER, FITNESS_SCALE_INTERMEDIATE, FITNESS_SCALE_ADVANCED, ELEVATED_FLAG_THRESHOLD, HIGH_FLAG_THRESHOLD
    connects(1deg): CardioIntensity, CardioType, TrainingExperience
    """
    def __init__(self):
        self.BASE_ECCENTRIC = 1.0
        self.BASE_CONCENTRIC = 0.5
        self.BASE_WALK = 0.25
        self.INTENSITY_LOW = 0.2
        self.INTENSITY_MODERATE = 0.6
        self.INTENSITY_HIGH = 1.0
        self.DURATION_REFERENCE_MINUTES = 40.0
        self.DURATION_CAP = 1.5
        self.FULL_WEIGHT_HOURS = 24.0
        self.WINDOW_HOURS = 72.0
        self.FITNESS_SCALE_BEGINNER = 1.3
        self.FITNESS_SCALE_INTERMEDIATE = 1.0
        self.FITNESS_SCALE_ADVANCED = 0.7
        self.ELEVATED_FLAG_THRESHOLD = 0.4
        self.HIGH_FLAG_THRESHOLD = 0.8
    def baseFor(self, type):
        """≡KT  fun baseFor  -> exact"""
        if type == CardioType.WALK:
            return self.BASE_WALK
        elif type.highEccentricImpact:
            return self.BASE_ECCENTRIC
        else:
            return self.BASE_CONCENTRIC
    def intensityFactor(self, intensity, perceivedRpe=None):
        """≡KT  fun intensityFactor  -> exact"""
        if perceivedRpe != None:
            return self.intensityFromRpe(perceivedRpe)
        if intensity == CardioIntensity.LOW:
            return self.INTENSITY_LOW
        elif intensity == CardioIntensity.MODERATE:
            return self.INTENSITY_MODERATE
        elif intensity == CardioIntensity.HIGH:
            return self.INTENSITY_HIGH
    def intensityFromRpe(self, rpe):
        """≡KT  fun intensityFromRpe  -> exact"""
        clamped = max(0, min(rpe, 10))
        return self.INTENSITY_LOW + (self.INTENSITY_HIGH - self.INTENSITY_LOW) * (clamped / 10.0)
    def durationFactor(self, durationMinutes):
        """≡KT  fun durationFactor  -> exact"""
        if durationMinutes <= 0:
            return 0.0
        return min((durationMinutes / self.DURATION_REFERENCE_MINUTES), self.DURATION_CAP)
    def recencyDecay(self, ageHours):
        """≡KT  fun recencyDecay  -> exact"""
        if ageHours <= self.FULL_WEIGHT_HOURS:
            return 1.0
        elif ageHours >= self.WINDOW_HOURS:
            return 0.0
        else:
            return (self.WINDOW_HOURS - ageHours) / (self.WINDOW_HOURS - self.FULL_WEIGHT_HOURS)
    def fitnessScale(self, experience):
        """≡KT  fun fitnessScale  -> exact"""
        if experience == TrainingExperience.BEGINNER:
            return self.FITNESS_SCALE_BEGINNER
        elif experience == TrainingExperience.INTERMEDIATE:
            return self.FITNESS_SCALE_INTERMEDIATE
        elif experience == TrainingExperience.ADVANCED:
            return self.FITNESS_SCALE_ADVANCED
    def costOf(self, load, experience):
        """≡KT  fun costOf  -> exact"""
        return self.baseFor(load.type) * self.intensityFactor(load.intensity, load.perceivedRpe) * self.durationFactor(load.durationMinutes) * self.recencyDecay(load.ageHours) * self.fitnessScale(experience)
    def recoveryCostByMuscleGroup(self, loads, experience):
        """≡KT  fun recoveryCostByMuscleGroup  -> exact"""
        out = mutableMapOf()
        for load in loads:
            cost = self.costOf(load, experience)
            if cost <= 0.0:
                continue
            for mg in load.affectsMuscleGroups:
                out[mg] = ((out[mg] if out[mg] is not None else 0.0)) + cost
        return out
    def flagFor(self, cost):
        """≡KT  fun flagFor  -> exact"""
        if cost >= self.HIGH_FLAG_THRESHOLD:
            return HighIntensityFlag.HIGH
        elif cost >= self.ELEVATED_FLAG_THRESHOLD:
            return HighIntensityFlag.ELEVATED
        else:
            return HighIntensityFlag.NONE
    def flagForMuscleGroups(self, costByMuscleGroup, muscleGroups):
        """≡KT  fun flagForMuscleGroups  -> exact"""
        maxCost = (muscleGroups.maxOfOrNull((lambda it=None: (costByMuscleGroup[it] if costByMuscleGroup[it] is not None else 0.0))) if muscleGroups.maxOfOrNull((lambda it=None: (costByMuscleGroup[it] if costByMuscleGroup[it] is not None else 0.0))) is not None else 0.0)
        return self.flagFor(maxCost)
    class CardioLoad:
        """≡KT  data class CardioLoad  -> data class (exact)
        attrs (6/6): affectsMuscleGroups, ageHours, durationMinutes, perceivedRpe, intensity, type
        """
        def __init__(self, type, intensity, perceivedRpe, durationMinutes, ageHours, affectsMuscleGroups):
            self.type = type
            self.intensity = intensity
            self.perceivedRpe = perceivedRpe
            self.durationMinutes = durationMinutes
            self.ageHours = ageHours
            self.affectsMuscleGroups = affectsMuscleGroups
    class HighIntensityFlag:
        """≡KT  enum class HighIntensityFlag  -> enum class (exact)
        attrs (3/3): NONE, ELEVATED, HIGH
        """
        pass
    HighIntensityFlag.NONE = HighIntensityFlag()
    HighIntensityFlag.ELEVATED = HighIntensityFlag()
    HighIntensityFlag.HIGH = HighIntensityFlag()
    HighIntensityFlag.NONE.name = "NONE"
    HighIntensityFlag.NONE.ordinal = 0
    HighIntensityFlag.ELEVATED.name = "ELEVATED"
    HighIntensityFlag.ELEVATED.ordinal = 1
    HighIntensityFlag.HIGH.name = "HIGH"
    HighIntensityFlag.HIGH.ordinal = 2
    HighIntensityFlag._entries = KtList([HighIntensityFlag.NONE, HighIntensityFlag.ELEVATED, HighIntensityFlag.HIGH])
    HighIntensityFlag.values = staticmethod(lambda: HighIntensityFlag._entries)
    HighIntensityFlag.entries = HighIntensityFlag._entries
    HighIntensityFlag.valueOf = staticmethod(lambda s: next(e for e in HighIntensityFlag._entries if e.name == s))


CardioLoad = CardioRecoveryEngine.CardioLoad
HighIntensityFlag = CardioRecoveryEngine.HighIntensityFlag
CardioRecoveryEngine = CardioRecoveryEngine()
