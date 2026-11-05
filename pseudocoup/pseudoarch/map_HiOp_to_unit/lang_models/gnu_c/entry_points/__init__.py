"""entry_points -- Clang Sema and CodeGen HiOp entry-point descriptors and
hijacked entry invocation synthesis from StateInfo0 (state_info[0]).

Plan: `.../node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_4_entry_points/`.

Given a structured `StateInfo0` token/state descriptor inferred from a
BranchTree path's surviving sets, synthesizes the minimal hijacked entry
invocation (`op_<key>`) for the hijacked Clang binary (`HIJACK_HIOP=1`),
with zero outer loop/switch AST wrappers and automatic `depth == 2` child
part stubbing (`part_b`, `part_c`, ...).
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from ....model_lang_parts import PLACEHOLDER, Operator, placeholders_of
from ....model_lang_parts.context.entry_context import (
    PartState0,
    StateInfo0,
    load_hiop_relations,
)


# Clang Sema + CodeGen entry functions per GNU C HiOp family.
HIOP_ENTRY_FUNCTIONS: Dict[str, Tuple[str, ...]] = {
    "BinaryOperator": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::CreateBuiltinBinOp",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitBin*",
    ),
    "CompoundAssignOperator": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::CreateBuiltinBinOp",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::EmitCompoundAssign",
    ),
    "UnaryOperator": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::CreateBuiltinUnaryOp",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitUnary*",
    ),
    "ConditionalOperator": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::ActOnConditionalOp",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitAbstractConditionalOperator",
    ),
    "BinaryConditionalOperator": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::ActOnConditionalOp",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitBinaryConditionalOperator",
    ),
    "ArraySubscriptExpr": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::CreateBuiltinArraySubscriptExpr",
        "clang/lib/CodeGen/CGExpr.cpp:CodeGenFunction::EmitArraySubscriptExpr",
    ),
    "MemberExpr": (
        "clang/lib/Sema/SemaExprMember.cpp:Sema::BuildMemberReferenceExpr",
        "clang/lib/CodeGen/CGExpr.cpp:CodeGenFunction::EmitMemberExpr",
    ),
    "CStyleCastExpr": (
        "clang/lib/Sema/SemaCast.cpp:Sema::BuildCStyleCastExpr",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitCastExpr",
    ),
    "UnaryExprOrTypeTraitExpr": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::CreateUnaryExprOrTypeTraitExpr",
        "clang/lib/CodeGen/CGExprScalar.cpp:ScalarExprEmitter::VisitUnaryExprOrTypeTraitExpr",
    ),
    "AtomicExpr": (
        "clang/lib/Sema/SemaChecking.cpp:Sema::BuildAtomicExpr",
        "clang/lib/CodeGen/CGAtomic.cpp:CodeGenFunction::EmitAtomicExpr",
    ),
    "CallExpr": (
        "clang/lib/Sema/SemaChecking.cpp:Sema::CheckBuiltinFunctionCall",
        "clang/lib/CodeGen/CGBuiltin.cpp:CodeGenFunction::EmitBuiltinExpr",
    ),
    "IfStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnIfStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitIfStmt",
    ),
    "WhileStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnWhileStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitWhileStmt",
    ),
    "DoStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnDoStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitDoStmt",
    ),
    "ForStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnForStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitForStmt",
    ),
    "SwitchStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnStartOfSwitchStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitSwitchStmt",
    ),
    "CaseStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnCaseStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitCaseStmt",
    ),
    "DefaultStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnDefaultStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitDefaultStmt",
    ),
    "BreakStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnBreakStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitBreakStmt",
    ),
    "ContinueStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnContinueStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitContinueStmt",
    ),
    "GotoStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnGotoStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitGotoStmt",
    ),
    "IndirectGotoStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnIndirectGotoStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitIndirectGotoStmt",
    ),
    "ReturnStmt": (
        "clang/lib/Sema/SemaStmt.cpp:Sema::ActOnReturnStmt",
        "clang/lib/CodeGen/CGStmt.cpp:CodeGenFunction::EmitReturnStmt",
    ),
    "AddrLabelExpr": (
        "clang/lib/Sema/SemaExpr.cpp:Sema::ActOnAddrLabel",
        "clang/lib/CodeGen/CGExpr.cpp:CodeGenFunction::EmitAddrLabelExpr",
    ),
}

GNU_C_ENTRY_PREAMBLE: Tuple[str, ...] = (
    "#include <stdint.h>",
    "#include <stdbool.h>",
    "#include <stddef.h>",
    "#include <stdarg.h>",
    "struct S { int m; int n; };",
    "struct SN { struct S m; };",
    "struct SA { int m[4]; };",
    "union U { int m; double n; };",
    "struct I;",
    "enum E { E0, E1 };",
    "typedef int v4si __attribute__((vector_size(16)));",
    "typedef float v4sf __attribute__((vector_size(16)));",
    "typedef unsigned int v4ui __attribute__((vector_size(16)));",
    "typedef double v4df __attribute__((vector_size(32)));",
    "typedef short v4hi __attribute__((vector_size(8)));",
    "typedef int ev4si __attribute__((ext_vector_type(4)));",
    "typedef float ev4sf __attribute__((ext_vector_type(4)));",
    "typedef bool ev4b __attribute__((ext_vector_type(4)));",
    "typedef int (*fnptr)(int);",
    "typedef int arr4[4];",
    "typedef int (*arrptr)[4];",
    "typedef int fntype(int);",
    "typedef _Complex _Float16 cf16;",
    "typedef int __attribute__((noderef)) *noderef_int_ptr;",
    "typedef struct S __attribute__((noderef)) *noderef_struct_ptr;",
    "typedef int __attribute__((noderef)) (*noderef_arr_ptr)[4];",
    "struct S_anon { union { int anon_m; float anon_f; }; struct { int m; }; };",
    "void __hiop_sink(void);",
)

ARCH_GLOBAL_REG: Dict[str, str] = {
    "riscv64": "s2",
    "x86_64": "r12",
    "aarch64": "x19",
}

NAME_SLOTS = ("m", "n")
TYPE_SLOTS = ("T", "U", "V", "W")
BUILTIN_PREFIXES = ("CallExpr.BI", "AtomicExpr.AO")


def entry_functions_for_operator(operator_name: str) -> Tuple[str, ...]:
    """Return the Clang Sema and CodeGen entry functions for a GNU C HiOp."""
    clean = operator_name[len("Kept."):] if operator_name.startswith("Kept.") else operator_name
    family = clean.split(".")[0]
    return HIOP_ENTRY_FUNCTIONS.get(family, ())


def _format_constant_for_part(part: PartState0) -> str:
    """Format a constant token from constant_value_sets for a part."""
    cv = part.constant_value
    unqual = f"__typeof__(((void)0, (*({part.holder} *)0)))"
    if cv in ("zero", "0", "memory_order_relaxed"):
        return f"(({unqual})0)"
    if cv in ("one", "1"):
        return f"(({unqual})1)"
    if cv in ("negative", "-1"):
        return f"(({unqual})-1)"
    if cv == "bitwidth":
        return f"(({unqual})(sizeof({unqual}) * 8))"
    if cv == "in-range-positive":
        return f"(({unqual})3)"
    if cv == "power-of-two":
        return f"(({unqual})16)"
    if cv.lstrip("-").isdigit():
        return f"(({unqual}){cv})"
    return f"(({unqual})0)"

def _synthesize_part_access(
    part: PartState0,
    key: str,
    arch: str,
    fields: List[str],
    top_decls: List[str],
) -> Tuple[str, str]:
    """Return (expr_text, stand_in_text) for one PartState0 and append its field."""
    slot = part.slot
    holder = part.holder
    if slot in NAME_SLOTS:
        return slot, slot
    if slot in TYPE_SLOTS:
        return holder, holder

    stand_in = f"(*({holder} *)0)"
    if part.constant_value not in (None, "place"):
        expr = _format_constant_for_part(part)
        return expr, stand_in

    place = part.place
    if place == "bit-field":
        width = 1 if holder in ("_Bool", "bool") else 13
        bf_type = "_Bool" if holder in ("_Bool", "bool") else "unsigned int"
        fields.append(f"{bf_type} {slot} : {width};")
        expr = f"p->{slot}"
    elif place == "signed bit-field":
        fields.append(f"signed int {slot} : 13;")
        expr = f"p->{slot}"
    elif place == "vector element":
        vec_type = holder if holder in ("v4si", "v4sf", "v4ui", "v4df", "v4hi") else "v4si"
        fields.append(f"{vec_type} {slot}_vec;")
        expr = f"p->{slot}_vec[0]"
        stand_in = f"((*({vec_type} *)0)[0])"
    elif place in ("ext-vector element", "ext vector element"):
        ev_type = holder if holder in ("ev4si", "ev4sf", "ev4b") else "ev4si"
        fields.append(f"{ev_type} {slot}_ev;")
        expr = f"p->{slot}_ev.x"
        stand_in = f"((*({ev_type} *)0).x)"
    elif place == "matrix element":
        fields.append(f"m4x4f {slot}_mat;")
        expr = f"p->{slot}_mat[0][0]"
        stand_in = "((*(m4x4f *)0)[0][0])"
    elif place == "global register":
        reg_name = ARCH_GLOBAL_REG.get(arch, "s2")
        reg_var = f"reg_{key}_{slot}"
        top_decls.append(f'register {holder} {reg_var} __asm__("{reg_name}");')
        expr = reg_var
    else:
        fields.append(f"{holder} {slot};")
        expr = f"p->{slot}"

    if part.value_category in ("rvalue", "prvalue") and place in ("field", "ordinary"):
        expr = f"(+({expr}))"
    return expr, stand_in

def _fill_template(spelling: str, mapping: Dict[str, str]) -> str:
    return PLACEHOLDER.sub(lambda m: mapping.get(m.group(1), m.group(1)), spelling)


def entry_lines_from_state_info_0(
    state_info_0: StateInfo0,
    key: str = "k",
    arch: str = "riscv64",
    library_decl: str = "",
) -> List[str]:
    """Synthesize the hijacked function lines (`struct P_<key>` + `op_<key>`)
    directly from a `StateInfo0` token/state descriptor and the lowerer-derived
    HiOp relations (`load_hiop_relations`).
    """
    op = state_info_0.operator
    clean_name = op.name[len("Kept."):] if op.name.startswith("Kept.") else op.name
    kind = clean_name.split(".")[0]
    spelling = op.spelling.replace("->template ", "->").replace(".template ", ".")

    fields: List[str] = []
    top_decls: List[str] = []
    if library_decl:
        top_decls.append(library_decl)

    part_by_slot: Dict[str, PartState0] = {p.slot: p for p in state_info_0.parts}
    expr_map: Dict[str, str] = {}
    stand_in_map: Dict[str, str] = {}

    rel = load_hiop_relations().get(spelling, {})
    body_slots: Tuple[str, ...] = rel.get("bodies", ())
    const_slots: Tuple[str, ...] = rel.get("constants", ())
    never_bodies: Tuple[str, ...] = rel.get("never_bodies", ())
    asks: Optional[str] = rel.get("asks")
    needs_in_fn: Tuple[str, ...] = rel.get("needs_in_function", ())
    fn_ctx: str = rel.get("function_context", "void f(void)")
    is_stmt: bool = rel.get("is_statement", kind.endswith("Stmt"))

    for slot in op.operands:
        if slot in NAME_SLOTS:
            expr_map[slot] = slot
            stand_in_map[slot] = slot
            continue
        if is_stmt and slot in body_slots:
            expr_map[slot] = "(void)0"
            stand_in_map[slot] = "0"
            continue
        part = part_by_slot.get(
            slot,
            PartState0(slot=slot, holder="int", place="field", value_category="lvalue", constant_value=None),
        )
        if slot in const_slots and part.constant_value in (None, "place"):
            part = part._replace(constant_value=str(const_slots.index(slot)))
        expr, stand_in = _synthesize_part_access(part, key, arch, fields, top_decls)
        if never_bodies and slot not in body_slots and part.constant_value in (None, "place"):
            expr = f"(*(volatile __typeof__({expr}) *)&({expr}))"
        expr_map[slot] = expr
        stand_in_map[slot] = stand_in

    applied = _fill_template(spelling, expr_map)
    ret_type = "void"

    if is_stmt:
        if "AddrLabelExpr" in needs_in_fn:
            body = f"{applied}\n\tm: (void)&&m;"
        elif "LabelStmt" in needs_in_fn:
            body = f"{applied}\n\tm:;"
        elif not fn_ctx.startswith("void ") and op.operands and op.operands[0] in stand_in_map:
            ret_type = f"__typeof__(((void)0, {stand_in_map[op.operands[0]]}))"
            body = applied
        else:
            body = applied
    elif "LabelStmt" in needs_in_fn:
        fields.append("void *result;")
        body = f"p->result = ({applied});\n\tm:;"
    elif clean_name.startswith(BUILTIN_PREFIXES):
        stand_in_applied = _fill_template(spelling, stand_in_map)
        res_type = (
            f"__typeof_unqual__(__builtin_choose_expr("
            f"__builtin_types_compatible_p(__typeof__({stand_in_applied}), void), "
            f"0, ((void)0, {stand_in_applied})))"
        )
        fields.append(f"{res_type} result;")
        body = (
            f"__builtin_choose_expr("
            f"__builtin_types_compatible_p(__typeof__({applied}), void), "
            f"({applied}), "
            f"(p->result = __builtin_choose_expr("
            f"__builtin_types_compatible_p(__typeof__({applied}), void), "
            f"0, ({applied}))));"
        )
    else:
        stand_in_applied = _fill_template(spelling, stand_in_map)
        res_type = f"__typeof__(((void)0, {stand_in_applied}))"
        fields.append(f"{res_type} result;")
        body = f"p->result = ({applied});"

    field_str = " ".join(fields) if fields else "char unused_;"
    decl_prefix = (" ".join(top_decls) + " ") if top_decls else ""
    struct_line = f"{decl_prefix}struct P_{key} {{ {field_str} }};"
    return [
        struct_line,
        f"{ret_type} op_{key}(struct P_{key} *p) {{",
        f"\t{body}",
        "}",
    ]


def synthesize_entry_program(
    state_info_0: StateInfo0,
    key: str = "k",
    arch: str = "riscv64",
    extra_preamble: Tuple[str, ...] = (),
    library_decl: str = "",
) -> Tuple[str, str]:
    """Synthesize a complete C translation unit for the hijacked lowerer from StateInfo0.

    Returns (program_text, symbol_name).
    """
    lines = list(GNU_C_ENTRY_PREAMBLE) + list(extra_preamble) + [""]
    lines.extend(entry_lines_from_state_info_0(state_info_0, key=key, arch=arch, library_decl=library_decl))
    return "\n".join(lines) + "\n", f"op_{key}"
