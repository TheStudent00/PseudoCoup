"""clang -- how clang's own source answers operator_reader's three per-lowerer
parts. c and cpp both use it: clang lowers both, from the same lists.

    operator_list        clang's own lists of operator names, each where the
                         write-back code takes a name from it:
                         - an enum whose entries the code writes by spelling,
                           through getOpcodeStr or getTraitSpelling. Which enum
                           is read from clang's headers: the parameter's type
                           (BinaryOperator::getOpcodeStr(Opcode Op), and Opcode
                           is BinaryOperatorKind), or the argument's
                           (getTraitSpelling(Node->getKind()), and
                           UnaryExprOrTypeTraitExpr::getKind returns
                           UnaryExprOrTypeTrait);
                         - an enum a getter of the node returns, which the code
                           switches on or compares (AtomicExpr::getOp returns
                           AtomicOp).
                         The enum's own lines say which file lists its entries
                         and how: `#define BINARY_OPERATION(Name, Spelling)
                         BO_##Name,`. A kind holds only the entries its own
                         constructors let it hold: `a *= b` is a
                         CompoundAssignOperator, never a BinaryOperator
                         (held_entries).
                         And the builtins: the name a call calls is one of
                         them, clang keeps it on every call
                         (CallExpr::getBuiltinCallee, Expr.h), and entry 0 is
                         the ordinary call. No type leads from the call to
                         those lists, so the link is written down here (CALLEE
                         below). clang's build makes the lists with
                         clang-tblgen, and so does this reader (made_list).
    expression_kinds     include/clang/Basic/StmtNodes.td declares every kind
                         of expression, `def ConditionalOperator : StmtNode<...>;`
    write_back_as_text   lib/AST/StmtPrinter.cpp writes each kind back out as
                         source text, `void StmtPrinter::VisitConditionalOperator`.
                         Its code is read with tree-sitter (cpp_code.py) and
                         walked (ways.py); the table below says what its calls
                         and writes mean.

The clang we compile with is 21.1.8, so these are 21.1.8's files. Paths are
relative to that checkout's root; where the checkouts live, and where
clang-tblgen and clang are, is configuration.
"""

import functools
import os
import re
import shlex
import subprocess
from typing import NamedTuple

from ... import declaring_file_path
from .cpp_code import NODE, read_functions
from .source_text import read_function_body, split_outside_literals
from .ways import Entry, Table, chosen_entry, ways_of

CHECKOUT = "llvm-project-21.1.8"
STMT_NODES = "clang/include/clang/Basic/StmtNodes.td"
PRINTER = "clang/lib/AST/StmtPrinter.cpp"
EXPR = "clang/include/clang/AST/Expr.h"
EXPR_CXX = "clang/include/clang/AST/ExprCXX.h"
OPERATIONS_ENUM = "clang/include/clang/AST/OperationKinds.h"
TRAITS_ENUM = "clang/include/clang/Basic/TypeTraits.h"
EXPRESSION_TRAITS_ENUM = "clang/include/clang/Basic/ExpressionTraits.h"
OPERATIONS = "clang/include/clang/AST/OperationKinds.def"
TOKENS = "clang/include/clang/Basic/TokenKinds.def"
CASTS = "clang/lib/AST/ExprCXX.cpp"
CONSTRUCTORS = "clang/lib/AST/Expr.cpp"
BUILTINS_HEADER = "clang/include/clang/Basic/Builtins.h"
TARGET_BUILTINS_HEADER = "clang/include/clang/Basic/TargetBuiltins.h"
BUILTINS_TD = "clang/include/clang/Basic/Builtins.td"
BUILTINS_BASE_TD = "clang/include/clang/Basic/BuiltinsBase.td"
BUILTINS_RISCV_TD = "clang/include/clang/Basic/BuiltinsRISCV.td"
BUILTINS_RISCV_XCV_TD = "clang/include/clang/Basic/BuiltinsRISCVXCV.td"
BUILTIN_HEADERS = "clang/include/clang/Basic/BuiltinHeaders.def"
# Where clang declares the classes of its expressions, and the enums whose
# entries its write-back code writes.
CLASS_HEADERS = (EXPR, EXPR_CXX)
ENUM_HEADERS = (OPERATIONS_ENUM, TRAITS_ENUM, EXPRESSION_TRAITS_ENUM)
FILES = (STMT_NODES, PRINTER) + CLASS_HEADERS + ENUM_HEADERS + (
    OPERATIONS, TOKENS, CASTS, CONSTRUCTORS, BUILTINS_HEADER, TARGET_BUILTINS_HEADER, BUILTINS_TD,
    BUILTINS_BASE_TD, BUILTINS_RISCV_TD, BUILTINS_RISCV_XCV_TD, BUILTIN_HEADERS)
# The `#include` in an enum names its listing relative to this folder.
INCLUDE_ROOT = "clang/include"

# The class whose functions write each kind back out: Visit<Kind> per kind.
PRINTER_CLASS = "StmtPrinter"

# A kind whose code has more ways than this for one choice of list entries
# is left out, with the reason.
WAY_LIMIT = 256

