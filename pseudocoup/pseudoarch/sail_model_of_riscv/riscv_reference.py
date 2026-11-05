#!/usr/bin/env python3
"""riscv_reference.py -- THE ONE SYMBOLIC SIMULATOR OF THE RISC-V MACHINE.

TASK sl1 (2026-09-14): THE TABLE IS GENERATED.  Sections 4, 4b and 5 of
this file -- the builders a person typed from Sail's text, the compressed
expansions, and the opcode table -- are gone.  `step` now hands each line
to `sail_lifter/lifter.py`: the image's assembler turns the text into its
word, the Sail model's own decoder (`encdec_backwards`, as the sail
compiler's Lean backend emitted it) turns the word into the model's own
instruction value, and the model's own `execute` (emitted the same way,
read by `sail_lifter/lean_reader.py`) applies it to this file's
MachineState.  Nothing below names an instruction.  The transcription this
replaced is kept beside it for the record, unread by anything:
`sail_lifter/riscv_reference_transcription_2026-09-13.py.txt`.  The family
constants that other files import (R_TYPE, LOAD, ...) are kept as EMPTY
containers so those imports still resolve; they describe nothing now.


WHAT THIS FILE IS, one sentence, in relation: the riscv64 symbolic simulator -- one z3
term per place an instruction writes, read off the instruction's own
disassembled text, so a carved riscv64 body can be walked into a term the
same way an x86 body is.

IT IS BUILT IN reference.py's OWN SHAPE, section for section, so the two
can be read side by side and so section 5 of the brief can count what had
to be written again:

    section 1  the widths, the sorts, and the register tables
    section 2  MachineState -- the sub-node
    section 3  the operand reader -- one place, used by every builder
    section 4  the term builders -- one per family, no second table
    section 5  opcode_table -- THE ONE TABLE
    section 6  RiscvReference -- the node's own class

THE FOUR THINGS THAT ARE NOT IN THE x86 FILE, each a fact of the
architecture and not a choice of ours:

  * THERE IS NO FLAGS REGISTER.  Nothing here writes one, nothing reads
    one, and `MachineState` has no `flags` attribute.  x86 spends
    `build_flag_only`, `carry_bit`, `overflow_bit`, `predicate_of`,
    `condition_table.py` and the whole `set`/`cmov`/`j` suffix family on
    the flags; RISC-V spends `slt`/`sltu` (a comparison writes a general
    register a 0 or a 1) and the six branches (a comparison is read
    inside the branch itself).

  * EVERY REGISTER WRITE IS THE FULL 64 BITS.  x86's `full64` /
    `place_bits` / `KEEPS_THE_UPPER_BITS` rule -- a 32-bit write
    zero-extends, an 8- or 16-bit write keeps the register's other bits --
    has no counterpart: the architecture has no sub-register names.  The
    32-bit forms (`addw`, `srliw`, `mulw` ...) compute at 32 bits and
    SIGN-EXTEND the result into the whole register, which is one rule
    written once here (`sign_extend_w`).

  * REGISTER x0 IS THE CONSTANT ZERO.  It reads zero and a write to it is
    discarded.  That is what makes the assembler's reading aids (`li`,
    `mv`, `ret`, `nop`, `seqz`) expressible with no new instructions, and
    it is why this file is walked over `llvm-objdump -M no-aliases` text:
    the aids are spellings, and a spelling is not machine form.

  * DIVISION DOES NOT TRAP.  x86's `idiv` raises on a zero divisor and on
    the MIN / -1 overflow, and the corpus's units carry a guard around it.
    RISC-V defines both: `div` by zero is all ones, `rem` by zero is the
    dividend, `divu` by zero is 2^64-1, `remu` by zero is the dividend,
    and `div`(MIN, -1) is MIN with `rem` 0.  The reference states them and
    the Sail model checks them.

THE HONEST LIMITS, named rather than hidden.

  * `simulate` walks the body in TEXT ORDER, exactly as the x86 reference
    does.  A conditional branch is recorded as a guard row and its
    condition is kept; no branch-merging walk is coded here, because the
    ten bodies of this task's handful have none.
  * `auipc` reads the program counter.  Its term carries a `pc` symbol,
    and the point check of section 3(b) cannot present a program counter
    as an input, so `auipc` is REFUSED BY NAME there rather than counted
    as agreeing.
  * The floating-point family here is exactly the instructions the ten
    carved bodies spell -- the same rule the x86 table follows ("no entry
    is invented for an opcode no body contains").  The vector extension is
    absent.
  * A floating-point instruction carries a ROUNDING MODE operand, which
    `llvm-objdump` prints as a trailing `dyn` when the instruction defers
    to the `fcsr` register.  This file reads round-to-nearest-even for
    every rounding, which is what `fcsr` holds at reset and what the ten
    bodies run under; a body that writes `fcsr` first is not modelled and
    none of the ten does.
  * ONE INSTRUCTION OUTSIDE RV64I+M IS IN THE TABLE, and it is here
    because a carved body spells it: `czero.eqz` of the Zicond extension,
    which clang 21 emits for the select the handful's `cmovne` row
    carries.  It is marked as an extension on its own entry.

THE SPELLING BAN, pasted verbatim as required:

"THE SPELLING BAN, ABSOLUTE (the owner, restated in anger 2026-08-25 after a
second violation).  No operator token may appear in ANY key, grouping,
pairing, row structure, candidate selection, or comparison scope, anywhere
in this line -- not in matching, not in "which pairs get compared", not in
report rows, not in dropdowns.  The candidate set for comparison comes from
machine-form evidence (clusters, connections, type pairs) or from ratified
intention -- never from the token.  The token appears exactly once per
unit: as a display label on the member.  HISTORY OF VIOLATIONS, so the
pattern is visible: (1) the arch campaign's cross-language matrix (caught
by the owner 2026-08-24); (2) verdicts.py's row pairing (caught by the owner
2026-08-25 -- the fix brief itself reintroduced it as "same-operator
pairs").  MECHANICAL GUARD REQUIRED: every pipeline stage that groups or
pairs units must run the spelling-key check
(op_pipeline/check_no_spelling_keys.py) and refuse its own output on
failure.  A brief handed to any subagent for this line MUST paste this
paragraph verbatim."

No operator token appears in this file.  The table is keyed by ARCH
MNEMONIC, which is machine-form evidence read off the disassembled body,
never by the source spelling a probe was generated from.

Coding discipline (the owner's ruling): no complex/compound one-liner statements.

usage:
  riscv_reference.py (library; `sail_points.py` and `claim_check.py` are
  this task's drivers)
"""

