---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.settling_the_ontology
status: draft
---

# SUPPORT — settling_the_ontology

The tree under `map_HiOp_to_unit`, being re-drawn at the owner's word. Started
2026-10-15 in PCHQ's brainstorming conversation. Nothing has moved yet: the
tree below is the proposal, and the plan's tree is still the one
`bash PRIVATE/PseudoCoup/hq.sh tree` prints.

the owner, 2026-10-15:

> what an unbelievable mess this is. it might actually be faster to start
> over and re-create the ontology from scratch then to try and disentangle
> this.

> the tree could still represent the code. so yes things would need to move.
> and yeah theres absolutely a cost and i really didnt want to be in this
> position but its significantly less costly than constantly trying to work
> within a mess.

> so lets focus on settling the ontology first. record what you need to
> record. if there are things you know you can update, update them.

It replaces the proposal of 2026-10-14 in
[SUPPORT_tree_now_and_proposed.html](SUPPORT_tree_now_and_proposed.html)
, which moved code within today's tree and added no node.

## 1. the owner's sketch, as given

Block A. the owner's tree, 2026-10-15, as written.

```
map_HiOp_to_unit
└── model_lang_components
|   └── HiOps
|   └── holders
|   └── infra
|   └── context
|   └── HiOp_complexities
└── lower_HiOp
|   └── standard_HiOp_wrapper
└── lang_models
|   └── gnu_c
|   └── go
...
```

## 2. the owner's decisions since

Table 1. Each decision after the sketch, in the owner's words, 2026-10-15.

| decision | the owner's words |
|---|---|
| `model_lang_components` is named `model_lang_parts` | "i might change components for parts. `model_lang_parts`. shorter, same info." |
| a sixth part, `HiOp_configurations`, holds `dependent_HiOp_reader` and `HiOp_configuration_solver` | "`model_lang_components -> HiOp_configurations`?", to Claude's proposal of a part for each HiOp's configuration: its bodies, and the HiOps that can only stand inside it |
| `extract_unit_from_LoHiOp` goes under `lower_HiOp` | "`lower_HiOp` produces `LoHiOps`. if anything, i would say `extract_unit_from_LoHiOp` would belong under `lower_HiOp`." |
| `complex_signature_reader` belongs with the readers, not in a separate `lowerers` folder | "what? why wouldnt it be part of the reader?", to Claude's proposal of a `lowerers` folder for it |
| `complex_signature_reader` goes under `HiOps`, not `holders`: what it reads is which holders each operator accepts, so each operator's HiOp variants | "why wouldnt it go under `model_lang_parts.HiOps`? because there are HiOp spellings and HiOp variants or whatever. but idk. if you have a reason for it being there." Claude had no reason that holds |
| clang's own pieces (the `clang.py` in three nodes, `cpp_code`, the C++ and clang parts of the walk) stay under `lang_models` → `gnu_c`; C++'s lowerer pieces go under C++ when it comes | "most languages have their own lowerer. theres only two languages that we are modelling that use clang. we can keep clang stuff under gnu_c and when we get to C++, we can put lowerer stuff under it too. but maybe it will be more clear later, especially after we have thoroughly cleaned up this mess." |
| the tree represents the code, and the code moves with it | "the tree could still represent the code. so yes things would need to move." |
| `DRY_mask_maker` is named `mask_maker`; its comments keep what DRY means (2026-10-16) | "i want to change `DRY_mask_maker` to `mask_maker`. comments inside can still example what its about DRY and what its doing." |

## 3. The tree, proposed

Figure 1. Every node under `map_HiOp_to_unit` today, placed in the owner's tree.
`(new)` marks a node that doesn't exist today. A node keeps its sub-nodes
unless §4 says otherwise. It shows placement only, not status.

```
map_HiOp_to_unit
├── dict_of_lang_HiOps
├── model_lang_parts                  (new)
│   ├── HiOps                         (new)
│   │   ├── operator_reader
│   │   └── complex_signature_reader
│   ├── holders                       (new)
│   │   └── holder_reader
│   ├── infra                         (new)
│   ├── context                       (new)
│   │   └── model_contexts
│   ├── HiOp_complexities             (new)
│   │   └── HiOp_sorter
│   └── HiOp_configurations           (new)
│       ├── dependent_HiOp_reader
│       └── HiOp_configuration_solver
├── lower_HiOp
│   ├── standard_HiOp_wrapper
│   ├── compile_standard_source
│   ├── read_words_at_symbol
│   └── extract_unit_from_LoHiOp
├── mask_maker                        (was DRY_mask_maker)
└── lang_models                       (was langs)
    ├── gnu_c
    └── go                            (new)
```

