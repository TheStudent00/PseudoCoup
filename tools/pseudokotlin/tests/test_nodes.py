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
