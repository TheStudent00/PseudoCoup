---
id: hq.projects.pseudocoup.ledgerer
level: 3
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: ledgerer
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_1_ledgerer/CORE_0_0_0_1_ledgerer.md
super_node:
    name: pseudocoup
    path: ../CORE_0_0_0_pseudocoup.md
sub_nodes:
    - name: universal_rich_node
      designation: code (class)
      realize: false
---

# CORE 0_0_0_1 — ledgerer

## metadata

- **id:** hq.projects.pseudocoup.ledgerer
- **level:** 3
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [pseudocoup](../CORE_0_0_0_pseudocoup.md)

## sub_nodes

- universal_rich_node — code (class) *(realize: false)*

## definition

Two directions over one artifact, the UR-Ledger. Detail waits; pseudoarch is
being descended first.

- **The UR-Ledger** is the artifact's name (the owner, 2026-10-09: "UR-Ledger might
  be a better way of describing things"; agreed the same day, "great, lets
  update that part of the design too"). It was called UR-AST, "Universal Rich
  AST" (PseudoCoup_v5's `ur` CORE, the owner, 2026-08-02). The AST is only the tree
  its nodes hang in; the ledger is the whole: its UR-Nodes, the connectors
  between them, and the order of every change .
- **The ledger is an RCG.** the owner, 2026-10-09: "the ledgerer has enough
  complexity to model Reflective Call Graphs (RCG: own term my thesis
  proposal to describe a Dynamic Call Graph that modifies itself but in a
  way that is observable -- a DCG might modify itself but without an
  additional axis, its reflections might not be easily observable). so in
  essence, the ledger is an RCG."
- **Its nodes are UR-Nodes** (the owner's `UniversalRichNode`, 
  it sits under both Ledgerer and AutoPoly; defined once, here). What one is
  was locked by the owner on 2026-10-09: "well its a strong argument. we can lock
  that design in. i have no disagreements with it." . Its
  shape is in `## design`.

*notes:*

- Declarations are done by hand now, and may be modelled later. the owner,
  2026-10-13: "i thought we solved declarations like ten times by now ...
  declarations are common across many other languages. we can model that
  by-hand and pick it up later potentially once PseudoCoup is actually up and
  running" , and, correcting my "later, by hand": "by-hand now,
  later potentially by modelling" (log 447). Settled before in logs 382, 383
  and 385. This covers the list's items 5, 20, 36, and 17 (the owner: "okay").
  Done by hand on 2026-10-13: `SUPPORT_gnu_c_declarations_by_hand.md` (log
  449).
- A holder declared without a value holds 0 in the ledger. the owner, 2026-10-13:
  "could we not initialize to zero?" A comparison against riscv64's own run
  accepts any value of the holder's type .
- A name and a relocation need nothing modelled: the ledger knows where each
  named holder lives and fills the blank address the linker would; in the
  Lean term the blank is a named unknown 
  "i dont see where the problem is").
- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant

## support

- [SUPPORT_gnu_c_declarations_by_hand.md](SUPPORT_gnu_c_declarations_by_hand.md):
  what the ledger does with each GNU C declaration, by hand: log 385's 22
  rules, the declarations named since, every attribute sorted by what it
  changes, and riscv64's sizes, alignments and layout rules read back from
  clang (run elv2_l157). the owner, 2026-10-13: "by-hand now, later potentially by
  modelling" .

## design

The UR-Node, as locked by the owner on 2026-10-09 
here the same day by Claude, Opus 5.5, at the owner's word).

```
class universal_rich_node
	"""
		one HiOp variant, carried with what it
		lowers to; universal because any Unit
		runs in any language (hub/autopoly)
	"""
	attributes:
		hiop
		units
		meaning
```

- `hiop`: the operator with its holders, as its language's lowerer reads it
  (`pseudoarch/map_HiOp_to_unit`). It is per language: in the words of
  PseudoCoup_v5's `ur` CORE, "'universal' names the destination, not the
  road", and the HiOp is the road.
- `units`: what the HiOp lowers to, one per architecture. It is the
  destination, the same in every language. One HiOp variant has one Unit per
  architecture, where an operator without its holders has many: C's
  `a ? b : c` and `a ?: b`, 2,788 kept HiOps, 327 different Units on riscv64
  .
- `meaning`: each Unit's Lean term, through Sail
  (`pseudoarch/map_unit_to_lean`). "The same meaning" between two UR-Nodes is a
  proof between two such terms, the `EquivalenceProver` beside the UR-Node
  under AutoPoly in log 302.

the owner's three points of 2026-10-09, and what carries each:

- "(1) a nodes universality -- that a node has the same meaning in all
  languages (via polyfill)": `units` and `meaning`, with AutoPoly running any
  Unit in any language.
- "(2) the ledger's rich-ness to model complexity of programs that an AST
  cannot model": not the node; the ledger's connectors and the order of its
  changes.
- "(3) ... it must be rich enough to be universal": `hiop` carries the
  holders, because the operator together with its holders is what has one
  Unit per architecture.

Not part of the node: dominance between UR-Nodes. It is a relation among
them, left for the Hub's construction (the owner, 2026-10-09: "lets leave it for
later"); the ideas so far are in the hub's `SUPPORT_BRAINSTORM_hub.md`.
