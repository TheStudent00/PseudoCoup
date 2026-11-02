"""logical_path -- the HiOp's path cut from a trace at the standard form's
marks, every call followed until it reaches its exit to LLVM (PCHQ plan:
research/trace_logical_paths/logical_path).

    path = from_trace(context, found, names, starts)

    checking   the steps of the lowerer's action on the HiOp: the last
               `Sema::ActOn...` the parser calls before the standard form's
               closing parenthesis. The parser builds an expression from the
               inside out, so the HiOp's own action is the last one inside
               the parentheses. The parenthesis is the first
               `Sema::ActOnParenExpr` of the function's body, or, after a
               cast (a builtin's `(void)(NAME(...))`), the first
               `Sema::ActOnParenListExpr`: clang 21 reads parentheses that
               follow a cast as a list (clang/lib/Parse/ParseExpr.cpp, lines
               2856 and 2888), which `ActOnCastExpr` then makes a
               parenthesis (clang/lib/Sema/SemaExpr.cpp, line 7869). Clang
               calls both for a refused HiOp too, on the recovery expression
               the parser makes (ParseExpr.cpp, lines 533-538 and
               1893-1899). When it does not, the statement's end is the mark
               (`ActOnExprStmt`, `ActOnExprStmtError`, `ActOnCompoundStmt`).
    lowering   the steps of the first `VisitParenExpr` of clang's scalar,
               complex or aggregate emitter, from its entry to its return:
               the standard form's parentheses, which hold the HiOp and
               nothing else. (The constant evaluator and four of CodeGen's
               own visitors have a VisitParenExpr too; they are not marks.)
    exits      each call into LLVM's IR builder, and each diagnostic clang
               reports (`DiagnosticsEngine::Report`, which clang calls only
               for a diagnostic it does not ignore): the step records the
               call and the path does not go into it. A diagnostic's exit is
               named by the function of clang's that issued it; a builder's
               exit that put no instruction in the block (the builder hands
               back a value that already has the type asked for, as a
               truncation of i32 to i32) is named with "(no instruction)",
               read from the trace: no inserter ran inside it.

A step is a function entered or returned from, a branch taken, or an exit,
with its offset in traced_clang's binary, its depth below the part's first
frame, and its owner: the start of the function the step is in (for a
branch, the function whose code holds it; a function's first branch is
recorded just before its entry).
"""

import bisect
import re
import struct
from array import array
from typing import NamedTuple

from ....model_lang_parts.context.entry_context import Context
from .trace import KINDS, RECORD, REPORT_FUNCTION, START_FUNCTION, Trace

ACTION_PREFIX = "clang::Sema::ActOn"
MARKS = ("clang::Sema::ActOnParenExpr(", "clang::Sema::ActOnParenListExpr(", "clang::Sema::ActOnExprStmt(",
         "clang::Sema::ActOnExprStmtError(", "clang::Sema::ActOnCompoundStmt(")
LOWERING_MARK = re.compile(r"(^|::)(Scalar|Complex|Agg)ExprEmitter::VisitParenExpr\(")
EXIT = re.compile(r"(^|[ *&])llvm::(IRBuilderBase::(Create|Insert)\w*|IRBuilder<.*>::(Create|Insert)\w*"
                  r"|BasicBlock::Create|PHINode::addIncoming)(<.*>)?\(")
EXIT_NAME = re.compile(r"::((Create|Insert)\w*|addIncoming)(<.*>)?\(")
DIAGNOSTIC = REPORT_FUNCTION
# Every instruction a builder puts in a block passes through its inserter.
INSERTERS = ("clang::CodeGen::CGBuilderInserter::InsertHelper(", "llvm::IRBuilderDefaultInserter::InsertHelper(")
NO_INSTRUCTION = " (no instruction)"
DIAGNOSTIC_MACHINERY = re.compile(r"Diag(nostic)?Builder|::Diag\(|EmitDiagnostic|DiagnosticsEngine::|DiagnosticIDs::")
STEP = struct.Struct("<BQ")
KIND_CODE = {"separator": 0, "enter": 1, "return": 2, "branch": 3, "exit": 4}
KIND_OF_CODE = ("separator", "enter", "return", "branch", "exit")
# A record whose kind is none of path_recorder's: the hole that ends a
# record (trace.events_of).
NOT_A_KIND = re.compile(rb"[^\x01-\x03]")