# What clang's write-back code means (the walker's Table, built by
# table_for below):
#
#     OS << x << y                   writes x, then y
#     PrintExpr(x), Visit(x)         an operand, for any x but the node itself
#     <type>.print(OS, Policy)       a type: a call whose name ends in Type
#                                    (getType, getTypeAsWritten,
#                                    getArgumentType), or a variable declared
#                                    QualType or as the result of such a call
#     <x>.printName(OS, Policy)      a name
#     OS << x->getName() and kin     a name (NAME_GETTER)
#     OS << Node->getCastName()      the kind's own cast name, from ExprCXX.cpp
#     getOpcodeStr(x),               the spelling of the entry x holds, from
#     getTraitSpelling(x)            the enum x's type names (SPELLING_CALLS)
#     Node->getOp() and kin          the entry the node holds, of the enum the
#                                    getter returns (getter_list)
#     Visit<Other>(Node),            the same node handed to another of the
#     PrintCallArgs(Node)            class's functions: followed
#     Node->isPostfix()              decided by the opcode the way chose,
#                                    from UnaryOperator::isPostfix in Expr.h
#     Node->isCmpXChg() and kin      decided by the entry the way chose, from
#                                    the test's own definition (method_labels)
#     PrintExpr(Node->getCallee())   in the kind whose own class declares
#                                    getBuiltinCallee (CallExpr): the name of
#                                    the builtin the way chose, or an operand
#                                    for entry 0, the ordinary call
#     i != Node->getNumArgs()        a loop that turns once per operand of the
#                                    builtin the way chose; for a count with
#                                    no end, that many and up to REPEATS more
#     Indent() << x, NL              indentation and a line break: spaces
#     PrintStmt(x), PrintStmt(x, n)  a statement slot, filled with one
#                                    expression statement over an operand:
#                                    `a;` (so every operand is a value)
#     dyn_cast<S>(x), isa<S>(x)      no, for a statement kind S: the slot
#                                    holds that one expression statement
#     Helper(x), a function of the   followed, whether x is the node or a
#     class                          statement inside it
WRITER = "OS"
INDENT = "Indent"
INDENT_LEVEL = "IndentLevel"
PART = "a statement inside the node"
FP_PRAGMAS = "Node->hasStoredFPFeatures()"
ASSERT = "assert"
# What `assert(...)` is once clang's own preprocessor has read the file, with
# NDEBUG as clang's release build has it: glibc's assert.h writes it
# `(__ASSERT_VOID_CAST (0))`, and `__ASSERT_VOID_CAST` is `static_cast<void>`
# in C++. A cast to void writes nothing, as the assert did. (Since 2026-10-16
# the readers read the preprocessed files; run elv2_l176 found the 101 forms
# of the printers that assert first, CompoundStmt's among them, unread.)
VOID_CAST = "static_cast<void>"
NEWLINE = "NL"
STATEMENT_CALL = "PrintStmt"
STATEMENT_TEST = re.compile(r"^(?:dyn_cast|dyn_cast_or_null|isa|isa_and_nonnull)<(\w+)>\(")
OPERAND_CALLS = ("PrintExpr", "Visit")
PRINT_ARGUMENTS = ("OS", "Policy")
SPELLING_CALLS = ("getOpcodeStr", "getTraitSpelling")
QUAL_TYPE = "QualType"
TYPE_GETTER = re.compile(r"Type\w*\(\)$")
DECLARED_AS = re.compile(r"^decltype\((.*)\)$")
NAME_GETTER = re.compile(r"(getMemberNameInfo|getNameInfo|getName|deuglifiedName)\(\)$")
THE_NODE = re.compile(rf"^(?:cast<[\w:]+>\()?{NODE}\)?$")
CAST_NAME = f"{NODE}->getCastName()"
POSTFIX = f"{NODE}->isPostfix()"
OPCODE = f"{NODE}->getOpcode()"

# A call writes its callee as an operand (StmtPrinter::VisitCallExpr), but
# clang keeps on every call "the builtin ID of the callee", 0 when it is not
# a builtin (CallExpr::getBuiltinCallee, Expr.h). That ID is an entry of
# clang's builtin lists: the enum Builtin::ID (Builtins.h), and, for the
# target we compile for, RISC-V's (namespace RISCV in TargetBuiltins.h). The
# getter's type is a plain unsigned, so no type in the header leads to the
# lists: this one link is written down here.
CALLEE = f"{NODE}->getCallee()"
BUILTIN_GETTER = "getBuiltinCallee"
BUILTIN_CALLEE = f"{NODE}->{BUILTIN_GETTER}()"
BUILTIN_ENUM = "Builtin::ID"
ARGUMENT_COUNT = f"{NODE}->getNumArgs()"

# The builtin lists a call can name, for the target we compile for (RISC-V):
# (the file clang's build makes the list from, the namespace of its
# enumerators, the name clang's code #includes the made list by). Line 88
# and line 108 of clang/include/clang/Basic/CMakeLists.txt make them.
BUILTIN_LISTS = (
    (BUILTINS_TD, "Builtin", "clang/Basic/Builtins.inc"),
    (BUILTINS_RISCV_TD, "RISCV", "clang/Basic/BuiltinsRISCV.inc"),
)

# Calls clang never keeps as calls: its checking code replaces each with an
# expression of another kind, read under that kind instead. Every builtin its
# list makes with ATOMIC_BUILTIN becomes an AtomicExpr
# (clang/lib/Sema/SemaChecking.cpp lines 2723-2726), and
# __builtin_shufflevector a ShuffleVectorExpr (lines 2515-2516).
ATOMIC_MACRO = "ATOMIC_BUILTIN"
REPLACED_CALLS = ("BI__builtin_shufflevector",)

# clang's own list-writer, the program clang's build runs to make its builtin
# lists. Configuration: found on PATH by default.
CLANG_TABLEGEN_VARIABLE = "PSEUDOARCH_CLANG_TABLEGEN"
DEFAULT_CLANG_TABLEGEN = "clang-tblgen"

# The clang that answers how many operands a builtin takes when no list says.
# Configuration: found on PATH by default.
COMPILER_VARIABLE = "PSEUDOARCH_CLANG"
DEFAULT_COMPILER = "clang"
ASK_TARGET = "riscv64-unknown-linux-gnu"
ASK_LANGUAGES = (("c", "c17"), ("c++", "c++20"))
# A builtin is asked once with no operand and once with this many.
ASK_OPERANDS = 9
# clang has its matrix builtins only with its matrix extension on
# (SemaChecking.cpp, BuiltinMatrixColumnMajorLoad: err_builtin_matrix_disabled).
ASK_FLAGS = ("-fenable-matrix",)
# A library builtin is asked with the header its own list names included; the
# image's C library headers for riscv64 sit at /usr/riscv64-linux-gnu.
HEADER_TARGET = ("--target=riscv64-linux-gnu", "--gcc-toolchain=/usr")
CLANG_HEADER = re.compile(r'^HEADER\((\w+),\s*"([^"]+)"\)', re.M)

# The attribute letter of a builtin whose prototype clang does not check,
# checking its calls with its own code instead: "t -> signature is
# meaningless, use custom typechecking" (Builtins.def).
MEANINGLESS_SIGNATURE = "t"
# clang's type letters (Builtins.def; read by DecodeTypeFromStr in
# clang/lib/AST/ASTContext.cpp, lines 12285-12620): letters before a type
# change it, one letter names it, and letters after it make it a pointer, a
# reference, or qualify it.
TYPE_PREFIXES = "ISULNWZO"
TYPE_LETTERS = "xyvhfdsicbzwFGHMaAYPJKpm"
TYPE_SUFFIXES = "*&CDR"

