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

    @classmethod
    def from_mapped_hiop(cls, mapped_hiop: Any, state_info_0: Any = None) -> "UniversalRichNode":
        """Construct a UniversalRichNode directly from a hijacked `MappedHiOp` and
        derive its `meaning` (`UnitLean` piecewise Domain-Range partition) via
        `PseudoArch.map_unit_to_lean`."""
        from PseudoArch.map_unit_to_lean import compose_LoOp_leans

        unit = getattr(mapped_hiop, "unit", mapped_hiop)
        ulean = compose_LoOp_leans(unit)
        arch = getattr(state_info_0, "target", "riscv64") if state_info_0 else "riscv64"
        words_list = [
            {
                "address": w.address,
                "bytes_hex": w.bytes_hex,
                "opcode": w.arch_opcode,
                "operands": w.operands,
                "relocations": list(w.relocations),
            }
            for w in unit.words
        ]
        hiop_dict = {
            "lang": getattr(state_info_0, "lang", "c") if state_info_0 else "c",
            "operator": getattr(state_info_0.operator, "name", "") if state_info_0 else "",
            "spelling": getattr(state_info_0.operator, "spelling", "") if state_info_0 else "",
            "holders": tuple(p.holder for p in getattr(state_info_0, "parts", ())) if state_info_0 else (),
        }
        meaning_dict = {
            "unit_obj": unit,
            "unit_lean": ulean,
            "D_ok": str(ulean.pieces[0].domain) if len(ulean.pieces) == 1 else "piecewise",
            "D_trap": "False",
            "R_val": str(ulean.combined_term) if ulean.combined_term is not None else "",
        }
        return cls(hiop=hiop_dict, units={arch: words_list}, meaning=meaning_dict)

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
        """Equivalence mode key (`D_ok`, `D_trap`, `R_val`) or canonical `Unit` signature from `meaning`."""
        if "R_val" in self.meaning and self.meaning["R_val"]:
            return (
                str(self.meaning.get("D_ok", "True")),
                str(self.meaning.get("D_trap", "False")),
                str(self.meaning.get("R_val", "")),
            )
        ul = dict.get(self.meaning, "unit_lean")
        if ul is not None:
            d_ok = str(ul.pieces[0].domain) if getattr(ul, "pieces", None) and len(ul.pieces) == 1 else "piecewise"
            r_val = str(ul.combined_term) if getattr(ul, "combined_term", None) is not None else ""
            return (d_ok, "False", r_val)
        u_obj = dict.get(self.meaning, "unit_obj")
        if u_obj is not None and getattr(u_obj, "words", None):
            sig = "|".join(f"{w.bytes_hex}:{','.join(w.relocations)}" for w in u_obj.words)
            return ("canonical_unit", str(getattr(u_obj, "holds_p", ())), sig)
        return (
            str(self.meaning.get("D_ok", "True")),
            str(self.meaning.get("D_trap", "False")),
            str(self.meaning.get("R_val", "")),
        )
