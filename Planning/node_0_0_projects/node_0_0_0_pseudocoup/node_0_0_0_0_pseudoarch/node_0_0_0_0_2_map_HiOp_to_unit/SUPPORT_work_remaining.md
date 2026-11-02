---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.work_remaining
status: draft
---

# SUPPORT — work_remaining

What must still be completed in `map_HiOp_to_unit`, to go through one or two
items at a time. Rewritten 2026-10-15 at the owner's word:

> make a list of things that must be completed within the `map_HiOp_to_unit`
> node that we need to go through. there are too many things in each
> response. there should be one or two things per response.

Only what remains is listed: an item leaves when it is done. Until
2026-10-15 this file held the nested-sector figures of 2026-10-05 and
2026-10-07; git keeps them. The record of every gap GNU C's vocabulary ever
had stays in `extract_lang_vocab`'s
[SUPPORT_gnu_c_vocab_what_is_missing.md](node_0_0_0_0_2_4_extract_lang_vocab/SUPPORT_gnu_c_vocab_what_is_missing.md).
"Shared" marks an item also on `pseudocoup`'s
[SUPPORT_gnu_c_work_remaining.md](../../SUPPORT_gnu_c_work_remaining.md),
which another conversation keeps.

First, at the owner's word of 2026-10-15, the tree: "so lets focus on settling
the ontology first." The draft is
[SUPPORT_settling_the_ontology.md](SUPPORT_settling_the_ontology.md). The
items below wait for it wherever it moves their code.

Table 1. What remains, in the order to go through it: `extract_lang_vocab`'s
items first, to settle that node, then the rest. It shows what remains and
who it waits on, not how long each takes.

| order | item | node | what remains | waits on |
|---|---|---|---|---|
| 1 | signatures dropped by the one-row check | `extract_lang_vocab` | the read-back asks clang only about the first row of each written form, and drops the whole form when clang makes another size of the builtin for that row: 165 of 1,237 forms, holding 23,045 signatures clang accepts. Shared | building it: the owner, 2026-10-15, "if it works, then yeah sure" |
| 2 | `__builtin_fpclassify`'s 32 HiOps | `extract_lang_vocab` | the read-back stops at `p->result =` and drops them. Shared | the owner's word |
| 3 | `extract()` makes its whole list every run | `extract_lang_vocab` | the owner's ruling of 2026-10-14 (log 462). The code still skips the combinations clang answered before, and the code that tries combinations and the standard-form's routing still sit in another module, outside their nodes (log 461). Shared | building it |
| 4 | a node for the read-back step | `extract_lang_vocab` | the step that checks clang reads each HiOp back as the operator written decides each HiOp's key, and has no plan node (log 463 §4) | the owner: its name |
| 5 | `complex_signature_reader` | `complex_signature_reader` | kept, to give the holders `extract()` tries, read from each operator's definition (the owner's idea, 2026-10-15; the plan of 2026-10-06, log 366 W5, never finished), and part of the reader (the owner, 2026-10-15: "why wouldnt it be part of the reader?"; proposed under `model_lang_parts` → `HiOps`). On 2026-10-01 its `checking_reader` read the 344 builtins clang 21.1.8 checks with its own code (marked `t`), for every language clang compiles: 139 of them are in GNU C's list, and 64 of those were read with no condition unread and no path stopped. Nothing in the product calls it yet; the product reads clang's code only for its operators (`operator_reader`) and where each dependent-HiOp may stand (`dependent_HiOp_reader`). Two of its parts already live elsewhere: `covered_vocabulary` (in `extract_lang_vocab/clang.py`) and `cpp_code` (used by `operator_reader`) | building it: the owner, 2026-10-15, "if it works, then yeah sure" |
| 6 | the owner's three classes in `HiOp_sorter`'s code | `model_HiOps` | the code sorts into two classes (log 367); the three classes were made by research code, the trace of log 379 | building it |
| 7 | a node for learning each context's change | `model_HiOps` | `Research/lower_HiOp/learn_context_changes_from_a_handful.py` (log 470) has no plan node; the simple stage uses it (log 430 §4) | the owner's word |
| 8 | the modelling itself | `model_HiOps` | simple HiOps first, then hybrid, then complex; not started | the owner |
| 9 | GNU C's parts out of the generic nodes | `langs` | GNU C's and clang's parts sit beside the generic code: a `clang.py` in three nodes, `read_clang_types` in `holder_reader.py`, and `holder_reader`'s CORE lists twelve languages' sources. They go to `langs/gnu_c`, and clang's shared readers to a `lowerers` folder (the owner, 2026-10-15) | the owner: when; "we havent even got through C yet" |
| 10 | generic classes with stubs, and a tool that measures what a language adds | every generic node | the owner's idea of 2026-10-15 | the owner |
| 11 | the label on each key by its signature | `dict_of_lang_HiOps` | `signature_label`: the label words are open since 2026-10-05 (log 361) | the owner |
| 12 | `extract_lang_infra` | a new node | the code the Units call (compiler-rt now) has no node; the owner's note of 2026-10-14 (log 456 §6) | the owner: make it |
| 13 | go through the other nodes | `dict_of_lang_HiOps`, `standard_HiOp_wrapper`, `lower_HiOp`, `extract_unit_from_LoHiOp`, `langs`, and the node that keeps the work already done | the review of 2026-10-14 and 2026-10-15 covered `extract_lang_vocab`'s parts | the owner |
| 14 | later: `a * b + c` as one `fmadd.d` | `lower_HiOp` | the owner: "we will get it later when we find a way to optimize arch-opcodes". Shared | later |

Done on 2026-10-15, and so off the list: the held-form renamed the
standard-form; `HiOp_sorter` moved to `model_HiOps`; the 11 out-of-date
statements of log 463 fixed.
