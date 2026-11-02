"""standard_HiOp_wrapper -- the standard-form: one HiOp held in a function of its
own, whose holders are fields of a struct the caller owns.

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_held_HiOp_wrapper/`.

    lines = standard_HiOp_wrapper(lang, key, operator, spellings, routing)   # the standard function's lines
    lines = HiOp_on_its_own_line(lines)                                  # the HiOp on a line of its own

Moved here on 2026-10-13 from DRY_mask_maker , at Dee's word:
"okay lets move the tools into their places". The code is as it was there,
line for line, with three changes: the main function took the node's name
(it was `standard_cell_lines`); the routing is always handed by the caller, since
the routing is read by DRY_mask_maker (`ROUTING`), which uses this module; and
its error messages name this module. DRY_mask_maker keeps `standard_cell_lines`,
which hands it `ROUTING`, and every name below that other code reads through
it.
"""
import json
import os
import re
from typing import NamedTuple

from ..model_lang_parts import PLACEHOLDER, placeholders_of


class StandardSource(NamedTuple):
    """What standard_HiOp_wrapper hands on: the standard source's text, and the name
    of the standard function in it (its CORE's Block A, line 6). It was in
    lower_HiOp until this module was written (2026-10-13, ;
    lower_HiOp reads it from here."""

    text: str
    symbol: str


# How a field of the held struct is reached from the probe's pointer.
FIELD_ACCESS = {
    "c": "p->",
    "cpp": "p->",
    "go": "p.",
    "rust": "p.",
    "java": "p.",
}


# The types a C holder may be built from, declared once at the top of every
# held file: one instance of each kind of type clang's TypeNodes.td gives C
# that a spelling alone cannot name. `m` and `n` are the member names the
# standard form writes for a name placeholder (`a.m`, `__builtin_offsetof(T, m.n)`).
C_HELD_TYPES = [
    "struct S { int m; int n; };",
    "struct SN { struct S m; };",
    "struct SA { int m[4]; };",
    "union U { int m; double n; };",
    "struct I;",
    "enum E { E0, E1 };",
    "typedef int v4si __attribute__((vector_size(16)));",
    "typedef float v4sf __attribute__((vector_size(16)));",
    "typedef int (*fnptr)(int);",
    "typedef int arr4[4];",
    "typedef int (*arrptr)[4];",
    "typedef int fntype(int);",
    "typedef int ev4si __attribute__((ext_vector_type(4)));",
]

# Additional holder declarations introduced by path-coverage enumeration
# (Research/trace_logical_paths_clone/enumerate_branch_candidates.py). Kept
# separate from C_HELD_TYPES because HiOp_configuration_solver reads
# C_HELD_TYPES via ast.literal_eval.
EXTRA_C_HELD_TYPES = [
    "#include <stddef.h>",
    "#include <stdarg.h>",
    "typedef float ev4sf __attribute__((ext_vector_type(4)));",
    "typedef unsigned int v4ui __attribute__((vector_size(16)));",
    "typedef bool ev4b __attribute__((ext_vector_type(4)));",
    "typedef double v4df __attribute__((vector_size(32)));",
    "typedef short v4hi __attribute__((vector_size(8)));",
    "typedef _Complex _Float16 cf16;",
    "typedef int __attribute__((noderef)) *noderef_int_ptr;",
    "typedef struct S __attribute__((noderef)) *noderef_struct_ptr;",
    "typedef int __attribute__((noderef)) (*noderef_arr_ptr)[4];",
    "struct S_anon { union { int anon_m; float anon_f; }; struct { int m; }; };",
]


PREAMBLE = {
    "c": ["#include <stdint.h>", "#include <stdbool.h>"] + EXTRA_C_HELD_TYPES + C_HELD_TYPES + [""],
    "cpp": ["#include <cstdint>", "#include <compare>", "#include <new>", ""],
    "go": ["package main", ""],
    "rust": ["#![allow(unused, non_camel_case_types, non_snake_case, unused_parens)]", ""],
    "java": ["// held cells, judged by javac", ""],
}


# A placeholder that names something rather than holding a value: a member
# (`a.m`) or a label (`goto m;`). It takes no holder and no slot in the grid;
# the standard form writes the name itself, and the held types declare it.
# The standard form of a c cell, in two parts: the stand-in for an operand where
# only its type is wanted (inside the result's type: an lvalue of the holder,
# never evaluated), and the result's type. A compound literal stand-in,
# (A){0}, is refused for every _Atomic holder ("illegal initializer type",
# clang/lib/Sema/SemaInit.cpp line 1471), so every _Atomic cell read as
# refused . The result's type is taken through a
# comma: C converts the comma's right side as it reads a held value, so a
# const or _Atomic holder's qualifier comes off and the result can be
# assigned, while a cast keeps the type clang gives it (__typeof_unqual__
# took _Atomic off a cast to _Atomic int too, and clang then refused the
# assignment, 676 cells, run elv2_l67).
C_STAND_IN = "(*({0} *)0)"


C_RESULT_TYPE = "__typeof__(((void)0, {0}))"


C_LIBRARY_RULE = "library builtins declared as clang types them; atomic builtins held as calls"


NAME_PLACEHOLDERS = ("m", "n")


TYPE_PLACEHOLDERS = ("T", "U", "V", "W")


# The letters that hold values (extract_lang_vocab's PLACEHOLDER: `a` to `h`).
VALUE_PLACEHOLDERS = ("a", "b", "c", "d", "e", "f", "g", "h")


# The template clang's Sema takes, for a builtin whose template in
# `vocabulary/c.json` has a part clang does not take. clang declares these
# atomic builtins `(...)` and counts their parts itself (Builtins.td lines
# 2022 to 2032; SemaChecking.cpp line 3955, BuildAtomicExpr's NumArgs: 2 for
# TestAndSetByte and ClearByte, `bool __atomic_test_and_set(A *, int)` and
# `void __atomic_clear(A *, int)`, lines 3947 to 3951). The vocabulary wrote
# them with three parts, and clang refused every form, "too many arguments to
# function call, expected 2, have 3" (fable1_l81, 36 forms; fable1_l152, 21;
# lines record fable1_l168). 2026-10-21, Dee: "for the things you can do, do
# them please".
FORMS_BY_HAND = {
    "__atomic_test_and_set": ("__atomic_test_and_set(a, b)", ("a", "b")),
    "__atomic_clear": ("__atomic_clear(a, b)", ("a", "b")),
    "__builtin_alloca_with_align": ("__builtin_alloca_with_align(a, 8)", ("a",)),
    "__builtin_alloca_with_align_uninitialized": ("__builtin_alloca_with_align_uninitialized(a, 8)", ("a",)),
    "__builtin_assume_dereferenceable": ("__builtin_assume_dereferenceable(a, 8)", ("a",)),
    "__builtin_memcpy_inline": ("__builtin_memcpy_inline(a, b, 8)", ("a", "b")),
    "__builtin_memset_inline": ("__builtin_memset_inline(a, b, 8)", ("a", "b")),
}