CLANG_STMT_NODE = re.compile(r"^\s*def\s+(\w+)\s*:\s*StmtNode<\s*(\w+)\s*(,\s*1)?\s*>")
CLANG_CLASS = r"^class\s+{name}\b[^;{{]*\{{"
CLANG_ANY_CLASS = re.compile(r"^class\s+(\w+)\b[^;{]*\{", re.M)
CLANG_ENUM = r"^\s*enum\s+{name}\s*\{{"
CLANG_BLOCK_END = re.compile(r"^};", re.M)
CLANG_INNER_BLOCK_END = re.compile(r"^\s*};", re.M)
CLANG_GETTER = r"^\s*(?:const\s+)?(\w+)\s+{getter}\(\)\s*const\b"
CLANG_PARAMETER = r"\b{method}\(\s*(\w+)\s+\w+\s*\)"
CLANG_TYPEDEF = r"\btypedef\s+(\w+)\s+{name}\s*;|\busing\s+{name}\s*=\s*(\w+)\s*;"
CLANG_ENUM_MACRO = re.compile(r"^#define\s+(\w+)\(([^)]*)\)\s+(\w+?)\s*##\s*(\w+)\b", re.M)
CLANG_INCLUDE = re.compile(r'^#include\s+"([^"]+)"', re.M)
CLANG_LISTED = r"^{macro}\((.*)\)\s*$"
CLANG_POSTFIX_START = "static bool isPostfix(Opcode Op) {"
CLANG_POSTFIX_OPCODE = re.compile(r"\bUO_(\w+)\b")
CLANG_CAST_NAME_START = "const char *CXXNamedCastExpr::getCastName() const {"
CLANG_CAST_NAME = re.compile(r'case\s+(\w+)Class:\s*return\s+"([^"]+)";')
CLANG_ASSERT = re.compile(r"assert\(\s*(!?)(is\w+)\(\)\s*&&")
MADE_SECTION = r"^#ifdef {name}\n(.*?)^#endif"
MADE_ENUMERATOR = re.compile(r"^\s+(BI\w+),$", re.M)
MADE_INFO = re.compile(r"StrOffsets\{\d+(?: /\* (.*?) \*/)?, \d+(?: /\* (.*?) \*/)?, \d+(?: /\* (.*?) \*/)?,[^}]*\}, HeaderDesc::(\w+)")
CLANG_ERROR = re.compile(r"^<stdin>:(\d+):\d+: (?:fatal )?error: (.*)$")
ANY_ERROR = re.compile(r"^(?:[^:\s]+):\d+:\d+: (?:fatal )?error: (.*)$")
UNDECLARED = re.compile(r"use of undeclared identifier|call to undeclared (library )?function")
TOO_FEW = re.compile(r"too few arguments to function call, (?:expected (at least )?(\d+)|(single) argument|(at least) argument)")
TOO_MANY = re.compile(r"too many arguments to function call, expected (at most )?(?:(\d+)|single argument)")


class Builtin(NamedTuple):
    """One builtin, as clang-tblgen lists it."""

    enumerator: str   # clang's name for it: BI__builtin_popcount
    type: str         # its type letters: iUi, an int result and an unsigned operand
    attributes: str   # its attribute letters: nc
    header: str = ""  # the C library header that declares it: PTHREAD_H, or NO_HEADER


def operator_list() -> dict:
    """enum -> its entries, for every list clang's write-back code takes a
    name from, in the order the kinds first reach them."""
    functions = printer_functions()
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    lists = {}
    for kind, _declared_at in expression_kinds():
        owner = printer_owner(kind, nodes, functions)
        if owner is None:
            continue
        pending = [functions[f"{PRINTER_CLASS}::Visit{owner}"].body]
        while pending:
            code = pending.pop()
            if code.form == "call":
                callee, arguments = code.parts
                if len(arguments) == 1:
                    if is_builtin_callee(kind, callee.text, arguments[0].text):
                        lists.setdefault(BUILTIN_ENUM, callee_entries())
                    found = list_for(kind, callee.text, arguments[0].text)
                    if found is not None:
                        lists.setdefault(found[0], enum_entries(found[0]))
                if not arguments and callee.form == "member" and callee.parts[0].text == NODE:
                    found = getter_list(kind, callee.parts[1])
                    if found is not None:
                        lists.setdefault(found[0], enum_entries(found[0]))
            for part in code.parts:
                pending.extend(codes_in(part))
    return lists


def codes_in(part) -> list:
    if hasattr(part, "form"):
        return [part]
    if isinstance(part, tuple):
        found = []
        for inner in part:
            found.extend(codes_in(inner))
        return found
    return []


def expression_kinds() -> tuple:
    """(kind, where clang declares it) for every concrete kind in
    StmtNodes.td, statements and expressions both, in clang's order (Dee,
    2026-09-30: statements are HiOps). An abstract kind is never built on its
    own, so it is not listed. The name still says expressions: renaming it
    waits for Dee's word."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    kinds = []
    for kind, (_base, is_abstract, line_number) in nodes.items():
        if is_abstract:
            continue
        kinds.append((kind, f"{STMT_NODES}:{line_number}"))
    listed = tuple(kinds)
    return listed


@functools.lru_cache(maxsize=None)
def is_statement_kind(kind: str) -> bool:
    """Whether `kind` is one of clang's statement kinds, not an expression."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    found = kind in nodes and "Expr" not in chain_of(kind, nodes)
    return found


