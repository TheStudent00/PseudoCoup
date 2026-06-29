def _ev(f):
    try:
        return f()
    except Exception:
        return None



class _Track:                             # records every define_*'s zone id -> owned_ids
    def __init__(self, ui, owned): self._ui, self._owned = ui, owned
    def __getattr__(self, n):
        fn = getattr(self._ui, n)
        if n.startswith('define_'):
            def w(zid, *a, **k):
                self._owned.append(zid)
                return fn(zid, *a, **k)
            return w
        return fn


class ExerciseDetailScreenGen:
    def __init__(self, db):
        self.db = db
        self.vm = build_transpiled_vm('exercise_detail', db)
        self.owned_ids = []

    def screen_id(self):
        return 'exercise_detail'


    def build(self, ui, content_zone_id, router):
        self.owned_ids = []
        ui = _Track(ui, self.owned_ids)
        self.router = router
        viewModel = self.vm
        content = content_zone_id
        exercise = _ev(lambda: viewModel.exercise.collectAsStateWithLifecycle())
        excludePrompt = _ev(lambda: viewModel.excludePrompt.collectAsStateWithLifecycle())
        showDeleteDialog = _ev(lambda: remember((lambda it=None: mutableStateOf(False))))
        _id0 = "exercise_detail_z0"
        ui.define_box(_id0, content, "V")
        _id1 = "exercise_detail_z1"
        ui.define_box(_id1, content, "V")
        ex = _ev(lambda: exercise)
        _id2 = "exercise_detail_z2"
        ui.define_box(_id2, content, "V")
        if _ev(lambda: ex != None):
            _id4 = "exercise_detail_z4"
            ui.define_box(_id4, _id2, "V")
            _id5 = "exercise_detail_z5"
            ui.define_box(_id5, _id4, "V")
            _id6 = "exercise_detail_z6"
            ui.define_box(_id6, _id5, "H")
            if _ev(lambda: exercise.isCustom):
                _id8 = "exercise_detail_z8"
                ui.define_box(_id8, _id6, "V")
                ui.define_text("exercise_detail_z9", _id8, 'Custom')
            else:
                _id10 = "exercise_detail_z10"
                ui.define_box(_id10, _id6, "V")
                ui.define_text("exercise_detail_z11", _id10, 'Built-in')
            _id12 = "exercise_detail_z12"
            ui.define_box(_id12, _id6, "V")
            ui.define_text("exercise_detail_z13", _id12, _ev(lambda: ("Compound" if exercise.isCompound else "Isolation")))
            _id14 = "exercise_detail_z14"
            ui.define_box(_id14, _id6, "V")
            ui.define_text("exercise_detail_z15", _id14, _ev(lambda: ("Unilateral" if exercise.isUnilateral else "Bilateral")))
            _id16 = "exercise_detail_z16"
            ui.define_box(_id16, _id5, "V")
            _id17 = "exercise_detail_z17"
            ui.define_box(_id17, _id16, "V")
            ui.define_text("exercise_detail_z18", _id17, 'Primary muscles')
            ui.define_spacer_zone("exercise_detail_z19", _id17)
            ui.define_text("exercise_detail_z20", _id17, _ev(lambda: body))
            _id21 = "exercise_detail_z21"
            ui.define_box(_id21, _id16, "H")
            for _i22, m in enumerate(_ev(lambda: exercise.primaryMuscleGroups) or []):
                _id23 = ("exercise_detail_z23" + "_" + str(_i22))
                ui.define_box(_id23, _id21, "V")
                ui.define_text(("exercise_detail_z24" + "_" + str(_i22)), _id23, _ev(lambda: m.displayName()))
            if _ev(lambda: (len(exercise.secondaryMuscleGroups) != 0)):
                _id26 = "exercise_detail_z26"
                ui.define_box(_id26, _id5, "V")
                _id27 = "exercise_detail_z27"
                ui.define_box(_id27, _id26, "V")
                ui.define_text("exercise_detail_z28", _id27, 'Secondary muscles')
                ui.define_spacer_zone("exercise_detail_z29", _id27)
                ui.define_text("exercise_detail_z30", _id27, _ev(lambda: body))
                _id31 = "exercise_detail_z31"
                ui.define_box(_id31, _id26, "H")
                for _i32, m in enumerate(_ev(lambda: exercise.secondaryMuscleGroups) or []):
                    _id33 = ("exercise_detail_z33" + "_" + str(_i32))
                    ui.define_box(_id33, _id31, "V")
                    ui.define_text(("exercise_detail_z34" + "_" + str(_i32)), _id33, _ev(lambda: m.displayName()))
            _id35 = "exercise_detail_z35"
            ui.define_box(_id35, _id5, "V")
            _id36 = "exercise_detail_z36"
            ui.define_box(_id36, _id35, "V")
            ui.define_text("exercise_detail_z37", _id36, 'Movement & equipment')
            ui.define_spacer_zone("exercise_detail_z38", _id36)
            ui.define_text("exercise_detail_z39", _id36, _ev(lambda: body))
            ui.define_text("exercise_detail_z40", _id35, _ev(lambda: f"{exercise.movementPattern.displayName()}  ·  {exercise.equipmentType.displayName()}"))
            if _ev(lambda: (not (exercise.instructions is None or len(exercise.instructions.strip()) == 0))):
                ui.define_divider_zone("exercise_detail_z42", _id5)
                ui.define_spacer_zone("exercise_detail_z43", _id5)
                _id44 = "exercise_detail_z44"
                ui.define_box(_id44, _id5, "V")
                _id45 = "exercise_detail_z45"
                ui.define_box(_id45, _id44, "V")
                ui.define_text("exercise_detail_z46", _id45, 'Form notes')
                ui.define_spacer_zone("exercise_detail_z47", _id45)
                ui.define_text("exercise_detail_z48", _id45, _ev(lambda: body))
                ui.define_text("exercise_detail_z49", _id44, _ev(lambda: exercise.instructions))
            if _ev(lambda: (not (exercise.cues is None or len(exercise.cues.strip()) == 0))):
                _id51 = "exercise_detail_z51"
                ui.define_box(_id51, _id5, "V")
                _id52 = "exercise_detail_z52"
                ui.define_box(_id52, _id51, "V")
                ui.define_text("exercise_detail_z53", _id52, 'Coaching cues')
                ui.define_spacer_zone("exercise_detail_z54", _id52)
                ui.define_text("exercise_detail_z55", _id52, _ev(lambda: body))
                ui.define_text("exercise_detail_z56", _id51, _ev(lambda: exercise.cues))
            if _ev(lambda: (not (exercise.videoLink is None or len(exercise.videoLink.strip()) == 0))):
                _id58 = "exercise_detail_z58"
                ui.define_box(_id58, _id5, "V")
                _id59 = "exercise_detail_z59"
                ui.define_box(_id59, _id58, "V")
                ui.define_text("exercise_detail_z60", _id59, 'Video reference')
                ui.define_spacer_zone("exercise_detail_z61", _id59)
                ui.define_text("exercise_detail_z62", _id59, _ev(lambda: body))
                ui.define_text("exercise_detail_z63", _id58, _ev(lambda: exercise.videoLink))
        _id64 = "exercise_detail_z64"
        ui.define_box(_id64, _id2, "V")
        ui.define_text("exercise_detail_z65", _id64, _ev(lambda: ((ex.name if ex is not None else None) if (ex.name if ex is not None else None) is not None else "")))
        ui.define_text("exercise_detail_z66", _id64, '←')
        def _h67(evt): onNavigateBack()
        ui.on_click("exercise_detail_z66", _h67)
        ui.define_icon("exercise_detail_z68", _id64, 'Toggle favorite')
        def _h69(evt): self.vm.toggleFavorite()
        ui.on_click("exercise_detail_z68", _h69)
        ui.define_icon("exercise_detail_z70", _id64, 'More')
        def _h71(evt): showMenu = true()
        ui.on_click("exercise_detail_z70", _h71)
        _id72 = "exercise_detail_z72"
        ui.define_box(_id72, _id64, "V")
        _id73 = "exercise_detail_z73"
        ui.define_box(_id73, _id72, "V")
        def _h74(evt): showMenu = false; self.vm.duplicate()
        ui.on_click(_id73, _h74)
        ui.define_text("exercise_detail_z75", _id73, 'Duplicate & Edit')
        _id76 = "exercise_detail_z76"
        ui.define_box(_id76, _id72, "V")
        def _h77(evt): showMenu = false; self.vm.onToggleExcluded()
        ui.on_click(_id76, _h77)
        ui.define_text("exercise_detail_z78", _id76, _ev(lambda: ("Allow programming again" if (ex.isExcluded if ex is not None else None) == True else "Never program this")))
        if _ev(lambda: (ex.isCustom if ex is not None else None) == True):
            _id80 = "exercise_detail_z80"
            ui.define_box(_id80, _id72, "V")
            def _h81(evt): showMenu = false; self.vm.editCurrent()
            ui.on_click(_id80, _h81)
            ui.define_text("exercise_detail_z82", _id80, 'Edit')
            _id83 = "exercise_detail_z83"
            ui.define_box(_id83, _id72, "V")
            def _h84(evt): showMenu = false; showDeleteDialog = true()
            ui.on_click(_id83, _h84)
            ui.define_text("exercise_detail_z85", _id83, 'Delete')
        if _ev(lambda: showDeleteDialog):
            _id87 = "exercise_detail_z87"
            ui.define_box(_id87, content, "V")
            ui.define_text("exercise_detail_z88", _id87, 'Delete exercise?')
            ui.define_text("exercise_detail_z89", _id87, _ev(lambda: f'This will permanently delete \"{(exercise.name if exercise is not None else None)}\". Logs and PRs are unaffected.'))
            ui.define_button("exercise_detail_z90", _id87, 'Delete')
            def _h91(evt): showDeleteDialog = false; self.vm.delete()
            ui.on_click("exercise_detail_z90", _h91)
            ui.define_button("exercise_detail_z92", _id87, 'Cancel')
            def _h93(evt): showDeleteDialog = false()
            ui.on_click("exercise_detail_z92", _h93)
        prompt = _ev(lambda: excludePrompt)
        if prompt is not None:
            where = _ev(lambda: ("1 spot in your program" if prompt.occurrences == 1 else f"{prompt.occurrences} spots in your program"))
            _id94 = "exercise_detail_z94"
            ui.define_box(_id94, content, "V")
            ui.define_text("exercise_detail_z95", _id94, 'Already in your program')
            ui.define_text("exercise_detail_z96", _id94, _ev(lambda: buildString(_lam1)))
            if _ev(lambda: prompt.substituteName != None):
                ui.define_button("exercise_detail_z98", _id94, 'Swap all now')
                def _h99(evt, prompt=prompt): self.vm.confirmSwapNow()
                ui.on_click("exercise_detail_z98", _h99)
            else:
                ui.define_button("exercise_detail_z100", _id94, 'Got it')
                def _h101(evt, prompt=prompt): self.vm.confirmSwapLater()
                ui.on_click("exercise_detail_z100", _h101)
            if _ev(lambda: prompt.substituteName != None):
                ui.define_button("exercise_detail_z103", _id94, 'Swap during workouts')
                def _h104(evt, prompt=prompt): self.vm.confirmSwapLater()
                ui.on_click("exercise_detail_z103", _h104)
            else:
                ui.define_button("exercise_detail_z105", _id94, 'Cancel')
                def _h106(evt, prompt=prompt): self.vm.dismissExcludePrompt()
                ui.on_click("exercise_detail_z105", _h106)
