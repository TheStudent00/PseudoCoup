---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.equivalence_classes
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: equivalence_classes
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_3_equivalence_classes/CORE_0_0_0_0_2_4_0_3_equivalence_classes.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_3 — equivalence_classes

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.equivalence_classes
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [gnu_c](../CORE_0_0_0_0_2_4_0_gnu_c.md)

## sub_nodes

*(none yet)*

## definition

GNU C's pre-queried holder facts and canonical gate-predicate equivalence
class representatives:

- **`holder_facts.json` (`holder_facts_riscv64-runner_l14.json`):** exact Clang AST and
  LLVM IR predicate answers across all `180` GNU C holders (`outer` and
  `.inner` element/pointee levels).
- **`EQUIVALENCE_CLASS_HOLDERS` (`42` canonical representatives) + `TYPE_ONLY_HOLDERS` (`3` type-slot holders):**
  signed and unsigned integers (`int`, `unsigned int`, `short`, `unsigned short`,
  `char`, `signed char`, `unsigned char`, `long`, `__int128`, `volatile int`,
  `_Bool`, `_BitInt(37)`), floating-point (`_Float16`, `float`, `double`,
  `long double`), complex (`cf16`, `double _Complex`, `_Complex int`),
  pointers (`int *`, `char *`, `void *`, `fnptr`, `noderef_int_ptr`,
  `noderef_struct_ptr`, `nullptr_t`), arrays (`arr4`, `vla`), GCC and
  ext-vectors (`v4si`, `v4ui`, `v4hi`, `v4sf`, `v4df`, `ev4si`, `ev4sf`,
  `ev4b`, `const v4si`), records/unions/enums/atomics (`struct S`,
  `struct S_anon`, `union U`, `enum E`, `_Atomic int`), and type-only slots
  (`fntype`, `void`, `struct I`), together with `HOLDER_PREAMBLE`.
