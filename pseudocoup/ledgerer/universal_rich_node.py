"""universal_rich_node -- locked design from CORE_0_0_0_1_ledgerer.md.

class universal_rich_node:
    '''
        one HiOp variant, carried with what it
        lowers to; universal because any Unit
        runs in any language (hub/autopoly)
    '''
    attributes:
        hiop
        units
        meaning
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class UniversalRichNode:
    """One HiOp variant, carried with its lowered Units and logical Meaning."""
    hiop: dict[str, Any]
    units: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    meaning: dict[str, Any] = field(default_factory=dict)

    @property
    def lang(self) -> str:
        return str(self.hiop.get("lang", ""))

    @property
    def operator(self) -> str:
        return str(self.hiop.get("operator", ""))

    @property
    def holders(self) -> tuple[str, ...]:
        return tuple(self.hiop.get("holders", ()))

    @property
    def qualified_name(self) -> str:
        return f"{self.lang}.{self.operator}"

    def canonical_lo_ops(self, arch: str = "riscv64") -> tuple[str, ...]:
        """Return the sliced Unit's sequence of LoOp mnemonics on `arch`."""
        words = self.units.get(arch, [])
        return tuple(w["opcode"] for w in words if "opcode" in w)

    def mode_key(self) -> tuple[str, str, str]:
        """Equivalence mode key (`D_ok`, `D_trap`, `R_val`) from `meaning`."""
        return (
            str(self.meaning.get("D_ok", "True")),
            str(self.meaning.get("D_trap", "False")),
            str(self.meaning.get("R_val", "")),
        )
