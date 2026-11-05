"""extract_unit_from_LoHiOp -- the Unit cut out of the LoHiOp: the words the
debug table files under the HiOp's own line, without the copy of `p`.

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_3_extract_unit_from_LoHiOp/`.

    unit = extract_unit(LoHiOp, HiOp_line)   # the words under the HiOp's line, in order

What a Unit is, the owner, 2026-10-12 (PCHQ log 440): the HiOp's holders' fetches,
its operation and its result's store; the frame and the copy of `p` are cut.
How its words are told, the owner, 2026-10-13 (log 446): "we need some way to tell
which arch-opcodes belong to the lowered HiOp". The standard-form writes the HiOp
on a line of its own (standard_HiOp_wrapper.HiOp_on_its_own_line), lower_HiOp reads
each word's source line from the debug table, and the frame's words are filed
under the function's first line and its closing brace. So the cut is by line,
and nothing here has to know what a frame is.

`p` is the standard function's one parameter, the address of the struct whose
fields are the HiOp's holders:

    void op_1970(struct P_1970 *p) {
    	p->result = p->a + p->b;
    }

With the optimizer off, clang stores `p` into the frame when it arrives
(riscv64 `sd a0, -0x18(s0)`, under the function's first line, so cut with the
frame) and loads it back from there before it reads a holder
(`ld a1, -0x18(s0)`). The debug table files that load under the HiOp's line,
so the line alone kept it in the Unit until 2026-10-13 (logs 450, 451). Each
such load is now taken out of the Unit's words and kept, at its place, in
`holds_p`: from `words[position]` on, `register` holds `p`. Log 440: the
register that holds `p` "is read from the cut copy, not modelled". It is kept
at its place, not only at the start, because a Unit can reuse that register
and load `p` again (`a++`, log 451 Table 2).

A HiOp with parts keeps its parts' calls: each is one call named by its
relocation (`part_<key>_<role>`, log 406), and the Unit lists the parts it
calls, which map_unit_to_lean takes as named unknowns.

Written 2026-10-13 (PCHQ log 449); the copy of `p` cut 2026-10-13 (log 453).
"""
from typing import NamedTuple, Optional

# `R_RISCV_CALL_PLT part_17_b`: the relocation that names a part's call.
PART_PREFIX = "part_"
# By machine: the register `p` arrives in, the arch-opcodes that store it
# into the frame, and those that load it back. riscv64 is lower_HiOp's own
# target; x86-64 and aarch64 are the all-three-architectures check (log 397).
ARRIVAL = {
    "riscv64": ("a0", ("sd", "c.sdsp"), ("ld", "c.ldsp")),
    "x86_64": ("%rdi", ("movq",), ("movq",)),
    "aarch64": ("x0", ("str", "stur"), ("ldr", "ldur")),
}


class Unit(NamedTuple):
    """The HiOp's own words, in order; the parts they call; and where, among
    those words, each register starts to hold `p`."""

    symbol: str
    words: tuple
    parts: tuple
    holds_p: tuple
    refusal: Optional[str]


BEGIN_MARKER = "__hiop_unit_begin"
END_MARKER = "__hiop_unit_end"
UNCOND_JUMPS = ("c.j", "j", "jmp", "b")


def _has_marker(word, marker_name: str) -> bool:
    for rel in word.relocations:
        if target_of(rel) == marker_name:
            return True
    return False


def _find_marker_index(words: tuple, marker_name: str, start: int = 0) -> Optional[int]:
    for idx in range(start, len(words)):
        if _has_marker(words[idx], marker_name):
            return idx
    return None


def words_between_markers(words: tuple, HiOp_line: Optional[int], machine: str) -> tuple:
    """Slice the words between `__hiop_unit_begin` and `__hiop_unit_end` when
    hijack boundary markers are present; fall back to `words_on_line` otherwise."""
    begin_idx = _find_marker_index(words, BEGIN_MARKER, 0)
    if begin_idx is None:
        if HiOp_line is None:
            return ()
        return words_on_line(words, HiOp_line)
    start_idx = begin_idx + 1
    if machine == "riscv64" and start_idx < len(words) and words[start_idx].arch_opcode == "jalr":
        start_idx += 1
    end_idx = _find_marker_index(words, END_MARKER, start_idx)
    if end_idx is not None:
        return words[start_idx:end_idx]
    if HiOp_line is not None:
        sliced = tuple(w for w in words[start_idx:] if w.line == HiOp_line)
    else:
        sliced = words[start_idx:]
    if (
        len(sliced) == 2
        and all(w.arch_opcode in UNCOND_JUMPS and not w.relocations for w in sliced)
    ):
        return (sliced[0],)
    return sliced


def extract_unit(LoHiOp, HiOp_line: Optional[int] = None, machine: str = "riscv64"):
    """The words of the LoHiOp between `__hiop_unit_begin` and `__hiop_unit_end`
    (or under `HiOp_line`), without the loads of `p`."""
    machine = machine.replace("-", "_")
    if LoHiOp.refusal is not None:
        refused = Unit(LoHiOp.symbol, (), (), (), LoHiOp.refusal)
        return refused
    begin_idx = _find_marker_index(LoHiOp.words, BEGIN_MARKER, 0)
    if begin_idx is None and HiOp_line is None:
        missing = Unit(LoHiOp.symbol, (), (), (), "no HiOp line or hijack marker given")
        return missing
    sliced = words_between_markers(LoHiOp.words, HiOp_line, machine)
    slot, entry_reg = prologue_p_state(LoHiOp.words, HiOp_line, machine, begin_idx=begin_idx)
    words, holds_p = without_the_copy_of_p(sliced, slot, machine)
    if begin_idx is None and words and not any(pos == 0 for pos, _ in holds_p) and entry_reg is not None:
        holds_p = ((0, entry_reg),) + holds_p
    parts = parts_called(words)
    unit = Unit(LoHiOp.symbol, words, parts, holds_p, None)
    return unit