# The parts clang's Sema counts for every atomic builtin, read from its own
# text (atomic_parts_from_sema, written to atomic_parts_c.json): the form
# BuildAtomicExpr gives each builtin (`switch (Op)`, SemaChecking.cpp lines
# 3998 to 4125), that form's count (`NumArgs`, line 3955), and one part more,
# the memory scope, for the OpenCL, HIP and scoped families but
# `__opencl_atomic_init` (lines 4127 to 4129), which Sema reads as the last
# part (lines 4488 to 4495). The vocabulary wrote 48 of them a part short, and
# clang refused every form, "too few arguments to function call, expected 4,
# have 3" (fable1_l82; PCHQ Gemini copy, log 491 §4, log 493 §4 line 3). The
# two FORMS_BY_HAND above agree with it.
ATOMIC_PARTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atomic_parts_c.json")
ATOMIC_PARTS = {}
SCOPE_FAMILIES = ("__opencl_atomic_", "__hip_atomic_", "__scoped_atomic_")
SCOPE_EXCEPTION = "__opencl_atomic_init"


def form_of(operator):
    """The operator as the standard form writes it: as the vocabulary has it,
    with the template clang's Sema takes (FORMS_BY_HAND), or, for an atomic
    builtin, with as many parts as Sema counts (atomic_parts)."""
    name = own_builtin_name(operator)
    found = FORMS_BY_HAND.get(name)
    if found is not None:
        written = operator._replace(spelling=found[0], operands=found[1])
        return written
    if operator.name == "MemberExpr":
        written = member_access_in_c(operator)
        return written
    if not operator.name.startswith("AtomicExpr."):
        return operator
    count = atomic_parts().get(name)
    if count is None or count == len(operator.operands):
        return operator
    operands = VALUE_PLACEHOLDERS[:count]
    spelling = name + "(" + ", ".join(operands) + ")"
    written = operator._replace(spelling=spelling, operands=tuple(operands))
    return written


def member_access_in_c(operator):
    """A member access as C writes it: `a->m`, `a.m`. The vocabulary's
    `a->template m` and `a.template m` are clang's printer writing C++'s
    `template` before a member name; C has no such word and reads `template`
    as a member's name, so every context of them was refused (fable1_l86: 0
    of 36; PCHQ Gemini copy, log 493 §3 row 5). The vocabulary's `a->` and
    `a.` name no member, so no C program writes them, and they stay as they
    are."""
    spelling = operator.spelling.replace("->template ", "->").replace(".template ", ".")
    if spelling == operator.spelling:
        return operator
    written = operator._replace(spelling=spelling)
    return written


def atomic_parts() -> dict:
    """builtin name -> the parts Sema counts for it, read once from atomic_parts_c.json."""
    if not ATOMIC_PARTS:
        with open(ATOMIC_PARTS_FILE, encoding="utf-8") as read:
            record = json.load(read)
        ATOMIC_PARTS.update(record["parts"])
    return ATOMIC_PARTS


def atomic_parts_from_sema(sema: str) -> dict:
    """builtin name -> the parts clang's Sema counts for it, read from
    SemaChecking.cpp's BuildAtomicExpr: its forms in order (the `enum` that
    ends `} Form = Init;`), each form's count (`NumArgs[]`), each builtin's
    form (`switch (Op)`: its `case AtomicExpr::AO__name:` lines, then
    `Form = Name;`), and one part more for a builtin of SCOPE_FAMILIES but
    SCOPE_EXCEPTION (`++AdjustedNumArgs`)."""
    with open(sema, encoding="utf-8") as read:
        lines = read.read().split("\n")
    start = index_of_text(lines, "AtomicArgumentOrder ArgOrder) {", 0)
    forms = atomic_forms(lines, start)
    counts = atomic_counts(lines, start)
    form_of_builtin = atomic_form_of_builtin(lines, start)
    parts = {}
    for name, form in form_of_builtin.items():
        count = counts[forms.index(form)]
        if name.startswith(SCOPE_FAMILIES) and name != SCOPE_EXCEPTION:
            count = count + 1
        parts[name] = count
    return parts


def index_of_text(lines: list, text: str, start: int) -> int:
    for number in range(start, len(lines)):
        if text in lines[number]:
            return number
    raise ValueError(f"atomic_parts_from_sema: {text!r} not found")


def atomic_forms(lines: list, start: int) -> list:
    """BuildAtomicExpr's forms, in the order of their enum."""
    first = index_of_text(lines, "enum {", start)
    last = index_of_text(lines, "} Form = Init;", first)
    forms = []
    for number in range(first + 1, last):
        match = re.match(r"^\s*([A-Z]\w*),?\s*$", lines[number])
        if match:
            forms.append(match.group(1))
    return forms


def atomic_counts(lines: list, start: int) -> list:
    """BuildAtomicExpr's `NumArgs[]`: each form's count, in the forms' order."""
    number = index_of_text(lines, "const unsigned NumArgs[] = {", start)
    inside = lines[number].split("{", 1)[1].split("}", 1)[0]
    counts = []
    for word in inside.split(","):
        counts.append(int(word.strip()))
    return counts


def atomic_form_of_builtin(lines: list, start: int) -> dict:
    """builtin name -> its form, from BuildAtomicExpr's `switch (Op)`."""
    first = index_of_text(lines, "switch (Op) {", start)
    last = index_of_text(lines, "unsigned AdjustedNumArgs = NumArgs[Form];", first)
    found = {}
    waiting = []
    for number in range(first + 1, last):
        line = lines[number]
        case = re.search(r"case AtomicExpr::AO(__\w+):", line)
        if case:
            waiting.append(case.group(1))
            continue
        form = re.search(r"Form = (\w+);", line)
        if form:
            for name in waiting:
                found[name] = form.group(1)
            continue
        if "break;" in line:
            waiting = []
    return found


