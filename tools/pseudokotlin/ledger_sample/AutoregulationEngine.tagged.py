# ≡KT module  java/com/sara/workoutforlife/engine/AutoregulationEngine.kt  ->  AutoregulationEngine.py
# connects(1deg): ProgressionType, SetType

class AutoregulationEngine:
    """≡KT  object AutoregulationEngine  -> object->instance
    attrs (18/18): MAX_REPS_TO_FAILURE_FOR_E1RM, STRONG_DEVIATION_RATIO, TOUGH_DEVIATION_RATIO, CONFIDENCE_MED_MIN_SESSIONS, CONFIDENCE_HIGH_MIN_SESSIONS, STALE_DAYS, VERY_STALE_DAYS, MIN_STEP_COMPOUND_KG, MIN_STEP_ISOLATION_KG, DELOAD_MIN_SESSIONS, READINESS_LOW_THRESHOLD, DELOAD_SIGNAL_MIN_SESSIONS, ACCEL_COMPOUND_CAP, ACCEL_ISOLATION_CAP, READINESS_GOOD_THRESHOLD, READINESS_TREND_WINDOW, READINESS_TREND_MIN_LOW_SESSIONS, LINEAR_STALL_SESSIONS
    connects(1deg): ProgressionType, SetType
    """
    def __init__(self):
        self.MAX_REPS_TO_FAILURE_FOR_E1RM = 20
        self.STRONG_DEVIATION_RATIO = 1.05
        self.TOUGH_DEVIATION_RATIO = 0.90
        self.CONFIDENCE_MED_MIN_SESSIONS = 3
        self.CONFIDENCE_HIGH_MIN_SESSIONS = 6
        self.STALE_DAYS = 21
        self.VERY_STALE_DAYS = 60
        self.MIN_STEP_COMPOUND_KG = 5.0
        self.MIN_STEP_ISOLATION_KG = 2.5
        self.DELOAD_MIN_SESSIONS = 3
        self.READINESS_LOW_THRESHOLD = 1.0
        self.DELOAD_SIGNAL_MIN_SESSIONS = 2
        self.ACCEL_COMPOUND_CAP = 0.10
        self.ACCEL_ISOLATION_CAP = 0.20
        self.READINESS_GOOD_THRESHOLD = 2
        self.READINESS_TREND_WINDOW = 3
        self.READINESS_TREND_MIN_LOW_SESSIONS = 2
        self.LINEAR_STALL_SESSIONS = 3
    def computeE1rm(self, weightKg, reps, rir):
        """≡KT  fun computeE1rm  -> exact"""
        require(weightKg > 0, (lambda it=None: "weightKg must be positive"))
        require(reps > 0, (lambda it=None: "reps must be positive"))
        require(rir >= 0, (lambda it=None: "rir must be non-negative"))
        repsToFailure = reps + rir
        return weightKg * (1.0 + repsToFailure / 30.0)
    def suggestRawWeight(self, e1rm, targetRir, targetRepsCenter):
        """≡KT  fun suggestRawWeight  -> exact"""
        require(e1rm > 0)
        require(targetRir >= 0)
        require(targetRepsCenter > 0)
        repsToFailure = targetRepsCenter + targetRir
        return e1rm / (1.0 + repsToFailure / 30.0)
    def predictReps(self, e1rm, weightKg, targetRir):
        """≡KT  fun predictReps  -> exact"""
        require(e1rm > 0)
        require(weightKg > 0)
        require(targetRir >= 0)
        repsToFailure = 30.0 * (e1rm / weightKg - 1.0)
        return max(roundToInt((repsToFailure - targetRir)), 0)
    def plateSnap(self, targetKg, availablePlatesKg, barWeightKg=20.0):
        """≡KT  fun plateSnap  -> exact"""
        if (len(availablePlatesKg) == 0) or targetKg <= barWeightKg:
            return barWeightKg
        sorted = availablePlatesKg.filter((lambda it=None: it > 0)).sortedDescending()
        if (len(sorted) == 0):
            return barWeightKg
        targetPerSide = (targetKg - barWeightKg) / 2.0
        floorPerSide = self.greedyFill(targetPerSide, sorted)
        floorTotal = barWeightKg + floorPerSide * 2.0
        smallestPlate = sorted.last()
        ceilingTotal = floorTotal + smallestPlate * 2.0
        return (ceilingTotal if abs(ceilingTotal - targetKg) < abs(floorTotal - targetKg) else floorTotal)
    def roundToIncrement(self, targetKg, increment=2.5):
        """≡KT  fun roundToIncrement  -> exact"""
        require(increment > 0)
        return roundToInt((targetKg / increment)) * increment
    def computeAvgRirDelta(self, sets, targetRir):
        """≡KT  fun computeAvgRirDelta  -> exact"""
        withRir = sets.filter((lambda it=None: it.rir != None))
        if (len(withRir) == 0):
            return None
        return withRir.map((lambda it=None: float((it.rir - targetRir)))).average()
    def suggestNextWeight(self, previousSets, targetRir, targetRepsCenter, availablePlatesKg=emptyList(), barWeightKg=20.0, pathRepRange=None):
        """≡KT  fun suggestNextWeight  -> exact"""
        working = previousSets.filter((lambda it=None: it.entryIndex == 0 and it.setType != SetType.WARMUP))
        usable = working.filter((lambda it=None: it.weightKg > 0 and it.reps != None and it.reps > 0))
        if (len(usable) == 0):
            return None
        best = (usable.firstOrNull((lambda it=None: it.rir != None)) if usable.firstOrNull((lambda it=None: it.rir != None)) is not None else usable.first())
        effectiveRir = (best.rir if best.rir is not None else 2)
        cappedReps = max(min(best.reps, self.MAX_REPS_TO_FAILURE_FOR_E1RM - effectiveRir), 1)
        e1rm = self.computeE1rm(best.weightKg, cappedReps, effectiveRir)
        effectiveRepsCenter = (((lambda it=None: max(it.min, min(targetRepsCenter, it.max)))(pathRepRange) if pathRepRange is not None else None) if ((lambda it=None: max(it.min, min(targetRepsCenter, it.max)))(pathRepRange) if pathRepRange is not None else None) is not None else targetRepsCenter)
        rawWeight = self.suggestRawWeight(e1rm, targetRir, effectiveRepsCenter)
        if (len(availablePlatesKg) != 0):
            snapped = self.plateSnap(rawWeight, availablePlatesKg, barWeightKg)
        else:
            snapped = self.roundToIncrement(rawWeight, increment=2.5)
        rirDelta = self.computeAvgRirDelta(usable, targetRir)
        predictedReps = ((lambda it=None: self.predictReps(e1rm, snapped, targetRir))(pathRepRange) if pathRepRange is not None else None)
        if pathRepRange == None:
            repRangeFlag = None
        elif targetRepsCenter < pathRepRange.min:
            repRangeFlag = RepRangeFlag.BELOW_RANGE
        elif targetRepsCenter > pathRepRange.max:
            repRangeFlag = RepRangeFlag.ABOVE_RANGE
        else:
            repRangeFlag = None
        return SuggestionResult(suggestedWeightKg=snapped, targetRir=targetRir, e1rmKg=e1rm, avgRirDelta=rirDelta, basedOnSets=len(usable), predictedReps=predictedReps, repRangeFlag=repRangeFlag)
    def suggestFromE1rm(self, e1rmKg, targetRir, targetRepsCenter, availablePlatesKg=emptyList(), barWeightKg=20.0, pathRepRange=None):
        """≡KT  fun suggestFromE1rm  -> exact"""
        if e1rmKg <= 0.0 or targetRir < 0 or targetRepsCenter <= 0:
            return None
        effectiveRepsCenter = (((lambda it=None: max(it.min, min(targetRepsCenter, it.max)))(pathRepRange) if pathRepRange is not None else None) if ((lambda it=None: max(it.min, min(targetRepsCenter, it.max)))(pathRepRange) if pathRepRange is not None else None) is not None else targetRepsCenter)
        rawWeight = self.suggestRawWeight(e1rmKg, targetRir, effectiveRepsCenter)
        if (len(availablePlatesKg) != 0):
            snapped = self.plateSnap(rawWeight, availablePlatesKg, barWeightKg)
        else:
            snapped = self.roundToIncrement(rawWeight, increment=2.5)
        predictedReps = ((lambda it=None: self.predictReps(e1rmKg, snapped, targetRir))(pathRepRange) if pathRepRange is not None else None)
        if pathRepRange == None:
            repRangeFlag = None
        elif targetRepsCenter < pathRepRange.min:
            repRangeFlag = RepRangeFlag.BELOW_RANGE
        elif targetRepsCenter > pathRepRange.max:
            repRangeFlag = RepRangeFlag.ABOVE_RANGE
        else:
            repRangeFlag = None
        return SuggestionResult(suggestedWeightKg=snapped, targetRir=targetRir, e1rmKg=e1rmKg, avgRirDelta=None, basedOnSets=0, predictedReps=predictedReps, repRangeFlag=repRangeFlag)
    def detectMidMicrocycleDeviation(self, loggedWeightKg, loggedReps, loggedRir, targetE1rmKg):
        """≡KT  fun detectMidMicrocycleDeviation  -> exact"""
        if targetE1rmKg <= 0.0 or loggedWeightKg <= 0.0 or loggedReps <= 0 or loggedRir < 0:
            return None
        cappedReps = max(min(loggedReps, self.MAX_REPS_TO_FAILURE_FOR_E1RM - loggedRir), 1)
        loggedE1rm = self.computeE1rm(loggedWeightKg, cappedReps, loggedRir)
        ratio = loggedE1rm / targetE1rmKg
        if ratio >= self.STRONG_DEVIATION_RATIO:
            return MidMicrocycleFlag.STRONG_SESSION
        elif ratio <= self.TOUGH_DEVIATION_RATIO:
            return MidMicrocycleFlag.TOUGH_SESSION
        else:
            return None
    def resolveConfidence(self, sessionCount, hasConsistentRir, daysSinceLastSession, isFreshlySeeded=False):
        """≡KT  fun resolveConfidence  -> exact"""
        if isFreshlySeeded or sessionCount < self.CONFIDENCE_MED_MIN_SESSIONS:
            return ConfidenceTier.LOW
        if sessionCount >= self.CONFIDENCE_HIGH_MIN_SESSIONS and hasConsistentRir:
            base = ConfidenceTier.HIGH
        else:
            base = ConfidenceTier.MEDIUM
        return self.applyStaleness(base, daysSinceLastSession)
    def applyDeadband(self, currentKg, suggestedKg, tier):
        """≡KT  fun applyDeadband  -> exact"""
        if currentKg <= 0.0:
            return suggestedKg
        relChange = abs(suggestedKg - currentKg) / currentKg
        return (currentKg if relChange < tier.deadbandFraction else suggestedKg)
    def clampIncreaseToMinStep(self, currentKg, suggestedKg, isCompound, availablePlatesKg=emptyList(), barWeightKg=20.0):
        """≡KT  fun clampIncreaseToMinStep  -> exact"""
        if currentKg <= 0.0 or suggestedKg <= currentKg:
            return suggestedKg
        step = (self.MIN_STEP_COMPOUND_KG if isCompound else self.MIN_STEP_ISOLATION_KG)
        capped = minOf(suggestedKg, currentKg + step)
        if (len(availablePlatesKg) != 0):
            return self.plateSnap(capped, availablePlatesKg, barWeightKg)
        else:
            return self.roundToIncrement(capped, increment=2.5)
    def detectDeloadTrend(self, window):
        """≡KT  fun detectDeloadTrend  -> exact"""
        if len(window) < self.DELOAD_MIN_SESSIONS:
            return DeloadRecommendation.NONE
        recent = window.take(3)
        perfDecrementSessions = recent.count((lambda it=None: it.avgRepsAchieved != None and it.avgRepsExpected != None and it.avgRepsAchieved < it.avgRepsExpected))
        rirCreepSessions = recent.count((lambda it=None: it.avgRir != None and it.targetRir != None and it.avgRir < it.targetRir))
        def _lam1(s):
            ratings = listOfNotNull(s.sleep, s.energy)
            return (len(ratings) != 0) and ratings.average() <= self.READINESS_LOW_THRESHOLD
        readinessLowSessions = recent.count(_lam1)
        signals = 0
        if perfDecrementSessions >= self.DELOAD_SIGNAL_MIN_SESSIONS:
            signals += 1
        if rirCreepSessions >= self.DELOAD_SIGNAL_MIN_SESSIONS:
            signals += 1
        if readinessLowSessions >= self.DELOAD_SIGNAL_MIN_SESSIONS:
            signals += 1
        if signals >= 2:
            return DeloadRecommendation.STRONG
        elif signals == 1:
            return DeloadRecommendation.SOFT_NUDGE
        else:
            return DeloadRecommendation.NONE
    def isReadinessGood(self, sleep, energy):
        """≡KT  fun isReadinessGood  -> exact"""
        return sleep != None and energy != None and sleep >= self.READINESS_GOOD_THRESHOLD and energy >= self.READINESS_GOOD_THRESHOLD
    def accelerateWeight(self, currentWeightKg, suggestedKg, isCompound, tier, readinessGood, availablePlatesKg=emptyList(), barWeightKg=20.0):
        """≡KT  fun accelerateWeight  -> exact"""
        if tier != ConfidenceTier.HIGH or (not readinessGood):
            return None
        if currentWeightKg <= 0.0 or suggestedKg <= currentWeightKg:
            return None
        if self.applyDeadband(currentWeightKg, suggestedKg, tier) == currentWeightKg:
            return None
        cap = (self.ACCEL_COMPOUND_CAP if isCompound else self.ACCEL_ISOLATION_CAP)
        cappedRaw = minOf(suggestedKg, currentWeightKg * (1.0 + cap))
        if (len(availablePlatesKg) != 0):
            return self.plateSnap(cappedRaw, availablePlatesKg, barWeightKg)
        else:
            return self.roundToIncrement(cappedRaw, increment=2.5)
    def resolveGatedWeight(self, currentWeightKg, suggestedKg, isCompound, tier, readinessGood, availablePlatesKg=emptyList(), barWeightKg=20.0):
        """≡KT  fun resolveGatedWeight  -> exact"""
        _let2 = self.accelerateWeight(currentWeightKg=currentWeightKg, suggestedKg=suggestedKg, isCompound=isCompound, tier=tier, readinessGood=readinessGood, availablePlatesKg=availablePlatesKg, barWeightKg=barWeightKg)
        if _let2 is not None:
            it = _let2
            return it
        None
        held = self.applyDeadband(currentWeightKg, suggestedKg, tier)
        if tier == ConfidenceTier.LOW:
            return self.clampIncreaseToMinStep(currentWeightKg, held, isCompound, availablePlatesKg, barWeightKg)
        else:
            return held
    def isReadinessTrendLow(self, sessions):
        """≡KT  fun isReadinessTrendLow  -> exact"""
        if len(sessions) < self.READINESS_TREND_MIN_LOW_SESSIONS:
            return False
        window = sessions.take(self.READINESS_TREND_WINDOW)
        def _lam3(day):
            ratings = listOfNotNull(day.sleep, day.energy)
            return (len(ratings) != 0) and ratings.average() <= self.READINESS_LOW_THRESHOLD
        lowCount = window.count(_lam3)
        return lowCount >= self.READINESS_TREND_MIN_LOW_SESSIONS
    def applyReadinessProgressionHold(self, currentKg, suggestedKg, trendLow):
        """≡KT  fun applyReadinessProgressionHold  -> exact"""
        return (currentKg if trendLow and currentKg > 0.0 and suggestedKg > currentKg else suggestedKg)
    def detectLinearStall(self, method, recentTopWeights, recoveryGood, stallSessions=None):
        """≡KT  fun detectLinearStall  -> exact"""
        if stallSessions is None: stallSessions = self.LINEAR_STALL_SESSIONS
        if method != ProgressionType.LINEAR or (not recoveryGood):
            return False
        if len(recentTopWeights) < stallSessions:
            return False
        window = recentTopWeights.take(stallSessions)
        oldestInWindow = window.last()
        return window.all((lambda it=None: it <= oldestInWindow + 1e-9))
    def _seedWeightFromRelated__0(self, knownWorkingKg, relationship, availablePlatesKg=emptyList(), barWeightKg=20.0):
        return self.seedWeightFromRelated(knownWorkingKg, relationship.ratio, availablePlatesKg, barWeightKg)
    def _seedWeightFromRelated__1(self, knownWorkingKg, ratio, availablePlatesKg=emptyList(), barWeightKg=20.0):
        if knownWorkingKg <= 0.0 or ratio <= 0.0:
            return None
        raw = knownWorkingKg * ratio
        if (len(availablePlatesKg) != 0):
            return self.plateSnap(raw, availablePlatesKg, barWeightKg)
        else:
            return self.roundToIncrement(raw, increment=2.5)
    def seedWeightFromRelated(self, *args, **kwargs):
        """≡KT  fun seedWeightFromRelated (overloaded)  -> overload-split
        impls: seedWeightFromRelated (wrapper) + _seedWeightFromRelated__0, _seedWeightFromRelated__1
        """
        if ((len(args) > 1 and isinstance(args[1], SeedRelationship)) or isinstance(kwargs.get('relationship'), SeedRelationship)):
            return self._seedWeightFromRelated__0(*args, **kwargs)
        return self._seedWeightFromRelated__1(*args, **kwargs)
    def applyStaleness(self, base, daysSinceLastSession):
        """≡KT  fun applyStaleness  -> exact"""
        _elv4 = daysSinceLastSession
        if _elv4 is None:
            return base
        days = _elv4
        if days > self.VERY_STALE_DAYS:
            return ConfidenceTier.LOW
        elif days > self.STALE_DAYS:
            return base.demoteOneStep()
        else:
            return base
    def greedyFill(self, targetPerSide, sortedPlatesDesc):
        """≡KT  fun greedyFill  -> exact"""
        remaining = targetPerSide
        achieved = 0.0
        for plate in sortedPlatesDesc:
            while remaining >= plate - 1e-9:
                achieved += plate
                remaining -= plate
        return achieved
    class ConfidenceTier:
        """≡KT  enum class ConfidenceTier  -> enum class (exact)
        attrs (4/4): deadbandFraction, LOW, MEDIUM, HIGH
        """
        def __init__(self, deadbandFraction):
            self.deadbandFraction = deadbandFraction
    ConfidenceTier.LOW = ConfidenceTier(0.09)
    ConfidenceTier.MEDIUM = ConfidenceTier(0.07)
    ConfidenceTier.HIGH = ConfidenceTier(0.05)
    ConfidenceTier.LOW.name = "LOW"
    ConfidenceTier.LOW.ordinal = 0
    ConfidenceTier.MEDIUM.name = "MEDIUM"
    ConfidenceTier.MEDIUM.ordinal = 1
    ConfidenceTier.HIGH.name = "HIGH"
    ConfidenceTier.HIGH.ordinal = 2
    ConfidenceTier._entries = KtList([ConfidenceTier.LOW, ConfidenceTier.MEDIUM, ConfidenceTier.HIGH])
    ConfidenceTier.values = staticmethod(lambda: ConfidenceTier._entries)
    ConfidenceTier.entries = ConfidenceTier._entries
    ConfidenceTier.valueOf = staticmethod(lambda s: next(e for e in ConfidenceTier._entries if e.name == s))
    class DeloadSessionSummary:
        """≡KT  data class DeloadSessionSummary  -> data class (exact)
        attrs (6/6): energy, sleep, targetRir, avgRir, avgRepsExpected, avgRepsAchieved
        """
        def __init__(self, avgRepsAchieved, avgRepsExpected, avgRir, targetRir, sleep, energy):
            self.avgRepsAchieved = avgRepsAchieved
            self.avgRepsExpected = avgRepsExpected
            self.avgRir = avgRir
            self.targetRir = targetRir
            self.sleep = sleep
            self.energy = energy
    class DeloadRecommendation:
        """≡KT  enum class DeloadRecommendation  -> enum class (exact)
        attrs (3/3): NONE, SOFT_NUDGE, STRONG
        """
        pass
    DeloadRecommendation.NONE = DeloadRecommendation()
    DeloadRecommendation.SOFT_NUDGE = DeloadRecommendation()
    DeloadRecommendation.STRONG = DeloadRecommendation()
    DeloadRecommendation.NONE.name = "NONE"
    DeloadRecommendation.NONE.ordinal = 0
    DeloadRecommendation.SOFT_NUDGE.name = "SOFT_NUDGE"
    DeloadRecommendation.SOFT_NUDGE.ordinal = 1
    DeloadRecommendation.STRONG.name = "STRONG"
    DeloadRecommendation.STRONG.ordinal = 2
    DeloadRecommendation._entries = KtList([DeloadRecommendation.NONE, DeloadRecommendation.SOFT_NUDGE, DeloadRecommendation.STRONG])
    DeloadRecommendation.values = staticmethod(lambda: DeloadRecommendation._entries)
    DeloadRecommendation.entries = DeloadRecommendation._entries
    DeloadRecommendation.valueOf = staticmethod(lambda s: next(e for e in DeloadRecommendation._entries if e.name == s))
    class ReadinessDay:
        """≡KT  data class ReadinessDay  -> data class (exact)
        attrs (2/2): energy, sleep
        """
        def __init__(self, sleep, energy):
            self.sleep = sleep
            self.energy = energy
    class SeedConfidence:
        """≡KT  enum class SeedConfidence  -> enum class (exact)
        attrs (2/2): MEDIUM, LOW
        """
        pass
    SeedConfidence.MEDIUM = SeedConfidence()
    SeedConfidence.LOW = SeedConfidence()
    SeedConfidence.MEDIUM.name = "MEDIUM"
    SeedConfidence.MEDIUM.ordinal = 0
    SeedConfidence.LOW.name = "LOW"
    SeedConfidence.LOW.ordinal = 1
    SeedConfidence._entries = KtList([SeedConfidence.MEDIUM, SeedConfidence.LOW])
    SeedConfidence.values = staticmethod(lambda: SeedConfidence._entries)
    SeedConfidence.entries = SeedConfidence._entries
    SeedConfidence.valueOf = staticmethod(lambda s: next(e for e in SeedConfidence._entries if e.name == s))
    class SeedRelationship:
        """≡KT  enum class SeedRelationship  -> enum class (exact)
        attrs (14/14): confidence, ratio, FLAT_BENCH_TO_CLOSE_GRIP, BARBELL_BENCH_TO_DUMBBELL, FLAT_BENCH_TO_INCLINE, BACK_SQUAT_TO_FRONT_SQUAT, CONVENTIONAL_TO_SUMO_DEADLIFT, CONVENTIONAL_DEADLIFT_TO_RDL, BENCH_TO_OVERHEAD_PRESS, FLAT_BENCH_TO_DECLINE, CONVENTIONAL_DEADLIFT_TO_TRAP_BAR, BARBELL_OHP_TO_DUMBBELL, BARBELL_OHP_TO_PUSH_PRESS, BARBELL_OHP_TO_ARNOLD
        """
        def __init__(self, ratio, confidence):
            self.ratio = ratio
            self.confidence = confidence
    SeedRelationship.FLAT_BENCH_TO_CLOSE_GRIP = SeedRelationship(0.95, SeedConfidence.MEDIUM)
    SeedRelationship.BARBELL_BENCH_TO_DUMBBELL = SeedRelationship(0.78, SeedConfidence.MEDIUM)
    SeedRelationship.FLAT_BENCH_TO_INCLINE = SeedRelationship(0.80, SeedConfidence.LOW)
    SeedRelationship.BACK_SQUAT_TO_FRONT_SQUAT = SeedRelationship(0.85, SeedConfidence.LOW)
    SeedRelationship.CONVENTIONAL_TO_SUMO_DEADLIFT = SeedRelationship(1.00, SeedConfidence.LOW)
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_RDL = SeedRelationship(0.85, SeedConfidence.LOW)
    SeedRelationship.BENCH_TO_OVERHEAD_PRESS = SeedRelationship(0.60, SeedConfidence.LOW)
    SeedRelationship.FLAT_BENCH_TO_DECLINE = SeedRelationship(1.00, SeedConfidence.LOW)
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_TRAP_BAR = SeedRelationship(1.05, SeedConfidence.LOW)
    SeedRelationship.BARBELL_OHP_TO_DUMBBELL = SeedRelationship(0.78, SeedConfidence.LOW)
    SeedRelationship.BARBELL_OHP_TO_PUSH_PRESS = SeedRelationship(1.15, SeedConfidence.LOW)
    SeedRelationship.BARBELL_OHP_TO_ARNOLD = SeedRelationship(0.70, SeedConfidence.LOW)
    SeedRelationship.FLAT_BENCH_TO_CLOSE_GRIP.name = "FLAT_BENCH_TO_CLOSE_GRIP"
    SeedRelationship.FLAT_BENCH_TO_CLOSE_GRIP.ordinal = 0
    SeedRelationship.BARBELL_BENCH_TO_DUMBBELL.name = "BARBELL_BENCH_TO_DUMBBELL"
    SeedRelationship.BARBELL_BENCH_TO_DUMBBELL.ordinal = 1
    SeedRelationship.FLAT_BENCH_TO_INCLINE.name = "FLAT_BENCH_TO_INCLINE"
    SeedRelationship.FLAT_BENCH_TO_INCLINE.ordinal = 2
    SeedRelationship.BACK_SQUAT_TO_FRONT_SQUAT.name = "BACK_SQUAT_TO_FRONT_SQUAT"
    SeedRelationship.BACK_SQUAT_TO_FRONT_SQUAT.ordinal = 3
    SeedRelationship.CONVENTIONAL_TO_SUMO_DEADLIFT.name = "CONVENTIONAL_TO_SUMO_DEADLIFT"
    SeedRelationship.CONVENTIONAL_TO_SUMO_DEADLIFT.ordinal = 4
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_RDL.name = "CONVENTIONAL_DEADLIFT_TO_RDL"
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_RDL.ordinal = 5
    SeedRelationship.BENCH_TO_OVERHEAD_PRESS.name = "BENCH_TO_OVERHEAD_PRESS"
    SeedRelationship.BENCH_TO_OVERHEAD_PRESS.ordinal = 6
    SeedRelationship.FLAT_BENCH_TO_DECLINE.name = "FLAT_BENCH_TO_DECLINE"
    SeedRelationship.FLAT_BENCH_TO_DECLINE.ordinal = 7
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_TRAP_BAR.name = "CONVENTIONAL_DEADLIFT_TO_TRAP_BAR"
    SeedRelationship.CONVENTIONAL_DEADLIFT_TO_TRAP_BAR.ordinal = 8
    SeedRelationship.BARBELL_OHP_TO_DUMBBELL.name = "BARBELL_OHP_TO_DUMBBELL"
    SeedRelationship.BARBELL_OHP_TO_DUMBBELL.ordinal = 9
    SeedRelationship.BARBELL_OHP_TO_PUSH_PRESS.name = "BARBELL_OHP_TO_PUSH_PRESS"
    SeedRelationship.BARBELL_OHP_TO_PUSH_PRESS.ordinal = 10
    SeedRelationship.BARBELL_OHP_TO_ARNOLD.name = "BARBELL_OHP_TO_ARNOLD"
    SeedRelationship.BARBELL_OHP_TO_ARNOLD.ordinal = 11
    SeedRelationship._entries = KtList([SeedRelationship.FLAT_BENCH_TO_CLOSE_GRIP, SeedRelationship.BARBELL_BENCH_TO_DUMBBELL, SeedRelationship.FLAT_BENCH_TO_INCLINE, SeedRelationship.BACK_SQUAT_TO_FRONT_SQUAT, SeedRelationship.CONVENTIONAL_TO_SUMO_DEADLIFT, SeedRelationship.CONVENTIONAL_DEADLIFT_TO_RDL, SeedRelationship.BENCH_TO_OVERHEAD_PRESS, SeedRelationship.FLAT_BENCH_TO_DECLINE, SeedRelationship.CONVENTIONAL_DEADLIFT_TO_TRAP_BAR, SeedRelationship.BARBELL_OHP_TO_DUMBBELL, SeedRelationship.BARBELL_OHP_TO_PUSH_PRESS, SeedRelationship.BARBELL_OHP_TO_ARNOLD])
    SeedRelationship.values = staticmethod(lambda: SeedRelationship._entries)
    SeedRelationship.entries = SeedRelationship._entries
    SeedRelationship.valueOf = staticmethod(lambda s: next(e for e in SeedRelationship._entries if e.name == s))
    class SetInput:
        """≡KT  data class SetInput  -> data class (exact)
        attrs (5/5): entryIndex, setType, rir, reps, weightKg
        """
        def __init__(self, weightKg, reps, rir, setType=SetType.STANDARD, entryIndex=0):
            self.weightKg = weightKg
            self.reps = reps
            self.rir = rir
            self.setType = setType
            self.entryIndex = entryIndex
    class SuggestionResult:
        """≡KT  data class SuggestionResult  -> data class (exact)
        attrs (7/7): repRangeFlag, predictedReps, basedOnSets, avgRirDelta, e1rmKg, targetRir, suggestedWeightKg
        """
        def __init__(self, suggestedWeightKg, targetRir, e1rmKg, avgRirDelta, basedOnSets, predictedReps=None, repRangeFlag=None):
            self.suggestedWeightKg = suggestedWeightKg
            self.targetRir = targetRir
            self.e1rmKg = e1rmKg
            self.avgRirDelta = avgRirDelta
            self.basedOnSets = basedOnSets
            self.predictedReps = predictedReps
            self.repRangeFlag = repRangeFlag
    class RepRange:
        """≡KT  data class RepRange  -> data class (exact)
        attrs (2/2): max, min
        """
        def __init__(self, min, max):
            self.min = min
            self.max = max
            require((1 <= min <= max), (lambda it=None: "invalid rep range $min..$max"))
        def contains(self, reps):
            """≡KT  fun contains  -> exact"""
            return (self.min <= reps <= self.max)
    class RepRangeFlag:
        """≡KT  enum class RepRangeFlag  -> enum class (exact)
        attrs (2/2): BELOW_RANGE, ABOVE_RANGE
        """
        pass
    RepRangeFlag.BELOW_RANGE = RepRangeFlag()
    RepRangeFlag.ABOVE_RANGE = RepRangeFlag()
    RepRangeFlag.BELOW_RANGE.name = "BELOW_RANGE"
    RepRangeFlag.BELOW_RANGE.ordinal = 0
    RepRangeFlag.ABOVE_RANGE.name = "ABOVE_RANGE"
    RepRangeFlag.ABOVE_RANGE.ordinal = 1
    RepRangeFlag._entries = KtList([RepRangeFlag.BELOW_RANGE, RepRangeFlag.ABOVE_RANGE])
    RepRangeFlag.values = staticmethod(lambda: RepRangeFlag._entries)
    RepRangeFlag.entries = RepRangeFlag._entries
    RepRangeFlag.valueOf = staticmethod(lambda s: next(e for e in RepRangeFlag._entries if e.name == s))
    class MidMicrocycleFlag:
        """≡KT  enum class MidMicrocycleFlag  -> enum class (exact)
        attrs (2/2): STRONG_SESSION, TOUGH_SESSION
        """
        pass
    MidMicrocycleFlag.STRONG_SESSION = MidMicrocycleFlag()
    MidMicrocycleFlag.TOUGH_SESSION = MidMicrocycleFlag()
    MidMicrocycleFlag.STRONG_SESSION.name = "STRONG_SESSION"
    MidMicrocycleFlag.STRONG_SESSION.ordinal = 0
    MidMicrocycleFlag.TOUGH_SESSION.name = "TOUGH_SESSION"
    MidMicrocycleFlag.TOUGH_SESSION.ordinal = 1
    MidMicrocycleFlag._entries = KtList([MidMicrocycleFlag.STRONG_SESSION, MidMicrocycleFlag.TOUGH_SESSION])
    MidMicrocycleFlag.values = staticmethod(lambda: MidMicrocycleFlag._entries)
    MidMicrocycleFlag.entries = MidMicrocycleFlag._entries
    MidMicrocycleFlag.valueOf = staticmethod(lambda s: next(e for e in MidMicrocycleFlag._entries if e.name == s))


ConfidenceTier = AutoregulationEngine.ConfidenceTier
DeloadSessionSummary = AutoregulationEngine.DeloadSessionSummary
DeloadRecommendation = AutoregulationEngine.DeloadRecommendation
ReadinessDay = AutoregulationEngine.ReadinessDay
SeedConfidence = AutoregulationEngine.SeedConfidence
SeedRelationship = AutoregulationEngine.SeedRelationship
SetInput = AutoregulationEngine.SetInput
SuggestionResult = AutoregulationEngine.SuggestionResult
RepRange = AutoregulationEngine.RepRange
RepRangeFlag = AutoregulationEngine.RepRangeFlag
MidMicrocycleFlag = AutoregulationEngine.MidMicrocycleFlag
def demoteOneStep(self):
    if self == ConfidenceTier.HIGH:
        return ConfidenceTier.MEDIUM
    elif self == ConfidenceTier.MEDIUM:
        return ConfidenceTier.LOW
    elif self == ConfidenceTier.LOW:
        return ConfidenceTier.LOW
ConfidenceTier.demoteOneStep = demoteOneStep
AutoregulationEngine = AutoregulationEngine()