def write_back_as_text(kind: str) -> tuple:
    """(ways, reason, where) for one kind: every way clang's code for writing
    that kind back out as source text can run, no reason, and where that
    code is; or no ways and the reason.

    A way's pieces are ("text", s), ("operand",), ("type",), ("name",). A way
    that met a call or a write the table does not know has stopped, and its
    `reason` says at what."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    functions = printer_functions()
    owner = printer_owner(kind, nodes, functions)
    if owner is None:
        return (), f"clang has no code that writes it back out ({PRINTER_CLASS}::Visit{kind} or above)", None
    function = functions[f"{PRINTER_CLASS}::Visit{owner}"]
    ways, reason = ways_of(function.body, table_for(kind, functions), WAY_LIMIT)
    found = (ways, reason, f"{PRINTER}:{function.line}")
    return found


def declares_no_operand(kind: str, way) -> bool:
    """Whether a way with no operand, or with only names, is still an
    operator: a statement (`break;`, `goto m;`), or a call to a builtin whose
    own type letters or clang's own errors say it takes none
    (`__builtin_trap()`). A value or a name with none is not."""
    if is_statement_kind(kind):
        return True
    entry = chosen_entry(way, BUILTIN_CALLEE)
    if entry is None or not entry.spelling:
        return False
    counted = builtin_operand_counts().get(entry.name)
    declared = counted is not None and counted[0] == 0
    return declared


def table_for(kind: str, functions: dict) -> Table:
    """The walker's Table for clang's code, while it writes `kind`."""

    def follow(code):
        """The body of the class's own function a call hands the node, or a
        statement inside it, to: defined outside the class
        (`StmtPrinter::PrintRawIfStmt`) or inside it (`PrintControlledStmt`)."""
        if code.form != "call":
            return None
        callee, arguments = code.parts
        if callee.form != "name" or not arguments:
            return None
        name = callee.parts[0]
        function = functions.get(f"{PRINTER_CLASS}::{name}") or functions.get(name)
        return function.body if function is not None else None

    def statement(code, way):
        items = written_items(code)
        if items is not None:
            return (("write", items),)
        if is_indent(code) or code.text.startswith(INDENT_LEVEL):
            return (("write", ()),)
        if code.form != "call":
            return None
        callee, arguments = code.parts
        if callee.form == "name" and callee.parts[0] == ASSERT:
            return (("write", ()),)
        if callee.text.replace(" ", "") == VOID_CAST:
            return (("write", ()),)
        if callee.form == "name" and callee.parts[0] == STATEMENT_CALL and arguments:
            # Inside a helper (PrintControlledStmt(S)), the statement it was
            # handed is read as the node: still one statement slot. clang
            # indents it and ends its line.
            return (("piece", ("text", " ")), ("piece", ("operand",)), ("piece", ("text", "; ")))
        handed_a_part = dict(way.types).get(NODE) == PART
        if (callee.form == "name" and callee.parts[0] in OPERAND_CALLS and len(arguments) == 1
                and (not THE_NODE.match(arguments[0].text) or handed_a_part)):
            if is_builtin_callee(kind, callee.text, arguments[0].text):
                entry = chosen_entry(way, BUILTIN_CALLEE)
                if entry is not None and entry.spelling:
                    return (("piece", ("text", entry.spelling)),)
            return (("piece", ("operand",)),)
        if callee.form == "member" and tuple(argument.text for argument in arguments) == PRINT_ARGUMENTS:
            receiver, method = callee.parts
            if method == "print" and is_type(receiver, way):
                return (("piece", ("type",)),)
            if method == "printName":
                return (("piece", ("name",)),)
            return None
        followed = follow(code)
        if followed is not None:
            # Handed a statement inside the node, the helper reads that
            # statement as `Node`: marked, so its PrintExpr(Node) is an operand.
            if not THE_NODE.match(arguments[0].text) or handed_a_part:
                return (("follow", followed, ((NODE, PART),)),)
            return (("follow", followed),)
        return None

    def item(code, way):
        if code.form == "name" and code.parts[0] == NEWLINE:
            return ("text", " ")
        if code.form == "call" and NAME_GETTER.search(code.text):
            return ("name",)
        if code.text == CAST_NAME and kind in cast_names():
            return ("text", cast_names()[kind])
        return None

    def lookup(code):
        if code.form != "call":
            return None
        callee, arguments = code.parts
        if not arguments and callee.form == "member" and callee.parts[0].text == NODE:
            found = getter_list(kind, callee.parts[1])
            return (code.text, found[1]) if found is not None else None
        if len(arguments) != 1:
            return None
        if is_builtin_callee(kind, callee.text, arguments[0].text):
            return (BUILTIN_CALLEE, callee_entries())
        found = list_for(kind, callee.text, arguments[0].text)
        if found is None:
            return None
        return (arguments[0].text, found[1])

    def decide(code, way):
        tested = STATEMENT_TEST.match(code.text)
        if tested is not None and is_statement_kind(tested.group(1)):
            return False
        if code.text == FP_PRAGMAS:
            # A compound's `#pragma STDC FENV_ACCESS` and kin are not read yet.
            return False
        if code.text == POSTFIX:
            entry = chosen_entry(way, OPCODE)
            if entry is None:
                return None
            return entry.name in postfix_operators()
        if code.form == "call" and not code.parts[1] and code.parts[0].form == "member":
            receiver, method = code.parts[0].parts
            found = method_labels(kind, method) if receiver.text == NODE else None
            if found is not None:
                entry = chosen_entry(way, f"{NODE}->{found[0]}()")
                if entry is None:
                    return None
                return entry.label.split("::")[-1] in found[1]
        return None

    def turns(code, way):
        if code.text != ARGUMENT_COUNT:
            return None
        entry = chosen_entry(way, BUILTIN_CALLEE)
        if entry is None:
            return None
        counted = builtin_operand_counts().get(entry.name)
        return counted

    table = Table(statement, item, lookup, decide, follow, turns)
    return table


def is_builtin_callee(kind: str, callee: str, argument: str) -> bool:
    """Whether `callee(argument)`, in the code that writes `kind`, writes the
    callee of a call whose own class declares getBuiltinCallee: CallExpr.
    The kinds below it (a member call, an operator call, a CUDA kernel call,
    a user-defined literal) inherit the getter, not the link."""
    if callee not in OPERAND_CALLS or argument != CALLEE:
        return False
    body = class_body(kind)
    declared = body is not None and re.search(CLANG_GETTER.format(getter=BUILTIN_GETTER), body, re.M) is not None
    return declared


def written_items(code):
    """(x, y) for `OS << x << y` or `Indent() << x << y`, else None."""
    items = []
    current = code
    while current.form == "binary" and current.parts[0] == "<<":
        items.append(current.parts[2])
        current = current.parts[1]
    if items and (current.form == "name" and current.parts[0] == WRITER or is_indent(current)):
        return tuple(reversed(items))
    return None


def is_indent(code) -> bool:
    """Whether `code` is `Indent()` or `Indent(n)`: spaces, then the stream."""
    found = code.form == "call" and code.parts[0].form == "name" and code.parts[0].parts[0] == INDENT
    return found


def is_type(receiver, way) -> bool:
    """Whether `receiver.print(OS, Policy)` writes a type."""
    if receiver.form == "call" and TYPE_GETTER.search(receiver.text):
        return True
    if receiver.form == "name":
        declared = dict(way.types).get(receiver.parts[0], "")
        if declared == QUAL_TYPE:
            return True
        as_value = DECLARED_AS.match(declared)
        if as_value is not None and TYPE_GETTER.search(as_value.group(1)):
            return True
    return False


@functools.lru_cache(maxsize=None)
def list_for(kind: str, callee: str, argument: str):
    """(enum, entries) when `callee(argument)`, in the code that writes
    `kind`, writes the spelling of an enum's entry; else None. The enum is
    the parameter's type for a class's own function (`BinaryOperator::
    getOpcodeStr(Opcode Op)`), else the type of the argument's getter on the
    kind's class or a class above it (`UnaryExprOrTypeTrait getKind()`).
    The entries are those `kind` can hold (held_entries)."""
    method = callee.split("::")[-1]
    if method not in SPELLING_CALLS:
        return None
    if "::" in callee:
        owner = callee.rsplit("::", 1)[0]
        enum = member_type((owner,), CLANG_PARAMETER.format(method=re.escape(method)))
    else:
        getter = re.fullmatch(rf"{NODE}->(\w+)\(\)", argument)
        if getter is None:
            return None
        nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
        enum = member_type(tuple(chain_of(kind, nodes)), CLANG_GETTER.format(getter=re.escape(getter.group(1))))
    if enum is None:
        return None
    entries = enum_entries(enum)
    if entries is None:
        return None
    return (enum, held_entries(kind, entries))


@functools.lru_cache(maxsize=None)
def getter_list(kind: str, getter: str):
    """(enum, entries) when `Node->getter()`, in the code that writes
    `kind`, returns an entry of one of clang's lists: the getter's type, on
    the kind's class or a class above it, is an enum whose entries can be
    read (`AtomicOp getOp() const`). Else None."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    enum = member_type(tuple(chain_of(kind, nodes)), CLANG_GETTER.format(getter=re.escape(getter)))
    if enum is None:
        return None
    entries = enum_entries(enum)
    if entries is None:
        return None
    return (enum, held_entries(kind, entries))