def write_atomic_parts(sema: str, path: str) -> dict:
    """atomic_parts_from_sema written to `path` with where it was read from."""
    parts = atomic_parts_from_sema(sema)
    record = {"lowerer": "clang 21.1.8", "read_from": "clang/lib/Sema/SemaChecking.cpp, Sema::BuildAtomicExpr",
              "rule": "the form's NumArgs, and one more (the memory scope, read last) for " +
                      ", ".join(SCOPE_FAMILIES) + " but " + SCOPE_EXCEPTION,
              "parts": parts}
    with open(path, "w", encoding="utf-8") as write:
        json.dump(record, write, indent=1, sort_keys=True)
    return record


def slots_of(operator) -> tuple:
    """The placeholders that take a holder, in the order written: every one
    but a name (of the template the standard form writes, form_of)."""
    operator = form_of(operator)
    slots = tuple(p for p in operator.operands if p not in NAME_PLACEHOLDERS)
    return slots


def filled(spelling: str, values: dict) -> str:
    """The template with each placeholder replaced from `values`."""
    def replace(match):
        return values[match.group(1)]
    text = PLACEHOLDER.sub(replace, spelling)
    return text


LIBRARY_DECLARATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_declarations_c.json")
LIBRARY_DECLARATIONS = {}


def library_declarations() -> dict:
    """function name -> the declaration clang asks for before a call to that
    library function (`int abs(int);`), read once from library_declarations_c.json:
    the list DRY_mask_maker.library_declarations made from clang's own
    refusals on 2026-10-16 (run elv2_l177), 331 names. C_LIBRARY_RULE."""
    if not LIBRARY_DECLARATIONS:
        with open(LIBRARY_DECLARATIONS_FILE, encoding="utf-8") as read:
            record = json.load(read)
        for line in record["declarations"]:
            match = re.search(r"([A-Za-z_]\w*)\s*\(", line)
            if match:
                LIBRARY_DECLARATIONS[match.group(1)] = line
    return LIBRARY_DECLARATIONS


def library_declaration_of(operator) -> str:
    """The declaration a C library call's cell must carry before the call, or
    "" for anything else: a `__builtin_` name, an expression, a statement.
    clang 21 refuses `abs(p->a)` without `int abs(int);` ("call to undeclared
    library function"), so a cell without it is refused for the writer's
    fault and never for the holders' ."""
    line = ""
    if is_builtin_call(operator):
        name = builtin_name(operator)
        if not name.startswith("__"):
            line = library_declarations().get(name, "")
    return line


def with_library_declaration(lang: str, operator, lines: list) -> list:
    """The cell's lines with the library declaration, if the operator needs
    one, at the front of the first line: a cell stays two lines, which the
    grid's reading of refusals by line depends on."""
    if lang != "c":
        return lines
    declaration = library_declaration_of(operator)
    if not declaration:
        return lines
    first_line = f"{declaration} {lines[0]}"
    declared = [first_line] + list(lines[1:])
    return declared


def standard_HiOp_wrapper(lang: str, key: str, operator, spellings: tuple, routing) -> list:
    """The standard form of one cell, with the library declaration a C library
    call needs (with_library_declaration); the lines themselves are
    standard_HiOp_lines'. A builtin of FORMS_BY_HAND is written with the
    template clang's Sema takes (form_of)."""
    operator = form_of(operator)
    lines = standard_HiOp_lines(lang, key, operator, spellings, routing)
    lines = with_library_declaration(lang, operator, lines)
    return lines


def standard_HiOp_lines(lang: str, key: str, operator, spellings: tuple, routing) -> list:
    """The standard form of one cell: a struct the caller owns, holding each
    operand in a field, and the operator applied over the fields into the
    struct's result.

        c    struct P_k { A a; B b; __typeof__(((void)0, (*(A *)0) OP (*(B *)0))) result; };
             void op_k(struct P_k *p) { p->result = (p->a OP p->b); }
        cpp  struct P_k { A a; B b; decltype(a OP b) result; };
             extern "C" void op_k(P_k *p) { p->result = (p->a OP p->b); }

    The applied operator is parenthesized so it is the whole right side of
    the assignment whatever its precedence: unparenthesized, `a , b` would
    assign `a` and then evaluate `b` beside it.

    A c statement, an expression held with inert parts and an expression whose
    answer is kept in a local take their configuration from `routing`, which
    the caller hands: DRY_mask_maker.ROUTING, read from the record, or
    another (ROUTING_BY_HAND, the check, in
    Research/lower_HiOp/compare_routing_by_the_record.py).
    """
    written = placeholders_of(operator.spelling)
    if tuple(written) != tuple(operator.operands):
        message = f"standard_HiOp_wrapper: {operator.name}'s template does not show its operands in order"
        raise ValueError(message)
    slots = slots_of(operator)
    if len(spellings) != len(slots):
        message = f"standard_HiOp_wrapper: {operator.name} takes {len(slots)} holders, given {len(spellings)}"
        raise ValueError(message)
    spelling_of_slot = dict(zip(slots, spellings))
    fields = []
    as_stand_in = {}
    as_member = {}
    as_field = {}
    constants = ()
    if lang == "c":
        constants = constant_operands(operator)
    for placeholder in operator.operands:
        if placeholder in NAME_PLACEHOLDERS:
            as_stand_in[placeholder] = placeholder
            as_member[placeholder] = placeholder
            as_field[placeholder] = placeholder
            continue
        spelling = spelling_of_slot[placeholder]
        if placeholder in TYPE_PLACEHOLDERS:
            as_stand_in[placeholder] = spelling
            as_member[placeholder] = spelling
            as_field[placeholder] = spelling
            continue
        as_stand_in[placeholder] = C_STAND_IN.format(spelling)
        as_member[placeholder] = placeholder
        if placeholder in constants:
            # written as a constant where the HiOp reads it, so nothing reads a
            # field for it, and it has none (log 404, §2; log 405). Until log
            # 405 the field was declared and never read.
            as_field[placeholder] = CONSTANT_FORM.format(spelling)
            continue
        as_field[placeholder] = f"{FIELD_ACCESS[lang]}{placeholder}"
        if lang == "go":
            fields.append(f"{placeholder} {spelling}")
        elif lang == "rust":
            fields.append(f"pub {placeholder}: {spelling}")
        elif lang == "java":
            fields.append(f"{spelling} {placeholder};")
        else:
            fields.append(f"{spelling} {placeholder};")
    applied = filled(operator.spelling, as_field)
    if lang == "java":
        # java has no typeof; `var` keeps the result in a local the compiler
        # types, and every operator here is an expression.
        struct_line = f"final class P_{key} {{ {' '.join(fields)} }}"
        function_line = f"final class O_{key} {{ static void op(P_{key} p) {{ var r = ({applied}); }} }}"
        lines = [struct_line, function_line]
        return lines
    if lang == "rust":
        # rust has no typeof either, and every operator here is an
        # expression (an assignment is one of type ()), so the result is
        # held in a local the compiler types.
        struct_line = f"#[repr(C)] pub struct P_{key} {{ {', '.join(fields)} }}"
        function_line = f"pub fn op_{key}(p: &mut P_{key}) {{ let r = ({applied}); let _ = r; }}"
        lines = [struct_line, function_line]
        return lines
    if lang == "go":
        # go has no typeof: the result is held in a local the compiler
        # types, and an assignment operator is a statement of its own.
        struct_line = f"type P_{key} struct {{ {'; '.join(fields)} }}"
        if operator.name.startswith("AssignStmt."):
            function_line = f"func op_{key}(p *P_{key}) {{ {applied} }}"
        else:
            function_line = f"func op_{key}(p *P_{key}) {{ r := ({applied}); _ = r }}"
        lines = [struct_line, function_line]
        return lines
    field_text = " ".join(fields)
    if lang == "c" and is_statement(operator):
        lines = held_statement_lines(key, operator, spelling_of_slot, routing)
        return lines
    if lang == "c" and listed_name(operator) in routing.expressions:
        lines = inert_expression_lines(key, operator, spelling_of_slot, as_stand_in, routing)
        return lines
    if lang == "c" and listed_name(operator) in routing.local_answers:
        lines = held_local_answer_lines(key, operator, spelling_of_slot, routing)
        return lines
    if lang == "c" and is_builtin_call(operator):
        # many builtins answer nothing (`void`), and no field can hold that,
        # so a builtin's call is held as an expression statement: accepted
        # or refused all the same, and no result is kept
        if not field_text:
            field_text = "char unused_;"
        struct_line = f"struct P_{key} {{ {field_text} }};"
        function_line = f"void op_{key}(struct P_{key} *p) {{ (void)({applied}); }}"
        lines = [struct_line, function_line]
        return lines
    if lang == "c" and flexible_array_operands(operator):
        lines = flexible_array_lines(key, operator, spelling_of_slot)
        return lines
    if lang == "c":
        result_type = result_type_of(operator, as_stand_in)
        struct_line = f"struct P_{key} {{ {field_text} {result_type} result; }};"
        function_line = f"void op_{key}(struct P_{key} *p) {{ p->result = ({applied}); }}"
    else:
        result_type = f"decltype({filled(operator.spelling, as_member)})"
        struct_line = f"struct P_{key} {{ {field_text} {result_type} result; }};"
        function_line = f'extern "C" void op_{key}(P_{key} *p) {{ p->result = ({applied}); }}'
    lines = [struct_line, function_line]
    return lines


