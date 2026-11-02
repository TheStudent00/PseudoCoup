---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.python_and_cpython_standard_hiop_wrapper
type: support
belongs_to: CORE_0_0_0_0_2_map_HiOp_to_unit.md
status: active
date: 2026-10-30
author: Gemini
---

# SUPPORT: Strictly-Typed Python, Cython, and GNU C Specification of `standard_HiOp_wrapper`

<details open>
<summary><b>1. Strictly-Typed Python Wrapper Specification</b></summary>

```python
# ==============================================================================
# STRICTLY-TYPED PYTHON SPECIFICATION: standard_HiOp_wrapper
# Clean high-level typed pseudo-notation communicating wrapper semantics.
# Invariant: Each wrapper isolates the HiOp on its own line for DWARF line-slicing.
# ==============================================================================

# --- Preamble & Type Helpers ---
# dummy(T): synthesizes an lvalue expression of type T for static return type evaluation.
# rvalue_typeof(E): decays type (strips top-level const/_Atomic qualifiers, decays array to ptr).
# unqual_typeof(E): strips all qualifiers (for __builtin_align_up/down/nondeterministic_value).
# discard(E): silences unused-value warnings for void / statement operations.
# deref(p): explicit pointer dereference (*p).
# label_addr(m): GNU C address-of-label value (&&m).

from typing import Annotated

# ------------------------------------------------------------------------------
# 1. EXPRESSION HIOP: p.result = (p.a + p.b)
# Struct holds operands; result slot holds decayed rvalue type; HiOp is parenthesized.
# ------------------------------------------------------------------------------
class P_expr:
    a: int32
    b: float64
    result: rvalue_typeof(dummy(int32) + dummy(float64))  # float64; mutable rvalue

def op_expr(p: P_expr) -> None:
    # Sliced Unit Line: Isolated on its own line with leading indent for DWARF line-table tagging
    p.result = (p.a + p.b)

# ------------------------------------------------------------------------------
# 2. VOID CALL / STATEMENT-ONLY HIOP: discard(fn(p.a))
# Mutation / side-effect only: no result slot is declared in P_k; discard() silences warnings.
# ------------------------------------------------------------------------------
class P_void:
    a: ptr[int32]
    b: int32
    c: int32
    # No result field declared

def op_void(p: P_void) -> None:
    # Sliced Unit Line: discard() silences compiler unused-value warning
    discard(__atomic_store_n(p.a, p.b, p.c))

# ------------------------------------------------------------------------------
# 3. SHORT-CIRCUIT EXPRESSION HIOP: p.result = (part_k_a() and part_k_b())
# Operands come from inert function calls to prevent compiler constant-folding of branches.
# ------------------------------------------------------------------------------
def part_sc_a() -> int32: ...
def part_sc_b() -> int32: ...

class P_short_circuit:
    result: rvalue_typeof(dummy(int32) and dummy(int32))

def op_short_circuit(p: P_short_circuit) -> None:
    # Sliced Unit Line: Both sides evaluated dynamically through inert calls
    p.result = (part_sc_a() and part_sc_b())

# ------------------------------------------------------------------------------
# 4. CONTROL STATEMENT HIOP: if part_k_a(): part_k_b() else: part_k_c()
# Conditions are typed inert calls; body statements are void inert calls; dummy struct.
# ------------------------------------------------------------------------------
def part_ctrl_a() -> int32: ...  # Condition value slot (typed)
def part_ctrl_b() -> None: ...   # Then-branch statement slot (void)
def part_ctrl_c() -> None: ...   # Else-branch statement slot (void)

class P_control:
    unused_: int8                # Minimal placeholder container

def op_control(p: P_control) -> None:
    # Sliced Unit Line: Preserves control-flow branches without compiler elimination
    if part_ctrl_a(): part_ctrl_b()
    else: part_ctrl_c()

# ------------------------------------------------------------------------------
# 5. JUMP-IN-CONTEXT HIOPS: Loop jump and Value return
# Enclosing context satisfies syntax; inert test + fallback ensure reached code after jump.
# ------------------------------------------------------------------------------
def part_jmp_test() -> int32: ...      # Dynamic condition keeps both taken and fallthrough paths alive
def part_jmp_skipped() -> None: ...    # Reached code prevents jump from collapsing to next word
def part_ret_val() -> int32: ...       # Inert operand value for return

class P_jump:
    unused_: int8                      # Minimal placeholder container

# 5a. Loop Jump (break / continue): Must reside within loop context
def op_break(p: P_jump) -> None:
    while True:                        # Required enclosing loop context
        # Sliced Unit Line: Real branch emitted over reached fallback code
        if part_jmp_test(): break
        part_jmp_skipped()

# 5b. Value Return (return a): Wrapper return type matches operand; fallthrough satisfies compiler
def op_return(p: P_jump) -> int32:
    # Sliced Unit Line: Dynamic return of held operand value
    if part_jmp_test(): return part_ret_val()
    part_jmp_skipped()
    return 0                           # Fallthrough return satisfies non-void function signature

# ------------------------------------------------------------------------------
# 6. SPECIAL CASES & COMPILER WORKAROUNDS
# ------------------------------------------------------------------------------

# 6a. Constant Operand: A(0) (__atomic_always_lock_free requires compile-time integer constant)
# Literal zero replaces runtime field p.a; slot 'a' is omitted from struct P_k.
class P_const_op:
    b: ptr[void]                       # Only runtime operands remain as struct fields
    result: bool

def op_const(p: P_const_op) -> None:
    # Sliced Unit Line: Typed constant zero int32(0) satisfies compiler constant-evaluation requirement
    p.result = __atomic_always_lock_free(int32(0), p.b)

# 6b. Inert-by-Address for float16 / bfloat16: *part_k_a()
# ARM / RISC-V ABIs forbid returning half-precision floats by value; inert part returns pointer.
def part_fp16_a() -> ptr[float16]: ...  # Returned by address to satisfy ABI

class P_by_addr:
    result: float16

def op_by_addr(p: P_by_addr) -> None:
    # Sliced Unit Line: Explicit pointer dereference reads half-precision value
    p.result = deref(part_fp16_a())

# 6c. Flexible Array Member: counted_by (__builtin_counted_by_ref)
# Requires trailing flexible array member with explicit count field; stores through result.
class P_flex_array:
    count: int32
    a: Annotated[list[elem_type(A)], counted_by("count")]  # Flexible array member

def op_flex_array(p: P_flex_array) -> None:
    # Sliced Unit Line: Stores through pointer because builtin answer cannot be assigned or returned
    deref(__builtin_counted_by_ref(p.a)) = 0

# 6d. Local Label Address: &&m (AddrLabelExpr)
# Label 'm' only exists inside op_k body; result cannot be declared in global struct P_k.
def part_label_target() -> None: ...

class P_label_addr:
    unused_: int8

def op_label_addr(p: P_label_addr) -> None:
    # Sliced Unit Line: Local variable holds label address; label follows with inert call
    result: label_type = label_addr(m)
    label m: part_label_target()
```