class Step(NamedTuple):
    kind: str
    offset: int
    depth: int
    owner: int


# Each test of a function's name, answered once for every function of the
# binary: the offsets whose names pass it, keyed by the names' dict and the
# test. A trace holds hundreds of thousands of events from the function's
# start, and asking each one's name again took most of a context's time
# (run fable1_l61). Filled in the run's main process, before its workers are
# made, so every worker has them.
NAME_TESTS = {}


def offsets_passing(names: dict, test) -> set:
    key = (id(names), test.__name__)
    if key not in NAME_TESTS:
        passing = set()
        for offset, name in names.items():
            if test(name):
                passing.add(offset)
        NAME_TESTS[key] = passing
    found = NAME_TESTS[key]
    return found


def is_lowering_mark(name: str) -> bool:
    mark = LOWERING_MARK.search(name) is not None
    return mark


def is_inserter(name: str) -> bool:
    inserter = name.startswith(INSERTERS)
    return inserter


def is_start(name: str) -> bool:
    start = name.startswith(START_FUNCTION)
    return start


def is_report(name: str) -> bool:
    report = name.startswith(DIAGNOSTIC)
    return report


def answer_name_tests(names: dict) -> None:
    """Every test of a name, answered for the whole binary at once."""
    for test in (is_lowering_mark, is_mark, is_action, is_exit, is_inserter, is_start, is_report, is_constant_maker,
                 is_constant_last_resort, is_statement_action, is_statement_emitter):
        offsets_passing(names, test)


class Marks(NamedTuple):
    """The records the cut looks for in a record's bytes, each packed as
    path_recorder writes it: the entry of the standard form's function's
    start (every overload), and the entry of a diagnostic's report."""

    starts: tuple
    reports: tuple


class LogicalPath(NamedTuple):
    context: Context
    accepted: bool
    messages: str
    checking: tuple
    lowering: tuple
    exits: tuple


def depths_of(events: list) -> list:
    """Each event's depth: how many recorded frames are open around it."""
    depths = []
    depth = 0
    for kind, _offset in events:
        if kind == "enter":
            depths.append(depth)
            depth += 1
        elif kind == "return":
            if depth > 0:
                depth -= 1
            depths.append(depth)
        else:
            depths.append(depth)
    return depths


def matching_return(events: list, depths: list, start: int) -> int:
    """The index of the return that closes the frame entered at `start`, or
    the last index when the run ended inside it."""
    depth = depths[start]
    offset = events[start][1]
    for index in range(start + 1, len(events)):
        kind, value = events[index]
        if kind == "return" and depths[index] == depth and value == offset:
            return index
    last = len(events) - 1
    return last


def lowering_bounds(events: list, depths: list, names: dict):
    """(start, end) of the first VisitParenExpr of clang's emitters, or None
    when there is no lowering (clang refused)."""
    marks = offsets_passing(names, is_lowering_mark)
    for index in range(len(events)):
        kind, offset = events[index]
        if kind == "enter" and offset in marks:
            end = matching_return(events, depths, index)
            bounds = (index, end)
            return bounds
    return None


def is_mark(name: str) -> bool:
    for mark in MARKS:
        if name.startswith(mark):
            return True
    return False


def is_action(name: str) -> bool:
    action = name.startswith(ACTION_PREFIX) and not is_mark(name)
    return action


