"""HiOp_sorter -- the module that sorts one language's operators into
simple_HiOps and complex_HiOps, from each operator's definition in its
lowerer's own code. Its function `sort(lang, operators)` returns both.

Plan: `.../node_0_0_0_0_2_8_model_HiOps/node_0_0_0_0_2_8_0_HiOp_sorter/` (under extract_lang_vocab until 2026-10-15),
and its four sub-nodes:

    definitions      per lowerer   operator -> the functions in the lowerer's
                                   code where its lowering starts (clang:
                                   `ScalarExprEmitter::VisitBinMul` for `*`)
    read_definition  shared        (lang, operator) -> its definition: those
                                   functions, and every function they call or
                                   hand on, up to where the code evaluates an
                                   operand
    composed_of      shared        (lang, operator) -> the other operators
                                   whose own functions its definition reaches
    sort             shared        (lang, operators) -> complex_HiOps, each
                                   with what it is built from, and simple_HiOps

the owner, 2026-10-01: "if its complex, its high level definition will have HiOps
which compose it", and "i was referring to the logical C++ definition, not
prose/comments".

An operator's own function is one that only its own definition calls:
`EmitMul`, which only `*`'s start calls. A function that the definitions of
several operators call belongs to none of them, so reaching it is not
composition (the design's own instance: `goto`, `break` and `continue` all
call `EmitBranchThroughCleanup`). A complex operator reaches another
operator's own function, by a call or by handing it on: `a *= b`'s start
hands `EmitMul` to `EmitCompoundAssign`.

    def sort(lang, operators):
        complex_HiOps, simple_HiOps = {}, []
        own = owners(lang, operators)                      # 1  whose own each function is
        for op in operators:
            parts = composed_of(lang, op, own)             # 2  others' own functions it reaches
            if parts:
                complex_HiOps[op] = parts                  # 3  kept with what it is built from
            else:
                simple_HiOps.append(op)                    # 4  lowers directly
        return complex_HiOps, simple_HiOps

AN EXCEPTION TO THE DESIGN, ARGUED FOR THE OWNER (PCHQ log 367): the design reads
each definition with tree-sitter. clang writes many of its definitions with
macros (`VisitBinMulAssign` comes from `HANDLEBINOP`), and tree-sitter does
not expand them, the design's own open item. So the definition is read from
clang's code compiled in debug mode, the owner's method (logs 350 and 366): every
macro is pasted in, and each function's relocation records name every
function it calls or hands on.

Each lowerer answers `definitions` in its own module beside this one:
clang.py, for c. Nothing in this file names a language, except LOWERERS.
"""

import collections
from typing import NamedTuple

from . import clang

# Which module answers `definitions` for each language.
LOWERERS = {
    "c": clang,
}


class Definitions(NamedTuple):
    """One lowerer's code, as the sort reads it.

    `calls` and `handed`: function -> the functions it calls, and the
    functions whose address it takes to hand on. `starts`: operator -> the
    functions where its lowering starts. `operand_evaluation`: the functions
    where the code evaluates an operand, whatever operator that operand is
    (the visitors' dispatch, and every function that takes a generic
    expression); the definition stops there. `paired`: function -> the
    operator whose own operation the lowerer's code pairs it with, where
    the code says so (clang's macro writes `VisitBin##OP` to call
    `Emit##OP`: EmitSub is `a - b`'s). `own_code`: the functions the
    lowerer's own files define, the only ones that can be an operator's own
    (not a header's inline getter, nor the library the lowerer builds with).
    """

    calls: dict
    handed: dict
    starts: dict
    operand_evaluation: frozenset
    paired: dict
    own_code: frozenset


# A function that calls or hands on the paired operations of this many
# operators or more picks one by the operator it is given, so a definition
# stops there as well: clang's EmitCompoundAssignmentLValue hands each
# compound assignment its operator's Emit##OP by opcode, and EmitPromoted
# calls EmitAdd, EmitSub, EmitMul or EmitDiv for an operand. (Counted over the
# paired operations only, which adding operators does not change; counted
# over every owned function, 693 builtins made 180 functions look like
# dispatchers, EmitMul among them.)
DISPATCH_FAN_OUT = 3


