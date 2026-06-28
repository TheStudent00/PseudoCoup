def _ev(f):
    try:
        return f()
    except Exception:
        return None


def build(ui, content, viewModel):
    activePaths = _ev(lambda: viewModel.activePaths.collectAsStateWithLifecycle())
    pickerState = _ev(lambda: viewModel.pickerState.collectAsStateWithLifecycle())
    _id0 = "paths_z0"
    ui.define_box(_id0, "content", "V")
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
    else:
        for _i11, path in enumerate(_ev(lambda: activePaths) or []):
            _id12 = ("paths_z12" + "_" + str(_i11))
            ui.define_box(_id12, _id1, "V")
            definition = _ev(lambda: PathDefinition.findById(path.id))
            _id13 = ("paths_z13" + "_" + str(_i11))
            ui.define_box(_id13, _id12, "V")
            if _ev(lambda: onClick != None):
                _id15 = ("paths_z15" + "_" + str(_i11))
                ui.define_box(_id15, _id13, "V")
            else:
                _id16 = ("paths_z16" + "_" + str(_i11))
                ui.define_box(_id16, _id13, "V")
            _id17 = ("paths_z17" + "_" + str(_i11))
            ui.define_box(_id17, _id13, "V")
            _id18 = ("paths_z18" + "_" + str(_i11))
            ui.define_box(_id18, _id17, "H")
            ui.define_text(("paths_z19" + "_" + str(_i11)), _id18, _ev(lambda: path.name))
            ui.define_button(("paths_z20" + "_" + str(_i11)), _id18, 'Leave path')
            it = _ev(lambda: definition)
            if it is not None:
                ui.define_spacer_zone(("paths_z21" + "_" + str(_i11)), _id17)
                ui.define_text(("paths_z22" + "_" + str(_i11)), _id17, _ev(lambda: it.tagline))
                ui.define_spacer_zone(("paths_z23" + "_" + str(_i11)), _id17)
                _id24 = ("paths_z24" + "_" + str(_i11))
                ui.define_box(_id24, _id17, "H")
                _id25 = ("paths_z25" + "_" + str(_i11))
                ui.define_box(_id25, _id24, "V")
                _id26 = ("paths_z26" + "_" + str(_i11))
                ui.define_box(_id26, _id25, "V")
                ui.define_text(("paths_z27" + "_" + str(_i11)), _id26, 'Sessions')
                ui.define_text(("paths_z28" + "_" + str(_i11)), _id26, _ev(lambda: f"{it.minSessionsPerWeek}–{it.maxSessionsPerWeek}/week"))
                _id29 = ("paths_z29" + "_" + str(_i11))
                ui.define_box(_id29, _id24, "V")
                _id30 = ("paths_z30" + "_" + str(_i11))
                ui.define_box(_id30, _id29, "V")
                ui.define_text(("paths_z31" + "_" + str(_i11)), _id30, 'Target')
                ui.define_text(("paths_z32" + "_" + str(_i11)), _id30, _ev(lambda: f"{it.targetMinutesPerSession} min"))
                ui.define_spacer_zone(("paths_z33" + "_" + str(_i11)), _id17)
                ui.define_text(("paths_z34" + "_" + str(_i11)), _id17, 'The evidence')
                _id35 = ("paths_z35" + "_" + str(_i11))
                ui.define_box(_id35, _id17, "V")
                ui.define_text(("paths_z36" + "_" + str(_i11)), _id35, _ev(lambda: it.evidenceSummary))
                _id37 = ("paths_z37" + "_" + str(_i11))
                ui.define_box(_id37, _id35, "V")
                ui.define_spacer_zone(("paths_z38" + "_" + str(_i11)), _id17)
        if _ev(lambda: len(activePaths) == 1):
            _id40 = "paths_z40"
            ui.define_box(_id40, _id1, "V")
            ui.define_button("paths_z41", _id40, 'Add a second path')
    _id42 = "paths_z42"
    ui.define_box(_id42, _id0, "V")
    state = _ev(lambda: pickerState)
    if state is not None:
        _id43 = "paths_z43"
        ui.define_box(_id43, _id42, "V")
        title = _ev(lambda: ("Add a second path" if state.isAddingSecond else "Find your Path"))
        if state.isAddingSecond:
            subtitle = "Choose one more to work toward."
        else:
            subtitle = "Choose what matters to you. Select up to 2 paths."
        _id44 = "paths_z44"
        ui.define_box(_id44, _id43, "V")
        _id45 = "paths_z45"
        ui.define_box(_id45, _id44, "V")
        ui.define_text("paths_z46", _id45, _ev(lambda: subtitle))
        _id47 = "paths_z47"
        ui.define_box(_id47, _id44, "V")
        ui.define_text("paths_z48", _id47, _ev(lambda: title))
        ui.define_text("paths_z49", _id47, '✕')
        _id50 = "paths_z50"
        ui.define_box(_id50, _id44, "V")
        ui.define_button("paths_z51", _id50, 'Start my Path')
