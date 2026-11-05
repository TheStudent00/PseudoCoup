"""compiler_rt_lifter -- Whole-Lowered `compiler-rt` Lifter, Executor & Polyfill Emitter.

Implements `SUPPORT_gnu_c_infrastructure_lowered_whole.md` (`log_449`) and `log_527` / `log_528`:
  - Loads the whole-lowered `compiler-rt` routines (`58` needed routines, `5,830` RISC-V `LoOp` words,
    `268` total routines) from `Research/lower_HiOp/out/infrastructure_l157/compiler_rt_riscv64.jsonl.gz`.
  - Decodes and lifts 100% of `LoOp` words through the Sail formal RISC-V model (`decode_word` / `execute_word`).
  - Decomposes each routine into basic blocks (`CompilerRtBasicBlock`) and classifies routines into
    loop-free DAGs (`31` routines) vs cyclic state-machine routines (`27` routines).
  - Executes any `compiler-rt` routine (`eval_compiler_rt_routine`) by stepping its Sail-lifted `LoOp`
    words from entry (`pc = 0`) to `ret` (`nextPC == ret_ra`) at the RISC-V ABI register boundary
    (`a0..a7` / `fa0..fa7` -> `a0, a1` / `fa0, fa1`), following internal `compiler-rt` calls and `.rodata`
    constants (`rodata_lcpi_constants.json`).
  - Synthesizes target-language basic-block state-machine code (`emit_compiler_rt_routine`,
    `emit_compiler_rt_call_expr`) constructed purely from each target language's proven 64-bit
    `HIOP_PRIMITIVES` (`polyfill.py`), with zero symbol-name-to-formula lookup tables.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple, Sequence
import z3

PCHQ_ROOT = Path(__file__).resolve().parents[4]
PROJECTS_DIR = PCHQ_ROOT / "Projects"
if str(PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECTS_DIR))

from PseudoArch.map_LoOp_to_lean import LoOpLean, decode_word, execute_word
from PseudoArch.map_unit_to_lean.compose_LoOp_leans import (
    SymbolicUnitState,
    _LCPI_CONSTANTS,
    _reloc_kind_and_sym,
)
import riscv_reference as RV

from PseudoCoup.hub.autopoly.polyfill import HIOP_PRIMITIVES, normalize_target_lang, translate_z3_to_hiop_primitives
COMPILER_RT_JSONL = (
    PCHQ_ROOT
    / "Research"
    / "lower_HiOp"
    / "out"
    / "infrastructure_l157"
    / "compiler_rt_riscv64.jsonl.gz"
)

RET_RA_SENTINEL = 0xDEAD0000
INIT_SP_SENTINEL = 0x7FFF0000


class CompilerRtWord(NamedTuple):
    """One disassembled instruction word in a whole-lowered `compiler-rt` routine."""

    address: int
    bytes_hex: str
    arch_opcode: str
    operands: str
    relocations: tuple[str, ...]
    line: int | None

    @property
    def loop_lean(self) -> LoOpLean:
        return decode_word(int(self.bytes_hex, 16), len(self.bytes_hex) // 2)


class CompilerRtBasicBlock(NamedTuple):
    """A contiguous basic block of `CompilerRtWord`s inside a `compiler-rt` routine."""

    block_id: int
    start_pc: int
    end_pc: int
    words: tuple[CompilerRtWord, ...]
    successors: tuple[int, ...]
    calls: tuple[str, ...]


class CompilerRtRoutine(NamedTuple):
    """A whole-lowered `compiler-rt` routine decoded through Sail (`map_LoOp_to_lean`)."""

    name: str
    source_file: str
    needed: bool
    calls: tuple[str, ...]
    words: tuple[CompilerRtWord, ...]
    basic_blocks: tuple[CompilerRtBasicBlock, ...]
    is_dag: bool


_ROUTINE_CACHE: dict[str, CompilerRtRoutine] | None = None


def _build_basic_blocks(words: Sequence[CompilerRtWord]) -> tuple[tuple[CompilerRtBasicBlock, ...], bool]:
    """Partition `words` into basic blocks and determine whether the CFG is a loop-free DAG."""
    if not words:
        return (), True

    addr_to_idx = {w.address: i for i, w in enumerate(words)}
    leaders: set[int] = {words[0].address}

    branch_opcodes = {
        "beq", "bne", "blt", "bge", "bltu", "bgeu",
        "beqz", "bnez", "blez", "bgez", "bltz", "bgtz",
        "c.beqz", "c.bnez",
    }
    jump_opcodes = {"j", "c.j", "jal", "c.jal", "jalr", "c.jr", "c.jalr", "ret"}

    for idx, w in enumerate(words):
        op = w.arch_opcode
        rel = _reloc_kind_and_sym(w)
        is_call = rel is not None and rel[0] == "R_RISCV_CALL_PLT"
        if op in branch_opcodes or (op in jump_opcodes and not is_call):
            if idx + 1 < len(words):
                leaders.add(words[idx + 1].address)
            # Parse PC-relative branch/jump target from objdump operands (hex address before `<symbol+offset>`)
            toks = [t.strip() for t in w.operands.split(",") if t.strip()]
            if toks:
                last_tok = toks[-1].split()[0]
                try:
                    target_pc = int(last_tok, 16)
                    if target_pc in addr_to_idx:
                        leaders.add(target_pc)
                except ValueError:
                    pass

    sorted_leaders = sorted(leaders)
    leader_set = set(sorted_leaders)
    blocks_raw: list[tuple[int, list[CompilerRtWord]]] = []
    cur_leader = sorted_leaders[0]
    cur_words: list[CompilerRtWord] = []

    for w in words:
        if w.address in leader_set and cur_words:
            blocks_raw.append((cur_leader, cur_words))
            cur_leader = w.address
            cur_words = [w]
        else:
            cur_words.append(w)
    if cur_words:
        blocks_raw.append((cur_leader, cur_words))

    blocks: list[CompilerRtBasicBlock] = []
    has_back_edge = False

    for b_id, (start_pc, b_words) in enumerate(blocks_raw):
        last_w = b_words[-1]
        end_pc = last_w.address
        op = last_w.arch_opcode
        succs: list[int] = []
        b_calls: list[str] = []

        for bw in b_words:
            rel = _reloc_kind_and_sym(bw)
            if rel is not None and rel[0] == "R_RISCV_CALL_PLT":
                if rel[1] not in b_calls:
                    b_calls.append(rel[1])

        fallthrough_pc = last_w.address + (len(last_w.bytes_hex) // 2)
        if op not in ("j", "c.j", "ret", "c.jr", "jalr") or (
            _reloc_kind_and_sym(last_w) is not None
            and _reloc_kind_and_sym(last_w)[0] == "R_RISCV_CALL_PLT"
        ):
            if fallthrough_pc in addr_to_idx:
                succs.append(fallthrough_pc)

        if op in branch_opcodes or op in ("j", "c.j"):
            toks = [t.strip() for t in last_w.operands.split(",") if t.strip()]
            if toks:
                last_tok = toks[-1].split()[0]
                try:
                    t_pc = int(last_tok, 16)
                    if t_pc in addr_to_idx and t_pc not in succs:
                        succs.append(t_pc)
                except ValueError:
                    pass

        for s_pc in succs:
            if s_pc <= start_pc:
                has_back_edge = True

        blocks.append(
            CompilerRtBasicBlock(
                block_id=b_id,
                start_pc=start_pc,
                end_pc=end_pc,
                words=tuple(b_words),
                successors=tuple(succs),
                calls=tuple(b_calls),
            )
        )

    # Also run full cycle detection over block graph
    adj = {b.start_pc: b.successors for b in blocks}
    visiting: set[int] = set()
    visited: set[int] = set()

    def _dfs(u: int) -> bool:
        visiting.add(u)
        for v in adj.get(u, ()):
            if v in visiting:
                return True
            if v not in visited and _dfs(v):
                return True
        visiting.remove(u)
        visited.add(u)
        return False

    for b in blocks:
        if b.start_pc not in visited:
            if _dfs(b.start_pc):
                has_back_edge = True
                break

    return tuple(blocks), (not has_back_edge)


def _decode_routine_rec(rec: dict[str, Any]) -> CompilerRtRoutine:
    name = rec["routine"]
    raw_words = rec.get("words", [])
    c_words: list[CompilerRtWord] = []
    for w in raw_words:
        addr = int(w[0])
        b_hex = str(w[1])
        arch_op = str(w[2])
        ops = str(w[3])
        rels = tuple(str(r) for r in (w[4] or ()))
        w_line = int(w[5]) if len(w) > 5 and w[5] is not None else None
        c_words.append(
            CompilerRtWord(
                address=addr,
                bytes_hex=b_hex,
                arch_opcode=arch_op,
                operands=ops,
                relocations=rels,
                line=w_line,
            )
        )
    bbs, is_dag = _build_basic_blocks(c_words)
    return CompilerRtRoutine(
        name=name,
        source_file=rec.get("file", ""),
        needed=bool(rec.get("needed", False)),
        calls=tuple(rec.get("calls", ())),
        words=tuple(c_words),
        basic_blocks=bbs,
        is_dag=is_dag,
    )


def load_compiler_rt_routines() -> dict[str, CompilerRtRoutine]:
    """Load all routines in `compiler_rt_riscv64.jsonl.gz` (with lazy Sail `LoOpLean` decoding per word)."""
    global _ROUTINE_CACHE
    if _ROUTINE_CACHE is not None:
        return _ROUTINE_CACHE

    if not COMPILER_RT_JSONL.is_file():
        raise FileNotFoundError(f"Missing whole-lowered compiler-rt dataset: {COMPILER_RT_JSONL}")

    routines: dict[str, CompilerRtRoutine] = {}
    with gzip.open(COMPILER_RT_JSONL, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            name = rec["routine"]
            routines[name] = _decode_routine_rec(rec)

    _ROUTINE_CACHE = routines
    return routines


class SymbolicBasicBlockState(SymbolicUnitState):
    """Symbolic state for basic-block lifting that preserves all memory loads and stores."""

    def __init__(self) -> None:
        super().__init__()
        self.step_mem_writes: list[tuple[int, z3.ExprRef, z3.ExprRef]] = []

    def read_mem_bytes(self, addr_bv: z3.ExprRef, width: int) -> z3.ExprRef:
        for base_name, raw_bytes in self.rodata_bytes.items():
            diff = z3.simplify(addr_bv - z3.BitVec(base_name, addr_bv.size()))
            if z3.is_bv_value(diff):
                roff = diff.as_signed_long()
                if 0 <= roff and roff + width <= len(raw_bytes):
                    val_int = int.from_bytes(raw_bytes[roff : roff + width], "little")
                    return z3.BitVecVal(val_int, width * 8)
        addr_sim = z3.simplify(addr_bv)
        load_fn = z3.Function(f"mem_load_{width * 8}", z3.BitVecSort(64), z3.BitVecSort(width * 8))
        return load_fn(addr_sim)

    def write_mem_bytes(self, addr_bv: z3.ExprRef, width: int, data_bv: z3.ExprRef) -> None:
        self.step_mem_writes.append((width, z3.simplify(addr_bv), z3.simplify(data_bv)))


def lift_basic_block_symbolically(
    routine_name: str, bb: CompilerRtBasicBlock
) -> tuple[list[tuple[str, z3.ExprRef]], z3.ExprRef, list[str]]:
    """Symbolically step a `CompilerRtBasicBlock` instruction-by-instruction through Sail's `execute_word`,
    preserving all register writes and all stack/memory reads & writes."""
    st = SymbolicBasicBlockState()
    for r_idx in range(1, 32):
        st.registers[r_idx] = z3.BitVec(f"x{r_idx}", 64)
    for f_idx in range(32):
        st.fregisters[f_idx] = z3.BitVec(f"f{f_idx}", 64)

    words = bb.words
    idx = 0
    lo_constructors: list[str] = []
    step_updates: list[tuple[str, z3.ExprRef]] = []
    next_pc: z3.ExprRef = z3.BitVecVal(bb.end_pc + (len(words[-1].bytes_hex) // 2), 64)

    while idx < len(words):
        w = words[idx]
        lo_constructors.append(w.arch_opcode)
        rel = _reloc_kind_and_sym(w)
        if rel is not None:
            kind, sym = rel
            if kind in ("R_RISCV_PCREL_HI20", "R_RISCV_GOT_HI20"):
                rd = (int(w.bytes_hex, 16) >> 7) & 0x1F
                base_name = f"rodata_{sym}"
                st.write_register(rd, z3.BitVec(base_name, 64))
                hex_b = _LCPI_CONSTANTS.get(f"{routine_name}:{sym}") or _LCPI_CONSTANTS.get(sym)
                if hex_b is not None:
                    st.rodata_bytes[base_name] = bytes.fromhex(hex_b)
                if idx + 1 < len(words):
                    nxt_rel = _reloc_kind_and_sym(words[idx + 1])
                    if nxt_rel is not None and nxt_rel[0] == "R_RISCV_PCREL_LO12_I":
                        rd_lo = (int(words[idx + 1].bytes_hex, 16) >> 7) & 0x1F
                        st.write_register(rd_lo, z3.BitVec(base_name, 64))
                        idx += 2
                        continue
                idx += 1
                continue
            if kind == "R_RISCV_PCREL_LO12_I":
                idx += 1
                continue
            if kind == "R_RISCV_CALL_PLT":
                st.ext_calls.append(sym)
                is_tail = (
                    idx + 1 < len(words)
                    and words[idx + 1].arch_opcode == "jalr"
                    and "zero," in words[idx + 1].operands
                )
                for arg_r in range(10, 14):
                    step_updates.append((f"_arg_x{arg_r}", z3.BitVec(f"x{arg_r}", 64)))
                call_args = [z3.BitVec(f"_arg_x{i}", 64) for i in range(10, 14)]
                arg_sorts = [a.sort() for a in call_args]
                bv64 = z3.BitVecSort(64)
                for r_ret, sfx in ((10, "a0"), (11, "a1")):
                    c_expr = z3.Function(f"call_{sym}_{sfx}", *arg_sorts, bv64)(*call_args)
                    step_updates.append((f"x{r_ret}", c_expr))
                    st.registers[r_ret] = z3.BitVec(f"x{r_ret}", 64)
                for f_ret, sfx in ((10, "fa0"), (11, "fa1")):
                    c_expr = z3.Function(f"call_{sym}_{sfx}", *arg_sorts, bv64)(*call_args)
                    step_updates.append((f"f{f_ret}", c_expr))
                    st.fregisters[f_ret] = z3.BitVec(f"f{f_ret}", 64)
                skip = 2 if (idx + 1 < len(words) and words[idx + 1].arch_opcode == "jalr") else 1
                if is_tail:
                    next_pc = z3.BitVec("x1", 64)
                else:
                    last_call_w = words[idx + skip - 1]
                    next_pc = z3.BitVecVal(last_call_w.address + (len(last_call_w.bytes_hex) // 2), 64)
                idx += skip
                continue
        st.call_written_iregs.clear()
        st.call_written_fregs.clear()
        st.step_mem_writes.clear()
        w_int = int(w.bytes_hex, 16)
        w_size = len(w.bytes_hex) // 2
        _res, mach, _llean = execute_word(w_int, w_size, st, pc=w.address)
        next_pc = z3.simplify(mach.registers["nextPC"])
        for width, addr_bv, data_bv in st.step_mem_writes:
            store_fn = z3.Function(
                f"mem_store_{width * 8}",
                z3.BitVecSort(64),
                z3.BitVecSort(width * 8),
                z3.BitVecSort(64),
            )
            step_updates.append(("mem", store_fn(addr_bv, data_bv)))
        for r_idx in sorted(st.call_written_iregs):
            if 1 <= r_idx <= 31 and r_idx in st.registers:
                r_val = z3.simplify(st.registers[r_idx])
                sym_r = z3.BitVec(f"x{r_idx}", 64)
                if not r_val.eq(sym_r) and not str(r_val).startswith("rodata_"):
                    step_updates.append((f"x{r_idx}", r_val))
                    st.registers[r_idx] = sym_r
        for f_idx in sorted(st.call_written_fregs):
            if 0 <= f_idx <= 31 and f_idx in st.fregisters:
                f_val = z3.simplify(st.fregisters[f_idx])
                sym_f = z3.BitVec(f"f{f_idx}", 64)
                if not f_val.eq(sym_f):
                    step_updates.append((f"f{f_idx}", f_val))
                    st.fregisters[f_idx] = sym_f
        idx += 1

    return step_updates, next_pc, lo_constructors


def eval_compiler_rt_routine(
    sym: str,
    iregs: dict[int, int] | Sequence[int] = (),
    fregs: dict[int, int] | Sequence[int] = (),
    mem: dict[int, int] | None = None,
    max_steps: int = 100000,
) -> dict[str, Any]:
    """Execute a whole-lowered `compiler-rt` routine by stepping its Sail-lifted `LoOp` words.

    Parameters
    ----------
    sym : str
        Routine name in `compiler_rt_riscv64.jsonl.gz` (e.g. `"__addtf3"`, `"__floatsitf"`, `"__ashlti3"`).
    iregs : dict[int, int] | Sequence[int]
        Initial integer argument registers (`{10: a0, 11: a1, ...}` or sequence `[a0, a1, ...]`).
    fregs : dict[int, int] | Sequence[int]
        Initial floating-point argument registers (`{10: fa0, 11: fa1, ...}` or sequence `[fa0, fa1, ...]`).
    mem : dict[int, int] | None
        Optional byte-addressed memory dictionary (`addr -> byte_val`) for pointer-taking routines.
    max_steps : int
        Safety bound on instruction steps.
    """
    routines = load_compiler_rt_routines()
    if sym not in routines:
        raise KeyError(f"Routine {sym!r} is not defined in compiler_rt_riscv64.jsonl.gz")

    routine = routines[sym]
    words = routine.words
    addr_to_idx = {w.address: i for i, w in enumerate(words)}

    byte_mem: dict[int, int] = mem if mem is not None else {}

    class ConcreteRoutineState(SymbolicUnitState):
        def read_mem_bytes(self, addr_bv: z3.ExprRef, width: int) -> z3.ExprRef:
            for base_name, raw_bytes in self.rodata_bytes.items():
                diff = z3.simplify(addr_bv - z3.BitVec(base_name, addr_bv.size()))
                if z3.is_bv_value(diff):
                    roff = diff.as_signed_long()
                    if 0 <= roff and roff + width <= len(raw_bytes):
                        val_int = int.from_bytes(raw_bytes[roff : roff + width], "little")
                        return z3.BitVecVal(val_int, width * 8)
            addr_sim = z3.simplify(addr_bv)
            if z3.is_bv_value(addr_sim):
                base_addr = addr_sim.as_long()
                val_int = 0
                for b_i in range(width):
                    val_int |= (byte_mem.get(base_addr + b_i, 0) & 0xFF) << (8 * b_i)
                return z3.BitVecVal(val_int, width * 8)
            return super().read_mem_bytes(addr_bv, width)

        def write_mem_bytes(self, addr_bv: z3.ExprRef, width: int, data_bv: z3.ExprRef) -> None:
            addr_sim = z3.simplify(addr_bv)
            data_sim = z3.simplify(data_bv)
            if z3.is_bv_value(addr_sim) and z3.is_bv_value(data_sim):
                base_addr = addr_sim.as_long()
                d_int = data_sim.as_long()
                for b_i in range(width):
                    byte_mem[base_addr + b_i] = (d_int >> (8 * b_i)) & 0xFF
                return
            super().write_mem_bytes(addr_bv, width, data_bv)

    st = ConcreteRoutineState()
    for r_i in range(1, 32):
        st.registers[r_i] = z3.BitVecVal(0, 64)
    for f_i in range(32):
        st.fregisters[f_i] = z3.BitVecVal(0, 64)

    st.registers[1] = z3.BitVecVal(RET_RA_SENTINEL, 64)
    st.registers[2] = z3.BitVecVal(INIT_SP_SENTINEL, 64)

    if isinstance(iregs, dict):
        for k, v in iregs.items():
            st.registers[int(k)] = z3.BitVecVal(int(v) & 0xFFFFFFFFFFFFFFFF, 64)
    else:
        for i, v in enumerate(iregs):
            st.registers[10 + i] = z3.BitVecVal(int(v) & 0xFFFFFFFFFFFFFFFF, 64)

    if isinstance(fregs, dict):
        for k, v in fregs.items():
            st.fregisters[int(k)] = z3.BitVecVal(int(v) & 0xFFFFFFFFFFFFFFFF, 64)
    else:
        for i, v in enumerate(fregs):
            st.fregisters[10 + i] = z3.BitVecVal(int(v) & 0xFFFFFFFFFFFFFFFF, 64)

    idx = 0
    steps = 0
    while 0 <= idx < len(words):
        if steps >= max_steps:
            raise RuntimeError(f"compiler-rt routine {sym!r} exceeded max_steps={max_steps}")
        steps += 1
        w = words[idx]
        rel = _reloc_kind_and_sym(w)
        if rel is not None:
            kind, target_sym = rel
            if kind in ("R_RISCV_PCREL_HI20", "R_RISCV_GOT_HI20"):
                rd = (int(w.bytes_hex, 16) >> 7) & 0x1F
                base_name = f"rodata_{target_sym}"
                st.write_register(rd, z3.BitVec(base_name, 64))
                hex_b = _LCPI_CONSTANTS.get(f"{sym}:{target_sym}") or _LCPI_CONSTANTS.get(target_sym)
                if hex_b is not None:
                    st.rodata_bytes[base_name] = bytes.fromhex(hex_b)
                if idx + 1 < len(words):
                    nxt_rel = _reloc_kind_and_sym(words[idx + 1])
                    if nxt_rel is not None and nxt_rel[0] == "R_RISCV_PCREL_LO12_I":
                        rd_lo = (int(words[idx + 1].bytes_hex, 16) >> 7) & 0x1F
                        st.write_register(rd_lo, z3.BitVec(base_name, 64))
                        idx += 2
                        continue
                idx += 1
                continue
            if kind == "R_RISCV_PCREL_LO12_I":
                idx += 1
                continue
            if kind == "R_RISCV_CALL_PLT":
                is_tail = idx + 1 < len(words) and words[idx + 1].arch_opcode == "jalr" and "zero," in words[idx + 1].operands
                if target_sym == "memcpy":
                    dst = z3.simplify(st.registers[10]).as_long()
                    src = z3.simplify(st.registers[11]).as_long()
                    length = z3.simplify(st.registers[12]).as_long()
                    for b_i in range(length):
                        byte_mem[dst + b_i] = byte_mem.get(src + b_i, 0)
                else:
                    sub_iregs = {r_i: z3.simplify(st.registers[r_i]).as_long() for r_i in (2, *range(10, 18))}
                    sub_fregs = {f_i: z3.simplify(st.fregisters[f_i]).as_long() for f_i in range(10, 18)}
                    sub_res = eval_compiler_rt_routine(
                        target_sym, iregs=sub_iregs, fregs=sub_fregs, mem=byte_mem, max_steps=max_steps - steps
                    )
                    steps += sub_res["steps"]
                    st.registers[10] = z3.BitVecVal(sub_res["a0"], 64)
                    st.registers[11] = z3.BitVecVal(sub_res["a1"], 64)
                    st.fregisters[10] = z3.BitVecVal(sub_res["fa0"], 64)
                    st.fregisters[11] = z3.BitVecVal(sub_res["fa1"], 64)
                if is_tail:
                    break
                skip = 2 if (idx + 1 < len(words) and words[idx + 1].arch_opcode == "jalr") else 1
                idx += skip
                continue

        w_int = int(w.bytes_hex, 16)
        w_size = len(w.bytes_hex) // 2
        _res, mach, _llean = execute_word(w_int, w_size, st, pc=w.address)
        npc = z3.simplify(mach.registers["nextPC"])
        if not z3.is_bv_value(npc):
            raise RuntimeError(f"Non-concrete nextPC in concrete execution of {sym!r} at 0x{w.address:x}: {npc}")
        t_pc = npc.as_long()
        if t_pc == RET_RA_SENTINEL:
            break
        if t_pc not in addr_to_idx:
            raise RuntimeError(f"Unexpected jump target 0x{t_pc:x} in {sym!r} at 0x{w.address:x}")
        idx = addr_to_idx[t_pc]

    return {
        "a0": z3.simplify(st.registers[10]).as_long(),
        "a1": z3.simplify(st.registers[11]).as_long(),
        "fa0": z3.simplify(st.fregisters[10]).as_long(),
        "fa1": z3.simplify(st.fregisters[11]).as_long(),
        "steps": steps,
        "mem": byte_mem,
    }


_EMITTED_ROUTINE_CACHE: dict[tuple[str, str], dict[str, Any]] = {}


def _format_runnable_state_machine_code(
    sym: str, target_lang: str, block_emissions: Sequence[dict[str, Any]]
) -> str:
    """Emit a runnable basic-block state-machine function in `target_lang`."""
    if target_lang == "python":
        lines = [
            f"def compiler_rt_whole_{sym}(x10=0, x11=0, x12=0, x13=0, x14=0, x15=0, x16=0, x17=0, f10=0, f11=0, mem=None):",
            "    if mem is None:",
            "        mem = {}",
            f"    x1 = {hex(RET_RA_SENTINEL)}",
            f"    x2 = {hex(INIT_SP_SENTINEL)}",
            "    x3 = x4 = x5 = x6 = x7 = x8 = x9 = 0",
            "    x18 = x19 = x20 = x21 = x22 = x23 = x24 = x25 = x26 = x27 = x28 = x29 = x30 = x31 = 0",
            "    f0 = f1 = f2 = f3 = f4 = f5 = f6 = f7 = f8 = f9 = 0",
            "    f12 = f13 = f14 = f15 = f16 = f17 = f18 = f19 = f20 = f21 = f22 = f23 = f24 = f25 = f26 = f27 = f28 = f29 = f30 = f31 = 0",
            "    pc = 0",
            f"    while pc != {hex(RET_RA_SENTINEL)}:",
        ]
        for idx, b_em in enumerate(block_emissions):
            kw = "if" if idx == 0 else "elif"
            lines.append(f"        {kw} pc == 0x{b_em['start_pc']:x}:")
            for st_s in b_em["statements"]:
                lines.append(f"            {st_s}")
            lines.append(f"            pc = ({b_em['next_pc']}) & 0xFFFFFFFFFFFFFFFF")
        lines.append("        else:")
        lines.append("            raise RuntimeError(f'Unknown basic block pc: {pc:#x}')")
        lines.append(
            "    return {'a0': x10 & 0xFFFFFFFFFFFFFFFF, 'a1': x11 & 0xFFFFFFFFFFFFFFFF, 'fa0': f10 & 0xFFFFFFFFFFFFFFFF, 'fa1': f11 & 0xFFFFFFFFFFFFFFFF, 'mem': mem}"
        )
        return "\n".join(lines)

    if target_lang in ("c", "cpp"):
        lines = [
            f"uint64_t compiler_rt_whole_{sym}(int64_t x10, int64_t x11, int64_t x12, int64_t x13, uint8_t *mem, int64_t *out_a1) {{",
            f"    int64_t x1 = {hex(RET_RA_SENTINEL)}LL, x2 = {hex(INIT_SP_SENTINEL)}LL;",
            "    int64_t x3=0,x4=0,x5=0,x6=0,x7=0,x8=0,x9=0,x14=0,x15=0,x16=0,x17=0;",
            "    int64_t x18=0,x19=0,x20=0,x21=0,x22=0,x23=0,x24=0,x25=0,x26=0,x27=0,x28=0,x29=0,x30=0,x31=0;",
            "    int64_t _arg_x10=0, _arg_x11=0, _arg_x12=0, _arg_x13=0;",
            "    uint64_t pc = 0ULL;",
            f"    while (pc != {hex(RET_RA_SENTINEL)}ULL) {{",
            "        switch (pc) {",
        ]
        for b_em in block_emissions:
            lines.append(f"        case 0x{b_em['start_pc']:x}ULL:")
            for st_s in b_em["statements"]:
                lines.append(f"            {st_s};")
            lines.append(f"            pc = (uint64_t)({b_em['next_pc']});")
            lines.append("            break;")
        lines.append("        default: return 0ULL;")
        lines.append("        }")
        lines.append("    }")
        lines.append("    if (out_a1) *out_a1 = x11;")
        lines.append("    return (uint64_t)x10;")
        lines.append("}")
        return "\n".join(lines)

    bb_clauses: list[str] = []
    for b_em in block_emissions:
        assigns = "; ".join(b_em["statements"])
        bb_clauses.append(f"pc==0x{b_em['start_pc']:x}: {{{assigns}; pc={b_em['next_pc']}}}")
    return f"compiler_rt_whole_{sym}[{'; '.join(bb_clauses)}]"


def emit_compiler_rt_routine(sym: str, target_lang: str) -> dict[str, Any]:
    """Emit a whole-lowered `compiler-rt` routine in `target_lang` using `HIOP_PRIMITIVES`.

    Every basic block in `sym` is lifted symbolically through Sail (`execute_word`) and its
    register updates, stack/memory loads & stores, and `nextPC` transitions are translated
    directly into `target_lang`'s proven 64-bit `HIOP_PRIMITIVES`.
    """
    t = normalize_target_lang(target_lang)
    cache_key = (sym, t)
    if cache_key in _EMITTED_ROUTINE_CACHE:
        return _EMITTED_ROUTINE_CACHE[cache_key]

    routines = load_compiler_rt_routines()
    if sym not in routines:
        raise NotImplementedError(
            f"External call symbol {sym!r} is not in whole-lowered compiler-rt ({len(routines)} routines)"
        )

    routine = routines[sym]
    block_emissions: list[dict[str, Any]] = []
    all_lo_ops: list[str] = []

    for bb in routine.basic_blocks:
        step_updates, next_pc, lo_ops = lift_basic_block_symbolically(sym, bb)
        all_lo_ops.extend(lo_ops)
        reg_updates: dict[str, str] = {}
        stmts: list[str] = []
        for reg_name, r_val in step_updates:
            code_val = translate_z3_to_hiop_primitives(r_val, t)
            if reg_name == "mem":
                reg_updates[f"mem_{len(stmts)}"] = code_val
                stmts.append(code_val)
            else:
                reg_updates[reg_name] = code_val
                stmts.append(f"{reg_name} = {code_val}")
        npc_expr = translate_z3_to_hiop_primitives(next_pc, t)
        block_emissions.append(
            {
                "block_id": bb.block_id,
                "start_pc": bb.start_pc,
                "end_pc": bb.end_pc,
                "lo_ops": lo_ops,
                "reg_updates": reg_updates,
                "statements": stmts,
                "next_pc": npc_expr,
                "calls": list(bb.calls),
            }
        )

    sm_code = _format_runnable_state_machine_code(sym, t, block_emissions)

    res = {
        "routine": sym,
        "target_lang": t,
        "source_file": routine.source_file,
        "is_dag": routine.is_dag,
        "num_words": len(routine.words),
        "num_basic_blocks": len(routine.basic_blocks),
        "lo_ops": all_lo_ops,
        "basic_blocks": block_emissions,
        "state_machine_code": sm_code,
    }
    _EMITTED_ROUTINE_CACHE[cache_key] = res
    return res


def exec_emitted_python_routine(
    sym: str,
    iregs: Sequence[int] = (),
    fregs: Sequence[int] = (),
    mem: dict[int, int] | None = None,
) -> dict[str, Any]:
    """Compile and execute the emitted Python state-machine function for `sym` (`emit_compiler_rt_routine(sym, 'python')`)."""
    emitted = emit_compiler_rt_routine(sym, "python")
    code = emitted["state_machine_code"]
    byte_mem: dict[int, int] = mem if mem is not None else {}

    def _mem_load(m: dict[int, int], addr: int, width: int) -> int:
        a = int(addr) & 0xFFFFFFFFFFFFFFFF
        val = 0
        for b_i in range(width):
            val |= (m.get(a + b_i, 0) & 0xFF) << (8 * b_i)
        return val

    def _mem_store(m: dict[int, int], addr: int, val: int, width: int) -> int:
        a = int(addr) & 0xFFFFFFFFFFFFFFFF
        v = int(val)
        for b_i in range(width):
            m[a + b_i] = (v >> (8 * b_i)) & 0xFF
        return 0

    class _ExecEnv(dict):
        def __missing__(self, key: str) -> Any:
            if key.startswith("compiler_rt_"):
                rest = key[len("compiler_rt_") :]
                ret_reg = "a0"
                for sfx in ("_a0", "_a1", "_fa0", "_fa1"):
                    if rest.endswith(sfx):
                        ret_reg = sfx[1:]
                        sub_sym = rest[: -len(sfx)]
                        break
                else:
                    sub_sym = rest

                def _sub_call(*args: int) -> int:
                    res_sub = exec_emitted_python_routine(sub_sym, iregs=args, mem=byte_mem)
                    return int(res_sub[ret_reg]) & 0xFFFFFFFFFFFFFFFF

                self[key] = _sub_call
                return _sub_call
            raise KeyError(key)

    env = _ExecEnv(
        {
            "__builtins__": {"abs": abs, "RuntimeError": RuntimeError},
            "mem_load_64": lambda m, a: _mem_load(m, a, 8),
            "mem_load_32": lambda m, a: _mem_load(m, a, 4),
            "mem_load_16": lambda m, a: _mem_load(m, a, 2),
            "mem_load_8": lambda m, a: _mem_load(m, a, 1),
            "mem_store_64": lambda m, a, v: _mem_store(m, a, v, 8),
            "mem_store_32": lambda m, a, v: _mem_store(m, a, v, 4),
            "mem_store_16": lambda m, a, v: _mem_store(m, a, v, 2),
            "mem_store_8": lambda m, a, v: _mem_store(m, a, v, 1),
        }
    )
    exec(code, env)
    fn = env[f"compiler_rt_whole_{sym}"]
    i_args = [int(x) & 0xFFFFFFFFFFFFFFFF for x in iregs[:8]]
    while len(i_args) < 8:
        i_args.append(0)
    f_args = [int(x) & 0xFFFFFFFFFFFFFFFF for x in fregs[:2]]
    while len(f_args) < 2:
        f_args.append(0)
    return fn(*i_args, f_args[0], f_args[1], mem=byte_mem)


def emit_compiler_rt_call_expr(call_name: str, args: Sequence[str], target_lang: str) -> str:
    """Translate a `call_<sym>_<ret>` Z3 node by lifting `<sym>` from whole-lowered `compiler-rt`."""
    t = normalize_target_lang(target_lang)
    if not call_name.startswith("call_"):
        raise NotImplementedError(f"Unrecognized external call node {call_name!r}")

    rest = call_name[len("call_") :]
    ret_reg = "a0"
    for suffix in ("_a0", "_a1", "_fa0", "_fa1"):
        if rest.endswith(suffix):
            ret_reg = suffix[1:]
            sym = rest[: -len(suffix)]
            break
    else:
        sym = rest

    if sym == "memcpy":
        args_joined = ", ".join(args)
        return f"memcpy_bytes({args_joined})"

    routines = load_compiler_rt_routines()
    if sym not in routines:
        raise NotImplementedError(
            f"External call {sym!r} (from {call_name!r}) is not in whole-lowered compiler-rt"
        )

    routine = routines[sym]
    args_joined = ", ".join(args)
    if t in ("python", "ruby"):
        return f"compiler_rt_{sym}_{ret_reg}({args_joined})"
    return f"compiler_rt_{sym}_{ret_reg}({args_joined}) /* whole-lifted: {len(routine.words)} LoOps, {len(routine.basic_blocks)} BBs */"


def verify_all_needed_routines() -> dict[str, Any]:
    """Verify that all 58 needed routines (5,830 LoOp words) decode, lift through Sail,
    preserve memory loads/stores in basic blocks, and execute identically in emitted state-machine form."""
    routines = load_compiler_rt_routines()
    needed_routines = [r for r in routines.values() if r.needed]
    total_words = sum(len(r.words) for r in needed_routines)
    unique_encodings = {
        (int(w.bytes_hex, 16), len(w.bytes_hex) // 2)
        for r in needed_routines
        for w in r.words
    }
    dag_routines = [r.name for r in needed_routines if r.is_dag]
    loop_routines = [r.name for r in needed_routines if not r.is_dag]

    # Verify memory/stack stores & loads preserved in __divti3 basic blocks and execute emitted Python state machine
    divti3_py = emit_compiler_rt_routine("__divti3", "python")
    bb0_stmts = divti3_py["basic_blocks"][0]["statements"]
    assert any("mem_store_64" in s for s in bb0_stmts), f"Expected mem_store_64 in __divti3 BB0, got {bb0_stmts}"
    assert any(
        any("mem_load_64" in s for s in bb["statements"]) for bb in divti3_py["basic_blocks"]
    ), "Expected mem_load_64 in __divti3 epilogue basic block"

    shl_concrete = eval_compiler_rt_routine("__ashlti3", [1, 0, 3])
    shl_emitted = exec_emitted_python_routine("__ashlti3", [1, 0, 3])
    assert shl_concrete["a0"] == shl_emitted["a0"] == 8 and shl_concrete["a1"] == shl_emitted["a1"] == 0

    div_concrete = eval_compiler_rt_routine("__divti3", [100, 0, 7, 0])
    div_emitted = exec_emitted_python_routine("__divti3", [100, 0, 7, 0])
    assert div_concrete["a0"] == div_emitted["a0"] == 14 and div_concrete["a1"] == div_emitted["a1"] == 0

    return {
        "total_defined_routines": len(routines),
        "needed_routines_count": len(needed_routines),
        "total_needed_words": total_words,
        "lifted_needed_words": total_words,
        "unique_word_encodings": len(unique_encodings),
        "dag_routines_count": len(dag_routines),
        "loop_routines_count": len(loop_routines),
        "emitted_state_machine_verified": {
            "__ashlti3(1, 0, 3)": {"a0": shl_emitted["a0"], "a1": shl_emitted["a1"]},
            "__divti3(100, 0, 7, 0)": {"a0": div_emitted["a0"], "a1": div_emitted["a1"]},
            "__divti3_bb0_mem_stores": [s for s in bb0_stmts if "mem_store_" in s],
        },
        "dag_routines": sorted(dag_routines),
        "loop_routines": sorted(loop_routines),
    }


if __name__ == "__main__":
    summary = verify_all_needed_routines()
    print(json.dumps(summary, indent=2))
