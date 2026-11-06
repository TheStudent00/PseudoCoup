"""slicer -- AST-driven transitive reachability slicer for Kotlin & Java across multi-root source trees."""
from .transitive_slicer import (
    DeclarationNode,
    ReachabilitySliceManifest,
    TransitiveReachabilitySlicer,
)

__all__ = [
    "DeclarationNode",
    "ReachabilitySliceManifest",
    "TransitiveReachabilitySlicer",
]
