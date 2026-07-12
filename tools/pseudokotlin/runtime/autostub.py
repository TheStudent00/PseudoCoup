"""
runtime/autostub.py — the SINGLE front door for every external name a transpiled file imports.

`from runtime.autostub import X` resolves X to:
  - the REAL wrapper, if a runtime module provides it (kotlin_rt / room / java_rt / json_rt / coroutines /
    android_rt / numbers, via the registry), OR
  - an inert Stub, otherwise.

So the hand-written real wrappers and the auto-generated stubs are ONE system: real where we have it, inert
elsewhere. A UI file's `Button` is a Stub today and becomes the real kit widget the moment a wrapper
provides it -- with no change to the transpiled code. This is the auto-generated equivalent of writing a
`UI.B` wrapper file by hand: the name always BINDS, so a transpiled file always LOADS (no NameError); an
un-wrapped one just does nothing yet.

Every name that falls through to a Stub is recorded in STUBBED, so "inert" is visible, never silent -- a
NON-UI name landing here is a real gap (externals.py asserts that set is empty for the foundation).
"""
import builtins as _builtins
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STUBBED = {}        # name -> the Stub subclass manufactured for it (the inert inventory)
_REAL = None        # cached {name -> real wrapper object}, merged across the runtime modules

# DEGRADATIONS tracks when a stub is actually USED AS A VALUE OR ACTION (coerced to a number, or
# called) -- as opposed to STUBBED, which only records that a name WAS manufactured. A name landing
# in STUBBED is silent-but-inert; a name landing in DEGRADATIONS actually did something (or nothing,
# invisibly) at runtime -- e.g. a stubbed PaddingValues' bottom inset coerced to int() -> 0, silently
# putting a button under the nav bar, or a stubbed onClick handler called -> a dead tap.
# Keyed by (stub_name, op) -> {"count": int, "where": "basename:lineno", "sample_stack": str}.
DEGRADATIONS = {}

_RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))


def _loud():
    return os.environ.get("STUB_LOUD", "").strip().lower() not in ("", "0", "false", "no")


def _strict():
    return os.environ.get("STUB_STRICT", "").strip().lower() not in ("", "0", "false", "no")


def _note_degrade(op, stub_obj):
    """Record that `stub_obj` (an inert Stub instance) degraded via `op` ("num" or "call"). FAST PATH
    (key already seen): just bump the count -- O(1) dict work, no stack walk, no I/O. SLOW PATH (first
    occurrence for this (name, op)): walk the stack to find the real transpiled-app/kit call site (the
    first frame outside this runtime package), record it, and optionally print it (STUB_LOUD)."""
    name = type(stub_obj).__name__
    key = (name, op)
    entry = DEGRADATIONS.get(key)
    if entry is not None:
        entry["count"] += 1                 # FAST PATH: no stack walk on repeat hits
        if _strict():
            raise RuntimeError(f"stub degrade: {name}.{op} -> inert at {entry['where']}")
        return
    # SLOW PATH: first time we've seen this (name, op) -- find the real call site.
    where = "<unknown>"
    stack = traceback.extract_stack()
    for frame in reversed(stack[:-1]):      # skip this frame itself (_note_degrade)
        fn = frame.filename
        if fn == os.path.abspath(__file__) or f"{os.sep}runtime{os.sep}" in fn:
            continue                        # skip frames inside autostub.py / the runtime package
        where = f"{os.path.basename(fn)}:{frame.lineno}"
        break
    entry = DEGRADATIONS[key] = {
        "count": 1,
        "where": where,
        "sample_stack": "".join(traceback.format_list(stack[-6:])),
    }
    if _loud():
        print(f"STUB-DEGRADE {op}: {name} -> inert at {where}", file=sys.stderr)
    if _strict():
        raise RuntimeError(f"stub degrade: {name}.{op} -> inert at {where}")


def degradation_report():
    """Sorted list of [{"name", "op", "count", "where"}, ...], most-frequent first."""
    rows = [
        {"name": name, "op": op, "count": v["count"], "where": v["where"]}
        for (name, op), v in DEGRADATIONS.items()
    ]
    rows.sort(key=lambda r: r["count"], reverse=True)
    return rows


def reset_degradations():
    """Clear DEGRADATIONS (for tests)."""
    DEGRADATIONS.clear()


def _real():
    global _REAL
    if _REAL is None:
        import registry
        _REAL = registry.namespace()
    return _REAL