def checking_bounds(events: list, depths: list, names: dict):
    """(start, end) of the HiOp's own action: the last `Sema::ActOn...` at
    depth 0 before the first mark at depth 0."""
    marks = offsets_passing(names, is_mark)
    actions = offsets_passing(names, is_action)
    mark = len(events)
    for index in range(len(events)):
        kind, offset = events[index]
        if kind == "enter" and depths[index] == 0 and offset in marks:
            mark = index
            break
    action = -1
    for index in range(mark):
        kind, offset = events[index]
        if kind == "enter" and depths[index] == 0 and offset in actions:
            action = index
    if action < 0:
        return None
    end = matching_return(events, depths, action)
    bounds = (action, end)
    return bounds


# A statement HiOp (IfStmt, ForStmt, ReturnStmt, ...) is written as a
# statement in the function's body, never inside the expression the marks
# bound, so its checking action is Sema's statement action and its lowering
# is CodeGenFunction's statement emitter (log 487 §24; the owner, 2026-10-19:
# "24 have no exit? are those actually HiOps if they literally have no
# exit?").
STATEMENT_ACTION = re.compile(r"^clang::Sema::ActOn\w*Stmt\(")
NOT_A_STATEMENT_ACTION = ("clang::Sema::ActOnExprStmt(", "clang::Sema::ActOnExprStmtError(",
                          "clang::Sema::ActOnCompoundStmt(", "clang::Sema::ActOnStartOfCompoundStmt(",
                          "clang::Sema::ActOnFinishOfCompoundStmt(")
# EmitCompoundStmtWithoutScope emits the function's own body; the HiOp `{ a; }`
# inside it is emitted by EmitCompoundStmt, which is its emitter (run l121:
# CompoundStmt's three forms had no lowering while every EmitCompoundStmt was left out).
STATEMENT_EMITTER = re.compile(r"^clang::CodeGen::CodeGenFunction::Emit(?!Stmt\(|SimpleStmt\(|CompoundStmtWithoutScope)\w*Stmt\(")


# A captured statement (`#pragma clang __debug captured`, OpenMP's regions) is
# finished by ActOnCapturedRegionEnd, not by an ActOn*Stmt (run l125: its
# checking part was empty).
CAPTURED_ACTION = "clang::Sema::ActOnCapturedRegionEnd("


def is_statement_action(name: str) -> bool:
    action = STATEMENT_ACTION.match(name) is not None and not name.startswith(NOT_A_STATEMENT_ACTION)
    if name.startswith(CAPTURED_ACTION):
        action = True
    return action


def is_statement_emitter(name: str) -> bool:
    emitter = STATEMENT_EMITTER.match(name) is not None
    return emitter


def is_statement_operator(context) -> bool:
    kind = context.operator.name.split(".")[0].split(" ")[0]
    statement = kind.endswith("Stmt") or kind.endswith("Directive")
    return statement


def statement_checking_bounds(events: list, depths: list, names: dict):
    """(start, end) of the last statement action at depth 0: the HiOp's own,
    after the actions of the inert calls in its parts."""
    actions = offsets_passing(names, is_statement_action)
    action = -1
    for index in range(len(events)):
        kind, offset = events[index]
        if kind == "enter" and depths[index] == 0 and offset in actions:
            action = index
    if action < 0:
        return None
    end = matching_return(events, depths, action)
    bounds = (action, end)
    return bounds


def statement_lowering_bounds(events: list, depths: list, names: dict):
    """(start, end) of the first statement emitter entered, or None."""
    emitters = offsets_passing(names, is_statement_emitter)
    for index in range(len(events)):
        kind, offset = events[index]
        if kind == "enter" and offset in emitters:
            end = matching_return(events, depths, index)
            bounds = (index, end)
            return bounds
    return None


def is_exit(name: str) -> bool:
    exit = name.startswith(DIAGNOSTIC) or EXIT.search(name) is not None
    return exit


