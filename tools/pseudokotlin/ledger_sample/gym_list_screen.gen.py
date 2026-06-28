def _ev(f):
    try:
        return f()
    except Exception:
        return None


def build(ui, content, viewModel):
    gyms = viewModel.gyms.collectAsStateWithLifecycle()
    activeGym = viewModel.activeGym.collectAsStateWithLifecycle()
    _id0 = "gym_list_z0"
    ui.define_box(_id0, "content", "V")
    if _ev(lambda: (len(gyms) == 0)):
        _id1 = "gym_list_z1"
        ui.define_box(_id1, _id0, "V")
        ui.define_text("gym_list_z2", _id1, 'No gyms yet. Tap + to add one.')
    else:
        _id3 = "gym_list_z3"
        ui.define_box(_id3, _id0, "V")
        for _i4, gymWithEquipment in enumerate(gyms):
            _id5 = ("gym_list_z5" + "_" + str(_i4))
            ui.define_box(_id5, _id3, "V")
            gym = gymWithEquipment.profile
            equipmentList = gymWithEquipment.equipment
            _id6 = ("gym_list_z6" + "_" + str(_i4))
            ui.define_box(_id6, _id5, "V")
            if _ev(lambda: onClick != None):
                _id7 = ("gym_list_z7" + "_" + str(_i4))
                ui.define_box(_id7, _id6, "V")
            else:
                _id8 = ("gym_list_z8" + "_" + str(_i4))
                ui.define_box(_id8, _id6, "V")
            _id9 = ("gym_list_z9" + "_" + str(_i4))
            ui.define_box(_id9, _id6, "V")
            _id10 = ("gym_list_z10" + "_" + str(_i4))
            ui.define_box(_id10, _id9, "H")
            ui.define_text(("gym_list_z11" + "_" + str(_i4)), _id10, gym.name)
            if _ev(lambda: (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id):
                _id12 = ("gym_list_z12" + "_" + str(_i4))
                ui.define_box(_id12, _id10, "V")
                ui.define_text(("gym_list_z13" + "_" + str(_i4)), _id12, 'Active')
            else:
                ui.define_button(("gym_list_z14" + "_" + str(_i4)), _id10, 'Set active')
            ui.define_spacer_zone(("gym_list_z15" + "_" + str(_i4)), _id9)
            type = gym.gymType
            if type is not None:
                ui.define_text(("gym_list_z16" + "_" + str(_i4)), _id9, f"{type.emoji} {type.displayName}")
            ui.define_spacer_zone(("gym_list_z17" + "_" + str(_i4)), _id9)
            _id18 = ("gym_list_z18" + "_" + str(_i4))
            ui.define_box(_id18, _id9, "H")
            _id19 = ("gym_list_z19" + "_" + str(_i4))
            ui.define_box(_id19, _id18, "V")
            _id20 = ("gym_list_z20" + "_" + str(_i4))
            ui.define_box(_id20, _id19, "V")
            ui.define_text(("gym_list_z21" + "_" + str(_i4)), _id20, 'Equipment')
            ui.define_text(("gym_list_z22" + "_" + str(_i4)), _id20, f"{len(equipmentList)} items")
            ui.define_spacer_zone(("gym_list_z23" + "_" + str(_i4)), _id9)
            if _ev(lambda: (len(equipmentList) != 0)):
                ui.define_text(("gym_list_z24" + "_" + str(_i4)), _id9, 'Equipment')
                _id25 = ("gym_list_z25" + "_" + str(_i4))
                ui.define_box(_id25, _id9, "V")
                equipmentNames = equipmentList.joinToString(", ", (lambda it=None: it.name))
                ui.define_text(("gym_list_z26" + "_" + str(_i4)), _id25, equipmentNames)
                _id27 = ("gym_list_z27" + "_" + str(_i4))
                ui.define_box(_id27, _id25, "V")
            else:
                ui.define_text(("gym_list_z28" + "_" + str(_i4)), _id9, 'No equipment listed')
            ui.define_spacer_zone(("gym_list_z29" + "_" + str(_i4)), _id9)
            _id30 = ("gym_list_z30" + "_" + str(_i4))
            ui.define_box(_id30, _id9, "H")
            ui.define_button(("gym_list_z31" + "_" + str(_i4)), _id30, 'Delete gym')
    _id32 = "gym_list_z32"
    ui.define_box(_id32, _id0, "V")
    ui.define_text("gym_list_z33", _id32, 'Gym profiles')
    ui.define_icon("gym_list_z34", _id32, 'Back')
    ui.define_icon("gym_list_z35", _id0, 'Add gym')
