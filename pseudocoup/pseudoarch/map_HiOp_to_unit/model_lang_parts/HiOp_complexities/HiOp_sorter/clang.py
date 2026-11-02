"""clang -- how clang's own code answers HiOp_sorter's `definitions`, for c.

The code read is clang 21.1.8's lowering, `clang/lib/CodeGen`, compiled for
riscv64 with the optimizer off and the debug table on, one section per
function (run elv2_l65). In that object every function's relocation records
name each function it calls (`R_RISCV_CALL_PLT`) and each function whose
address it takes to hand on (`R_RISCV_PCREL_HI20`, `R_RISCV_GOT_HI20`), with
every macro already pasted in. The run writes one `<file>.refs.json` per
compiled file; where they are is configuration (COMPILED_VARIABLE).

Where an operator's lowering starts, clang decides in four dispatches:

    the visitors          ScalarExprEmitter, ComplexExprEmitter and
                          AggExprEmitter, one per kind of holder (a scalar, a
                          complex number, a struct or array); each one's
                          StmtVisitorBase::Visit calls VisitBin<entry> for a
                          binary operator, VisitUnary<entry> for a unary one,
                          and Visit<kind> for any other kind; a kind the
                          emitter has no function for goes through the
                          visitor's default to the nearest kind above it
                          (clang/include/clang/AST/StmtVisitor.h)
    the lvalue dispatch   CodeGenFunction::EmitLValueHelper, for an
                          expression used as a place: one function per kind,
                          named by the class it takes (EmitMemberExpr takes
                          a MemberExpr)
    the statements        CodeGenFunction::EmitStmt and EmitSimpleStmt: one
                          function per kind of statement, by the class it
                          takes (EmitIfStmt takes an IfStmt)

The names are the ones clang's macros form (StmtVisitor.h: `Bin##NAME`,
`Unary##NAME`, `Visit##CLASS`); for ScalarExprEmitter, run elv2_l55 read the
compiled switch and found each value at the function of that name, 33 of 33
binary and 14 of 14 unary.

A kind with an opcode (binary, compound assignment, unary) has its lvalue
function shared by all its entries, and inside it a switch on the opcode
that only a per-case reading separates, so for those kinds only the
visitors' per-entry starts are read.

Three kinds of operator are lowered as one case of a switch, not by a
function of their own: the builtins (CodeGenFunction::EmitBuiltinExpr, two
switches on the builtin's number), the atomic operations (EmitAtomicExpr and
EmitAtomicOp, on AtomicExpr::AtomicOp) and the conversions
(ScalarExprEmitter::VisitCastExpr, on CastKind). Each such operator starts in
the functions its case calls, read case by case from the compiled switch
(Research/extract_lang_vocabulary/HiOp_sorter/read_switch_cases.py, into
switches/cases.json), and the switch's own function is where the reading
stops, like a visitor. A builtin no case names is lowered as a call to its
library function, or by the target's builtins: no start here.
"""

import functools
import json
import os
import re

from ...HiOps.operator_reader import clang as clang_lists

# Where run elv2_l65 put the compiled reference graph: one
# `<file>.refs.json` per compiled file. Configuration.
COMPILED_VARIABLE = "PSEUDOARCH_COMPILED_CLANG"
FILES = ("CGExprScalar", "CGExprComplex", "CGExprAgg", "CGExpr", "CGStmt", "CGAtomic", "CGBuiltin")
CALL = "R_RISCV_CALL_PLT"
ADDRESS = ("R_RISCV_PCREL_HI20", "R_RISCV_GOT_HI20")