</details>

<details open>
<summary><b>2. Cython / Strictly-Typed CPython Wrapper Specification</b></summary>

```cython
# ==============================================================================
# CYTHON / STRICTLY-TYPED CPYTHON SPECIFICATION: standard_HiOp_wrapper
# Exact 1-to-1 mapping of lowering wrapper structures into Cython cdef notation.
# Invariant: Each wrapper isolates the HiOp on its own line for DWARF line-slicing.
# ==============================================================================

# --- Preamble & Type Helpers ---
# typeof(rvalue(E)): evaluates expression E and decays qualifiers (strips const/_Atomic).
# unqual_typeof(E): strips all qualifiers (scoped to __builtin_align_up/down/nondeterministic_value).
# discard(E): silences unused-value warnings for void / statement operations.

# ------------------------------------------------------------------------------
# 1. EXPRESSION HIOP: p.result = (p.a + p.b)
# Struct holds operands; result slot holds decayed rvalue type; HiOp is parenthesized.
# ------------------------------------------------------------------------------
cdef struct P_expr:
    int32 a
    float64 b
    typeof(rvalue(int32 + float64)) result  # float64; mutable rvalue

cdef void op_expr(P_expr *p):
    # Sliced Unit Line: Isolated on its own line with leading indent for DWARF line-table tagging
    p.result = (p.a + p.b)

# ------------------------------------------------------------------------------
# 2. VOID CALL / STATEMENT-ONLY HIOP: discard(fn(p.a))
# Mutation / side-effect only: no result slot is declared in P_k; discard() silences warnings.
# ------------------------------------------------------------------------------
cdef struct P_void:
    int32 *a
    int32 b
    int32 c
    # No result field declared

cdef void op_void(P_void *p):
    # Sliced Unit Line: discard() silences compiler unused-value warning
    discard(__atomic_store_n(p.a, p.b, p.c))

# ------------------------------------------------------------------------------
# 3. SHORT-CIRCUIT EXPRESSION HIOP: p.result = (part_k_a() and part_k_b())
# Operands come from inert function calls to prevent compiler constant-folding of branches.
# ------------------------------------------------------------------------------
cdef extern int32 part_sc_a()
cdef extern int32 part_sc_b()

cdef struct P_short_circuit:
    typeof(rvalue(int32 and int32)) result

cdef void op_short_circuit(P_short_circuit *p):
    # Sliced Unit Line: Both sides evaluated dynamically through inert calls
    p.result = (part_sc_a() and part_sc_b())

# ------------------------------------------------------------------------------
# 4. CONTROL STATEMENT HIOP: if part_k_a(): part_k_b() else: part_k_c()
# Conditions are typed inert calls; body statements are void inert calls; dummy struct.
# ------------------------------------------------------------------------------
cdef extern int32 part_ctrl_a()  # Condition value slot (typed)
cdef extern void part_ctrl_b()   # Then-branch statement slot (void)
cdef extern void part_ctrl_c()   # Else-branch statement slot (void)

cdef struct P_control:
    int8 unused_                 # Minimal placeholder container

cdef void op_control(P_control *p):
    # Sliced Unit Line: Preserves control-flow branches without compiler elimination
    if part_ctrl_a(): part_ctrl_b()
    else: part_ctrl_c()

# ------------------------------------------------------------------------------
# 5. JUMP-IN-CONTEXT HIOPS: Loop jump and Value return
# Enclosing context satisfies syntax; inert test + fallback ensure reached code after jump.
# ------------------------------------------------------------------------------
cdef extern int32 part_jmp_test()      # Dynamic condition keeps both taken and fallthrough paths alive
cdef extern void part_jmp_skipped()    # Reached code prevents jump from collapsing to next word
cdef extern int32 part_ret_val()       # Inert operand value for return

cdef struct P_jump:
    int8 unused_                       # Minimal placeholder container

# 5a. Loop Jump (break / continue): Must reside within loop context
cdef void op_break(P_jump *p):
    while True:                        # Required enclosing loop context
        # Sliced Unit Line: Real branch emitted over reached fallback code
        if part_jmp_test(): break
        part_jmp_skipped()

# 5b. Value Return (return a): Wrapper return type matches operand; fallthrough satisfies compiler
cdef int32 op_return(P_jump *p):
    # Sliced Unit Line: Dynamic return of held operand value
    if part_jmp_test(): return part_ret_val()
    part_jmp_skipped()
    return 0                           # Fallthrough return satisfies non-void function signature

# ------------------------------------------------------------------------------
# 6. SPECIAL CASES & COMPILER WORKAROUNDS
# ------------------------------------------------------------------------------

# 6a. Constant Operand: A(0) (__atomic_always_lock_free requires compile-time integer constant)
# Literal zero replaces runtime field p.a; slot 'a' is omitted from struct P_k.
cdef struct P_const_op:
    void *b                            # Only runtime operands remain as struct fields
    bint result

cdef void op_const(P_const_op *p):
    # Sliced Unit Line: Typed constant zero <int32>0 satisfies compiler constant-evaluation requirement
    p.result = __atomic_always_lock_free(<int32>0, p.b)

# 6b. Inert-by-Address for float16 / bfloat16: *part_k_a()
# ARM / RISC-V ABIs forbid returning half-precision floats by value; inert part returns pointer.
cdef extern float16 *part_fp16_a()     # Returned by address to satisfy ABI

cdef struct P_by_addr:
    float16 result

cdef void op_by_addr(P_by_addr *p):
    # Sliced Unit Line: Explicit pointer dereference reads half-precision value
    p.result = part_fp16_a()[0]

# 6c. Flexible Array Member: counted_by (__builtin_counted_by_ref)
# Requires trailing flexible array member with explicit count field; stores through result.
cdef struct P_flex_array:
    int32 count
    elem_type_a a[0]                   # Flexible array member (annotated with counted_by(count))

cdef void op_flex_array(P_flex_array *p):
    # Sliced Unit Line: Stores through pointer because builtin answer cannot be assigned or returned
    __builtin_counted_by_ref(p.a)[0] = 0

# 6d. Local Label Address: &&m (AddrLabelExpr)
# Label 'm' only exists inside op_k body; result cannot be declared in global struct P_k.
cdef extern void part_label_target()

cdef struct P_label_addr:
    int8 unused_

cdef void op_label_addr(P_label_addr *p):
    # Sliced Unit Line: Local variable holds label address; label follows with inert call
    cdef void *result = &&m
    m: part_label_target()
```

