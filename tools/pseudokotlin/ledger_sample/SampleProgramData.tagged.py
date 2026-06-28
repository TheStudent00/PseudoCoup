# ≡KT module  java/com/sara/workoutforlife/data/model/SampleProgramData.kt  ->  SampleProgramData.py
# connects(1deg): ContractionFocus, DayType, DeloadType, ExerciseSeedData, MacrocycleEntity, MacrocycleGoal, MesocycleEntity, MesocycleStatus, MesocycleType, MicrocycleEntity, MicrocycleStatus, MicrocycleType, ProgramDayEntity, ProgramEntity, ProgramExerciseEntity, ProgramSetEntity, ProgressionType, SampleProgramSpecs, SetType, TrainingExperience, label

class SampleProgramData:
    """≡KT  object SampleProgramData  -> object->instance
    attrs (3/3): T, MICROCYCLE_DAYS, ALL
    connects(1deg): ContractionFocus, DayType, DeloadType, ExerciseSeedData, MacrocycleEntity, MacrocycleGoal, MesocycleEntity, MesocycleStatus, MesocycleType, MicrocycleEntity, MicrocycleStatus, MicrocycleType, ProgramDayEntity, ProgramEntity, ProgramExerciseEntity, ProgramSetEntity, ProgressionType, SampleProgramSpecs, SetType, TrainingExperience, label
    """
    def __init__(self):
        self.T = 0
        self.MICROCYCLE_DAYS = 7
    def prog(self, id, name, desc, pathIds, frequency, displayWeeks, experience=None):
        """≡KT  fun prog  -> exact"""
        return ProgramEntity(id, self.stripExperienceSuffix(name), desc, pathIds, frequencyPerWeek=frequency, totalWeeks=displayWeeks, experienceLevel=experience, isActive=True, isEnrolled=False, isAppCurated=True, createdAt=self.T, updatedAt=self.T)
    def stripExperienceSuffix(self, name):
        """≡KT  fun stripExperienceSuffix  -> exact"""
        return (Regex("\\s*\\((?:Beginner|Intermediate|Advanced)\\)\\s*$").replace(name, "") if isinstance(Regex("\\s*\\((?:Beginner|Intermediate|Advanced)\\)\\s*$"), Regex) else name.replace(Regex("\\s*\\((?:Beginner|Intermediate|Advanced)\\)\\s*$"), ""))
    def macro(self, id, progId, seq=1, name=None, status=MesocycleStatus.ACTIVE, started=None, completed=None, goal=None, experience=None, arc=None, notes=None, scienceNote=None):
        """≡KT  fun macro  -> exact"""
        if name is None: name = "Macrocycle $seq"
        return MacrocycleEntity(id=id, programId=progId, sequenceNumber=seq, name=name, status=status, startedAt=started, completedAt=completed, goal=goal, experienceLevelTarget=experience, arcDescription=arc, notes=notes, scienceNote=scienceNote, createdAt=self.T, updatedAt=self.T)
    def meso(self, id, macroId, seq, type, workingWeeks, status=MesocycleStatus.ACTIVE, deload=DeloadType.VOLUME, contraction=None, targetRirMin=None, targetRirMax=None, volumeWaveStartPct=None, progression=None, description=None, scienceNote=None):
        """≡KT  fun meso  -> exact"""
        return MesocycleEntity(id=id, macrocycleId=macroId, sequenceNumber=seq, mesocycleType=type, plannedWorkingWeeks=workingWeeks, actualWeeks=None, status=status, startedAt=None, completedAt=None, deloadType=deload, progressionType=progression, progressionRateKg=None, progressionTiming=None, progressionMethod=None, contractionFocus=contraction, targetRirMin=targetRirMin, targetRirMax=targetRirMax, volumeWaveStartPct=volumeWaveStartPct, description=description, scienceNote=scienceNote, createdAt=self.T, updatedAt=self.T)
    def micro(self, id, mesoId, n, name, type=MicrocycleType.PROGRESSION, status=MicrocycleStatus.PENDING, notes=None, description=None, scienceNote=None):
        """≡KT  fun micro  -> exact"""
        return MicrocycleEntity(id=id, mesocycleId=mesoId, weekNumber=n, name=name, microcycleType=type, status=status, calculatedAt=None, notes=notes, description=description, scienceNote=scienceNote, createdAt=self.T, updatedAt=self.T)
    def day(self, id, micId, n, name, minutes):
        """≡KT  fun day  -> exact"""
        return ProgramDayEntity(id=id, microcycleId=micId, dayNumber=n, name=name, notes=None, estimatedDurationMinutes=minutes, createdAt=self.T, updatedAt=self.T)
    def restDay(self, id, micId, n):
        """≡KT  fun restDay  -> exact"""
        return ProgramDayEntity(id=id, microcycleId=micId, dayNumber=n, name="Rest", dayType=DayType.REST_COMPLETE, notes=None, estimatedDurationMinutes=None, createdAt=self.T, updatedAt=self.T)
    def exRow(self, id, dayId, exId, order, supersetId=None, notes=None):
        """≡KT  fun exRow  -> exact"""
        return ProgramExerciseEntity(id=id, programDayId=dayId, exerciseId=exId, orderIndex=order, supersetGroupId=supersetId, notes=notes, createdAt=self.T, updatedAt=self.T)
    def seedSets(self, programExerciseId, sets, repsMin, repsMax, rpe, rest, setType):
        """≡KT  fun seedSets  -> exact"""
        return (KtList(range(1, sets + 1))).map((lambda n: ProgramSetEntity(id=f"{programExerciseId}_s$n", programExerciseId=programExerciseId, setNumber=n, setType=setType, prescribedRepsMin=repsMin, prescribedRepsMax=repsMax, prescribedLoadKg=None, prescribedRpe=rpe, prescribedRir=None, restSeconds=rest, notes=None, createdAt=self.T, updatedAt=self.T)))
    def macroScience(self, name):
        """≡KT  fun macroScience  -> exact"""
        if ("Foundations" in name):
            return "Beginners gain fastest through motor learning — grooving the movement patterns and calibrating effort before chasing load. Submaximal practice with full range builds the skill and base the later phases require."
        elif ("Metabolite" in name):
            return "A brief functional overreach: volume is pushed toward your maximum recoverable volume (MRV) with metabolite techniques (drop sets, rest-pause). The planned deload that follows drives supercompensation."
        elif ("Base" in name) or ("Accumulation" in name):
            return "Phase potentiation — hypertrophy/volume first. Added muscle raises your force ceiling and the work capacity built here lets the heavier phases that follow be tolerated. Volume (sets near MEV climbing toward MAV) is the primary growth driver."
        elif ("Tension" in name) or ("Intensification" in name):
            return "Mechanical tension is the key hypertrophy stimulus. Heavier loads at lower reps bias high-threshold motor units and tension per fibre, building on the volume the previous arc accumulated."
        elif ("Build" in name):
            return "With muscle in place, the adaptation shifts neural: heavier loads and lower reps train motor-unit recruitment, rate coding, and coordination. The hypertrophy base potentiates these strength gains (conjugate sequencing)."
        elif ("Peak" in name) or ("Realization" in name):
            return "Realization/peaking — volume drops while intensity stays high, so accumulated fatigue dissipates and the fitness built earlier is expressed as a peak (fitness–fatigue model)."
        elif ("Own It" in name):
            return "Autonomy supports long-term adherence (self-determination theory) and teaches the autoregulation skills — deloads, periodisation, exercise swaps — needed to train independently."
        elif ("New Way" in name):
            return "For mental health, adherence and weekly dose drive the benefit — not load. Optional variety can sustain engagement, but it stays optional so it never raises the barrier to showing up."
        elif ("Move" in name) or ("Daily" in name):
            return "For mental health, consistency and weekly dose (~150 min) drive the benefit, not intensity. Predictable, repeatable sessions lower the activation barrier and build the habit."
        else:
            return "Each macrocycle is a complete arc sequenced to potentiate the next — build the quality this phase targets, then express it in the phase that follows."
    def mesoScience(self, type):
        """≡KT  fun mesoScience  -> exact"""
        if type == MesocycleType.ACCUMULATION:
            return "Accumulation — training volume waves up across the block (sets near MEV climbing toward MAV) to drive the adaptation; the deload that ends the block clears the fatigue it built."
        elif type == MesocycleType.INTENSIFICATION:
            return "Intensification — load rises and volume trims so the body adapts to heavier intensities (recruitment, rate coding) while fatigue stays in check."
        elif type == MesocycleType.REALIZATION:
            return "Realization — lowest volume, highest intensity. Fatigue dissipates so the fitness built earlier is expressed as a peak."
        elif type == MesocycleType.MAINTENANCE:
            return "Maintenance — just enough stimulus to hold adaptations with minimal fatigue; here it keeps the habit and consolidates what you've built."
    def microScience(self, isDeload, isTransition, type):
        """≡KT  fun microScience  -> exact"""
        if isTransition:
            return "Active-rest transition — a macro-level reset between arcs: it dissipates residual fatigue and restores trainability before the next phase begins."
        elif isDeload:
            return "Deload week — a planned drop in stress lets accumulated fatigue clear so the fitness you built is expressed (supercompensation). It is scheduled, not optional."
        elif type == MesocycleType.ACCUMULATION:
            return "Progression week — working volume ramps toward your MAV; small weekly increases keep adaptation ahead of fatigue (progressive overload)."
        else:
            return "Progression week — load and intensity step up week to week with volume managed, so you keep adapting (progressive overload)."
    def build(self):
        """≡KT  fun build  -> exact"""
        programs = mutableListOf()
        macrocycles = mutableListOf()
        mesocycles = mutableListOf()
        microcycles = mutableListOf()
        days = mutableListOf()
        exercises = mutableListOf()
        programSets = mutableListOf()
        def ex(id, dayId, exId, order, sets, repsMin, repsMax, rpe=None, rest=None, supersetId=None, notes=None, setType=SetType.STANDARD):
            nonlocal exercises
            nonlocal programSets
            exercises += self.exRow(id, dayId, exId, order, supersetId, notes)
            programSets += self.seedSets(id, sets, repsMin, repsMax, rpe, rest, setType)
        def contractionOf(s):
            return (None if (len(s.strip()) == 0) else ContractionFocus.valueOf(s))
        def progOf(s):
            return (None if (len(s.strip()) == 0) else ProgressionType.valueOf(s))
        def rpeToRir(rpe):
            return max(0, min((10 - int(Math.round(rpe))), 4))
        def estMinutes(slots):
            return max(25, min((20 + slots * 8), 80))
        def expandWeeks(b):
            out = mutableListOf()
            for wk in KtList(range(1, b.workingWeeks + 1)):
                t = (0.0 if b.workingWeeks == 1 else float((wk - 1)) / (b.workingWeeks - 1))
                pSets = int(Math.round(b.startSets + (b.endSets - b.startSets) * t))
                pRpe = float((Math.round((b.startRpe + (b.endRpe - b.startRpe) * t) * 2.0) / 2.0))
                out += WkX(f"{b.name} · Week $wk", MicrocycleType.PROGRESSION, False, pSets, pRpe, maxOf(2, pSets - 1), maxOf(6, pRpe - 1))
            if DeloadType.valueOf(b.deload) == DeloadType.VOLUME:
                dSets, dRpe = Pair(maxOf(2, (b.startSets // 2)), float(max(6.0, min((b.endRpe - 1.0), 8.0))))
            elif DeloadType.valueOf(b.deload) == DeloadType.INTENSITY:
                dSets, dRpe = Pair(3, 6)
            elif DeloadType.valueOf(b.deload) == DeloadType.ACTIVE_REST:
                dSets, dRpe = Pair(2, 5)
            out += WkX(f"{b.name} · Deload", MicrocycleType.DELOAD, True, dSets, dRpe, maxOf(2, dSets - 1), maxOf(6, dRpe - 1))
            return out
        def resolveDays(key, macroNum, blockNum, variant):
            base = SampleProgramSpecs.daymap.filter((lambda it=None: it.key == key and it.macroNum == 0 and it.blockNum == 0))
            blockRows = (SampleProgramSpecs.daymap.filter((lambda it=None: it.key == key and it.macroNum == macroNum and it.blockNum == blockNum)) if macroNum > 0 else emptyList())
            orders = base.map((lambda it=None: it.dayOrder)).distinct().sorted()
            out = mutableListOf()
            for o in orders:
                rows = base.filter((lambda it=None: it.dayOrder == o))
                if rows.any((lambda it=None: it.rest)):
                    out += DayX(o, True, "Rest", emptyList())
                    continue
                sorted = rows.sortedBy((lambda it=None: it.slotOrder))
                def _lam1(r):
                    ex = (r.altId if variant == 1 and (len(r.altId.strip()) != 0) else r.exId)
                    return SlotX(ex, r.role, r.repMin, r.repMax, r.restSec, r.perSide, r.note)
                slots = sorted.map(_lam1)
                label = sorted.first().dayLabel
                bs = blockRows.filter((lambda it=None: it.dayOrder == o))
                if (len(bs) != 0):
                    ohp = bs.first()
                    ohpEx = (ohp.altId if variant == 1 and (len(ohp.altId.strip()) != 0) else ohp.exId)
                    ohpSlot = SlotX(ohpEx, "PRIMARY", ohp.repMin, ohp.repMax, ohp.restSec, ohp.perSide, ohp.note)
                    slots = listOf(slots.first(), ohpSlot) + slots.drop(1).dropLast(1)
                    label = ohp.dayLabel
                slots = slots.filter((lambda it=None: (len(it.exId.strip()) != 0)))
                out += DayX(o, False, label, slots)
            return out
        exMuscles = ExerciseSeedData.ALL.associate((lambda it=None: (it.id, (it.primaryMuscleGroups + it.secondaryMuscleGroups).toSet())))
        exPrimaryMuscles = ExerciseSeedData.ALL.associate((lambda it=None: (it.id, it.primaryMuscleGroups.toSet())))
        def pairCost(a, b):
            shared = len(((exMuscles[a] if exMuscles[a] is not None else emptySet())).intersect((exMuscles[b] if exMuscles[b] is not None else emptySet())))
            sharedPrimary = len(((exPrimaryMuscles[a] if exPrimaryMuscles[a] is not None else emptySet())).intersect((exPrimaryMuscles[b] if exPrimaryMuscles[b] is not None else emptySet())))
            return shared + sharedPrimary * 10
        def sharesPrimaryMover(a, b):
            return (len(((exPrimaryMuscles[a] if exPrimaryMuscles[a] is not None else emptySet())).intersect((exPrimaryMuscles[b] if exPrimaryMuscles[b] is not None else emptySet()))) != 0)
        def assignSupersets(slots, dayId, light, style):
            out = arrayOfNulls(len(slots))
            soloIdx = mutableSetOf()
            def _lam2(i, s):
                nonlocal soloIdx
                if s.role == "PRIMARY":
                    soloIdx += i
            (slots.forEachIndexed(_lam2) if (not light) else None)
            lastAcc = slots.indexOfLast((lambda it=None: it.role == "ACCESSORY"))
            if style == "FINISHER" and lastAcc >= 0:
                soloIdx += lastAcc
            pool = KtList(range(len(slots))).filter((lambda it=None: (it not in soloIdx))).toMutableList()
            if len(pool) < 2:
                return out
            groups = mutableListOf()
            while len(pool) >= 2:
                a = pool.removeAt(0)
                partner = pool.minByOrNull((lambda it=None: pairCost(slots[a].exId, slots[it].exId)))
                if (not light) and sharesPrimaryMover(slots[a].exId, slots[partner].exId):
                    continue
                pool.remove(partner)
                groups.add(mutableListOf(a, partner))
            if len(pool) == 1:
                leftover = pool.removeAt(0)
                last = groups.lastOrNull()
                if last != None and len(last) < 3 and last.none((lambda it=None: sharesPrimaryMover(slots[it].exId, slots[leftover].exId))):
                    last += leftover
            def _lam3(gi, g):
                gid = f'ss_{dayId}_{chr(ord("A") + gi)}'
                for idx in g:
                    pass
            groups.forEachIndexed(_lam3)
            return out
        def emitBlock(key, mesoId, b, macroGoal, daysList, weeks, gWeekStart):
            nonlocal days
            nonlocal microcycles
            pairEverything = macroGoal == MacrocycleGoal.GENERAL_HEALTH and b.deload == "ACTIVE_REST"
            gWeek = gWeekStart
            for w in weeks:
                gWeek += 1
                micId = f"wk_{key}_$gWeek"
                microcycles += self.micro(micId, mesoId, gWeek, w.label, w.type, notes=(b.deloadNote if w.isDeload else b.purpose), description=(b.deloadNote if w.isDeload else b.purpose), scienceNote=self.microScience(w.isDeload, False, MesocycleType.valueOf(b.mesoType)))
                for dx in daysList:
                    dayNo = dx.order
                    if dx.isRest:
                        days += self.restDay(f"day_{key}_w{gWeek}_d$dayNo", micId, dayNo)
                        continue
                    dayId = f"day_{key}_w{gWeek}_d$dayNo"
                    days += self.day(dayId, micId, dayNo, dx.label, estMinutes(len(dx.slots)))
                    lastAcc = dx.slots.indexOfLast((lambda it=None: it.role == "ACCESSORY"))
                    ssIds = (arrayOfNulls(len(dx.slots)) if w.isDeload else assignSupersets(dx.slots, dayId, pairEverything, b.style))
                    order = 0
                    n = 1
                    def _lam4(si, s):
                        nonlocal n
                        nonlocal order
                        primary = s.role == "PRIMARY"
                        sets = (w.pSets if primary else w.aSets)
                        rpe = (w.pRpe if primary else w.aRpe)
                        rMin = (b.repMin if primary else s.repMin)
                        rMax = (b.repMax if primary else s.repMax)
                        rest = s.rest
                        ss = ssIds[si]
                        st = SetType.STANDARD
                        if primary and (len(b.tempo.strip()) != 0):
                            note = b.tempo
                        elif (len(s.note.strip()) != 0):
                            note = s.note
                        elif s.perSide:
                            note = "Per side."
                        else:
                            note = None
                        if (not w.isDeload):
                            if b.style == "FINISHER" and (not primary) and si == lastAcc:
                                st = SetType.REST_PAUSE
                                note = "Rest-pause: 15s breaks, same weight."
                            if b.style == "CONDITION" and ss != None:
                                rest = maxOf(30, ((rest * 3) // 5))
                        _inc5 = n
                        n += 1
                        _inc6 = order
                        order += 1
                        return ex(f"pex_{key}_w{gWeek}_d{dayNo}_{_inc5}", dayId, s.exId, _inc6, sets, rMin, rMax, rpe, rest, supersetId=ss, notes=note, setType=st)
                    dx.slots.forEachIndexed(_lam4)
            return gWeek
        def emitTransition(key, mesoId, gWeek, transitionNote):
            nonlocal days
            nonlocal microcycles
            micId = f"wk_{key}_$gWeek"
            microcycles += self.micro(micId, mesoId, gWeek, "Active-Rest Transition", MicrocycleType.DELOAD, notes=transitionNote, description=transitionNote, scienceNote=self.microScience(False, True, MesocycleType.MAINTENANCE))
            for dx in resolveDays(key, 0, 0, 0):
                dayNo = dx.order
                if dx.isRest:
                    days += self.restDay(f"day_{key}_w{gWeek}_d$dayNo", micId, dayNo)
                    continue
                dayId = f"day_{key}_w{gWeek}_d$dayNo"
                days += self.day(dayId, micId, dayNo, dx.label, estMinutes(len(dx.slots)))
                order = 0
                n = 1
                def _lam7(_, s):
                    nonlocal n
                    nonlocal order
                    primary = s.role == "PRIMARY"
                    rMin = (8 if primary else s.repMin)
                    rMax = (12 if primary else s.repMax)
                    note = (s.note if (len(s.note.strip()) != 0) else ("Per side." if s.perSide else None))
                    _inc8 = n
                    n += 1
                    _inc9 = order
                    order += 1
                    return ex(f"pex_{key}_w{gWeek}_d{dayNo}_{_inc8}", dayId, s.exId, _inc9, 2, rMin, rMax, 5, s.rest, notes=note)
                dx.slots.forEachIndexed(_lam7)
        for p in SampleProgramSpecs.programs:
            key = p.key
            progId = "prog_$key"
            programs += self.prog(progId, p.name, p.arc, p.pathIds, p.frequency, p.totalWeeks, experience=TrainingExperience.valueOf(p.experience))
            macros = SampleProgramSpecs.macros.filter((lambda it=None: it.key == key)).sortedBy((lambda it=None: it.macroNum))
            gWeek = 0
            def _lam10(mi, mac):
                nonlocal gWeek
                nonlocal macrocycles
                nonlocal mesocycles
                macroId = f"macro_{key}_{mac.macroNum}"
                macrocycles += self.macro(macroId, progId, mac.macroNum, name=mac.name, goal=MacrocycleGoal.valueOf(mac.goal), experience=TrainingExperience.valueOf(mac.experience), arc=mac.arc, notes=mac.transition, scienceNote=self.macroScience(mac.name))
                blocks = SampleProgramSpecs.blocks.filter((lambda it=None: it.key == key and it.macroNum == mac.macroNum)).sortedBy((lambda it=None: it.blockNum))
                lastMesoId = macroId
                for b in blocks:
                    mesoId = f"meso_{key}_m{mac.macroNum}_{b.blockNum}"
                    lastMesoId = mesoId
                    mesocycles += self.meso(mesoId, macroId, b.blockNum, MesocycleType.valueOf(b.mesoType), b.workingWeeks, deload=DeloadType.valueOf(b.deload), contraction=contractionOf(b.contraction), targetRirMin=rpeToRir(b.endRpe), targetRirMax=rpeToRir(b.startRpe), volumeWaveStartPct=60, progression=progOf(b.progression), description=b.purpose, scienceNote=self.mesoScience(MesocycleType.valueOf(b.mesoType)))
                    daysList = resolveDays(key, mac.macroNum, b.blockNum, b.variant)
                    gWeek = emitBlock(key, mesoId, b, MacrocycleGoal.valueOf(mac.goal), daysList, expandWeeks(b), gWeek)
                if mi < len(macros) - 1:
                    gWeek += 1
                    return emitTransition(key, lastMesoId, gWeek, mac.transition)
            macros.forEachIndexed(_lam10)
        programs += self.prog("prog_learn_to_listen_basics", "Basic Gym Movements", (str(("The first step in your journey. Learn the fundamental compound and isolation " + str("movements while establishing your starting weights. Focus is 100% on form "))) + "and muscle activation, not load."), "path_learn_to_listen", frequency=3, displayWeeks=4, experience=TrainingExperience.BEGINNER)
        macrocycles += self.macro("macro_ltl_basics", "prog_learn_to_listen_basics", 1, "Skill Acquisition Block", goal=MacrocycleGoal.GENERAL_HEALTH, experience=TrainingExperience.BEGINNER, arc="Accumulation", notes=("A single accumulation block focused 100% on movement skill and establishing " + str("starting loads — not progression. Serves Learn to Listen.")), scienceNote=("Beginners gain fastest through motor learning. This block is deliberate " + str("practice — grooving the movements and finding honest starting loads — not progression.")))
        mesocycles += self.meso("meso_ltl_basics_1", "macro_ltl_basics", 1, MesocycleType.ACCUMULATION, 4, scienceNote=("Skill-first accumulation: practise the patterns at submaximal effort to build " + str("competence and baseline loads before any real loading.")))
        def addBasicsWeek(wkN, label, pRpe):
            nonlocal days
            nonlocal microcycles
            micId = "wk_ltl_basics_$wkN"
            microcycles += self.micro(micId, "meso_ltl_basics_1", wkN, label, description="Practise the lifts with full range and a braced core — the goal is the movement, not the number.", scienceNote="Skill-acquisition week: deliberate practice builds the motor pattern and your starting loads.")
            mins = 40
            dA = f"day_ltl_basics_{wkN}_a"
            days += self.day(dA, micId, 1, "Day A — Squat & Push", mins)
            ex(f"pex_ltl_basics_{wkN}_a_1", dA, "ex_squat", 0, 3, 8, 12, pRpe, 90, notes="Focus on depth and braced core.")
            ex(f"pex_ltl_basics_{wkN}_a_2", dA, "ex_bench_press", 1, 3, 8, 12, pRpe, 90, notes="Controlled eccentric; feel the chest stretch.")
            ex(f"pex_ltl_basics_{wkN}_a_3", dA, "ex_bb_row", 2, 3, 10, 12, pRpe, 90, notes="Squeeze shoulder blades at the top.")
            ex(f"pex_ltl_basics_{wkN}_a_4", dA, "ex_db_curl", 3, 2, 12, 15, 6, 60)
            dB = f"day_ltl_basics_{wkN}_b"
            days += self.day(dB, micId, 2, "Day B — Hinge & Pull", mins)
            ex(f"pex_ltl_basics_{wkN}_b_1", dB, "ex_deadlift", 0, 3, 8, 10, pRpe, 120, notes="Keep bar close; neutral spine.")
            ex(f"pex_ltl_basics_{wkN}_b_2", dB, "ex_ohp", 1, 3, 8, 10, pRpe, 120)
            ex(f"pex_ltl_basics_{wkN}_b_3", dB, "ex_pullup", 2, 3, 5, 10, pRpe, 120, notes="Use band assistance to focus on lat activation.")
            ex(f"pex_ltl_basics_{wkN}_b_4", dB, "ex_band_tri_pushdown", 3, 2, 12, 15, 6, 60)
            dC = f"day_ltl_basics_{wkN}_c"
            days += self.day(dC, micId, 3, "Day C — Accessories & Form", mins)
            ex(f"pex_ltl_basics_{wkN}_c_1", dC, "ex_goblet_squat", 0, 3, 10, 12, pRpe, 90)
            ex(f"pex_ltl_basics_{wkN}_c_2", dC, "ex_db_bench_press", 1, 3, 10, 12, pRpe, 90)
            ex(f"pex_ltl_basics_{wkN}_c_3", dC, "ex_landmine_row", 2, 3, 10, 12, pRpe, 90)
            ex(f"pex_ltl_basics_{wkN}_c_4", dC, "ex_lateral_raise", 3, 2, 12, 15, 6, 60)
        addBasicsWeek(1, "Week 1 — Introduction", pRpe=5)
        addBasicsWeek(2, "Week 2 — Practice", pRpe=6)
        addBasicsWeek(3, "Week 3 — Consolidation", pRpe=7)
        addBasicsWeek(4, "Week 4 — Calibration", pRpe=8)
        programs += self.prog("prog_learn_to_listen_rir", "RIR Awareness", (str(("Develop the skill of Reps in Reserve (RIR) perception. Through a 8-week " + str("curriculum, you'll learn to accurately estimate how much effort you have "))) + "left in the tank, enabling precise autoregulation for life."), "path_learn_to_listen", frequency=3, displayWeeks=8, experience=TrainingExperience.INTERMEDIATE)
        macrocycles += self.macro("macro_ltl_rir", "prog_learn_to_listen_rir", 1, "Calibration Block", goal=MacrocycleGoal.GENERAL_HEALTH, experience=TrainingExperience.INTERMEDIATE, arc="Accumulation → Intensification", notes=("An eight-week curriculum training accurate RIR perception for lifelong " + str("autoregulation. Serves Learn to Listen.")), scienceNote=("Accurate effort perception (Reps in Reserve) is a trainable skill and the " + str("foundation of autoregulation. This curriculum calibrates it from observation to full self-regulation.")))
        mesocycles += self.meso("meso_ltl_rir_1", "macro_ltl_rir", 1, MesocycleType.ACCUMULATION, 4, scienceNote="Observation → calibration: log perceived RIR, then test against true failure to calibrate your sense of effort.")
        mesocycles += self.meso("meso_ltl_rir_2", "macro_ltl_rir", 2, MesocycleType.INTENSIFICATION, 4, scienceNote="Guided → full RIR: train to RIR targets, building autoregulation you can use for life.")
        def addRirWeek(wkN, label, pRpe, pRir, notesA=None, notesB=None, notesC=None, type=MicrocycleType.PROGRESSION):
            nonlocal days
            nonlocal microcycles
            mesoId = ("meso_ltl_rir_1" if wkN <= 4 else "meso_ltl_rir_2")
            micId = "wk_ltl_rir_$wkN"
            microcycles += self.micro(micId, mesoId, wkN, label, type, description="Estimate your reps-in-reserve on every working set, then check it against how the set actually felt.", scienceNote="Interoception week: comparing your RIR call to reality sharpens effort perception (autoregulation).")
            mins = 45
            dA = f"day_ltl_rir_{wkN}_a"
            days += self.day(dA, micId, 1, "Day A — Squat Focus", mins)
            ex(f"pex_ltl_rir_{wkN}_a_1", dA, "ex_squat", 0, 3, 8, 10, pRpe, 120, notes=notesA)
            ex(f"pex_ltl_rir_{wkN}_a_2", dA, "ex_bb_row", 1, 3, 10, 12, pRpe, 90)
            ex(f"pex_ltl_rir_{wkN}_a_3", dA, "ex_leg_press", 2, 3, 12, 15, pRpe, 90)
            dB = f"day_ltl_rir_{wkN}_b"
            days += self.day(dB, micId, 2, "Day B — Hinge Focus", mins)
            ex(f"pex_ltl_rir_{wkN}_b_1", dB, "ex_deadlift", 0, 3, 5, 8, pRpe, 120, notes=notesB)
            ex(f"pex_ltl_rir_{wkN}_b_2", dB, "ex_bench_press", 1, 3, 8, 10, pRpe, 90)
            ex(f"pex_ltl_rir_{wkN}_b_3", dB, "ex_leg_extension", 2, 3, 12, 15, pRpe, 60)
            dC = f"day_ltl_rir_{wkN}_c"
            days += self.day(dC, micId, 3, "Day C — Push Focus", mins)
            ex(f"pex_ltl_rir_{wkN}_c_1", dC, "ex_ohp", 0, 3, 8, 10, pRpe, 120, notes=notesC)
            ex(f"pex_ltl_rir_{wkN}_c_2", dC, "ex_pullup", 1, 3, 8, 12, pRpe, 120)
            ex(f"pex_ltl_rir_{wkN}_c_3", dC, "ex_lateral_raise", 2, 3, 12, 15, pRpe, 60)
        addRirWeek(1, "Week 1 — Observation", pRpe=6, pRir=None, notesA="Log RIR as an observation only — how many more reps COULD you have done?", notesB="Focus on the feeling of the last 2-3 reps.", notesC="Don't worry about being 'right' yet.")
        addRirWeek(2, "Week 2 — Observation", pRpe=7, pRir=None)
        addRirWeek(3, "Week 3 — Calibration", pRpe=7, pRir=None, notesB="LEG EXTENSION: On the last set, go to true failure (0 RIR). Compare to your estimate.")
        addRirWeek(4, "Week 4 — Calibration", pRpe=8, pRir=None, notesC="LATERAL RAISE: On the last set, go to true failure. How many more reps did you get than you thought?")
        addRirWeek(5, "Week 5 — Guided (Iso)", pRpe=8, pRir=None, notesA="Use target RIR for Leg Press. Compounds stay at target reps.")
        addRirWeek(6, "Week 6 — Guided (Iso)", pRpe=8, pRir=None)
        addRirWeek(7, "Week 7 — Full RIR", pRpe=8, pRir=None, notesA="All exercises now use RIR targets. Trust your body.")
        addRirWeek(8, "Week 8 — Full RIR", pRpe=9, pRir=None)
        restDays = mutableListOf()
        for mic in microcycles:
            workoutCount = days.count((lambda it=None: it.microcycleId == mic.id))
            for i in KtList(range(1, max((self.MICROCYCLE_DAYS - workoutCount), 0) + 1)):
                n = workoutCount + i
                restDays += self.restDay(f"{mic.id}_rest_$n", mic.id, n)
        days += restDays
        return Bundle(programs, macrocycles, mesocycles, microcycles, days, exercises, programSets)
    @property
    def ALL(self):
        if not hasattr(self, "_ALL"):
            self._ALL = self.build()
        return self._ALL
    class Bundle:
        """≡KT  data class Bundle  -> data class (exact)
        attrs (7/7): programSets, exercises, days, microcycles, mesocycles, macrocycles, programs
        """
        def __init__(self, programs, macrocycles, mesocycles, microcycles, days, exercises, programSets):
            self.programs = programs
            self.macrocycles = macrocycles
            self.mesocycles = mesocycles
            self.microcycles = microcycles
            self.days = days
            self.exercises = exercises
            self.programSets = programSets
    class WkX:
        """≡KT  class WkX  -> class (exact)
        attrs (7/7): aRpe, aSets, pRpe, pSets, isDeload, type, label
        """
        def __init__(self, label, type, isDeload, pSets, pRpe, aSets, aRpe):
            self.label = label
            self.type = type
            self.isDeload = isDeload
            self.pSets = pSets
            self.pRpe = pRpe
            self.aSets = aSets
            self.aRpe = aRpe
    class SlotX:
        """≡KT  class SlotX  -> class (exact)
        attrs (7/7): note, perSide, rest, repMax, repMin, role, exId
        """
        def __init__(self, exId, role, repMin, repMax, rest, perSide, note):
            self.exId = exId
            self.role = role
            self.repMin = repMin
            self.repMax = repMax
            self.rest = rest
            self.perSide = perSide
            self.note = note
    class DayX:
        """≡KT  class DayX  -> class (exact)
        attrs (4/4): slots, label, isRest, order
        """
        def __init__(self, order, isRest, label, slots):
            self.order = order
            self.isRest = isRest
            self.label = label
            self.slots = slots


Bundle = SampleProgramData.Bundle
WkX = SampleProgramData.WkX
SlotX = SampleProgramData.SlotX
DayX = SampleProgramData.DayX
SampleProgramData = SampleProgramData()
