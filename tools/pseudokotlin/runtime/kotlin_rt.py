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
import re as _re


class Regex:
    def __init__(self, pattern, *options):
        self.pattern = pattern
        self._c = _re.compile(pattern)

    def matches(self, s):
        return self._c.fullmatch(s) is not None

    def containsMatchIn(self, s):
        return self._c.search(s) is not None

    def replace(self, s, repl):
        return self._c.sub(repl, s)

    def find(self, s):
        return self._c.search(s)

    def split(self, s):
        return KtList(self._c.split(s))


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


def assertThrows(*args):
    # assertThrows([msg,] expectedClass, executable) -> run it, assert it raises expectedClass; return it
    expected, executable = args[-2], args[-1]
    try:
        executable()
    except BaseException as e:                       # noqa: BLE001
        if isinstance(e, expected):
            return e
        raise AssertionError(f"expected {getattr(expected, '__name__', expected)}, "
                             f"got {type(e).__name__}: {e}")
    raise AssertionError(f"expected {getattr(expected, '__name__', expected)} to be thrown")


# ---- Kotlin / java.lang exceptions thrown by bare name (`throw IllegalStateException(msg)`) ---- #
class IllegalStateException(RuntimeError):
    pass


class IllegalArgumentException(ValueError):
    pass


class NoSuchElementException(Exception):
    pass


class IndexOutOfBoundsException(IndexError):
    pass


class UnsupportedOperationException(Exception):
    pass


class ConcurrentModificationException(Exception):
    pass


# ---- kotlin.Result / runCatching -- a block's outcome captured as success(value) | failure(exc) ---- #
class Result:
    def __init__(self, value=None, exception=None):
        self._value, self._exc = value, exception

    @property
    def isSuccess(self):
        return self._exc is None

    @property
    def isFailure(self):
        return self._exc is not None

    def getOrNull(self):
        return self._value if self._exc is None else None

    def exceptionOrNull(self):
        return self._exc

    def getOrThrow(self):
        if self._exc is not None:
            raise self._exc
        return self._value

    def getOrDefault(self, default):
        return self._value if self._exc is None else default

    def getOrElse(self, onFailure):
        return self._value if self._exc is None else onFailure(self._exc)

    def onSuccess(self, action):
        if self._exc is None:
            action(self._value)
        return self

    def onFailure(self, action):
        if self._exc is not None:
            action(self._exc)
        return self

    def map(self, transform):
        return Result(transform(self._value)) if self._exc is None else self

    def fold(self, onSuccess, onFailure):
        return onSuccess(self._value) if self._exc is None else onFailure(self._exc)


def runCatching(block, *rest):
    # top-level `runCatching { }` -> block is the lambda; `x.runCatching { }` -> (x, lambda) where the
    # lambda takes x. Either way, run it and capture success/failure (Kotlin catches Throwable).
    fn = rest[0] if rest else block
    arg = (block,) if rest else ()
    try:
        return Result(fn(*arg))
    except Exception as e:                      # noqa: BLE001 -- mirror Kotlin runCatching
        return Result(exception=_as_throwable(e))


