"""lower_HiOp -- the standard source compiled, and the standard function's machine
words read at its symbol as arch-opcodes: the LoHiOp.

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/`, with
its two sub-nodes, `compile_standard_source` and `read_words_at_symbol`.

    machine_code = compile_standard_source(lang, source)            # refuses when the language declines the HiOp
    LoHiOp = read_words_at_symbol(machine_code, source.symbol)  # refuses when no symbol reaches the object

A machine word and its arch-opcode are one thing in two forms (the node's
definition), so nothing is mapped here, and no Sail model is read here. the owner,
2026-09-21: "the mapping between arch-opcode and machine-opcode is 1-to-1".

Written fresh on 2026-10-07 ; nothing in it is lifted
from the research scripts.
"""
import hashlib
import os
import re
import shlex
import subprocess
import tempfile
from typing import NamedTuple, Optional

# What standard_HiOp_wrapper hands on: the standard source's text, and the name of the
# standard function in it. The class was here until standard_HiOp_wrapper had a module
# of its own, and moved there on 2026-10-13 .
from .standard_HiOp_wrapper import StandardSource


# The compiler and its flags, one row per language.
#
# The optimizer is off (-O0). the owner, 2026-10-08: "we want an honest lowering,
# not a simplification ... the default is no optimizer for all lowerings where
# we are trying to extract the arch-units." The optimizer is used only with a
# reason given to the owner before the run. Until 2026-10-08 this row said -O1,
# copied from the grid's syntax-only check .
#
# The debug table is on (-g), so each word can be traced to the field it
# reads. the owner, the same day: "debug as a default might be a good rule to have."
#
# The rest is GNU C's dialect, the grid's own, with -c: no -march, because our
# target is clang's own riscv64 default (RVA23U64 + Zifencei); -ferror-limit=0,
# so clang lists every error, not only the first 19.
#
# The check of every HiOp on x86-64 and aarch64 (the owner's rule of 2026-10-01,
# lower only what lowers on every major architecture;  swaps
# this row's target and DISASSEMBLE_COMMAND for its run
# (Research/lower_HiOp/lower_gnu_c.py --target); the reader below reads the
# words of all three.
COMPILE_COMMAND = {
    "c": "clang -std=gnu17 -O0 -g --target=riscv64-unknown-linux-gnu -nostdlibinc -ferror-limit=0 -Wno-atomic-alignment -c",
}
SUFFIX = {
    "c": ".c",
}
# The words are read in the architecture's own names (-M no-aliases: never an
# assembler shorthand, such as `ret` for `jalr zero, 0x0(ra)`), with their
# relocations (-r), and with the source line the debug table gives each (-l),
# which extract_unit_from_LoHiOp cuts the Unit by . No list of
# extensions is given: the disassembler reads the target the compile used
# from the object file itself.
DISASSEMBLER = os.environ.get("LLVM_OBJDUMP", "llvm-objdump")
SYMBOL_LISTER = os.environ.get("LLVM_NM", "llvm-nm")
DISASSEMBLE_COMMAND = f"{DISASSEMBLER} -d -r -l -M no-aliases"
SYMBOLS_COMMAND = f"{SYMBOL_LISTER} --print-size --defined-only"
COMMAND_SECONDS = 30
# Where standard sources and their object files are written. A caller with many
# standard sources points this at a scratch folder of its own.
WORK_DIRECTORY = tempfile.gettempdir()


class MachineCode(NamedTuple):
    """The object file a compile wrote, or the compiler's refusal of the
    source, in the compiler's own words."""

    path: Optional[str]
    refusal: Optional[str]


class Word(NamedTuple):
    """One machine word of the standard function, read as its arch-opcode, with
    the source line the debug table files it under (None when the listing
    gives none)."""

    address: int
    bytes_hex: str
    arch_opcode: str
    operands: str
    relocations: tuple
    line: Optional[int] = None


class LoHiOp(NamedTuple):
    """The standard function's words in order, or why there are none."""

    symbol: str
    words: tuple
    refusal: Optional[str]


def lower_HiOp(lang: str, source: StandardSource, compile_command: Optional[str] = None) -> LoHiOp:
    """The HiOp becomes machine words, read as arch-opcodes: the LoHiOp."""
    machine_code = compile_standard_source(lang, source, compile_command)
    LoHiOp = read_words_at_symbol(machine_code, source.symbol)
    return LoHiOp


# ---------------------------------------------------------------------------
# compile_standard_source


def compile_standard_source(lang: str, source: StandardSource, compile_command: Optional[str] = None) -> MachineCode:
    """The standard source compiled for riscv64, with the optimizer off and the
    debug table on, into an object file. Refuses when the compiler refuses the
    source: the language declines the HiOp, and the refusal keeps the
    compiler's own words."""
    source_path = write_standard_source(lang, source)
    object_path = object_path_of(source_path)
    command = compile_command if compile_command is not None else COMPILE_COMMAND[lang]
    finished = run_command(command, [source_path, "-o", object_path])
    machine_code = machine_code_of(finished, object_path)
    return machine_code


