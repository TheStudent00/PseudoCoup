"""
runtime/numbers.py — fixed-width numeric wrappers: the SINGLE SOURCE OF TRUTH for the Kotlin primitive
numeric semantics Python's built-ins silently drop. Fidelity-first: the policy is to WRAP; bare-emit/unwrap
later for speed where a context proves it safe.

The wrappers SUBCLASS int / float, so `isinstance(x, int)`, indexing, `str`/format, hashing and equality all
behave like the underlying number for free (the whole runtime assumes bare int/float). Only the ARITHMETIC
is overridden, to apply:
  - Int (Int32) / Long (Int64): two's-complement WRAPAROUND on overflow.
  - Float (Float32): 32-bit IEEE rounding (Python float is 64-bit).
  - integer `/` truncates toward zero; integer `%` takes the dividend's sign.
  - PROMOTION Int < Long < Float < Double: the wider operand wins, and once a Float/Double enters, `/` and `%`
    are real (so `Int * 100.0` is a Double, not a truncated Int).

Double stays bare `float`; String stays `str`. Refinements: unsigned (UInt/ULong) and `ushr`.
"""
import math
import struct


class ArithmeticException(ArithmeticError):
    pass


def _wrap(v, bits):
    v &= (1 << bits) - 1
    if v >> (bits - 1):
        v -= 1 << bits
    return v


def _tdiv(a, b):
    if b == 0:
        raise ArithmeticException("/ by zero")
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _tmod(a, b):
    return a - _tdiv(a, b) * b


def _f32(v):
    return struct.unpack("f", struct.pack("f", float(v)))[0]


class _NumOps:
    """Arithmetic overrides + Kotlin numeric promotion. Mixed into int/float subclasses (so `self` IS the
    number; int(self)/float(self) read its value without recursion)."""

    @property
    def dp(self):                       # compose `24.dp` / `16.sp` extension properties -- a dimension
        return self                     # IS its number here (matches the dp()/sp() wrapper functions)

    sp = dp

    def _promote(self, o):
        """-> (box, x, y, float_result) under Int < Long < Float < Double widening."""
        if isinstance(o, float) and not isinstance(o, Float32):        # a bare Double dominates
            return float, float(self), float(o), True
        if isinstance(self, Float32) or isinstance(o, Float32):        # Float
            return Float32, float(self), float(o), True
        bits = getattr(self, "BITS", 32)                              # both integral -> wider width
        if isinstance(o, _IntN):
            bits = max(bits, o.BITS)
        return (Int64 if bits == 64 else Int32), int(self), int(o), False

    def __add__(self, o): b, x, y, _ = self._promote(o); return b(x + y)
    def __radd__(self, o): b, x, y, _ = self._promote(o); return b(y + x)
    def __sub__(self, o): b, x, y, _ = self._promote(o); return b(x - y)
    def __rsub__(self, o): b, x, y, _ = self._promote(o); return b(y - x)
    def __mul__(self, o): b, x, y, _ = self._promote(o); return b(x * y)
    def __rmul__(self, o): b, x, y, _ = self._promote(o); return b(y * x)

    def __truediv__(self, o):
        b, x, y, fl = self._promote(o); return b(x / y if fl else _tdiv(x, y))

    def __rtruediv__(self, o):
        b, x, y, fl = self._promote(o); return b(y / x if fl else _tdiv(y, x))

    def __floordiv__(self, o):
        b, x, y, fl = self._promote(o); return b(x // y if fl else _tdiv(x, y))

    def __mod__(self, o):
        b, x, y, fl = self._promote(o); return b(math.fmod(x, y) if fl else _tmod(x, y))

    def __rmod__(self, o):
        b, x, y, fl = self._promote(o); return b(math.fmod(y, x) if fl else _tmod(y, x))

    def __neg__(self): b, x, _y, _ = self._promote(0); return b(-x)
    def __abs__(self): b, x, _y, _ = self._promote(0); return b(abs(x))
    def __pos__(self): return self


class _IntN(_NumOps, int):
    BITS = 32

    def __new__(cls, value=0):
        return int.__new__(cls, _wrap(int(value), cls.BITS))

    def __repr__(self):
        return f"{type(self).__name__}({int(self)})"

    def __str__(self):                       # `$x` / .toString() -> the value, not the debug repr
        return str(int(self))

    def __format__(self, spec):
        return format(int(self), spec)

    def __invert__(self):
        return type(self)(~int(self))

    def _bitop(self, o, fn):
        bits = self.BITS
        if isinstance(o, _IntN):
            bits = max(bits, o.BITS)
        return (Int64 if bits == 64 else Int32)(fn(int(self), int(o)))

    def __and__(self, o): return self._bitop(o, lambda a, b: a & b)
    def __rand__(self, o): return self._bitop(o, lambda a, b: b & a)
    def __or__(self, o): return self._bitop(o, lambda a, b: a | b)
    def __ror__(self, o): return self._bitop(o, lambda a, b: b | a)
    def __xor__(self, o): return self._bitop(o, lambda a, b: a ^ b)
    def __rxor__(self, o): return self._bitop(o, lambda a, b: b ^ a)
    def __lshift__(self, o): return type(self)(int(self) << int(o))
    def __rshift__(self, o): return type(self)(int(self) >> int(o))      # Kotlin `shr` (arithmetic)


class Int32(_IntN):
    BITS = 32


class Int64(_IntN):
    BITS = 64


class Float32(_NumOps, float):
    def __new__(cls, value=0.0):
        return float.__new__(cls, _f32(value))

    def __repr__(self):
        return f"Float32({float(self)})"

    def __str__(self):
        return str(float(self))

    def __format__(self, spec):
        return format(float(self), spec)


if __name__ == "__main__":
    assert isinstance(Int32(5), int) and isinstance(Float32(1.5), float)   # subclass -> int checks pass
    assert int(Int32(2**31 - 1) + Int32(1)) == -2**31 and int(Int32(2**16) * Int32(2**16)) == 0
    assert int(Int64(2**63 - 1) + Int64(1)) == -2**63
    assert isinstance(Int32(1) + Int64(1), Int64) and isinstance(1 + Int32(5), Int32)
    assert int(Int32(-7) / Int32(2)) == -3 and int(Int32(-7) % Int32(2)) == -1
    assert int(Int32(100) / Int32(3)) == 33
    r = Int32(53) * 100.0 / Int32(100)
    assert isinstance(r, float) and r == 53.0, r                           # Double promotion (oracle's bug)
    assert isinstance(Int32(5) * 2.0, float) and isinstance(Float32(1.5) + 1, Float32)
    assert isinstance(Float32(2.0) + 1.0, float)                           # Float + Double = Double
    assert int(Int32(-1) >> 1) == -1 and int(Int32(1) << 31) == -2**31 and int(Int32(0xF0) & Int32(0x0F)) == 0
    assert float(Float32(16777216.0) + Float32(1.0)) == 16777216.0
    assert f"{Int32(7):03d}" == "007" and str(Int32(42)) == "42" and Int32(5) == 5
    assert list(range(Int32(0), Int32(3))) == [0, 1, 2]                    # usable as an index/range bound
    try:
        _ = Int32(1) / Int32(0); assert False
    except ArithmeticException:
        pass
    print("numbers self-test: OK")