def held_entries(kind: str, entries: tuple) -> tuple:
    """The entries `kind` can hold: all of them, unless a constructor of its
    own class asserts a test of the entry, and then those the test lets
    through. BinaryOperator's asserts `!isCompoundAssignmentOp()`
    (clang/lib/AST/Expr.cpp line 4856) and CompoundAssignOperator's
    `isCompoundAssignmentOp()` (Expr.h line 4245), so `a *= b` is only ever
    a CompoundAssignOperator and `a * b` only ever a BinaryOperator."""
    kept = entries
    for negated, method in constructor_asserts(kind):
        passing = predicate_entries(kind, method, entries)
        if passing is None:
            continue
        kept = tuple(entry for entry in kept if (entry in passing) != negated)
    return kept


@functools.lru_cache(maxsize=None)
def constructor_asserts(kind: str) -> tuple:
    """(negated, test) for each `assert(isX() && ...)` or `assert(!isX() &&
    ...)` in a constructor that builds `kind`: one whose initializer names
    `<kind>Class`, or, naming none, one of `kind`'s own class. So
    BinaryOperator's second constructor, which builds
    `CompoundAssignOperatorClass` (Expr.cpp line 4873), counts for
    CompoundAssignOperator and not for BinaryOperator. Read for the kind and
    every class above it."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    found = []
    for owner in chain_of(kind, nodes):
        for initializer, body in constructors(owner):
            built = re.findall(r"\b(\w+)Class\b", initializer)
            if (kind in built) if built else (owner == kind):
                found.extend((negated == "!", method) for negated, method in CLANG_ASSERT.findall(body))
    return tuple(found)


@functools.lru_cache(maxsize=None)
def constructors(owner: str) -> tuple:
    """(initializer, body) of each constructor of class `owner` that has a
    body: those written in the class (Expr.h, ExprCXX.h), and those written
    outside it (Expr.cpp)."""
    found = []
    body = class_body(owner)
    if body is not None:
        found.extend(re.findall(rf"^\s*{owner}\([^;{{]*?\)\s*(:[^{{]*)?\{{(.*?)^\s*\}}", body, re.M | re.S))
    found.extend(re.findall(rf"^{owner}::{owner}\([^{{]*?\)\s*(:[^{{]*)?\{{(.*?)^\}}", header_text(CONSTRUCTORS),
                            re.M | re.S))
    return tuple(found)


def predicate_entries(kind: str, method: str, entries: tuple):
    """The entries for which clang's test `method` is true, the test read
    from its definition in `kind`'s class or a class above it, when it
    compares the entry against entries of the same list and nothing else:
    `static bool isCompoundAssignmentOp(Opcode Opc) { return Opc > BO_Assign
    && Opc <= BO_OrAssign; }` (Expr.h line 4107). None for another shape."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    order = {entry.label: index for index, entry in enumerate(entries)}
    for owner in chain_of(kind, nodes):
        body = class_body(owner)
        if body is None:
            continue
        found = re.search(rf"static bool {re.escape(method)}\(\s*\w+\s+(\w+)\s*\)\s*\{{\s*return\s+([^;]*);\s*\}}", body)
        if found is None:
            continue
        variable, test = found.groups()
        passing = []
        for index, entry in enumerate(entries):
            outcome = order_test(test, variable, index, order)
            if outcome is None:
                return None
            if outcome:
                passing.append(entry)
        return tuple(passing)
    return None


def order_test(test: str, variable: str, index: int, order: dict):
    """`test` for the entry at `index` of its list: comparisons of
    `variable` against entries, by their place in the list, joined by `&&`
    and `||`. None when a part is anything else."""
    compared = {"==": int.__eq__, "!=": int.__ne__, "<": int.__lt__, "<=": int.__le__, ">": int.__gt__,
                ">=": int.__ge__}
    alternatives = []
    for alternative in test.split("||"):
        outcomes = []
        for term in alternative.split("&&"):
            found = re.fullmatch(rf"\s*{re.escape(variable)}\s*(==|!=|<=|>=|<|>)\s*(\w+)\s*", term)
            if found is None or found.group(2) not in order:
                return None
            outcomes.append(compared[found.group(1)](index, order[found.group(2)]))
        alternatives.append(all(outcomes))
    return any(alternatives)


def member_type(classes: tuple, pattern: str):
    """The type `pattern` captures in the first of `classes` that declares
    it, through any typedef those classes declare for it; else None."""
    for owner in classes:
        body = class_body(owner)
        if body is None:
            continue
        found = re.search(pattern, body, re.M)
        if found is None:
            continue
        named = found.group(1)
        for aliasing in classes:
            aliasing_body = class_body(aliasing)
            if aliasing_body is None:
                continue
            alias = re.search(CLANG_TYPEDEF.format(name=re.escape(named)), aliasing_body)
            if alias is not None:
                return alias.group(1) or alias.group(2)
        return named
    return None