def write_standard_source(lang: str, source: StandardSource) -> str:
    """The standard source written into the work folder, named by its own text,
    so the same source is always the same file."""
    encoded = source.text.encode("utf-8")
    digest = hashlib.sha1(encoded).hexdigest()
    file_name = f"held_{digest[:20]}{SUFFIX[lang]}"
    source_path = os.path.join(WORK_DIRECTORY, file_name)
    with open(source_path, "w", encoding="utf-8") as held:
        held.write(source.text)
    return source_path


def object_path_of(source_path: str) -> str:
    stem, _ = os.path.splitext(source_path)
    object_path = stem + ".o"
    return object_path


def run_command(command: str, arguments: list) -> subprocess.CompletedProcess:
    """The command run to its end, everything it printed kept. A command
    that has not finished in COMMAND_SECONDS is stopped and reported as
    such."""
    words = shlex.split(command) + list(arguments)
    try:
        finished = subprocess.run(words, capture_output=True, text=True, errors="replace",
                                  timeout=COMMAND_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        message = f"did not finish in {COMMAND_SECONDS} s"
        finished = subprocess.CompletedProcess(words, -1, "", message)
    return finished


def machine_code_of(finished: subprocess.CompletedProcess, object_path: str) -> MachineCode:
    if finished.returncode != 0:
        refusal = finished.stderr.strip()
        refused = MachineCode(None, refusal)
        return refused
    compiled = MachineCode(object_path, None)
    return compiled


# ---------------------------------------------------------------------------
# read_words_at_symbol


def read_words_at_symbol(machine_code: MachineCode, symbol: str) -> LoHiOp:
    """The standard function's machine words, read out of the object file as
    arch-opcodes: from its symbol, for the symbol's size, in order. That list
    is the LoHiOp. Refuses when the symbol is not in the object."""
    if machine_code.refusal is not None:
        refused = LoHiOp(symbol, (), machine_code.refusal)
        return refused
    words_by_symbol = words_of_object(machine_code.path)
    words = words_by_symbol.get(symbol)
    if words is None:
        missing = LoHiOp(symbol, (), f"no symbol {symbol} in the object")
        return missing
    lowered = LoHiOp(symbol, words, None)
    return lowered


# The words of the last object read, by symbol: an object holding many held
# functions is read once, and each symbol is then cut from it.
LAST_OBJECT = {"path": None, "words_by_symbol": {}}


def words_of_object(object_path: str) -> dict:
    if LAST_OBJECT["path"] == object_path:
        words_by_symbol = LAST_OBJECT["words_by_symbol"]
        return words_by_symbol
    sizes = symbol_sizes(object_path)
    listing = disassembly(object_path)
    words_by_symbol = words_by_symbol_of(listing, sizes)
    LAST_OBJECT["path"] = object_path
    LAST_OBJECT["words_by_symbol"] = words_by_symbol
    return words_by_symbol


# `0000000000000000 0000000000000014 T op_25`: address, size, kind, name.
SYMBOL_LINE = re.compile(r"^([0-9a-f]+)\s+([0-9a-f]+)\s+[Tt]\s+(\S+)$")


def symbol_sizes(object_path: str) -> dict:
    """Each function symbol's size in bytes, from the object's symbol table."""
    finished = run_command(SYMBOLS_COMMAND, [object_path])
    if finished.returncode != 0:
        message = f"lower_HiOp: {SYMBOL_LISTER} could not read {object_path}: {finished.stderr.strip()}"
        raise RuntimeError(message)
    sizes = {}
    for line in finished.stdout.splitlines():
        found = SYMBOL_LINE.match(line.strip())
        if found is None:
            continue
        sizes[found.group(3)] = int(found.group(2), 16)
    return sizes


def disassembly(object_path: str) -> list:
    """The object's machine words as the disassembler prints them. A
    disassembler that fails is a fault of the tools, not a refusal of the
    HiOp, so it stops the run."""
    finished = run_command(DISASSEMBLE_COMMAND, [object_path])
    if finished.returncode != 0:
        message = f"lower_HiOp: {DISASSEMBLER} could not read {object_path}: {finished.stderr.strip()}"
        raise RuntimeError(message)
    lines = finished.stdout.splitlines()
    return lines


# `0000000000000000 <op_25>:` opens a symbol's words.
SYMBOL_HEADER = re.compile(r"^([0-9a-f]+) <([^>]+)>:$")
# `       8: 00c585bb     	addw	a1, a1, a2`: address, bytes, arch-opcode,
# operands. A compressed riscv64 word prints 4 hex digits, a full one 8, and an
# aarch64 word 8. x86-64 prints its bytes in pairs, `48 89 e5`, which the
# check on all three architectures reads too (elv2_l101, .
WORD_LINE = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f]{8}|[0-9a-f]{4}|(?:[0-9a-f]{2} )*[0-9a-f]{2})\s+(\S+)(?:\s+(.*))?$")
# `		0000000000000014:  R_RISCV_CALL_PLT	sin`: a relocation on the word at
# that address.
RELOCATION_LINE = re.compile(r"^\s*([0-9a-f]+):\s+(R_\S+)\s*(.*)$")
# `; /work/lower_HiOp/gnu_c_all/held_ab12.c:17`, which -l prints: the source
# line the words below it were written for, by the debug table.
SOURCE_LINE = re.compile(r"^; .*:(\d+)$")
# What the disassembler adds for the reader: `<op_7+0x10>` after a branch's
# target, and a comment, `# ...` or `// ...`. aarch64 writes its immediates
# with a `#`, `sub sp, sp, #0x10`, so only a `#` followed by a space opens a
# comment: until elv2_l102 a lone `#` did, and every aarch64 immediate was
# cut off .
READER_NOTE = re.compile(r"\s*(<[^>]*>|#\s.*|//.*)$")


