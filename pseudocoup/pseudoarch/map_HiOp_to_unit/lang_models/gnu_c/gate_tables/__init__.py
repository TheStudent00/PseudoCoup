"""gate_tables -- Tree-sitter C++ extractor for `derived_info` (`state_info[n]`)
def-use chains and lowerer gate-to-set resolution in Clang (`llvm-project-21.1.8`).

Plan: `.../node_0_0_0_0_2_4_0_2_gate_tables/`.
"""

import re
from typing import Dict, List, NamedTuple, Optional, Tuple

import tree_sitter
import tree_sitter_cpp

from ....model_lang_parts.HiOps.branch_trees import (
    INNER_READS,
    PLACE_TESTS,
    leaf_reading,
    type_test_names,
)
from ....model_lang_parts.HiOps.enumerate_branch_candidates import (
    CANNOT_REACH_NAMES,
    LANGUAGE_NAMES,
    NOT_NEEDED_NAMES,
    OPTION_NAMES,
    PART_NAMES,
    REFUSAL,
    entry_info_unreachable,
)

_CPP_PARSER = None


def cpp_parser() -> tree_sitter.Parser:
    global _CPP_PARSER
    if _CPP_PARSER is None:
        _CPP_PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_cpp.language()))
    return _CPP_PARSER


class DerivedVar(NamedTuple):
    """One local variable assignment (`state_info[n]`) inside a Clang HiOp function."""

    name: str
    decl_type: str
    rhs_text: str
    line: int


def _declarator_identifier(node) -> str:
    """Extract the variable identifier from a C++ declarator AST node."""
    cur = node
    while cur is not None:
        if cur.type in ("identifier", "field_identifier"):
            return cur.text.decode("utf-8", errors="replace")
        next_node = cur.child_by_field_name("declarator")
        if next_node is not None:
            cur = next_node
            continue
        found = None
        for child in cur.named_children:
            if child.type in ("identifier", "pointer_declarator", "reference_declarator", "array_declarator"):
                found = child
                break
        cur = found
    return ""


def extract_derived_info(cpp_source: str) -> Dict[str, DerivedVar]:
    """Parse a C++ function body (or snippet) with Tree-sitter and extract its
    local variable `state_info[n]` def-use table: `var_name -> DerivedVar`."""
    tree = cpp_parser().parse(cpp_source.encode("utf-8"))
    derived: Dict[str, DerivedVar] = {}
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "declaration":
            type_node = node.child_by_field_name("type")
            decl_type = " ".join(type_node.text.decode("utf-8", errors="replace").split()) if type_node else ""
            for child in node.named_children:
                if child.type == "init_declarator":
                    decl_part = child.child_by_field_name("declarator")
                    val_part = child.child_by_field_name("value")
                    var_name = _declarator_identifier(decl_part)
                    if var_name and val_part is not None:
                        rhs = " ".join(val_part.text.decode("utf-8", errors="replace").split())
                        derived[var_name] = DerivedVar(var_name, decl_type, rhs, child.start_point[0] + 1)
        elif node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            if left is not None and right is not None and left.type == "identifier":
                var_name = left.text.decode("utf-8", errors="replace")
                if var_name not in derived:
                    rhs = " ".join(right.text.decode("utf-8", errors="replace").split())
                    derived[var_name] = DerivedVar(var_name, "", rhs, node.start_point[0] + 1)
        for child in reversed(node.children):
            stack.append(child)
    return derived


IDENT_RE = re.compile(r"\b([A-Za-z_]\w*)\b")
ARG_INDEX_RE = re.compile(r"getArg\(\s*(\d+)\s*\)")
METHOD_CALL_RE = re.compile(r"(?:->|\.)\s*(is\w+|has\w+)\s*\(\s*\)")
TEMPLATE_CAST_RE = re.compile(
    r"\b(?:isa|dyn_cast|cast|getAs|castAs)\s*<\s*(?:clang::|llvm::)?(\w+)\s*>"
)


