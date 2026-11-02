---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.compile_standard_source.check
---

# CHECK — 0_0_0_0_2_2_1_compile_standard_source

Node `hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.compile_standard_source`. Status `draft`.

## check 1 — completeness

> a node being complete means its sub-nodes are complete. if a node is
> a leaf with no sub-nodes, it is complete.
>
> there is a difference between an intentionally empty list vs a list
> that wont be empty eventually. but we have things like "draft"
> codifications to indicate an incomplete node.
>
> — the owner, 2026-07-31

So the rule has two parts, and the second is what stops it being
vacuous:

    complete(node) = status is `settled` AND every sub-node complete

Without the status clause every leaf is complete by definition and the
recursion bottoms out at "the whole tree is complete", which is true of
any tree and therefore says nothing. `draft` versus `settled` carries
the difference between a node that is a leaf on purpose and one that
simply has not been decomposed yet.

**Is this node settled?** **no** — `status: draft`

**Sub-nodes:**

*none — this is a leaf.*

A leaf is complete when its status is `settled`. There is
nothing beneath it to be incomplete.

### verdict

**NOT COMPLETE** — status is not `settled`.

## check 2 and beyond

None yet. the owner, 2026-07-31: "we can figure out better checks later."
