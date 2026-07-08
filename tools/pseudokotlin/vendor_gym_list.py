"""Vendor the gym_list 1:1 backend + generated screen into WFL_PseudoCoup/src.
Run from PseudoCoup/tools/pseudokotlin. Produces committed .py (no transpiler at app runtime)."""
import os
import shutil
import sys

HERE = "/home/lucas/Programming/PseudoCoup_v0/tools/pseudokotlin"
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


def _notify_recompose():
    """A MutableStateFlow write is the Kotlin analog of a PseudoCoup State.set() -- it must request a
    repaint. Lazy + guarded so this shim stays importable without the app's reactive module."""
    try:
        from reactive import invalidate as _inv
        _inv()
    except Exception:                                  # noqa: BLE001 -- no recompose host (sandbox)
        pass


class _FlowOps:
    """Pull-model Flow operators: each transforms the LATEST emission and is re-read on access (a
    cold Flow). Approximate (no backpressure/timing) but enough to run flow-chaining VMs. `_read()`
    yields the current value; subclasses define it."""
    def map(self, f): return Flow(lambda: f(self._read()))
    def mapLatest(self, f): return Flow(lambda: f(self._read()))
    def filter(self, p):
        def q():
            v = self._read()
            return v if p(v) else None
        return Flow(q)
    def flatMapLatest(self, f):
        def q():
            inner = f(self._read())
            return inner._read() if hasattr(inner, "_read") else inner
        return Flow(q)
    def onEach(self, f):
        def q():
            v = self._read(); f(v); return v
        return Flow(q)
    def onStart(self, *a): return self
    def distinctUntilChanged(self, *a): return self
    def catch(self, *a): return self
    def flowOn(self, *a): return self
    def debounce(self, *a): return self
    def sample(self, *a): return self
    def take(self, *a): return self
    def drop(self, *a): return self
    def collect(self, f):
        v = self._read()
        if v is not None: f(v)
    def collectLatest(self, f): self.collect(f)


class StateFlow(_FlowOps):
    # MutableStateFlow -> State: writing `.value` invalidates the recompose frame, so a UI-FLAG flow
    # (dialog-open, search query) repaints like Compose snapshot state would. Reads stay cheap.
    # Doubles as MutableSharedFlow: `collect` registers a handler, `emit` notifies them synchronously
    # (the pull analog of a LaunchedEffect collecting a nav event).
    def __init__(self, v=None): self._value = v; self._collectors = []
    def _read(self): return self._value
    @property
    def value(self): return self._value
    @value.setter
    def value(self, v):
        changed = self._value != v
        self._value = v
        if changed: _notify_recompose()
    def update(self, f): self.value = f(self._value)   # MutableStateFlow.update { it.copy(...) }
    def stateIn(self, *a): return self
    def asStateFlow(self): return self
    def asSharedFlow(self): return self
    def collectAsStateWithLifecycle(self, *a): return self._value
    def collectAsState(self, *a): return self._value
    def first(self): return self._value
    def collect(self, h): self._collectors.append(h)               # SharedFlow: register
    def emit(self, *a):                                            # SharedFlow event -> notify
        for h in list(self._collectors): h(*a)


class Flow(_FlowOps):
    # `v` may be a value OR a thunk. A Kotlin Flow re-emits on every db change; the pull analog is
    # to re-read on each access -- so `.value` calls the thunk fresh and stateIn returns the SAME
    # lazy flow (not a frozen snapshot). Without this the screen shows stale data after a mutation.
    def __init__(self, v): self._v = v
    def _read(self): return self._v() if callable(self._v) else self._v
    def _val(self): return self._read()                # back-compat alias
    def stateIn(self, *a): return self
    def collectAsStateWithLifecycle(self, *a): return self._read()
    def collectAsState(self, *a): return self._read()
    def first(self): return self._read()

    @property
    def value(self): return self._read()


def flowOf(*xs): return Flow(lambda: xs[-1] if xs else None)   # latest emission
def emptyFlow(): return Flow(lambda: None)


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

# 3b. the TRANSPILED GymRepository -- the real Kotlin repository LOGIC (setActive's deactivate+
#     activate, deleteGym's getById+delete, getAllWithEquipment delegation). DAOs bridged in (4).
repo_hdr = ('"""Transpiled (KtToPy) GymRepository -- the real Kotlin repository LOGIC running in the\n'
            'app (setActive deactivate+activate, deleteGym getById+delete). Vendored; regenerate via\n'
            'tools/pseudokotlin/vendor_gym_list.py. The DAOs are bridged to the app store in\n'
            'gym_list_backend.py."""\n'
            "import time as _time\n"
            "import uuid as _uuid\n"
            "from generated.gym_list_kt import GymProfileEntity, GymWithEquipment, GymType  # noqa: F401\n\n\n"
            "class System:\n"
            "    @staticmethod\n"
            "    def currentTimeMillis(): return int(_time.time() * 1000)\n\n\n"
            "class _Uuid:\n"
            "    def toString(self): return str(_uuid.uuid4())\n\n\n"
            "class UUID:\n"
            "    @staticmethod\n"
            "    def randomUUID(): return _Uuid()\n\n\n")
