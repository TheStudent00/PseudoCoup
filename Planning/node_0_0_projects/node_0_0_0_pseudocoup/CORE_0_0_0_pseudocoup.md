---
id: hq.projects.pseudocoup
level: 2
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: pseudocoup
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/CORE_0_0_0_pseudocoup.md
super_node:
    name: projects
    path: ../CORE_0_0_projects.md
sub_nodes:
    - name: pseudoarch
      path: node_0_0_0_0_pseudoarch/CORE_0_0_0_0_pseudoarch.md
    - name: ledgerer
      path: node_0_0_0_1_ledgerer/CORE_0_0_0_1_ledgerer.md
    - name: hub
      path: node_0_0_0_2_hub/CORE_0_0_0_2_hub.md
---

# CORE 0_0_0 — pseudocoup

## metadata

- **id:** hq.projects.pseudocoup
- **level:** 2
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [projects](../CORE_0_0_projects.md)

## sub_nodes

- [pseudoarch](node_0_0_0_0_pseudoarch/CORE_0_0_0_0_pseudoarch.md) — The system the Hub is constructed with.
- [ledgerer](node_0_0_0_1_ledgerer/CORE_0_0_0_1_ledgerer.md) — Two directions over one artifact, the UR-Ledger.
- [hub](node_0_0_0_2_hub/CORE_0_0_0_2_hub.md) — Holds AutoPoly.

## definition

The product. It holds the Ledgerer and the Hub, and PseudoArch is what
the Hub is built out of.

Built at `Projects/PseudoCoup` as a plain directory inside this repo,
copy-pasted over `TheStudent00/PseudoCoup` when it is done.

The ontology this node and everything under it comes from is
`Planning/CORE_0_0_0_pseudocoup.md

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant

## support

- [SUPPORT_gnu_c_work_remaining.md](SUPPORT_gnu_c_work_remaining.md): what
  remains for GNU C, started over on 2026-10-13 with everything done taken out
  : four things and one for later, each with what it waits on
  and my recommendation, and what was done that day. Dee: "i asked you to
  start the list over with the things we solved removed" (log 449); first
  written at "i need to see a new report of the work that remains" (log 445).
- [SUPPORT_gnu_c_work_remaining_in_python.html](SUPPORT_gnu_c_work_remaining_in_python.html):
  the same, as one small program written in Python's syntax with each problem
  marked once; a click on a mark opens its card (the GNU C line, riscv64's
  words, what is missing); its list shows only what remains (log 449). Dee,
  2026-10-13: "i would like to use Python to represent the C code".
- [SUPPORT_gnu_c_sync_fetch_and_add_walk.py](SUPPORT_gnu_c_sync_fetch_and_add_walk.py)
  and [SUPPORT_gnu_c_sync_fetch_and_add_walk.html](SUPPORT_gnu_c_sync_fetch_and_add_walk.html):
  what `__sync_fetch_and_add_4(p, v)` does, in Python: `fetch_and_add(p,
  size, v)` as written in chat, the two functions it calls (`read_number` and
  `write_number`) written out, and below them two threads, A and B, taking two
  files from one list. With a read and then a write, both take a.txt; with
  `fetch_and_add`, A takes a.txt and B takes b.txt. The page steps through
  that run one line at a time, 24 steps . Dee,
  2026-10-14: "use Python to show me what `__sync_fetch_and_add_4(a, b)`
  [does] ... i want to observe literal behavior on actual data." And: "i want
  to see fetch_and_add used and showing how two threads use it to
  coordinate"
- [SUPPORT_gnu_c_clang_code_by_sub_model.html](SUPPORT_gnu_c_clang_code_by_sub_model.html):
  clang's own code for GNU C's HiOps, each line marked by the sub-model whose
  programs make clang run it . Dee, 2026-10-17: "a handful of
  actual lowerer code containing its HiOp vocabulary per problem".
- [SUPPORT_gnu_c_sub_models_reach.html](SUPPORT_gnu_c_sub_models_reach.html):
  a few examples per sub-model, in Python beside clang's C++, and everything
  unmodelled . Dee, 2026-10-17: "a few examples per
  sub-model which expresses the power of that sub-model".
