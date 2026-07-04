"""extras.py -- the remaining stdlib / platform names, filled.

Real where behaviour matters: kotlin.math (PI/cos/sin/abs), a real Random, a real viewModelScope (a
CoroutineScope so viewModelScope.launch runs), delay as a synchronous no-op. Permissive-structural for the
edge platform bits the render doesn't exercise: java.time extras, Uri, and DI/annotation markers. Completes
the binding so these are provided wrappers, not autostub stubs.
"""
import math as _math
import random as _random
import builtins as _bi
import runtime.coroutines as _coro


class _P:
    """A permissive real value: attr/call/index all yield it, arithmetic/compare-safe."""
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, _n):
        return _P_

    def __call__(self, *a, **k):
        return _P_

    def __getitem__(self, _k):
        return _P_

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def _id(self, *a):
        return self

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = _id
    __truediv__ = __rtruediv__ = __floordiv__ = __mod__ = __neg__ = __pos__ = __abs__ = _id

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __index__(self):
        return 0

    def __lt__(self, _o):
        return False

    __gt__ = __le__ = __ge__ = __lt__

    def __repr__(self):
        return "<extra>"


_P_ = _P()


def _identity_deco(x=None, *a, **k):        # an annotation used as @X or X(...) -> pass the target through
    return x if callable(x) else _P_


# ---- kotlin.math ------------------------------------------------------------------------------- #
PI = _math.pi
abs = _bi.abs


def cos(x=0.0):
    return _math.cos(x)


def sin(x=0.0):
    return _math.sin(x)


class Random:                                # kotlin.random.Random (+ its Default companion)
    def __init__(self, *a, **k):
        self._r = _random.Random()

    def nextInt(self, a=None, b=None):
        if a is None:
            return self._r.randint(0, 2 ** 31 - 1)
        if b is None:
            return self._r.randrange(int(a)) if a else 0
        return self._r.randint(int(a), int(b) - 1)

    def nextLong(self, *a):
        return self.nextInt(*a)

    def nextDouble(self, *a):
        return self._r.random()

    def nextBoolean(self):
        return self._r.random() < 0.5


Random.Default = Random()


# ---- coroutines / flow (free-name forms; the real behaviour is the Flow methods in coroutines.py) --- #
def delay(*a, **k):                          # synchronous model -> no wait
    return None


FlowPreview = _identity_deco
SharedFlow = _P_
asSharedFlow = collectLatest = debounce = distinctUntilChanged = _P_
viewModelScope = _coro.CoroutineScope()      # real scope -> viewModelScope.launch runs the block


# ---- java.time extras (permissive; DayOfWeek and TextStyle are REAL in java_rt) ----------------- #
WeekFields = _P_


# ---- android / lifecycle / hilt / room markers ------------------------------------------------- #
Uri = _P_


class SavedStateHandle:
    """androidx SavedStateHandle: the key->value holder navigation fills with the route's arguments (the
    'which item?' input -- e.g. gymId for 'edit THIS gym'). Missing key -> None (Kotlin's get is nullable),
    which is the launched-directly / create-new state. Navigation supplies real values when it routes."""
    def __init__(self, args=None):
        self._d = dict(args or {})

    def __getitem__(self, k):
        return self._d.get(k)

    def get(self, k, default=None):
        v = self._d.get(k)
        return default if v is None else v

    def __setitem__(self, k, v):
        self._d[k] = v

    def set(self, k, v):
        self._d[k] = v

    def contains(self, k):
        return k in self._d
HiltViewModel = _identity_deco
Delete = _identity_deco


class ViewModel:                             # androidx.lifecycle.ViewModel -- a base a VM may extend
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, _n):
        return _P_


_VM_FACTORY = None


def set_vm_factory(fn):
    """The render layer installs the assembler here: fn(cls) -> a real ViewModel (wired to the db and the
    current navigation arguments) or None when it can't be built fully real."""
    global _VM_FACTORY
    _VM_FACTORY = fn


def hiltViewModel(cls=None, *a, **k):        # DI entry -- called per screen call, with the declared type
    if _VM_FACTORY is not None and isinstance(cls, type):
        vm = _VM_FACTORY(cls)
        if vm is not None:
            return vm
    return _P_                               # no factory / not fully buildable -> inert placeholder