</details>

<details open>
<summary><b>3. GNU C Wrapper Specification (Actual Emitted C)</b></summary>

```c
// ==============================================================================
// GNU C SPECIFICATION (ACTUAL EMITTED WRAPPER): standard_HiOp_wrapper
// Exact C code generated by standard_HiOp_wrapper.py compiled at -O0 -g.
// Invariant: Sliced Unit Line sits on its own line with leading '\t' for DWARF line-slicing.
// ==============================================================================

// --- Macro Definitions Emitted by lower_gnu_c ---
// C_STAND_IN:      (*(T *)0)                      Fake lvalue for static type deduction
// C_RESULT_TYPE:   __typeof__(((void)0, EXPR))     Comma decays array->ptr and strips const/_Atomic
// C_UNQUAL_TYPE:   __typeof_unqual__(((void)0, E)) Scoped to __builtin_align_up/down/nondet

// ------------------------------------------------------------------------------
// 1. EXPRESSION HIOP: p->result = (p->a + p->b)
// Struct holds operands; result slot holds decayed rvalue type; HiOp is parenthesized.
// ------------------------------------------------------------------------------
struct P_expr {
    int32 a;
    float64 b;
    // Comma operator ((void)0, ...) strips const and _Atomic qualifiers so result is assignable
    __typeof__(((void)0, (*(int32 *)0) + (*(float64 *)0))) result;
};

void op_expr(struct P_expr *p) {
	p->result = (p->a + p->b);  // <-- Sliced Unit Line (isolated \t line for DWARF line-table)
}

// ------------------------------------------------------------------------------
// 2. VOID CALL / STATEMENT-ONLY HIOP: (void)(fn(p->a))
// Mutation / side-effect only: no result slot is declared in P_k; (void) silences warnings.
// ------------------------------------------------------------------------------
struct P_void {
    int32 *a;
    int32 b;
    int32 c;
    // No result field declared
};

void op_void(struct P_void *p) {
	(void)(__atomic_store_n(p->a, p->b, p->c));  // <-- Sliced Unit Line ((void) silences -Wunused-value)
}

// ------------------------------------------------------------------------------
// 3. SHORT-CIRCUIT EXPRESSION HIOP: p->result = (part_k_a() && part_k_b())
// Operands come from inert function calls to prevent compiler constant-folding of branches.
// ------------------------------------------------------------------------------
int32 part_sc_a(void);
int32 part_sc_b(void);

struct P_short_circuit {
    __typeof__(((void)0, (*(int32 *)0) && (*(int32 *)0))) result;
};

void op_short_circuit(struct P_short_circuit *p) {
	p->result = (part_sc_a() && part_sc_b());  // <-- Sliced Unit Line
}

// ------------------------------------------------------------------------------
// 4. CONTROL STATEMENT HIOP: if (part_k_a()) part_k_b(); else part_k_c();
// Conditions are typed inert calls; body statements are void inert calls; dummy struct.
// ------------------------------------------------------------------------------
int32 part_ctrl_a(void);  // Condition value slot (typed)
void part_ctrl_b(void);   // Then-branch statement slot (void)
void part_ctrl_c(void);   // Else-branch statement slot (void)

struct P_control {
    char unused_;         // Minimal placeholder container
};

void op_control(struct P_control *p) {
	if (part_ctrl_a()) part_ctrl_b(); else part_ctrl_c();  // <-- Sliced Unit Line
}

// ------------------------------------------------------------------------------
// 5. JUMP-IN-CONTEXT HIOPS: Loop jump and Value return
// Enclosing context satisfies syntax; inert test + fallback ensure reached code after jump.
// ------------------------------------------------------------------------------
int part_jmp_test(void);      // Dynamic condition keeps both taken and fallthrough paths alive
void part_jmp_skipped(void);  // Reached code prevents jump from collapsing to next word
int32 part_ret_val(void);     // Inert operand value for return

struct P_jump {
    char unused_;             // Minimal placeholder container
};

// 5a. Loop Jump (break / continue): Must reside within loop context (for (;;))
void op_break(struct P_jump *p) {
	for (;;) { if (part_jmp_test()) break; part_jmp_skipped(); }  // <-- Sliced Unit Line
}

// 5b. Value Return (return a): Wrapper return type matches operand; fallthrough satisfies compiler
int32 op_return(struct P_jump *p) {
	if (part_jmp_test()) return part_ret_val(); part_jmp_skipped(); return 0;  // <-- Sliced Unit Line
}

// ------------------------------------------------------------------------------
// 6. SPECIAL CASES & COMPILER WORKAROUNDS
// ------------------------------------------------------------------------------

// Case 6a: Constant Operand: A(0) (__atomic_always_lock_free requires compile-time integer constant)
// Literal zero replaces runtime field p->a; slot 'a' is omitted from struct P_k.
struct P_const_op {
    void *b;                  // Only runtime operands remain as struct fields
    _Bool result;
};

void op_const(struct P_const_op *p) {
	// Sliced Unit Line: Compile-time constant zero passed to satisfy Clang's ExprConstant requirement
	p->result = (__atomic_always_lock_free(((__typeof__(((void)0, (*(int32 *)0))))0), p->b));
}

// Case 6b: Inert-by-Address for float16 / bfloat16: *part_k_a()
// ARM / RISC-V ABIs forbid returning half-precision floats by value; inert part returns pointer.
__fp16 *part_fp16_a(void);    // Returned by address to satisfy ABI

struct P_by_addr {
    __typeof__(((void)0, *part_fp16_a())) result;
};

void op_by_addr(struct P_by_addr *p) {
	// Sliced Unit Line: Explicit pointer dereference reads half-precision value
	p->result = (*part_fp16_a());
}

// Case 6c: Flexible Array Member: counted_by (__builtin_counted_by_ref)
// Requires trailing flexible array member with explicit count field; stores through result.
struct P_flex_array {
    int count;
    __typeof__((*(elem_type_a *)0)[0]) a[] __attribute__((counted_by(count)));
};

void op_flex_array(struct P_flex_array *p) {
	// Sliced Unit Line: Stores through pointer because builtin answer cannot be assigned or returned
	*__builtin_counted_by_ref(p->a) = 0;
}

// Case 6d: Local Label Address: &&m (AddrLabelExpr)
// Label 'm' only exists inside op_k body; result cannot be declared in global struct P_k.
void part_label_target(void);

struct P_label_addr {
    char unused_;
};

void op_label_addr(struct P_label_addr *p) {
	// Sliced Unit Line: Local variable holds label address; label follows with inert call
	__typeof__(&&m) result = (&&m); m: part_label_target();
}
```

</details>