def short_function(name: str) -> str:
    """`clang::Sema::InvalidOperands` for its full signature."""
    text = name.replace("(anonymous namespace)", "{anonymous}")
    short = text.split("(", 1)[0]
    return short


def issuer_of(frames: list, names: dict) -> str:
    """The function of clang's that issued a diagnostic: the innermost open
    frame that is not the diagnostic's own machinery."""
    position = len(frames) - 1
    while position >= 0:
        name = names.get(frames[position], "")
        if not DIAGNOSTIC_MACHINERY.search(name):
            issuer = short_function(name)
            return issuer
        position -= 1
    return "?"


def exit_name(name: str, frames: list, names: dict) -> str:
    """`CreateNSWAdd` for `llvm::IRBuilderBase::CreateNSWAdd(...)`;
    `Diagnostic from clang::Sema::InvalidOperands` for a diagnostic."""
    if name.startswith(DIAGNOSTIC):
        named = "Diagnostic from " + issuer_of(frames, names)
        return named
    found = EXIT_NAME.search(name)
    if found is None:
        return name
    short = found.group(1)
    if "llvm::BasicBlock::" in name:
        short = "BasicBlock::" + short
    return short


def owner_of(offset: int, starts: list) -> int:
    """The start of the function whose code holds `offset` (`starts` is every
    function's start, sorted)."""
    index = bisect.bisect_right(starts, offset) - 1
    if index < 0:
        return 0
    owner = starts[index]
    return owner


def inserts(events: list, names: dict, first: int, last: int) -> bool:
    """Whether an inserter ran between an exit's entry and its return."""
    inserters = offsets_passing(names, is_inserter)
    for index in range(first + 1, last):
        kind, offset = events[index]
        if kind == "enter" and offset in inserters:
            return True
    return False


def steps_of(events: list, depths: list, names: dict, starts: list, bounds) -> tuple:
    """The steps from bounds' start to its end, and the exits among them."""
    steps = []
    exits = []
    if bounds is None:
        found = (tuple(steps), tuple(exits))
        return found
    start, end = bounds
    base = depths[start]
    exits_of_binary = offsets_passing(names, is_exit)
    frames = []
    index = start
    while index <= end:
        kind, offset = events[index]
        depth = depths[index] - base
        if kind == "enter" and offset in exits_of_binary:
            steps.append(Step("exit", offset, depth, offset))
            named = exit_name(names.get(offset, ""), frames, names)
            last = matching_return(events, depths, index)
            if named.startswith("Create") and not inserts(events, names, index, last):
                named = named + NO_INSTRUCTION
            exits.append(named)
            index = last + 1
            continue
        if kind == "enter":
            frames.append(offset)
        elif kind == "return" and frames and frames[-1] == offset:
            frames.pop()
        owner = offset
        if kind == "branch":
            owner = owner_of(offset, starts)
        steps.append(Step(kind, offset, depth, owner))
        index += 1
    found = (tuple(steps), tuple(exits))
    return found


def function_start(events: list, names: dict) -> int:
    """The index of the standard form's function's start in the record, or
    the record's length when clang never reached it."""
    starts = offsets_passing(names, is_start)
    for index in range(len(events)):
        kind, offset = events[index]
        if kind == "enter" and offset in starts:
            return index
    length = len(events)
    return length


def diagnostics_before(events: list, names: dict, end: int) -> tuple:
    """The diagnostics clang reported before `end`, each named by its
    issuer: a refusal in the struct's own line."""
    found = diagnostics_between(events, names, 0, end, " (before the function)")
    return found


def diagnostics_between(events: list, names: dict, start: int, end: int, label: str) -> tuple:
    """The diagnostics clang reported at events[start:end], each named by
    its issuer and labelled with where it fell. The frames are followed from
    the record's start, so the issuer is right wherever `start` is."""
    reports = offsets_passing(names, is_report)
    frames = []
    exits = []
    for index in range(end):
        kind, offset = events[index]
        if kind == "enter":
            if offset in reports and index >= start:
                exits.append(exit_name(names.get(offset, ""), frames, names) + label)
            frames.append(offset)
        elif kind == "return" and frames and frames[-1] == offset:
            frames.pop()
    found = tuple(exits)
    return found