Table 2. Each node of today, where Figure 1 puts it, and whose placement it
is. "Claude's" placements wait for the owner's word.

| today | proposed | whose |
|---|---|---|
| `extract_lang_vocab` | none: its sub-nodes go into `model_lang_parts` | the owner's sketch |
| `extract_lang_vocab` → `operator_reader` | `model_lang_parts` → `HiOps` → `operator_reader` | the owner's sketch (`HiOps`); Claude's (as its sub-node) |
| `extract()`, `extract_lang_vocab`'s own loop: operators crossed with holders, the variants clang accepts kept | `model_lang_parts` → `HiOps` | Claude's |
| `extract_lang_vocab` → `holder_reader` | `model_lang_parts` → `holders` → `holder_reader` | the owner's sketch (`holders`); Claude's (as its sub-node) |
| `complex_signature_reader` | `model_lang_parts` → `HiOps` → `complex_signature_reader` | the owner (Table 1) |
| `extract_lang_infra` (on the work list, no node yet) | `model_lang_parts` → `infra` | the owner's sketch |
| `model_HiOps` → `model_contexts` | `model_lang_parts` → `context` → `model_contexts` | the owner's sketch (`context`); Claude's (as its sub-node) |
| `model_HiOps` → `HiOp_sorter` | `model_lang_parts` → `HiOp_complexities` → `HiOp_sorter` | the owner's sketch (`HiOp_complexities`); Claude's (as its sub-node) |
| `model_HiOps`, the modelling itself (simple HiOps first, then hybrid, then complex) | `model_lang_parts` → `HiOps` | Claude's |
| `extract_lang_vocab` → `dependent_HiOp_reader`, `HiOp_configuration_solver` | `model_lang_parts` → `HiOp_configurations` | the owner |
| `standard_HiOp_wrapper` | `lower_HiOp` → `standard_HiOp_wrapper` | the owner's sketch |
| `lower_HiOp` → `compile_standard_source`, `read_words_at_symbol` | unchanged | |
| `extract_unit_from_LoHiOp` | `lower_HiOp` → `extract_unit_from_LoHiOp` | the owner |
| `langs` → `gnu_c` | `lang_models` → `gnu_c` | the owner's sketch |
| none | `lang_models` → `go` | the owner's sketch |
| `dict_of_lang_HiOps` | unchanged: what the whole tree fills, its keys from `HiOps` and its values from `lower_HiOp` | Claude's |
| `DRY_mask_maker` | `mask_maker`, renamed | the owner (Table 1) |

## 4. Still open

1. `complex_signature_reader`'s `lowering_reader` reads clang's lowering
   code, not its checking code: does it stay with it under `HiOps`, or go
   to `context` or `lower_HiOp`?
2. The names under each part: does each part keep today's node as its
   sub-node (`HiOp_sorter` under `HiOp_complexities`), or take its place?
3. Claude's placements in Table 2: `extract()`'s loop and the modelling
   under `HiOps`, and `dict_of_lang_HiOps` where it is.

Settled on 2026-10-15 and moved to Table 1: where clang's own pieces go.

## 5. What moves with the tree

- The code: each node's code moves with it, under
  `Projects/PseudoArch/map_HiOp_to_unit/`, and every import of it changes,
  the research scripts' included.
- The plan: the nodes move with the plan's own tools, which keep each
  node's `id`.
- The work list: the items whose node moves
  ([SUPPORT_work_remaining.md](SUPPORT_work_remaining.md)) wait for the
  tree.

## 6. How it goes live: PlanPlan's `.NASCENT`

PlanPlan's `framework/PROTOCOL.md` §6d (the owner, 2026-10-15) gives the way.
The new CORE and the new nodes are built in `map_HiOp_to_unit/.NASCENT/`,
which every tool skips. Today's nodes stay live, and each moves once, at
the end, with everything it holds then. Table 2 becomes
`.NASCENT/SUPPORT_migration_map.md`, whose frontmatter lists every node
`from:` and `to:` (`to: deleted`, `from: new`). Opened 2026-10-15 at
the owner's word: "please fill in the .NASCENT for `map_HiOps_to_unit` as best
you can." The map is `.NASCENT/SUPPORT_migration_map.md`.