def _as_throwable(e):
    """Give a caught Python exception Kotlin's Throwable.message (so `it.message` in an onFailure / catch
    works). Set on the instance, never overwriting a real `message` property on a wrapper exception."""
    if not hasattr(e, "message"):
        try:
            e.message = str(e)
        except (AttributeError, TypeError):
            pass
    return e


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

    def __add__(self, other):           # Kotlin list + list = concat; list + elem = append
        if isinstance(other, (list, tuple, set, frozenset)):
            return KtList(list(self) + list(other))
        return KtList(list(self) + [other])

    def __iadd__(self, other):          # Kotlin `list += elem` APPENDS (Python would
        if isinstance(other, (list, tuple, set, frozenset)):   # extend -> iterate elem)
            self.extend(other)
        else:
            self.append(other)
        return self

    def __getitem__(self, i):           # slices stay KtList so chains keep the methods
        r = list.__getitem__(self, i)
        return KtList(r) if isinstance(i, slice) else r

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

    def mapTo(self, dest, f):               # map into an existing destination, return it
        for x in self:
            dest.add(f(x))
        return dest

    def mapNotNullTo(self, dest, f):
        for x in self:
            y = f(x)
            if y is not None:
                dest.add(y)
        return dest

    def filterTo(self, dest, p):
        for x in self:
            if p(x):
                dest.add(x)
        return dest

    def flatMapTo(self, dest, f):
        for x in self:
            for y in f(x):
                dest.add(y)
        return dest

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

    def find(self, p):                  # Kotlin find = firstOrNull with a predicate
        return next((x for x in self if p(x)), None)

    def findLast(self, p):
        return next((x for x in reversed(self) if p(x)), None)

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

    def sortedWith(self, comparator):
        return KtList(sorted(self, key=functools.cmp_to_key(comparator)))

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

    def groupingBy(self, key):
        return _KtGrouping(self, key)

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

    def indexOfLast(self, p):
        return next((i for i in range(len(self) - 1, -1, -1) if p(self[i])), -1)

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

    def add(self, *a):                  # add(x) appends; add(i, x) inserts
        if len(a) == 2:
            self.insert(a[0], a[1])
        else:
            self.append(a[0])
        return True

    def addAll(self, coll):
        self.extend(coll)
        return True

    def removeAt(self, i):
        return self.pop(i)

    def removeFirst(self):
        return self.pop(0)

    def removeLast(self):
        return self.pop()

    def removeAll(self, coll):
        s = set(coll)
        self[:] = [x for x in self if x not in s]
        return True

    def toList(self):
        return self

    def orEmpty(self):                      # non-null receiver -> identity (None handled by `or KtList()`)
        return self

    def toMutableList(self):
        return KtList(self)

    def toSet(self):
        return KtSet(self)

    def toMutableSet(self):
        return KtSet(self)

    def toHashSet(self):
        return KtSet(self)

    def toTypedArray(self):
        return KtList(self)

    def reversedArray(self):
        return KtList(reversed(self))


class _KtGrouping:
    """Lazy result of `xs.groupingBy { key }` -- a source + key selector that the
    terminal ops (eachCount/fold/reduce/aggregate) materialise per-key, mirroring
    Kotlin's Grouping<T, K>."""
    def __init__(self, src, key):
        self._src, self._key = src, key

    def eachCount(self):
        out = KtMap()
        for x in self._src:
            k = self._key(x)
            out[k] = (out[k] or 0) + 1        # KtMap.__missing__ -> None, so `or 0`
        return out

    def fold(self, initial, operation):
        out = KtMap()
        for x in self._src:
            k = self._key(x)
            acc = out[k] if k in out else initial
            out[k] = operation(acc, x)
        return out

    def reduce(self, operation):
        out = KtMap()
        for x in self._src:
            k = self._key(x)
            out[k] = x if k not in out else operation(k, out[k], x)
        return out

    def aggregate(self, operation):
        out = KtMap()
        for x in self._src:
            k = self._key(x)
            out[k] = operation(k, out[k] if k in out else None, x, k not in out)
        return out


class KtMap(dict):
    def __missing__(self, k):           # Kotlin map[k] returns null for an absent key
        return None

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


