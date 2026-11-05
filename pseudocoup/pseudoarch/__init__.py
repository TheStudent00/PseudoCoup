"""pseudoarch -- the system the Hub is constructed with.

Plan: `Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/`.

    HiOp   lowers to a Unit (`map_HiOp_to_unit`)
    Unit   is a sequence of LoOps
    LoOp   has a Lean expression, from the Sail model (`sail_model_of_riscv`, `map_LoOp_to_lean`)
    Unit   composes its LoOp Leans into a single term and piecewise Domain-Range partition (`map_unit_to_lean`)
"""

import sys as _sys
_sys.modules.setdefault("PseudoArch", _sys.modules[__name__])

from . import sail_model_of_riscv  # noqa: F401, E402
from . import map_LoOp_to_lean  # noqa: F401, E402
from . import map_HiOp_to_unit  # noqa: F401, E402
from . import map_unit_to_lean  # noqa: F401, E402

__all__ = [
    "sail_model_of_riscv",
    "map_LoOp_to_lean",
    "map_HiOp_to_unit",
    "map_unit_to_lean",
]