EMITTERS = ("ScalarExprEmitter", "ComplexExprEmitter", "AggExprEmitter")
VISITOR = "clang::StmtVisitorBase<std::add_pointer, (anonymous namespace)::{0}"
VISIT = ">::Visit(clang::Stmt*"
EMITTER_FUNCTION = re.compile(r"^\(anonymous namespace\)::(\w+)::Visit(\w+)\(")
VISITOR_DEFAULT = re.compile(r"^clang::StmtVisitorBase<.*>::Visit(\w+)\(")
# The emitter's catch-all, which reports an unsupported kind: no operator's start.
CATCH_ALL = ("Expr", "Stmt")
DISPATCHES = (
    "clang::CodeGen::CodeGenFunction::EmitLValueHelper(clang::Expr const*, clang::CodeGen::KnownNonNull_t)",
    "clang::CodeGen::CodeGenFunction::EmitStmt(clang::Stmt const*, llvm::ArrayRef<clang::Attr const*>)",
    "clang::CodeGen::CodeGenFunction::EmitSimpleStmt(clang::Stmt const*, llvm::ArrayRef<clang::Attr const*>)",
)
TAKES_CLASS = re.compile(r"^clang::CodeGen::CodeGenFunction::(Emit\w+)\(clang::(\w+) const[*&]")
# A parameter of clang's generic expression: the function evaluates whatever
# operator it is handed.
GENERIC_EXPRESSION = re.compile(r"[(,] ?clang::Expr (const)?\*")
OPCODE_KINDS = {"BinaryOperator": "Bin", "CompoundAssignOperator": "Bin", "UnaryOperator": "Unary"}
# kind -> (its group in cases.json, how the debug table names an entry)
CASE_KINDS = {"CallExpr": ("builtins", "{0}"), "AtomicExpr": ("atomics", "{0}"),
              "ImplicitCastExpr": ("casts", "CK_{0}")}
CASES = os.path.join("switches", "cases.json")
NOT_A_BUILTIN = "NotBuiltin"
# The switches' own functions: a definition read stops there.
SWITCH_FUNCTIONS = ("clang::CodeGen::CodeGenFunction::EmitBuiltinExpr(",
                    "clang::CodeGen::CodeGenFunction::EmitAtomicExpr(",
                    "EmitAtomicOp(",
                    "(anonymous namespace)::ScalarExprEmitter::VisitCastExpr(")
ABOVE_EVERY_KIND = ("Expr", "Stmt", "ValueStmt")


def compiled_directory() -> str:
    directory = os.environ.get(COMPILED_VARIABLE)
    if directory is None:
        message = f"{COMPILED_VARIABLE} is not set: it names the folder of clang's compiled reference graph"
        raise LookupError(message)
    return directory


# A function a file defines itself is bound `T` (global) or `t` (local to
# the file); a header's inline function, copied into each object that uses
# it, is weak (`W`, `V`). Run elv2_l69 read each object's bindings.
DEFINED_HERE = ("T", "t")


@functools.lru_cache(maxsize=None)
def read_own_code(directory: str) -> frozenset:
    """The functions the compiled lowering files define themselves."""
    own = set()
    for name in FILES:
        path = os.path.join(directory, f"{name}.symbols.json")
        if not os.path.isfile(path):
            message = f"HiOp_sorter: {path} is not on disk (run elv2_l69 makes it)"
            raise FileNotFoundError(message)
        with open(path, encoding="utf-8") as symbols:
            binding = json.load(symbols)["binding"]
        own |= {function for function, letter in binding.items() if letter in DEFINED_HERE}
    return frozenset(own)


@functools.lru_cache(maxsize=None)
def read_graph(directory: str) -> tuple:
    """(calls, handed): function -> the functions it calls, and the
    functions whose address it takes, from every compiled file's records."""
    calls, handed = {}, {}
    for name in FILES:
        path = os.path.join(directory, f"{name}.refs.json")
        if not os.path.isfile(path):
            message = f"HiOp_sorter: {path} is not on disk (run elv2_l65 makes it)"
            raise FileNotFoundError(message)
        with open(path, encoding="utf-8") as compiled:
            functions = json.load(compiled)["functions"]
        for function, record in functions.items():
            calls.setdefault(function, [])
            handed.setdefault(function, [])
            for kind, target in record["refs"]:
                if kind == CALL:
                    calls[function].append(target)
                elif kind in ADDRESS and "(" in target and not target.startswith("."):
                    handed[function].append(target)
    return calls, handed


def emitter_function(name: str, calls: dict, seen: tuple = ()):
    """The emitter's own function a visitor's call reaches: the call itself,
    or, for one of the visitor's defaults, the function it hands the node to."""
    if EMITTER_FUNCTION.match(name):
        return name
    if name in seen or name not in calls:
        return None
    for callee in calls[name]:
        found = emitter_function(callee, calls, seen + (name,))
        if found is not None:
            return found
    return None