def diagnostics_outside_the_cut(events: list, names: dict, checking, lowering) -> tuple:
    """The diagnostics reported inside the function but outside the cut's
    two parts: before the checking action (the callee's own name looked up,
    `call to undeclared library function 'acos'`), between the two parts,
    and after the lowering. Runs fable1_l10 to l98 held 365 operators refused
    with such a diagnostic and no diagnostic exit on the path (log 487 §21).
    Before the first part they are labelled "(before the action)", after it
    "(after the action)"."""
    first_bound = len(events)
    if checking is not None:
        first_bound = checking[0]
    elif lowering is not None:
        first_bound = lowering[0]
    before = diagnostics_between(events, names, 0, first_bound, " (before the action)")
    after = ()
    if checking is not None:
        after_start = checking[1] + 1
        lowering_start = len(events)
        lowering_end = len(events)
        if lowering is not None:
            lowering_start = lowering[0]
            lowering_end = lowering[1] + 1
        between = diagnostics_between(events, names, after_start, min(lowering_start, len(events)), " (after the action)")
        later = diagnostics_between(events, names, min(lowering_end, len(events)), len(events), " (after the lowering)")
        after = between + later
    found = before + after
    return found


def marks_of(names: dict) -> Marks:
    starts = []
    for offset, name in names.items():
        if name.startswith(START_FUNCTION):
            starts.append(RECORD.pack(1, offset))
    reports = []
    for offset, name in names.items():
        if name.startswith(DIAGNOSTIC):
            reports.append(RECORD.pack(1, offset))
    marks = Marks(tuple(starts), tuple(reports))
    return marks


def usable_records(data: bytes) -> int:
    """How many whole records the bytes hold before the first hole."""
    whole = len(data) // RECORD.size
    kinds = data[0:whole * RECORD.size:RECORD.size]
    hole = NOT_A_KIND.search(kinds)
    if hole is None:
        return whole
    count = hole.start()
    return count


def aligned_find(data: bytes, record: bytes, end: int) -> int:
    """The index of the first whole record among the first `end` that equals
    `record`, or `end`."""
    limit = end * RECORD.size
    position = data.find(record, 0, limit)
    while position >= 0:
        if position % RECORD.size == 0:
            index = position // RECORD.size
            return index
        position = data.find(record, position + 1, limit)
    return end


def first_record(data: bytes, wanted: tuple, end: int) -> int:
    """The index of the first record among the first `end` that is one of
    `wanted`, or `end` when none is."""
    first = end
    for record in wanted:
        index = aligned_find(data, record, end)
        if index < first:
            first = index
    return first


def events_between(data: bytes, first: int, last: int) -> list:
    events = []
    for kind, offset in RECORD.iter_unpack(data[first * RECORD.size:last * RECORD.size]):
        events.append((KINDS[kind], offset))
    return events


def cut_record(data: bytes, accepted: bool, messages: str, names: dict, marks: Marks) -> Trace:
    """The trace from the standard form's function's start, cut from the
    record's bytes before they are read as events: the same events, early
    exits and count as reading the whole record and cutting it in
    from_trace, without reading the millions of events before the function
    (the struct, the typedefs, the builtins' declarations). The events
    before the function are read only when a diagnostic's report is among
    them."""
    total = usable_records(data)
    first = first_record(data, marks.starts, total)
    early_exits = ()
    if first_record(data, marks.reports, first) < first:
        early_exits = diagnostics_in_bytes(data, first, names)
    events = events_between(data, first, total)
    found = Trace(events, accepted, messages, early_exits, total)
    return found


