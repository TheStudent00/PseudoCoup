"""U4 egress-gate tests: pseudoir.gate wired into the CLI pre-transpile.

Covers: Hub source that PASSes emits normally; a real registry fail cell
(op.safe_call @ cpp, strategy=fail) refuses to emit and surfaces the gate
report; pending swift cells warn but do not block (D3); plain python
(non-Hub) skips the gate entirely; --no-gate bypasses the gate.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

HUB_PASS = """\
from hub import U

def pick(a: int, b: int) -> int:
    return U.coalesce(a, b)

def main() -> None:
    result: int = pick(3, 7)
    print(result)

main()
"""

# op.safe_call @ cpp is a genuine registry fail cell (strategy=fail).
HUB_FAIL_CPP = """\
from hub import U

def name_of(obj: object) -> str:
    return U.safe(obj).name.unwrap("anon")

def main() -> None:
    print(name_of(None))

main()
"""

# op.string_interp @ swift is pending (non-fail strategy) -> D3 warning path.
HUB_WARN_SWIFT = """\
from hub import U

def greet(name: str) -> str:
    return f"hello {name}"

def main() -> None:
    print(greet("world"))

main()
"""


def run_cli(source: Path, target: str, *extra):
    return subprocess.run(
        [sys.executable, "-m", "pseudocoup.cli",
         "--source", str(source),
         "--source-lang", "python",
         "--target-lang", target, *extra],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )


def test_hub_source_gate_pass_emits(tmp_path):
    src = tmp_path / "hub_pass.py"
    src.write_text(HUB_PASS)
    result = run_cli(src, "dart")
    assert result.returncode == 0, result.stderr
    out = src.with_suffix(".dart")
    assert out.exists() and out.read_text().strip()


def test_hub_source_fail_cell_refuses_to_emit(tmp_path):
    src = tmp_path / "hub_fail.py"
    src.write_text(HUB_FAIL_CPP)
    result = run_cli(src, "cpp")
    assert result.returncode != 0
    # format_report output surfaced
    assert "REGISTRY GATE" in result.stderr
    assert "VERDICT: FAIL" in result.stderr
    assert "op.safe_call" in result.stderr
    assert "refusing to emit" in result.stderr
    assert not src.with_suffix(".cpp").exists()


def test_pending_swift_is_pass_with_warning(tmp_path):
    """D3: pending cells for swift/csharp warn on stderr but do not block."""
    src = tmp_path / "hub_warn.py"
    src.write_text(HUB_WARN_SWIFT)
    result = run_cli(src, "swift")
    assert result.returncode == 0, result.stderr
    assert "PASS-WITH-WARNING" in result.stderr
    assert "op.string_interp" in result.stderr
    assert src.with_suffix(".swift").exists()


def test_pending_cell_blocks_for_non_warn_target(tmp_path):
    """The same construct that only warns on swift blocks on cpp
    (op.safe_call @ cpp is strategy=fail -- outside the D3 downgrade)."""
    src = tmp_path / "hub_fail2.py"
    src.write_text(HUB_FAIL_CPP)
    result = run_cli(src, "cpp")
    assert result.returncode != 0


def test_plain_python_skips_gate(tmp_path):
    """Non-Hub python (no U import) must not be gated -- fox.py-style source
    would MAP-fail the gate, so the gate only runs on verified Hub notation."""
    src = tmp_path / "plain.py"
    src.write_text("def f(x):\n    return [i for i in range(x)]\n\nprint(f(3))\n")
    result = run_cli(src, "dart")
    assert result.returncode == 0, result.stderr
    assert "REGISTRY GATE" not in result.stderr
    assert src.with_suffix(".dart").exists()


def test_no_gate_flag_bypasses_refusal(tmp_path):
    src = tmp_path / "hub_skip.py"
    src.write_text(HUB_FAIL_CPP)
    result = run_cli(src, "cpp", "--no-gate")
    assert result.returncode == 0, result.stderr
    assert src.with_suffix(".cpp").exists()
