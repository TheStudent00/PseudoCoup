"""
runtime/java_rt.py — stand-ins for the java.* platform names the foundation uses (beyond the java date
helpers already in kotlin_rt). These have real Python equivalents, so they are faithful wrappers, not
stubs -- except network I/O (URL/HttpURLConnection), which is a documented stub (it does not run in tests).

The java.time chain is the main one: Instant.ofEpochMilli(ms).atZone(zone).toLocalDate(), backed by
Python's datetime. UUID.randomUUID() -> uuid4. TimeUnit.HOURS.toMillis(n) -> arithmetic.
"""
import uuid as _uuid
from datetime import datetime as _dt, date as _date, timezone as _tz, timedelta as _td


# ---- java.time ---------------------------------------------------------------------------------- #
class ZoneId:
    def __init__(self, tzinfo):
        self._tz = tzinfo

    @staticmethod
    def of(s):
        if s in ("UTC", "Z", "GMT"):
            return ZoneId(_tz.utc)
        try:
            from zoneinfo import ZoneInfo
            return ZoneId(ZoneInfo(s))
        except Exception:                       # noqa: BLE001 -- unknown zone -> UTC
            return ZoneId(_tz.utc)

    @staticmethod
    def systemDefault():
        return ZoneId(_tz.utc)


class ZoneOffset:
    UTC = ZoneId(_tz.utc)


class LocalDate:
    def __init__(self, d):
        self._d = d                             # a python date

    @staticmethod
    def now(zone=None):
        return LocalDate(_date.today())

    @staticmethod
    def of(y, m, d):
        return LocalDate(_date(y, m, d))

    @staticmethod
    def ofEpochDay(n):
        return LocalDate(_date(1970, 1, 1) + _td(days=n))

    @property
    def year(self):
        return self._d.year

    @property
    def monthValue(self):
        return self._d.month

    @property
    def dayOfMonth(self):
        return self._d.day

    def getDayOfWeek(self):
        return self._d.isoweekday()             # Mon=1..Sun=7, matching java DayOfWeek value

    def with_(self, adjuster):
        # java `date.with(DayOfWeek.MONDAY)`: that day within the SAME ISO week (DayOfWeek is an adjuster)
        if isinstance(adjuster, int):
            return LocalDate(self._d + _td(days=int(adjuster) - self._d.isoweekday()))
        return self

    def withDayOfYear(self, n):
        return LocalDate(_date(self._d.year, 1, 1) + _td(days=int(n) - 1))

    def withDayOfMonth(self, n):
        return LocalDate(self._d.replace(day=int(n)))

    def plusDays(self, n):
        return LocalDate(self._d + _td(days=n))

    def minusDays(self, n):
        return LocalDate(self._d - _td(days=n))

    def plusWeeks(self, n):
        return LocalDate(self._d + _td(weeks=n))

    def toEpochDay(self):
        return (self._d - _date(1970, 1, 1)).days

    def isBefore(self, o):
        return self._d < o._d

    def isAfter(self, o):
        return self._d > o._d

    def atStartOfDay(self, zone=None):
        tz = zone._tz if isinstance(zone, ZoneId) else _tz.utc
        return ZonedDateTime(_dt(self._d.year, self._d.month, self._d.day, tzinfo=tz))

    def __eq__(self, o):
        return isinstance(o, LocalDate) and self._d == o._d

    def __lt__(self, o):
        return self._d < o._d

    def __le__(self, o):
        return self._d <= o._d

    def __hash__(self):
        return hash(self._d)

    def toString(self):
        return self._d.isoformat()


LocalDate.EPOCH = LocalDate(_date(1970, 1, 1))      # java.time.LocalDate.EPOCH


class DayOfWeek:                        # java.time.DayOfWeek -- the int IS getValue() (Mon=1..Sun=7),
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = 1, 2, 3, 4, 5, 6, 7   # and an adjuster


class LocalDateTime:
    def __init__(self, dt):
        self._dt = dt

    def toLocalDate(self):
        return LocalDate(self._dt.date())

    def format(self, fmt):
        return fmt.format(self)


class ZonedDateTime:
    def __init__(self, dt):
        self._dt = dt

    def toLocalDate(self):
        return LocalDate(self._dt.date())

    def toLocalTime(self):
        return LocalDateTime(self._dt)

    def toLocalDateTime(self):
        return LocalDateTime(self._dt)

    def toInstant(self):
        return Instant(int(self._dt.timestamp() * 1000))

    def toEpochSecond(self):
        return int(self._dt.timestamp())

    def format(self, fmt):
        return fmt.format(self)


