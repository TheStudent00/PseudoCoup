"""compose_LoOp_leans -- One term per Unit, plus its piecewise Domain-Range
partition derived directly from the Sail Lean model.

Plan: `.../node_0_0_0_0_3_map_unit_to_lean/node_0_0_0_0_3_0_compose_LoOp_leans/`.
"""

import json
import os
import re
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
import z3

from ..map_LoOp_to_lean import LoOpLean, decode_word, execute_word
import lifter as _lifter
import riscv_reference as RV

_LCPI_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rodata_lcpi_constants.json")
_LCPI_CONSTANTS: Dict[str, str] = {}
if os.path.isfile(_LCPI_PATH):
    with open(_LCPI_PATH, "r", encoding="utf-8") as _f:
        _lcpi_raw = json.load(_f)
        _LCPI_CONSTANTS = dict(_lcpi_raw.get("merged", {}))
        for _k, _v in list(_LCPI_CONSTANTS.items()):
            _tok = _k.split(":")[-1]
            if _tok not in _LCPI_CONSTANTS:
                _LCPI_CONSTANTS[_tok] = _v


def _offset_of_addr_bv(addr_bv: z3.ExprRef) -> Optional[int]:
    """Symbolically subtract `P_BASE` from `addr_bv` in Z3 to extract struct field offset."""
    p_base = z3.BitVec("P_BASE", addr_bv.size())
    diff = z3.simplify(addr_bv - p_base)
    if z3.is_bv_value(diff):
        off = diff.as_signed_long()
        if 0 <= off < 4096:
            return off
    return None


def _offset_of_sp_bv(addr_bv: z3.ExprRef) -> Optional[int]:
    """Symbolically subtract stack pointer `seed_x2` from `addr_bv` in Z3 to extract stack slot offset."""
    sp_base = z3.BitVec("seed_x2", addr_bv.size())
    diff = z3.simplify(addr_bv - sp_base)
    if z3.is_bv_value(diff):
        off = diff.as_signed_long()
        if -4096 <= off < 4096:
            return off
    return None


class DomainRangePiece(NamedTuple):
    """One disjoint feasible piece (D_k -> R_k) of a Unit's behaviour."""

    domain: z3.BoolRef
    range_term: Optional[z3.ExprRef]
    part_calls: Tuple[str, ...]
    exit_target: Optional[int]
    ext_calls: Tuple[str, ...] = ()


class UnitLean(NamedTuple):
    """The composed symbolic meaning of a lowered Unit from `map_HiOp_to_unit`."""

    loop_leans: Tuple[LoOpLean, ...]
    inputs: Dict[int, z3.ExprRef]
    output_offset: Optional[int]
    output_width: Optional[int]
    combined_term: Optional[z3.ExprRef]
    pieces: Tuple[DomainRangePiece, ...]
    is_straight_line: bool
    ext_calls: Tuple[str, ...] = ()