def HiOp_on_its_own_line(lines: list) -> list:
    """A c standard form with its function written over three lines: the header
    and its opening brace, the HiOp alone on the next line, and the closing
    brace. The lines before the function (its struct, its declarations) are
    kept as they are.

        void op_k(struct P_k *p) {
        	p->result = (p->a OP p->b);
        }

    The debug table then files the HiOp's words under a line of their own,
    and the frame's under the header and the closing brace, so
    extract_unit_from_LoHiOp cuts the Unit by line. Dee, 2026-10-13 (PCHQ log
    446): "we need some way to tell which arch-opcodes belong to the lowered
    HiOp"; written the same day (log 449). Only the layout changes."""
    if len(lines) >= 3 and lines[-1].strip() == "}" and lines[-3].endswith("*p) {"):
        held = list(lines[:-2])
        body = lines[-2].lstrip("\t")
        held.append("\t" + body)
        held.append("}")
        return held
    function_line = lines[-1]
    header, body = header_and_body_of(function_line)
    held = list(lines[:-1])
    held.append(header)
    held.append("\t" + body)
    held.append("}")
    return held


def custom_program_lines(key: str, program: str) -> list:
    """Normalizes a custom single-variant C program from consolidated path
    enumeration so it can sit inside a multi-function batch alongside
    standard_HiOp_wrapper lines without symbol or struct collisions."""
    preamble_set = {line.strip() for line in PREAMBLE["c"] if line.strip()}
    preamble_set.add("typedef _Bool ev4b __attribute__((ext_vector_type(4)));")
    preamble_set.add("enum E_case { E0 = 0 };")
    text = program
    if "struct SA { int pad;" in text:
        text = re.sub(r"\bSA\b", f"SA_{key}", text)
    text = re.sub(r"\bop_k\b", f"op_{key}", text)
    text = re.sub(r"\bP_k\b", f"P_{key}", text)
    text = re.sub(r"\bpart_k_", f"part_{key}_", text)
    text = re.sub(r"\breg_k_", f"reg_{key}_", text)
    text = re.sub(r"\bomp_depend_t\b", f"omp_depend_t_{key}", text)
    text = re.sub(r"\bomp_interop_t\b", f"omp_interop_t_{key}", text)
    text = re.sub(r"\bdispatch_target_fn\b", f"dispatch_target_fn_{key}", text)
    text = re.sub(r"\bdispatch_base_fn\b", f"dispatch_base_fn_{key}", text)
    kept = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped in preamble_set:
            continue
        kept.append(stripped)
    return kept


def header_and_body_of(function_line: str) -> tuple:
    """`void op_k(struct P_k *p) { BODY }` -> ("void op_k(struct P_k *p) {",
    "BODY"): split at the brace that opens the function and the one that
    closes it."""
    opening = function_line.index("*p) { ") + len("*p) {")
    closing = function_line.rindex(" }")
    header = function_line[:opening]
    body = function_line[opening + 1:closing]
    parts = (header, body)
    return parts


# How `vocabulary/c.json` names a builtin's call: `CallExpr.BI<name>`, and
# for clang's atomic builtins, which clang builds as a kind of their own,
# `AtomicExpr.AO<name>`.
BUILTIN_PREFIXES = ("CallExpr.BI", "AtomicExpr.AO")


def is_builtin_call(operator) -> bool:
    """Whether the operator is one of the lowerer's builtins, written as a
    call. An atomic builtin is one too: `__atomic_load` answers nothing, so
    held with its result in a field it read as refused for every holder
    ."""
    builtin = operator.name.startswith(BUILTIN_PREFIXES)
    return builtin


