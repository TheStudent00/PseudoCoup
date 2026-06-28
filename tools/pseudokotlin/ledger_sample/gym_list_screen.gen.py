def _ev(f):
    try:
        return f()
    except Exception:
        return None


def build(ui, content, viewModel):
    gyms = _ev(lambda: viewModel.gyms.collectAsStateWithLifecycle())
    activeGym = _ev(lambda: viewModel.activeGym.collectAsStateWithLifecycle())
    _id0 = "gym_list_z0"
    ui.define_box(_id0, content, "V")
    if _ev(lambda: (len(gyms) == 0)):
        _id2 = "gym_list_z2"
        ui.define_box(_id2, _id0, "V")
        ui.define_text("gym_list_z3", _id2, 'No gyms yet. Tap + to add one.')
    else:
        _id4 = "gym_list_z4"
        ui.define_box(_id4, _id0, "V")
        for _i5, gymWithEquipment in enumerate(_ev(lambda: gyms) or []):
            _id6 = ("gym_list_z6" + "_" + str(_i5))
            ui.define_box(_id6, _id4, "V")
            gym = _ev(lambda: gymWithEquipment.profile)
            equipmentList = _ev(lambda: gymWithEquipment.equipment)
            _id7 = ("gym_list_z7" + "_" + str(_i5))
            ui.define_box(_id7, _id6, "V")
            if _ev(lambda: onClick != None):
                _id9 = ("gym_list_z9" + "_" + str(_i5))
                ui.define_box(_id9, _id7, "V")
            else:
                _id10 = ("gym_list_z10" + "_" + str(_i5))
                ui.define_box(_id10, _id7, "V")
            _id11 = ("gym_list_z11" + "_" + str(_i5))
            ui.define_box(_id11, _id7, "V")
            _id12 = ("gym_list_z12" + "_" + str(_i5))
            ui.define_box(_id12, _id11, "H")
            ui.define_text(("gym_list_z13" + "_" + str(_i5)), _id12, _ev(lambda: gym.name))
            if _ev(lambda: (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id):
                _id15 = ("gym_list_z15" + "_" + str(_i5))
                ui.define_box(_id15, _id12, "V")
                ui.define_text(("gym_list_z16" + "_" + str(_i5)), _id15, '✓ Active')
            else:
                ui.define_button(("gym_list_z17" + "_" + str(_i5)), _id12, 'Set active')
            ui.define_spacer_zone(("gym_list_z18" + "_" + str(_i5)), _id11)
            type = _ev(lambda: gym.gymType)
            if type is not None:
                ui.define_text(("gym_list_z19" + "_" + str(_i5)), _id11, _ev(lambda: f"{type.emoji} {type.displayName}"))
            ui.define_spacer_zone(("gym_list_z20" + "_" + str(_i5)), _id11)
            _id21 = ("gym_list_z21" + "_" + str(_i5))
            ui.define_box(_id21, _id11, "H")
            _id22 = ("gym_list_z22" + "_" + str(_i5))
            ui.define_box(_id22, _id21, "V")
            _id23 = ("gym_list_z23" + "_" + str(_i5))
            ui.define_box(_id23, _id22, "V")
            ui.define_text(("gym_list_z24" + "_" + str(_i5)), _id23, 'Equipment')
            ui.define_text(("gym_list_z25" + "_" + str(_i5)), _id23, _ev(lambda: f"{len(equipmentList)} items"))
            ui.define_spacer_zone(("gym_list_z26" + "_" + str(_i5)), _id11)
            if _ev(lambda: (len(equipmentList) != 0)):
                ui.define_text(("gym_list_z28" + "_" + str(_i5)), _id11, 'Equipment')
                _id29 = ("gym_list_z29" + "_" + str(_i5))
                ui.define_box(_id29, _id11, "V")
                equipmentNames = _ev(lambda: equipmentList.joinToString(", ", (lambda it=None: it.name)))
                ui.define_text(("gym_list_z30" + "_" + str(_i5)), _id29, _ev(lambda: equipmentNames))
                _id31 = ("gym_list_z31" + "_" + str(_i5))
                ui.define_box(_id31, _id29, "V")
            else:
                ui.define_text(("gym_list_z32" + "_" + str(_i5)), _id11, 'No equipment listed')
            ui.define_spacer_zone(("gym_list_z33" + "_" + str(_i5)), _id11)
            _id34 = ("gym_list_z34" + "_" + str(_i5))
            ui.define_box(_id34, _id11, "H")
            ui.define_button(("gym_list_z35" + "_" + str(_i5)), _id34, 'Delete gym')
    _id36 = "gym_list_z36"
    ui.define_box(_id36, _id0, "V")
    ui.define_text("gym_list_z37", _id36, 'Gym profiles')
    ui.define_text("gym_list_z38", _id36, '←')
    ui.define_text("gym_list_z39", _id0, '+')