repo_src = KtToPy().transpile(open(O.find_one(O.MAIN, "GymRepository.kt"), "rb").read())
open(os.path.join(GEN, "gym_repository_kt.py"), "w").write(repo_hdr + repo_src + "\n")

# 4. Room-DAO -> InMemoryDb BRIDGES (the framework boundary, ported once) + int->enum lift. The
#    repository LOGIC above runs transpiled-from-Kotlin; only the DAO CRUD is bridged here.
open(os.path.join(GEN, "gym_list_backend.py"), "w").write('''"""gym_list backend: GymProfileDao/GymEquipmentDao -> InMemoryDb BRIDGES (framework boundary,
ported once) + int->enum lift. These feed the TRANSPILED GymRepository, which feeds the transpiled
GymListViewModel -- so the repository logic traces to Kotlin; only DAO CRUD is hand-bridged."""
from generated import kotlin_rt as rt
from generated.reactive_shim import Flow
from generated.gym_list_kt import (GymListViewModel, GymProfileEntity, GymWithEquipment, GymType)
from generated.gym_repository_kt import GymRepository
from data.repository.gym_profile_repository import GymProfileRepository
from data.repository.gym_equipment_repository import GymEquipmentRepository
from reactive import invalidate                  # db mutation -> repaint (Kotlin Flow re-emit analog)


def _lift(g):
    gt = GymType.entries[int(g.gymType)] if g.gymType is not None else None
    return GymProfileEntity(g.id, g.name, g.isActive, gt, g.createdAt, g.updatedAt)


class _ProfileDao:
    """GymProfileDao -> InMemoryDb: camelCase Kotlin names, Flow-wrapped reads (lazy re-query),
    rows lifted to the transpiled Kotlin entity shape. Mutations request a repaint."""
    def __init__(self, db):
        self._p = GymProfileRepository(db)
        self._e = GymEquipmentRepository(db)

    def getAll(self):
        return Flow(lambda: rt.KtList(_lift(g) for g in self._p.get_all()))

    def getAllWithEquipment(self):
        def q():                                  # thunk: re-queried each read (Flow re-emits)
            return rt.KtList(GymWithEquipment(_lift(g), rt.KtList(self._e.get_by_gym(g.id)))
                             for g in self._p.get_all())
        return Flow(q)

    def getById(self, id):
        def q():
            g = self._p.get_by_id(id)
            return _lift(g) if g is not None else None
        return Flow(q)

    def getActive(self):
        def q():
            a = self._p.get_active()
            return _lift(a) if a is not None else None
        return Flow(q)

    def insert(self, gym): self._p.insert(gym); invalidate()
    def update(self, gym): self._p.update(gym); invalidate()
    def delete(self, gym): self._p.delete(gym); invalidate()
    def deactivateAll(self, now): self._p.deactivate_all(now); invalidate()
    def activate(self, gymId, now): self._p.activate(gymId, now); invalidate()


class _EquipmentDao:
    """GymEquipmentDao -> InMemoryDb."""
    def __init__(self, db): self._e = GymEquipmentRepository(db)

    def getByGym(self, gymId):
        return Flow(lambda: rt.KtList(self._e.get_by_gym(gymId)))

    def getAvailableByGym(self, gymId):
        return Flow(lambda: rt.KtList(self._e.get_available_by_gym(gymId)))

    def insert(self, e): self._e.insert(e); invalidate()
    def insertAll(self, es): self._e.insert_all(es); invalidate()
    def delete(self, e): self._e.delete(e); invalidate()
    def deleteAllForGym(self, gymId): self._e.delete_all_for_gym(gymId); invalidate()


class _Database:
    def withTransaction(self, block): return block()   # InMemoryDb is synchronous -- run inline


def make_vm(db, sel=None):
    repo = GymRepository(_Database(), _ProfileDao(db), _EquipmentDao(db))
    return GymListViewModel(repo)
''')

# 5. the generated screen, wired to the vendored backend
cname, ir = R.build_ir(O.find_one(O.MAIN, "GymListScreen.kt"))
src = R.emit_app_screen(ir, "gym_list", "GymListScreenGen")
src = "from generated.gym_list_backend import make_vm\n\n\n" + src
src = src.replace("self.vm = build_transpiled_vm('gym_list', self.db, _sel)", "self.vm = make_vm(self.db, _sel)")
src = ('"""GENERATED by PseudoUI from Compose GymListScreen.kt -- drop-in for the hand-built\n'
       'GymListScreen, backed by the transpiled (1:1-with-Kotlin) GymListViewModel."""\n' + src)
open(os.path.join(APP, "ui", "gym_list_screen_gen.py"), "w").write(src)

print("vendored:")
for f in ("generated/kotlin_rt.py", "generated/reactive_shim.py", "generated/gym_list_kt.py",
          "generated/gym_repository_kt.py", "generated/gym_list_backend.py",
          "ui/gym_list_screen_gen.py"):
    print(f"  {f}  ({os.path.getsize(os.path.join(APP, f))} bytes)")
