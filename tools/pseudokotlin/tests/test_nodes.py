"""
test_nodes.py — per-construct goldens. Each Kotlin snippet must (a) transpile and
(b) produce Python that compiles, plus a few exact-shape checks. The compile is the
anti-slop oracle; "looks right" is not "parses".
"""
import os
import py_compile
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from transpiler import KtToPy  # noqa: E402


def tp(src: str) -> str:
    return KtToPy().transpile(src.encode())


def compiles(py: str) -> bool:
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    f.write(py)
    f.close()
    try:
        py_compile.compile(f.name, doraise=True)
        return True
    except py_compile.PyCompileError:
        return False
    finally:
        os.unlink(f.name)


def test_function_if_else():
    py = tp("fun area(w: Int, h: Int): Int {\n"
            "    val a = w * h\n"
            "    if (a > 0) { return a } else { return 0 }\n}")
    assert compiles(py)
    assert "def area(w, h):" in py
    assert "a = w * h" in py


def test_class_members_resolve_to_self():
    py = tp("class Point(val x: Int, val y: Int) {\n"
            "    fun dist(): Int { return x * x + y * y }\n}")
    assert compiles(py)
    assert "class Point:" in py
    assert "def __init__(self, x, y):" in py
    assert "self.x = x" in py
    assert "return self.x * self.x + self.y * self.y" in py   # member resolution


def test_for_and_augmented_assign():
    py = tp("fun total(xs: List<Int>): Int {\n"
            "    var s = 0\n    for (v in xs) { s += v }\n    return s\n}")
    assert compiles(py)
    assert "for v in xs:" in py
    assert "s += v" in py


def test_null_dp_and_safe_call():
    py = tp("fun f(): Int { return 16.dp }")          # WRAP: 16.dp -> dp(16)
    assert "dp(16)" in py
    assert compiles(py)


def test_when_distributes_into_return():
    py = tp('fun grade(x: Int): String { return when (x) {\n'
            '    1 -> "a"\n    2 -> "b"\n    else -> "c" } }')
    assert compiles(py)
    assert "if x == 1:" in py and "return \"a\"" in py
    assert "elif x == 2:" in py and "else:" in py


def test_try_catch_finally():
    py = tp("fun f() { try { g() } catch (e: Exception) { h() } finally { k() } }")
    assert compiles(py)
    assert "try:" in py and "except Exception as e:" in py and "finally:" in py


def test_lambda_range_infix():
    py = tp("fun f(n: Int) { val ys = xs.map { v -> v * 2 }\n"
            "    for (i in 0..n) { p(i) }\n    val pr = 1 to 2 }")
    assert compiles(py)
    assert "lambda v: v * 2" in py
    assert "for i in range(0, n + 1):" in py
    assert "pr = (1, 2)" in py


def test_increment_decrement_to_augmented():
    py = tp("fun tick(): Int { var i = 0; i++; i--; return i }")
    assert compiles(py)
    assert "i += 1" in py and "i -= 1" in py


def test_by_lazy_to_cached_property():
    py = tp("class C(val n: Int) { val x by lazy { n * 2 } }")
    assert compiles(py)
    assert "@property" in py
    assert 'if not hasattr(self, "_x"):' in py
    assert "self._x = self.n * 2" in py
    assert "return self._x" in py


def test_non_lazy_delegate_fails_loud():
    from dispatch import Untranspilable
    import pytest
    with pytest.raises(Untranspilable):
        tp("class C { val w by Delegates.observable(0) { a, b, c -> } }")


def test_guard_clause_stays_statement():
    # one-armed `if (c) return x` is a statement, never a ternary value
    py = tp("fun f(xs: List<Int>): Int { if (xs.isEmpty()) return 0; return xs.size }")
    assert compiles(py)
    assert "if (len(xs) == 0):" in py and "return 0" in py   # isEmpty/size -> len WRAP
    assert "(return 0" not in py and "0 if" not in py        # not collapsed to a ternary


def test_stdlib_method_wrap():
    py = tp("fun f(xs: List<Int>, n: Int): Int {\n"
            "    if (xs.isNotEmpty()) return n.coerceIn(1, 10)\n"
            "    return n.coerceAtMost(5) }")
    assert compiles(py)
    assert "(len(xs) != 0)" in py
    assert "max(1, min(n, 10))" in py
    assert "min(n, 5)" in py


def test_elvis_with_early_return_hoists_guard():
    py = tp("fun f(m: Map<Int,Int>): Int { val v = m[1] ?: return -1; return v + 1 }")
    assert compiles(py)
    assert "if _elv1 is None:" in py and "return -1" in py
    assert "v = _elv1" in py


def test_expression_body_when_distributes():
    py = tp('fun g(x: Int): String = when (x) { 1 -> "a"; else -> "b" }')
    assert compiles(py)
    assert "if x == 1:" in py and 'return "a"' in py
    assert "return when" not in py            # the bug this guards against


def test_extension_function_takes_self():
    py = tp("fun Foo.label(): String = bar()")
    assert compiles(py)
    assert "def label(self):" in py


def test_try_as_value_distributes_return():
    py = tp("fun h(): Int = try { compute() } catch (e: Exception) { -1 }")
    assert compiles(py)
    assert "try:" in py and "return compute()" in py
    assert "except Exception as e:" in py and "return -1" in py


def test_extension_property_getter_is_function():
    py = tp("val List<Int>.tot: Int get() = sum()")
    assert compiles(py)
    assert "def tot(self):" in py and "return sum()" in py


def test_python_keyword_names_mangled():
    py = tp("class C { fun from(x: Int) = x }")
    assert compiles(py)
    assert "def from_(self, x):" in py
