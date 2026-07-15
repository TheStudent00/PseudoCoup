"""CLI transpile smoke tests: every target emits, exit 0, nonempty output."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"

TARGET_EXT = {
    "python": ".python",
    "dart": ".dart",
    "go": ".go",
    "kotlin": ".kt",
    "java": ".java",
    "csharp": ".cs",
    "typescript": ".ts",
    "swift": ".swift",
    "rust": ".rs",
    "cpp": ".cpp",
    "ruby": ".rb",
    "php": ".php",
}

EXAMPLE_FILES = ["fox.py", "space_station.py"]


def transpile(source: Path, target: str) -> subprocess.CompletedProcess:
    """Run the CLI transpile. Output lands next to the source file."""
    return subprocess.run(
        [sys.executable, "-m", "pseudocoup.cli",
         "--source", str(source),
         "--source-lang", "python",
         "--target-lang", target],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("example", EXAMPLE_FILES)
@pytest.mark.parametrize("target", sorted(TARGET_EXT))
def test_cli_transpile(example, target, tmp_path):
    src = tmp_path / example
    shutil.copy(EXAMPLES / example, src)
    result = transpile(src, target)
    assert result.returncode == 0, (
        f"CLI exited {result.returncode} for {example} -> {target}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    out = src.with_suffix(TARGET_EXT[target])
    assert out.exists(), f"expected output file {out.name} was not created"
    assert out.read_text().strip(), f"output file {out.name} is empty"
