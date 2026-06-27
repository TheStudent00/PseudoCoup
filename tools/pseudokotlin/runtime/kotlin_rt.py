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


# ---- JUnit lifecycle annotations -> identity decorators that TAG the method, so
#      the oracle runs only real @Test methods (not private helpers) and runs
#      @Before setup first. --------------------------------------------------- #
def Test(fn):
    fn._is_test = True
    return fn


def Before(fn):
    fn._is_setup = True
    return fn


def After(fn):
    fn._is_teardown = True
    return fn


def Ignore(fn):
    fn._is_ignored = True
    return fn


BeforeEach, AfterEach, Disabled = Before, After, Ignore


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
class Pair:
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __eq__(self, o):
        return isinstance(o, Pair) and (self.first, self.second) == (o.first, o.second)

    def __iter__(self):
        return iter((self.first, self.second))


class Triple:
    def __init__(self, first, second, third):
        self.first, self.second, self.third = first, second, third

    def __eq__(self, o):
        return isinstance(o, Triple) and \
            (self.first, self.second, self.third) == (o.first, o.second, o.third)

    def __iter__(self):
        return iter((self.first, self.second, self.third))


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


def emptySet():
    return set()


def mutableListOf(*xs):
    return list(xs)


def mutableSetOf(*xs):
    return set(xs)


def mutableMapOf(*pairs):
    return dict(pairs)


# ---- Kotlin preconditions ---------------------------------------------------- #
def require(*args):
    cond = args[0]
    if not cond:
        raise ValueError(args[1]() if len(args) > 1 and callable(args[1])
                         else "requirement failed")
    return cond


def check(*args):
    cond = args[0]
    if not cond:
        raise RuntimeError(args[1]() if len(args) > 1 and callable(args[1])
                           else "check failed")
    return cond


def requireNotNull(*args):
    if args[0] is None:
        raise ValueError("required value was null")
    return args[0]


def checkNotNull(*args):
    if args[0] is None:
        raise RuntimeError("value was null")
    return args[0]