def builtin_name(operator) -> str:
    """The builtin's own name: `abs` for `CallExpr.BIabs`."""
    for prefix in BUILTIN_PREFIXES:
        if operator.name.startswith(prefix):
            return operator.name[len(prefix):]
    return operator.name


def is_statement(operator) -> bool:
    """Whether the operator is one of the lowerer's statements (clang's kinds
    end in `Stmt`), which has no value to hold."""
    kind = operator.name.split(".")[0]
    statement = kind.endswith("Stmt")
    return statement


# The standard form of a control HiOp: every part is an inert call, a call to a
# function declared and never defined, so clang keeps every part, and the
# HiOp's Unit is its own jumps and tests with a call where each part goes.
# Dee, 2026-10-08: "having inert function bodies might actually solve that
# problem because the polyfill would be a nested structure of function
# calls". Tried in research 
# try_inert_parts.py) and moved here at Dee's word (log 399): "it seems like
# the new standard-form is incredibly successful and would make sense to be in
# the project PlanPlan and its implementation".
#
# Where each listing's configuration comes from 
# 420 §4; Dee, 2026-10-11: "proceed with part b"): which placeholders are
# bodies, which expressions hold bodies, which statements jump, what a
# dependent-HiOp stands inside, what a part stands inside, which standard function
# answers a value, and which answer is kept in a local are read from the record
# of HiOp_configuration_solver (ROUTING, made by routing_from_the_record, in the
# section "the routing" below). The tables and branches written by hand until
# then are kept here under their names with _BY_HAND added (ROUTING_BY_HAND
# holds them), as the check the routing from the record is compared with: Dee,
# 2026-10-10, by-hand results are the oracle when automating (logs 400 to 402).
# The standard-form uses only ROUTING.
#
# Each placeholder of each template, by what it is to the HiOp: a value it
# tests or hands on, whose holder matters; a body it runs, whose holder does
# not; a constant it compares with (a case label); or a name (a label).
INERT_PART_ROLES_BY_HAND = {
    "if (a) b;": {"a": "value", "b": "body"},
    "if (a) b; else c;": {"a": "value", "b": "body", "c": "body"},
    "while (a) b;": {"a": "value", "b": "body"},
    "do a; while (b);": {"a": "body", "b": "value"},
    "for (a; b; c) d;": {"a": "body", "b": "value", "c": "body", "d": "body"},
    "for (a; b;) c;": {"a": "body", "b": "value", "c": "body"},
    "for (a; ; b) c;": {"a": "body", "b": "body", "c": "body"},
    "for (a; ;) b;": {"a": "body", "b": "body"},
    "for (; a; b) c;": {"a": "value", "b": "body", "c": "body"},
    "for (; a;) b;": {"a": "value", "b": "body"},
    "for (;; a) b;": {"a": "body", "b": "body"},
    "for (;;) a;": {"a": "body"},
    "switch (a) b;": {"a": "value", "b": "body"},
    "case a: b;": {"a": "constant", "b": "body"},
    "case a ... b: c;": {"a": "constant", "b": "constant", "c": "body"},
    "default: a;": {"a": "body"},
    "{ a; b; }": {"a": "body", "b": "body"},
    "{ a; }": {"a": "body"},
    "{ }": {},
    "m: a;": {"m": "name", "a": "body"},
    "goto m;": {"m": "name"},
    "goto *a;": {"a": "value"},
    "return a;": {"a": "value"},
    "return;": {},
    "break;": {},
    "continue;": {},
    ";": {},
    "a && b": {"a": "value", "b": "value"},
    "a || b": {"a": "value", "b": "value"},
    "a ? b : c": {"a": "value", "b": "value", "c": "value"},
    "a ?: b": {"a": "value", "b": "value"},
}


# The expressions whose parts run only on some paths, held the same way.
INERT_PART_EXPRESSIONS_BY_HAND = ("BinaryOperator.LAnd", "BinaryOperator.LOr", "ConditionalOperator",
                                  "BinaryConditionalOperator")


# The value a HiOp reads from a holder, as an inert value part returns it:
# the holder's type taken through a comma, as C_RESULT_TYPE takes a result's,
# so const, volatile and _Atomic come off and an array comes back as its
# pointer. Returning the holder's own type, clang refused every _Atomic one
# (log 397, elv2_l102).
INERT_VALUE_TYPE = "__typeof__(((void)0, (*({0} *)0)))"


# Holders no function can return: handed back by address, and read through it.
INERT_BY_ADDRESS = ("__fp16", "__bf16")


# An operand GNU C needs as a constant is written as a zero: a case label, and
# `__atomic_always_lock_free`'s size. clang's prototype for that builtin takes
# a plain size_t (Builtins.td lines 2052 to 2056), but clang answers it only by
# evaluating it as a constant (ExprConstant.cpp lines 13584 to 13589) and has
# no code for it otherwise (CGBuiltin.cpp line 6471, "cannot compile this
# builtin function yet"). Read from a field, all 442 of its HiOps were refused
# (log 398).
CONSTANT_OPERANDS = {
    "__atomic_always_lock_free": ("a",),
}


# The zero is of the value read from the holder (INERT_VALUE_TYPE), so an
# _Atomic holder's zero is a plain one: written `((_Atomic int)0)`, clang
# refused it as a size, "passing '_Atomic(int)' to parameter of incompatible
# type 'unsigned long'" (39 HiOps, elv2_l108).
CONSTANT_FORM = "((" + INERT_VALUE_TYPE + ")0)"


# A builtin whose answer keeps its operand's qualifiers: clang types
# `__builtin_align_up` and `__builtin_align_down` "the same as the
# (potentially decayed) argument type including qualifiers" (SemaChecking.cpp
# lines 389 to 392), and `__builtin_nondeterministic_value` as its argument's
# own type (line 15861). On a `const int` the result field was `const` too, and
# clang refused the store into it, "cannot assign to non-static data member
# 'result' with const-qualified type" (37 HiOps, log 398). Their result field
# is typed without qualifiers; held so by hand, the 37 lowered to the same
# words as the same builtins on a plain `int` (log 400). For these three only:
# `__typeof_unqual__` for every HiOp also took `_Atomic` off a cast's type, and
# clang refused 676 casts to `_Atomic` holders (log 367, run elv2_l67), which is
# why C_RESULT_TYPE takes the type through a comma. Dee, 2026-10-09: "okay go
# ahead and make both corrections to the standard-form" (log 402).
UNQUALIFIED_RESULTS = (
    "__builtin_align_up",
    "__builtin_align_down",
    "__builtin_nondeterministic_value",
    "__builtin_preserve_access_index",
)


