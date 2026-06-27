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
    # JUnit overloads: assertEquals([msg,] expected, actual [, delta]). The float form's
    # THIRD value is a tolerance delta -- NOT the actual. Strip an optional leading
    # String message, then read expected, actual, and an optional trailing delta.
    if len(args) >= 3 and isinstance(args[0], str):   # leading message only with 3+ args
        args = args[1:]                               # (2-arg form may compare two strings)
    expected, actual = args[0], args[1]
    delta = args[2] if len(args) > 2 else None
    if delta is not None:
        assert abs(expected - actual) <= delta, \
            f"expected {expected!r}, got {actual!r} (delta {delta})"
    elif isinstance(expected, float) or isinstance(actual, float):
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


# ---- Kotlin collection runtime -- KtList/KtMap carry the Kotlin stdlib methods so
#      `xs.sortedBy { … }.map { … }` dispatches uniformly. List-returning methods
#      return KtList (chains stay typed); map-returning methods return KtMap. Lambdas
#      arrive as the transpiler's `(lambda it=None: …)`, called positionally. -------- #
import functools


class KtEntry:                       # Kotlin Map.Entry (mapValues { it.value } etc.)
    __slots__ = ("key", "value")

    def __init__(self, key, value):
        self.key, self.value = key, value


class KtList(list):
    @property
    def size(self):
        return len(self)

    @property
    def indices(self):
        return KtList(range(len(self)))

    @property
    def lastIndex(self):
        return len(self) - 1

    def isEmpty(self):
        return len(self) == 0

    def isNotEmpty(self):
        return len(self) != 0

    def contains(self, x):
        return x in self

    def filter(self, p):
        return KtList(x for x in self if p(x))

    def filterNot(self, p):
        return KtList(x for x in self if not p(x))

    def filterNotNull(self):
        return KtList(x for x in self if x is not None)

    def filterIndexed(self, p):
        return KtList(x for i, x in enumerate(self) if p(i, x))

    def map(self, f):
        return KtList(f(x) for x in self)

    def mapIndexed(self, f):
        return KtList(f(i, x) for i, x in enumerate(self))

    def mapNotNull(self, f):
        return KtList(y for y in (f(x) for x in self) if y is not None)

    def flatMap(self, f):
        return KtList(y for x in self for y in f(x))

    def flatten(self):
        return KtList(y for x in self for y in x)

    def forEach(self, action):
        for x in self:
            action(x)

    def forEachIndexed(self, action):
        for i, x in enumerate(self):
            action(i, x)

    def onEach(self, action):
        for x in self:
            action(x)
        return self

    def first(self, p=None):
        return next(x for x in self if p(x)) if p else self[0]

    def firstOrNull(self, p=None):
        if p:
            return next((x for x in self if p(x)), None)
        return self[0] if self else None

    def last(self, p=None):
        if p:
            return next(x for x in reversed(self) if p(x))
        return self[-1]

    def lastOrNull(self, p=None):
        if p:
            return next((x for x in reversed(self) if p(x)), None)
        return self[-1] if self else None

    def single(self, p=None):
        items = [x for x in self if p(x)] if p else list(self)
        if len(items) != 1:
            raise ValueError("expected single element")
        return items[0]

    def singleOrNull(self, p=None):
        items = [x for x in self if p(x)] if p else list(self)
        return items[0] if len(items) == 1 else None

    def take(self, n):
        return KtList(self[:max(0, n)])

    def takeLast(self, n):
        return KtList(self[len(self) - n:] if n > 0 else [])

    def takeWhile(self, p):
        out = KtList()
        for x in self:
            if not p(x):
                break
            out.append(x)
        return out

    def drop(self, n):
        return KtList(self[max(0, n):])

    def dropLast(self, n):
        return KtList(self[:max(0, len(self) - n)])

    def sorted(self):
        return KtList(sorted(self))

    def sortedDescending(self):
        return KtList(sorted(self, reverse=True))

    def sortedBy(self, key):
        return KtList(sorted(self, key=key))

    def sortedByDescending(self, key):
        return KtList(sorted(self, key=key, reverse=True))

    def reversed(self):
        return KtList(reversed(self))

    def distinct(self):
        seen, out = set(), KtList()
        for x in self:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def distinctBy(self, key):
        seen, out = set(), KtList()
        for x in self:
            k = key(x)
            if k not in seen:
                seen.add(k)
                out.append(x)
        return out

    def sumOf(self, selector):
        return sum(selector(x) for x in self)

    def sum(self):
        return sum(self)

    def average(self):
        return sum(self) / len(self) if self else 0.0

    def count(self, p=None):
        return sum(1 for x in self if p(x)) if p else len(self)

    def maxOrNull(self):
        return max(self) if self else None

    def minOrNull(self):
        return min(self) if self else None

    def maxOf(self, selector):
        return max(selector(x) for x in self)

    def minOf(self, selector):
        return min(selector(x) for x in self)

    def maxOfOrNull(self, selector):
        return max((selector(x) for x in self), default=None)

    def minOfOrNull(self, selector):
        return min((selector(x) for x in self), default=None)

    def maxByOrNull(self, selector):
        return max(self, key=selector) if self else None

    def minByOrNull(self, selector):
        return min(self, key=selector) if self else None

    def any(self, p=None):
        return any(p(x) for x in self) if p else len(self) > 0

    def all(self, p):
        return all(p(x) for x in self)

    def none(self, p=None):
        return not self.any(p)

    def associateBy(self, key, value=None):
        return KtMap((key(x), value(x) if value else x) for x in self)

    def associateWith(self, value):
        return KtMap((x, value(x)) for x in self)

    def associate(self, transform):
        return KtMap(tuple(transform(x)) for x in self)

    def groupBy(self, key, value=None):
        out = KtMap()
        for x in self:
            out.setdefault(key(x), KtList()).append(value(x) if value else x)
        return out

    def partition(self, p):
        yes, no = KtList(), KtList()
        for x in self:
            (yes if p(x) else no).append(x)
        return Pair(yes, no)

    def zip(self, other, transform=None):
        return KtList(transform(a, b) if transform else Pair(a, b)
                      for a, b in zip(self, other))

    def zipWithNext(self, transform=None):
        return KtList(transform(a, b) if transform else Pair(a, b)
                      for a, b in zip(self, self[1:]))

    def chunked(self, n, transform=None):
        chunks = (KtList(self[i:i + n]) for i in range(0, len(self), n))
        return KtList(transform(c) if transform else c for c in chunks)

    def windowed(self, size, step=1, partialWindows=False):
        out = KtList()
        i = 0
        while i + (size if not partialWindows else 1) <= len(self):
            out.append(KtList(self[i:i + size]))
            i += step
        return out

    def fold(self, initial, op):
        return functools.reduce(op, self, initial)

    def reduce(self, op):
        return functools.reduce(op, self)

    def getOrNull(self, i):
        return self[i] if 0 <= i < len(self) else None

    def getOrElse(self, i, default):
        return self[i] if 0 <= i < len(self) else default(i)

    def elementAtOrNull(self, i):
        return self.getOrNull(i)

    def indexOfFirst(self, p):
        return next((i for i, x in enumerate(self) if p(x)), -1)

    def indexOf(self, x):
        try:
            return super().index(x)
        except ValueError:
            return -1

    def withIndex(self):
        return KtList(Pair(i, x) for i, x in enumerate(self))

    def joinToString(self, *args, **kw):
        sep = next((a for a in args if isinstance(a, str)), kw.get("separator", ", "))
        transform = next((a for a in args if callable(a)), kw.get("transform"))
        return sep.join(str(transform(x)) if transform else str(x) for x in self)

    def toList(self):
        return self

    def toMutableList(self):
        return KtList(self)

    def toSet(self):
        return set(self)

    def toTypedArray(self):
        return KtList(self)

    def reversedArray(self):
        return KtList(reversed(self))


