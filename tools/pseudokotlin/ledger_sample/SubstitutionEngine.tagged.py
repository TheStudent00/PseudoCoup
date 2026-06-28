# ≡KT module  java/com/sara/workoutforlife/engine/SubstitutionEngine.kt  ->  SubstitutionEngine.py
# connects(1deg): --

class SubstitutionEngine:
    """≡KT  object SubstitutionEngine  -> object->instance
    attrs (6/6): W_PRIMARY, W_SECONDARY, W_PATTERN, W_CLASS, W_FAVORITE, W_UNILATERAL
    """
    def __init__(self):
        self.W_PRIMARY = 1.00
        self.W_SECONDARY = 0.25
        self.W_PATTERN = 0.30
        self.W_CLASS = 0.20
        self.W_FAVORITE = 0.50
        self.W_UNILATERAL = 0.05
    def rankSubstitutes(self, target, candidates, avoidMuscles=emptySet(), avoidPatterns=emptySet()):
        """≡KT  fun rankSubstitutes  -> exact"""
        if (len(target.primaryMuscles) == 0):
            return emptyList()
        return candidates.filter((lambda it=None: it.id != target.id)).filter((lambda it=None: (it.movementPattern not in avoidPatterns))).filter((lambda it=None: (it.primaryMuscles + it.secondaryMuscles).none((lambda mg: (mg in avoidMuscles))))).mapNotNull((lambda candidate: self.score(target, candidate))).sortedWith(compareByDescending((lambda it=None: it.score)).thenByDescending((lambda it=None: it.isFavorite)).thenByDescending((lambda it=None: it.sharedPrimaryCount))).toList()
    def score(self, target, candidate):
        """≡KT  fun score  -> exact"""
        candidateAll = candidate.primaryMuscles + candidate.secondaryMuscles
        sharedPrimary = target.primaryMuscles.count((lambda it=None: (it in candidateAll)))
        if sharedPrimary == 0:
            return None
        def _lam1(mg):
            if (mg in candidate.primaryMuscles):
                return 1.0
            elif (mg in candidate.secondaryMuscles):
                return 0.5
            else:
                return 0.0
        primaryCoverage = target.primaryMuscles.sumOf(_lam1) / len(target.primaryMuscles)
        secondaryOverlap = (0.0 if (len(target.secondaryMuscles) == 0) else float(target.secondaryMuscles.count((lambda it=None: (it in candidateAll)))) / len(target.secondaryMuscles))
        score = primaryCoverage * self.W_PRIMARY + secondaryOverlap * self.W_SECONDARY
        if candidate.movementPattern == target.movementPattern:
            score += self.W_PATTERN
        if candidate.isCompound == target.isCompound:
            score += self.W_CLASS
        if candidate.isUnilateral == target.isUnilateral:
            score += self.W_UNILATERAL
        if candidate.isFavorite:
            score += self.W_FAVORITE
        return SubstitutionMatch(exerciseId=candidate.id, score=score, sharedPrimaryCount=sharedPrimary, samePattern=candidate.movementPattern == target.movementPattern, isFavorite=candidate.isFavorite)
    class ExerciseProfile:
        """≡KT  data class ExerciseProfile  -> data class (exact)
        attrs (7/7): isFavorite, isUnilateral, isCompound, movementPattern, secondaryMuscles, primaryMuscles, id
        """
        def __init__(self, id, primaryMuscles, secondaryMuscles, movementPattern, isCompound, isUnilateral, isFavorite):
            self.id = id
            self.primaryMuscles = primaryMuscles
            self.secondaryMuscles = secondaryMuscles
            self.movementPattern = movementPattern
            self.isCompound = isCompound
            self.isUnilateral = isUnilateral
            self.isFavorite = isFavorite
    class SubstitutionMatch:
        """≡KT  data class SubstitutionMatch  -> data class (exact)
        attrs (5/5): isFavorite, samePattern, sharedPrimaryCount, score, exerciseId
        """
        def __init__(self, exerciseId, score, sharedPrimaryCount, samePattern, isFavorite):
            self.exerciseId = exerciseId
            self.score = score
            self.sharedPrimaryCount = sharedPrimaryCount
            self.samePattern = samePattern
            self.isFavorite = isFavorite


ExerciseProfile = SubstitutionEngine.ExerciseProfile
SubstitutionMatch = SubstitutionEngine.SubstitutionMatch
SubstitutionEngine = SubstitutionEngine()