class _StubMeta(type):
    """Makes a Stub CLASS permissive: a missing attribute or a subscript yields another stub, so the class
    works as a value, a base class, an isinstance target, AND a generic (`Stub[T]`)."""
    def __getattr__(cls, name):
        return stub(f"{cls.__name__}.{name}")

    def __getitem__(cls, _key):
        return cls


class Stub(metaclass=_StubMeta):
    """An inert object. Constructing / calling / reading any attribute / indexing / iterating it all
    succeed and yield stubs -- faithful to STRUCTURE (the name and call exist) but not BEHAVIOUR (it does
    nothing). `__init__` swallows any args, so `Button("Save", onClick = …)` just works."""
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, name):
        return stub(name)()

    def __call__(self, *a, **k):
        _note_degrade("call", self)         # a handler/action silently doing nothing -- worth knowing
        return self

    def __getitem__(self, _key):
        return self

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def __contains__(self, _x):
        return False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    # numeric / value usage: arithmetic stays a stub (chains don't crash), conversions give a neutral
    # value, ordered comparisons are False -- so `dp(8) + dp(16)`, `int(x)`, `x < y` render instead of
    # raising. (A kind-aware NUMERIC stub refines this further; this is the safe floor for every stub.)
    def _id(self, *a):
        return self

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = _id
    __truediv__ = __rtruediv__ = __floordiv__ = __mod__ = __neg__ = __pos__ = __abs__ = _id

    # Only "num" (numeric coercion) and "call" are hooked below -- these two ops are the ones that
    # cause silent WRONG BEHAVIOUR (a layout computed from an inert 0, or a handler that fires but does
    # nothing). __getattr__/__bool__/__iter__/arithmetic are deliberately left un-hooked: attribute
    # access and truthiness of a stub are extremely common, mostly-benign CHAINING (e.g. `x.copy().foo`,
    # `if maybeStub:`) that would make the registry noisy without pinpointing an actual bug; arithmetic
    # on stubs likewise just propagates another inert stub, not a wrong number, until it's finally
    # coerced (int/float/index) or invoked (call) -- which is exactly where we hook.
    def __int__(self):
        _note_degrade("num", self)
        return 0

    def __float__(self):
        _note_degrade("num", self)
        return 0.0

    def __index__(self):
        _note_degrade("num", self)
        return 0

    def __lt__(self, _o):
        return False

    __gt__ = __le__ = __ge__ = __lt__

    def __repr__(self):
        return f"<stub {type(self).__name__}>"


def stub(name):
    """The cached inert Stub subclass for `name` (the same external name is one type everywhere)."""
    s = STUBBED.get(name)
    if s is None:
        s = STUBBED[name] = _StubMeta(str(name), (Stub,), {})
    return s


_OBJS = {}      # name -> the one singleton instance manufactured for an 'obj'-kind name


def _kind(name):
    try:
        import surface                      # AST-classified kind (obj/func/class/value); needs the foundation
        return surface.kinds().get(name)
    except Exception:                       # noqa: BLE001 -- no foundation in scope -> permissive default
        return None


def __getattr__(name):                      # PEP 562: `from runtime.autostub import X`
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)          # leave dunders (e.g. __path__) to Python's normal machinery
    real = _real().get(name)
    if real is not None:                    # a hand-written runtime wrapper
        return real
    bi = getattr(_builtins, name, None)     # a Kotlin stdlib name that IS a Python builtin (abs/min/max…)
    if bi is not None:
        return bi
    # no equivalent -> an inert stub, SHAPED by its AST kind: a Kotlin object/namespace becomes ONE singleton
    # instance (not a class); a class/function/value stays the permissive Stub class (callable, base-able).
    if _kind(name) == "obj":
        if name not in _OBJS:
            _OBJS[name] = stub(name)()
        return _OBJS[name]
    return stub(name)


if __name__ == "__main__":
    import runtime.autostub as A                       # use ONE module instance (not __main__'s copy)
    assert A.KtList.__name__ == "KtList", A.KtList      # a real wrapper -> the real class
    W = A.SomeUnwrappedWidget                           # no wrapper -> an inert stub
    b = W("Save", onClick=lambda: None)                # swallows args
    assert b.copy().foo().bar is not None              # any call/attr chain stays inert, never crashes
    assert b + 1 is b and int(b) == 0 and (b < 5) is False    # robust: arithmetic/convert/compare, no crash
    assert "SomeUnwrappedWidget" in A.STUBBED and "KtList" not in A.STUBBED

    class Screen(W):                                   # usable as a base class
        pass
    assert isinstance(Screen(), W)                     # and as an isinstance target
    print("autostub self-test: OK")
