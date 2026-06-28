# ≡KT module  java/com/sara/workoutforlife/engine/WarmupEngine.kt  ->  WarmupEngine.py
# connects(1deg): AutoregulationEngine, TrainingExperience

class WarmupEngine:
    """≡KT  object WarmupEngine  -> object->instance
    attrs (5/5): LIGHT_BARBELL_FACTOR, LIGHT_ISOLATION_FLOOR_KG, ISOLATION_MAX_RUNGS, EMPTY_BAR_GAP_FACTOR, EPS
    connects(1deg): AutoregulationEngine, TrainingExperience
    """
    def __init__(self):
        self.LIGHT_BARBELL_FACTOR = 1.5
        self.LIGHT_ISOLATION_FLOOR_KG = 12.0
        self.ISOLATION_MAX_RUNGS = 2
        self.EMPTY_BAR_GAP_FACTOR = 1.1
        self.EPS = 1e-6
    def generate(self, input):
        """≡KT  fun generate  -> exact"""
        work = input.workingWeightKg
        if work <= 0.0:
            return emptyList()
        emptyBar = self.needsEmptyBarSet(input)
        ramp = self.rampFor(input)
        if (len(ramp) == 0):
            return (listOf(self.emptyBarSet(input)) if emptyBar else emptyList())
        sets = mutableListOf()
        if emptyBar:
            sets += self.emptyBarSet(input)
        lastLoad = (input.barWeightKg if emptyBar else 0.0)
        for rung in ramp:
            load = self.snap(rung.pct * work, input)
            if input.isBarbell and load <= input.barWeightKg + self.EPS:
                continue
            if load <= lastLoad + self.EPS:
                continue
            if load >= work - self.EPS:
                continue
            sets += WarmupSet(loadKg=load, reps=rung.reps, pctOfWorking=roundToInt((load / work * 100)))
            lastLoad = load
        return sets
    def rampFor(self, input):
        """≡KT  fun rampFor  -> exact"""
        work = input.workingWeightKg
        trivial = (work < input.barWeightKg * self.LIGHT_BARBELL_FACTOR if input.isBarbell else work < self.LIGHT_ISOLATION_FLOOR_KG)
        if trivial:
            return emptyList()
        if input.experience == TrainingExperience.BEGINNER:
            base = listOf(Rung(0.65, 8))
        elif input.experience == TrainingExperience.INTERMEDIATE:
            base = listOf(Rung(0.50, 8), Rung(0.75, 5))
        elif input.experience == TrainingExperience.ADVANCED:
            base = listOf(Rung(0.40, 8), Rung(0.55, 5), Rung(0.70, 3), Rung(0.85, 2))
        return (base if input.isCompound else base.takeLast(minOf(self.ISOLATION_MAX_RUNGS, len(base))))
    def needsEmptyBarSet(self, input):
        """≡KT  fun needsEmptyBarSet  -> exact"""
        return input.isBarbell and input.workingWeightKg > input.barWeightKg * self.EMPTY_BAR_GAP_FACTOR
    def emptyBarSet(self, input):
        """≡KT  fun emptyBarSet  -> exact"""
        return WarmupSet(loadKg=input.barWeightKg, reps=8, pctOfWorking=roundToInt((input.barWeightKg / input.workingWeightKg * 100)), isEmptyBar=True)
    def snap(self, rawKg, input):
        """≡KT  fun snap  -> exact"""
        return (AutoregulationEngine.plateSnap(rawKg, input.availablePlatesKg, input.barWeightKg) if (len(input.availablePlatesKg) != 0) else AutoregulationEngine.roundToIncrement(rawKg, input.incrementKg))
    class WarmupSet:
        """≡KT  data class WarmupSet  -> data class (exact)
        attrs (4/4): isEmptyBar, pctOfWorking, reps, loadKg
        """
        def __init__(self, loadKg, reps, pctOfWorking, isEmptyBar=False):
            self.loadKg = loadKg
            self.reps = reps
            self.pctOfWorking = pctOfWorking
            self.isEmptyBar = isEmptyBar
    class WarmupInput:
        """≡KT  data class WarmupInput  -> data class (exact)
        attrs (7/7): incrementKg, availablePlatesKg, barWeightKg, experience, isBarbell, isCompound, workingWeightKg
        """
        def __init__(self, workingWeightKg, isCompound, isBarbell, experience=TrainingExperience.INTERMEDIATE, barWeightKg=20.0, availablePlatesKg=emptyList(), incrementKg=2.5):
            self.workingWeightKg = workingWeightKg
            self.isCompound = isCompound
            self.isBarbell = isBarbell
            self.experience = experience
            self.barWeightKg = barWeightKg
            self.availablePlatesKg = availablePlatesKg
            self.incrementKg = incrementKg
    class Rung:
        """≡KT  data class Rung  -> data class (exact)
        attrs (2/2): reps, pct
        """
        def __init__(self, pct, reps):
            self.pct = pct
            self.reps = reps


WarmupSet = WarmupEngine.WarmupSet
WarmupInput = WarmupEngine.WarmupInput
Rung = WarmupEngine.Rung
WarmupEngine = WarmupEngine()