class SymbolicUnitState(RV.MachineState):
    """Symbolic machine state tracking struct `P_BASE` reads/writes and stack cells."""

    def __init__(self, shared_seed=None):
        super().__init__(shared_seed)
        self.mem_map: Dict[Tuple[str, int], z3.ExprRef] = {}
        self.p_inputs: Dict[int, z3.ExprRef] = {}
        self.last_p_write: Optional[Tuple[int, int, z3.ExprRef]] = None
        self.last_sp_write: Optional[Tuple[int, int, z3.ExprRef]] = None
        self.ignore_p_input: bool = False
        self.part_calls: List[str] = []
        self.ext_calls: List[str] = []
        self.rodata_bytes: Dict[str, bytes] = {}
        self.call_written_iregs: set[int] = set()
        self.call_written_fregs: set[int] = set()
        self.last_call_ret_a0: bool = False
        self.exit_target: Optional[int] = None

    def clone(self) -> "SymbolicUnitState":
        c = SymbolicUnitState(self.shared_seed)
        c.registers = dict(self.registers)
        c.fregisters = dict(self.fregisters)
        c.mem_map = dict(self.mem_map)
        c.p_inputs = dict(self.p_inputs)
        c.last_p_write = self.last_p_write
        c.last_sp_write = self.last_sp_write
        c.ignore_p_input = self.ignore_p_input
        c.part_calls = list(self.part_calls)
        c.ext_calls = list(self.ext_calls)
        c.rodata_bytes = dict(self.rodata_bytes)
        c.call_written_iregs = set(self.call_written_iregs)
        c.call_written_fregs = set(self.call_written_fregs)
        c.last_call_ret_a0 = self.last_call_ret_a0
        c.exit_target = self.exit_target
        c.path_condition = self.path_condition
        return c

    def write_register(self, reg_idx: int, value: z3.ExprRef) -> None:
        super().write_register(reg_idx, value)
        if reg_idx != 0:
            self.call_written_iregs.add(reg_idx)

    def write_float(self, reg_idx: int, value: z3.ExprRef) -> None:
        super().write_float(reg_idx, value)
        self.call_written_fregs.add(reg_idx)

    def read_mem_bytes(self, addr_bv: z3.ExprRef, width: int) -> z3.ExprRef:
        if self.ignore_p_input:
            return z3.BitVecVal(0, width * 8)
        for base_name, raw_bytes in self.rodata_bytes.items():
            diff = z3.simplify(addr_bv - z3.BitVec(base_name, addr_bv.size()))
            if z3.is_bv_value(diff):
                roff = diff.as_signed_long()
                if 0 <= roff and roff + width <= len(raw_bytes):
                    val_int = int.from_bytes(raw_bytes[roff : roff + width], "little")
                    return z3.BitVecVal(val_int, width * 8)
        addr_s = str(z3.simplify(addr_bv))
        key = (addr_s, width)
        if key not in self.mem_map:
            off = _offset_of_addr_bv(addr_bv)
            if off is not None:
                sym = z3.BitVec(f"in_off_{off}", width * 8)
                self.p_inputs[off] = sym
                self.mem_map[key] = sym
            else:
                self.mem_map[key] = z3.BitVec(f"mem_{addr_s}_{width}", width * 8)
        return self.mem_map[key]

    def write_mem_bytes(self, addr_bv: z3.ExprRef, width: int, data_bv: z3.ExprRef) -> None:
        addr_s = str(z3.simplify(addr_bv))
        key = (addr_s, width)
        val = z3.simplify(data_bv)
        self.mem_map[key] = val
        off = _offset_of_addr_bv(addr_bv)
        if off is not None:
            self.last_p_write = (off, width, val)
        else:
            sp_off = _offset_of_sp_bv(addr_bv)
            if sp_off is not None and str(val) != "P_BASE" and not str(val).startswith("rodata_"):
                self.last_sp_write = (sp_off, width, val)


def _count_ites(expr: z3.ExprRef, limit: int = 12) -> int:
    seen: set[int] = set()
    ite_count = 0
    stack = [expr]
    while stack:
        cur = stack.pop()
        cid = cur.get_id()
        if cid in seen:
            continue
        seen.add(cid)
        if z3.is_app_of(cur, z3.Z3_OP_ITE):
            ite_count += 1
            if ite_count > limit:
                return ite_count
        for i in range(cur.num_args()):
            stack.append(cur.arg(i))
    return ite_count


def _find_first_ite_any(expr: z3.ExprRef) -> Optional[z3.ExprRef]:
    if z3.is_app_of(expr, z3.Z3_OP_ITE):
        return expr
    for i in range(expr.num_args()):
        hit = _find_first_ite_any(expr.arg(i))
        if hit is not None:
            return hit
    return None


def split_ite_complete(
    term: z3.ExprRef, cond: Optional[z3.BoolRef] = None
) -> List[Tuple[z3.BoolRef, z3.ExprRef]]:
    """Hoist all nested Z3 ITEs to top level and prune infeasible branches via Z3."""
    if cond is None:
        cond = z3.BoolVal(True)
    term = z3.simplify(term)
    if _count_ites(term, 12) > 12:
        return [(cond, term)]
    if z3.is_app_of(term, z3.Z3_OP_ITE):
        inner = _find_first_ite_any(term.arg(0))
        if inner is not None:
            ic, it, ie = inner.arg(0), inner.arg(1), inner.arg(2)
            t_b = z3.substitute(term, (inner, it))
            e_b = z3.substitute(term, (inner, ie))
            return split_ite_complete(z3.If(ic, t_b, e_b), cond)
        c, t, e = term.arg(0), term.arg(1), term.arg(2)
        out: List[Tuple[z3.BoolRef, z3.ExprRef]] = []
        s = z3.Solver()
        c_true = z3.simplify(z3.And(cond, c))
        if s.check(c_true) == z3.sat:
            out.extend(split_ite_complete(t, c_true))
        c_false = z3.simplify(z3.And(cond, z3.Not(c)))
        if s.check(c_false) == z3.sat:
            out.extend(split_ite_complete(e, c_false))
        return out
    inner = _find_first_ite_any(term)
    if inner is not None:
        ic, it, ie = inner.arg(0), inner.arg(1), inner.arg(2)
        t_b = z3.substitute(term, (inner, it))
        e_b = z3.substitute(term, (inner, ie))
        return split_ite_complete(z3.If(ic, t_b, e_b), cond)
    return [(cond, term)]


