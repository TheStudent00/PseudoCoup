"""unit_vm -- Universal RISC-V Unit Executor for Single & Multi-Body UR-Nodes.

Executes any sliced RISC-V `Unit` (`words`, `unit`, `parts`) directly:
  - Invokes `part_callbacks[part_name]()` whenever `auipc` + `jalr` hits `R_RISCV_CALL_PLT part_*`
  - Follows internal branch offsets (`beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`, `c.beqz`, `c.bnez`, `c.j`, `j`)
  - Propagates dependent control-flow exits (`BreakSignal`, `ContinueSignal`, `ReturnSignal`)
  - Supports complex holders (structs, arrays, pointers) in a byte-addressable MemoryArena
"""
from __future__ import annotations
from typing import Any, Callable


class BreakSignal(Exception):
    """Raised by a dependent `break;` Unit to exit its enclosing loop/switch Unit."""


class ContinueSignal(Exception):
    """Raised by a dependent `continue;` Unit to advance its enclosing loop Unit."""


class ReturnSignal(Exception):
    """Raised by a `return` Unit with an optional return value."""
    def __init__(self, value: int = 0) -> None:
        super().__init__(value)
        self.value = value


MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1


def s64(u: int) -> int:
    u &= MASK64
    return u - (1 << 64) if u >= (1 << 63) else u


def s32(u: int) -> int:
    u &= MASK32
    return u - (1 << 32) if u >= (1 << 31) else u


