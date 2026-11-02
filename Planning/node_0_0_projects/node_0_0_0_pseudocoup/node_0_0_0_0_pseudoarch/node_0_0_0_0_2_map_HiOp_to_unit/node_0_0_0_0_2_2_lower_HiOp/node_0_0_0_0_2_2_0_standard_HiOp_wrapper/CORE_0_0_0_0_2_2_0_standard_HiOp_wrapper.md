---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper
level: 6
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.standard_HiOp_wrapper
designation: code (module)
node:
    name: standard_HiOp_wrapper
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_0_standard_HiOp_wrapper/CORE_0_0_0_0_2_2_0_standard_HiOp_wrapper.md
super_node:
    name: lower_HiOp
    path: ../CORE_0_0_0_0_2_2_lower_HiOp.md
sub_nodes: []
---

# CORE 0_0_0_0_2_2_0 — standard_HiOp_wrapper

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper
- **level:** 6
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.standard_HiOp_wrapper

## super_node

- [lower_HiOp](../CORE_0_0_0_0_2_2_lower_HiOp.md)

## sub_nodes

*(none yet)*

## definition

A parameter is a value the function owns, so a write to it is dead
and the compiler deletes it — which is why `a++` lowers to a bare
return and `a!` to nothing at all.

Held, the holders are fields of a struct the CALLER allocates and the
function has only a pointer, so every write the HiOp performs has to
be emitted. It recovers three families the bare wrapper destroyed:
mutation, constant folding, and short-circuit evaluation.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant

## abstract design

Added 2026-10-07 by Claude (Opus 5.5), at the owner's word: "i suppose we can
note the abstract design in its CORE". The standard-form is the owner's: it "uses a
container-wrapper instead of the original function-warpper" (log 302, as
written). The
four parts below, their wording and the helper names in Block A are mine,
read from that and from the code that writes the standard-form today. None of
the helper names is a sub-node.

Block A. The standard-form in every language: the same four parts (lines 2 to
5), each written in the language's own words. Line labels on the right.

```python
def standard_HiOp_wrapper(lang, key):
    template = held_templates[lang]                     # 1  one row per language: how it writes each part
    container = container_of(template, key)             # 2  one field per operand, of its holder, and one for the result
    function = function_of(template, key)               # 3  a function given only a reference to the container
    applied = HiOp_over_fields(template, key)           # 4  the key's operator applied to the fields
    body = result_stored(template, applied)             # 5  the result written back into the container
    source = standard_source(container, function, body)     # 6  the text, and the name of its function
    return source
```

- Line 1: what differs between languages is the words each part is written
  in, not the parts. `held_templates` is a table with one row per language.
- Line 2: the container is the struct the CALLER allocates (definition,
  above).
- Line 5 is what makes the form held: the compiler may delete a write to a
  value the function owns, but not a write into memory the caller owns.
- Line 6: the function's name is the symbol `lower_HiOp` reads the machine
  words at.

Table 1. Part of one row of `held_templates`, for three languages, filled for
`a + b` on two 32-bit ints. GNU C's column is the real program for `+` that
log 377 lowered (`what_clang_writes/all_architectures/probes/e0025.c`); Go's
and Rust's are what the format strings of `standard_cell_lines` (named
`standard_HiOp_wrapper` since 2026-10-13, log 454) write for the same operator.

| part | GNU C | Go | Rust |
|---|---|---|---|
| container | `struct P_25 { int a; int b; __typeof__(((void)0, (*(int *)0) + (*(int *)0))) result; };` | `type P_k struct { a int32; b int32 }` | `#[repr(C)] pub struct P_k { pub a: i32, pub b: i32 }` |
| function | `void op_25(struct P_25 *p)` | `func op_k(p *P_k)` | `pub fn op_k(p: &mut P_k)` |
| a field | `p->a` | `p.a` | `p.a` |
| result stored | `p->result = (p->a + p->b);` | not yet: `r := (p.a + p.b); _ = r` | not yet: `let r = (p.a + p.b); let _ = r;` |

The language rules a row of words cannot carry, each written once per
language:

- Naming the result's holder in the container. GNU C writes `__typeof__`
  and C++ `decltype`. Go, Rust and Java have no `typeof`, so the field's
  holder cannot be written from the operands, which is why their result sits
  in a local today (Table 1, last row).
- A statement has no result. One that only stands inside another statement
  is held inside it (`C_STATEMENT_CONTEXT`): `break;` and `continue;` in a
  `for (;;)`, `goto m;` before its label, `goto *a;` before a label whose
  address is taken, `case` in a switch on a value, and `default` beside a
  case. A switch's body gets a case label before it. `return a;`'s held
  function answers the value `a` reads, since clang refuses a value returned
  from a function that answers nothing.
