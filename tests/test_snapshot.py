"""Byte-diff regression against the pre-upgrade snapshot.

tests/snapshot_pre_upgrade/ holds the output of every (example, target) pair
captured BEFORE the V4/pseudoir upgrade touched any emitter (2026-07-14,
working tree at that date). When a later work unit deliberately changes an
emitter's output, it must update that emitter's snapshot files in the same
change and say so; any other diff here is an unintended regression.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"
SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshot_pre_upgrade"

from tests.test_transpile import TARGET_EXT, EXAMPLE_FILES, transpile


@pytest.mark.parametrize("example", EXAMPLE_FILES)
@pytest.mark.parametrize("target", sorted(TARGET_EXT))
def test_output_matches_snapshot(example, target, tmp_path):
    stem = Path(example).stem
    snapshot = SNAPSHOT_DIR / (stem + TARGET_EXT[target])
    assert snapshot.exists(), f"missing snapshot file {snapshot.name}"

    src = tmp_path / example
    shutil.copy(EXAMPLES / example, src)
    result = transpile(src, target)
    assert result.returncode == 0, (
        f"CLI exited {result.returncode} for {example} -> {target}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    out = src.with_suffix(TARGET_EXT[target])
    assert out.read_bytes() == snapshot.read_bytes(), (
        f"{stem} -> {target}: output differs from pre-upgrade snapshot "
        f"({snapshot.name}). If this emitter was intentionally changed, "
        f"update the snapshot in the same change."
    )