import re

import z3


class NotModeled(Exception):
    """the reference refuses this instruction by name, and says why."""


class LeavesTheUnit(Exception):
    """this line transfers OUT of the unit."""

    def __init__(self, line, target):
        Exception.__init__(self, "%s -> %s" % (line, target))
        self.line = line
        self.target = target


# ------------------------------------------------------------------
# section 1: the widths, the sorts, and the register tables
# ------------------------------------------------------------------

XLEN = 64

FLOAT_SORT = {32: z3.Float32(), 64: z3.Float64()}

ROUNDING = z3.RNE()

# The integer register file, by the ABI names `llvm-objdump` prints.  The
# value is the ARCHITECTURAL index, which is the machine-form key: two ABI
# names for one index (`s0` and `fp`) are one register.
INTEGER_REGISTERS = {
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
    "t0": 5, "t1": 6, "t2": 7,
    "s0": 8, "fp": 8, "s1": 9,
    "a0": 10, "a1": 11, "a2": 12, "a3": 13,
    "a4": 14, "a5": 15, "a6": 16, "a7": 17,
    "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "s8": 24, "s9": 25, "s10": 26, "s11": 27,
    "t3": 28, "t4": 29, "t5": 30, "t6": 31,
}
for _i in range(32):
    INTEGER_REGISTERS["x%d" % _i] = _i

FLOAT_REGISTERS = {}
for _i in range(8):
    FLOAT_REGISTERS["ft%d" % _i] = _i
for _i in range(2):
    FLOAT_REGISTERS["fs%d" % _i] = 8 + _i
for _i in range(8):
    FLOAT_REGISTERS["fa%d" % _i] = 10 + _i