- A jump needs reached code between it and its target, or the compiler writes
  nothing for that code and the jump lands on the very next word (log 399).
  So every statement that jumps (`C_JUMPS`: `break;`, `continue;`, `goto m;`,
  `goto *a;`, `return a;`, `return;`) sits behind an inert test, with an inert
  call after it: `for (;;) { if (part_k_test()) break; part_k_skipped(); }`,
  `if (part_k_test()) return part_k_a(); part_k_skipped();`. The test lets a
  path skip the jump and reach the call, so the jump goes over it, as it does
  in real code (zlib's `inflate.c`, log 400). `break;` and `goto m;` at the owner's
  word, 2026-10-09: "okay go ahead and make both corrections to the
  held-form" (log 402). The other four since log 405, after the owner asked the
  same day: "should we not make `GNU-C` current with the most advanced
  design?"
- A builtin that answers nothing (`void`) is held as the call alone, since
  no field can hold it.
- A control HiOp's parts are inert calls (the owner's idea, 2026-10-08: "having
  inert function bodies might actually solve that problem because the
  polyfill would be a nested structure of function calls"; tried in PCHQ log
  397, moved here at the owner's word in log 399: "would make sense to be in the
  project PlanPlan and its implementation"). A control HiOp is a statement,
  or `a && b`, `a || b`, `a ? b : c`, `a ?: b`. Each part is a call to a
  function declared and never defined, so the compiler keeps every part, and
  the HiOp's Unit is its own jumps and tests with a call where each part
  goes. A body is a call to `void part_<key>_<letter>(void)`. A value is a
  call returning the value the HiOp reads from its holder: the holder's type
  through a comma, so `const`, `volatile` and `_Atomic` come off and an
  array comes back as its pointer (`__fp16` and `__bf16`, which no function
  returns, come back by address). The declarations share the struct's line,
  so the C text the standard-form writes for each HiOp stays two lines, as the
  grid reads it.
- An operand GNU C needs as a constant is written as a zero of the value read
  from its holder (`CONSTANT_FORM`, the holder's type through the same comma):
  a case label, and `__atomic_always_lock_free`'s size, which clang answers
  only by evaluating it as a constant (`CONSTANT_OPERANDS`; logs 398 and 399).
  An `_Atomic` holder's zero is so a plain one: written `((_Atomic int)0)`,
  clang refused it as a size (39 HiOps, elv2_l108). Such an operand has no
  field in the container, since nothing reads one (log 405).
- A builtin whose answer keeps its operand's qualifiers has its result field
  typed without them (`UNQUALIFIED_RESULTS`, `__typeof_unqual__`):
  `__builtin_align_up`, `__builtin_align_down` and
  `__builtin_nondeterministic_value`, which clang types as their operand's own
  type, `const` included. On a `const int` the field was `const`, and the
  standard function could not write it (37 HiOps, logs 398 and 400). For these
  three only: `__typeof_unqual__` for every HiOp also took `_Atomic` off a
  cast's type, and clang refused 676 casts (log 367), so every other result
  type is taken through a comma (log 402).
- An operand GNU C needs as a flexible array member (a struct's last field
  written with no length) is written as one, last in the container, with the
  count field `counted_by` names: `__builtin_counted_by_ref`'s
  (`FLEXIBLE_ARRAY_OPERANDS`). clang refuses that builtin's answer stored, so
  the standard function stores through it: `*__builtin_counted_by_ref(p->a) = 0;`
  (logs 400 and 402).

Where GNU C's routing comes from, since 2026-10-11 : which configuration each listing takes (its parts' roles, which expressions hold bodies, which statements jump, what a dependent-HiOp or a part stands in, which standard function answers a value or keeps its answer in a local) is read from the record of `HiOp_configuration_solver` by `DRY_mask_maker.routing_from_the_record` (`ROUTING`, rules R1 to R7); the tables and standard functions written by hand until then are kept as `*_BY_HAND`, the check.

GNU C's instance, in this node's own module since 2026-10-13 ,
`Projects/PseudoArch/map_HiOp_to_unit/standard_HiOp_wrapper.py`: `standard_HiOp_wrapper`
(lines 121 to 246; it was named `standard_cell_lines`), and from line 314 the inert
parts, `held_statement_lines` (line 532), `statement_in_context` (line 636),
`jump_over_reached_code` (line 700), `inert_expression_lines` (line 721),
`constant_operands` (line 794), `result_type_of` (line 810) and
`flexible_array_lines` (line 821). The routing is handed to it:
`DRY_mask_maker.standard_cell_lines` hands it `ROUTING`. Until log 454 the code
was in `DRY_mask_maker.py`, whose comment said it would move here when this
node was coded.

The standard-form for any language, written out: its rules, its five steps as
descriptive code in log 373's form, and instances in GNU C and Python, with
where GNU C's code does each step:
[SUPPORT_standard_form_for_any_language.md](SUPPORT_standard_form_for_any_language.md)
(log 404 §2, put here at the owner's word in log 405). Block A above is the four
parts; that file's Block A is the whole standard-form.

The standard-form in the context of modelling abstraction, as its
configurations: a HiOp with N bodies, written as its parts `HiOp[0]` to
`HiOp[N-1]` (the owner's notation), and a depended-HiOp with its dependent-HiOps
inside; a draft for the owner to build on, nothing ruled (the owner, 2026-10-10):
[SUPPORT_standard_form_in_modelling_abstraction.md](SUPPORT_standard_form_in_modelling_abstraction.md).
