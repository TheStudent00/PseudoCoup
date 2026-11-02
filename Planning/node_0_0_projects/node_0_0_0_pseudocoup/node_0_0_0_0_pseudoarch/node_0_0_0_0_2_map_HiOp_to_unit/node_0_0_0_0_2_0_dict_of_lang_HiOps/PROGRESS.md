---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.dict_of_lang_HiOps.progress
status: living
---

# PROGRESS — dict_of_lang_HiOps

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-09-23: settled that the dict is DERIVED from each language's own
  declaration, never hand-written. Eleven of twelve declare the operator x
  holder grid; c and cpp are the outlier. Citations in
  `SUPPORT_declared_vocabularies.md`.
- 2026-09-23: measured the gap the current dict carries — c declares 59
  builtin types and the dict uses 6; go declares 15 concrete numeric types
  and the dict uses 5. No nullable holder exists in the dict at all, which
  is why dart's `a ?? b` and `a!` lowered to nothing.
- 2026-09-28: CORRECTS the 2026-09-23 bullet "Eleven of twelve declare the
  operator x holder grid; c and cpp are the outlier". Every one of the twelve
  declares its operators and its holders. Eight also write some pairings down
  as data (java, dart, rust, swift, ruby, csharp, go, and php for long and
  double); four keep them only in code (c, cpp, python, javascript). The dict
  is filled from the lowerer's verdict on the grid, not from those pairings.
- 2026-10-14 : I wrote the module,
  `Projects/PseudoArch/map_HiOp_to_unit/dict_of_lang_HiOps.py`: `Variant` (one
  HiOp; I moved the class here from `extract_lang_vocab`, which still
  imports the name), and `write` and `read`, one JSON line per HiOp.
  `extract()` gives the HiOps that `write` puts in the file. GNU C's file,
  which `extract()` made on 2026-10-14, holds 325,613 HiOps:
  `Research/extract_lang_vocabulary/refactor_check/extract_l164/c.HiOps.jsonl.gz`.
  `lower_gnu_c.py` doesn't read the dict yet: it keeps its list of
  2026-10-06 until Dee rules on the two faults of log 456 §5. Status:
  written; not yet read by the lowering.
