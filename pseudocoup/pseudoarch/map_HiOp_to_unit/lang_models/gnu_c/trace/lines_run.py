"""lines_run -- which lines of a function of clang's a recorded run runs, and
where it goes from each, read from traced_clang's own binary (PCHQ plan:
research/trace_logical_paths; the page's routes, log 486).

    ranges = function_ranges(names, wanted)
    blocks = blocks_of(binary, ranges)
    ran = lines_ran(events, blocks, starts)

A branch event's offset is where the recorder's call returns to, at the start
of a block of clang's code: built with `no-prune` (run elv2_l202), sanitizer
coverage calls the recorder once at the start of every block. (Without it,
the build of runs elv2_l192 and elv2_l199 recorded only the edges whose
taking the other recorded ones do not imply, so the instructions after one
recorder call could belong to several blocks: run elv2_l201.) llvm-objdump's
listing of a function, with its source lines, gives each block's
instructions and so its lines. A block begins at the instruction that loads
the recorder's argument (the address of the block's counter, in
`__sancov_guards`), just before the call. A run runs a line when it runs a
block that holds it. It leaves a block from the line of the block's last
instruction (its jump), for the next block it runs in the same function's
frame.
"""

import bisect
import gzip
import os
import re
import subprocess
from typing import NamedTuple

OBJDUMP = os.environ.get("LLVM_OBJDUMP", "llvm-objdump-21")
GUARD = "<__sanitizer_cov_trace_pc_guard>"
GUARD_ADDRESS = "<__start___sancov_guards"
LINE_MARK = re.compile(r"^; (/\S+?):(\d+)")
INSTRUCTION = re.compile(r"^\s*([0-9a-f]+):\s+(\S+)(.*)$")


class Block(NamedTuple):
    function: str
    file: str
    first: int
    last: int
    lines: tuple


def function_ranges(names: dict, wanted: list) -> list:
    """(wanted name, start, end) for every function whose name holds one of
    `wanted` followed by its parameters (`ScalarExprEmitter::EmitAdd`), every
    overload; a function ends where the next one starts."""
    starts = sorted(names)
    ranges = []
    for name in wanted:
        mark = "::" + name + "("
        for position in range(len(starts)):
            offset = starts[position]
            if mark in names[offset] or names[offset].startswith(name + "("):
                end = offset + 1
                if position + 1 < len(starts):
                    end = starts[position + 1]
                ranges.append((name, offset, end))
    return ranges


# Each function's listing is read from the binary once and kept on disk, so
# the loop's workers, which begin every round without the blocks, and every
# later run read it from there (PCHQ Gemini copy, run riscv64-runner_l18: one
# candidate's functions took 88 s of objdump, and every worker did it again in
# every round). TLP_LISTING_CACHE names the folder; unset, nothing is kept.
# The kept listing is the text objdump wrote, so every reading of it is the
# same as before.
LISTING_CACHE = os.environ.get("TLP_LISTING_CACHE", "")


def kept_listing_path(binary: str, start: int, end: int) -> str:
    """Where a function's listing is kept: under the binary's name, size
    and time, so a rebuilt binary is never read from an older listing."""
    facts = os.stat(binary)
    tag = f"{os.path.basename(binary)}_{facts.st_size}_{int(facts.st_mtime)}"
    path = os.path.join(LISTING_CACHE, tag, f"{start:x}_{end:x}.txt.gz")
    return path


def kept_listing(path: str) -> str:
    with gzip.open(path, "rt", encoding="utf-8") as read:
        text = read.read()
    return text