for _i in range(10):
    FLOAT_REGISTERS["fs%d" % (_i + 2)] = 18 + _i
for _i in range(4):
    FLOAT_REGISTERS["ft%d" % (_i + 8)] = 28 + _i
for _i in range(32):
    FLOAT_REGISTERS["f%d" % _i] = _i

ZERO_REGISTER = 0

# THE ARGUMENT AND ANSWER PLACES OF THE psABI (`lp64d`), stated once and
# read by the walk, never guessed per unit.
INTEGER_ARGUMENTS = [10, 11, 12, 13, 14, 15, 16, 17]     # a0 .. a7
INTEGER_ANSWER = 10                                      # a0
FLOAT_ARGUMENTS = [10, 11, 12, 13, 14, 15, 16, 17]       # fa0 .. fa7
FLOAT_ANSWER = 10                                        # fa0


def sign_extend_w(value32):
    """THE 32-BIT FORMS' OWN WRITE RULE: compute at 32 bits, then place the
    sign-extension of that result in the whole 64-bit register.  This is
    the whole of what x86 spends `full64` and `place_bits` on."""
    return z3.SignExt(32, value32)


def bits_of(value, width):
    if value.size() == width:
        return value
    if value.size() > width:
        return z3.Extract(width - 1, 0, value)
    return z3.ZeroExt(width - value.size(), value)


def as_float(bits, width):
    return z3.fpBVToFP(bits_of(bits, width), FLOAT_SORT[width])


def from_float(value):
    return z3.fpToIEEEBV(value)


def nan_box(bits32):
    """a 32-bit float value held in a 64-bit float register is NaN-boxed:
    the upper 32 bits are all ones (the RISC-V ISA manual, `Zfinx`-free
    F-in-D rule)."""
    return z3.Concat(z3.BitVecVal((1 << 32) - 1, 32), bits32)


def memory_symbol_name(text):
    """`0x8(sp)` names the cell `MEM_0x8_sp_`, the same mangling
    `reference.memory_symbol_name` does for x86, so a memory operand is one
    fixed unknown per literal text."""
    out = re.sub(r"[^0-9A-Za-z]", "_", text)
    return "MEM_%s" % out


# ------------------------------------------------------------------
# section 2: MachineState -- the sub-node
# ------------------------------------------------------------------

class MachineState(object):
    """the symbolic machine the reference walks a body over.

      registers  -- architectural index -> 64-bit term, seeded as
                    `seed_x<i>` free symbols, so a proof is about every
                    input at once.  Index 0 always reads zero.
      fregisters -- architectural index -> the 64-bit RAW BITS of the
                    floating-point register, seeded as `seed_f<i>`.
      memory     -- literal operand text -> 64-bit term; an unwritten cell
                    reads one fixed unknown named `seed_MEM_<mangled>`.
      pc         -- one symbol; only `auipc` and the transfers read it.

    THERE IS NO FLAGS ATTRIBUTE.  The architecture has no flags register,
    so there is nothing to hold.
    """

    def __init__(self, shared_seed=None):
        if shared_seed is None:
            shared_seed = {}
        self.shared_seed = shared_seed
        self.registers = {}
        self.fregisters = {}
        self.memory = {}
        self.refusals = []
        self.guard_rows = []
        self.branch_condition = None
        self.path_condition = z3.BoolVal(True)

    # -- integer registers -------------------------------------------

    def seed(self, index):
        name = "seed_x%d" % index
        if name not in self.shared_seed:
            self.shared_seed[name] = z3.BitVec(name, XLEN)
        return self.shared_seed[name]

    def bind(self, index, term):
        """pre-bind a register to somebody else's symbol -- the arrival
        contract's job."""
        self.registers[index] = term

    def read_register(self, index):
        if index == ZERO_REGISTER:
            return z3.BitVecVal(0, XLEN)
        if index in self.registers:
            return self.registers[index]
        value = self.seed(index)
        self.registers[index] = value
        return value

    def write_register(self, index, term):
        """EVERY WRITE IS THE FULL 64 BITS, and a write to x0 is
        discarded."""
        if index == ZERO_REGISTER:
            return
        self.registers[index] = bits_of(term, XLEN)

    # -- floating-point registers ------------------------------------

    def seed_float(self, index):
        name = "seed_f%d" % index
        if name not in self.shared_seed:
            self.shared_seed[name] = z3.BitVec(name, XLEN)
        return self.shared_seed[name]

    def read_float(self, index):
        if index in self.fregisters:
            return self.fregisters[index]
        value = self.seed_float(index)
        self.fregisters[index] = value
        return value

    def write_float(self, index, term):
        self.fregisters[index] = bits_of(term, XLEN)

    # -- memory -------------------------------------------------------

    def memory_cell(self, text):
        if text in self.memory:
            return self.memory[text]
        name = memory_symbol_name(text)
        if name not in self.shared_seed:
            self.shared_seed[name] = z3.BitVec("seed_%s" % name, XLEN)
        cell = self.shared_seed[name]
        self.memory[text] = cell
        return cell

    def set_memory_cell(self, text, term):
        self.memory[text] = bits_of(term, XLEN)

    # -- the program counter -----------------------------------------

    def program_counter(self):
        if "pc" not in self.shared_seed:
            self.shared_seed["pc"] = z3.BitVec("pc", XLEN)
        return self.shared_seed["pc"]


