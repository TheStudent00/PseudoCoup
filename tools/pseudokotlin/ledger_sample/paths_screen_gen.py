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


class PathsScreenGen:
    def __init__(self, db):
        self.db = db
        self.vm = None
        self._vm_sel = None
        self.owned_ids = []

    def screen_id(self):
        return 'paths'


    def build(self, ui, content_zone_id, router):
        self.owned_ids = []
        ui = _Track(ui, self.owned_ids)
        self.router = router
        _sel = getattr(router, 'selected_id', None)
        if self.vm is None or self._vm_sel != _sel:
            self.vm = build_transpiled_vm('paths', self.db, _sel)
            self._vm_sel = _sel
        viewModel = self.vm
        content = content_zone_id
        activePaths = _ev(lambda: viewModel.activePaths.collectAsStateWithLifecycle())
        pickerState = _ev(lambda: viewModel.pickerState.collectAsStateWithLifecycle())
        _id0 = "paths_z0"
        ui.define_box(_id0, content, "V")
        _id1 = "paths_z1"
        ui.define_box(_id1, _id0, "V")
        if _ev(lambda: (len(activePaths) != 0)):
            ui.define_text("paths_z3", _id1, 'Paths are the why. Programs are the how.')
        if _ev(lambda: (len(activePaths) == 0)):
            _id5 = "paths_z5"
            ui.define_box(_id5, _id1, "V")
            _id6 = "paths_z6"
            ui.define_box(_id6, _id5, "V")
            ui.define_text("paths_z7", _id6, 'Start with your why.')
            ui.define_text("paths_z8", _id6, 'A Path connects your training to what actually matters — evidence-backed goals for mental health, bone strength, brain function, and more.')
            ui.define_spacer_zone("paths_z9", _id6)
            ui.define_button("paths_z10", _id6, 'Find your path')
            def _h11(evt): self.vm.startPicker()
            ui.on_click("paths_z10", _h11)
        else:
            for _i12, path in enumerate(_ev(lambda: activePaths) or []):
                _id13 = ("paths_z13" + "_" + str(_i12))
                ui.define_box(_id13, _id1, "V")
                definition = _ev(lambda: PathDefinition.findById(path.id))
                _id14 = ("paths_z14" + "_" + str(_i12))
                ui.define_box(_id14, _id13, "V")
                def _h15(evt, path=path): onNavigateToDetail(path.id)
                ui.on_click(_id14, _h15)
                if _ev(lambda: onClick != None):
                    _id17 = ("paths_z17" + "_" + str(_i12))
                    ui.define_box(_id17, _id14, "V")
                    def _h18(evt, path=path): onNavigateToDetail(path.id)
                    ui.on_click(_id17, _h18)
                else:
                    _id19 = ("paths_z19" + "_" + str(_i12))
                    ui.define_box(_id19, _id14, "V")
                _id20 = ("paths_z20" + "_" + str(_i12))
                ui.define_box(_id20, _id14, "V")
                _id21 = ("paths_z21" + "_" + str(_i12))
                ui.define_box(_id21, _id20, "H")
                ui.define_text(("paths_z22" + "_" + str(_i12)), _id21, _ev(lambda: path.name))
                ui.define_button(("paths_z23" + "_" + str(_i12)), _id21, 'Leave path')
                def _h24(evt, path=path): onUnenroll()
                ui.on_click(("paths_z23" + "_" + str(_i12)), _h24)
                it = _ev(lambda: definition)
                if it is not None:
                    ui.define_spacer_zone(("paths_z25" + "_" + str(_i12)), _id20)
                    ui.define_text(("paths_z26" + "_" + str(_i12)), _id20, _ev(lambda: it.tagline))
                    ui.define_spacer_zone(("paths_z27" + "_" + str(_i12)), _id20)
                    _id28 = ("paths_z28" + "_" + str(_i12))
                    ui.define_box(_id28, _id20, "H")
                    _id29 = ("paths_z29" + "_" + str(_i12))
                    ui.define_box(_id29, _id28, "V")
                    _id30 = ("paths_z30" + "_" + str(_i12))
                    ui.define_box(_id30, _id29, "V")
                    ui.define_text(("paths_z31" + "_" + str(_i12)), _id30, 'Sessions')
                    ui.define_text(("paths_z32" + "_" + str(_i12)), _id30, _ev(lambda: f"{it.minSessionsPerWeek}–{it.maxSessionsPerWeek}/week"))
                    _id33 = ("paths_z33" + "_" + str(_i12))
                    ui.define_box(_id33, _id28, "V")
                    _id34 = ("paths_z34" + "_" + str(_i12))
                    ui.define_box(_id34, _id33, "V")
                    ui.define_text(("paths_z35" + "_" + str(_i12)), _id34, 'Target')
                    ui.define_text(("paths_z36" + "_" + str(_i12)), _id34, _ev(lambda: f"{it.targetMinutesPerSession} min"))
                    ui.define_spacer_zone(("paths_z37" + "_" + str(_i12)), _id20)
                    ui.define_text(("paths_z38" + "_" + str(_i12)), _id20, 'The evidence')
                    _id39 = ("paths_z39" + "_" + str(_i12))
                    ui.define_box(_id39, _id20, "V")
                    ui.define_text(("paths_z40" + "_" + str(_i12)), _id39, _ev(lambda: it.evidenceSummary))
                    _id41 = ("paths_z41" + "_" + str(_i12))
                    ui.define_box(_id41, _id39, "V")
                    ui.define_spacer_zone(("paths_z42" + "_" + str(_i12)), _id20)
            if _ev(lambda: len(activePaths) == 1):
                _id44 = "paths_z44"
                ui.define_box(_id44, _id1, "V")
                ui.define_button("paths_z45", _id44, 'Add a second path')
                def _h46(evt): self.vm.startAddSecond(activePaths.map((lambda it=None: it.id)).toSet())
                ui.on_click("paths_z45", _h46)
        _id47 = "paths_z47"
        ui.define_box(_id47, _id0, "V")
        state = _ev(lambda: pickerState)
        if state is not None:
            _id48 = "paths_z48"
            ui.define_box(_id48, _id47, "V")
            sections = _ev(lambda: PathDefinition.grouped(excludeIds=(state.enrolledPathIds if state.isAddingSecond else emptySet())))
            title = _ev(lambda: ("Add a second path" if state.isAddingSecond else "Find your Path"))
            if state.isAddingSecond:
                subtitle = "Choose one more to work toward."
            else:
                subtitle = "Choose what matters to you. Select up to 2 paths."
            _id49 = "paths_z49"
            ui.define_box(_id49, _id48, "V")
            _id50 = "paths_z50"
            ui.define_box(_id50, _id49, "V")
            ui.define_text("paths_z51", _id50, _ev(lambda: subtitle))
            for _i52, it in enumerate(_ev(lambda: sections) or []):
                _id53 = ("paths_z53" + "_" + str(_i52))
                ui.define_box(_id53, _id50, "V")
                _id54 = ("paths_z54" + "_" + str(_i52))
                ui.define_box(_id54, _id53, "V")
                if _ev(lambda: category == PathCategory.SELF_DIRECTED):
                    ui.define_divider_zone(("paths_z56" + "_" + str(_i52)), _id54)
                ui.define_text(("paths_z57" + "_" + str(_i52)), _id54, _ev(lambda: category.displayName))
                for _i58, def_ in enumerate(_ev(lambda: paths) or []):
                    isSelected = _ev(lambda: (def_.id in state.selectedPathIds))
                    _id59 = ("paths_z59" + "_" + (str(_i52) + "_" + str(_i58)))
                    ui.define_box(_id59, _id50, "V")
                    _id60 = ("paths_z60" + "_" + (str(_i52) + "_" + str(_i58)))
                    ui.define_box(_id60, _id59, "V")
                    def _h61(evt, state=state, it=it, def_=def_): onTogglePathSelection(def_.id)
                    ui.on_click(_id60, _h61)
                    containerColor = _ev(lambda: (MaterialTheme.colorScheme.primaryContainer if isSelected else MaterialTheme.colorScheme.surface))
                    _id62 = ("paths_z62" + "_" + (str(_i52) + "_" + str(_i58)))
                    ui.define_box(_id62, _id60, "V")
                    def _h63(evt, state=state, it=it, def_=def_): onTogglePathSelection(def_.id)
                    ui.on_click(_id62, _h63)
                    if _ev(lambda: onClick != None):
                        _id65 = ("paths_z65" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id65, _id62, "V")
                        def _h66(evt, state=state, it=it, def_=def_): onTogglePathSelection(def_.id)
                        ui.on_click(_id65, _h66)
                    else:
                        _id67 = ("paths_z67" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id67, _id62, "V")
                    _id68 = ("paths_z68" + "_" + (str(_i52) + "_" + str(_i58)))
                    ui.define_box(_id68, _id62, "H")
                    _id69 = ("paths_z69" + "_" + (str(_i52) + "_" + str(_i58)))
                    ui.define_box(_id69, _id68, "V")
                    ui.define_text(("paths_z70" + "_" + (str(_i52) + "_" + str(_i58))), _id69, _ev(lambda: definition.name))
                    ui.define_spacer_zone(("paths_z71" + "_" + (str(_i52) + "_" + str(_i58))), _id69)
                    ui.define_text(("paths_z72" + "_" + (str(_i52) + "_" + str(_i58))), _id69, _ev(lambda: definition.tagline))
                    ui.define_spacer_zone(("paths_z73" + "_" + (str(_i52) + "_" + str(_i58))), _id69)
                    ui.define_text(("paths_z74" + "_" + (str(_i52) + "_" + str(_i58))), _id69, _ev(lambda: f"{definition.minSessionsPerWeek}–{definition.maxSessionsPerWeek} sessions/week · ~{definition.targetMinutesPerSession} min"))
                    if _ev(lambda: isSelected):
                        ui.define_spacer_zone(("paths_z76" + "_" + (str(_i52) + "_" + str(_i58))), _id68)
                        _id77 = ("paths_z77" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id77, _id68, "V")
                        _id78 = ("paths_z78" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id78, _id77, "V")
                    if _ev(lambda: isSelected and def_.hasCustomName):
                        ui.define_spacer_zone(("paths_z80" + "_" + (str(_i52) + "_" + str(_i58))), _id59)
                        _id81 = ("paths_z81" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id81, _id59, "V")
                        _id82 = ("paths_z82" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id82, _id81, "V")
                        _id83 = ("paths_z83" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id83, _id82, "V")
                        ui.define_text(("paths_z84" + "_" + (str(_i52) + "_" + str(_i58))), _id83, 'What are you recovering from?')
                        _id85 = ("paths_z85" + "_" + (str(_i52) + "_" + str(_i58)))
                        ui.define_box(_id85, _id81, "V")
            _id86 = "paths_z86"
            ui.define_box(_id86, _id49, "V")
            ui.define_text("paths_z87", _id86, _ev(lambda: title))
            ui.define_text("paths_z88", _id86, '✕')
            def _h89(evt, state=state): self.vm.dismissPicker()
            ui.on_click("paths_z88", _h89)
            _id90 = "paths_z90"
            ui.define_box(_id90, _id49, "V")
            ui.define_button("paths_z91", _id90, 'Start my Path')
            def _h92(evt, state=state): self.vm.enrollAndFinish()
            ui.on_click("paths_z91", _h92)