def keep_listing(path: str, text: str) -> None:
    """Written whole or not at all: beside, then put in place."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    beside = f"{path}.{os.getpid()}.writing"
    with gzip.open(beside, "wt", encoding="utf-8", compresslevel=1) as written:
        written.write(text)
    os.replace(beside, path)


def listing_of(binary: str, start: int, end: int) -> str:
    path = ""
    if LISTING_CACHE:
        path = kept_listing_path(binary, start, end)
        if os.path.exists(path):
            text = kept_listing(path)
            return text
    command = [OBJDUMP, "-d", "-l", "--no-show-raw-insn", f"--start-address=0x{start:x}",
               f"--stop-address=0x{end:x}", binary]
    finished = subprocess.run(command, capture_output=True, text=True, check=True)
    if path:
        keep_listing(path, finished.stdout)
    return finished.stdout


def add_line(values: dict, number: int) -> None:
    if not number:
        return
    if not values["first"]:
        values["first"] = number
    values["lines"].add(number)
    values["last"] = number


def new_block(file: str, lines: list) -> dict:
    values = {"file": file, "first": 0, "last": 0, "lines": set()}
    for number in lines:
        add_line(values, number)
    return values


def blocks_in(listing: str, function: str) -> dict:
    """offset -> Block, for every block of one function's listing. The
    instructions from the load of a counter's address up to the next such
    load are one block; its offset is where its recorder call returns to."""
    found = {}
    current_file = ""
    current_line = 0
    block = None
    pending = []
    opening = False
    for line in listing.split("\n"):
        mark = LINE_MARK.match(line)
        if mark:
            current_file = mark.group(1)
            current_line = int(mark.group(2))
            continue
        instruction = INSTRUCTION.match(line)
        if not instruction:
            continue
        address = int(instruction.group(1), 16)
        operands = instruction.group(3)
        is_call = instruction.group(2).startswith("call")
        if GUARD_ADDRESS in operands and not is_call:
            block = None
            pending = [current_line]
            continue
        if is_call and GUARD in operands:
            pending.append(current_line)
            opening = True
            continue
        if opening:
            block = address
            found[block] = new_block(current_file, pending)
            opening = False
            pending = []
        if block is None:
            pending.append(current_line)
            continue
        add_line(found[block], current_line)
    blocks = {}
    for offset, values in found.items():
        blocks[offset] = Block(function, values["file"], values["first"], values["last"],
                               tuple(sorted(values["lines"])))
    return blocks


def blocks_of(binary: str, ranges: list) -> dict:
    """offset -> Block, for every block of every function in `ranges`."""
    blocks = {}
    for name, start, end in ranges:
        found = blocks_in(listing_of(binary, start, end), name)
        for offset, block in found.items():
            blocks[offset] = block
    return blocks


# Where each block goes next (PCHQ plan research/trace_logical_paths_clone,
# SUPPORT_plan_the_untaken_side_names_the_next_holder.md §4.1, 2026-10-20):
# the untaken side of a test is a block the test's block jumps or falls to
# that no context ran. The listing is x86-64 (the VM's build): every `j...`
# mnemonic is a jump; `jmp` and `ret` and `ud2` end a block with no fall-through.
JUMP = re.compile(r"^j[a-z]+$")
NO_FALL_THROUGH = ("jmp", "jmpq", "ret", "retq", "ud2")
JUMP_TARGET = re.compile(r"^\s*(?:0x)?([0-9a-f]+)\b")


def jump_target(operands: str) -> int:
    """The address a direct jump goes to (`jne 0x502e690 <...>`); 0 for an
    indirect one (`jmpq *%rax`, a switch's table)."""
    if "*" in operands:
        return 0
    found = JUMP_TARGET.match(operands)
    if not found:
        return 0
    target = int(found.group(1), 16)
    return target


def block_owners(listing: str) -> tuple:
    """(address -> the offset of the block blocks_in puts it in, block
    offsets in order, block offset -> [jump targets], block offset -> its last
    mnemonic). Read with blocks_in's own rule for where a block begins, so the
    offsets are the keys blocks_in gives; the recorder's call and the load
    before it belong to the block they open."""
    owner = {}
    order = []
    targets = {}
    last = {}
    waiting = []
    block = None
    opening = False
    for line in listing.split("\n"):
        instruction = INSTRUCTION.match(line)
        if not instruction:
            continue
        address = int(instruction.group(1), 16)
        mnemonic = instruction.group(2)
        operands = instruction.group(3)
        is_call = mnemonic.startswith("call")
        if GUARD_ADDRESS in operands and not is_call:
            block = None
            waiting.append(address)
            continue
        if is_call and GUARD in operands:
            waiting.append(address)
            opening = True
            continue
        if opening:
            block = address
            order.append(block)
            targets[block] = []
            for waited in waiting:
                owner[waited] = block
            waiting = []
            opening = False
        if block is None:
            waiting.append(address)
            continue
        owner[address] = block
        last[block] = mnemonic
        if JUMP.match(mnemonic):
            targets[block].append(jump_target(operands))
    found = (owner, order, targets, last)
    return found


def successors_in(listing: str, function: str) -> dict:
    """offset -> [offsets], for every block of one function's listing (the
    offsets blocks_in gives `function`'s blocks): the blocks its jumps go to,
    and the next block when it does not end in a jump that always goes. An
    indirect jump (a switch's table) goes to the blocks no direct jump or
    fall-through reaches, since the table is not in the listing."""
    owner, order, targets, last = block_owners(listing)
    successors = {}
    reached = set()
    indirect = []
    for position in range(len(order)):
        offset = order[position]
        successors[offset] = []
        for target in targets[offset]:
            if target == 0:
                indirect.append(offset)
                continue
            to = owner.get(target)
            if to is None or to in successors[offset]:
                continue
            successors[offset].append(to)
            reached.add(to)
        falls = last.get(offset, "") not in NO_FALL_THROUGH
        if falls and position + 1 < len(order):
            following = order[position + 1]
            if following not in successors[offset]:
                successors[offset].append(following)
                reached.add(following)
    unreached = []
    for offset in order[1:]:
        if offset not in reached:
            unreached.append(offset)
    for offset in indirect:
        for to in unreached:
            if to not in successors[offset]:
                successors[offset].append(to)
    return successors


def owner_of(offset: int, starts: list) -> int:
    index = bisect.bisect_right(starts, offset) - 1
    if index < 0:
        return 0
    owner = starts[index]
    return owner


def note_block(ran: dict, block: Block) -> None:
    if block.function not in ran:
        ran[block.function] = {"lines": set(), "leaves": set()}
    for line in block.lines:
        ran[block.function]["lines"].add(line)


def lines_ran(events: list, blocks: dict, starts: list) -> dict:
    """function -> {"lines": the lines run, "leaves": (from line, to line)
    for every move from one block to the next in the same frame}."""
    ran = {}
    frames = []
    pending = None
    for kind, offset in events:
        if kind == "enter":
            first = None
            if pending is not None and owner_of(pending, starts) == offset:
                first = pending
            frames.append([offset, first])
            pending = None
            continue
        if kind == "return":
            if frames:
                frames.pop()
            pending = None
            continue
        block = blocks.get(offset)
        if block is None:
            pending = None
            continue
        note_block(ran, block)
        owner = owner_of(offset, starts)
        if frames and frames[-1][0] == owner:
            last = frames[-1][1]
            if last is not None:
                ran[block.function]["leaves"].add((blocks[last].last, block.first))
            frames[-1][1] = offset
        else:
            pending = offset
    return ran
