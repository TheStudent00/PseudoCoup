"""HiOps -- reading a language's HiOps, building in-HiOp BranchTrees,
enumerating branch candidates and paths, and finding unreached paths."""
import os as _os
from . import operator_reader  # noqa: F401
_RESEARCH_CLONE = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "..", "..", "Research", "trace_logical_paths_clone"))
if _os.path.isdir(_RESEARCH_CLONE):
    from . import branch_trees, enumerate_branch_candidates, enumerate_paths, find_unreached_paths  # noqa: F401
