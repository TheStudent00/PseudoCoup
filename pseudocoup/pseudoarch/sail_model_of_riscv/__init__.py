"""sail_model_of_riscv -- The RISC-V model, Sail-emitted to Lean.

Plan: `Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_0_sail_model_of_riscv/`.

Every LoOp's definition comes from here (`encdec_backwards`,
`encdec_compressed_backwards`, and `execute_*` in `Sl1Lean/`), along with the
GMP-sliced SoftFloat external definitions (`LeanIM/Gmp/`).
"""

import os
import sys
from typing import Any, Dict, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SAIL_LIFTER_DIR = os.path.join(REPO_ROOT, "Research", "oracle", "riscv", "sail_lifter")
RISCV_ORACLE_DIR = os.path.join(REPO_ROOT, "Research", "oracle", "riscv")
EMIT_DIR = os.path.join(RISCV_ORACLE_DIR, "leanpath", "gmp_insert")
SL1_EMIT_DIR = os.path.join(SAIL_LIFTER_DIR, "lean_emit")
GMP_INSERT_DIR = os.path.join(EMIT_DIR, "LeanIM")
GMP_SLICES_DIR = os.path.join(GMP_INSERT_DIR, "Gmp")
FLAT_SLICES_DIR = os.path.join(RISCV_ORACLE_DIR, "softfloat_slices", "flattened")

for _p in (RISCV_ORACLE_DIR, SAIL_LIFTER_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lean_reader as _lean_reader  # noqa: E402


def sail_model_commit() -> str:
    """Return the commit hash of the Sail RISC-V model emitted into `EMIT_DIR`."""
    for d in (EMIT_DIR, SL1_EMIT_DIR):
        commit_path = os.path.join(d, "SAIL_MODEL_COMMIT.txt")
        if os.path.isfile(commit_path):
            with open(commit_path, "r", encoding="utf-8") as f:
                return f.read().strip()
    return "unknown"


def load_sail_lean_definitions() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, int]]:
    """Parse and return `(definitions, origin, register_widths)` from the Sail Lean emit."""
    definitions, origin = _lean_reader.parse_emit(EMIT_DIR)
    widths = _lean_reader.register_widths(EMIT_DIR)
    return definitions, origin, widths