class KtSet(set):
    @property
    def size(self):
        return len(self)

    def isEmpty(self):
        return len(self) == 0

    def isNotEmpty(self):
        return len(self) != 0

    def contains(self, x):
        return x in self

    def _coerce(self, other):           # Kotlin `set + elem` adds; `set + coll` unions
        return set(other) if isinstance(other, (set, frozenset, list)) else {other}

    def __add__(self, other):
        return KtSet(self | self._coerce(other))

    def __sub__(self, other):
        return KtSet(set(self) - self._coerce(other))

    def plus(self, other):
        return self.__add__(other)

    def minus(self, other):
        return self.__sub__(other)

    def union(self, other):
        return KtSet(self | set(other))

    def intersect(self, other):
        return KtSet(self & set(other))

    def subtract(self, other):
        return KtSet(self - set(other))

    def toList(self):
        return KtList(self)

    def toMutableSet(self):
        return KtSet(self)

    def toSet(self):
        return self

    def map(self, f):
        return KtList(self).map(f)

    def mapNotNull(self, f):
        return KtList(self).mapNotNull(f)

    def filter(self, p):
        return KtList(self).filter(p)

    def any(self, p=None):
        return KtList(self).any(p)

    def all(self, p):
        return KtList(self).all(p)

    def none(self, p=None):
        return KtList(self).none(p)

    def count(self, p=None):
        return KtList(self).count(p)

    def sumOf(self, s):
        return KtList(self).sumOf(s)

    def maxOf(self, s):
        return KtList(self).maxOf(s)

    def minOf(self, s):
        return KtList(self).minOf(s)

    def maxByOrNull(self, s):
        return KtList(self).maxByOrNull(s)

    def minByOrNull(self, s):
        return KtList(self).minByOrNull(s)

    def sorted(self):
        return KtList(self).sorted()

    def sortedBy(self, k):
        return KtList(self).sortedBy(k)

    def associateBy(self, k, v=None):
        return KtList(self).associateBy(k, v)

    def associateWith(self, v):
        return KtList(self).associateWith(v)

    def groupBy(self, k, v=None):
        return KtList(self).groupBy(k, v)

    def first(self, p=None):
        return KtList(self).first(p)

    def firstOrNull(self, p=None):
        return KtList(self).firstOrNull(p)

    def forEach(self, a):
        KtList(self).forEach(a)

    def joinToString(self, *a, **k):
        return KtList(self).joinToString(*a, **k)


# ---- Kotlin stdlib helpers (added as engines surface them) ------------------- #
def List(n, init):                      # List(size) { i -> … } factory
    return KtList(init(i) for i in range(n))


def MutableList(n, init):
    return KtList(init(i) for i in range(n))


class Pair:
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __eq__(self, o):
        return isinstance(o, Pair) and (self.first, self.second) == (o.first, o.second)

    def __iter__(self):
        return iter((self.first, self.second))

    def __getitem__(self, i):           # so the .first/.second WRAP ([0]/[1]) also works
        return (self.first, self.second)[i]


class Triple:
    def __init__(self, first, second, third):
        self.first, self.second, self.third = first, second, third

    def __eq__(self, o):
        return isinstance(o, Triple) and \
            (self.first, self.second, self.third) == (o.first, o.second, o.third)

    def __iter__(self):
        return iter((self.first, self.second, self.third))

    def __getitem__(self, i):
        return (self.first, self.second, self.third)[i]


def listOf(*xs):
    return KtList(xs)


def listOfNotNull(*xs):
    return KtList(x for x in xs if x is not None)


# Kotlin type names used as values (String(chars), Boolean("true"), …) -> Python types
String = str
CharSequence = str
Any = object                            # kotlin.Any -> Python object; `Any()` is a bare lock/sentinel


class _KClass:                          # X::class -> kclass(X); .java/.kotlin are X, .simpleName its name
    def __init__(self, cls):
        self.java = cls
        self.kotlin = cls
        self.simpleName = getattr(cls, "__name__", None)
        self.qualifiedName = getattr(cls, "__name__", None)


def kclass(cls):
    return _KClass(cls)


def arrayOf(*xs):
    return KtList(xs)


def arrayOfNulls(n):
    return KtList([None] * n)


def intArrayOf(*xs):
    return KtList(xs)


Unit = type("Unit", (), {})     # kotlin.Unit -- the void singleton/type (a default import, used bare)


def repeat(n, action):
    for i in range(n):
        action(i)