# ------------------------------------------------------------------
# section 3: the operand reader -- one place, used by every builder
# ------------------------------------------------------------------

IMMEDIATE_RE = re.compile(r"^-?(?:0x[0-9a-fA-F]+|\d+)$")
MEMORY_RE = re.compile(r"^(-?(?:0x[0-9a-fA-F]+|\d+))\(([a-z0-9]+)\)$")


def split_operands(rest):
    """split an operand list on top-level commas only."""
    out = []
    depth = 0
    current = ""
    for char in rest:
        if char == "(":
            depth = depth + 1
            current = current + char
            continue
        if char == ")":
            depth = depth - 1
            current = current + char
            continue
        if char == "," and depth == 0:
            out.append(current)
            current = ""
            continue
        current = current + char
    if current:
        out.append(current)
    return [item.strip() for item in out]


class Operands(object):
    """the resolved operand slots of one body line, in the disassembler's
    own order (RISC-V: destination first, then the sources).  Every builder
    in the table reads its inputs through this object and through nothing
    else."""

    def __init__(self, state, mnemonic, texts):
        self.state = state
        self.mnemonic = mnemonic
        self.texts = texts

    # -- classification ----------------------------------------------

    def is_immediate(self, text):
        return IMMEDIATE_RE.match(text) is not None

    def is_integer_register(self, text):
        return text in INTEGER_REGISTERS

    def is_float_register(self, text):
        return text in FLOAT_REGISTERS

    def is_memory(self, text):
        return MEMORY_RE.match(text) is not None

    # -- reading ------------------------------------------------------

    def immediate_value(self, text):
        negative = text.startswith("-")
        body = text[1:] if negative else text
        if body.startswith("0x"):
            value = int(body, 16)
        else:
            value = int(body, 10)
        if negative:
            value = -value
        return value

    def immediate(self, index):
        text = self.texts[index]
        if not self.is_immediate(text):
            raise NotModeled(
                "operand %r of %r is not an immediate"
                % (text, self.mnemonic))
        return z3.BitVecVal(self.immediate_value(text) % (1 << XLEN), XLEN)

    def register_index(self, index):
        text = self.texts[index]
        if text not in INTEGER_REGISTERS:
            raise NotModeled(
                "register spelling %r is not an integer register of this "
                "architecture" % text)
        return INTEGER_REGISTERS[text]

    def float_index(self, index):
        text = self.texts[index]
        if text not in FLOAT_REGISTERS:
            raise NotModeled(
                "register spelling %r is not a floating-point register of "
                "this architecture" % text)
        return FLOAT_REGISTERS[text]

    def read(self, index):
        return self.state.read_register(self.register_index(index))

    def read_float(self, index):
        return self.state.read_float(self.float_index(index))

    def write(self, index, term):
        self.state.write_register(self.register_index(index), term)

    def write_float(self, index, term):
        self.state.write_float(self.float_index(index), term)

    def memory_parts(self, index):
        text = self.texts[index]
        hit = MEMORY_RE.match(text)
        if hit is None:
            raise NotModeled(
                "operand %r of %r is not an offset-and-base memory "
                "operand" % (text, self.mnemonic))
        return hit.group(1), hit.group(2)


