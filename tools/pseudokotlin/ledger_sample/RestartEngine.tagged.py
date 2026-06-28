# ≡KT module  java/com/sara/workoutforlife/engine/RestartEngine.kt  ->  RestartEngine.py
# connects(1deg): ActivityLevel, BodyFeeling, BreakReason, RestartLevel

class RestartEngine:
    """≡KT  object RestartEngine  -> object->instance
    attrs (4/4): COMPOUND_MODIFIER, GAP_PROMPT_THRESHOLD_DAYS, MS_PER_DAY, SEVERE_INJURY_REASONS
    connects(1deg): ActivityLevel, BodyFeeling, BreakReason, RestartLevel
    """
    def __init__(self):
        self.COMPOUND_MODIFIER = 0.95
        self.GAP_PROMPT_THRESHOLD_DAYS = 14
        self.MS_PER_DAY = 86400000
        self.SEVERE_INJURY_REASONS = setOf(BreakReason.INJURY_WITH_IMMOBILIZATION, BreakReason.ILLNESS_SEVERE_BED_REST)
    def compute(self, input):
        """≡KT  fun compute  -> exact"""
        base = self.baseTierMultiplier(input.gapDays)
        reason = self.reasonMultiplier(input.reason)
        activity = self.activityMultiplier(input.activityLevel)
        feeling = self.feelingMultiplier(input.bodyFeeling)
        compound = (self.COMPOUND_MODIFIER if input.isCompound else 1.0)
        raw = base * reason * activity * feeling * compound
        clamped = max(0.35, min(raw, 1.00))
        return RestartOutput(weightMultiplier=clamped, recommendedLevel=self.recommendLevel(input.gapDays, input.reason), rampMicrocycles=self.rampMicrocycles(input.gapDays), breakdown=Breakdown(basePct=roundToInt((base * 100)), reasonPct=roundToInt((reason * 100)), activityPct=roundToInt((activity * 100)), feelingPct=roundToInt((feeling * 100)), compoundPct=roundToInt((compound * 100)), finalPct=roundToInt((clamped * 100))))
    def applyToWeight(self, lastWorkingWeightKg, input, plateSnapKg=2.5):
        """≡KT  fun applyToWeight  -> exact"""
        multiplier = self.compute(input).weightMultiplier
        raw = lastWorkingWeightKg * multiplier
        return (self.snapToPlate(raw, plateSnapKg) if plateSnapKg > 0 else raw)
    def baseTierMultiplier(self, gapDays):
        """≡KT  fun baseTierMultiplier  -> exact"""
        if gapDays < 14:
            return 1.00
        elif gapDays < 28:
            return 0.93
        elif gapDays < 60:
            return 0.88
        elif gapDays < 120:
            return 0.78
        elif gapDays < 180:
            return 0.65
        elif gapDays < 365:
            return 0.55
        else:
            return 0.40
    def reasonMultiplier(self, reason):
        """≡KT  fun reasonMultiplier  -> exact"""
        if reason == BreakReason.VACATION:
            return 1.00
        elif reason == BreakReason.GENERAL_OTHER:
            return 0.97
        elif reason == BreakReason.ILLNESS_MILD:
            return 0.92
        elif reason == BreakReason.ILLNESS_SEVERE_BED_REST:
            return 0.80
        elif reason == BreakReason.INJURY_NO_IMMOBILIZATION:
            return 0.85
        elif reason == BreakReason.INJURY_WITH_IMMOBILIZATION:
            return 0.75
    def activityMultiplier(self, level):
        """≡KT  fun activityMultiplier  -> exact"""
        if level == ActivityLevel.FULLY_SEDENTARY:
            return 0.90
        elif level == ActivityLevel.LIGHT_MOVEMENT:
            return 0.95
        elif level == ActivityLevel.MODERATE:
            return 1.00
        elif level == ActivityLevel.ACTIVE:
            return 1.05
        elif level == ActivityLevel.VERY_ACTIVE:
            return 1.08
    def feelingMultiplier(self, feeling):
        """≡KT  fun feelingMultiplier  -> exact"""
        if feeling == BodyFeeling.ROUGH:
            return 0.90
        elif feeling == BodyFeeling.OK:
            return 0.95
        elif feeling == BodyFeeling.GOOD:
            return 1.00
        elif feeling == BodyFeeling.GREAT:
            return 1.03
    def recommendLevel(self, gapDays, reason):
        """≡KT  fun recommendLevel  -> exact"""
        if gapDays < 14:
            return RestartLevel.CONTINUE
        elif gapDays < 28:
            return RestartLevel.MICROCYCLE_RESTART
        elif gapDays < 90:
            return RestartLevel.MESOCYCLE_RESTART
        elif gapDays < 180 and (reason not in self.SEVERE_INJURY_REASONS):
            return RestartLevel.MESOCYCLE_RESTART
        else:
            return RestartLevel.MACROCYCLE_RESTART
    def rampMicrocycles(self, gapDays):
        """≡KT  fun rampMicrocycles  -> exact"""
        if gapDays < 14:
            return 0
        elif gapDays < 60:
            return 1
        else:
            return 2
    def gapDays(self, lastSessionMs, nowMs):
        """≡KT  fun gapDays  -> exact"""
        return max(int(((nowMs - lastSessionMs) / self.MS_PER_DAY)), 0)
    def shouldPrompt(self, gapDays):
        """≡KT  fun shouldPrompt  -> exact"""
        return gapDays >= self.GAP_PROMPT_THRESHOLD_DAYS
    def snapToPlate(self, weightKg, snapKg):
        """≡KT  fun snapToPlate  -> exact"""
        return roundToInt((weightKg / snapKg)) * snapKg
    class RestartInput:
        """≡KT  data class RestartInput  -> data class (exact)
        attrs (5/5): isCompound, bodyFeeling, activityLevel, reason, gapDays
        """
        def __init__(self, gapDays, reason, activityLevel, bodyFeeling, isCompound=True):
            self.gapDays = gapDays
            self.reason = reason
            self.activityLevel = activityLevel
            self.bodyFeeling = bodyFeeling
            self.isCompound = isCompound
    class RestartOutput:
        """≡KT  data class RestartOutput  -> data class (exact)
        attrs (4/4): breakdown, rampMicrocycles, recommendedLevel, weightMultiplier
        """
        def __init__(self, weightMultiplier, recommendedLevel, rampMicrocycles, breakdown):
            self.weightMultiplier = weightMultiplier
            self.recommendedLevel = recommendedLevel
            self.rampMicrocycles = rampMicrocycles
            self.breakdown = breakdown
    class Breakdown:
        """≡KT  data class Breakdown  -> data class (exact)
        attrs (6/6): finalPct, compoundPct, feelingPct, activityPct, reasonPct, basePct
        """
        def __init__(self, basePct, reasonPct, activityPct, feelingPct, compoundPct, finalPct):
            self.basePct = basePct
            self.reasonPct = reasonPct
            self.activityPct = activityPct
            self.feelingPct = feelingPct
            self.compoundPct = compoundPct
            self.finalPct = finalPct


RestartInput = RestartEngine.RestartInput
RestartOutput = RestartEngine.RestartOutput
Breakdown = RestartEngine.Breakdown
RestartEngine = RestartEngine()
