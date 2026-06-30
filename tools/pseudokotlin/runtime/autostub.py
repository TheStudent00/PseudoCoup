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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STUBBED = {}        # name -> the Stub subclass manufactured for it (the inert inventory)
_REAL = None        # cached {name -> real wrapper object}, merged across the runtime modules


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

    def __repr__(self):
        return f"<stub {type(self).__name__}>"


def stub(name):
    """The cached inert Stub subclass for `name` (the same external name is one type everywhere)."""
    s = STUBBED.get(name)
    if s is None:
        s = STUBBED[name] = _StubMeta(str(name), (Stub,), {})
    return s


def __getattr__(name):                      # PEP 562: `from runtime.autostub import X`
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)          # leave dunders (e.g. __path__) to Python's normal machinery
    real = _real().get(name)
    if real is not None:                    # a hand-written runtime wrapper
        return real
    bi = getattr(_builtins, name, None)     # a Kotlin stdlib name that IS a Python builtin (abs/min/max…)
    if bi is not None:
        return bi
    return stub(name)                       # no equivalent -> inert (recorded in STUBBED)


if __name__ == "__main__":
    import runtime.autostub as A                       # use ONE module instance (not __main__'s copy)
    assert A.KtList.__name__ == "KtList", A.KtList      # a real wrapper -> the real class
    b = A.Button("Save", onClick=lambda: None)         # no wrapper -> an inert stub; swallows args
    assert b.copy().foo().bar is not None              # any call/attr chain stays inert, never crashes
    assert "Button" in A.STUBBED and "KtList" not in A.STUBBED

    class Screen(A.Button):                            # usable as a base class
        pass
    assert isinstance(Screen(), A.Button)              # and as an isinstance target
    print("autostub self-test: OK")
