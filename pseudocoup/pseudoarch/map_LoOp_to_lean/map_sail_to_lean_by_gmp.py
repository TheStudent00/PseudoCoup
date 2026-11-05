"""map_sail_to_lean_by_gmp -- The Sail emit leaves the floating-point externals
as `axiom` with no body; each is given a body by slicing Berkeley SoftFloat to
the context, flattening it to one basic block, and walking that block to Lean
over the GMP primitives.

Plan: `.../node_0_0_0_0_1_map_LoOp_to_lean/node_0_0_0_0_1_1_map_sail_to_lean_by_gmp/`.
"""

import os
import re
from typing import Dict, List, NamedTuple, Optional

from ..sail_model_of_riscv import FLAT_SLICES_DIR, GMP_INSERT_DIR, GMP_SLICES_DIR

GMP_INDEX_FILE = os.path.join(GMP_INSERT_DIR, "Gmp.lean")
GMP_HELPERS_FILE = os.path.join(GMP_SLICES_DIR, "Helpers.lean")

_DEF_RE = re.compile(r"^def\s+(riscv_\w+)\s*(.*?)\s*:=\s*\n((?:  .*\n)+)", re.M)


class GmpAxiomBody(NamedTuple):
    """One SoftFloat external axiom given a loop-free Lean body over the GMP primitives."""

    axiom_name: str
    signature: str
    wrapper_body: str
    lean_module_file: str


def list_gmp_axiom_bodies() -> Dict[str, GmpAxiomBody]:
    """Return all 67 SoftFloat external axiom bodies from `LeanIM/Gmp.lean`."""
    if not os.path.isfile(GMP_INDEX_FILE):
        return {}
    with open(GMP_INDEX_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    out: Dict[str, GmpAxiomBody] = {}
    for m in _DEF_RE.finditer(text):
        name = m.group(1)
        sig = m.group(2).strip()
        body = m.group(3).rstrip()
        short = name[len("riscv_"):]
        short_cap = short[:1].upper() + short[1:]
        mod_file = os.path.join(GMP_SLICES_DIR, f"{short_cap}.lean")
        out[name] = GmpAxiomBody(
            axiom_name=name,
            signature=sig,
            wrapper_body=body,
            lean_module_file=mod_file,
        )
    return out


def read_gmp_lean_slice(axiom_name: str) -> Optional[str]:
    """Read the full flattened GMP Lean module for `axiom_name` (e.g. `riscv_f64Mul`)."""
    bodies = list_gmp_axiom_bodies()
    info = bodies.get(axiom_name)
    if info is None or not os.path.isfile(info.lean_module_file):
        return None
    with open(info.lean_module_file, "r", encoding="utf-8") as f:
        return f.read()


def list_flattened_slices() -> List[str]:
    """List all flattened single-basic-block SoftFloat slices (`.flat.ll`)."""
    if not os.path.isdir(FLAT_SLICES_DIR):
        return []
    return sorted(f for f in os.listdir(FLAT_SLICES_DIR) if f.endswith(".flat.ll"))