@functools.lru_cache(maxsize=None)
def class_body(name: str):
    """The text of clang's declaration of class `name`, or None."""
    for header in CLASS_HEADERS:
        text = header_text(header)
        found = re.search(CLANG_CLASS.format(name=re.escape(name)), text, re.M)
        if found is None:
            continue
        end = CLANG_BLOCK_END.search(text, found.end())
        return text[found.start(): end.end() if end is not None else len(text)]
    return None


@functools.lru_cache(maxsize=None)
def enum_entries(enum: str):
    """The entries of clang's enum `enum`, read from the list its own lines
    #include, with the shape its own #defines give; or None. The enum may
    stand alone (OperationKinds.h) or inside a class (AtomicExpr's AtomicOp,
    Expr.h), and the list may be one clang's build makes (Builtins.inc)."""
    for header in ENUM_HEADERS + CLASS_HEADERS:
        text = header_text(header)
        found = re.search(CLANG_ENUM.format(name=re.escape(enum)), text, re.M)
        if found is None:
            continue
        end = CLANG_INNER_BLOCK_END.search(text, found.end())
        block = text[found.end(): end.start() if end is not None else len(text)]
        shapes = {}
        for macro, parameters, prefix, pasted in CLANG_ENUM_MACRO.findall(block):
            names = tuple(parameter.strip() for parameter in parameters.split(","))
            shapes.setdefault(macro, (names, prefix, pasted))
        includes = CLANG_INCLUDE.findall(block)
        if not shapes or not includes:
            return None
        owner = enclosing_class(text, found.start())
        return read_listed(includes[0], tuple(shapes.items()), f"{owner}::" if owner else "")
    return None


def enclosing_class(text: str, position: int):
    """The class whose declaration holds `position` in a header, or None
    when it stands outside every class."""
    owner = None
    for found in CLANG_ANY_CLASS.finditer(text, 0, position):
        if CLANG_BLOCK_END.search(text, found.end(), position) is None:
            owner = found.group(1)
    return owner


@functools.lru_cache(maxsize=None)
def header_text(relative: str) -> str:
    with open(declaring_file_path(CHECKOUT, relative), encoding="utf-8") as header_file:
        text = header_file.read()
    return text


@functools.lru_cache(maxsize=None)
def read_listed(included: str, shapes: tuple, qualifier: str = "") -> tuple:
    """Every entry the #included list gives through the macros in `shapes`,
    in its order. `shapes` is ((macro, (parameter names, label prefix, the
    parameter pasted after it)), ...). An entry's name is its Name argument
    when the macro has one, else its label; its spelling is its Spelling
    argument when there is one, else the pasted argument; its label is how
    clang's code names it, inside `qualifier` when the enum sits in a class."""
    text, where = listed_text(included)
    entries = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for macro, (parameters, prefix, pasted) in shapes:
            found = re.match(CLANG_LISTED.format(macro=re.escape(macro)), line)
            if found is None:
                continue
            arguments = split_outside_literals(found.group(1), ",")
            value = arguments[parameters.index(pasted)]
            label = f"{prefix}{value}"
            name = arguments[parameters.index("Name")] if "Name" in parameters else label
            spelling = arguments[parameters.index("Spelling")].strip('"') if "Spelling" in parameters else value
            entries.append(Entry(name, spelling, f"{qualifier}{label}", f"{where}:{line_number}"))
    return tuple(entries)


def listed_text(included: str) -> tuple:
    """(text, where) of a list clang's code #includes: a file of the
    checkout, or one its build makes (made_includes)."""
    made = dict(made_includes())
    if included in made:
        made_from = next(td for td, _namespace, included_as in BUILTIN_LISTS if included_as == included)
        return made[included], f"{included}, made from {made_from}"
    relative = f"{INCLUDE_ROOT}/{included}"
    return header_text(relative), relative


@functools.lru_cache(maxsize=None)
def postfix_operators() -> frozenset:
    """The unary operators that go after their operand, from
    UnaryOperator::isPostfix in Expr.h."""
    body, _line = read_function_body(CHECKOUT, EXPR, CLANG_POSTFIX_START)
    found = frozenset(CLANG_POSTFIX_OPCODE.findall(body))
    return found


@functools.lru_cache(maxsize=None)
def method_labels(kind: str, method: str):
    """(getter, labels) when `kind`'s class, or one above it, defines
    `bool method() const { return getter() == L1 || getter() == L2 ...; }`:
    the test true exactly for those entries (AtomicExpr::isCmpXChg, Expr.h
    line 6892). Else None."""
    nodes = read_clang_stmt_nodes(CHECKOUT, STMT_NODES)
    for owner in chain_of(kind, nodes):
        body = class_body(owner)
        if body is None:
            continue
        found = re.search(rf"\bbool\s+{re.escape(method)}\(\)\s*const\s*\{{\s*return\s+([^;]*);\s*\}}", body)
        if found is None:
            continue
        test = found.group(1)
        pairs = re.findall(r"(\w+)\(\)\s*==\s*(\w+)", test)
        getters = {getter for getter, _label in pairs}
        if len(getters) != 1 or len(pairs) != test.count("==") or re.search(r"&&|!=", test):
            return None
        return (getters.pop(), frozenset(label for _getter, label in pairs))
    return None


@functools.lru_cache(maxsize=None)
def cast_names() -> dict:
    """kind -> the name a program writes for that cast (`static_cast` ...),
    from CXXNamedCastExpr::getCastName in ExprCXX.cpp."""
    body, _line = read_function_body(CHECKOUT, CASTS, CLANG_CAST_NAME_START)
    found = dict(CLANG_CAST_NAME.findall(body))
    return found


def printer_functions() -> dict:
    """clang's write-back functions, with the lists its build makes given
    for a switch whose cases a macro writes over one (AtomicExpr)."""
    found = read_functions(CHECKOUT, PRINTER, made_includes())
    return found


@functools.lru_cache(maxsize=None)
def made_includes() -> tuple:
    """((the name clang's code #includes a made list by, its text), ...)."""
    made = tuple((included_as, made_list(td)) for td, _namespace, included_as in BUILTIN_LISTS)
    return made