def synchronized(lock, block=None):
    # synchronized(lock) { … } -> run the block (single-threaded Python needs no real monitor)
    return block() if block is not None else (lock() if callable(lock) else lock)


def trimIndent(s):
    # Kotlin String.trimIndent(): drop the common minimal indent + the leading/trailing blank lines.
    import textwrap
    return textwrap.dedent(s).strip("\n")


def trimMargin(s, marker="|"):
    # Kotlin String.trimMargin(): each line keeps only what follows its first margin marker.
    out = []
    for line in s.split("\n"):
        i = line.find(marker)
        out.append(line[i + len(marker):] if i >= 0 else line)
    return "\n".join(out).strip("\n")


def setOf(*xs):
    return KtSet(xs)


def mapOf(*pairs):
    return KtMap(tuple(p) for p in pairs)


def emptyList():
    return KtList()


def emptyMap():
    return KtMap()


def emptySet():
    return KtSet()


def mutableListOf(*xs):
    return KtList(xs)


def mutableSetOf(*xs):
    return KtSet(xs)


def mutableMapOf(*pairs):
    return KtMap(tuple(p) for p in pairs)


# Java collection constructors used directly in Kotlin (HashSet(), ArrayList(xs), …).
def HashSet(src=()):
    return KtSet(src)


def LinkedHashSet(src=()):
    return KtSet(src)


def ArrayList(src=()):
    return KtList(src)


class KtArrayDeque(KtList):             # kotlin.collections.ArrayDeque / java Deque (ring-buffer use)
    def addLast(self, x):
        self.append(x)

    def addFirst(self, x):
        self.insert(0, x)

    def pollFirst(self):               # Java Deque: head, or null when empty
        return self.pop(0) if self else None

    def pollLast(self):
        return self.pop() if self else None


def ArrayDeque(arg=()):                 # ArrayDeque()/ArrayDeque(capacity:Int) -> empty; (coll) -> filled
    return KtArrayDeque() if isinstance(arg, int) else KtArrayDeque(arg)


def HashMap(src=None):
    return KtMap(src or {})


def LinkedHashMap(src=None):
    return KtMap(src or {})


class StringBuilder:                    # kotlin.text.StringBuilder / java.lang.StringBuilder. Each mutator
    """A mutable text buffer. Every append returns the builder, so chains (`sb.append(a).append(b)`) and the
    buildString receiver pattern both work; toString() yields the accumulated text."""
    def __init__(self, src=""):
        self._parts = [] if src in ("", None) else [str(src)]

    def append(self, x=""):
        self._parts.append("" if x is None else str(x))
        return self

    def appendLine(self, x=""):
        self._parts.append(("" if x is None else str(x)) + "\n")
        return self

    def insert(self, i, x):
        self._parts.insert(i, "" if x is None else str(x))
        return self

    def toString(self):
        return "".join(self._parts)

    def isEmpty(self):
        return not any(self._parts)

    def isNotEmpty(self):
        return any(self._parts)

    @property
    def length(self):
        return len(self.toString())

    def __len__(self):
        return self.length

    def __str__(self):
        return self.toString()


StringBuffer = StringBuilder            # java.lang.StringBuffer -- same surface here


def buildString(block):                 # kotlin.text.buildString -- usually inlined by the transpiler's
    sb = StringBuilder()                # builder scope, but kept real so a first-class reference still runs
    block(sb)
    return sb.toString()


def buildList(block):                   # kotlin.collections.buildList
    lst = KtList()
    block(lst)
    return lst


# ---- java.util / java.text date stand-ins (bare-name, like java.lang.Math above) ------------ #
from datetime import datetime as _datetime


class Date:                             # java.util.Date -- Date() is now; Date(ms) is epoch-millis
    def __init__(self, millis=None):
        self._dt = _datetime.now() if millis is None else _datetime.fromtimestamp(millis / 1000)


