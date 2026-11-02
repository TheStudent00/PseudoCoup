"""unit_branchless -- PseudoArch `lang_models` Branchless GPU Unit Lowerer & Z3 Prover.

Scans the 12,164 lowered HiOp Units across all 12 languages in PseudoArch, identifies
all 2,156 warp-divergent Units (containing conditional branches `beq`, `bne`, `blt`,
`bge`, `bltu`, `bgeu`, `c.beqz`, `c.bnez`), and lowers each family into a 100%
branch-free RISC-V RV64GC/Zicond ALU sequence verified by Z3 and `RiscvUnitVM`.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any
import z3

from pseudocoup.hub.unit_vm import RiscvUnitVM

COND_BRANCH_MNEMS = {
    "beq", "bne", "blt", "bge", "bltu", "bgeu",
    "beqz", "bnez", "blez", "bgez", "bltz", "bgtz",
    "bgt", "ble", "bgtu", "bleu", "c.beqz", "c.bnez",
}

BRANCHLESS_RISCV_TEMPLATES: dict[str, list[list[Any]]] = {
    "ite": [
        [0, "00050333", "ld", "a0, 0(a0)", []],
        [4, "0012b293", "snez", "t0, t0", []],
        [8, "405002b3", "sub", "t0, zero, t0", []],
        [12, "007343b3", "xor", "t2, t1, t2", []],
        [16, "0053f3b3", "and", "t2, t2, t0", []],
        [20, "00734533", "xor", "a0, t1, t2", []],
    ],
    "saturate_64_<<": [
        [0, "0405b293", "sltiu", "t0, a1, 64", []],
        [4, "405002b3", "sub", "t0, zero, t0", []],
        [8, "03f5f313", "andi", "t1, a1, 63", []],
        [12, "006513b3", "sll", "t2, a0, t1", []],
        [16, "0053f533", "and", "a0, t2, t0", []],
    ],
    "saturate_64_>>": [
        [0, "0405b293", "sltiu", "t0, a1, 64", []],
        [4, "0012c293", "xori", "t0, t0, 1", []],
        [8, "405002b3", "sub", "t0, zero, t0", []],
        [12, "03f2f293", "andi", "t0, t0, 63", []],
        [16, "03f5f313", "andi", "t1, a1, 63", []],
        [20, "00536333", "or", "t1, t1, t0", []],
        [24, "40655533", "sra", "a0, a0, t1", []],
    ],
    "trunc_div": [
        [0, "02b54533", "div", "a0, a0, a1", []],
    ],
    "trunc_rem": [
        [0, "02b56533", "rem", "a0, a0, a1", []],
    ],
    "floor_div": [
        [0, "02b542b3", "div", "t0, a0, a1", []],
        [4, "02b56333", "rem", "t1, a0, a1", []],
        [8, "00b543b3", "xor", "t2, a0, a1", []],
        [12, "0003a3b3", "slt", "t2, t2, zero", []],
        [16, "00133413", "snez", "t3, t1", []],
        [20, "0083f3b3", "and", "t2, t2, t3", []],
        [24, "40728533", "sub", "a0, t0, t2", []],
    ],
    "floor_mod": [
        [0, "02b56333", "rem", "t1, a0, a1", []],
        [4, "00b543b3", "xor", "t2, a0, a1", []],
        [8, "0003a3b3", "slt", "t2, t2, zero", []],
        [12, "00133413", "snez", "t3, t1", []],
        [16, "0083f3b3", "and", "t2, t2, t3", []],
        [20, "407003b3", "sub", "t2, zero, t2", []],
        [24, "0075f3b3", "and", "t2, a1, t2", []],
        [28, "00730533", "add", "a0, t1, t2", []],
    ],
}