@functools.lru_cache(maxsize=None)
def made_list(td: str) -> str:
    """The list clang's build makes from `td` with clang-tblgen
    -gen-clang-builtins (clang/include/clang/Basic/CMakeLists.txt lines 88
    and 108): the same program, run on the same file."""
    path = declaring_file_path(CHECKOUT, td)
    include_root = path[: -len(td)] + INCLUDE_ROOT
    tablegen = os.environ.get(CLANG_TABLEGEN_VARIABLE, DEFAULT_CLANG_TABLEGEN)
    command = shlex.split(tablegen) + ["-gen-clang-builtins", "-I", include_root, path]
    finished = subprocess.run(command, capture_output=True, text=True, check=False)
    if finished.returncode != 0:
        message = f"clang: clang-tblgen refused {td}: {finished.stderr[:400]}"
        raise RuntimeError(message)
    return finished.stdout


@functools.lru_cache(maxsize=None)
def made_builtins(td: str) -> tuple:
    """Every builtin the list made from `td` holds, in clang's order: each
    enumerator, with its type letters and attribute letters."""
    text = made_list(td)
    enumerators = MADE_ENUMERATOR.findall(made_section(text, "GET_BUILTIN_ENUMERATORS"))
    infos = (MADE_INFO.findall(made_section(text, "GET_BUILTIN_INFOS"))
             + MADE_INFO.findall(made_section(text, "GET_BUILTIN_PREFIXED_INFOS")))
    if len(enumerators) != len(infos):
        message = f"clang: {td}'s list has {len(enumerators)} enumerators but {len(infos)} infos"
        raise ValueError(message)
    builtins = tuple(Builtin(enumerator, type_letters or "", attributes or "", header)
                     for enumerator, (_name, type_letters, attributes, header) in zip(enumerators, infos))
    return builtins


def made_section(text: str, name: str) -> str:
    found = re.search(MADE_SECTION.format(name=name), text, re.M | re.S)
    return found.group(1) if found is not None else ""


@functools.lru_cache(maxsize=None)
def builtin_list() -> tuple:
    """The builtins a call can name, as clang numbers them: entry 0,
    NotBuiltin (Builtins.h: "This is not a builtin function"), then clang's
    own list and RISC-V's, each as clang-tblgen makes it. An Entry's name is
    clang's enumerator (BI__builtin_popcount); its spelling is the name a
    program calls; its label is how clang's code names it in a case
    (Builtin::BI__builtin_popcount, RISCV::BI__builtin_riscv_orc_b_32)."""
    not_builtin, line = first_enumerator(BUILTINS_HEADER, BUILTIN_ENUM.split("::")[-1])
    entries = [Entry(not_builtin, "", f"Builtin::{not_builtin}", f"{BUILTINS_HEADER}:{line}")]
    for td, namespace, _included_as in BUILTIN_LISTS:
        for builtin in made_builtins(td):
            entries.append(Entry(builtin.enumerator, builtin.enumerator[len("BI"):],
                                 f"{namespace}::{builtin.enumerator}", f"{td}, as clang-tblgen lists it"))
    listed = tuple(entries)
    return listed


@functools.lru_cache(maxsize=None)
def callee_entries() -> tuple:
    """builtin_list, less the builtins clang never keeps as calls."""
    replaced = replaced_calls()
    kept = tuple(entry for entry in builtin_list() if entry.name not in replaced)
    return kept


@functools.lru_cache(maxsize=None)
def replaced_calls() -> frozenset:
    """The builtins clang never keeps as a call (REPLACED_CALLS): every one
    its list makes with ATOMIC_BUILTIN, and __builtin_shufflevector."""
    atomic = re.findall(rf"^{ATOMIC_MACRO}\((\w+),", made_list(BUILTINS_TD), re.M)
    replaced = frozenset(f"BI{name}" for name in atomic) | frozenset(REPLACED_CALLS)
    return replaced


@functools.lru_cache(maxsize=None)
def builtin_operand_counts() -> dict:
    """enumerator -> (fewest, most) operands, most None when there is no
    end, for every builtin a call can name. From the builtin's type letters:
    the first type is the result, each after it an operand, a last `.` means
    more may follow. Where clang calls the letters meaningless, or gives
    none, from clang's own errors when asked (asked_operand_counts). A
    builtin neither answers is not in it."""
    counts = {}
    unanswered = []
    for td, _namespace, _included_as in BUILTIN_LISTS:
        for builtin in made_builtins(td):
            if builtin.type and MEANINGLESS_SIGNATURE not in builtin.attributes:
                fixed, more_may_follow = type_letter_operands(builtin.type)
                counts[builtin.enumerator] = (fixed, None if more_may_follow else fixed)
            else:
                unanswered.append(builtin.enumerator)
    asked = asked_operand_counts(tuple(enumerator[len("BI"):] for enumerator in unanswered))
    for enumerator in unanswered:
        if enumerator[len("BI"):] in asked:
            counts[enumerator] = asked[enumerator[len("BI"):]]
    return counts


def type_letter_operands(letters: str) -> tuple:
    """(fixed operands, whether more may follow) of a builtin's type
    letters, `iUi`: read one type at a time, as DecodeTypeFromStr and
    GetBuiltinType do (ASTContext.cpp lines 12285-12700)."""
    position = one_type(letters, 0, True)
    count = 0
    while position < len(letters) and letters[position] != ".":
        position = one_type(letters, position, True)
        count += 1
    more_may_follow = position < len(letters) and letters[position] == "."
    return (count, more_may_follow)


def one_type(letters: str, position: int, suffixes: bool) -> int:
    """Where the type that starts at `position` ends."""
    while letters[position] in TYPE_PREFIXES:
        position += 1
    letter = letters[position]
    position += 1
    if letter in "qVE":
        while letters[position].isdigit():
            position += 1
        position = one_type(letters, position, False)
    elif letter == "X":
        position = one_type(letters, position, False)
    elif letter == "Q":
        position += 1
    elif letter not in TYPE_LETTERS:
        message = f"clang: type letter {letter!r} in {letters!r} is none clang reads"
        raise ValueError(message)
    while suffixes and position < len(letters) and letters[position] in TYPE_SUFFIXES:
        pointer = letters[position] in "*&"
        position += 1
        while pointer and position < len(letters) and letters[position].isdigit():
            position += 1
    return position