def expand_through_derived_info(expr_text: str, derived: Dict[str, DerivedVar], max_hops: int = 8) -> str:
    """Substitute local `state_info[n]` variables in `expr_text` backward to
    their `state_info[0]` entry definitions."""
    current = expr_text
    seen = set()
    for _ in range(max_hops):
        changed = False
        for ident in IDENT_RE.findall(current):
            if ident in derived and ident not in seen:
                seen.add(ident)
                rhs = derived[ident].rhs_text
                current = re.sub(r"\b" + re.escape(ident) + r"\b", f"({rhs})", current)
                changed = True
        if not changed:
            break
    return current


def resolve_state_info_n(
    expr_text: str,
    derived: Dict[str, DerivedVar],
    part_count: int = 2,
) -> dict:
    """Resolve a C++ gate expression through `derived_info` (`state_info[n]`)
    back to `state_info[0]`: returns the constrained operand part(s), whether
    `.inner` (pointee/element) is projected, any implied outer holder-set, and
    the lowerer set family and predicate."""
    expanded = expand_through_derived_info(expr_text, derived)
    parts: List[int] = []
    for arg_match in ARG_INDEX_RE.finditer(expanded):
        idx = int(arg_match.group(1))
        if idx < part_count and idx not in parts:
            parts.append(idx)
    if not parts:
        if any(w in expanded for w in ("getLHS", "LHS", "Op0", "Cond", "SubExpr", "Base")):
            parts.append(0 if part_count != 3 else (0 if "Cond" in expanded else 1))
        if any(w in expanded for w in ("getRHS", "RHS", "Op1")) and part_count >= 2:
            parts.append(1 if part_count != 3 else 2)
    if not parts:
        parts = list(range(part_count))

    inner = False
    implied_outer = None
    if any(w in expanded for w in ("getPointeeType", "PointerType")):
        if "getPointeeType" in expanded:
            inner = True
            implied_outer = "isPointerType"
    if any(w in expanded for w in ("getElementType", "VectorType", "ExtVectorType")):
        if "getElementType" in expanded:
            inner = True
            implied_outer = "isVectorType"

    set_family = "holder_sets"
    predicate = None
    for place_pred in PLACE_TESTS:
        if place_pred in expanded:
            set_family = "place_sets"
            predicate = place_pred
            break
    if predicate is None:
        if any(w in expanded for w in ("isIntegerConstantExpr", "EvaluateAsInt", "ConstantInt")):
            set_family = "constant_value_sets"
            predicate = "ConstantInt"
        elif any(w in expanded for w in ("isGLValue", "isLValue")):
            set_family = "value_category_sets"
            predicate = "isGLValue"
        else:
            m = METHOD_CALL_RE.search(expanded)
            if m and m.group(1) in type_test_names():
                predicate = m.group(1)
            else:
                tm = TEMPLATE_CAST_RE.search(expanded)
                if tm:
                    node_type = tm.group(1)
                    type_map = {
                        "PointerType": "isPointerType",
                        "VectorType": "isVectorType",
                        "ExtVectorType": "isExtVectorType",
                        "RecordType": "isRecordType",
                        "ComplexType": "isAnyComplexType",
                        "AtomicType": "isAtomicType",
                        "EnumType": "isEnumeralType",
                        "BitIntType": "isBitIntType",
                        "FunctionType": "isFunctionType",
                        "FunctionProtoType": "isFunctionType",
                        "ArrayType": "isArrayType",
                        "ConstantArrayType": "isArrayType",
                        "IntegerType": "isIntegerTy",
                        "ConstantInt": "ConstantInt",
                    }
                    predicate = type_map.get(node_type)
                    if predicate == "ConstantInt":
                        set_family = "constant_value_sets"

    return {
        "original": expr_text,
        "expanded": expanded,
        "parts": tuple(parts),
        "inner": inner,
        "implied_outer_holder_set": implied_outer,
        "set_family": set_family,
        "predicate": predicate,
    }


__all__ = [
    "CANNOT_REACH_NAMES",
    "DerivedVar",
    "INNER_READS",
    "LANGUAGE_NAMES",
    "NOT_NEEDED_NAMES",
    "OPTION_NAMES",
    "PART_NAMES",
    "REFUSAL",
    "entry_info_unreachable",
    "expand_through_derived_info",
    "extract_derived_info",
    "leaf_reading",
    "resolve_state_info_n",
]