C_UNQUALIFIED_RESULT_TYPE = "__typeof_unqual__(((void)0, {0}))"


# An operand GNU C needs as a flexible array member, a struct's last field
# written with no length: `__builtin_counted_by_ref`'s (SemaChecking.cpp,
# Sema::BuiltinCountedByRef, from line 5957). It is written as one, last in
# the container, its element the element of the value read from the holder,
# with the count field that clang's `counted_by` names. clang refuses the
# builtin's answer assigned, passed or returned (CheckInvalidBuiltinCountedByRef,
# from line 6008), so the standard function stores through the answer, as clang's
# documentation does (LanguageExtensions.rst, from line 4132). Held from a field
# with its answer stored, its one HiOp was refused (logs 398 and 400).
FLEXIBLE_ARRAY_OPERANDS = {
    "__builtin_counted_by_ref": ("a",),
}


C_FLEXIBLE_ARRAY_FIELD = "int count; __typeof__((*({0} *)0)[0]) {1}[] __attribute__((counted_by(count)));"


# The jump rule: a statement that jumps needs reached code between it and its
# target, so it sits behind an inert test, with an inert call after it (`{0}`
# the statement, `{1}` the test, `{2}` the call). The test lets a path skip the
# jump and reach that call, so the jump goes over it, as it does in real code
# (zlib's inflate.c, log 400). Held with only a call after the jump (a
# do-while's test, a skipped body), no path reached that call, none of its
# words were in the object on any of the three architectures, and the jump
# went to the very next word (log 399). `break;` and `goto m;` since log 402;
# `continue;`, `goto *a;`, `return a;` and `return;` since log 405, after Dee
# asked, 2026-10-09: "should we not make `GNU-C` current with the most advanced
# design?". Before it, `continue;` jumped back to itself, `return a;` and
# `return;` wrote no jump at all (log 404, §3), and `goto *a;` jumped over the
# standard function's return only.
C_JUMPS_BY_HAND = ("BreakStmt", "ContinueStmt", "GotoStmt", "IndirectGotoStmt", "ReturnStmt")


C_JUMP_OVER_REACHED_CODE = "if ({1}) {0} {2};"


# What a statement needs around it so that it is reached and its jump goes
# somewhere, `{0}` the statement (behind its test, if it jumps) and `{1}` an
# inert call: `break;` and `continue;` in a `for (;;)`, `goto m;` before its
# label, `goto *a;` before a label whose address is taken (clang takes
# `goto *a;` only in a function that takes one), a `case` in a switch on a
# value, and a `default` beside a case, so that it is chosen against something
# (log 394, Table 1).
C_STATEMENT_CONTEXT_BY_HAND = {
    "BreakStmt": "for (;;) {{ {0} }}",
    "ContinueStmt": "for (;;) {{ {0} }}",
    "GotoStmt": "{0} m:;",
    "IndirectGotoStmt": "{0} m: (void)&&m;",
    "CaseStmt": "switch ({1}) {{ {0} }}",
    "DefaultStmt": "switch ({1}) {{ case 0: break; {0} }}",
}


# The inert call statement_in_context wrote for a context's `{1}`, by hand: the
# switch's value, named `switch` (its code until log 424).
C_CONTEXT_NAMES_BY_HAND = {
    "CaseStmt": {"value": "switch"},
    "DefaultStmt": {"value": "switch"},
}


# switch_with_a_case_label, by hand (its code until log 424): `switch (a) b;`
# with a case label before b, so b can be reached (log 394, Table 1, line
# 2378), `{0}` the part as held; the `;` the template ends with stays, after the
# switch's body.
C_PART_CONTEXTS_BY_HAND = {
    "switch (a) b;": {"b": "{{ case 0: {0}; }}"},
}


# statement_returns, by hand (its code until log 424): `return a;` returns its
# value's own type; every other statement returns nothing.
C_FUNCTION_ANSWERS_BY_HAND = {
    "return a;": "a",
}


class InertParts:
    """A HiOp's parts as inert calls: the text each placeholder becomes, and
    the declarations of the functions they call."""

    def __init__(self):
        self.text = {}
        self.declarations = []


def listed_name(operator) -> str:
    """The operator's name as the vocabulary lists it: without the `Kept.` the
    lowering puts before a builtin whose result it keeps (lower_gnu_c)."""
    name = operator.name
    if name.startswith("Kept."):
        name = name[len("Kept."):]
    return name


def kind_of(operator) -> str:
    """The lowerer's kind of the operator: its listed name up to the first dot
    (`CaseStmt`, `BinaryOperator`)."""
    name = listed_name(operator)
    kind = name.split(".")[0]
    return kind


def held_statement_lines(key: str, operator, spelling_of_slot: dict, routing) -> list:
    """The standard form of a C statement: its parts inert (the routing's roles),
    a part in what it must stand in (the routing's part contexts), and the
    statement behind its test if it jumps and in what it needs around it (the
    routing's jumps and contexts). Two lines, as every held cell is, because
    the grid reads each cell's refusals by its two lines: the inert functions'
    declarations and the struct, then the standard function.

        int part_k_a(void); void part_k_b(void); struct P_k { char unused_; };
        void op_k(struct P_k *p) { if (part_k_a()) part_k_b(); }

    The standard function answers a value where the routing says so (`return a;`
    returns its value's own type)."""
    parts = inert_parts(key, operator, spelling_of_slot, routing)
    texts = parts_in_their_contexts(operator, parts, spelling_of_slot, routing)
    body = filled(operator.spelling, texts)
    body = statement_in_context(key, operator, parts, body, spelling_of_slot, routing)
    returns = statement_returns(operator, parts, routing)
    declarations = " ".join(parts.declarations)
    first_line = f"{declarations} struct P_{key} {{ char unused_; }};"
    first_line = first_line.strip()
    function_line = f"{returns} op_{key}(struct P_{key} *p) {{ {body} }}"
    lines = [first_line, function_line]
    return lines


def inert_parts(key: str, operator, spelling_of_slot: dict, routing) -> InertParts:
    roles = roles_of(operator, routing)
    parts = InertParts()
    for placeholder, role in roles.items():
        held_as = role_held_as(operator, role)
        add_inert_part(parts, key, placeholder, held_as, spelling_of_slot.get(placeholder))
    return parts