def visited_starts(calls: dict) -> tuple:
    """(visited name -> the emitters' functions it starts at, the visitors
    and their defaults). The visited name is clang's: Bin<entry>,
    Unary<entry>, or a kind."""
    starts, dispatch = {}, set()
    for emitter in EMITTERS:
        prefix = VISITOR.format(emitter)
        visitor = next((f for f in calls if f.startswith(prefix) and VISIT in f), None)
        if visitor is None:
            message = f"HiOp_sorter: no visitor for {emitter} in the compiled graph"
            raise LookupError(message)
        dispatch.add(visitor)
        for callee in calls[visitor]:
            own, default = EMITTER_FUNCTION.match(callee), VISITOR_DEFAULT.match(callee)
            if own is None and default is None:
                continue
            visited = own.group(2) if own else default.group(1)
            if default:
                dispatch.add(callee)
            reached = emitter_function(callee, calls)
            if reached is None or EMITTER_FUNCTION.match(reached).group(2) in CATCH_ALL:
                continue
            starts.setdefault(visited, set()).add(reached)
    return starts, dispatch


def class_starts(calls: dict) -> dict:
    """class -> the functions the lvalue and statement dispatches hand that
    class to, by the class each function takes."""
    starts = {}
    for dispatch in DISPATCHES:
        for callee in calls.get(dispatch, ()):
            taken = TAKES_CLASS.match(callee)
            if taken and taken.group(2) not in ABOVE_EVERY_KIND:
                starts.setdefault(taken.group(2), set()).add(callee)
    return starts


@functools.lru_cache(maxsize=None)
def read_cases(directory: str) -> dict:
    path = os.path.join(directory, CASES)
    if not os.path.isfile(path):
        message = f"HiOp_sorter: {path} is not on disk (HiOp_sorter/read_switch_cases.py makes it)"
        raise FileNotFoundError(message)
    with open(path, encoding="utf-8") as cases:
        found = json.load(cases)
    return found


def starts_of(operator: str, visited: dict, by_class: dict, nodes: dict, cases: dict, calls: dict) -> set:
    """The functions where `operator`'s lowering starts. `Kind.Entry` is
    clang's own naming (vocabulary/c.json)."""
    kind, _, entry = operator.partition(".")
    if kind == "CallExpr" and entry == NOT_A_BUILTIN:
        # Builtin::ID's value 0: an ordinary call, which EmitCallExpr lowers
        # without the builtins' switch
        entry = ""
    if kind in CASE_KINDS and entry:
        group, named = CASE_KINDS[kind]
        called = cases.get(group, {}).get(named.format(entry), ())
        found = {function for function in called if function in calls}
        return found
    if kind in OPCODE_KINDS:
        found = set(visited.get(OPCODE_KINDS[kind] + entry, ()))
        return found
    found = set(visited.get(kind, ()))
    for above in clang_lists.chain_of(kind, nodes):
        if above in ABOVE_EVERY_KIND:
            break
        if above in by_class:
            found |= by_class[above]
            break
    return found


def definitions(operators: tuple):
    """HiOp_sorter.Definitions for clang: the compiled graph, each operator's
    starts, and where the code evaluates an operand."""
    from . import Definitions
    calls, handed = read_graph(compiled_directory())
    visited, dispatch = visited_starts(calls)
    by_class = class_starts(calls)
    nodes = clang_lists.read_clang_stmt_nodes(clang_lists.CHECKOUT, clang_lists.STMT_NODES)
    cases = read_cases(compiled_directory())
    starts = {operator: starts_of(operator, visited, by_class, nodes, cases, calls) for operator in operators}
    every_start = set().union(*visited.values(), *by_class.values())
    evaluators = {f for f in calls
                  if f not in every_start and "(" in f and GENERIC_EXPRESSION.search(f[f.index("("):])}
    switches = {f for f in calls if f.startswith(SWITCH_FUNCTIONS)}
    operand_evaluation = frozenset(dispatch | set(DISPATCHES) | evaluators | switches)
    # clang's macro writes each binary operator's start to call its own
    # operation: `VisitBin##OP` calls `Emit##OP` (CGExprScalar.cpp lines
    # 892-895) and, for complex numbers, `EmitBin##OP` (CGExprComplex.cpp
    # lines 343-349).
    paired = {}
    for operator, functions in starts.items():
        kind, _, entry = operator.partition(".")
        if OPCODE_KINDS.get(kind) != "Bin":
            continue
        for start in functions:
            emitter = EMITTER_FUNCTION.match(start)
            if emitter is None:
                continue
            for operation in (f"Emit{entry}(", f"EmitBin{entry}("):
                name = f"(anonymous namespace)::{emitter.group(1)}::{operation}"
                for callee in calls.get(start, ()):
                    if callee.startswith(name):
                        paired[callee] = operator
    own_code = read_own_code(compiled_directory())
    found = Definitions(calls, handed, starts, operand_evaluation, paired, own_code)
    return found