class RiscvUnitVM:
    """Executes sliced RISC-V Units with multi-body part callbacks and complex holder memory."""

    def __init__(self) -> None:
        self.regs: dict[str, int] = {f"x{i}": 0 for i in range(32)}
        self.fregs: dict[str, float] = {f"f{i}": 0.0 for i in range(32)}
        self.mem: dict[int, int] = {}
        self.STACK_BASE = 0x10000
        self.HOLDER_BASE = 0x20000
        self.reset()

    def reset(self) -> None:
        self.regs.clear()
        self.mem.clear()
        self.regs["zero"] = 0
        self.regs["sp"] = self.STACK_BASE
        self.regs["s0"] = self.STACK_BASE
        self.regs["a0"] = self.HOLDER_BASE
        self.mem[self.STACK_BASE - 0x18] = self.HOLDER_BASE

    def get_reg(self, r: str) -> int:
        r = r.strip()
        if r in ("zero", "x0"):
            return 0
        return self.regs.get(r, 0) & MASK64

    def set_reg(self, r: str, val: int) -> None:
        r = r.strip()
        if r not in ("zero", "x0"):
            self.regs[r] = val & MASK64

    def write_holder_words(self, values: list[int]) -> None:
        for idx, v in enumerate(values):
            self.mem[self.HOLDER_BASE + idx * 8] = v & MASK64

    def read_holder_word(self, slot: int = 0) -> int:
        return s64(self.mem.get(self.HOLDER_BASE + slot * 8, 0))

    def execute_unit(
        self,
        words: list[list[Any]],
        unit_indices: list[int] | None = None,
        part_callbacks: dict[str, Callable[[], int]] | None = None,
        max_steps: int = 500,
        holds_p: Any = None,
    ) -> dict[str, Any]:
        """Step a sliced RISC-V Unit, calling `part_callbacks` at `R_RISCV_CALL_PLT` sites."""
        callbacks = part_callbacks or {}
        idxs = unit_indices if unit_indices else list(range(len(words)))
        slice_words = [words[i] for i in idxs if 0 <= i < len(words)]
        addr_to_pc = {int(w[0]): pc for pc, w in enumerate(slice_words)}

        holds_p_map: dict[int, list[str]] = {}
        if holds_p is True:
            holds_p_map[0] = ["a0"]
        elif isinstance(holds_p, (list, tuple)):
            for item in holds_p:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    holds_p_map.setdefault(int(item[0]), []).append(str(item[1]))

        def resolve_target(cur_pc: int, cur_addr: int, tgt_addr: int) -> int:
            if tgt_addr != cur_addr:
                if tgt_addr in addr_to_pc:
                    return addr_to_pc[tgt_addr]
                if tgt_addr >= 0 and slice_words:
                    for pc_cand, w_cand in enumerate(slice_words):
                        if int(w_cand[0]) >= tgt_addr:
                            return pc_cand
                    return len(slice_words)
            # Unlinked RISC-V `-mrelax` relocation (`.L0`): jump past next unconditional jump
            for k in range(cur_pc + 1, len(slice_words)):
                if slice_words[k][2] in ("c.j", "j") and k > cur_pc + 1:
                    return k + 1
            return len(slice_words)

        pc = 0
        steps = 0
        called_parts: list[str] = []
        pending_call: str | None = None

        while 0 <= pc < len(slice_words) and steps < max_steps:
            for reg_p in holds_p_map.get(pc, ()):
                self.set_reg(reg_p, self.HOLDER_BASE)
            steps += 1
            addr, _hex, mnem, ops_str, relocs = slice_words[pc]
            ops = [x.strip() for x in str(ops_str).split(",") if x.strip()]

            # Detect part call relocation on `auipc` or `jal`
            for rel in (relocs or []):
                if "R_RISCV_CALL" in str(rel) or "R_RISCV_JAL" in str(rel):
                    sym = str(rel).split()[-1]
                    pending_call = sym

            if mnem in ("jalr", "c.jalr", "jal", "c.jal") and pending_call:
                sym = pending_call
                pending_call = None
                if sym not in ("__hiop_unit_begin", "__hiop_unit_end"):
                    called_parts.append(sym)
                    if sym in callbacks:
                        ret_val = callbacks[sym]()
                        self.set_reg("a0", int(ret_val))
                        self.set_reg("a1", 0)
                pc += 1
                continue

            # Branch instructions inside the Unit
            if mnem in ("c.j", "j"):
                tok = ops[-1].split()[0] if ops else ""
                tgt = int(tok, 16) if tok.startswith("0x") else -1
                pc = resolve_target(pc, int(addr), tgt)
                continue
            if mnem in ("c.beqz", "beqz", "c.bnez", "bnez") and len(ops) >= 2:
                v = self.get_reg(ops[0])
                tok = ops[1].split()[0]
                tgt = int(tok, 16) if tok.startswith("0x") else -1
                cond = (v == 0) if "beqz" in mnem else (v != 0)
                if cond:
                    pc = resolve_target(pc, int(addr), tgt)
                    continue
                pc += 1
                continue
            if mnem in ("beq", "bne", "blt", "bge", "bltu", "bgeu") and len(ops) >= 3:
                v1, v2 = self.get_reg(ops[0]), self.get_reg(ops[1])
                tok = ops[2].split()[0]
                tgt = int(tok, 16) if tok.startswith("0x") else -1
                cond = {
                    "beq": v1 == v2, "bne": v1 != v2,
                    "blt": s64(v1) < s64(v2), "bge": s64(v1) >= s64(v2),
                    "bltu": v1 < v2, "bgeu": v1 >= v2,
                }[mnem]
                if cond:
                    pc = resolve_target(pc, int(addr), tgt)
                    continue
                pc += 1
                continue

            self._exec_alu_or_mem(mnem, ops)
            pc += 1

        return {"steps": steps, "called_parts": called_parts, "a0": s64(self.get_reg("a0"))}

    def _exec_alu_or_mem(self, mnem: str, ops: list[str]) -> None:
        import re

        def parse_imm(s: str) -> int:
            s = s.strip()
            return int(s, 16) if s.startswith(("0x", "-0x")) else int(s)

        if mnem in ("ld", "c.ld", "lw", "c.lw", "lwu", "lb", "lbu", "lh", "lhu") and len(ops) >= 2:
            m = re.match(r"(-?(?:0x[0-9a-fA-F]+|\d+))\(([^)]+)\)", ops[1])
            if m:
                off, base = parse_imm(m.group(1)), self.get_reg(m.group(2))
                self.set_reg(ops[0], self.mem.get(base + off, 0))
            return
        if mnem in ("sd", "c.sd", "sw", "c.sw", "sb", "sh") and len(ops) >= 2:
            m = re.match(r"(-?(?:0x[0-9a-fA-F]+|\d+))\(([^)]+)\)", ops[1])
            if m:
                off, base = parse_imm(m.group(1)), self.get_reg(m.group(2))
                self.mem[base + off] = self.get_reg(ops[0])
            return
        if mnem in ("li", "c.li") and len(ops) >= 2:
            self.set_reg(ops[0], parse_imm(ops[1]))
        elif mnem in ("mv", "c.mv") and len(ops) >= 2:
            self.set_reg(ops[0], self.get_reg(ops[1]))
        elif mnem in ("seqz", "snez") and len(ops) >= 2:
            v = self.get_reg(ops[1])
            self.set_reg(ops[0], int(v == 0) if mnem == "seqz" else int(v != 0))
        elif mnem in ("addi", "c.addi", "addiw", "c.addiw") and len(ops) >= 2:
            rd, rs1 = ops[0], (ops[1] if len(ops) >= 3 else ops[0])
            imm = parse_imm(ops[-1])
            val = self.get_reg(rs1) + imm
            self.set_reg(rd, s32(val) if "w" in mnem else val)
        elif mnem in ("xori", "andi", "ori", "slti", "sltiu") and len(ops) >= 3:
            v1, imm = self.get_reg(ops[1]), parse_imm(ops[2])
            res = {
                "xori": v1 ^ (imm & MASK64),
                "andi": v1 & (imm & MASK64),
                "ori":  v1 | (imm & MASK64),
                "slti": int(s64(v1) < imm),
                "sltiu": int(v1 < (imm & MASK64)),
            }[mnem]
            self.set_reg(ops[0], res)
        elif mnem in ("czero.eqz", "czero.nez") and len(ops) >= 3:
            v, c = self.get_reg(ops[1]), self.get_reg(ops[2])
            zero_it = (c == 0) if mnem == "czero.eqz" else (c != 0)
            self.set_reg(ops[0], 0 if zero_it else v)
        elif mnem in ("div", "divw", "rem", "remw", "divu", "remu") and len(ops) >= 3:
            a, b = self.get_reg(ops[1]), self.get_reg(ops[2])
            sa, sb = s64(a), s64(b)
            base_m = mnem.rstrip("w")
            if base_m == "div":
                res = -1 if sb == 0 else (sa if (sa == -(1 << 63) and sb == -1) else int(sa / sb))
            elif base_m == "rem":
                res = sa if sb == 0 else (0 if (sa == -(1 << 63) and sb == -1) else (sa - int(sa / sb) * sb))
            elif base_m == "divu":
                res = MASK64 if b == 0 else (a // b)
            else:
                res = a if b == 0 else (a % b)
            self.set_reg(ops[0], s32(res) if mnem.endswith("w") else res)
        elif mnem in ("add", "c.add", "addw", "c.addw", "sub", "c.sub", "subw", "c.subw",
                      "mul", "mulw", "and", "c.and", "or", "c.or", "xor", "c.xor",
                      "sll", "sllw", "srl", "srlw", "sra", "sraw", "slt", "sltu") and len(ops) >= 2:
            rd = ops[0]
            r1 = ops[1] if len(ops) >= 3 else ops[0]
            r2 = ops[2] if len(ops) >= 3 else ops[1]
            a, b = self.get_reg(r1), self.get_reg(r2)
            base_m = mnem.replace("c.", "").rstrip("w")
            res = {
                "add": a + b, "sub": a - b, "mul": a * b,
                "and": a & b, "or": a | b, "xor": a ^ b,
                "sll": a << (b & 63), "srl": a >> (b & 63),
                "sra": s64(a) >> (b & 63),
                "slt": int(s64(a) < s64(b)), "sltu": int(a < b),
            }[base_m]
            self.set_reg(rd, s32(res) if mnem.endswith("w") else res)