def words_on_line(words: tuple, line: int) -> tuple:
    first_idx = None
    epilogue_idx = None
    for i, word in enumerate(words):
        if word.line == line and first_idx is None:
            first_idx = i
        elif first_idx is not None and word.line is not None and word.line > line and epilogue_idx is None:
            epilogue_idx = i
    if first_idx is None:
        return ()
    kept = []
    for i, word in enumerate(words):
        if word.line == line:
            kept.append(word)
        elif first_idx < i and (epilogue_idx is None or i < epilogue_idx):
            kept.append(word)
    on_line = tuple(kept)
    return on_line


def prologue_p_state(
    words: tuple, HiOp_line: Optional[int], machine: str, begin_idx: Optional[int] = None
) -> tuple[Optional[str], Optional[str]]:
    """Return `(slot, entry_reg)` by tracking `p` from arrival register through
    prologue register moves (`mv`/`c.mv`) and stack frame stores."""
    register, stores, loads = ARRIVAL[machine]
    limit = begin_idx if begin_idx is not None else len(words)
    p_regs = {register}
    last_p_reg: Optional[str] = register
    last_slot: Optional[str] = None
    for word in words[:limit]:
        if begin_idx is None and HiOp_line is not None and word.line == HiOp_line:
            break
        if word.arch_opcode in ("mv", "c.mv"):
            dst, _, src = word.operands.partition(", ")
            dst, src = dst.strip(), src.strip()
            if src in p_regs:
                p_regs.add(dst)
                last_p_reg = dst
            else:
                p_regs.discard(dst)
            continue
        matched_store = False
        for r in list(p_regs):
            s = stored_slot(word, r, stores, machine)
            if s is not None:
                last_slot = s
                last_p_reg = r
                matched_store = True
                break
        if matched_store:
            continue
        if word.arch_opcode in loads:
            loaded = loaded_register(word, last_slot, machine)
            if loaded is not None:
                p_regs.add(loaded)
                last_p_reg = loaded
            else:
                dst, _ = register_and_memory(word.operands, machine, True)
                p_regs.discard(dst.strip())
    entry_reg = last_p_reg if last_p_reg in p_regs else (sorted(p_regs)[0] if p_regs else last_p_reg)
    return last_slot, entry_reg


def slot_of_p(words: tuple, HiOp_line: Optional[int], machine: str, begin_idx: Optional[int] = None) -> Optional[str]:
    """Where the frame stores `p` when it arrives."""
    slot, _ = prologue_p_state(words, HiOp_line, machine, begin_idx=begin_idx)
    return slot


def stored_slot(word, register: str, stores: tuple, machine: str) -> Optional[str]:
    """The memory a store of `register` writes, or None for any other word."""
    if word.arch_opcode not in stores:
        return None
    source, memory = register_and_memory(word.operands, machine, False)
    if source != register:
        return None
    return memory


def loaded_register(word, slot: Optional[str], machine: str) -> Optional[str]:
    """The register a load from `p`'s slot writes, or None for any other
    word."""
    register, stores, loads = ARRIVAL[machine]
    if slot is None or word.arch_opcode not in loads:
        return None
    target, memory = register_and_memory(word.operands, machine, True)
    if memory != slot:
        return None
    return target


def register_and_memory(operands: str, machine: str, loading: bool) -> tuple:
    """(register, memory) from a store's or a load's operands. riscv64 and
    aarch64 write the register first (`a1, -0x18(s0)`, `x8, [sp, #0x8]`);
    x86-64 writes the source first, so a load's memory comes first
    (`-0x8(%rbp), %rax`)."""
    first, _, rest = operands.partition(", ")
    if machine == "x86_64" and loading:
        pair = (rest, first)
        return pair
    pair = (first, rest)
    return pair


def without_the_copy_of_p(words: tuple, slot: Optional[str], machine: str) -> tuple:
    """The words with each load of `p` taken out, and, for each one taken
    out, (the place it stood among the words kept, the register it loaded)."""
    kept = []
    holds_p = []
    for word in words:
        loaded = loaded_register(word, slot, machine)
        if loaded is None:
            kept.append(word)
            continue
        holds_p.append((len(kept), loaded))
    cut = (tuple(kept), tuple(holds_p))
    return cut


def parts_called(words: tuple) -> tuple:
    """The parts the words call, each named once, in the order called."""
    parts = []
    for word in words:
        for relocation in word.relocations:
            target = target_of(relocation)
            if target.startswith(PART_PREFIX) and target not in parts:
                parts.append(target)
    called = tuple(parts)
    return called


def target_of(relocation: str) -> str:
    """`R_RISCV_CALL_PLT part_17_b` -> `part_17_b`; x86-64 writes the call's
    addend after the name, `R_X86_64_PLT32 part_17_b-0x4`, which is dropped."""
    target = relocation.split()[-1]
    target = target.split("-")[0]
    target = target.split("+")[0]
    return target