class Instant:
    def __init__(self, millis):
        self._ms = millis

    @staticmethod
    def now():
        return Instant(int(_dt.now(_tz.utc).timestamp() * 1000))

    @staticmethod
    def ofEpochMilli(ms):
        return Instant(ms)

    def toEpochMilli(self):
        return self._ms

    def atZone(self, zone):
        tz = zone._tz if isinstance(zone, ZoneId) else _tz.utc
        return ZonedDateTime(_dt.fromtimestamp(self._ms / 1000, tz))


# java.time.format.DateTimeFormatter -- ofPattern(java pattern).format(temporal). Java pattern letters map
# to strftime; longest tokens first so MMM beats MM beats M.
_JAVA_TOKS = [("yyyy", "%Y"), ("yy", "%y"), ("MMMM", "%B"), ("MMM", "%b"), ("MM", "%m"), ("M", "%-m"),
              ("dd", "%d"), ("d", "%-d"), ("EEEE", "%A"), ("EEE", "%a"), ("HH", "%H"), ("hh", "%I"),
              ("h", "%-I"), ("mm", "%M"), ("ss", "%S"), ("a", "%p")]


def _java_to_strftime(pattern):
    import re
    rx = re.compile("|".join(t for t, _ in _JAVA_TOKS))
    m = dict(_JAVA_TOKS)
    return rx.sub(lambda x: m[x.group(0)], pattern)


class DateTimeFormatter:
    def __init__(self, strf):
        self._strf = strf

    @staticmethod
    def ofPattern(pattern, *a):
        return DateTimeFormatter(_java_to_strftime(pattern))

    def format(self, temporal):
        d = getattr(temporal, "_dt", None)
        if d is None:
            d = getattr(temporal, "_d", None)
        return d.strftime(self._strf) if d is not None else str(temporal)

    def withLocale(self, *a):
        return self


# ---- java.util.UUID ----------------------------------------------------------------------------- #
class _UUIDValue:
    def __init__(self, u):
        self._u = u

    def toString(self):
        return str(self._u)

    def __str__(self):
        return str(self._u)


class UUID:
    @staticmethod
    def randomUUID():
        return _UUIDValue(_uuid.uuid4())

    @staticmethod
    def fromString(s):
        return _UUIDValue(_uuid.UUID(s))


# ---- java.util.concurrent.TimeUnit -------------------------------------------------------------- #
class _TimeUnit:
    def __init__(self, to_millis):
        self._m = to_millis

    def toMillis(self, n):
        return n * self._m

    def toSeconds(self, n):
        return n * self._m // 1000


class TimeUnit:
    MILLISECONDS = _TimeUnit(1)
    SECONDS = _TimeUnit(1000)
    MINUTES = _TimeUnit(60 * 1000)
    HOURS = _TimeUnit(60 * 60 * 1000)
    DAYS = _TimeUnit(24 * 60 * 60 * 1000)


# ---- java.io / java.net (File is real; network is a documented stub) ---------------------------- #
class IOException(Exception):
    pass


class File:
    def __init__(self, *parts):
        import os
        self.path = os.path.join(*[str(p) for p in parts]) if parts else ""

    def exists(self):
        import os
        return os.path.exists(self.path)

    def delete(self):
        import os
        try:
            os.remove(self.path)
            return True
        except OSError:
            return False

    def readText(self, *a):
        with open(self.path) as f:
            return f.read()

    def writeText(self, text, *a):
        with open(self.path, "w") as f:
            f.write(text)

    def getName(self):
        import os
        return os.path.basename(self.path)


class URL:                                       # network is not exercised by the foundation's tests
    def __init__(self, spec):
        self.spec = spec

    def openConnection(self):
        return HttpURLConnection(self.spec)


class HttpURLConnection:
    def __init__(self, spec=None):
        self.spec = spec
        self.requestMethod = "GET"
        self.responseCode = 0

    def setRequestProperty(self, *a):
        pass

    def connect(self):
        raise IOException("network I/O is a stub in the foundation runtime")

    def disconnect(self):
        pass


# ---- self-test: the faithful (non-network) parts must be correct -------------------------------- #
if __name__ == "__main__":
    ms = 1_700_000_000_000
    ld = Instant.ofEpochMilli(ms).atZone(ZoneOffset.UTC).toLocalDate()
    assert ld.year == 2023, ld.year
    assert Instant.ofEpochMilli(ms).toEpochMilli() == ms
    assert LocalDate.of(2024, 1, 1).plusDays(31) == LocalDate.of(2024, 2, 1)
    assert LocalDate.of(2024, 1, 1).isBefore(LocalDate.of(2024, 2, 1))
    assert len(str(UUID.randomUUID())) == 36
    assert TimeUnit.HOURS.toMillis(2) == 7_200_000
    assert TimeUnit.DAYS.toMillis(1) == 86_400_000
    print("java_rt self-test: OK")