class Locale:                           # java.util.Locale -- only passed through to a formatter here
    US = "en_US"

    @staticmethod
    def getDefault():
        return Locale.US


_JAVA_DATE_TOKENS = (("yyyy", "%Y"), ("MM", "%m"), ("dd", "%d"),
                     ("HH", "%H"), ("mm", "%M"), ("ss", "%S"), ("SSS", "%f"))


class SimpleDateFormat:                 # java.text.SimpleDateFormat -- translate pattern -> strftime
    def __init__(self, pattern, locale=None):
        p = pattern
        for java_tok, py_tok in _JAVA_DATE_TOKENS:
            p = p.replace(java_tok, py_tok)
        self._pattern, self._millis = p, "%f" in p

    def format(self, date):
        d = date._dt if isinstance(date, Date) else date
        out = d.strftime(self._pattern)
        return out[:-3] if self._millis else out      # %f is 6-digit micros; SSS wants 3 (millis)


# ---- Android-framework stand-ins. NOTE: NOT Kotlin/Java stdlib -- the leading edge of the
#      Room/Compose/Hilt set the UI phase will need. When that set grows, splitting the runtime
#      by origin (and likely renaming this file) is the structural call -- deferred until then. - #
class Migration:                        # androidx.room.migration.Migration -- STUB (no Python Room)
    def __init__(self, startVersion, endVersion):
        self.startVersion, self.endVersion = startVersion, endVersion

    def migrate(self, db):              # overridden per anonymous migration; runs only vs a real DB
        pass


# ---- Kotlin comparators (compareBy { … }.thenBy { … }; sortedWith) ----------- #
def _cmp_key(ka, kb):
    return -1 if ka < kb else (1 if ka > kb else 0)


class Comparator:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, a, b):
        return self.fn(a, b)

    def thenBy(self, selector):
        prev = self.fn
        return Comparator(lambda a, b: prev(a, b) or _cmp_key(selector(a), selector(b)))

    def thenByDescending(self, selector):
        prev = self.fn
        return Comparator(lambda a, b: prev(a, b) or -_cmp_key(selector(a), selector(b)))

    def reversed(self):
        return Comparator(lambda a, b: -self.fn(a, b))


def compareBy(*selectors):
    def cmp(a, b):
        for s in selectors:
            r = _cmp_key(s(a), s(b))
            if r:
                return r
        return 0
    return Comparator(cmp)


def compareByDescending(*selectors):
    return compareBy(*selectors).reversed()


# ---- Kotlin top-level math (called by bare name) ----------------------------- #
def minOf(*xs):
    return min(xs)


def maxOf(*xs):
    return max(xs)


class Math:                             # java.lang.Math (used as `Math.round(x)` etc.)
    PI = math.pi
    E = math.e
    round = staticmethod(lambda x: math.floor(x + 0.5))
    abs = staticmethod(abs)
    max = staticmethod(max)
    min = staticmethod(min)
    floor = staticmethod(lambda x: math.floor(x))
    ceil = staticmethod(lambda x: math.ceil(x))
    sqrt = staticmethod(math.sqrt)
    cbrt = staticmethod(lambda x: math.copysign(abs(x) ** (1 / 3), x))
    pow = staticmethod(pow)
    exp = staticmethod(math.exp)
    log = staticmethod(math.log)
    log10 = staticmethod(math.log10)
    sin = staticmethod(math.sin)
    cos = staticmethod(math.cos)
    tan = staticmethod(math.tan)


class System:                          # java.lang.System (currentTimeMillis / nanoTime by bare name)
    @staticmethod
    def currentTimeMillis():
        import time
        return int(time.time() * 1000)

    @staticmethod
    def nanoTime():
        import time
        return int(time.perf_counter() * 1e9)

    @staticmethod
    def lineSeparator():
        return "\n"

    @staticmethod
    def getProperty(*a):
        return a[1] if len(a) > 1 else None


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
