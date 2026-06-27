"""
classify.py — the four buckets every named grammar kind must fall into, on the
record. The coverage gate asserts: NAMED_KINDS == ROUTED ∪ CONTAINER ∪ WRAP ∪
OUT_OF_SCOPE, with nothing left over. Anything left over is the worklist.

  ROUTED        — has a handler (Visitor._route); see transpiler.py
  CONTAINER     — trivia / consumed by a parent rule; no handler of its own
  WRAP          — no Python equivalent; always routed to a shim (P3)
  OUT_OF_SCOPE  — explicitly refused (parse errors, etc.)
  (leftover)    — UNROUTED: the worklist P1/P2 drive to empty
"""

# Trivia + nodes a parent rule consumes directly (it never gets its own handler).
# Seeded from the donor coverage instrument (tools/transpiler/coverage.py); refined
# as P1 lands real handlers.
CONTAINER = {
    "package_header", "import", "import_list", "import_header",
    "shebang", "file_annotation",
    "value_argument", "value_arguments", "string_content", "escape_sequence",
    "variable_declaration", "multi_variable_declaration",
    "modifiers", "visibility_modifier", "class_modifier", "member_modifier",
    "function_modifier", "property_modifier", "inheritance_modifier",
    "parameter_modifiers", "type_modifiers", "use_site_target",
    "function_value_parameters", "function_body", "class_body", "enum_class_body",
    "class_parameters", "class_parameter", "primary_constructor",
    "constructor_invocation", "constructor_delegation_call",
    "lambda_parameters", "annotated_lambda", "property_delegate",
    "enum_entry", "getter", "setter", "type_test",
    "line_comment", "block_comment",
    # suites/bodies are descended into by their parent renderer, never dispatched
    "block", "function_body", "statements",
}

# No Python equivalent -> always a shim (the wrap layer lands in P3).
WRAP: set = set()

# Explicitly refused.
OUT_OF_SCOPE = {"ERROR"}


def bucket(node_kind: str, routed: set) -> str:
    if node_kind in routed:
        return "ROUTED"
    if node_kind in CONTAINER:
        return "container"
    if node_kind in WRAP:
        return "wrap"
    if node_kind in OUT_OF_SCOPE:
        return "out-of-scope"
    return "UNROUTED"