# ------------------------------------------------------------------
# section 4: the definitions -- GENERATED from the Sail model (task sl1)
# ------------------------------------------------------------------
#
# There is no builder here.  The meaning of every instruction is the Sail
# model's own `execute` clause, as the sail compiler's Lean backend wrote
# it, read by `sail_lifter/lean_reader.py`; the decoding of a word is the
# model's own `encdec` mapping, the same way.  `sail_lifter/lifter.py`
# holds the bridge.  Below, the names the older drivers import are kept
# as empty containers: they described the typed table and describe
# nothing now.

import os as _os
import sys as _sys

_SAIL_LIFTER = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                             "sail_lifter")
if _SAIL_LIFTER not in _sys.path:
    _sys.path.insert(0, _SAIL_LIFTER)

import lifter as GENERATED                                   # noqa: E402

R_TYPE = frozenset()
R_TYPE_W = frozenset()
I_TYPE = frozenset()
SHIFT_I = frozenset()
I_TYPE_W = frozenset()
SHIFT_I_W = frozenset()
UPPER = frozenset()
MULTIPLY = frozenset()
MULTIPLY_W = frozenset()
DIVIDE = frozenset()
CONDITIONAL_ZERO = frozenset()
DIVIDE_W = frozenset()
ADD_UNSIGNED_WORD = frozenset()
BIT_SET_I = frozenset()
FLOAT_SIGN_INJECT = {}
LOAD = {}
STORE = {}
BRANCH = frozenset()
JUMP = frozenset()
NO_OPERATION = frozenset()
TRAP = frozenset()
FLOAT_BINARY = {}
FLOAT_FROM_INTEGER = {}
FLOAT_WIDEN = {}
FLOAT_MOVE = {}
FLOAT_COMPARE = {}
FLOAT_LOAD = {}
FLOAT_STORE = {}
COMPRESSED = {}


def expand_compressed(mnemonic, texts):
    """RETIRED: the model decodes a compressed word itself.  Nothing."""
    return None


# ------------------------------------------------------------------
# section 5: opcode_table -- kept as an empty frame for the drivers that
# import it; the definitions live in the generated emit
# ------------------------------------------------------------------

NAMED = "the operands the instruction names"
DESTINATION = "the first named operand"
MEMORY = "memory"
THE_BRANCH_CONDITION = "the branch condition the walk forks on"
THE_PROGRAM_COUNTER = "the program counter"

TRAP_CAUSE = "a trap, and this reference walks a body in text order"


class Entry(object):
    """one arch instruction's meaning: kept for the drivers' imports."""

    def __init__(self, mnemonic, reads, writes, build, cause=None):
        self.mnemonic = mnemonic
        self.reads = tuple(reads)
        self.writes = tuple(writes)
        self.build = build
        self.cause = cause

    def __repr__(self):
        return "Entry(%r, reads=%r, writes=%r, modelled=%r)" % (
            self.mnemonic, self.reads, self.writes, self.build is not None)


class OpcodeTable(object):
    """the frame the drivers import; EMPTY, because the table is
    generated (see section 4)."""

    def __init__(self):
        self.entries = {}

    def entry_for(self, mnemonic):
        return None

    def builder_for(self, mnemonic):
        return None

    def without_a_builder(self):
        return []


# ------------------------------------------------------------------
# section 6: RiscvReference -- the node's own class (the walk, unchanged)
# ------------------------------------------------------------------

RETURN_LINES = frozenset(["jalr zero, 0x0(ra)", "c.jr ra", "ret"])

RETIRED = "Retire_Success"