@functools.lru_cache(maxsize=None)
def asked_operand_counts(names: tuple) -> dict:
    """name -> (fewest, most or None), as clang's own errors state them, for
    builtins no list gives a count for. Each is called once with no operand
    and once with ASK_OPERANDS, each call in a function of its own, first as
    C, then as C++ for those C does not have. "too few arguments to function
    call, expected 3, have 0" gives the fewest; "too many arguments to
    function call, expected at most 3, have 9" the most. A call with no
    operand that clang takes without an error has 0 fewest, and one with
    ASK_OPERANDS no most. A builtin whose first call clang refuses for
    another reason is left out."""
    answered = {}
    remaining = list(names)
    for language, standard in ASK_LANGUAGES:
        if not remaining:
            break
        none = compile_errors(tuple(f"{name}()" for name in remaining), language, standard)
        many = compile_errors(tuple(f"{name}({', '.join(['0'] * ASK_OPERANDS)})" for name in remaining),
                              language, standard)
        unknown = []
        for index, name in enumerate(remaining):
            refused = none.get(index, ())
            if any(UNDECLARED.search(error) for error in refused):
                unknown.append(name)
                continue
            counted = counted_operands(refused, many.get(index, ()))
            if counted is not None:
                answered[name] = counted
        remaining = unknown
    # A library builtin clang declares only once its header is included
    # (pthread_create, from pthread.h) is asked again, as C, with that header.
    headers = builtin_headers()
    declared_in = {builtin.enumerator[len("BI"):]: headers.get(builtin.header)
                   for td, _namespace, _included_as in BUILTIN_LISTS for builtin in made_builtins(td)}
    for name in names:
        header = declared_in.get(name)
        if name in answered or header is None:
            continue
        language, standard = ASK_LANGUAGES[0]
        none = compile_errors((f"{name}()",), language, standard, (header,), HEADER_TARGET)
        many = compile_errors((f"{name}({', '.join(['0'] * ASK_OPERANDS)})",), language, standard, (header,),
                              HEADER_TARGET)
        if -1 in none or -1 in many:
            continue
        counted = counted_operands(none.get(0, ()), many.get(0, ()))
        if counted is not None:
            answered[name] = counted
    return answered


@functools.lru_cache(maxsize=None)
def builtin_headers() -> dict:
    """HeaderDesc name -> the header clang says declares it, from
    BuiltinHeaders.def: PTHREAD_H -> pthread.h. NO_HEADER names none."""
    path = declaring_file_path(CHECKOUT, BUILTIN_HEADERS)
    with open(path, encoding="utf-8") as listing:
        found = dict(CLANG_HEADER.findall(listing.read()))
    return found


def counted_operands(with_none: tuple, with_many: tuple):
    """(fewest, most or None) from clang's errors at a call with no operand
    and at one with ASK_OPERANDS; None when the first says nothing of the
    count yet refuses the call."""
    fewest = 0 if not with_none else None
    most = None
    for error in with_none:
        found = TOO_FEW.search(error)
        if found is None:
            continue
        at_least, number, single, at_least_one = found.groups()
        fewest = 1 if (single or at_least_one) else int(number)
        if single or (number and not at_least):
            most = fewest
    if fewest is None:
        return None
    if most is None:
        for error in with_many:
            found = TOO_MANY.search(error)
            if found is not None:
                most = int(found.group(2)) if found.group(2) else 1
    return (fewest, most)


def compile_errors(calls: tuple, language: str, standard: str, headers: tuple = (), target: tuple = None) -> dict:
    """index -> the errors clang gives at `calls[index]`, each call compiled
    in a function of its own, for the target we compile for, after
    `#include`-ing `headers`."""
    compiler = os.environ.get(COMPILER_VARIABLE, DEFAULT_COMPILER)
    included = "".join(f"#include <{header}>\n" for header in headers)
    source = included + "".join(f"void asked_{index}(void) {{ {call}; }}\n" for index, call in enumerate(calls))
    aimed = list(target) if target is not None else [f"--target={ASK_TARGET}"]
    command = (shlex.split(compiler) + ["-fsyntax-only", "-ferror-limit=0"] + aimed + list(ASK_FLAGS)
               + ["-x", language, f"-std={standard}", "-"])
    finished = subprocess.run(command, input=source, capture_output=True, text=True, check=False)
    errors = {}
    for line in finished.stderr.splitlines():
        found = CLANG_ERROR.match(line)
        if found is None and ANY_ERROR.match(line):
            # An error inside an included header: filed under -1 too.
            errors.setdefault(-1, []).append(ANY_ERROR.match(line).group(1))
            continue
        if found is not None:
            # An error on an `#include` line, like a header not found, is filed
            # under -1: no call's count may be read past it.
            index = max(int(found.group(1)) - 1 - len(headers), -1)
            errors.setdefault(index, []).append(found.group(2))
    return {index: tuple(found) for index, found in errors.items()}


def first_enumerator(relative: str, enum: str) -> tuple:
    """(name, line) of the first entry of `enum` in the header `relative`."""
    text = header_text(relative)
    found = re.search(CLANG_ENUM.format(name=re.escape(enum)), text, re.M)
    if found is None:
        message = f"clang: no enum {enum} in {relative}"
        raise LookupError(message)
    first = re.compile(r"^\s*(\w+)\s*(?:=[^,]*)?,", re.M).search(text, found.end())
    line = text.count("\n", 0, first.start(1)) + 1
    return (first.group(1), line)


@functools.lru_cache(maxsize=None)
def read_clang_stmt_nodes(checkout: str, relative: str) -> dict:
    """kind -> (base, is abstract, line), every node StmtNodes.td declares."""
    path = declaring_file_path(checkout, relative)
    nodes = {}
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            match = CLANG_STMT_NODE.match(line)
            if match is None:
                continue
            is_abstract = match.group(3) is not None
            nodes[match.group(1)] = (match.group(2), is_abstract, line_number)
    return nodes


def chain_of(kind: str, nodes: dict) -> list:
    """The kind and every kind above it, nearest first."""
    chain = []
    current = kind
    while current in nodes:
        chain.append(current)
        current = nodes[current][0]
    chain.append(current)
    return chain


def printer_owner(kind: str, nodes: dict, functions: dict):
    """The nearest kind at or above `kind` that has its own
    StmtPrinter::Visit function: the one clang falls back to. None when no
    kind above it has one."""
    for candidate in chain_of(kind, nodes):
        if f"{PRINTER_CLASS}::Visit{candidate}" in functions:
            return candidate
    return None