def definitions(lang: str, operators: tuple) -> Definitions:
    """Where each operator's lowering starts in `lang`'s lowerer, and the
    lowerer's code as the sort reads it."""
    lowerer = LOWERERS.get(lang)
    if lowerer is None:
        message = f"HiOp_sorter: no lowerer module answers definitions for {lang!r} yet"
        raise LookupError(message)
    found = lowerer.definitions(operators)
    start_of = {function for operator in operators for function in found.starts.get(operator, ())}
    fan_out = set()
    for function, called in found.calls.items():
        if function in found.operand_evaluation or function in start_of:
            continue
        handed_to = {found.paired.get(t) for t in called + found.handed.get(function, [])}
        if len(handed_to - {None}) >= DISPATCH_FAN_OUT:
            fan_out.add(function)
    found = found._replace(operand_evaluation=found.operand_evaluation | fan_out)
    return found


def read_definition(found: Definitions, operator: str, through=("calls",)) -> set:
    """The operator's definition: its starts, and every function they reach
    by `through` (calls, and with "handed" the functions handed on), stopping
    where the code evaluates an operand."""
    seen = set()
    todo = list(found.starts.get(operator, ()))
    while todo:
        function = todo.pop()
        if function in seen or function in found.operand_evaluation:
            continue
        seen.add(function)
        for edges in through:
            todo.extend(getattr(found, edges).get(function, ()))
    return seen


def owners(found: Definitions, operators: tuple) -> dict:
    """function -> the one operator it belongs to. Only the functions the
    lowerer's own files define can belong to one.

    1. A function the lowerer's code pairs with an operator's start, as that
       operator's own operation, is that operator's: EmitSub is `a - b`'s,
       though clang lowers integer `-a` with it too, as `0 - a`
       (CGExprScalar.cpp line 3441).
    2. Any other function belongs to the one operator whose definition alone
       calls it, if there is one."""
    called_by = collections.defaultdict(set)
    for operator in operators:
        for function in read_definition(found, operator):
            if function in found.own_code:
                called_by[function].add(operator)
    owned = {function: next(iter(ops)) for function, ops in called_by.items() if len(ops) == 1}
    for function, operator in found.paired.items():
        if operator in operators and function in found.own_code:
            owned[function] = operator
    return owned


def shared(found: Definitions, operators: tuple) -> dict:
    """function -> every operator whose definition calls it, for the
    functions two or more call: the helpers the sort counts as no one's."""
    called_by = collections.defaultdict(set)
    for operator in operators:
        for function in read_definition(found, operator):
            if function in found.own_code:
                called_by[function].add(operator)
    found_shared = {function: sorted(ops) for function, ops in called_by.items() if len(ops) > 1}
    return found_shared


def composed_of(found: Definitions, operator: str, owned: dict) -> dict:
    """other operator -> its own functions that `operator`'s definition
    reaches, by a call or by handing it on. Empty when the operator lowers
    directly."""
    parts = collections.defaultdict(set)
    seen = set()
    todo = list(found.starts.get(operator, ()))
    while todo:
        function = todo.pop()
        if function in seen or function in found.operand_evaluation:
            continue
        seen.add(function)
        owner = owned.get(function)
        if owner is not None and owner != operator:
            parts[owner].add(function)
            continue
        todo.extend(found.calls.get(function, ()))
        todo.extend(found.handed.get(function, ()))
    built_from = {other: sorted(functions) for other, functions in parts.items()}
    return built_from


def sort(lang: str, operators: tuple) -> tuple:
    """(complex_HiOps, simple_HiOps, no_start). complex_HiOps: operator ->
    {other operator: the other's own functions it reaches}. simple_HiOps: the
    operators that lower directly. no_start: the operators whose lowering
    starts in no function of the lowerer's code (clang lowers `;` inside
    EmitSimpleStmt's switch)."""
    found = definitions(lang, operators)
    owned = owners(found, operators)
    complex_HiOps, simple_HiOps, no_start = {}, [], []
    for operator in operators:
        if not found.starts.get(operator):
            no_start.append(operator)
            continue
        parts = composed_of(found, operator, owned)
        if parts:
            complex_HiOps[operator] = parts
        else:
            simple_HiOps.append(operator)
    return complex_HiOps, simple_HiOps, no_start
