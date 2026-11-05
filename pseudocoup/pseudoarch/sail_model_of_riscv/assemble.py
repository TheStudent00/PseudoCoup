#!/usr/bin/env python3
"""assemble.py -- the instruction WORDS of a body's text lines, by the
image's own assembler (task sl1).

WHAT THIS IS, one sentence, in relation: the step that turns the
disassembled text the carver hands the lifter back into the machine
words the Sail model's own decoder reads, so that the lifter's identity
for an instruction is its encoding and never its spelling.

HOW: the lines are written to one assembly file, assembled by clang for
riscv64 with the march string the corpus's compilers target, and read
back with llvm-objdump, whose output carries the bytes of every
instruction beside its text; a line the assembler refuses is a refusal
by that line's number and clang's own words.
"""
import os
import re
import shutil
import subprocess

CLANG = shutil.which("clang") or "clang-21"
OBJDUMP = shutil.which("llvm-objdump") or "llvm-objdump-21"
MARCH = "rv64gc_zba_zbb_zbs_zicond_zcb_zfa"
OBJDUMP_LINE = re.compile(r"^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2} ?)+|[0-9a-f]{4,8})\s*(.*)$")


def words_of(lines, work):
    """[(word as int, byte length)] per line, in order; raises
    AssemblyRefused with clang's diagnostic."""
    if not os.path.isdir(work):
        os.makedirs(work)
    source = os.path.join(work, "body.S")
    obj = os.path.join(work, "body.o")
    text = [".text", ".option rvc"]
    for line in lines:
        text.append("    " + clean(line))
    open(source, "w").write("\n".join(text) + "\n")
    proc = subprocess.run([CLANG, "--target=riscv64-unknown-elf",
                           "-march=" + MARCH, "-c", source, "-o", obj],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise AssemblyRefused(proc.stderr.decode("utf-8", "replace")[:600])
    proc = subprocess.run([OBJDUMP, "-d", "-M", "no-aliases",
                           "--mattr=+m,+a,+f,+d,+c,+zba,+zbb,+zbs,+zicond,+zcb,+zfa",
                           obj], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise AssemblyRefused(proc.stderr.decode("utf-8", "replace")[:600])
    out = []
    for raw in proc.stdout.decode("utf-8", "replace").splitlines():
        hit = OBJDUMP_LINE.match(raw)
        if hit is None:
            continue
        digits = hit.group(1).replace(" ", "")
        if len(digits) not in (4, 8):
            continue
        # llvm-objdump prints the word little-endian byte by byte when
        # spaced, and as one number otherwise; both are normalised here
        if " " in hit.group(1).strip():
            pairs = hit.group(1).split()
            value = int("".join(reversed(pairs)), 16)
        else:
            value = int(digits, 16)
        out.append((value, len(digits) // 2))
    return out


def clean(line):
    """the line without the disassembler's trailing symbol aid."""
    text = re.sub(r"\s*<[^>]*>\s*$", "", line.strip())
    return text


class AssemblyRefused(Exception):
    pass


if __name__ == "__main__":
    import sys
    print(words_of(sys.argv[2:], sys.argv[1]))