class RiscvReference(object):
    """THE one symbolic simulator of the RISC-V machine."""

    def __init__(self):
        self.opcode_table = OpcodeTable()

    @property
    def lifter(self):
        return GENERATED.shared_lifter()

    # -- the node's methods -------------------------------------------

    def simulate(self, body_text, arrival_contract=None,
                 shared_seed=None):
        """(body_text, arrival_contract) -> MachineState after the body."""
        state = MachineState(shared_seed)
        if arrival_contract:
            self.apply_arrival_contract(state, arrival_contract)
        self.walk_body(state, self.body_lines(body_text))
        return state

    def walk_body(self, state, lines):
        for line in lines:
            if line in RETURN_LINES:
                break
            self.step(state, line)
        return state

    def step(self, state, line):
        """one line: its word by the assembler, its instruction by the
        model's decoder, its effect by the model's execute."""
        text = self.split_line(line)
        del text
        lifter = self.lifter
        try:
            words = lifter.words_of_lines([self.clean_line(line)])
            word, size = words[0]
            instr = lifter.decode(word, size)
            seed_pc = state.program_counter()
            result, machine = self.execute_at(lifter, instr, state,
                                              seed_pc, size)
        except GENERATED.LiftRefused as problem:
            raise NotModeled("%s (line %r)" % (problem, line))
        self.record(state, line, result, machine)

    def execute_at(self, lifter, instr, state, seed_pc, size):
        """the model's own step order: PC is the walk's symbol, nextPC is
        PC plus the word's size (`Step.lean`), then execute."""
        lifter.reset_registers["PC"] = seed_pc
        lifter.reset_registers["nextPC"] = seed_pc + z3.BitVecVal(size, XLEN)
        return lifter.execute(instr, state)

    def record(self, state, line, result, machine):
        """what the walk keeps of one executed instruction: a branch's
        condition (the top conditional of the nextPC the model wrote), and
        a result that is not a retirement leaves the unit."""
        written = dict(machine.registers)
        next_pc = written.get("nextPC")
        if next_pc is not None and z3.is_bv(next_pc):
            simplified = z3.simplify(next_pc)
            if z3.is_app_of(simplified, z3.Z3_OP_ITE):
                state.branch_condition = simplified.arg(0)
        name = GENERATED.constructor_name(result)
        if name not in (RETIRED, "ite"):
            raise LeavesTheUnit(line, name)

    def clean_line(self, line):
        text = line.strip()
        text = re.sub(r"\s*<[^>]*>\s*$", "", text)
        return text

    def split_line(self, line):
        """`add a0, a1, a2` -> ('add', ['a0', 'a1', 'a2']).

        `llvm-objdump` appends a symbolic target to a transfer -- `jal ra,
        0x38 <op_1>` -- and that trailing `<...>` is the reader's aid, not
        an operand."""
        text = line.strip()
        text = re.sub(r"\s*<[^>]*>\s*$", "", text)
        parts = text.split(None, 1)
        if not parts:
            raise NotModeled("an empty body line")
        mnemonic = parts[0]
        if len(parts) == 1:
            return mnemonic, []
        return mnemonic, split_operands(parts[1])

    def body_lines(self, body_text):
        if isinstance(body_text, list):
            return [line for line in body_text if line.strip()]
        out = []
        for line in body_text.split(";"):
            if line.strip():
                out.append(line.strip())
        return out

    def apply_arrival_contract(self, state, arrival_contract):
        """bind each arriving value to the symbol the caller names.

        `arrival_contract` is a list of (place, term): the place is an
        integer register's ABI name or index, or a floating-point
        register's."""
        for place, term in arrival_contract:
            if isinstance(place, str) and place in FLOAT_REGISTERS and \
                    place not in INTEGER_REGISTERS:
                state.write_float(FLOAT_REGISTERS[place], term)
                continue
            if isinstance(place, str):
                if place not in INTEGER_REGISTERS:
                    raise NotModeled(
                        "arrival place %r is not a register of this "
                        "architecture" % place)
                state.bind(INTEGER_REGISTERS[place], term)
                continue
            state.bind(place, term)

    def answer_of(self, state, answer_home="a0"):
        """the term the body left in its answer place."""
        if answer_home in FLOAT_REGISTERS and \
                answer_home not in INTEGER_REGISTERS:
            return state.read_float(FLOAT_REGISTERS[answer_home])
        if answer_home not in INTEGER_REGISTERS:
            raise NotModeled(
                "answer home %r is not a register of this architecture"
                % answer_home)
        return state.read_register(INTEGER_REGISTERS[answer_home])