def diagnostics_in_bytes(data: bytes, end: int, names: dict) -> tuple:
    """diagnostics_before over the first `end` records, read in one pass
    over the bytes: the same diagnostics, each named by its issuer, without
    making the millions of events first."""
    reports = offsets_passing(names, is_report)
    frames = []
    exits = []
    for kind, offset in RECORD.iter_unpack(data[:end * RECORD.size]):
        if kind == 1:
            if offset in reports:
                exits.append(exit_name(names.get(offset, ""), frames, names) + " (before the function)")
            frames.append(offset)
        elif kind == 2 and frames and frames[-1] == offset:
            frames.pop()
    found = tuple(exits)
    return found


def from_trace(context: Context, found, names: dict, starts: list) -> LogicalPath:
    """The HiOp's path in one trace (trace.Trace); `starts` is every
    function's start in the binary, sorted. The record may begin before the
    function (with the struct): the cut starts at the function, and a
    diagnostic before it is an exit of the path. A trace from cut_record
    begins at the function already, and carries those diagnostics."""
    first = function_start(found.events, names)
    early_exits = found.early_exits + diagnostics_before(found.events, names, first)
    events = found.events[first:]
    depths = depths_of(events)
    lowering = lowering_bounds(events, depths, names)
    checking = checking_bounds(events, depths, names)
    if is_statement_operator(context):
        lowering = statement_lowering_bounds(events, depths, names)
        checking = statement_checking_bounds(events, depths, names)
    checking_steps, checking_exits = steps_of(events, depths, names, starts, checking)
    lowering_steps, lowering_exits = steps_of(events, depths, names, starts, lowering)
    outside = diagnostics_outside_the_cut(events, names, checking, lowering)
    if found.accepted and lowering is not None and not lowering_exits:
        lowering_exits = constant_exits(events, names, lowering)
    path = LogicalPath(context, found.accepted, found.messages, checking_steps, lowering_steps,
                       early_exits + outside + checking_exits + lowering_exits)
    return path


# Where clang makes a value without LLVM's IR builder: it folds the HiOp to
# a constant (sizeof, alignof, __builtin_inf, __builtin_classify_type, the
# type traits; log 487 §21: 215 operators). The path's exit is then the
# function that made the constant, named here by its prefix; the builtins
# that hand LLVM a constant from inside EmitBuiltinExpr (ConstantFP::get is
# LLVM's, unrecorded) name EmitBuiltinExpr itself.
CONSTANT_MAKERS = ("clang::Expr::EvaluateKnownConstInt(", "clang::Expr::EvaluateAsRValue(", "clang::Expr::EvaluateAsInt(",
                   "clang::Expr::EvaluateAsFloat(", "clang::Expr::EvaluateAsConstantExpr(",
                   "clang::Expr::EvaluateAsBooleanCondition(", "clang::CodeGen::ConstantEmitter::",
                   "clang::CodeGen::CodeGenFunction::ConstantFoldsToSimpleInteger(")
CONSTANT_LAST_RESORT = ("clang::CodeGen::CodeGenFunction::EmitBuiltinExpr(",)
CONSTANT_EXIT = "Constant from "


def is_constant_maker(name: str) -> bool:
    maker = name.startswith(CONSTANT_MAKERS)
    return maker


def is_constant_last_resort(name: str) -> bool:
    maker = name.startswith(CONSTANT_LAST_RESORT)
    return maker


def constant_exits(events: list, names: dict, bounds) -> tuple:
    """The exits of a lowered path that called nothing of the IR builder:
    the constant makers it entered, each once; EmitBuiltinExpr alone when
    no other maker was entered; else one exit saying the value was made
    without the builder."""
    makers = offsets_passing(names, is_constant_maker)
    last_resort = offsets_passing(names, is_constant_last_resort)
    exits = []
    fallback = []
    start, end = bounds
    for index in range(start, end + 1):
        kind, offset = events[index]
        if kind != "enter":
            continue
        if offset in makers:
            named = CONSTANT_EXIT + short_function(names.get(offset, ""))
            if named not in exits:
                exits.append(named)
        elif offset in last_resort:
            named = CONSTANT_EXIT + short_function(names.get(offset, ""))
            if named not in fallback:
                fallback.append(named)
    if not exits:
        exits = fallback
    if not exits:
        exits = [CONSTANT_EXIT + "the lowering, without the IR builder"]
    found = tuple(exits)
    return found


