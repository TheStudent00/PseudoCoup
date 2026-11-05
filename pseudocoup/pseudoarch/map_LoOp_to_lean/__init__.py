"""map_LoOp_to_lean -- One Lean expression per LoOp, with nothing left body-less.

Plan: `Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_1_map_LoOp_to_lean/`.

Sub-nodes:
- `map_sail_to_lean_direct`: A LoOp's Lean is the body Sail already emitted for it.
- `map_sail_to_lean_by_gmp`: The Sail emit leaves the floating-point externals
  as `axiom` with no body; each is given a body by slicing Berkeley SoftFloat
  and walking that block to Lean over the GMP primitives.
"""

from . import map_sail_to_lean_direct
from . import map_sail_to_lean_by_gmp
from .map_sail_to_lean_direct import (
    LoOpLean,
    decode_word,
    ensure_memory_hook,
    execute_word,
    shared_sail_lifter,
)
from .map_sail_to_lean_by_gmp import (
    GmpAxiomBody,
    list_flattened_slices,
    list_gmp_axiom_bodies,
    read_gmp_lean_slice,
)


def map_LoOp_to_lean(word_or_hex, size: int = 0) -> LoOpLean:
    """Decode a machine word (int or hex string) via the Sail model and return its `LoOpLean`."""
    if isinstance(word_or_hex, str):
        clean = word_or_hex.strip().lower()
        if clean.startswith("0x"):
            clean = clean[2:]
        w_int = int(clean, 16)
        w_size = size or (len(clean) // 2)
    else:
        w_int = int(word_or_hex)
        w_size = size or (2 if (w_int & 0x3) != 0x3 else 4)
    return decode_word(w_int, w_size)


__all__ = [
    "LoOpLean",
    "GmpAxiomBody",
    "decode_word",
    "ensure_memory_hook",
    "execute_word",
    "list_flattened_slices",
    "list_gmp_axiom_bodies",
    "map_LoOp_to_lean",
    "map_sail_to_lean_by_gmp",
    "map_sail_to_lean_direct",
    "read_gmp_lean_slice",
    "shared_sail_lifter",
]
