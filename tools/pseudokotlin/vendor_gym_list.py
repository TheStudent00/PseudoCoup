"""Vendor the gym_list 1:1 backend + generated screen into WFL_PseudoCoup/src.
Run from PseudoCoup/tools/pseudokotlin. Produces committed .py (no transpiler at app runtime)."""
import os
import shutil
import sys

HERE = "/home/lucas/Programming/PseudoCoup/tools/pseudokotlin"
sys.path.insert(0, HERE)
import oracle as O                            # noqa: E402
import pseudoui_run as R                      # noqa: E402
from transpiler import KtToPy                 # noqa: E402

APP = "/home/lucas/Programming/WFL_PseudoCoup/src"
GEN = os.path.join(APP, "generated")
os.makedirs(GEN, exist_ok=True)

open(os.path.join(GEN, "__init__.py"), "w").write(
    '"""Generated 1:1-with-Kotlin backend for PseudoUI-generated screens (do not hand-edit)."""\n')

# 1. vendor kotlin_rt (the Kotlin stdlib runtime; stdlib-only deps)
shutil.copy(os.path.join(HERE, "runtime", "kotlin_rt.py"), os.path.join(GEN, "kotlin_rt.py"))

# 2. reactive shim: Kotlin Flow/StateFlow/coroutines -> PseudoCoup's synchronous pull model
open(os.path.join(GEN, "reactive_shim.py"), "w").write('''"""Reactive shim (vendored, fixed -- not per-screen): Kotlin Flow / StateFlow / coroutines ->
PseudoCoup's synchronous pull model, so a transpiled-from-Kotlin viewmodel runs headlessly."""
from generated.kotlin_rt import *          # noqa: F401,F403 -- emptyList/KtList/etc. for transpiled code


class StateFlow:
    def __init__(self, v=None): self.value = v
    def stateIn(self, *a): return self
    def asStateFlow(self): return self
    def asSharedFlow(self): return self
    def collectAsStateWithLifecycle(self, *a): return self.value
    def collectAsState(self, *a): return self.value
    def first(self): return self.value
    def emit(self, *a): pass


class Flow:
    def __init__(self, v): self._v = v
    def stateIn(self, *a): return StateFlow(self._v)
    def collectAsStateWithLifecycle(self, *a): return self._v
    def first(self): return self._v

    @property
    def value(self): return self._v


class _Scope:
    def launch(self, f):
        try:
            return f()
        except Exception:
            return None


class SharingStarted:
    @staticmethod
    def WhileSubscribed(*a): return None


viewModelScope = _Scope()
MutableStateFlow = StateFlow
MutableSharedFlow = StateFlow


def combine(*args):
    *flows, fn = args
    try:
        return Flow(fn(*[getattr(f, "value", f) for f in flows]))
    except Exception:
        return Flow(None)


def checkNotNull(x, *a): return x


class _Permissive:
    def __getattr__(self, n): return _Permissive()
    def __getitem__(self, k): return _Permissive()
    def __call__(self, *a, **k): return _Permissive()


Screen = _Permissive()
''')

# 3. the TRANSPILED viewmodel + entities + enum (1:1 with Kotlin), with shim imports
hdr = ("from generated.kotlin_rt import *          # noqa: F401,F403\n"
       "from generated.reactive_shim import *      # noqa: F401,F403\n\n\n")
parts = [KtToPy().transpile(open(O.find_one(O.MAIN, f), "rb").read())
         for f in ("GymType.kt", "GymProfileEntity.kt", "GymListViewModel.kt")]
open(os.path.join(GEN, "gym_list_kt.py"), "w").write(
    '"""Transpiled (KtToPy) GymType + GymProfileEntity/GymWithEquipment + GymListViewModel."""\n'
    + hdr + "\n\n".join(parts) + "\n")

# 4. the Room-DAO -> InMemoryDb adapter (the framework boundary) + int->enum lift + make_vm
open(os.path.join(GEN, "gym_list_backend.py"), "w").write('''"""gym_list backend: the Room-DAO -> InMemoryDb adapter (framework boundary) + the int->enum
lift, presenting the transpiled Kotlin shapes to the transpiled GymListViewModel."""
from generated import kotlin_rt as rt
from generated.reactive_shim import Flow
from generated.gym_list_kt import (GymListViewModel, GymProfileEntity, GymWithEquipment, GymType)
from domain.gym_service import GymService
from data.repository.gym_equipment_repository import GymEquipmentRepository


def _lift(g):
    gt = GymType.entries[int(g.gymType)] if g.gymType is not None else None
    return GymProfileEntity(g.id, g.name, g.isActive, gt, g.createdAt, g.updatedAt)


class _GymRepo:
    """getAllWithEquipment / getActive over the kit's InMemoryDb, in the Kotlin shapes."""
    def __init__(self, db): self.db = db

    def getAllWithEquipment(self):
        eq = GymEquipmentRepository(self.db)
        return Flow(rt.KtList(GymWithEquipment(_lift(g), rt.KtList(eq.get_by_gym(g.id)))
                              for g in GymService(self.db).get_all()))

    def getActive(self):
        act = [g for g in GymService(self.db).get_all() if g.isActive]
        return Flow(_lift(act[0]) if act else None)

    def setActive(self, gid): GymService(self.db).set_active(gid)

    def deleteGym(self, gid): GymService(self.db).delete_gym(gid)


def make_vm(db):
    return GymListViewModel(_GymRepo(db))
''')

# 5. the generated screen, wired to the vendored backend
cname, ir = R.build_ir(O.find_one(O.MAIN, "GymListScreen.kt"))
src = R.emit_app_screen(ir, "gym_list", "GymListScreenGen")
src = "from generated.gym_list_backend import make_vm\n\n\n" + src
src = src.replace("self.vm = build_transpiled_vm('gym_list', db)", "self.vm = make_vm(db)")
src = ('"""GENERATED by PseudoUI from Compose GymListScreen.kt -- drop-in for the hand-built\n'
       'GymListScreen, backed by the transpiled (1:1-with-Kotlin) GymListViewModel."""\n' + src)
open(os.path.join(APP, "ui", "gym_list_screen_gen.py"), "w").write(src)

print("vendored:")
for f in ("generated/kotlin_rt.py", "generated/reactive_shim.py", "generated/gym_list_kt.py",
          "generated/gym_list_backend.py", "ui/gym_list_screen_gen.py"):
    print(f"  {f}  ({os.path.getsize(os.path.join(APP, f))} bytes)")