def words_by_symbol_of(lines: list, sizes: dict) -> dict:
    """The listing cut into each symbol's words, each symbol stopped at its
    own size. A function of size 0 is in the object with no words: the
    disassembler prints no heading for it (elv2_l96: `__builtin_unreachable()`
    held alone compiles to a function with nothing in it)."""
    bodies = symbol_bodies(lines, sizes)
    words_by_symbol = {}
    for symbol, size in sizes.items():
        if size == 0:
            words_by_symbol[symbol] = ()
    for symbol, (start, body) in bodies.items():
        words = words_of_lines(body)
        size = sizes.get(symbol)
        words_by_symbol[symbol] = words_within(words, start, size)
    return words_by_symbol


def symbol_bodies(lines: list, sizes: dict) -> dict:
    """Symbol -> (its address, the listing lines under it). A header line
    opens a new function only for a function's own name. A local label inside
    a function keeps its lines with that function: riscv64 names the place an
    address computation reaches (`.Ltmp0`) and the `auipc` that begins it
    (`.Lpcrel_hi0`), and the disassembler prints a header line for each.
    Until 2026-10-13 every header line opened a new function, so the words
    after the first local label were never read as the function's: `&&m`
    kept 5 of its 16 riscv64 words, and 1,170 other riscv64 Units were read
    short 
    445)."""
    bodies = {}
    symbol = None
    for line in lines:
        header = SYMBOL_HEADER.match(line)
        if header is not None and opens_a_function(header.group(2), sizes):
            symbol = header.group(2)
            start = int(header.group(1), 16)
            bodies[symbol] = (start, [])
            continue
        if symbol is not None:
            bodies[symbol][1].append(line)
    return bodies


def opens_a_function(name: str, sizes: dict) -> bool:
    """A function's own name: the symbol table gives it a size above 0. A
    local label has size 0 (`llvm-nm` lists `.Ltmp0` as `t`, size 0). A name
    the table does not list opens a new function, as every header did
    before."""
    size = sizes.get(name)
    opens = size is None or size > 0
    return opens


def words_of_lines(body: list) -> list:
    """One Word per instruction line, with the relocations printed under it
    and the source line the debug table gives it. A relocation belongs to the
    word printed just above it: riscv64 and aarch64 put a relocation at its
    word's own address, but x86-64 puts a call's 1 byte into the call
    (elv2_l101), so the address alone does not name the word."""
    words = []
    source_line = None
    for line in body:
        marker = SOURCE_LINE.match(line)
        if marker is not None:
            source_line = int(marker.group(1))
            continue
        found = WORD_LINE.match(line)
        if found is not None:
            word = word_of(found, source_line)
            words.append(word)
            continue
        relocation = relocation_of(line)
        if relocation is not None and words:
            words[-1] = with_relocation(words[-1], relocation)
    return words


def word_of(found: re.Match, source_line: Optional[int]) -> Word:
    address = int(found.group(1), 16)
    printed = found.group(4)
    if printed is None:
        printed = ""
    operands = READER_NOTE.sub("", printed)
    operands = operands.strip()
    word = Word(address, found.group(2), found.group(3), operands, (), source_line)
    return word


def relocation_of(line: str) -> Optional[str]:
    found = RELOCATION_LINE.match(line)
    if found is None:
        return None
    target = found.group(3).strip()
    relocation = f"{found.group(2)} {target}"
    relocation = relocation.strip()
    return relocation


def with_relocation(word: Word, relocation: str) -> Word:
    relocations = word.relocations + (relocation,)
    word = word._replace(relocations=relocations)
    return word


def words_within(words: list, start: int, size: Optional[int]) -> tuple:
    """The words from the symbol's address up to its size; what the
    disassembler prints after that (padding before the next symbol) is not
    the function's."""
    if size is None:
        kept = tuple(words)
        return kept
    end = start + size
    within = []
    for word in words:
        if word.address < end:
            within.append(word)
    kept = tuple(within)
    return kept

from . import standard_HiOp_wrapper, extract_unit_from_LoHiOp  # noqa: E402,F401
