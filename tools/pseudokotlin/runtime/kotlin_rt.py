"""
kotlin_rt.py — the Python side of the Kotlin runtime. The transpiled engines and
tests call JUnit asserts and a handful of Kotlin stdlib helpers by BARE name (the
transpiler emits `assertTrue(x)`, `listOf(...)`, etc. verbatim). The oracle execs
this module's namespace in front of the transpiled code so those names resolve.

This is the WRAP layer made concrete: where Kotlin has no Python builtin, a shim
stands in. It grows one helper at a time, each time a new engine surfaces a call --
and every addition is itself under the runtime oracle (if the shim is wrong, the
transpiled test diverges from the JVM-verified assertion and the oracle catches it).
"""
import math


# ---- JUnit (org.junit.Assert.*) -- the boolean/value is always the LAST arg; an
#      optional JUnit message precedes it. ------------------------------------- #
def assertTrue(*args):
    assert args[-1], "assertTrue failed"


def assertFalse(*args):
    assert not args[-1], "assertFalse failed"


def assertEquals(*args):
    expected, actual = args[-2], args[-1]
    if isinstance(expected, float) or isinstance(actual, float):
        assert math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-9), \
            f"expected {expected!r}, got {actual!r}"
    else:
        assert expected == actual, f"expected {expected!r}, got {actual!r}"


def assertNotEquals(*args):
    a, b = args[-2], args[-1]
    assert a != b, f"expected {a!r} != {b!r}"


def assertNull(*args):
    assert args[-1] is None, f"expected None, got {args[-1]!r}"


def assertNotNull(*args):
    assert args[-1] is not None, "expected non-None"


# ---- Kotlin stdlib helpers (added as engines surface them) ------------------- #
def listOf(*xs):
    return list(xs)


def setOf(*xs):
    return set(xs)


def mapOf(*pairs):
    return dict(pairs)


def emptyList():
    return []


def emptyMap():
    return {}


def mutableListOf(*xs):
    return list(xs)
