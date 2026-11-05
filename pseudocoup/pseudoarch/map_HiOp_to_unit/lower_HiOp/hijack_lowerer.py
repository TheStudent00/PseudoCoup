"""hijack_lowerer -- supplies structured `state_info[0]` (`StateInfo0`) at the
lowerer's HiOp entry point (`HIJACK_HIOP=1`) with the optimizer off (`-O0`) and
produces the object file (`MachineCode`) with `__hiop_unit_begin` and
`__hiop_unit_end` boundary relocations.

Plan: `.../node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_0_hijack_lowerer/`.
"""

from __future__ import annotations

import hashlib
import os
import shlex
import subprocess
import tempfile
from typing import Dict, NamedTuple, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..model_lang_parts.context.entry_context import StateInfo0

DEFAULT_HIJACK_CLANG = "/tmp/llvm-hijack-build/bin/clang"
HIJACK_CLANG = os.environ.get(
    "HIJACK_CLANG",
    DEFAULT_HIJACK_CLANG if os.path.isfile(DEFAULT_HIJACK_CLANG) else "clang",
)

ARCH_TRIPLE: Dict[str, str] = {
    "riscv64": "riscv64-unknown-linux-gnu",
    "x86-64": "x86_64-unknown-linux-gnu",
    "x86_64": "x86_64-unknown-linux-gnu",
    "aarch64": "aarch64-unknown-linux-gnu",
}

COMMAND_SECONDS = 30
WORK_DIRECTORY = tempfile.gettempdir()


class MachineCode(NamedTuple):
    """The object file a hijacked lowerer invocation wrote, or its refusal."""

    path: Optional[str]
    refusal: Optional[str]


class HijackedEntry(NamedTuple):
    """The hijacked entry descriptor and its `op_<key>` symbol and line."""

    text: str
    symbol: str
    hiop_line: int
    state_info_0: StateInfo0


def _hiop_line_of(program_text: str, symbol: str) -> int:
    """Return the 1-based line number of the HiOp statement inside `op_<key>`."""
    header = f" {symbol}("
    lines = program_text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if header in line and line.rstrip().endswith("{"):
            return idx + 1
    return max(1, len(lines) - 1)


def hijack_compile_command(state_info_0: StateInfo0, clang_bin: Optional[str] = None) -> str:
    """Build the `-O0 -g` hijacked lowerer command for `state_info_0`."""
    compiler = clang_bin or HIJACK_CLANG
    arch = state_info_0.target.replace("-", "_")
    triple = ARCH_TRIPLE.get(arch, ARCH_TRIPLE["riscv64"])
    cmd = [
        compiler,
        "-x",
        "c",
        "-std=gnu17",
        "-O0",
        "-g",
        "-mllvm",
        "-fast-isel=0",
        f"--target={triple}",
        "-nostdlibinc",
        "-ferror-limit=0",
        "-Wno-atomic-alignment",
    ]
    if arch == "riscv64":
        cmd.append("-mno-relax")
    for opt in state_info_0.options:
        if opt and not opt.startswith("not "):
            cmd.append(opt)
    if any(p.place == "matrix element" or "m4x4f" in p.holder for p in state_info_0.parts):
        if "-fenable-matrix" not in cmd:
            cmd.append("-fenable-matrix")
    cmd.append("-c")
    return " ".join(cmd)


def hijack_lowerer(
    state_info_0: StateInfo0,
    key: str = "k",
    compile_command: Optional[str] = None,
    library_decl: str = "",
) -> Tuple[MachineCode, HijackedEntry]:
    """Supply `state_info_0` at the lowerer's HiOp entry point (`HIJACK_HIOP=1`)
    and return `(MachineCode, HijackedEntry)`."""
    from ..lang_models.gnu_c.entry_points import synthesize_entry_program

    arch = state_info_0.target.replace("-", "_")
    extra_preamble = ()
    if any(p.place == "matrix element" or "m4x4f" in p.holder for p in state_info_0.parts):
        extra_preamble = ("typedef float m4x4f __attribute__((matrix_type(4, 4)));",)
    text, symbol = synthesize_entry_program(
        state_info_0,
        key=key,
        arch=arch,
        extra_preamble=extra_preamble,
        library_decl=library_decl,
    )
    hiop_line = _hiop_line_of(text, symbol)
    entry = HijackedEntry(text=text, symbol=symbol, hiop_line=hiop_line, state_info_0=state_info_0)

    digest = hashlib.sha1((text + "|" + arch + "|" + str(state_info_0.options)).encode("utf-8")).hexdigest()
    source_path = os.path.join(WORK_DIRECTORY, f"hijack_{digest[:20]}.c")
    object_path = os.path.join(WORK_DIRECTORY, f"hijack_{digest[:20]}.o")
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(text)

    command = compile_command if compile_command is not None else hijack_compile_command(state_info_0)
    words = shlex.split(command) + [source_path, "-o", object_path]
    env = dict(os.environ)
    env["HIJACK_HIOP"] = "1"
    try:
        finished = subprocess.run(
            words,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=COMMAND_SECONDS,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return MachineCode(None, f"did not finish in {COMMAND_SECONDS} s"), entry

    if finished.returncode != 0:
        return MachineCode(None, finished.stderr.strip()), entry
    return MachineCode(object_path, None), entry