def roles_of(operator, routing) -> dict:
    """Each placeholder's role, as the routing reads it from the record (R1).
    A statement the record does not hold has no record to read: R1 then
    reads, as it does for every placeholder with nothing in the record, a
    name for a name letter and a value otherwise. Such statements are the
    ones the language refuses, which the grid asks so that its lowerer says
    so: C++'s `try` and `if consteval`, Objective-C's `@try`, and others.
    Until 2026-10-14  a lookup here stopped on them, and the
    grid could not run since the routing came from the record (log 424):
    13,139 of its 2,088,155 cells, none of them accepted on 2026-10-06."""
    if operator.spelling in routing.roles:
        roles = routing.roles[operator.spelling]
        return roles
    roles = {}
    for placeholder in placeholders_of(operator.spelling):
        if placeholder in NAME_PLACEHOLDERS:
            roles[placeholder] = "name"
            continue
        roles[placeholder] = "value"
    return roles


def role_held_as(operator, role: str) -> str:
    """How a role is held. A body of an expression is held as a value is: the
    expression hands that body's value on (`a ? b : c` answers the value `b`
    or `c` reads; `a && b` answers by the value `b` reads), so the standard-form
    stores what comes from it, and its call answers the value read from its
    holder. A call answering nothing cannot give that value. The design says
    so for `?:`: SUPPORT_held_form_in_modelling_abstraction.md, Table 1,
    "each body a value". Bodies of expressions came with the routing from the
    record ; the table written by hand gave those parts the role
    value, held the same way. A statement's body answers nothing, as before."""
    if role == "body" and not is_statement(operator):
        held_as = "value"
        return held_as
    held_as = role
    return held_as


def add_inert_part(parts: InertParts, key: str, placeholder: str, role: str, spelling) -> None:
    name = f"part_{key}_{placeholder}"
    if role == "name":
        parts.text[placeholder] = placeholder
    elif role == "body":
        parts.declarations.append(f"void {name}(void);")
        parts.text[placeholder] = f"{name}()"
    elif role == "constant":
        parts.text[placeholder] = CONSTANT_FORM.format(spelling)
    elif spelling in INERT_BY_ADDRESS:
        parts.declarations.append(f"__typeof__({spelling}) *{name}(void);")
        parts.text[placeholder] = f"(*{name}())"
    else:
        value_type = INERT_VALUE_TYPE.format(spelling)
        parts.declarations.append(f"{value_type} {name}(void);")
        parts.text[placeholder] = f"{name}()"


def add_inert_call(parts: InertParts, key: str, name_end: str, returns: str) -> str:
    """One more inert function, for what a statement stands in; its call."""
    name = f"part_{key}_{name_end}"
    parts.declarations.append(f"{returns} {name}(void);")
    call = f"{name}()"
    return call


def parts_in_their_contexts(operator, parts: InertParts, spelling_of_slot: dict, routing) -> dict:
    """What each placeholder is written as: its part as held, or, for a part
    the routing stands inside something, the part inside it (a switch's body
    inside a case label, so that it is reached): `{0}` the part as held, `{2}`
    a zero of the value the listing's first value reads."""
    texts = dict(parts.text)
    contexts = routing.part_contexts.get(operator.spelling, {})
    for placeholder, template in contexts.items():
        constant = CONSTANT_FORM.format(first_value_holder(operator, spelling_of_slot, routing))
        texts[placeholder] = template.format(parts.text[placeholder], "", constant)
    return texts


def first_value_holder(operator, spelling_of_slot: dict, routing) -> str:
    """The holder of the listing's first placeholder whose role is value
    (`int` when it has none): what a switch's own case label is compared
    with."""
    roles = routing.roles.get(operator.spelling, {})
    for placeholder, role in roles.items():
        if role == "value":
            holder = spelling_of_slot[placeholder]
            return holder
    holder = "int"
    return holder


def statement_in_context(key: str, operator, parts: InertParts, body: str, spelling_of_slot: dict,
                         routing) -> str:
    """The statement behind its test if it jumps (the routing's jumps), then
    in what it needs around it (the routing's contexts)."""
    kind = kind_of(operator)
    if kind in routing.jumps:
        body = jump_over_reached_code(key, parts, body)
    template = routing.contexts.get(kind)
    if template is None:
        return body
    held = stood_in_its_context(key, operator, parts, body, spelling_of_slot, template, routing)
    return held


def stood_in_its_context(key: str, operator, parts: InertParts, statement: str, spelling_of_slot: dict,
                         template: str, routing) -> str:
    """A context's text with its holes filled: `{0}` the statement; `{1}` an
    inert call answering the value the context takes (a switch's), read as
    the holder of the HiOp's first constant, the value it is compared with (a
    case label's), or as `int` when the HiOp has none; `{2}` a zero of that
    value; `{3}` an inert call for a line the context holds (a label's
    statement). Each inert call is named as the routing names it."""
    names = routing.context_names.get(kind_of(operator), {})
    value = ""
    if "{1}" in template:
        value_type = context_value_type(operator, spelling_of_slot, routing)
        value = add_inert_call(parts, key, names["value"], value_type)
    constant = ""
    if "{2}" in template:
        holder = first_constant_holder(operator, spelling_of_slot, routing)
        if holder is None:
            holder = "int"
        constant = CONSTANT_FORM.format(holder)
    held_line = ""
    if "{3}" in template:
        held_line = add_inert_call(parts, key, names["held"], "void")
    held = template.format(statement, value, constant, held_line)
    return held


def context_value_type(operator, spelling_of_slot: dict, routing) -> str:
    """The type of the value a context takes: the value read from the holder
    of the HiOp's first constant, or `int` when the HiOp has none (as
    statement_in_context wrote it since log 399)."""
    holder = first_constant_holder(operator, spelling_of_slot, routing)
    if holder is None:
        value_type = "int"
        return value_type
    value_type = INERT_VALUE_TYPE.format(holder)
    return value_type


def first_constant_holder(operator, spelling_of_slot: dict, routing):
    """The holder of the HiOp's first placeholder whose role is constant, or
    None."""
    roles = routing.roles.get(operator.spelling, {})
    for placeholder, role in roles.items():
        if role == "constant":
            holder = spelling_of_slot[placeholder]
            return holder
    holder = None
    return holder


