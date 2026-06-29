"""
runtime/numbers.py — fixed-width numeric wrappers: the SINGLE SOURCE OF TRUTH for the Kotlin primitive
numeric semantics that Python's built-ins silently drop. Fidelity-first: the policy is to WRAP, and
bare-emit/unwrap later for speed where a context proves it safe.

What a bare map gets wrong, and what these fix in one place:
  - Int (Int32) / Long (Int64): two's-complement WRAPAROUND on overflow. Python int never overflows.
  - Float (Float32): 32-bit IEEE rounding. Python float is 64-bit, so `Float -> float` silently WIDENS.
  - integer `/`: truncates TOWARD ZERO. Python `//` floors -> differs on negatives (-7/2 = -3, not -4).
  - integer `%`: takes the DIVIDEND's sign (Kotlin/Java rem). Python `%` floor-mods (-7%2 = -1, not 1).

Double maps to bare `float` (both 64-bit IEEE) and String to `str`, so neither needs a wrapper.

First cut: same-type ops and wrapper-with-plain-number ops (the common case) are exact. Noted refinements:
mixed-WIDTH promotion (Int32+Int64 -> Int64, Float+Double -> Double), unsigned (UInt/ULong), Byte/Short,
and `ushr` (logical vs arithmetic shift).
"""
import struct


class ArithmeticException(ArithmeticError):
    pass


def _wrap(v, bits):
    v &= (1 << bits) - 1
    if v >> (bits - 1):                 # sign bit set -> negative in two's complement
        v -= 1 << bits
    return v


def _tdiv(a, b):                        # integer `/`: truncate toward zero
    if b == 0:
        raise ArithmeticException("/ by zero")
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _tmod(a, b):                        # integer `%`: remainder with the dividend's sign
    return a - _tdiv(a, b) * b


class _IntN:
    BITS = 32

    def __init__(self, value):
        self._v = _wrap(int(value), self.BITS)

    def __int__(self): return self._v
    def __index__(self): return self._v
    def __float__(self): return float(self._v)
    def __bool__(self): return self._v != 0
    def __hash__(self): return hash(self._v)
    def __repr__(self): return f"{type(self).__name__}({self._v})"

    def _w(self, v): return type(self)(v)               # wrap a result back to this width

    def __add__(self, o): return self._w(self._v + int(o))
    def __radd__(self, o): return self._w(int(o) + self._v)
    def __sub__(self, o): return self._w(self._v - int(o))
    def __rsub__(self, o): return self._w(int(o) - self._v)
    def __mul__(self, o): return self._w(self._v * int(o))
    def __rmul__(self, o): return self._w(int(o) * self._v)
    def __truediv__(self, o): return self._w(_tdiv(self._v, int(o)))
    def __rtruediv__(self, o): return self._w(_tdiv(int(o), self._v))
    def __floordiv__(self, o): return self._w(_tdiv(self._v, int(o)))
    def __mod__(self, o): return self._w(_tmod(self._v, int(o)))
    def __rmod__(self, o): return self._w(_tmod(int(o), self._v))
    def __neg__(self): return self._w(-self._v)
    def __pos__(self): return self
    def __abs__(self): return self._w(abs(self._v))
    def __and__(self, o): return self._w(self._v & int(o))
    def __rand__(self, o): return self._w(int(o) & self._v)
    def __or__(self, o): return self._w(self._v | int(o))
    def __ror__(self, o): return self._w(int(o) | self._v)
    def __xor__(self, o): return self._w(self._v ^ int(o))
    def __rxor__(self, o): return self._w(int(o) ^ self._v)
    def __lshift__(self, o): return self._w(self._v << int(o))
    def __rshift__(self, o): return self._w(self._v >> int(o))      # Kotlin `shr` (arithmetic)
    def __invert__(self): return self._w(~self._v)
    def __eq__(self, o): return isinstance(o, (int, _IntN)) and self._v == int(o)
    def __ne__(self, o): return not self.__eq__(o)
    def __lt__(self, o): return self._v < int(o)
    def __le__(self, o): return self._v <= int(o)
    def __gt__(self, o): return self._v > int(o)
    def __ge__(self, o): return self._v >= int(o)


class Int32(_IntN):
    BITS = 32


class Int64(_IntN):
    BITS = 64


def _f32(v):
    return struct.unpack("f", struct.pack("f", float(v)))[0]


class Float32:
    def __init__(self, value):
        self._v = _f32(value)

    def __float__(self): return self._v
    def __bool__(self): return self._v != 0.0
    def __hash__(self): return hash(self._v)
    def __repr__(self): return f"Float32({self._v})"

    def _w(self, v): return Float32(v)

    def __add__(self, o): return self._w(self._v + float(o))
    def __radd__(self, o): return self._w(float(o) + self._v)
    def __sub__(self, o): return self._w(self._v - float(o))
    def __rsub__(self, o): return self._w(float(o) - self._v)
    def __mul__(self, o): return self._w(self._v * float(o))
    def __rmul__(self, o): return self._w(float(o) * self._v)
    def __truediv__(self, o): return self._w(self._v / float(o))
    def __rtruediv__(self, o): return self._w(float(o) / self._v)
    def __neg__(self): return self._w(-self._v)
    def __abs__(self): return self._w(abs(self._v))
    def __eq__(self, o): return isinstance(o, (int, float, Float32)) and self._v == float(o)
    def __ne__(self, o): return not self.__eq__(o)
    def __lt__(self, o): return self._v < float(o)
    def __le__(self, o): return self._v <= float(o)
    def __gt__(self, o): return self._v > float(o)
    def __ge__(self, o): return self._v >= float(o)


if __name__ == "__main__":
    assert int(Int32(2**31 - 1) + Int32(1)) == -2**31          # overflow wraps to MIN
    assert int(Int32(2**31 - 1) + 1) == -2**31                 # wrapper + plain int
    assert int(Int32(2**16) * Int32(2**16)) == 0               # 2^32 wraps to 0
    assert int(Int64(2**63 - 1) + Int64(1)) == -2**63          # 64-bit overflow
    assert int(Int32(-7) / Int32(2)) == -3                     # trunc toward zero (Python // -> -4)
    assert int(Int32(7) / Int32(2)) == 3
    assert int(Int32(-7) % Int32(2)) == -1                     # dividend's sign (Python % -> 1)
    assert int(Int32(-1) >> 1) == -1                           # arithmetic shift
    assert int(Int32(1) << 31) == -2**31                       # shift into the sign bit
    assert float(Float32(16777216.0) + Float32(1.0)) == 16777216.0   # 2^24+1 not representable in f32
    assert float(Float32(0.1)) != 0.1                          # f32(0.1) != 64-bit 0.1
    try:
        _ = Int32(1) / Int32(0)
        assert False
    except ArithmeticException:
        pass
    print("numbers self-test: OK")
