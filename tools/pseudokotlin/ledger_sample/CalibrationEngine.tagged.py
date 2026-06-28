# ≡KT module  java/com/sara/workoutforlife/engine/CalibrationEngine.kt  ->  CalibrationEngine.py
# connects(1deg): AutoregulationEngine, ConfidenceTier, MovementPattern, StrengthGainProfile, TrainingExperience

class CalibrationEngine:
    """≡KT  object CalibrationEngine  -> object->instance
    attrs (2/2): CALIBRATION_MAX_REPS, COLD_START_DISCOUNT
    connects(1deg): AutoregulationEngine, ConfidenceTier, MovementPattern, StrengthGainProfile, TrainingExperience
    """
    def __init__(self):
        self.CALIBRATION_MAX_REPS = 10
        self.COLD_START_DISCOUNT = 0.90
    def seedFromCalibrationSet(self, weightKg, reps, rir, experience):
        """≡KT  fun seedFromCalibrationSet  -> exact"""
        _elv1 = self.e1rmFromSet(weightKg, reps, rir)
        if _elv1 is None:
            return None
        e1rm = _elv1
        if experience == TrainingExperience.BEGINNER:
            return CalibrationSeed(e1rm, ConfidenceTier.MEDIUM, CalibrationMethod.CALIBRATION_SET_NOVICE)
        else:
            return CalibrationSeed(e1rm, ConfidenceTier.HIGH, CalibrationMethod.CALIBRATION_SET_TRAINED)
    def seedFromEnteredOneRepMax(self, e1rmKg):
        """≡KT  fun seedFromEnteredOneRepMax  -> exact"""
        if e1rmKg <= 0.0:
            return None
        return CalibrationSeed(e1rmKg, ConfidenceTier.HIGH, CalibrationMethod.ENTERED_ONE_REP_MAX)
    def coldStartSeed(self, pattern, profile, bodyWeightKg):
        """≡KT  fun coldStartSeed  -> exact"""
        if bodyWeightKg <= 0.0:
            return None
        _elv2 = self.untrainedStandard(pattern)
        if _elv2 is None:
            return None
        std = _elv2
        if profile == StrengthGainProfile.FASTER:
            multiplier = std.higher
        elif profile == StrengthGainProfile.GRADUAL or profile == None:
            multiplier = std.lower
        e1rm = bodyWeightKg * multiplier * self.COLD_START_DISCOUNT
        return CalibrationSeed(e1rm, ConfidenceTier.LOW, CalibrationMethod.COLD_START_STANDARD)
    def seedFromRelated(self, knownE1rmKg, relationship):
        """≡KT  fun seedFromRelated  -> exact"""
        if knownE1rmKg <= 0.0:
            return None
        return CalibrationSeed(e1rmKg=knownE1rmKg * relationship.ratio, tier=ConfidenceTier.LOW, method=CalibrationMethod.CROSS_EXERCISE_SEED)
    def untrainedStandard(self, pattern):
        """≡KT  fun untrainedStandard  -> exact"""
        if pattern == MovementPattern.SQUAT:
            return UntrainedStandard(higher=0.75, lower=0.50)
        elif pattern == MovementPattern.HIP_HINGE:
            return UntrainedStandard(higher=1.00, lower=0.65)
        elif pattern == MovementPattern.PUSH_HORIZONTAL:
            return UntrainedStandard(higher=0.50, lower=0.30)
        elif pattern == MovementPattern.PUSH_VERTICAL:
            return UntrainedStandard(higher=0.35, lower=0.20)
        elif pattern == MovementPattern.PULL_HORIZONTAL:
            return UntrainedStandard(higher=0.50, lower=0.30)
        elif pattern == MovementPattern.PULL_VERTICAL:
            return UntrainedStandard(higher=0.50, lower=0.30)
        else:
            return None
    def e1rmFromSet(self, weightKg, reps, rir):
        """≡KT  fun e1rmFromSet  -> exact"""
        if weightKg <= 0.0 or reps <= 0 or rir < 0:
            return None
        cappedReps = max(min(reps, self.CALIBRATION_MAX_REPS - rir), 1)
        return AutoregulationEngine.computeE1rm(weightKg, cappedReps, rir)
    class CalibrationMethod:
        """≡KT  enum class CalibrationMethod  -> enum class (exact)
        attrs (5/5): ENTERED_ONE_REP_MAX, CALIBRATION_SET_TRAINED, CALIBRATION_SET_NOVICE, COLD_START_STANDARD, CROSS_EXERCISE_SEED
        """
        pass
    CalibrationMethod.ENTERED_ONE_REP_MAX = CalibrationMethod()
    CalibrationMethod.CALIBRATION_SET_TRAINED = CalibrationMethod()
    CalibrationMethod.CALIBRATION_SET_NOVICE = CalibrationMethod()
    CalibrationMethod.COLD_START_STANDARD = CalibrationMethod()
    CalibrationMethod.CROSS_EXERCISE_SEED = CalibrationMethod()
    CalibrationMethod.ENTERED_ONE_REP_MAX.name = "ENTERED_ONE_REP_MAX"
    CalibrationMethod.ENTERED_ONE_REP_MAX.ordinal = 0
    CalibrationMethod.CALIBRATION_SET_TRAINED.name = "CALIBRATION_SET_TRAINED"
    CalibrationMethod.CALIBRATION_SET_TRAINED.ordinal = 1
    CalibrationMethod.CALIBRATION_SET_NOVICE.name = "CALIBRATION_SET_NOVICE"
    CalibrationMethod.CALIBRATION_SET_NOVICE.ordinal = 2
    CalibrationMethod.COLD_START_STANDARD.name = "COLD_START_STANDARD"
    CalibrationMethod.COLD_START_STANDARD.ordinal = 3
    CalibrationMethod.CROSS_EXERCISE_SEED.name = "CROSS_EXERCISE_SEED"
    CalibrationMethod.CROSS_EXERCISE_SEED.ordinal = 4
    CalibrationMethod._entries = KtList([CalibrationMethod.ENTERED_ONE_REP_MAX, CalibrationMethod.CALIBRATION_SET_TRAINED, CalibrationMethod.CALIBRATION_SET_NOVICE, CalibrationMethod.COLD_START_STANDARD, CalibrationMethod.CROSS_EXERCISE_SEED])
    CalibrationMethod.values = staticmethod(lambda: CalibrationMethod._entries)
    CalibrationMethod.entries = CalibrationMethod._entries
    CalibrationMethod.valueOf = staticmethod(lambda s: next(e for e in CalibrationMethod._entries if e.name == s))
    class CalibrationSeed:
        """≡KT  data class CalibrationSeed  -> data class (exact)
        attrs (3/3): method, tier, e1rmKg
        """
        def __init__(self, e1rmKg, tier, method):
            self.e1rmKg = e1rmKg
            self.tier = tier
            self.method = method
    class UntrainedStandard:
        """≡KT  data class UntrainedStandard  -> data class (exact)
        attrs (2/2): lower, higher
        """
        def __init__(self, higher, lower):
            self.higher = higher
            self.lower = lower


CalibrationMethod = CalibrationEngine.CalibrationMethod
CalibrationSeed = CalibrationEngine.CalibrationSeed
UntrainedStandard = CalibrationEngine.UntrainedStandard
CalibrationEngine = CalibrationEngine()