class KtMap(dict):
    @property
    def size(self):
        return len(self)

    @property
    def entries(self):
        return KtList(KtEntry(k, v) for k, v in self.items())

    def isEmpty(self):
        return len(self) == 0

    def isNotEmpty(self):
        return len(self) != 0

    def containsKey(self, k):
        return k in self

    def getValue(self, k):
        return self[k]

    def getOrDefault(self, k, d):
        return dict.get(self, k, d)

    def getOrElse(self, k, default):
        return self[k] if k in self else default()

    def mapValues(self, f):
        return KtMap((k, f(KtEntry(k, v))) for k, v in self.items())

    def mapKeys(self, f):
        return KtMap((f(KtEntry(k, v)), v) for k, v in self.items())

    def filterValues(self, p):
        return KtMap((k, v) for k, v in self.items() if p(v))

    def filterKeys(self, p):
        return KtMap((k, v) for k, v in self.items() if p(k))

    def filter(self, p):
        return KtMap((k, v) for k, v in self.items() if p(KtEntry(k, v)))

    def toList(self):
        return KtList(Pair(k, v) for k, v in self.items())

    def keysList(self):
        return KtList(self.keys())

    def valuesList(self):
        return KtList(self.values())


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
    return KtList(xs)


def listOfNotNull(*xs):
    return KtList(x for x in xs if x is not None)


def setOf(*xs):
    return set(xs)


def mapOf(*pairs):
    return KtMap(tuple(p) for p in pairs)


def emptyList():
    return KtList()


def emptyMap():
    return KtMap()


def emptySet():
    return set()


def mutableListOf(*xs):
    return KtList(xs)


def mutableSetOf(*xs):
    return set(xs)


def mutableMapOf(*pairs):
    return KtMap(tuple(p) for p in pairs)


# ---- Kotlin top-level math (called by bare name) ----------------------------- #
def minOf(*xs):
    return min(xs)


def maxOf(*xs):
    return max(xs)


def roundToInt(x):
    return math.floor(x + 0.5)          # Kotlin rounds half up (Math.round)


def roundToLong(x):
    return math.floor(x + 0.5)


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
