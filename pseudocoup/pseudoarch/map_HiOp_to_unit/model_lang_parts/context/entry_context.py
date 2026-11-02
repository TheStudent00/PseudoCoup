"""context -- one HiOp entry with everything carried into the lowerer to
determine its path (PCHQ plan: research/trace_logical_paths/context).

    context = Context(operator, holders, setup)
    text = standard_source(context)
"""

import json
import os
import re
import sys
from typing import NamedTuple

# The standard form's own function and struct names take this key.
KEY = "k"


class Operator(NamedTuple):
    """The HiOp: clang's name for it, its template, and its parts in the
    template's order."""

    name: str
    spelling: str
    operands: tuple


class Setup(NamedTuple):
    """A setup: the compile command, which fixes the language (GNU C), the
    options and the target, and any types it declares beside the standard
    form's own (a matrix type needs -fenable-matrix and a declaration)."""

    command: str
    preamble: tuple = ()


class Context(NamedTuple):
    operator: Operator
    holders: tuple
    setup: Setup
    program: str = ""


def our_setup() -> Setup:
    """lower_HiOp's command for C, as it compiles every standard source."""
    from PseudoArch.map_HiOp_to_unit import lower_HiOp
    setup = Setup(lower_HiOp.COMPILE_COMMAND["c"])
    return setup


def setup_with(options: str, preamble: tuple = ()) -> Setup:
    """Our setup with options added to its command, and types declared."""
    from PseudoArch.map_HiOp_to_unit import lower_HiOp
    setup = Setup(lower_HiOp.COMPILE_COMMAND["c"] + " " + options, preamble)
    return setup


def standard_source(context: Context) -> str:
    """The program: the standard form's preamble and the setup's own
    declarations, then the HiOp in the standard form with the context's
    holders, routed as the record routes it; or the context's own program."""
    if context.program:
        return context.program
    from PseudoArch.map_HiOp_to_unit import mask_maker as DRY_mask_maker
    from PseudoArch.map_HiOp_to_unit.lower_HiOp import standard_HiOp_wrapper as wrapper
    lines = list(wrapper.PREAMBLE["c"])
    for line in context.setup.preamble:
        lines.append(line)
    held = wrapper.standard_HiOp_wrapper("c", KEY, context.operator, context.holders, DRY_mask_maker.ROUTING)
    for line in held:
        lines.append(line)
    text = "\n".join(lines) + "\n"
    return text


def command_for(context: Context, clang: str, source: str, output: str) -> list:
    """Our setup's command, run with `clang`, on `source`, writing `output`."""
    words = context.setup.command.split()
    words[0] = clang
    command = words + ["-o", output, source]
    return command


HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
if not os.path.isdir(os.path.join(PROJECTS, "PseudoArch")):
    PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "Projects"))
if PROJECTS not in sys.path:
    sys.path.insert(0, PROJECTS)
