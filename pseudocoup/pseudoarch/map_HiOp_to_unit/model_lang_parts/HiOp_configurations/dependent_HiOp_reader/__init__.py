"""dependent_HiOp_reader -- where each dependent-HiOp of GNU C may stand, and
which parts of each GNU C listing are bodies, read from clang 21.1.8's own
source code.

Plan: `.../node_0_0_0_0_2_4_extract_lang_vocab/node_0_0_0_0_2_4_2_dependent_HiOp_reader/`
(a research node until 2026-10-11, .

    dependent_HiOp_reader.py          the reader: out/places.json (steps 1 and 2) and out/bodies.json (step 3)
    check_against_clang.py            step 2, checked against clang's own checker
    check_bodies_against_clang.py     step 3, checked against clang's dump of its control-flow builder

Each runs as a script inside a run on the tower. Its runs and records stay in
Research/extract_lang_vocabulary/dependent_HiOp_reader/ (lanes_elv2/, out/),
as HiOp_sorter's do.
"""