class Steps:
    """A path's steps packed, as a worker hands them to the run's main
    process: one record a step in the signature's form (kind code and
    offset, STEP), and the steps' kind codes, offsets, depths and owners as
    arrays. A lowering holds a median of 223,707 steps; handing them over
    one object at a time held the main process at full use while the
    workers waited (run fable1_l63). It reads as a sequence of Step."""

    __slots__ = ("packed", "kinds", "offsets", "depths", "owners")

    def __init__(self, packed: bytes, kinds: bytes, offsets: array, depths: array, owners: array):
        self.packed = packed
        self.kinds = kinds
        self.offsets = offsets
        self.depths = depths
        self.owners = owners

    def __len__(self) -> int:
        length = len(self.kinds)
        return length

    def __getitem__(self, index: int) -> Step:
        step = Step(KIND_OF_CODE[self.kinds[index]], self.offsets[index], self.depths[index], self.owners[index])
        return step

    def __iter__(self):
        for index in range(len(self.kinds)):
            yield self[index]


def packed_steps(steps) -> Steps:
    packed = []
    kinds = bytearray()
    offsets = array("Q")
    depths = array("q")
    owners = array("Q")
    for step in steps:
        code = KIND_CODE[step.kind]
        packed.append(STEP.pack(code, step.offset))
        kinds.append(code)
        offsets.append(step.offset)
        depths.append(step.depth)
        owners.append(step.owner)
    found = Steps(b"".join(packed), bytes(kinds), offsets, depths, owners)
    return found


def packed_path(path: LogicalPath) -> LogicalPath:
    """The path with its steps packed, to be handed to the main process."""
    packed = path._replace(checking=packed_steps(path.checking), lowering=packed_steps(path.lowering))
    return packed


SEPARATOR_STEPS = packed_steps((Step("separator", 0, 0, 0),))


def step_columns(path: LogicalPath) -> Steps:
    """The path's steps in order, packed: checking, a separator, lowering
    (all_steps, without making a Step for each)."""
    checking = path.checking
    lowering = path.lowering
    if not isinstance(checking, Steps):
        checking = packed_steps(checking)
    if not isinstance(lowering, Steps):
        lowering = packed_steps(lowering)
    packed = checking.packed + SEPARATOR_STEPS.packed + lowering.packed
    kinds = checking.kinds + SEPARATOR_STEPS.kinds + lowering.kinds
    offsets = checking.offsets + SEPARATOR_STEPS.offsets + lowering.offsets
    depths = checking.depths + SEPARATOR_STEPS.depths + lowering.depths
    owners = checking.owners + SEPARATOR_STEPS.owners + lowering.owners
    joined = Steps(packed, kinds, offsets, depths, owners)
    return joined


def all_steps(path: LogicalPath) -> list:
    """The path's steps in order: checking, a separator, lowering."""
    steps = list(path.checking)
    steps.append(Step("separator", 0, 0, 0))
    for step in path.lowering:
        steps.append(step)
    return steps


def signature(path: LogicalPath) -> bytes:
    """What two paths are compared by: their steps, packed."""
    if isinstance(path.checking, Steps) and isinstance(path.lowering, Steps):
        packed = path.checking.packed + SEPARATOR_STEPS.packed + path.lowering.packed
        return packed
    parts = []
    for step in all_steps(path):
        parts.append(STEP.pack(KIND_CODE[step.kind], step.offset))
    packed = b"".join(parts)
    return packed