def _part_reloc_of(word) -> Optional[str]:
    for r in getattr(word, "relocations", ()):
        tokens = [str(x) for x in r] if isinstance(r, tuple) else str(r).split()
        for tok in tokens:
            if tok.startswith("part_"):
                return re.sub(r"^part_(?:func_\d+_)?", "part_", tok)
            m = re.match(r"^_Z\d+(part_(?:func_\d+_)?[A-Za-z0-9_]+?)v?$", tok)
            if m:
                return re.sub(r"^part_(?:func_\d+_)?", "part_", m.group(1))
    return None


def _reloc_kind_and_sym(word) -> Optional[Tuple[str, str]]:
    for r in getattr(word, "relocations", ()):
        tokens = [str(x) for x in r] if isinstance(r, tuple) else str(r).split()
        if len(tokens) >= 2:
            kind = tokens[0] if tokens[0].startswith("R_RISCV_") else (tokens[1] if len(tokens) >= 3 else tokens[0])
            return kind, tokens[-1]
    return None


TRAP_ARCH_OPCODES = ("c.unimp", "unimp", "ebreak", "c.ebreak")
TRAP_CALL_SYMBOLS = ("abort", "exit", "_Exit", "__assert_fail")


def compose_LoOp_leans(unit_or_mapped: Any, max_steps: int = 256, max_explored: int = 2048) -> UnitLean:
    """Step each LoOp word of a hijacked Unit through the Sail Lean model and
    return its composed `UnitLean` and piecewise `(D_k, R_k)` partition."""
    unit = getattr(unit_or_mapped, "unit", unit_or_mapped)
    words = tuple(unit.words)
    holds_p_dict = dict(getattr(unit, "holds_p", ()))

    def next_idx_for_pc(target_pc: int) -> int:
        for i, w in enumerate(words):
            if w.address >= target_pc:
                return i
        return len(words)

    loop_leans = tuple(
        decode_word(int(w.bytes_hex, 16), len(w.bytes_hex) // 2)
        for w in words
        if _part_reloc_of(w) is None and w.arch_opcode not in TRAP_ARCH_OPCODES
    )
    finished_paths: List[SymbolicUnitState] = []
    trapped_paths: List[SymbolicUnitState] = []
    all_inputs: Dict[int, z3.ExprRef] = {}
    queue: List[Tuple[int, SymbolicUnitState, int]] = [(0, SymbolicUnitState(), 0)]
    explored = 0

    while queue:
        explored += 1
        if explored > max_explored:
            raise _lifter.LiftRefused(
                f"MAX_PATHS_EXCEEDED: unit exceeded {max_explored} symbolic execution steps"
            )
        idx, st, steps = queue.pop(0)
        if idx >= len(words) or steps >= max_steps:
            finished_paths.append(st)
            all_inputs.update(st.p_inputs)
            continue
        w = words[idx]
        if idx in holds_p_dict:
            reg_name = holds_p_dict[idx]
            if reg_name in RV.INTEGER_REGISTERS:
                r_idx = RV.INTEGER_REGISTERS[reg_name]
                st.bind(r_idx, z3.BitVec("P_BASE", 64))
                if getattr(w, "relocations", ()):
                    st.call_written_iregs.add(r_idx)
        part_sym = _part_reloc_of(w)
        if part_sym is not None:
            st.part_calls.append(part_sym)
            st.write_register(10, z3.BitVec(f"{part_sym}_ret", 64))
            st.write_float(10, z3.BitVec(f"{part_sym}_fret", 64))
            skip = 2 if (idx + 1 < len(words) and words[idx + 1].arch_opcode == "jalr") else 1
            queue.append((idx + skip, st, steps + 1))
            continue
        rel_info = _reloc_kind_and_sym(w)
        if rel_info is not None:
            kind, sym = rel_info
            if kind in ("R_RISCV_PCREL_HI20", "R_RISCV_GOT_HI20"):
                rd = (int(w.bytes_hex, 16) >> 7) & 0x1F
                base_name = f"rodata_{sym}"
                st.write_register(rd, z3.BitVec(base_name, 64))
                u_sym = getattr(unit, "symbol", "")
                hex_b = _LCPI_CONSTANTS.get(f"{u_sym}:{sym}") or _LCPI_CONSTANTS.get(sym)
                if hex_b is not None:
                    st.rodata_bytes[base_name] = bytes.fromhex(hex_b)
                nxt_rel = _reloc_kind_and_sym(words[idx + 1]) if idx + 1 < len(words) else None
                if nxt_rel is not None and nxt_rel[0] == "R_RISCV_PCREL_LO12_I":
                    rd_lo = (int(words[idx + 1].bytes_hex, 16) >> 7) & 0x1F
                    st.write_register(rd_lo, z3.BitVec(base_name, 64))
                    skip = 2
                else:
                    skip = 1
                queue.append((idx + skip, st, steps + 1))
                continue
            if kind == "R_RISCV_PCREL_LO12_I":
                queue.append((idx + 1, st, steps + 1))
                continue
            if kind == "R_RISCV_CALL_PLT":
                if (
                    sym in TRAP_CALL_SYMBOLS
                    or sym.startswith(("__ubsan_handle_", "__asan_report_", "__asan_handle_no_return", "runtime.panic", "runtime.gopanic"))
                    or "panicking" in sym
                ):
                    st_trap = st.clone()
                    st_trap.last_p_write = None
                    st_trap.last_sp_write = None
                    st_trap.exit_target = w.address
                    st_trap.ext_calls.append(sym)
                    trapped_paths.append(st_trap)
                    all_inputs.update(st_trap.p_inputs)
                    continue
                st.ext_calls.append(sym)
                call_args: List[z3.ExprRef] = []
                for ireg in sorted(st.call_written_iregs):
                    if 10 <= ireg <= 17 and ireg in st.registers:
                        rval = z3.simplify(st.registers[ireg])
                        if _offset_of_addr_bv(rval) is not None:
                            call_args.append(st.read_mem_bytes(rval, 8))
                        else:
                            call_args.append(rval)
                for freg in sorted(st.call_written_fregs):
                    if 10 <= freg <= 17 and freg in st.fregisters:
                        call_args.append(z3.simplify(st.fregisters[freg]))
                if not call_args:
                    if st.last_call_ret_a0 and 10 in st.registers:
                        call_args.append(z3.simplify(st.registers[10]))
                    else:
                        call_args.append(z3.BitVecVal(0, 64))
                all_inputs.update(st.p_inputs)
                arg_sorts = [a.sort() for a in call_args]
                bv64 = z3.BitVecSort(64)
                st.call_written_iregs.clear()
                st.call_written_fregs.clear()
                for clob in range(12, 18):
                    st.registers.pop(clob, None)
                    st.fregisters.pop(clob, None)
                st.registers[10] = z3.Function(f"call_{sym}_a0", *arg_sorts, bv64)(*call_args)
                st.registers[11] = z3.Function(f"call_{sym}_a1", *arg_sorts, bv64)(*call_args)
                st.fregisters[10] = z3.Function(f"call_{sym}_fa0", *arg_sorts, bv64)(*call_args)
                st.fregisters[11] = z3.Function(f"call_{sym}_fa1", *arg_sorts, bv64)(*call_args)
                st.last_call_ret_a0 = True
                skip = 2 if (idx + 1 < len(words) and words[idx + 1].arch_opcode == "jalr") else 1
                queue.append((idx + skip, st, steps + 1))
                continue
            raise _lifter.LiftRefused(
                f"UNLINKED_RELOC for {w.arch_opcode} at 0x{w.address:x}: {w.relocations}"
            )
        if w.arch_opcode in TRAP_ARCH_OPCODES:
            st_trap = st.clone()
            st_trap.last_p_write = None
            st_trap.exit_target = w.address
            trapped_paths.append(st_trap)
            all_inputs.update(st_trap.p_inputs)
            continue

        w_int = int(w.bytes_hex, 16)
        size = len(w.bytes_hex) // 2
        st.ignore_p_input = (
            w.arch_opcode in ("lb", "lh", "lw", "ld", "lbu", "lhu", "lwu")
            and getattr(w, "operands", "").startswith("zero,")
        )
        _res, mach, _llean = execute_word(w_int, size, st, pc=w.address)
        st.ignore_p_input = False
        all_inputs.update(st.p_inputs)

        npc = z3.simplify(mach.registers["nextPC"])
        if z3.is_bv_value(npc):
            t_pc = npc.as_long()
            n_idx = next_idx_for_pc(t_pc)
            if n_idx <= idx:
                st.exit_target = t_pc
                finished_paths.append(st)
            elif (
                t_pc == w.address + size
                and n_idx < len(words)
                and words[n_idx].address > t_pc
                and n_idx not in holds_p_dict
                and any("panic" in str(r) for rem_w in words[n_idx:] for r in getattr(rem_w, "relocations", ()))
            ):
                st.exit_target = t_pc
                finished_paths.append(st)
            else:
                queue.append((n_idx, st, steps + 1))
        elif z3.is_app_of(npc, z3.Z3_OP_ITE):
            cond = npc.arg(0)
            t_pc = z3.simplify(npc.arg(1)).as_long()
            f_pc = z3.simplify(npc.arg(2)).as_long()
            for br_cond, br_pc in ((cond, t_pc), (z3.Not(cond), f_pc)):
                st_b = st.clone()
                st_b.path_condition = z3.simplify(z3.And(st.path_condition, br_cond))
                s = z3.Solver()
                if s.check(st_b.path_condition) == z3.sat:
                    n_idx = next_idx_for_pc(br_pc)
                    if n_idx <= idx:
                        st_b.exit_target = br_pc
                        finished_paths.append(st_b)
                    else:
                        queue.append((n_idx, st_b, steps + 1))
        else:
            finished_paths.append(st)

    if not finished_paths and trapped_paths:
        trap_ops = [w.arch_opcode for w in words if w.arch_opcode in TRAP_ARCH_OPCODES]
        trap_calls = [ec for st in trapped_paths for ec in st.ext_calls]
        raise _lifter.LiftRefused(
            f"TRAP_ONLY_UNIT: all {len(trapped_paths)} paths ended in hardware trap {trap_ops or trap_calls}"
        )

    pieces: List[DomainRangePiece] = []
    out_off: Optional[int] = None
    out_w: Optional[int] = None
    ret_ext_calls: List[str] = []
    has_any_p_write = any(st.last_p_write is not None for st in finished_paths)
    for st in finished_paths:
        for ec in st.ext_calls:
            if ec not in ret_ext_calls:
                ret_ext_calls.append(ec)
        write_rec = st.last_p_write if has_any_p_write else (st.last_sp_write if len(finished_paths) <= 6 else None)
        if write_rec is not None:
            out_off, out_w, val = write_rec
            for d_sub, r_sub in split_ite_complete(val, st.path_condition):
                pieces.append(DomainRangePiece(d_sub, r_sub, tuple(st.part_calls), st.exit_target, tuple(st.ext_calls)))
        else:
            pieces.append(DomainRangePiece(st.path_condition, None, tuple(st.part_calls), st.exit_target, tuple(st.ext_calls)))
    for st in trapped_paths:
        pieces.append(DomainRangePiece(st.path_condition, None, tuple(st.part_calls), st.exit_target, tuple(st.ext_calls)))

    combined: Optional[z3.ExprRef] = None
    val_pieces = [(p.domain, p.range_term) for p in pieces if p.range_term is not None]
    if val_pieces:
        max_bw = max((r.size() for _, r in val_pieces if z3.is_bv(r)), default=64)
        norm_pieces = [
            (d_k, z3.ZeroExt(max_bw - r_k.size(), r_k) if (z3.is_bv(r_k) and r_k.size() < max_bw) else r_k)
            for d_k, r_k in val_pieces
        ]
        combined = norm_pieces[-1][1]
        for d_k, r_k in reversed(norm_pieces[:-1]):
            combined = z3.If(d_k, r_k, combined)
        combined = z3.simplify(combined)

    return UnitLean(
        loop_leans=tuple(loop_leans),
        inputs=dict(sorted(all_inputs.items())),
        output_offset=out_off,
        output_width=out_w,
        combined_term=combined,
        pieces=tuple(pieces),
        is_straight_line=(len(finished_paths) <= 1),
        ext_calls=tuple(ret_ext_calls),
    )
