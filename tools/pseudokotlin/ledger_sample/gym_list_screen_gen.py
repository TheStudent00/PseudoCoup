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


class GymListScreenGen:
    def __init__(self, db):
        self.db = db
        self.vm = None
        self._vm_sel = None
        self.owned_ids = []

    def screen_id(self):
        return 'gym_list'

    def _nav_back(self):
        self.router.navigate('you')
    def _nav_editor(self, gymId=None):
        if gymId is None:
            self.router.navigate('gym_create_wizard')
        else:
            self.router.selected_id = gymId
            self.router.navigate('gym_editor')

    def build(self, ui, content_zone_id, router):
        self.owned_ids = []
        ui = _Track(ui, self.owned_ids)
        self.router = router
        _sel = getattr(router, 'selected_id', None)
        if self.vm is None or self._vm_sel != _sel:
            self.vm = build_transpiled_vm('gym_list', self.db, _sel)
            self._vm_sel = _sel
        viewModel = self.vm
        content = content_zone_id
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
                def _h8(evt, gymWithEquipment=gymWithEquipment): self._nav_editor(gymWithEquipment.profile.id)
                ui.on_click(_id7, _h8)
                if _ev(lambda: onClick != None):
                    _id10 = ("gym_list_z10" + "_" + str(_i5))
                    ui.define_box(_id10, _id7, "V")
                    def _h11(evt, gymWithEquipment=gymWithEquipment): self._nav_editor(gymWithEquipment.profile.id)
                    ui.on_click(_id10, _h11)
                else:
                    _id12 = ("gym_list_z12" + "_" + str(_i5))
                    ui.define_box(_id12, _id7, "V")
                _id13 = ("gym_list_z13" + "_" + str(_i5))
                ui.define_box(_id13, _id7, "V")
                _id14 = ("gym_list_z14" + "_" + str(_i5))
                ui.define_box(_id14, _id13, "H")
                ui.define_text(("gym_list_z15" + "_" + str(_i5)), _id14, _ev(lambda: gym.name))
                if _ev(lambda: (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id):
                    _id17 = ("gym_list_z17" + "_" + str(_i5))
                    ui.define_box(_id17, _id14, "V")
                    ui.define_text(("gym_list_z18" + "_" + str(_i5)), _id17, '✓ Active')
                else:
                    ui.define_button(("gym_list_z19" + "_" + str(_i5)), _id14, 'Set active')
                    def _h20(evt, gymWithEquipment=gymWithEquipment): self.vm.setActive(gymWithEquipment.profile)
                    ui.on_click(("gym_list_z19" + "_" + str(_i5)), _h20)
                ui.define_spacer_zone(("gym_list_z21" + "_" + str(_i5)), _id13)
                type = _ev(lambda: gym.gymType)
                if type is not None:
                    ui.define_text(("gym_list_z22" + "_" + str(_i5)), _id13, _ev(lambda: f"{type.emoji} {type.displayName}"))
                ui.define_spacer_zone(("gym_list_z23" + "_" + str(_i5)), _id13)
                _id24 = ("gym_list_z24" + "_" + str(_i5))
                ui.define_box(_id24, _id13, "H")
                _id25 = ("gym_list_z25" + "_" + str(_i5))
                ui.define_box(_id25, _id24, "V")
                _id26 = ("gym_list_z26" + "_" + str(_i5))
                ui.define_box(_id26, _id25, "V")
                ui.define_text(("gym_list_z27" + "_" + str(_i5)), _id26, 'Equipment')
                ui.define_text(("gym_list_z28" + "_" + str(_i5)), _id26, _ev(lambda: f"{len(equipmentList)} items"))
                ui.define_spacer_zone(("gym_list_z29" + "_" + str(_i5)), _id13)
                if _ev(lambda: (len(equipmentList) != 0)):
                    ui.define_text(("gym_list_z31" + "_" + str(_i5)), _id13, 'Equipment')
                    _id32 = ("gym_list_z32" + "_" + str(_i5))
                    ui.define_box(_id32, _id13, "V")
                    equipmentNames = _ev(lambda: equipmentList.joinToString(", ", (lambda it=None: it.name)))
                    ui.define_text(("gym_list_z33" + "_" + str(_i5)), _id32, _ev(lambda: equipmentNames))
                    _id34 = ("gym_list_z34" + "_" + str(_i5))
                    ui.define_box(_id34, _id32, "V")
                else:
                    ui.define_text(("gym_list_z35" + "_" + str(_i5)), _id13, 'No equipment listed')
                ui.define_spacer_zone(("gym_list_z36" + "_" + str(_i5)), _id13)
                _id37 = ("gym_list_z37" + "_" + str(_i5))
                ui.define_box(_id37, _id13, "H")
                ui.define_button(("gym_list_z38" + "_" + str(_i5)), _id37, 'Delete gym')
                def _h39(evt, gymWithEquipment=gymWithEquipment): self.vm.delete(gymWithEquipment.profile)
                ui.on_click(("gym_list_z38" + "_" + str(_i5)), _h39)
        _id40 = "gym_list_z40"
        ui.define_box(_id40, _id0, "V")
        ui.define_text("gym_list_z41", _id40, 'Gym profiles')
        ui.define_text("gym_list_z42", _id40, '←')
        def _h43(evt): self._nav_back()
        ui.on_click("gym_list_z42", _h43)
        ui.define_text("gym_list_z44", _id0, '+')
        def _h45(evt): self._nav_editor(None)
        ui.on_click("gym_list_z44", _h45)
