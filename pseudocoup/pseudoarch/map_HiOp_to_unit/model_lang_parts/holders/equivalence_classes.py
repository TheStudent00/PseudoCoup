"""equivalence_classes -- partitioning a language's holder pool into minimal
gate-predicate equivalence classes over the BranchTree leaf vocabulary."""
from ..HiOps.branch_trees import (
    EQUIVALENCE_CLASS_HOLDERS,
    TYPE_ONLY_HOLDERS,
    holders_where,
    holder_answer,
)

__all__ = [
    "EQUIVALENCE_CLASS_HOLDERS",
    "TYPE_ONLY_HOLDERS",
    "holders_where",
    "holder_answer",
]