def jump_over_reached_code(key: str, parts: InertParts, statement: str) -> str:
    """A statement that jumps, behind an inert test, with an inert call after
    it, so the code between the jump and its target is reached and the
    lowerer writes it (C_JUMP_OVER_REACHED_CODE)."""
    test = add_inert_call(parts, key, "test", "int")
    skipped = add_inert_call(parts, key, "skipped", "void")
    guarded = C_JUMP_OVER_REACHED_CODE.format(statement, test, skipped)
    return guarded


def statement_returns(operator, parts: InertParts, routing) -> str:
    """What the standard function answers: the value of the placeholder the
    routing names for the listing (`return a;`'s `a`), or nothing."""
    placeholder = routing.function_answers.get(operator.spelling)
    if placeholder is None:
        returns = "void"
        return returns
    returns = C_RESULT_TYPE.format(parts.text[placeholder])
    return returns


def inert_expression_lines(key: str, operator, spelling_of_slot: dict, as_stand_in: dict, routing) -> list:
    """An expression whose parts run only on some paths (`a && b`, `a || b`,
    `a ? b : c`, `a ?: b`, and since the routing from the record
    `__builtin_fpclassify`): its parts inert, its result stored in the struct
    as every expression's is, of the same type as before. Two lines."""
    parts = inert_parts(key, operator, spelling_of_slot, routing)
    applied = filled(operator.spelling, parts.text)
    result_type = C_RESULT_TYPE.format(filled(operator.spelling, as_stand_in))
    declarations = " ".join(parts.declarations)
    first_line = f"{declarations} struct P_{key} {{ {result_type} result; }};"
    function_line = f"void op_{key}(struct P_{key} *p) {{ p->result = ({applied}); }}"
    lines = [first_line, function_line]
    return lines


# An answer kept in a local of the standard function, of its own type, named inside
# the function. The container's result field is declared outside every
# function, where a type that names a label cannot be written: `&&m`, the
# address of a label, which only a function holds. The grid has held `&&m` with
# its answer in such a local since log 377 (run_elv3.label_address_check). It is
# one of the uses the standard-form's rule allows for an answer the lowerer refuses
# to store (log 404 §2: "used the way the lowerer allows").
C_LOCAL_ANSWER = "__typeof__({0}) result = ({0});"


def held_local_answer_lines(key: str, operator, spelling_of_slot: dict, routing) -> list:
    """An expression whose answer the routing keeps in a local (`&&m`): the
    answer in a local of its own type (C_LOCAL_ANSWER), then what the
    expression needs in the same function, as the routing writes its context
    (`m:`, its label, holding an inert call). Two lines:

        void part_k_label(void); struct P_k { char unused_; };
        void op_k(struct P_k *p) { __typeof__(&&m) result = (&&m); m: part_k_label(); }
    """
    parts = InertParts()
    names = names_as_written(operator)
    applied = filled(operator.spelling, names)
    statement = C_LOCAL_ANSWER.format(applied)
    statement = statement_in_context(key, operator, parts, statement, spelling_of_slot, routing)
    declarations = " ".join(parts.declarations)
    first_line = f"{declarations} struct P_{key} {{ char unused_; }};"
    first_line = first_line.strip()
    function_line = f"void op_{key}(struct P_{key} *p) {{ {statement} }}"
    lines = [first_line, function_line]
    return lines


def names_as_written(operator) -> dict:
    """Each placeholder written as itself; only names are, so any other
    placeholder stops the standard-form here rather than being guessed at."""
    names = {}
    for placeholder in operator.operands:
        if placeholder not in NAME_PLACEHOLDERS:
            message = (f"standard_HiOp_wrapper: {operator.name} keeps its answer in a local, and its placeholder "
                       f"{placeholder} is not a name; the standard-form has no rule for it")
            raise ValueError(message)
        names[placeholder] = placeholder
    return names


def own_builtin_name(operator) -> str:
    """A builtin's own name, from its operator's: `abs` for `CallExpr.BIabs`,
    and for `Kept.CallExpr.BIabs`, as the caller names a builtin whose result
    is kept. Any other operator's name comes back as it is."""
    name = operator.name
    if name.startswith("Kept."):
        name = name[len("Kept."):]
    for prefix in BUILTIN_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def constant_operands(operator) -> tuple:
    """The operands of a builtin that GNU C needs as constants
    (CONSTANT_OPERANDS)."""
    name = own_builtin_name(operator)
    operands = CONSTANT_OPERANDS.get(name, ())
    return operands


def flexible_array_operands(operator) -> tuple:
    """The operands of a builtin that GNU C needs as flexible array members
    (FLEXIBLE_ARRAY_OPERANDS)."""
    name = own_builtin_name(operator)
    operands = FLEXIBLE_ARRAY_OPERANDS.get(name, ())
    return operands


def result_type_of(operator, as_stand_in: dict) -> str:
    """The result field's type: taken through a comma (C_RESULT_TYPE), or
    without qualifiers for a builtin whose answer keeps them
    (UNQUALIFIED_RESULTS)."""
    form = C_RESULT_TYPE
    if own_builtin_name(operator) in UNQUALIFIED_RESULTS:
        form = C_UNQUALIFIED_RESULT_TYPE
    result_type = form.format(filled(operator.spelling, as_stand_in))
    return result_type


def flexible_array_lines(key: str, operator, spelling_of_slot: dict) -> list:
    """A builtin with an operand GNU C needs as a flexible array member: the
    operand last in the container, after the count field, and the held
    function storing through the builtin's answer, since clang refuses the
    answer stored (FLEXIBLE_ARRAY_OPERANDS). Two lines:

        struct P_k { int count; __typeof__((*(A *)0)[0]) a[] __attribute__((counted_by(count))); };
        void op_k(struct P_k *p) { *__builtin_counted_by_ref(p->a) = 0; }
    """
    flexible = flexible_array_operands(operator)
    fields = []
    as_field = {}
    for placeholder in operator.operands:
        as_field[placeholder] = f"{FIELD_ACCESS['c']}{placeholder}"
        if placeholder not in flexible:
            fields.append(f"{spelling_of_slot[placeholder]} {placeholder};")
    for placeholder in flexible:
        fields.append(C_FLEXIBLE_ARRAY_FIELD.format(spelling_of_slot[placeholder], placeholder))
    applied = filled(operator.spelling, as_field)
    struct_line = f"struct P_{key} {{ {' '.join(fields)} }};"
    function_line = f"void op_{key}(struct P_{key} *p) {{ *{applied} = 0; }}"
    lines = [struct_line, function_line]
    return lines
