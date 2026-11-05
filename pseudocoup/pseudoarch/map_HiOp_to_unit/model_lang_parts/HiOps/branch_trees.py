#!/usr/bin/env python3
"""branch_trees.py -- the branch tree of every function in clang's files that
the operators' traced paths run, read with tree-sitter from each file as
clang's preprocessor writes it, and the depth of every path.

the owner, 2026-10-22 (PCHQ Gemini copy, after log 501): "when i say depth, im
referring to the meaning thats used by every reasonably sane person on the
planet in the field of computation. a logical control flow branch. the
number of those along a path define its depth." Then: "just measure it. is
it not obvious from just running tree-sitter on the whole lowerer files
that are relevant and analyze the depth of the tree paths? and we might as
well not throw away that tree."

A branch point is a test the code's control flow splits at. Reading A counts
every one: an `if`'s test, a `switch` (one branch point, one way for each
case label and one more when it has no `default`), a loop's test (`while`,
`for`, `do`, a range `for`), a `?:`, and each operand an `&&` or `||` tests.
Reading B counts the statements' branch points only: `if`, `switch` and the
loops, a whole test being one branch point.

A path through a function takes one way at each branch point it meets. A
loop is entered once or not at all, its test counted once; `return`, `throw`
and `goto` end a path; `break` leaves its loop or `switch`; `continue` ends
the loop's one pass. `if constexpr` is decided when the code is compiled, so
it adds no branch point. A lambda is a function of its own. The depth of a
path is the number of branch points on it.

The tree kept for each function holds its branch points only, in the order
the code meets them: each with its line, its test and the branch points on
each of its ways, the lines each way holds; and the exits (`return`,
`break`, ...). Each operand a test tests keeps its text and its atoms (the
calls with their receivers and arguments, the comparisons, the names).

§4 (PCHQ log 503, at the owner's word: "wouldnt we be able to determine the
abstract objects which unlock each branch?"): the abstract objects that
unlock a branch. A branch's chain, the ways a path takes from its
function's entry to it (calls not followed), narrows what a program may be,
part by part (holders, places, value forms), with the options and the
target; what is left is written as the loop's candidates. §5: the checks of
log 503 §3, and the count of the branches a new candidate unlocks before a
run traces them.

    branch_trees.py files OUT     the files and functions the lines records name
    branch_trees.py trees OUT     each function's tree, and the depths of its paths
    branch_trees.py traced OUT    the depth of every traced path, by operator
    branch_trees.py unlock OUT    log 503's checks: run tlp1_l10's five branches unlocked, functions trimmed
    branch_trees.py dry OUT       every not-reached branch unlocked without tracing; the operators to run
                                  (both read the trees PSEUDOIR_BRANCH_TREES names)

Every count runs on the tower (instance tlp1): clang's files are
preprocessed there first (PSEUDOIR_PREPROCESSED names OUT/preprocessed).
"""

import copy
import itertools
import json
import os
import re
import statistics
import sys
import threading
import time
from typing import NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
if PROJECTS not in sys.path:
    sys.path.insert(0, PROJECTS)

CHECKOUT = "llvm-project-21.1.8"
# The prefixes a lines record's function names its file with.
SOURCE_PREFIXES = ("/persist/traced_clang_src/", "/sources/llvm-project-21.1.8/")
READINGS = ("A", "B")
EXITS = ("return", "throw", "goto", "break", "continue")
LOOPS = ("while", "for", "range for")
# the expression's own branch points, counted in reading A only
EXPRESSION_KINDS = ("?:", "value &&", "value ||")
SAY_EVERY = 60
STATE = {"said": 0.0}


def say(text: str) -> None:
    print(f"{time.strftime('%H:%M:%S', time.gmtime())} {text}", flush=True)


def say_now_and_then(text: str) -> None:
    if time.time() - STATE["said"] >= SAY_EVERY:
        say(text)
        STATE["said"] = time.time()


def read_json(path: str):
    with open(path, encoding="utf-8") as read:
        data = json.load(read)
    return data


def write_json(data, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    beside = path + ".writing"
    with open(beside, "w", encoding="utf-8") as written:
        json.dump(data, written)
        written.write("\n")
    os.replace(beside, path)


# ---------------------------------------------------------------------------
# 1. the files: every function some traced path ran, and its file

def lines_records() -> list:
    """Every lines run's lines.json, oldest first, the pruned binary's left
    out: the loop's own list (enumerate_branch_candidates.lines_records)."""
    import enumerate_branch_candidates as loop
    records = loop.lines_records()
    return records


def relative_of(file: str) -> str:
    """A file's path inside clang's checkout, or '' when it is none of it."""
    for prefix in SOURCE_PREFIXES:
        if file.startswith(prefix):
            relative = file[len(prefix):]
            return relative
    return ""


def files_named(records: list) -> dict:
    """relative file -> function name -> [first, last]: every function a
    lines record names."""
    found = {}
    for number in range(len(records)):
        data = read_json(records[number])
        for name, function in data.get("functions", {}).items():
            add_function(found, name, function)
        say(f"[files] {number + 1} of {len(records)} lines records read; {len(found)} files so far")
    return found


def add_function(found: dict, name: str, function: dict) -> None:
    relative = relative_of(function.get("file") or "")
    if not relative:
        return
    held = found.setdefault(relative, {})
    held[name] = [function.get("first"), function.get("last")]


def files_step(out: str) -> None:
    records = lines_records()
    found = files_named(records)
    write_json(found, os.path.join(out, "files.json"))
    with open(os.path.join(out, "files.txt"), "w", encoding="utf-8") as written:
        for relative in sorted(found):
            written.write(relative + "\n")
    functions = 0
    for held in found.values():
        functions += len(held)
    say(f"[files] {len(found)} files, {functions} functions named by {len(records)} lines records")


# ---------------------------------------------------------------------------
# 2. the trees: each function's branch points, read from its tree-sitter tree

def parser_of():
    import tree_sitter
    import tree_sitter_cpp
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_cpp.language()))
    return parser


def line_of(node) -> int:
    line = node.start_point[0] + 1
    return line


def functions_of(root) -> list:
    """Every function the file defines, and every lambda, each with its name,
    first and last line, and its tree."""
    found = []
    pending = [root]
    while pending:
        node = pending.pop()
        if node.type == "function_definition":
            add_definition(found, node)
        elif node.type == "lambda_expression":
            add_lambda(found, node)
        pending.extend(node.children)
    found.sort(key=function_order)
    return found


def function_order(function: dict) -> tuple:
    order = (function["first"], -function["last"])
    return order


def add_definition(found: list, node) -> None:
    from PseudoIR.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import cpp_code
    declarator = cpp_code.function_declarator(node)
    body = node.child_by_field_name("body")
    if declarator is None or body is None:
        return
    name = cpp_code.collapsed(declarator.child_by_field_name("declarator").text.decode(errors="replace"))
    items = []
    for sub_node in node.named_children:
        if sub_node.type == "field_initializer_list":
            items.extend(expression_items(sub_node))
    items.extend(statement_items(body))
    found.append(new_function(name, node, items, False))


def add_lambda(found: list, node) -> None:
    body = node.child_by_field_name("body")
    if body is None:
        return
    name = f"lambda at line {line_of(node)}"
    found.append(new_function(name, node, statement_items(body), True))


def new_function(name: str, node, items: list, is_lambda: bool) -> dict:
    function = {"name": name, "first": line_of(node), "last": node.end_point[0] + 1, "lambda": is_lambda,
                "parse_errors": errors_in(node), "tree": items}
    return function


def errors_in(node) -> int:
    """How many parts of a function tree-sitter's grammar could not read."""
    count = 0
    pending = [node]
    while pending:
        current = pending.pop()
        if current.type == "ERROR" or current.is_missing:
            count += 1
        if current.has_error:
            pending.extend(current.children)
    return count


# a statement's branch points

def statement_items(node) -> list:
    """The branch points and exits of one statement, in the order the code
    meets them."""
    kind = node.type
    if kind == "compound_statement":
        items = sub_node_items(node)
        return items
    if kind == "if_statement":
        items = if_items(node)
        return items
    if kind == "switch_statement":
        items = switch_items(node)
        return items
    if kind == "while_statement":
        items = while_items(node)
        return items
    if kind == "for_statement":
        items = for_items(node)
        return items
    if kind == "for_range_loop":
        items = range_for_items(node)
        return items
    if kind == "do_statement":
        items = do_items(node)
        return items
    if kind in ("return_statement", "throw_statement", "co_return_statement"):
        items = expression_sub_node_items(node) + [exit_item(EXIT_OF[kind], node)]
        return items
    if kind in ("break_statement", "continue_statement", "goto_statement"):
        items = [exit_item(EXIT_OF[kind], node)]
        return items
    if kind == "try_statement":
        items = statement_items(node.child_by_field_name("body"))
        return items
    if kind in ("labeled_statement", "attributed_statement") or kind.startswith("preproc_"):
        items = sub_node_items(node)
        return items
    # decided when the code is compiled: no branch point
    if kind in ("lambda_expression", "static_assert_declaration"):
        return []
    items = expression_items(node)
    return items


EXIT_OF = {"return_statement": "return", "throw_statement": "throw", "co_return_statement": "return",
           "break_statement": "break", "continue_statement": "continue", "goto_statement": "goto"}


def exit_item(kind: str, node) -> dict:
    item = {"kind": kind, "line": line_of(node)}
    return item


def sub_node_items(node) -> list:
    items = []
    for sub_node in node.named_children:
        if sub_node.type in ("comment", "statement_identifier"):
            continue
        items.extend(statement_items(sub_node))
    return items


def expression_sub_node_items(node) -> list:
    items = []
    for sub_node in node.named_children:
        items.extend(expression_items(sub_node))
    return items


def if_items(node) -> list:
    """An `if`: its condition's own initializer first, then the branch point
    with its two ways. `if constexpr` adds no branch point."""
    condition = node.child_by_field_name("condition")
    before, test, line = condition_parts(condition)
    alternative = node.child_by_field_name("alternative")
    then_items = statement_items(node.child_by_field_name("consequence"))
    else_items = []
    if alternative is not None:
        else_items = sub_node_items(alternative)
    kind = "if"
    for sub_node in node.children:
        if sub_node.type == "constexpr":
            kind = "if constexpr"
    item = {"kind": kind, "line": line, "test": test, "then": then_items, "else": else_items,
            "then_span": span_of(node.child_by_field_name("consequence")), "else_span": span_of(alternative)}
    items = before + [item]
    return items


def condition_parts(condition) -> tuple:
    """(the items its initializer holds, its test, the test's line) of a
    condition_clause; a declaration tested is one test, its value's own
    branch points inside it."""
    before = []
    initializer = condition.child_by_field_name("initializer")
    if initializer is not None:
        before = statement_items(initializer)
    value = condition.child_by_field_name("value")
    if value.type == "declaration":
        test = {"op": "test", "line": line_of(value), "inner": expression_sub_node_items(value),
                "text": text_of(value), "atoms": atoms_of(value)}
        parts = (before, test, line_of(value))
        return parts
    parts = (before, test_of(value), line_of(value))
    return parts


def switch_items(node) -> list:
    """A `switch`: its value's own branch points, then one branch point with
    a way for each case label, and a way out when it has no `default`."""
    condition = node.child_by_field_name("condition")
    before, test, line = condition_parts(condition)
    # the value's own branch points come before the switch's
    inner = [{"kind": "test of a switch", "test": test}]
    if test["op"] == "test":
        inner = test["inner"]
    cases = []
    has_default = False
    body = node.child_by_field_name("body")
    for sub_node in body.named_children:
        if sub_node.type != "case_statement":
            continue
        is_default = sub_node.child_by_field_name("value") is None
        if is_default:
            has_default = True
        cases.append({"line": line_of(sub_node), "default": is_default, "body": case_body_items(sub_node),
                      "span": span_of(sub_node)})
    item = {"kind": "switch", "line": line, "test": test, "cases": cases, "default": has_default}
    items = before + inner + [item]
    return items


def case_body_items(case) -> list:
    """The statements a case label opens, up to the next label."""
    value = case.child_by_field_name("value")
    items = []
    for sub_node in case.named_children:
        if value is not None and sub_node.id == value.id:
            continue
        if sub_node.type in ("comment", "case_statement"):
            continue
        items.extend(statement_items(sub_node))
    return items


def while_items(node) -> list:
    condition = node.child_by_field_name("condition")
    before, test, line = condition_parts(condition)
    item = {"kind": "while", "line": line, "test": test, "body": statement_items(node.child_by_field_name("body")),
            "update": [], "body_span": span_of(node.child_by_field_name("body"))}
    items = before + [item]
    return items


def for_items(node) -> list:
    """A `for`: its initializer, then the loop; with no test it is entered
    with no branch point."""
    before = []
    initializer = node.child_by_field_name("initializer")
    if initializer is not None:
        before = statement_items(initializer)
    condition = node.child_by_field_name("condition")
    test = None
    line = line_of(node)
    if condition is not None:
        test = test_of(condition)
        line = line_of(condition)
    update = []
    for sub_node in node.children_by_field_name("update"):
        update.extend(expression_items(sub_node))
    item = {"kind": "for", "line": line, "test": test, "body": statement_items(node.child_by_field_name("body")),
            "update": update, "body_span": span_of(node.child_by_field_name("body"))}
    items = before + [item]
    return items


def range_for_items(node) -> list:
    """A range `for`: its range's own branch points, then one branch point,
    the range empty or not."""
    before = expression_items(node.child_by_field_name("right"))
    right = node.child_by_field_name("right")
    test = {"op": "test", "line": line_of(node), "inner": [], "text": text_of(right), "atoms": atoms_of(right)}
    item = {"kind": "range for", "line": line_of(node), "test": test,
            "body": statement_items(node.child_by_field_name("body")), "update": [],
            "body_span": span_of(node.child_by_field_name("body"))}
    items = before + [item]
    return items


def do_items(node) -> list:
    condition = node.child_by_field_name("condition")
    item = {"kind": "do", "line": line_of(condition), "body": statement_items(node.child_by_field_name("body")),
            "test": test_of(condition), "body_span": span_of(node.child_by_field_name("body"))}
    items = [item]
    return items


# an expression's branch points

def expression_items(node) -> list:
    """The branch points an expression meets as it is worked out: each `?:`,
    and each `&&` and `||` whose value is kept (reading A)."""
    kind = node.type
    if kind == "lambda_expression":
        return []
    if kind == "conditional_expression":
        item = {"kind": "?:", "line": line_of(node), "test": test_of(node.child_by_field_name("condition")),
                "then": expression_items(node.child_by_field_name("consequence")),
                "else": expression_items(node.child_by_field_name("alternative")),
                "then_span": span_of(node.child_by_field_name("consequence")),
                "else_span": span_of(node.child_by_field_name("alternative"))}
        items = [item]
        return items
    operator = logical_operator(node)
    if operator == "&&":
        item = {"kind": "value &&", "line": line_of(node), "test": test_of(node.child_by_field_name("left")),
                "then": expression_items(node.child_by_field_name("right")), "else": [],
                "then_span": span_of(node.child_by_field_name("right")), "else_span": None}
        items = [item]
        return items
    if operator == "||":
        item = {"kind": "value ||", "line": line_of(node), "test": test_of(node.child_by_field_name("left")),
                "then": [], "else": expression_items(node.child_by_field_name("right")),
                "then_span": None, "else_span": span_of(node.child_by_field_name("right"))}
        items = [item]
        return items
    items = []
    for sub_node in node.named_children:
        items.extend(expression_items(sub_node))
    return items


def logical_operator(node) -> str:
    """'&&' or '||' for a binary expression that is one, else ''."""
    if node.type != "binary_expression":
        return ""
    operator = node.child_by_field_name("operator")
    text = operator.type if operator is not None else ""
    if text in ("&&", "and"):
        return "&&"
    if text in ("||", "or"):
        return "||"
    return ""


def test_of(node) -> dict:
    """What a condition tests: its `&&`, `||`, `!` and `?:` as a tree, each
    operand tested a branch point of its own (reading A)."""
    kind = node.type
    if kind in ("parenthesized_expression", "condition_clause") and node.named_child_count == 1:
        test = test_of(node.named_children[0])
        return test
    if kind == "unary_expression":
        operator = node.child_by_field_name("operator")
        if operator is not None and operator.type in ("!", "not"):
            test = {"op": "!", "of": test_of(node.child_by_field_name("argument"))}
            return test
    operator = logical_operator(node)
    if operator:
        test = {"op": operator, "left": test_of(node.child_by_field_name("left")),
                "right": test_of(node.child_by_field_name("right"))}
        return test
    if kind == "conditional_expression":
        test = {"op": "?:", "test": test_of(node.child_by_field_name("condition")),
                "then": test_of(node.child_by_field_name("consequence")),
                "else": test_of(node.child_by_field_name("alternative"))}
        return test
    test = {"op": "test", "line": line_of(node), "inner": expression_items(node), "text": text_of(node),
            "atoms": atoms_of(node)}
    return test


def span_of(node):
    """[first line, last line] of a node; None for none."""
    if node is None:
        return None
    span = [line_of(node), node.end_point[0] + 1]
    return span


def text_of(node) -> str:
    """A node's text as the preprocessed file writes it, its spaces made one."""
    if node is None:
        return ""
    text = " ".join(node.text.decode(errors="replace").split())
    return text


# a leaf test's atoms (PCHQ log 503 §2, Table 1): what it is made of, its
# outermost form first, then the forms inside it in the order written
COMPARISONS = ("==", "!=", "<", "<=", ">", ">=")
NAMES = ("identifier", "qualified_identifier", "field_identifier", "namespace_identifier", "type_identifier",
         "this")
LITERALS = ("number_literal", "true", "false", "null", "nullptr", "char_literal", "string_literal")
ATOMS_KEPT = 12


def atoms_of(node) -> list:
    atoms = []
    if node is not None:
        add_atoms(atoms, node)
    return atoms


def add_atoms(atoms: list, node) -> None:
    if len(atoms) >= ATOMS_KEPT:
        return
    atom, inner = atom_of(node)
    if atom is not None:
        atoms.append(atom)
    for sub_node in inner:
        add_atoms(atoms, sub_node)


def atom_of(node) -> tuple:
    """(the atom a node is, or None; the nodes inside it to read next)."""
    kind = node.type
    if kind == "call_expression":
        found = call_atom(node)
        return found
    if kind == "binary_expression":
        operator = node.child_by_field_name("operator")
        operator_text = operator.type if operator is not None else ""
        left = node.child_by_field_name("left")
        right = node.child_by_field_name("right")
        if operator_text in COMPARISONS:
            atom = {"atom": "compare", "operator": operator_text, "left": text_of(left), "right": text_of(right)}
            found = (atom, [left, right])
            return found
    if kind == "field_expression":
        receiver = node.child_by_field_name("argument")
        atom = {"atom": "field", "receiver": text_of(receiver), "field": callee_name(node.child_by_field_name("field"))}
        found = (atom, [receiver])
        return found
    if kind in NAMES:
        atom = {"atom": "name", "name": text_of(node)}
        found = (atom, [])
        return found
    if kind in LITERALS:
        atom = {"atom": "literal", "value": text_of(node)}
        found = (atom, [])
        return found
    found = (None, list(node.named_children))
    return found


def call_atom(node) -> tuple:
    """A call: its callee's name (`isPointerTy`), the receiver it is called
    on (`OrigTy`, `DstAddr.getElementType()`; '' for a function), the
    template it names (`castAs<ConstantMatrixType>`) and its arguments."""
    function = node.child_by_field_name("function")
    arguments = node.child_by_field_name("arguments")
    receiver = None
    callee = function
    if function is not None and function.type == "field_expression":
        receiver = function.child_by_field_name("argument")
        callee = function.child_by_field_name("field")
    argument_nodes = []
    if arguments is not None:
        argument_nodes = list(arguments.named_children)
    texts = []
    for argument in argument_nodes:
        texts.append(text_of(argument))
    atom = {"atom": "call", "callee": callee_name(callee), "receiver": text_of(receiver), "arguments": texts,
            "template": template_of(callee)}
    inner = []
    if receiver is not None:
        inner.append(receiver)
    found = (atom, inner + argument_nodes)
    return found


def callee_name(node) -> str:
    """The name a callee is called by, without its class, namespace or
    template: `isa<llvm::PointerType>` -> isa, `llvm::cast` -> cast."""
    if node is None:
        return ""
    if node.type in ("template_function", "template_method"):
        node = node.child_by_field_name("name")
    text = text_of(node)
    name = text.split("::")[-1].strip()
    return name


def template_of(node) -> str:
    if node is None or node.type not in ("template_function", "template_method"):
        return ""
    arguments = node.child_by_field_name("arguments")
    text = text_of(arguments)
    return text


# ---------------------------------------------------------------------------
# the depths: how many paths have each depth (a dist: depth -> paths)

def one() -> dict:
    dist = {0: 1}
    return dist


def shifted(dist: dict, steps: int) -> dict:
    found = {}
    for depth, paths in dist.items():
        found[depth + steps] = paths
    return found


def joined(first: dict, second: dict) -> dict:
    found = dict(first)
    for depth, paths in second.items():
        found[depth] = found.get(depth, 0) + paths
    return found


def convolved(first: dict, second: dict) -> dict:
    """Every path of `first` followed by every path of `second`."""
    found = {}
    for depth, paths in first.items():
        for more, other in second.items():
            found[depth + more] = found.get(depth + more, 0) + paths * other
    return found


def new_flow(live: dict) -> dict:
    """The paths going on (`live`), ended, left by a `break`, and ended by a
    `continue`."""
    flow = {"live": live, "ended": {}, "broke": {}, "continued": {}}
    return flow


def merged(first: dict, second: dict) -> dict:
    flow = {}
    for channel in ("live", "ended", "broke", "continued"):
        flow[channel] = joined(first[channel], second[channel])
    return flow


def flow_through(items: list, live: dict, reading: str) -> dict:
    flow = new_flow(live)
    for item in items:
        if not flow["live"]:
            break
        flow = step(item, flow, reading)
    return flow


def step(item: dict, flow: dict, reading: str) -> dict:
    """The paths going on, after one item."""
    kind = item["kind"]
    if kind in EXITS:
        stepped = exit_step(kind, flow)
        return stepped
    if kind in EXPRESSION_KINDS and reading == "B":
        return flow
    if kind in ("if",) + EXPRESSION_KINDS:
        stepped = two_ways_step(item, flow, reading)
        return stepped
    if kind == "if constexpr":
        stepped = constexpr_step(item, flow, reading)
        return stepped
    if kind == "switch":
        stepped = switch_step(item, flow, reading)
        return stepped
    if kind in LOOPS:
        stepped = loop_step(item, flow, reading)
        return stepped
    if kind == "do":
        stepped = do_step(item, flow, reading)
        return stepped
    if kind == "test of a switch":
        stepped = switch_test_step(item, flow, reading)
        return stepped
    return flow


def exit_step(kind: str, flow: dict) -> dict:
    channel = "ended"
    if kind == "break":
        channel = "broke"
    if kind == "continue":
        channel = "continued"
    stepped = dict(flow)
    stepped[channel] = joined(flow[channel], flow["live"])
    stepped["live"] = {}
    return stepped


def kept(flow: dict, inner: dict, live: dict) -> dict:
    """`flow` with `inner`'s ended, broke and continued paths added, and
    `live` going on."""
    stepped = {"live": live}
    for channel in ("ended", "broke", "continued"):
        stepped[channel] = joined(flow[channel], inner[channel])
    return stepped


def two_ways_step(item: dict, flow: dict, reading: str) -> dict:
    to_true, to_false = decided(item["test"], reading)
    then_flow = flow_through(item["then"], convolved(flow["live"], to_true), reading)
    else_flow = flow_through(item["else"], convolved(flow["live"], to_false), reading)
    both = merged(then_flow, else_flow)
    stepped = kept(flow, both, both["live"])
    return stepped


def constexpr_step(item: dict, flow: dict, reading: str) -> dict:
    then_flow = flow_through(item["then"], flow["live"], reading)
    else_flow = flow_through(item["else"], flow["live"], reading)
    both = merged(then_flow, else_flow)
    stepped = kept(flow, both, both["live"])
    return stepped


def switch_test_step(item: dict, flow: dict, reading: str) -> dict:
    """A switch's value with `&&`, `||` or `?:` in it: its own branch
    points (reading A), before the switch's."""
    if reading == "B":
        return flow
    to_true, to_false = decided(item["test"], reading)
    live = convolved(flow["live"], joined(to_true, to_false))
    stepped = dict(flow)
    stepped["live"] = live
    return stepped


def switch_step(item: dict, flow: dict, reading: str) -> dict:
    """One branch point; each case label a way in, each case falling into
    the next until a `break` or an exit; no `default`, one more way out."""
    entry = shifted(flow["live"], 1)
    running = {}
    inner = new_flow({})
    for case in item["cases"]:
        running = joined(running, entry)
        case_flow = flow_through(case["body"], running, reading)
        running = case_flow["live"]
        inner = {"live": {}, "ended": joined(inner["ended"], case_flow["ended"]),
                 "broke": joined(inner["broke"], case_flow["broke"]),
                 "continued": joined(inner["continued"], case_flow["continued"])}
    live = joined(running, inner["broke"])
    if not item["default"]:
        live = joined(live, entry)
    passed = {"live": {}, "ended": inner["ended"], "broke": {}, "continued": inner["continued"]}
    stepped = kept(flow, passed, live)
    return stepped


def loop_step(item: dict, flow: dict, reading: str) -> dict:
    """Entered once or not at all; a `break` leaves it, a `continue` ends its
    one pass; with no test (`for (;;)`) it is always entered."""
    to_true, to_false = one(), {}
    if item["test"] is not None:
        to_true, to_false = decided(item["test"], reading)
    body = flow_through(item["body"], convolved(flow["live"], to_true), reading)
    after = joined(body["live"], body["continued"])
    after = flow_through(item["update"], after, reading)["live"]
    live = joined(joined(convolved(flow["live"], to_false), after), body["broke"])
    passed = {"live": {}, "ended": body["ended"], "broke": {}, "continued": {}}
    stepped = kept(flow, passed, live)
    return stepped


def do_step(item: dict, flow: dict, reading: str) -> dict:
    """Its body once, then its test; either way the path goes on."""
    body = flow_through(item["body"], flow["live"], reading)
    after = joined(body["live"], body["continued"])
    to_true, to_false = decided(item["test"], reading)
    live = joined(joined(convolved(after, to_true), convolved(after, to_false)), body["broke"])
    passed = {"live": {}, "ended": body["ended"], "broke": {}, "continued": {}}
    stepped = kept(flow, passed, live)
    return stepped


def decided(test: dict, reading: str) -> tuple:
    """(paths that find it true, paths that find it false), each with the
    branch points the test passes. Reading B: a whole test is one."""
    if reading == "B":
        ways = ({1: 1}, {1: 1})
        return ways
    op = test["op"]
    if op == "!":
        to_true, to_false = decided(test["of"], reading)
        ways = (to_false, to_true)
        return ways
    if op == "&&":
        left_true, left_false = decided(test["left"], reading)
        right_true, right_false = decided(test["right"], reading)
        ways = (convolved(left_true, right_true), joined(left_false, convolved(left_true, right_false)))
        return ways
    if op == "||":
        left_true, left_false = decided(test["left"], reading)
        right_true, right_false = decided(test["right"], reading)
        ways = (joined(left_true, convolved(left_false, right_true)), convolved(left_false, right_false))
        return ways
    if op == "?:":
        ways = conditional_decided(test, reading)
        return ways
    inner = flow_through(test["inner"], one(), reading)["live"]
    tested = shifted(inner, 1)
    ways = (tested, tested)
    return ways


def conditional_decided(test: dict, reading: str) -> tuple:
    chosen_true, chosen_false = decided(test["test"], reading)
    then_true, then_false = decided(test["then"], reading)
    else_true, else_false = decided(test["else"], reading)
    to_true = joined(convolved(chosen_true, then_true), convolved(chosen_false, else_true))
    to_false = joined(convolved(chosen_true, then_false), convolved(chosen_false, else_false))
    ways = (to_true, to_false)
    return ways


def depths_of(items: list, reading: str) -> dict:
    """depth -> paths, for every path through a function: each one ends at
    an exit or at the function's end (a `break` or `continue` outside a loop
    ends it too)."""
    flow = flow_through(items, one(), reading)
    ended = joined(flow["live"], flow["ended"])
    ended = joined(joined(ended, flow["broke"]), flow["continued"])
    return ended


def summary_of(dist: dict) -> dict:
    """The deepest path, how many paths, and depth -> paths (as text: the
    counts are exact and can be very large)."""
    paths = 0
    for count in dist.values():
        paths += count
    by_depth = {}
    for depth in sorted(dist):
        by_depth[str(depth)] = str(dist[depth])
    deepest = max(dist) if dist else 0
    summary = {"deepest": deepest, "paths": str(paths), "by_depth": by_depth}
    return summary


# ---------------------------------------------------------------------------
# branch points by line, for the traced paths

def branch_lines(items: list, reading: str) -> list:
    """[line, ...]: the line each branch point's test sits on, one per
    branch point (two on one line, that line twice)."""
    found = []
    for item in items:
        add_branch_lines(found, item, reading)
    return found


def add_branch_lines(found: list, item: dict, reading: str) -> None:
    kind = item["kind"]
    if kind in EXITS:
        return
    if kind in EXPRESSION_KINDS and reading == "B":
        return
    if kind in ("if", "do") + EXPRESSION_KINDS + LOOPS:
        add_test_lines(found, item, reading)
    if kind == "switch":
        found.append(item["line"])
    if kind == "test of a switch" and reading == "A":
        add_tested_lines(found, item["test"])
    for way in ("then", "else", "body", "update"):
        for inner in item.get(way, []):
            add_branch_lines(found, inner, reading)
    for case in item.get("cases", []):
        for inner in case["body"]:
            add_branch_lines(found, inner, reading)


def add_test_lines(found: list, item: dict, reading: str) -> None:
    if item.get("test") is None and item["kind"] != "range for":
        return
    if reading == "B":
        found.append(item["line"])
        return
    add_tested_lines(found, item["test"])


def add_tested_lines(found: list, test: dict) -> None:
    """Reading A: the line of each operand a test tests, and the branch
    points inside it."""
    op = test["op"]
    if op == "!":
        add_tested_lines(found, test["of"])
        return
    if op in ("&&", "||"):
        add_tested_lines(found, test["left"])
        add_tested_lines(found, test["right"])
        return
    if op == "?:":
        add_tested_lines(found, test["test"])
        add_tested_lines(found, test["then"])
        add_tested_lines(found, test["else"])
        return
    found.append(test["line"])
    for inner in test["inner"]:
        add_branch_lines(found, inner, "A")


# ---------------------------------------------------------------------------
# the trees step

def trees_step(out: str) -> None:
    from PseudoIR.map_HiOp_to_unit.model_lang_parts import preprocessed_file_path
    named = read_json(os.path.join(out, "files.json"))
    parser = parser_of()
    refused = {}
    by_file = {}
    relatives = sorted(named)
    for number in range(len(relatives)):
        relative = relatives[number]
        try:
            path = preprocessed_file_path(CHECKOUT, relative)
        except FileNotFoundError as refusal:
            refused[relative] = str(refusal)
            continue
        by_file[relative] = tree_of_file(parser, path)
        say(f"[trees] {number + 1} of {len(relatives)}: {relative}: {len(by_file[relative])} functions")
    by_name = names_index(by_file)
    for relative in named:
        mark_on_paths(named[relative], relative, by_name, by_file)
    static = new_static()
    for relative, functions in by_file.items():
        write_json({"file": relative, "functions": functions}, os.path.join(out, "trees", relative + ".json"))
        add_to_static(static, relative, functions)
    static["refused"] = refused
    written_whole(static)
    write_json(static, os.path.join(out, "static.json"))
    say_static(static)


def names_index(by_file: dict) -> dict:
    """name -> [function, ...]: every function the trees hold, by its name
    as written (CodeGenFunction::EmitTypeCheck outside its class,
    EmitTypeCheck inside it)."""
    found = {}
    for relative, functions in by_file.items():
        for function in functions:
            found.setdefault(function["name"], []).append(function)
    return found


def short_name(name: str) -> str:
    """A name without its class or namespace: CodeGenFunction::EmitTypeCheck
    -> EmitTypeCheck."""
    short = name.split("::")[-1]
    return short


def candidates_for(name: str, relative: str, first, by_name: dict, by_file: dict) -> list:
    """The tree's functions a lines record's function is. A record keys its
    functions by name and gives one file, so every definition of the name
    is one: each with its qualified name, and each written inside its class
    in the record's file; only when none is found, the function of the
    record's file whose lines hold the record's first line."""
    found = []
    seen = set()
    for function in by_name.get(name, []):
        add_once(found, seen, function)
    short = short_name(name)
    if short != name:
        for function in by_file.get(relative, []):
            if function["name"] == short:
                add_once(found, seen, function)
    if not found:
        function = holding(by_file.get(relative, []), first)
        if function is not None:
            add_once(found, seen, function)
    return found


def add_once(found: list, seen: set, function) -> None:
    if id(function) in seen:
        return
    seen.add(id(function))
    found.append(function)


def tree_of_file(parser, path: str) -> list:
    with open(path, "rb") as source:
        tree = parser.parse(source.read())
    functions = functions_of(tree.root_node)
    for function in functions:
        for reading in READINGS:
            function[reading] = summary_of(depths_of(function["tree"], reading))
    return functions


def mark_on_paths(named: dict, relative: str, by_name: dict, by_file: dict) -> None:
    """Marks each function a lines record names (candidates_for)."""
    for name, span in named.items():
        for function in candidates_for(name, relative, span[0], by_name, by_file):
            on_paths = function.setdefault("on_paths", [])
            if name not in on_paths:
                on_paths.append(name)


def holding(functions: list, line) -> dict:
    """The smallest function whose lines hold `line`, or None."""
    found = None
    if line is None:
        return found
    for function in functions:
        if function["first"] <= line <= function["last"]:
            if found is None or function["last"] - function["first"] < found["last"] - found["first"]:
                found = function
    return found


def new_static() -> dict:
    static = {"files": 0, "functions": 0, "lambdas": 0, "parse_errors": 0, "functions_on_paths": 0}
    for reading in READINGS:
        static[reading] = {"deepest": {}, "deepest_on_paths": {}, "paths_by_depth": {}}
    return static


def add_to_static(static: dict, relative: str, functions: list) -> None:
    static["files"] += 1
    for function in functions:
        static["functions"] += 1
        if function["lambda"]:
            static["lambdas"] += 1
        static["parse_errors"] += function["parse_errors"]
        if function.get("on_paths"):
            static["functions_on_paths"] += 1
        for reading in READINGS:
            add_reading(static[reading], function, function[reading])


def add_reading(held: dict, function: dict, summary: dict) -> None:
    deepest = str(summary["deepest"])
    held["deepest"][deepest] = held["deepest"].get(deepest, 0) + 1
    if function.get("on_paths"):
        held["deepest_on_paths"][deepest] = held["deepest_on_paths"].get(deepest, 0) + 1
    for depth, paths in summary["by_depth"].items():
        held["paths_by_depth"][depth] = held["paths_by_depth"].get(depth, 0) + int(paths)


def written_whole(static: dict) -> None:
    """The path counts as text, written whole: they can run to thousands of
    digits."""
    for reading in READINGS:
        counts = static[reading]["paths_by_depth"]
        for depth in counts:
            counts[depth] = str(counts[depth])


def say_static(static: dict) -> None:
    say(f"[trees] {static['files']} files, {static['functions']} functions ({static['lambdas']} lambdas), "
        f"{static['functions_on_paths']} named by the lines records; parts the grammar could not read: "
        f"{static['parse_errors']}; refused (not preprocessed): {len(static['refused'])}")
    for reading in READINGS:
        say(f"[trees] reading {reading}, functions by their deepest path: {sorted_counts(static[reading]['deepest'])}")
        say(f"[trees] reading {reading}, the functions named by the lines records: "
            f"{sorted_counts(static[reading]['deepest_on_paths'])}")


def sorted_counts(counts: dict) -> list:
    rows = []
    for key in sorted(counts, key=int):
        rows.append([int(key), counts[key]])
    return rows


# ---------------------------------------------------------------------------
# 3. the traced paths: how many branch points each one passed

PAGE_NODE = os.path.normpath(os.path.join(HERE, "..", "..", "Planning", "node_0_1_research",
                                          "node_0_1_5_trace_logical_paths_clone"))


def gnu_c_reading():
    """(the page module, the vocabulary's keys, the 1,806 GNU C operators):
    a record's key is read as the page reads it (vocabulary_key)."""
    if PAGE_NODE not in sys.path:
        sys.path.insert(0, PAGE_NODE)
    import SUPPORT_vocabulary_runs_clangs_code as page
    keyed = page.results_page().keys_of_vocabulary(page.results_page().vocabulary_entries())
    gnu_c = page.gnu_c_keys(keyed)
    reading = (page, keyed, gnu_c)
    return reading


def traced_step(out: str) -> None:
    index = branch_index(out)
    page, keyed, gnu_c = gnu_c_reading()
    records = lines_records()
    by_operator = {}
    outside = {}
    unmatched = {}
    for number in range(len(records)):
        data = read_json(records[number])
        run = os.path.basename(os.path.dirname(records[number]))
        add_record(by_operator, outside, unmatched, index, data, (page, keyed, gnu_c, run))
        say(f"[traced] {number + 1} of {len(records)} lines records read; {len(by_operator)} GNU C operators so far")
        del data
    rows = operator_rows(by_operator)
    traced = {"operators": rows, "gnu_c_operators": len(gnu_c), "outside_gnu_c": outside,
              "unmatched_functions": unmatched}
    for reading in READINGS:
        traced[reading] = histograms(rows, by_operator, reading)
    write_json(traced, os.path.join(out, "traced.json"))
    say_traced(traced, len(by_operator))


def branch_index(out: str) -> dict:
    """{"by_file": relative -> [span, ...], "by_name": name -> [span, ...]},
    a span being [first, last, A lines, B lines, name] for one function of
    the trees step's files, each lines a count by line."""
    by_file = {}
    by_name = {}
    trees = os.path.join(out, "trees")
    for folder, _, names in os.walk(trees):
        for name in names:
            if not name.endswith(".json"):
                continue
            data = read_json(os.path.join(folder, name))
            spans = []
            for function in data["functions"]:
                span = [function["first"], function["last"], counted(branch_lines(function["tree"], "A")),
                        counted(branch_lines(function["tree"], "B")), function["name"]]
                spans.append(span)
                by_name.setdefault(function["name"], []).append(span)
            by_file[data["file"]] = spans
    index = {"by_file": by_file, "by_name": by_name}
    return index


def counted(lines: list) -> dict:
    counts = {}
    for line in lines:
        counts[line] = counts.get(line, 0) + 1
    return counts


def add_record(by_operator: dict, outside: dict, unmatched: dict, index: dict, data: dict, reading: tuple) -> None:
    """Each path of one lines record, under its GNU C operator; a key that
    is none of the 1,806 is counted apart."""
    page, keyed, gnu_c, run = reading
    functions = data.get("functions", {})
    spans = {}
    for key, entry in data.get("operators", {}).items():
        vocabulary = page.vocabulary_key(key, None, run, keyed)
        if vocabulary not in gnu_c:
            outside[key] = outside.get(key, 0) + len(entry.get("paths", []))
            continue
        contexts = by_operator.setdefault(vocabulary, {})
        for path in entry.get("paths", []):
            depths = path_depths(path, functions, index, spans, unmatched)
            contexts[context_key(path)] = depths


def context_key(path: dict) -> str:
    """One context: its holders, its setup and its program; a context traced
    again in a later record keeps the later record's depths."""
    import hashlib
    text = json.dumps([path.get("holders"), path.get("setup"), path.get("program")])
    key = hashlib.sha1(text.encode()).hexdigest()
    return key


def path_depths(path: dict, functions: dict, index: dict, spans: dict, unmatched: dict) -> dict:
    """How many branch points one traced path passed, in each reading: the
    branch points whose test's line it ran, in every function it ran."""
    depths = {"A": 0, "B": 0, "functions": 0}
    for name, lines in path.get("lines", {}).items():
        found = spans_of(name, functions, index, spans)
        if not found:
            unmatched[name] = unmatched.get(name, 0) + 1
            continue
        depths["functions"] += 1
        for span in found:
            depths["A"] += passed(span, span[2], lines)
            depths["B"] += passed(span, span[3], lines)
    return depths


def spans_of(name: str, functions: dict, index: dict, spans: dict) -> list:
    """The tree's functions a record's function is (candidates_for, read on
    the spans), found once per record."""
    if name in spans:
        found = spans[name]
        return found
    function = functions.get(name) or {}
    relative = relative_of(function.get("file") or "")
    found = []
    for span in index["by_name"].get(name, []):
        found.append(span)
    short = short_name(name)
    if short != name:
        for span in index["by_file"].get(relative, []):
            if span[4] == short and span not in found:
                found.append(span)
    if not found:
        span = span_holding(index["by_file"].get(relative, []), function.get("first"))
        if span is not None:
            found.append(span)
    spans[name] = found
    return found


def span_holding(spans: list, line):
    found = None
    if line is None:
        return found
    for span in spans:
        if span[0] <= line <= span[1]:
            if found is None or span[1] - span[0] < found[1] - found[0]:
                found = span
    return found


def passed(span: list, branch_lines_of: dict, lines: list) -> int:
    """The branch points whose test's line is among the lines a path ran,
    each line once, inside the function's own lines (a record's lines of
    two definitions of one name are not told apart by file)."""
    count = 0
    for line in set(lines):
        if span[0] <= line <= span[1]:
            count += branch_lines_of.get(line, 0)
    return count


def operator_rows(by_operator: dict) -> list:
    rows = []
    for key in sorted(by_operator):
        contexts = list(by_operator[key].values())
        row = {"operator": key, "paths": len(contexts)}
        for reading in READINGS:
            depths = []
            for depths_of_path in contexts:
                depths.append(depths_of_path[reading])
            row[reading] = {"deepest": max(depths) if depths else 0,
                            "median": statistics.median(depths) if depths else 0,
                            "shallowest": min(depths) if depths else 0}
        rows.append(row)
    return rows


BIN = 10


def histograms(rows: list, by_operator: dict, reading: str) -> dict:
    """Operators by their deepest traced path, and paths by depth, in bins
    of BIN branch points."""
    operators = {}
    for row in rows:
        add_to_bin(operators, row[reading]["deepest"])
    paths = {}
    for contexts in by_operator.values():
        for depths in contexts.values():
            add_to_bin(paths, depths[reading])
    found = {"operators_by_deepest_path": sorted_counts(operators), "paths_by_depth": sorted_counts(paths),
             "bin": BIN}
    return found


def add_to_bin(counts: dict, depth: int) -> None:
    low = str((depth // BIN) * BIN)
    counts[low] = counts.get(low, 0) + 1


def say_traced(traced: dict, operators: int) -> None:
    say(f"[traced] {operators} of the {traced['gnu_c_operators']} GNU C operators hold traced paths; record keys "
        f"outside GNU C: {len(traced['outside_gnu_c'])}; functions of the records with no tree: "
        f"{traced['unmatched_functions']}")
    for reading in READINGS:
        say(f"[traced] reading {reading}, operators by their deepest path (bins of {BIN}): "
            f"{traced[reading]['operators_by_deepest_path']}")
        say(f"[traced] reading {reading}, paths by depth (bins of {BIN}): {traced[reading]['paths_by_depth']}")


# ---------------------------------------------------------------------------
# 4. the abstract objects that unlock a branch, and the candidates they write
#
# PCHQ log 503 (Gemini copy), at the owner's word: "beautifully designed. lets put
# it in a research node and fill out the PlanPlan for it, down to the leaf
# nodes. and then we will generate the instruction for Claude to implement
# and run." Plan node research/trace_logical_paths/branch_trees. the owner,
# 2026-10-22: "wouldnt we be able to determine the abstract objects which
# unlock each branch? ... we could use intelligent trimming of possibilities
# to make the method reach wider and deeper."
#
#     chain = BranchTree.super_chain_of_branch(tree, test, first)   # the ways from the function's entry
#     states = [the base context's constraint]
#     for step_test, step_way in chain:                             # each way narrows what can still take them all
#         states = [intersect(state, unlocking) for state in states
#                   for unlocking in unlocking_set_for_test(step_test, step_way)]
#     candidates = [write_from_constraint(writer, base, state) for state in states]
#
# A part's holders are the holders of its value as clang's checks read its
# type: an element place is read as its element (`p->a[0][1]` of an m2 is an
# int), P_k keeping the vector or matrix it is an element of
# (ELEMENT_HOLDERS).

TARGETS = ("riscv64", "x86-64", "aarch64")
PLACES = ("field", "bit-field", "signed bit-field", "vector element", "ext vector element", "matrix element",
          "global register")
VALUE_FORMS = ("place", "constant 0", "constant 1", "constant 2", "constant 3", "constant 4", "constant 5",
               "literal", "parenthesis")
CONSTANT_FORMS = ("constant 0", "constant 1", "constant 2", "constant 3", "constant 4", "constant 5", "literal")
CONSTANT_TEXT = {"constant 0": "0", "constant 1": "1", "constant 2": "2", "constant 3": "3", "constant 4": "4",
                 "constant 5": "5", "literal": "1"}
# clang's kinds of LValue (CGValue.h), the tests that read them, and the places of each
PLACE_TESTS = {"isSimple": ("field",), "isBitField": ("bit-field", "signed bit-field"),
               "isVectorElt": ("vector element",), "isExtVectorElt": ("ext vector element",),
               "isGlobalReg": ("global register",), "isMatrixElt": ("matrix element",)}
# an element place: the holder P_k keeps, by the element's holder, and how op_k reads the element
ELEMENT_HOLDERS = {"vector element": {"int": "v4si", "unsigned int": "v4ui", "float": "v4sf", "double": "v4df",
                                      "arr4": "arrptr"},
                   "ext vector element": {"int": "ev4si", "float": "ev4sf", "_Bool": "ev4b", "ev4si": "ev4si"},
                   "matrix element": {"int": "m2"}}
ELEMENT_READS = {"vector element": "p->{name}[1]", "ext vector element": "p->{name}.x",
                 "matrix element": "p->{name}[0][1]"}
ELEMENT_OF = {"v4si": "int", "v4ui": "unsigned int", "v4sf": "float", "v4df": "double",
              "ev4si": "int", "ev4sf": "float", "ev4b": "_Bool", "m2": "int", "arrptr": "arr4"}
# the kinds of holder a bit-field can be: C23 6.7.2.1 names the bit-precise
# integers beside int and bool (the l10 records hold `unsigned _BitInt(37) b
# : 13` accepted, run tlp1_l10, part 1, path 125)
BIT_FIELD_KINDS = ("integer", "bool", "enum", "bitint")
# a test's receiver read for its inner type: a vector's element, a pointer's pointee (log 503 §2)
INNER_READS = ("getElementType()", "getPointeeType()", "SrcEltType", "SrcEltTy", "DstEltType", "DstEltTy",
               "ElementTy", "eltType", "elementType", "PointeeType", "AtomTy", "ValType", "InputSigned",
               "OutputSigned")
# the holders the writer takes first, simplest first; the others after them, by name
SIMPLE_HOLDERS = ("int", "unsigned int", "_Bool", "long", "unsigned long", "char", "short", "long long",
                  "float", "double", "int *", "void *")
from ..holders.equivalence_classes import (
    EQUIVALENCE_CLASS_HOLDERS,
    TYPE_ONLY_HOLDERS,
)
# the kinds of test that read a part
PART_KINDS = ("holder", "place", "signed", "constant", "lvalue")
# how many alternatives a test keeps, states a chain keeps, and bindings of
# its receivers to parts a chain is tried with (the first ones)
ALTERNATIVES_KEPT = 64
STATES_KEPT = 64
BINDINGS_KEPT = 27
# trim_paths: past this many constraints at one point of a function, they are
# made one (the open one), and the function is marked
TRIM_STATES_KEPT = 256
# the saved trees and the holder facts the loop reads
TREES = os.environ.get("PSEUDOIR_BRANCH_TREES", os.path.join(HERE, "tlp1_l13_the_branch_trees", "trees"))
FACTS_FILE = os.environ.get("PSEUDOIR_HOLDER_FACTS", os.path.join(HERE, "holder_facts_tlp1_l13.json"))
CACHE = {"trees": {}, "holders": {}, "fits": {}, "type_tests": None, "leaves": {}, "capped": 0}


def loop_module():
    import enumerate_branch_candidates as loop
    return loop


def key_name() -> str:
    """The key the standard form's own names take (context.KEY: op_k, P_k)."""
    from PseudoIR.map_HiOp_to_unit.model_lang_parts.context.entry_context import KEY
    return KEY


def signatures_module():
    from PseudoIR.map_HiOp_to_unit.model_lang_parts.holders import accepted_signatures as signatures
    return signatures


class BranchTree(NamedTuple):
    """One function's branch tree (§2): its name as clang's source writes it
    (`CodeGenFunction::EmitStoreThroughLValue`), its first and last line in
    the preprocessed file, and its branch points and exits in the order the
    code meets them, each test with its atoms (`items`)."""

    function_name: str
    first_line: int
    last_line: int
    items: list

    @staticmethod
    def from_preprocessed_file(path: str) -> list:
        """Every function and lambda one preprocessed file defines."""
        with open(path, "rb") as source:
            tree = parser_of().parse(source.read())
        trees = []
        for function in functions_of(tree.root_node):
            trees.append(tree_of(function))
        return trees

    @staticmethod
    def super_chain_of_branch(tree, test_line: int, branch_line: int):
        """[(step_test, step_way), ...]: the ways a path takes from the
        function's entry to the branch whose test is on `test_line` and whose
        way enters `branch_line`, that branch's own way last; None when no
        branch point of the tree tests on that line. A way is True or False;
        a `switch`'s is the line of the case label it enters ({"case": line},
        {"case": None} for no label)."""
        chain = chain_in(tree.items, test_line, branch_line)
        if chain is not None:
            return chain
        for delta in (1, 2, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, -11, -12, -13, -14, -15, -16):
            chain = chain_in(tree.items, test_line + delta, branch_line)
            if chain is not None:
                return chain
        return None

    @staticmethod
    def trim_paths(tree, initial_constraint, held_facts) -> list:
        """[(depth, constraints, paths), ...]: the paths through the function
        (calls not followed, reading A's depths) that some program can take,
        by depth and by what they need. Each path carries the alternatives
        under which a program takes it (each a constraint, and the parts its
        receivers are bound to); each branch point's way narrows every
        alternative (unlocking_set_for_test), and a way none survives is cut
        with everything after it. A path is counted once, however many
        alternatives take it."""
        CACHE["leaves"] = {}
        CACHE["open_facts"] = held_facts
        start = {frozenset([(initial_constraint, frozenset())]): one()}
        flow = trimmed_through(tree.items, start, held_facts)
        ended = state_joined(state_joined(flow["live"], flow["ended"]), state_joined(flow["broke"], flow["continued"]))
        surviving = []
        for alternatives, dist in ended.items():
            constraints = []
            for constraint, binding in alternatives:
                constraints.append(constraint)
            for depth, paths in dist.items():
                surviving.append((depth, constraints, paths))
        surviving.sort(key=lambda row: row[0])
        return surviving


def tree_of(function: dict) -> BranchTree:
    tree = BranchTree(function["name"], function["first"], function["last"], function["tree"])
    return tree


def trees_in(trees: str, relative: str) -> list:
    """The BranchTrees of one file, read from the trees step's record once."""
    path = os.path.join(trees, relative + ".json")
    if path in CACHE["trees"]:
        found = CACHE["trees"][path]
        return found
    found = []
    if os.path.exists(path):
        for function in read_json(path)["functions"]:
            found.append(tree_of(function))
    CACHE["trees"][path] = found
    return found


def tree_of_branch(branch: dict, trees: str = TREES):
    """The tree of the function a branch of the loop is in: of the functions
    of its file whose lines hold its test, the one of its name (as written
    outside its class or inside it), else the smallest; None when none."""
    relative = relative_of(branch["file"])
    named = None
    smallest = None
    for tree in trees_in(trees, relative):
        if not tree.first_line <= branch["test"] <= tree.last_line:
            continue
        if smallest is None or tree.last_line - tree.first_line < smallest.last_line - smallest.first_line:
            smallest = tree
        if tree.function_name in (branch["function"], short_name(branch["function"])):
            if named is None or tree.last_line - tree.first_line < named.last_line - named.first_line:
                named = tree
    if named is not None and smallest is not None and smallest is not named:
        if BranchTree.super_chain_of_branch(named, branch["test"], branch["first"]) is None:
            if BranchTree.super_chain_of_branch(smallest, branch["test"], branch["first"]) is not None:
                return smallest
    if named is not None:
        return named
    return smallest


# the chain into a branch

def chain_in(items: list, test_line: int, branch_line: int):
    """The chain into the branch inside `items`: for each item before the one
    that holds it, the ways a path must take to go on past that item
    (fall_through_steps); then the chain inside the item that holds it."""
    steps = []
    for item in items:
        found = chain_into(item, test_line, branch_line)
        if found is not None:
            chain = steps + found
            return chain
        steps = steps + fall_through_steps(item)
    return None


def chain_into(item: dict, test_line: int, branch_line: int):
    """The chain when `item` holds the branch: the way into the part of the
    item whose lines hold the test, then the chain inside it; or the item's
    own way, when its own test is on `test_line`. None when it does not."""
    if item["kind"] in EXITS:
        return None
    for way_items, span, step in ways_of(item):
        if not inside(span, test_line):
            continue
        found = chain_in(way_items, test_line, branch_line)
        if found is not None:
            chain = with_step(step, found)
            return chain
    test = item.get("test")
    if test is not None and test_line in leaf_lines(test):
        for leaf in leaves_of(test):
            found = chain_in(leaf.get("inner", []), test_line, branch_line)
            if found is not None:
                return found
    if tests_on(item, test_line):
        chain = final_steps(item, test_line, branch_line)
        return chain
    return None


def ways_of(item: dict) -> list:
    """[(items, lines, step), ...]: each way into an item's parts, the lines
    it holds, and the way taken to enter it (None: entered with no test)."""
    kind = item["kind"]
    test = item.get("test")
    if kind in ("if", "?:", "value &&", "value ||"):
        ways = [(item["then"], item.get("then_span"), (test, True)), (item["else"], item.get("else_span"), (test, False))]
        return ways
    if kind == "if constexpr":
        ways = [(item["then"], item.get("then_span"), None), (item["else"], item.get("else_span"), None)]
        return ways
    if kind in LOOPS:
        step = None
        if test is not None:
            step = (test, True)
        ways = [(item["body"] + item["update"], item.get("body_span"), step)]
        return ways
    if kind == "do":
        ways = [(item["body"], item.get("body_span"), None)]
        return ways
    if kind == "switch":
        ways = []
        for case in item["cases"]:
            ways.append((case["body"], case.get("span"), (test, {"case": case["line"]})))
        return ways
    return []


def with_step(step, found: list) -> list:
    if step is None:
        return found
    chain = [step] + found
    return chain


def inside(span, line: int) -> bool:
    found = span is not None and span[0] <= line <= span[1]
    return found


def tests_on(item: dict, line: int) -> bool:
    """Whether the item's own test is on `line`: one of its operands, or the
    item's own line (a switch, a loop)."""
    if item["kind"] in ("test of a switch", "if constexpr"):
        return False
    if item.get("line") == line:
        return True
    test = item.get("test")
    found = test is not None and line in leaf_lines(test)
    return found


def final_steps(item: dict, test_line: int, branch_line: int) -> list:
    """The branch's own way: into the part of the item holding
    `branch_line`; into an operand of the test, when `branch_line` is one of
    the test's own lines past its first; else past the item, the false way
    (a loop left, an `if` with no `else`, a `do` not repeated)."""
    kind = item["kind"]
    test = item.get("test")
    if kind == "switch":
        for case in item["cases"]:
            if inside(case.get("span"), branch_line):
                steps = [(test, {"case": case["line"]})]
                return steps
        steps = [(test, {"case": None})]
        return steps
    for way_items, span, step in ways_of(item):
        if step is not None and inside(span, branch_line):
            steps = [step]
            return steps
    if test is None:
        return []
    lines = leaf_lines(test)
    if lines and min(lines) < branch_line <= max(lines):
        operand = steps_to_operand(test, branch_line)
        if operand:
            return operand
    if kind == "do" and inside(item.get("body_span"), branch_line):
        steps = [(test, True)]
        return steps
    steps = [(test, False)]
    return steps


def steps_to_operand(test: dict, line: int):
    """The ways of the operands worked out before the first operand on
    `line` (`a &&` on one line, `b` on the next: `a` true); None when no
    operand past the first is on it."""
    op = test["op"]
    if op == "!":
        found = steps_to_operand(test["of"], line)
        return found
    if op in ("&&", "||"):
        found = steps_to_operand(test["left"], line)
        if found is not None:
            return found
        if line in leaf_lines(test["right"]):
            inner = steps_to_operand(test["right"], line) or []
            steps = [(test["left"], op == "&&")] + inner
            return steps
        return None
    if op == "?:":
        found = steps_to_operand(test["test"], line)
        if found is not None:
            return found
        for way, value in (("then", True), ("else", False)):
            if line in leaf_lines(test[way]):
                inner = steps_to_operand(test[way], line) or []
                steps = [(test["test"], value)] + inner
                return steps
        return None
    return None


def leaves_of(test: dict) -> list:
    """A test's operands, each a leaf (`op` "test"), in the order written."""
    op = test["op"]
    if op == "!":
        found = leaves_of(test["of"])
        return found
    if op in ("&&", "||"):
        found = leaves_of(test["left"]) + leaves_of(test["right"])
        return found
    if op == "?:":
        found = leaves_of(test["test"]) + leaves_of(test["then"]) + leaves_of(test["else"])
        return found
    return [test]


def leaf_lines(test: dict) -> list:
    lines = []
    for leaf in leaves_of(test):
        lines.append(leaf["line"])
    return lines


def fall_through_steps(item: dict) -> list:
    """The ways a path must take at `item` to go on past it: at an `if` one
    of whose ways always leaves (a `return`, `throw`, `goto`, a `break` or
    `continue` out of the block), the other way, and what that way needs to
    go on itself; nothing for a branch point every way of which can go on."""
    if item["kind"] != "if":
        return []
    then_on = falls_through(item["then"])
    else_on = falls_through(item["else"])
    if then_on and not else_on:
        steps = [(item["test"], True)] + needed_to_pass(item["then"])
        return steps
    if else_on and not then_on:
        steps = [(item["test"], False)] + needed_to_pass(item["else"])
        return steps
    return []


def needed_to_pass(items: list) -> list:
    steps = []
    for item in items:
        steps = steps + fall_through_steps(item)
    return steps


def falls_through(items: list) -> bool:
    """Whether some path through `items` reaches their end (reading B's paths)."""
    flow = flow_through(items, one(), "B")
    found = bool(flow["live"])
    return found


# PartConstraint

class PartConstraint(NamedTuple):
    """What one part of the HiOp may be along a path: its holders (of its
    value, as clang's checks read its type), its places, its value forms
    (PCHQ log 503, plan node PartConstraint)."""

    holders: frozenset
    places: frozenset
    value_forms: frozenset

    @staticmethod
    def unconstrained(all_holders) -> "PartConstraint":
        part = PartConstraint(frozenset(all_holders), frozenset(PLACES), frozenset(VALUE_FORMS))
        return part

    @staticmethod
    def intersect(first, second, held_facts=None) -> "PartConstraint":
        """The three intersections; with the holder facts, a place no holder
        left fits is dropped, and a holder no place left fits (a bit-field
        keeps the integer kinds, a global register the integers and
        pointers of at most 8 bytes, an element place its elements)."""
        holders = first.holders & second.holders
        places = first.places & second.places
        value_forms = first.value_forms & second.value_forms
        if held_facts is not None:
            holders, places = compatible(holders, places, held_facts)
        part = PartConstraint(holders, places, value_forms)
        return part

    @staticmethod
    def is_empty(part) -> bool:
        empty = not part.holders or not part.places or not part.value_forms
        return empty


def compatible(holders: frozenset, places: frozenset, held_facts: dict) -> tuple:
    if "field" in places:
        found = (holders, places)
        return found
    kept_holders = set()
    kept_places = set()
    for holder in holders:
        for place in places:
            if fits(holder, place, held_facts):
                kept_holders.add(holder)
                kept_places.add(place)
    found = (frozenset(kept_holders), frozenset(kept_places))
    return found


def fits(holder: str, place: str, held_facts: dict) -> bool:
    """Whether a part of this holder can be in this place (log 503 §2)."""
    key = (id(held_facts), holder, place)
    if key in CACHE["fits"]:
        return CACHE["fits"][key]
    found = False
    held = held_facts.get(holder)
    if place == "field":
        found = True
    elif place in ELEMENT_HOLDERS:
        found = holder in ELEMENT_HOLDERS[place]
    elif held is None:
        found = False
    elif place == "bit-field":
        found = held.kind in BIT_FIELD_KINDS
    elif place == "signed bit-field":
        found = held.kind in BIT_FIELD_KINDS and held.signed
    elif place == "global register":
        found = held.kind in ("integer", "enum", "pointer") and held.size is not None and held.size <= 8
    CACHE["fits"][key] = found
    return found


def all_holders(held_facts: dict) -> frozenset:
    """Every holder a part may be: each spelling clang gave facts for (not
    void, not a function, unless in TYPE_ONLY_HOLDERS), and the holders an
    option's type needs (an m2 under -fenable-matrix, an _Accum under
    -ffixed-point)."""
    key = id(held_facts)
    if key in CACHE["holders"]:
        return CACHE["holders"][key]
    found = set()
    for spelling, held in held_facts.items():
        if held is not None and (held.kind not in ("void", "function", "builtin_other") or spelling in TYPE_ONLY_HOLDERS):
            found.add(spelling)
    for name, options, holder, preamble in loop_module().OPTION_NAMES:
        if holder:
            found.add(holder)
    for holder in loop_module().HOLDER_PREAMBLE:
        found.add(holder)
    CACHE["holders"][key] = frozenset(found)
    return CACHE["holders"][key]


# AbstractConstraint

class AbstractConstraint(NamedTuple):
    """What a program must be to take a branch, or a chain of them: one
    PartConstraint for each part, the options (a flag required; one
    forbidden written `not <flag>`), the targets among the three (PCHQ log
    503, plan node AbstractConstraint)."""

    parts: tuple
    options: frozenset
    targets: frozenset

    @staticmethod
    def from_base_context(base_context, held_facts) -> "AbstractConstraint":
        """The constraint a chain starts from: one part for each of the base
        context's parts, each open. What the base has (its holders, places,
        value forms, options, target) is kept by the writer wherever the chain
        allows it (write_from_constraint), not pinned here: the base took the
        other way at the branch's own test, so what that test reads must be
        free to change (run tlp1_l10's base for EmitStoreThroughLValue
        2510->2527 reads part 0 as a matrix element, and the branch needs it
        to be a bit-field)."""
        constraint = open_constraint(len(base_context.holders), held_facts)
        return constraint

    @staticmethod
    def unlocking_set_for_test(test: dict, want_true, part_count: int, held_facts: dict) -> list:
        """[AbstractConstraint, ...]: the alternatives under which `test`
        comes out `want_true`, read through its `!`, `&&`, `||` and `?:` (De
        Morgan's rules) down to each operand's atoms (leaf_unlocking). A
        switch's way narrows a constant integer part when its case label is
        0..5; a test with nothing read leaves everything open."""
        if isinstance(want_true, dict) and want_true.get("values") and test is not None:
            found = switch_case_unlocking(test, want_true["values"], part_count, held_facts)
            return found
        if not isinstance(want_true, bool) or test is None:
            found = [open_constraint(part_count, held_facts)]
            return found
        op = test["op"]
        if op == "!":
            found = AbstractConstraint.unlocking_set_for_test(test["of"], not want_true, part_count, held_facts)
            return found
        if op in ("&&", "||"):
            found = joined_unlocking(test, want_true, part_count, held_facts)
            return found
        if op == "?:":
            found = conditional_unlocking(test, want_true, part_count, held_facts)
            return found
        found = leaf_unlocking(test, want_true, part_count, held_facts)
        return found

    @staticmethod
    def intersect(first, second, held_facts=None) -> "AbstractConstraint":
        parts = []
        for first_part, second_part in zip(first.parts, second.parts):
            parts.append(PartConstraint.intersect(first_part, second_part, held_facts))
        constraint = AbstractConstraint(tuple(parts), first.options | second.options, first.targets & second.targets)
        return constraint

    @staticmethod
    def is_empty(constraint) -> bool:
        for part in constraint.parts:
            if PartConstraint.is_empty(part):
                return True
        for option in constraint.options:
            if "not " + option in constraint.options:
                return True
        empty = not constraint.targets
        return empty

    @staticmethod
    def to_candidates(constraint, base_context, writer) -> list:
        candidates = CandidateWriter.write_from_constraint(writer, base_context, constraint)
        return candidates


def open_constraint(part_count: int, held_facts: dict) -> AbstractConstraint:
    parts = []
    for part in range(part_count):
        parts.append(PartConstraint.unconstrained(all_holders(held_facts)))
    constraint = AbstractConstraint(tuple(parts), frozenset(), frozenset(TARGETS))
    return constraint


def switch_case_unlocking(test: dict, values: list, part_count: int, held_facts: dict) -> list:
    """When a switch tests an integer expression derived from a part (`ord`,
    `Ord->getZExtValue()`) and its case label is an integer in 0..5, narrows
    that part's value_forms to the case's constant form."""
    start = open_constraint(part_count, held_facts)
    forms = []
    for value in values:
        form = "constant " + str(value)
        if form in CONSTANT_FORMS and form not in forms:
            forms.append(form)
    if not forms:
        return [start]
    found = []
    for parts in parts_of_leaf(test, test.get("text") or "", part_count):
        new_parts = list(start.parts)
        for part in parts:
            old = new_parts[part]
            new_parts[part] = old._replace(value_forms=old.value_forms & frozenset(forms))
        narrowed = AbstractConstraint.intersect(start._replace(parts=tuple(new_parts)), start, held_facts)
        if not AbstractConstraint.is_empty(narrowed) and narrowed not in found:
            found.append(narrowed)
    if not found:
        return [start]
    return found


def joined_unlocking(test: dict, want_true: bool, part_count: int, held_facts: dict) -> list:
    """`a && b` true: both; false: `a` false, or `a` true and `b` false.
    `a || b` true: `a` true, or `a` false and `b` true; false: both false."""
    unlock = AbstractConstraint.unlocking_set_for_test
    left = test["left"]
    right = test["right"]
    if test["op"] == "&&":
        if want_true:
            found = products(unlock(left, True, part_count, held_facts), unlock(right, True, part_count, held_facts),
                             held_facts)
            return found
        found = unions(unlock(left, False, part_count, held_facts),
                       products(unlock(left, True, part_count, held_facts),
                                unlock(right, False, part_count, held_facts), held_facts))
        return found
    if want_true:
        found = unions(unlock(left, True, part_count, held_facts),
                       products(unlock(left, False, part_count, held_facts),
                                unlock(right, True, part_count, held_facts), held_facts))
        return found
    found = products(unlock(left, False, part_count, held_facts), unlock(right, False, part_count, held_facts),
                     held_facts)
    return found


def conditional_unlocking(test: dict, want_true: bool, part_count: int, held_facts: dict) -> list:
    unlock = AbstractConstraint.unlocking_set_for_test
    chosen = products(unlock(test["test"], True, part_count, held_facts),
                      unlock(test["then"], want_true, part_count, held_facts), held_facts)
    other = products(unlock(test["test"], False, part_count, held_facts),
                     unlock(test["else"], want_true, part_count, held_facts), held_facts)
    found = unions(chosen, other)
    return found


def products(firsts: list, seconds: list, held_facts: dict) -> list:
    found = []
    for first in firsts:
        for second in seconds:
            narrowed = AbstractConstraint.intersect(first, second, held_facts)
            if AbstractConstraint.is_empty(narrowed) or narrowed in found:
                continue
            found.append(narrowed)
            if len(found) >= ALTERNATIVES_KEPT:
                return found
    return found


def unions(firsts: list, seconds: list) -> list:
    found = []
    for constraint in firsts + seconds:
        if constraint not in found:
            found.append(constraint)
    found = found[:ALTERNATIVES_KEPT]
    return found


# one operand: what its atoms read

def leaf_reading(test: dict):
    """(kind, name, receiver) of an operand, read from its atoms, its
    outermost form first: a place test (clang's LValue kinds), a bit-field's
    sign (`Info.IsSigned`), a sanitizer, an option (the loop's OPTION_NAMES),
    a test of a holder's type (accepted_signatures.type_predicate, the loop's
    CHANGE_FOR), a constant, an lvalue, the target; None when it reads none
    of them."""
    loop = loop_module()
    atoms = test.get("atoms") or []
    text = test.get("text") or ""
    outer = {}
    if atoms:
        outer = atoms[0]
    if outer.get("atom") == "name" and outer.get("name") in ("InputSigned", "OutputSigned"):
        return ("holder", "isSignedIntegerOrEnumerationType", outer["name"])
    if outer.get("atom") == "name" and outer.get("name") in ("TyA", "VecTy"):
        return ("holder", "isVectorType", "Arg")
    if "PromoteType->isUnsignedIntegerType() != UnderlyingType->isUnsignedIntegerType()" in text:
        return ("holder", "isUnsignedIntegerType", "UnderlyingType")
    if "Combined != MemberQuals" in text:
        return ("holder", "hasQualifiers", "BaseExpr")
    if "IntegerContantExpr" in text:
        return ("constant", "isIntegerConstantExpr", "IndexExpr")
    if outer.get("atom") == "name" and outer.get("name") in ("Ord", "Scp"):
        return ("constant", "ConstantInt", outer["name"])
    if outer.get("atom") == "name" and outer.get("name") == "EmitBoolCondBranch":
        return ("constant", "EmitBoolCondBranch", "Cond")
    if outer.get("atom") == "name" and outer.get("name") == "IndirectMemberDecl":
        return ("holder", "IndirectMemberDecl", "BaseExpr")
    if "attr::NoDeref" in text:
        return ("holder", "NoDeref", text)
    if "IndirectFieldDecl" in text:
        return ("holder", "IndirectFieldDecl", text)
    if "dyn_cast<FieldDecl>" in text or "getAsSingle<FieldDecl>" in text:
        return ("holder", "FieldDecl", text)
    if outer.get("atom") == "name":
        for atom in atoms:
            if atom.get("atom") in ("call", "compare", "field"):
                outer = atom
                break
    callee = ""
    receiver = ""
    template = ""
    args = []
    if outer.get("atom") == "call":
        callee = outer["callee"]
        receiver = outer["receiver"]
        template = outer.get("template", "")
        args = outer.get("arguments") or []
    if outer.get("atom") == "field":
        receiver = outer["receiver"]
    if callee in ("isa", "dyn_cast", "cast", "isa_and_nonnull", "dyn_cast_or_null", "dyn_cast_if_present") and template and args:
        arg0 = args[0]
        if "ExtVectorElementExpr" in template:
            return ("place", "isExtVectorElt", arg0)
        if "ArraySubscriptExpr" in template:
            return ("place", "isVectorElt", arg0)
        if "ConstantInt" in template:
            return ("constant", "ConstantInt", arg0)
        if "IntegerType" in template:
            return ("holder", "isIntegerTy", arg0)
        if "ExtVectorType" in template:
            return ("holder", "isExtVectorType", arg0)
        if "VectorType" in template:
            return ("holder", "isVectorType", arg0)
        if "PointerType" in template:
            return ("holder", "isPointerType", arg0)
        if "RecordType" in template:
            return ("holder", "isRecordType", arg0)
        if "ComplexType" in template:
            return ("holder", "isAnyComplexType", arg0)
        if "AtomicType" in template:
            return ("holder", "isAtomicType", arg0)
        if "EnumType" in template:
            return ("holder", "isEnumeralType", arg0)
        if "BitIntType" in template:
            return ("holder", "isBitIntType", arg0)
        if "FunctionType" in template or "FunctionProtoType" in template:
            return ("holder", "isFunctionType", arg0)
        if "ArrayType" in template or "ConstantArrayType" in template:
            return ("holder", "isArrayType", arg0)
    if callee in ("getAs", "castAs") and template:
        if "ExtVectorType" in template:
            return ("holder", "isExtVectorType", receiver)
        if "VectorType" in template:
            return ("holder", "isVectorType", receiver)
        if "PointerType" in template:
            return ("holder", "isPointerType", receiver)
        if "RecordType" in template:
            return ("holder", "isRecordType", receiver)
        if "ComplexType" in template:
            return ("holder", "isAnyComplexType", receiver)
        if "AtomicType" in template:
            return ("holder", "isAtomicType", receiver)
        if "EnumType" in template:
            return ("holder", "isEnumeralType", receiver)
        if "BitIntType" in template:
            return ("holder", "isBitIntType", receiver)
        if "FunctionType" in template or "FunctionProtoType" in template:
            return ("holder", "isFunctionType", receiver)
        if "ArrayType" in template or "ConstantArrayType" in template:
            return ("holder", "isArrayType", receiver)
        if "BuiltinType" in template:
            return ("holder", "isBuiltinType", receiver)
    if callee == "isNull" and any(w in receiver for w in ("PromotionType", "promotionTy", "PromoteType")):
        if "promotionTy" in receiver:
            return ("holder", "promotionTy.isNull", receiver)
        if "PromoteType" in receiver:
            return ("holder", "PromoteType.isNull", receiver)
        return ("holder", "PromotionType.isNull", receiver)
    if callee == "isOne" and "Size" in receiver:
        return ("holder", "elementSize.isOne", receiver)
    if callee == "isPromotableIntegerType":
        return ("holder", "isPromotableIntegerType", args[0] if args else receiver)
    if callee == "isSpecificBuiltinType" and "Char_" in text:
        return ("holder", "isCharType", receiver)
    if callee == "isSpecificBuiltinType" and "Float" in text:
        return ("holder", "isSpecificBuiltinType", receiver)
    if callee == "typesAreCompatible" and "PromoteType" in text:
        return ("holder", "typesAreCompatible_PromoteType", "UnderlyingType")
    if callee in PLACE_TESTS:
        found = ("place", callee, receiver)
        return found
    if outer.get("atom") == "field" and outer.get("field") == "IsSigned":
        found = ("signed", "IsSigned", receiver)
        return found
    if loop.sanitizer_kinds(text) and "SanitizerKind" in text:
        found = ("sanitizer", "", receiver)
        return found
    for option_name, options, holder, preamble in loop.OPTION_NAMES:
        if option_name == callee or re.search(r"(?<!\w)" + re.escape(option_name) + r"(?!\w)", text):
            found = ("option", option_name, receiver)
            return found
    if callee in type_test_names() or is_a_table_test(callee):
        found = ("holder", callee, receiver)
        return found
    if callee in loop.CONSTANT_NAMES:
        found = ("constant", callee, receiver)
        return found
    if callee == "isGLValue":
        found = ("lvalue", callee, receiver)
        return found
    for name in loop.TARGET_NAMES:
        if name in text:
            found = ("target", name, "")
            return found
    return None


def type_test_names() -> frozenset:
    """The type tests accepted_signatures.type_predicate answers (clang's
    QualType tests and CodeGen's llvm::Type ones)."""
    if CACHE["type_tests"] is not None:
        return CACHE["type_tests"]
    signatures = signatures_module()
    sample = signatures.Held("int", "integer", True, 4)
    CACHE["type_tests"] = frozenset(signatures.type_answers(sample))
    return CACHE["type_tests"]


def is_a_table_test(name: str) -> bool:
    if not name:
        return False
    for predicate, true_holder, false_holder in loop_module().CHANGE_FOR:
        if predicate == name:
            return True
    return False


def leaf_unlocking(test: dict, want_true: bool, part_count: int, held_facts: dict) -> list:
    """The alternatives under which one operand comes out `want_true`."""
    start = open_constraint(part_count, held_facts)
    reading = leaf_reading(test)
    if reading is None:
        return [start]
    kind, name, receiver = reading
    if kind == "sanitizer":
        found = sanitizer_unlocking(start, test, receiver, want_true)
        return found
    if kind == "option":
        found = option_unlocking(start, test, name, receiver, want_true, part_count, held_facts)
        return found
    if kind == "target":
        found = []
        for target in TARGETS:
            found.append(start._replace(targets=frozenset([target])))
        return found
    found = []
    for parts in parts_of_leaf(test, receiver, part_count):
        narrowed = part_narrowed(start, parts, kind, name, receiver, want_true, held_facts)
        if not AbstractConstraint.is_empty(narrowed) and narrowed not in found:
            found.append(narrowed)
    return found


def sanitizer_unlocking(start, test: dict, receiver: str, want_true: bool) -> list:
    """`SanOpts.has(SanitizerKind::X)`: -fsanitize=x; read through
    `SanitizeTrap`, -fsanitize-trap=x beside it; several kinds named, any
    one of them (true) or none (false)."""
    loop = loop_module()
    flags = []
    for kind, flag in loop.sanitizer_kinds(test.get("text") or ""):
        flags.append(flag)
    found = []
    if not want_true:
        forbidden = set()
        for flag in flags:
            forbidden.add("not " + sanitizer_word(flag, receiver))
        found.append(start._replace(options=frozenset(forbidden)))
        return found
    for flag in flags:
        words = {"-fsanitize=" + flag}
        if "SanitizeTrap" in receiver:
            words.add("-fsanitize-trap=" + flag)
        found.append(start._replace(options=frozenset(words)))
    return found


def sanitizer_word(flag: str, receiver: str) -> str:
    if "SanitizeTrap" in receiver:
        return "-fsanitize-trap=" + flag
    return "-fsanitize=" + flag


def option_unlocking(start, test: dict, name: str, receiver: str, want_true: bool, part_count: int,
                     held_facts: dict) -> list:
    """An option the loop's table names (OPTION_NAMES): true, each of its
    flags, alone and with the holder its type needs in each part set read;
    false, its flags forbidden."""
    loop = loop_module()
    found = []
    for option_name, options, holder, preamble in loop.OPTION_NAMES:
        if option_name != name:
            continue
        for option in options:
            if not want_true:
                found.append(start._replace(options=frozenset(["not " + option])))
                continue
            with_option = start._replace(options=frozenset([option]))
            found.append(with_option)
            if not holder:
                continue
            for parts in parts_of_leaf(test, receiver, part_count):
                new_parts = list(with_option.parts)
                for part in parts:
                    new_parts[part] = new_parts[part]._replace(holders=frozenset([holder]))
                found.append(with_option._replace(parts=tuple(new_parts)))
    if not found:
        found = [start]
    return found


def parts_of_leaf(test: dict, receiver: str, part_count: int) -> list:
    """The part sets an operand reads: the part a chain bound its receiver
    to (bound_chains); else the parts the loop's names place (PART_NAMES:
    `getLHS` part 0, `E->getType()` every part); else each part in turn."""
    if "bound" in test:
        found = [[test["bound"]]]
        return found
    text_or_recv = receiver or test.get("text") or ""
    if part_count == 3 and "slt" not in (test.get("text") or ""):
        if "LHS" in text_or_recv and "RHS" not in text_or_recv:
            return [[1]]
        if "RHS" in text_or_recv and "LHS" not in text_or_recv:
            return [[2]]
    loop = loop_module()
    sets = []
    for parts in loop.parts_named(text_or_recv):
        if parts == ["every"]:
            sets.append(list(range(part_count)))
        elif parts and max(parts) < part_count and parts not in sets:
            sets.append(list(parts))
    if sets:
        return sets
    each = []
    for part in range(part_count):
        each.append([part])
    return each


def part_narrowed(start, parts: list, kind: str, name: str, receiver: str, want_true: bool,
                  held_facts: dict) -> AbstractConstraint:
    new_parts = list(start.parts)
    for part in parts:
        old = new_parts[part]
        if kind == "holder":
            new_parts[part] = old._replace(holders=old.holders & holders_where(name, receiver, want_true, held_facts))
        elif kind == "place":
            places = frozenset(PLACE_TESTS[name])
            if not want_true:
                places = frozenset(PLACES) - places
            new_parts[part] = old._replace(places=old.places & places)
        elif kind == "signed":
            signed = holders_where("isSignedIntegerOrEnumerationType", "", want_true, held_facts)
            new_parts[part] = old._replace(holders=old.holders & signed,
                                           places=old.places & frozenset(("bit-field", "signed bit-field")))
        elif kind == "constant":
            forms = frozenset(CONSTANT_FORMS)
            if not want_true:
                forms = frozenset(VALUE_FORMS) - forms
            new_parts[part] = old._replace(value_forms=old.value_forms & forms)
        elif kind == "lvalue":
            forms = frozenset(("place", "parenthesis"))
            if not want_true:
                forms = frozenset(CONSTANT_FORMS)
            new_parts[part] = old._replace(value_forms=old.value_forms & forms)
    narrowed = AbstractConstraint.intersect(start._replace(parts=tuple(new_parts)), start, held_facts)
    return narrowed


def holders_where(name: str, receiver: str, want_true: bool, held_facts: dict) -> frozenset:
    """The holders a type test comes out `want_true` for: type_predicate on
    each holder, or on what it holds when the receiver reads its element or
    pointee (log 503 §2); a test only the loop's table names (CHANGE_FOR:
    `wasCast`), its holder for each way. A holder the test is not answered
    for is kept both ways; one clang gave no facts for (an option's m2 or
    _Accum) is taken as failing every type test."""
    signatures = signatures_module()
    inner = False
    for read in INNER_READS:
        if read == "getElementType()" and "getAddress()" in receiver:
            continue
        if read in receiver:
            inner = True
    if receiver == "QT" and name in ("isSignedIntegerType", "isUnsignedIntegerType", "isFloatingType"):
        inner = True
    found = set()
    for spelling in all_holders(held_facts):
        held = held_facts.get(spelling)
        if inner:
            if held is None or held.inner is None:
                continue
            if any(w in receiver for w in ("SrcElt", "DstElt", "InputSigned", "OutputSigned", "VTy", "VectorType")) or receiver == "QT":
                if held.kind not in ("vector", "extvector"):
                    continue
            if any(w in receiver for w in ("Pointee", "elementType", "elementSize")):
                if held.kind != "pointer":
                    continue
        answer = holder_answer(name, spelling, held, inner, signatures)
        if answer is signatures.UNDECIDED or answer == want_true:
            found.add(spelling)
    return frozenset(found)


def holder_answer(name: str, spelling: str, held, inner: bool, signatures):
    if name in type_test_names():
        if held is None:
            return False
        tested = held
        if inner:
            tested = held.inner
        answer = signatures.type_predicate(name, tested)
        return answer
    named = False
    for predicate, true_holder, false_holder in loop_module().CHANGE_FOR:
        if predicate != name:
            continue
        named = True
        if spelling == true_holder:
            return True
    if not named:
        return signatures.UNDECIDED
    # the table's holder makes it true; any other holder, false
    return False


# the receivers a chain names, each bound to one part

def bound_chains(chain: list, part_count: int) -> list:
    """The chain once for each way of binding the receivers its operands
    read and no name places (`Dst`, `OrigTy`, `DstType`) to the parts, each
    receiver one part all along the chain: `Dst.isGlobalReg()` and
    `Dst.isMatrixElt()` read the same part."""
    roots = []
    for step_test, step_way in chain:
        if not isinstance(step_way, bool) or step_test is None:
            continue
        for leaf in leaves_of(step_test):
            root = unbound_root(leaf, part_count)
            if root and root not in roots:
                roots.append(root)
    if not roots or part_count < 2:
        return [chain]
    chains = []
    for assignment in itertools.product(range(part_count), repeat=len(roots)):
        chains.append(bound_chain(chain, dict(zip(roots, assignment)), part_count))
        if len(chains) >= BINDINGS_KEPT:
            break
    return chains


def unbound_root(leaf: dict, part_count: int) -> str:
    """The name an operand's receiver starts with (`DstAddr` of
    `DstAddr.getElementType()`), when the operand reads a part and no name
    of the loop places it; '' otherwise."""
    reading = leaf_reading(leaf)
    if reading is None or reading[0] not in PART_KINDS:
        return ""
    receiver = reading[2]
    if not receiver:
        return ""
    if part_count == 3 and any(w in receiver for w in ("LHS", "RHS")):
        return ""
    for parts in loop_module().parts_named(receiver):
        if parts == ["every"] or (parts and max(parts) < part_count):
            return ""
    found = re.match(r"[\s(*&]*(?:this\s*->\s*)?([A-Za-z_]\w*)", receiver)
    if found is None:
        return ""
    root = found.group(1)
    return root


def bound_chain(chain: list, binding: dict, part_count: int) -> list:
    bound = []
    for step_test, step_way in chain:
        if step_test is None or not isinstance(step_way, bool):
            bound.append((step_test, step_way))
            continue
        copied = copy.deepcopy(step_test)
        for leaf in leaves_of(copied):
            root = unbound_root(leaf, part_count)
            if root in binding:
                leaf["bound"] = binding[root]
        bound.append((copied, step_way))
    return bound


# CandidateWriter

class CandidateWriter(NamedTuple):
    """Writes a constraint as a context (PCHQ log 503, plan node
    CandidateWriter): the holders the standard form can write (the pool, and
    the loop's HOLDER_PREAMBLE), and each holder's facts."""

    pool: frozenset
    held_facts: dict

    @staticmethod
    def write_from_constraint(writer, base_context, constraint) -> list:
        """[Context]: for each part, the base's own holder, place and value
        form where the constraint allows them, else the simplest it allows
        (SIMPLE_HOLDERS, PLACES and VALUE_FORMS in order), the place written
        with the part's own holder (`register int *reg_k_a __asm__("sp");`,
        `_Bool a : 1;`); the base's options the constraint does not forbid,
        with the ones it requires; the base's target if allowed. Also emits
        representatives from EQUIVALENCE_CLASS_HOLDERS for narrowed parts and
        alternate operator templates. [] when no holder of a part can be
        written."""
        loop = loop_module()
        base = base_reading(base_context)
        slots = loop.slots_of_operator(base_context.operator)
        part_count = len(constraint.parts)
        choices = []
        for index in range(part_count):
            is_type_slot = index < len(slots) and slots[index] in ("T", "U", "V", "W")
            choice = chosen_part(constraint.parts[index], base["parts"][index], writer, is_type_slot)
            if choice is None:
                return []
            choices.append(choice)
        options = chosen_options(constraint, base)
        target = chosen_target(constraint, base)
        op_name = base_context.operator.name
        alt_operators = []
        for alt_op in loop.operators_of(loop.key_for(base_context.operator)):
            if alt_op != base_context.operator and len(loop.slots_of_operator(alt_op)) == part_count:
                alt_operators.append(alt_op)
        results = []
        seen_choices = set()

        def emit(cand_choices, op=None):
            use_op = op or base_context.operator
            key = (use_op, tuple(cand_choices))
            if key in seen_choices:
                return
            seen_choices.add(key)
            ctx = written_context(use_op, cand_choices, options, target, base, writer)
            if ctx is not None:
                results.append(ctx)

        if not (choices == base["parts"] and set(options) == set(base["options"]) and target == base["target"]):
            emit(choices)
        for alt_op in alt_operators:
            emit(choices, alt_op)

        all_count = len(all_holders(writer.held_facts))
        narrowed = [i for i in range(part_count) if len(constraint.parts[i].holders) < all_count]
        rep_limit = 3
        for index in narrowed:
            if op_name == "VAArgExpr" and index == 0:
                continue
            is_type_slot = index < len(slots) and slots[index] in ("T", "U", "V", "W")
            c_place, c_form = choices[index][1], choices[index][2]
            added = 0
            for rep in EQUIVALENCE_CLASS_HOLDERS:
                if rep not in constraint.parts[index].holders or rep == choices[index][0]:
                    continue
                if op_name == "ConvertVectorExpr":
                    rep_held = writer.held_facts.get(rep)
                    if rep_held is None or rep_held.kind not in ("vector", "extvector"):
                        continue
                if not is_type_slot and rep in TYPE_ONLY_HOLDERS:
                    for alt_op in alt_operators:
                        alt_slots = loop.slots_of_operator(alt_op)
                        if index < len(alt_slots) and alt_slots[index] in ("T", "U", "V", "W"):
                            alt_type = list(choices)
                            alt_type[index] = (rep, "field", "place")
                            emit(alt_type, alt_op)
                    continue
                use_place = "field" if is_type_slot else c_place
                use_form = "place" if is_type_slot else c_form
                if not is_type_slot and use_form not in CONSTANT_FORMS and not fits(rep, use_place, writer.held_facts):
                    continue
                alt = list(choices)
                alt[index] = (rep, use_place, use_form)
                emit(alt)
                for alt_op in alt_operators:
                    emit(alt, alt_op)
                for other in narrowed:
                    if op_name == "VAArgExpr" and other == 0:
                        continue
                    if other != index and rep in constraint.parts[other].holders:
                        other_type = other < len(slots) and slots[other] in ("T", "U", "V", "W")
                        if not other_type and rep not in TYPE_ONLY_HOLDERS and fits(rep, choices[other][1], writer.held_facts):
                            alt_both = list(alt)
                            alt_both[other] = (rep, choices[other][1], choices[other][2])
                            emit(alt_both)
                added += 1
                if added >= rep_limit:
                    break
        arms = None
        if part_count == 2 and op_name != "VAArgExpr":
            arms = (0, 1)
        elif part_count == 3 and op_name == "ConditionalOperator":
            arms = (1, 2)
        if arms is not None and (arms[0] in narrowed or arms[1] in narrowed):
            i0, i1 = arms
            t0 = i0 < len(slots) and slots[i0] in ("T", "U", "V", "W")
            t1 = i1 < len(slots) and slots[i1] in ("T", "U", "V", "W")
            if not t0 and not t1:
                same_added = 0
                for rep in EQUIVALENCE_CLASS_HOLDERS:
                    if rep in TYPE_ONLY_HOLDERS:
                        continue
                    if rep not in constraint.parts[i0].holders or rep not in constraint.parts[i1].holders:
                        continue
                    if op_name == "ConvertVectorExpr":
                        rep_held = writer.held_facts.get(rep)
                        if rep_held is None or rep_held.kind not in ("vector", "extvector"):
                            continue
                    if fits(rep, choices[i0][1], writer.held_facts) and fits(rep, choices[i1][1], writer.held_facts):
                        alt = list(choices)
                        alt[i0] = (rep, choices[i0][1], choices[i0][2])
                        alt[i1] = (rep, choices[i1][1], choices[i1][2])
                        emit(alt)
                        same_added += 1
                        if same_added >= 4:
                            break
                if (i0 in narrowed and i1 in narrowed) or op_name in ("ConvertVectorExpr", "ConditionalOperator"):
                    reps0 = [r for r in EQUIVALENCE_CLASS_HOLDERS
                             if r not in TYPE_ONLY_HOLDERS and r in constraint.parts[i0].holders
                             and (op_name != "ConvertVectorExpr" or (writer.held_facts.get(r) is not None and writer.held_facts.get(r).kind in ("vector", "extvector")))
                             and fits(r, choices[i0][1], writer.held_facts)][:3]
                    reps1 = [r for r in EQUIVALENCE_CLASS_HOLDERS
                             if r not in TYPE_ONLY_HOLDERS and r in constraint.parts[i1].holders
                             and (op_name != "ConvertVectorExpr" or (writer.held_facts.get(r) is not None and writer.held_facts.get(r).kind in ("vector", "extvector")))
                             and fits(r, choices[i1][1], writer.held_facts)][:3]
                    pair_added = 0
                    for r0 in reps0:
                        for r1 in reps1:
                            if r0 == r1:
                                continue
                            alt = list(choices)
                            alt[i0] = (r0, choices[i0][1], choices[i0][2])
                            alt[i1] = (r1, choices[i1][1], choices[i1][2])
                            emit(alt)
                            pair_added += 1
                            if pair_added >= 4:
                                break
                        if pair_added >= 4:
                            break
        return results


def writer_of(pool) -> CandidateWriter:
    """The writer for the loop's pool, with the holder facts saved by the run
    that asked clang for them (FACTS_FILE)."""
    loop = loop_module()
    signatures = signatures_module()
    synth_map = (
        ("volatile int", "int"),
        ("noderef_int_ptr", "int *"),
        ("noderef_struct_ptr", "struct S *"),
        ("struct S_anon", "struct S"),
        ("struct S_anon *", "struct S *"),
        ("nullptr_t", "void *"),
    )
    synth_names = {s for s, _ in synth_map}
    holders = sorted(set(pool) | set(loop.HOLDER_PREAMBLE))
    base_holders = sorted((set(pool) | set(loop.HOLDER_PREAMBLE)) - synth_names)
    domain, added = signatures.domain_of(base_holders)
    asked = list(domain) + sorted(set(signatures.CONTEXT_TYPES.values()) - {"void"})
    work = os.environ.get("TLP_WORK", "/work/enumerate_every_path")
    preamble = []
    for holder in sorted(set(loop.HOLDER_PREAMBLE) - synth_names):
        for line in loop.HOLDER_PREAMBLE[holder]:
            if line not in preamble:
                preamble.append(line)
    held_facts = signatures.holder_facts_kept(asked, os.path.join(work, "holder_facts"), FACTS_FILE, tuple(preamble))
    for synth, like in synth_map:
        if held_facts.get(synth) is None and held_facts.get(like) is not None:
            held_facts[synth] = held_facts[like]
    writer = CandidateWriter(frozenset(holders), held_facts)
    return writer


def base_reading(base_context) -> dict:
    """What the base is, part by part: (holder of its value, place, value
    form), read from its program (the standard form's when it has none); its
    options beyond our setup's command; its target; its declarations."""
    from context import our_setup
    loop = loop_module()
    slots = loop.slots_of_operator(base_context.operator)
    body, struct = own_lines(base_context.program)
    parts = []
    for index in range(len(base_context.holders)):
        holder = base_context.holders[index]
        name = ""
        if index < len(slots):
            name = slots[index]
        place, form = place_and_form(body, struct, name)
        if place in ELEMENT_READS:
            holder = ELEMENT_OF.get(holder, holder)
        parts.append((holder, place, form))
    ours = our_setup().command.split()
    options = []
    for word in base_context.setup.command.split():
        if word not in ours and not word.startswith("--target=") and word not in options:
            options.append(word)
    reading = {"parts": parts, "options": options, "target": loop.target_of(base_context),
               "preamble": list(base_context.setup.preamble)}
    return reading


def own_lines(program: str) -> tuple:
    body = ""
    struct = ""
    for line in (program or "").split("\n"):
        if "op_" + key_name() + "(" in line:
            body = line
        if line.startswith("struct P_" + key_name() + " {"):
            struct = line
    found = (body, struct)
    return found


def place_and_form(body: str, struct: str, name: str) -> tuple:
    """(place, value form) of the part named `name` in a program's op_k and
    P_k lines; a field read as it is when there is no program."""
    if not body or not name:
        found = ("field", "place")
        return found
    place = "field"
    if re.search(r"(?<!\w)reg_" + key_name() + "_" + re.escape(name) + r"(?!\w)", body):
        place = "global register"
    elif "p->" + name + "[0][1]" in body:
        place = "matrix element"
    elif "p->" + name + "[1]" in body:
        place = "vector element"
    elif re.search(re.escape("p->" + name + ".x") + r"(?!\w)", body) or re.search(re.escape("p->" + name + ".hi") + r"(?!\w)", body):
        place = "ext vector element"
    elif re.search(r"(?<!\w)" + re.escape(name) + r"\s*:\s*\d+\s*;", struct):
        place = "bit-field"
    form = "place"
    spellings = ("p->" + name, "reg_" + key_name() + "_" + name, "part_" + key_name() + "_" + name + "()")
    held = False
    for spelling in spellings:
        if re.search(re.escape(spelling) + r"(?!\w)", body):
            held = True
    if not held:
        form = "constant 1"
    elif re.search(r"\(\s*" + re.escape("p->" + name) + r"\s*\)", body):
        form = "parenthesis"
    found = (place, form)
    return found


def chosen_part(part: PartConstraint, base_part: tuple, writer: CandidateWriter, is_type_slot: bool = False):
    """(holder, place, value form) for one part: the base's where allowed,
    else the simplest allowed; the holder first, then a place it fits."""
    base_holder, base_place, base_form = base_part
    if is_type_slot:
        for holder in holder_order(part.holders, base_holder, writer, is_type_slot=True):
            return (holder, "field", "place")
        return None
    form = base_form
    if form not in part.value_forms:
        form = first_of(VALUE_FORMS, part.value_forms)
    if form in CONSTANT_FORMS:
        holder = base_holder
        if holder not in part.holders or holder in TYPE_ONLY_HOLDERS:
            holder = first_of(holder_order(part.holders, base_holder, writer, is_type_slot=False), part.holders)
        found = (holder or base_holder, "field", form)
        return found
    for holder in holder_order(part.holders, base_holder, writer, is_type_slot=False):
        for place in place_order(part.places, base_place):
            if fits(holder, place, writer.held_facts):
                found = (holder, place, form)
                return found
    return None


def first_of(order, allowed):
    for each in order:
        if each in allowed:
            return each
    return None


def holder_order(allowed: frozenset, base_holder: str, writer: CandidateWriter, is_type_slot: bool = False) -> list:
    """The holders the writer can write that the part allows: the base's
    first, then SIMPLE_HOLDERS, then EQUIVALENCE_CLASS_HOLDERS, then the
    others with facts by name, then those without."""
    order = []
    writable = set(writer.pool) | set(ELEMENT_OF)
    if not is_type_slot:
        writable = writable - set(TYPE_ONLY_HOLDERS)
    for name, options, holder, preamble in loop_module().OPTION_NAMES:
        if holder:
            writable.add(holder)
    if base_holder in allowed and base_holder in writable:
        order.append(base_holder)
    for holder in SIMPLE_HOLDERS + EQUIVALENCE_CLASS_HOLDERS:
        if holder in allowed and holder in writable and holder not in order:
            order.append(holder)
    rest = sorted(allowed & writable - set(order))
    for holder in rest:
        if writer.held_facts.get(holder) is not None:
            order.append(holder)
    for holder in rest:
        if writer.held_facts.get(holder) is None:
            order.append(holder)
    return order


def place_order(allowed: frozenset, base_place: str) -> list:
    order = []
    if base_place in allowed:
        order.append(base_place)
    for place in PLACES:
        if place in allowed and place not in order:
            order.append(place)
    return order


def chosen_options(constraint: AbstractConstraint, base: dict) -> list:
    options = []
    for word in base["options"]:
        if "not " + word not in constraint.options and word not in options:
            options.append(word)
    for flag in sorted(constraint.options):
        if not flag.startswith("not ") and flag not in options:
            options.append(flag)
    return options


def chosen_target(constraint: AbstractConstraint, base: dict) -> str:
    if base["target"] in constraint.targets:
        return base["target"]
    target = first_of(TARGETS, constraint.targets)
    return target


def written_context(operator, choices: list, options: list, target: str, base: dict, writer: CandidateWriter):
    """The context: the standard form of the parts' holders under the
    setup, then each part written in its place and value form; None when the
    standard form does not write it."""
    from context import Context, Setup, our_setup, standard_source
    loop = loop_module()
    preamble = list(base["preamble"])
    needs = list(options)
    for holder, place, form in choices:
        kept = holder
        if place in ELEMENT_HOLDERS:
            kept = ELEMENT_HOLDERS[place][holder]
        for each in (holder, kept):
            for line in loop.HOLDER_PREAMBLE.get(each, ()):
                add_new(preamble, line)
            for name, flags, option_holder, lines in loop.OPTION_NAMES:
                if option_holder and option_holder == each:
                    for line in lines:
                        add_new(preamble, line)
                    add_new(needs, flags[0])
    command = our_setup().command
    for word in needs:
        command = command + " " + word
    if target != loop.BASE_TARGET[0]:
        for name, triple in loop.OTHER_TARGETS:
            if name == target:
                command = loop.with_target(command, triple)
    setup = Setup(command, tuple(preamble))
    effective = []
    for holder, place, form in choices:
        effective.append(holder)
    try:
        text = standard_source(Context(operator, tuple(effective), setup))
    except Exception:
        return None
    program = with_places(text, operator, choices, target, writer)
    if program is None:
        return None
    holders = []
    for holder, place, form in choices:
        if place in ELEMENT_HOLDERS:
            holder = ELEMENT_HOLDERS[place][holder]
        holders.append(holder)
    if program == text:
        program = ""
    context = Context(operator, tuple(holders), setup, program)
    return context


def add_new(found: list, item) -> None:
    if item not in found:
        found.append(item)


def with_places(text: str, operator, choices: list, target: str, writer: CandidateWriter):
    """The standard form's program with each part written in its place and
    value form: a bit-field of its own holder (`_Bool a : 1;`), an element of
    the vector or matrix P_k keeps (`p->a[0][1]`), a global register of its
    own holder declared before P_k, a constant, in parentheses."""
    loop = loop_module()
    lines = text.split("\n")
    body_at = loop.index_of_line(lines, "op_" + key_name() + "(")
    struct_at = loop.index_of_line(lines, "struct P_" + key_name() + " {")
    if body_at < 0:
        return None
    slots = loop.slots_of_operator(operator)
    declarations = []
    for index in range(len(choices)):
        holder, place, form = choices[index]
        if index >= len(slots):
            continue
        name = slots[index]
        spelling = loop.spelling_in(lines[body_at], name)
        if not spelling:
            continue
        if form in CONSTANT_FORMS:
            held = writer.held_facts.get(holder)
            if held is not None and held.kind in ("struct", "union"):
                const_str = f"(({holder}){{0}})"
            elif holder != "int" and holder not in TYPE_ONLY_HOLDERS:
                const_str = f"(({holder}){CONSTANT_TEXT[form]})"
            else:
                const_str = CONSTANT_TEXT[form]
            lines[body_at] = loop.rewritten(lines[body_at], spelling, const_str)
            continue
        if place != "field" and (struct_at < 0 or not spelling.startswith("p->")):
            return None
        if place in ("bit-field", "signed bit-field"):
            field = f"{holder} {name} : {width_of(holder, writer)};"
            lines[struct_at] = loop.with_field_text(lines[struct_at], name, field)
        elif place in ELEMENT_HOLDERS:
            read = ELEMENT_READS[place].format(name=name)
            if place == "ext vector element" and holder == "ev4si":
                read = f"p->{name}.hi"
            lines[struct_at] = loop.with_field_text(lines[struct_at], name, f"{ELEMENT_HOLDERS[place][holder]} {name};")
            lines[body_at] = loop.rewritten(lines[body_at], spelling, read)
            spelling = read
        elif place == "global register":
            read = "reg_" + key_name() + "_" + name
            lines[body_at] = loop.rewritten(lines[body_at], spelling, read)
            spelling = read
            declarations.append(register_declaration(holder, name, target))
        if form == "parenthesis":
            lines[body_at] = loop.rewritten(lines[body_at], spelling, "(" + spelling + ")")
    lines = loop.with_declarations(lines, struct_at, declarations)
    program = "\n".join(lines)
    return program


def width_of(holder: str, writer: CandidateWriter) -> int:
    """A bit-field's width: the loop's WIDTH, or the holder's own width
    when narrower (a _Bool 1, a char 8)."""
    width = loop_module().WIDTH
    held = writer.held_facts.get(holder)
    if held is None:
        return width
    if held.kind == "bool":
        return 1
    bits = held.bits
    if not bits and held.size:
        bits = held.size * 8
    if bits:
        width = min(width, bits)
    return width


def register_declaration(holder: str, name: str, target: str) -> str:
    """`register int *reg_k_a __asm__("sp");`: the part's own holder, in the
    register the loop names for the target (GLOBAL_REGISTERS)."""
    loop = loop_module()
    register = loop.GLOBAL_REGISTERS.get(target, loop.GLOBAL_REGISTERS[loop.BASE_TARGET[0]])
    spelled = holder + " "
    if holder.endswith("*"):
        spelled = holder
    line = f"register {spelled}reg_{key_name()}_{name} __asm__(\"{register}\");"
    return line


# unlock_branch

def unlock_branch(branch: dict, base_context, tree, writer) -> list:
    """Block A of PCHQ log 503 §2: the chain into the branch in its
    function's tree; along it, from the base's constraint, each way's
    unlocking set intersected in turn (a state left empty is cut); each
    state left written as a context. The chain is tried once for each
    binding of its receivers to the parts (bound_chains)."""
    chain = BranchTree.super_chain_of_branch(tree, branch["test"], branch["first"])
    if chain is None:
        return []
    chain = with_case_values(chain, branch.get("file") or "")
    part_count = len(base_context.holders)
    candidates = []
    seen = set()
    for bound in bound_chains(chain, part_count):
        for state in states_after(bound, base_context, writer, part_count):
            for written in CandidateWriter.write_from_constraint(writer, base_context, state):
                key = loop_module().check.key_of(written)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(written)
                if len(candidates) >= 12:
                    return candidates
    return candidates


CASE_INT = re.compile(r"\bcase\s+([0-5])\s*:")


def with_case_values(chain: list, file: str) -> list:
    """Annotates switch steps `{"case": line}` with any integer case values
    `0..5` on or right above `line` in `file`."""
    if not file:
        return chain
    loop = loop_module()
    source = loop.source_lines(file)
    updated = []
    for step_test, step_way in chain:
        if isinstance(step_way, dict) and isinstance(step_way.get("case"), int):
            line = step_way["case"]
            text = loop.text_at(source, line) + " " + loop.case_labels_above(source, line + 1)
            values = []
            for match in CASE_INT.finditer(text):
                val = match.group(1)
                if val not in values:
                    values.append(val)
            if values:
                way = dict(step_way)
                way["values"] = values
                updated.append((step_test, way))
                continue
        updated.append((step_test, step_way))
    return updated


def states_after(chain: list, base_context, writer: CandidateWriter, part_count: int) -> list:
    """Block A's lines 2 to 13."""
    states = [AbstractConstraint.from_base_context(base_context, writer.held_facts)]
    for step_test, step_way in chain:
        next_states = []
        unlocking_list = AbstractConstraint.unlocking_set_for_test(step_test, step_way, part_count, writer.held_facts)
        for state in states:
            for unlocking in unlocking_list:
                narrowed = AbstractConstraint.intersect(state, unlocking, writer.held_facts)
                if not AbstractConstraint.is_empty(narrowed) and narrowed not in next_states:
                    next_states.append(narrowed)
        if not next_states:
            return []
        states = next_states[:STATES_KEPT]
    return states


def why_none(branch: dict, base_context, tree, writer) -> str:
    """Why unlock_branch wrote no candidate for a branch, for the record."""
    chain = BranchTree.super_chain_of_branch(tree, branch["test"], branch["first"])
    if chain is None:
        why = f"no branch point of {tree.function_name} tests on line {branch['test']}"
        return why
    part_count = len(base_context.holders)
    read = 0
    unread = []
    for step_test, step_way in chain:
        if step_test is None or not isinstance(step_way, bool):
            continue
        for leaf in leaves_of(step_test):
            if leaf_reading(leaf) is None:
                unread.append(leaf.get("text") or "")
            else:
                read += 1
    states = 0
    for bound in bound_chains(chain, part_count):
        states += len(states_after(bound, base_context, writer, part_count))
    if states == 0:
        why = f"no program takes every way of its chain of {len(chain)} ({read} operands read)"
        return why
    if read == 0:
        why = f"its chain of {len(chain)} reads nothing the tables know: {unread[:3]}"
        return why
    why = f"the base is already what its chain of {len(chain)} needs ({read} operands read; not read: {unread[:3]})"
    return why


def chain_shown(chain) -> list:
    """The chain as the record shows it: `line: way` for each step."""
    shown = []
    for step_test, step_way in chain or []:
        line = None
        if step_test is not None:
            lines = leaf_lines(step_test)
            if lines:
                line = lines[0]
        shown.append(f"{line}: {step_way}")
    return shown


def constraint_shown(constraint: AbstractConstraint, held_facts: dict) -> dict:
    """A constraint as the record shows it: each part's sets (all holders
    said as "every"), the options, the targets."""
    every = all_holders(held_facts)
    parts = []
    for part in constraint.parts:
        holders = "every"
        if part.holders != every:
            holders = sorted(part.holders)
            if len(holders) > 12:
                holders = holders[:12] + [f"... {len(part.holders)} in all"]
        parts.append({"holders": holders, "places": [p for p in PLACES if p in part.places],
                      "value_forms": [f for f in VALUE_FORMS if f in part.value_forms]})
    shown = {"parts": parts, "options": sorted(constraint.options), "targets": [t for t in TARGETS if t in
                                                                              constraint.targets]}
    return shown


# trim_paths: the paths of a function that some program can take
#
# The depths of §2 again, each path carrying the alternatives under which a
# program takes it, each a constraint and the parts its receivers are bound
# to: a flow is {frozenset of (constraint, binding): depth -> paths}.

def state_joined(first: dict, second: dict) -> dict:
    found = dict(first)
    for state, dist in second.items():
        found[state] = joined(found.get(state, {}), dist)
    return found


def state_shifted(live: dict, steps: int) -> dict:
    found = {}
    for state, dist in live.items():
        found[state] = shifted(dist, steps)
    return found


def state_flow(live: dict) -> dict:
    flow = {"live": live, "ended": {}, "broke": {}, "continued": {}}
    return flow


def state_kept(flow: dict, inner: dict, live: dict) -> dict:
    stepped = {"live": live}
    for channel in ("ended", "broke", "continued"):
        stepped[channel] = state_joined(flow[channel], inner[channel])
    return stepped


def state_merged(first: dict, second: dict) -> dict:
    flow = {}
    for channel in ("live", "ended", "broke", "continued"):
        flow[channel] = state_joined(first[channel], second[channel])
    return flow


def trimmed_through(items: list, live: dict, held_facts: dict) -> dict:
    flow = state_flow(live)
    for item in items:
        if not flow["live"]:
            break
        flow = trimmed_step(item, flow, held_facts)
    return flow


def trimmed_step(item: dict, flow: dict, held_facts: dict) -> dict:
    """step() of §2, each way's paths narrowed by the way's test."""
    if CACHE.get("deadline") and time.time() > CACHE["deadline"]:
        raise TimeoutError("over its time")
    kind = item["kind"]
    if kind in EXITS:
        channel = {"break": "broke", "continue": "continued"}.get(kind, "ended")
        stepped = dict(flow)
        stepped[channel] = state_joined(flow[channel], flow["live"])
        stepped["live"] = {}
        return stepped
    if kind in ("if",) + EXPRESSION_KINDS:
        to_true, to_false = tested_states(item["test"], flow["live"], held_facts)
        both = state_merged(trimmed_through(item["then"], to_true, held_facts),
                            trimmed_through(item["else"], to_false, held_facts))
        stepped = state_kept(flow, both, both["live"])
        return stepped
    if kind == "if constexpr":
        both = state_merged(trimmed_through(item["then"], flow["live"], held_facts),
                            trimmed_through(item["else"], flow["live"], held_facts))
        stepped = state_kept(flow, both, both["live"])
        return stepped
    if kind == "switch":
        stepped = trimmed_switch(item, flow, held_facts)
        return stepped
    if kind in LOOPS or kind == "do":
        stepped = trimmed_loop(item, flow, held_facts)
        return stepped
    if kind == "test of a switch":
        to_true, to_false = tested_states(item["test"], flow["live"], held_facts)
        stepped = dict(flow)
        stepped["live"] = state_joined(to_true, to_false)
        return stepped
    return flow


def trimmed_switch(item: dict, flow: dict, held_facts: dict) -> dict:
    entry = state_shifted(flow["live"], 1)
    running = {}
    inner = state_flow({})
    for case in item["cases"]:
        running = state_joined(running, entry)
        case_flow = trimmed_through(case["body"], running, held_facts)
        running = case_flow["live"]
        inner = {"live": {}, "ended": state_joined(inner["ended"], case_flow["ended"]),
                 "broke": state_joined(inner["broke"], case_flow["broke"]),
                 "continued": state_joined(inner["continued"], case_flow["continued"])}
    live = state_joined(running, inner["broke"])
    if not item["default"]:
        live = state_joined(live, entry)
    passed = {"live": {}, "ended": inner["ended"], "broke": {}, "continued": inner["continued"]}
    stepped = state_kept(flow, passed, live)
    return stepped


def trimmed_loop(item: dict, flow: dict, held_facts: dict) -> dict:
    if item["kind"] == "do":
        body = trimmed_through(item["body"], flow["live"], held_facts)
        after = state_joined(body["live"], body["continued"])
        to_true, to_false = tested_states(item["test"], after, held_facts)
        live = state_joined(state_joined(to_true, to_false), body["broke"])
        passed = {"live": {}, "ended": body["ended"], "broke": {}, "continued": {}}
        stepped = state_kept(flow, passed, live)
        return stepped
    to_true, to_false = flow["live"], {}
    if item["test"] is not None:
        to_true, to_false = tested_states(item["test"], flow["live"], held_facts)
    body = trimmed_through(item["body"], to_true, held_facts)
    after = state_joined(body["live"], body["continued"])
    after = trimmed_through(item["update"], after, held_facts)["live"]
    live = state_joined(state_joined(to_false, after), body["broke"])
    passed = {"live": {}, "ended": body["ended"], "broke": {}, "continued": {}}
    stepped = state_kept(flow, passed, live)
    return stepped


def tested_states(test: dict, live: dict, held_facts: dict) -> tuple:
    """(the paths that find the test true, those that find it false), each
    narrowed by what that way needs; each operand a branch point (reading A)."""
    op = test["op"]
    if op == "!":
        to_true, to_false = tested_states(test["of"], live, held_facts)
        found = (to_false, to_true)
        return found
    if op == "&&":
        left_true, left_false = tested_states(test["left"], live, held_facts)
        right_true, right_false = tested_states(test["right"], left_true, held_facts)
        found = (right_true, state_joined(left_false, right_false))
        return found
    if op == "||":
        left_true, left_false = tested_states(test["left"], live, held_facts)
        right_true, right_false = tested_states(test["right"], left_false, held_facts)
        found = (state_joined(left_true, right_true), right_false)
        return found
    if op == "?:":
        chosen_true, chosen_false = tested_states(test["test"], live, held_facts)
        then_true, then_false = tested_states(test["then"], chosen_true, held_facts)
        else_true, else_false = tested_states(test["else"], chosen_false, held_facts)
        found = (state_joined(then_true, else_true), state_joined(then_false, else_false))
        return found
    live = trimmed_through(test.get("inner", []), live, held_facts)["live"]
    to_true = {}
    to_false = {}
    for alternatives, dist in live.items():
        moved = shifted(dist, 1)
        for want, out in ((True, to_true), (False, to_false)):
            narrowed = set()
            for constraint, binding in alternatives:
                for state in leaf_states(test, want, constraint, binding, held_facts):
                    narrowed.add(state)
            if not narrowed:
                continue
            kept = alternatives_kept(narrowed)
            out[kept] = joined(out.get(kept, {}), moved)
    found = (capped(to_true), capped(to_false))
    return found


def alternatives_kept(narrowed: set) -> frozenset:
    """A path's alternatives, past ALTERNATIVES_KEPT made one, the open one
    (the path kept, what it needs forgotten)."""
    if len(narrowed) <= ALTERNATIVES_KEPT:
        return frozenset(narrowed)
    CACHE["capped"] += 1
    part_count = len(next(iter(narrowed))[0].parts)
    opened = frozenset([(open_constraint(part_count, CACHE["open_facts"]), frozenset())])
    return opened


def leaf_states(test: dict, want: bool, constraint, binding: frozenset, held_facts: dict) -> list:
    """The (constraint, binding) pairs a path goes on with after one operand
    comes out `want`; a receiver no name places is bound to one part the
    first time the path reads it."""
    part_count = len(constraint.parts)
    if leaf_reading_cached(test) is None:
        return [(constraint, binding)]
    root = unbound_root(test, part_count)
    tries = [(None, binding)]
    if root:
        bound = dict(binding).get(root)
        if bound is not None:
            tries = [(bound, binding)]
        else:
            tries = []
            for part in range(part_count):
                tries.append((part, binding | {(root, part)}))
    found = []
    for part, new_binding in tries:
        for unlocking in leaf_unlocking_cached(test, want, part_count, part, held_facts):
            narrowed = AbstractConstraint.intersect(constraint, unlocking, held_facts)
            if not AbstractConstraint.is_empty(narrowed):
                found.append((narrowed, new_binding))
    return found


def leaf_reading_cached(test: dict):
    key = ("reading", id(test))
    if key not in CACHE["leaves"]:
        CACHE["leaves"][key] = (test, leaf_reading(test))
    return CACHE["leaves"][key][1]


def leaf_unlocking_cached(test: dict, want: bool, part_count: int, part, held_facts: dict) -> list:
    key = ("unlocking", id(test), want, part_count, part)
    if key not in CACHE["leaves"]:
        leaf = test
        if part is not None:
            leaf = dict(test)
            leaf["bound"] = part
        CACHE["leaves"][key] = (test, leaf_unlocking(leaf, want, part_count, held_facts))
    return CACHE["leaves"][key][1]


def capped(live: dict) -> dict:
    """Past TRIM_STATES_KEPT sets of alternatives at one point, one: the
    open one, every path kept (the function counted as capped)."""
    if len(live) <= TRIM_STATES_KEPT:
        return live
    CACHE["capped"] += 1
    merged = {}
    part_count = 0
    for alternatives, dist in live.items():
        part_count = len(next(iter(alternatives))[0].parts)
        merged = joined(merged, dist)
    opened = frozenset([(open_constraint(part_count, CACHE["open_facts"]), frozenset())])
    found = {opened: merged}
    return found


def parts_read_in(tree: BranchTree) -> int:
    """How many parts a function's tests read: one past the highest
    `getArg(N)`, at least 2."""
    found = 2
    for line in re.findall(r"getArg\((\d+)\)", json.dumps(tree.items)):
        found = max(found, int(line) + 1)
    return found


def trimmed_summary(tree: BranchTree, held_facts: dict, seconds: float = 0) -> dict:
    """trim_paths on one function from the open constraint of the parts its
    tests read: its paths and deepest path, beside §2's reading A; a
    TimeoutError past `seconds` (0: no bound)."""
    CACHE["open_facts"] = held_facts
    CACHE["capped"] = 0
    CACHE["deadline"] = time.time() + seconds if seconds else 0
    part_count = parts_read_in(tree)
    started = time.time()
    surviving = BranchTree.trim_paths(tree, open_constraint(part_count, held_facts), held_facts)
    dist = {}
    constraints = set()
    for depth, alternatives, paths in surviving:
        dist[depth] = dist.get(depth, 0) + paths
        for constraint in alternatives:
            constraints.add(constraint)
    summary = summary_of(dist)
    summary["parts"] = part_count
    summary["constraints"] = len(constraints)
    summary["capped"] = CACHE["capped"]
    summary["seconds"] = round(time.time() - started, 2)
    untrimmed = summary_of(depths_of(tree.items, "A"))
    summary["untrimmed"] = {"deepest": untrimmed["deepest"], "paths": untrimmed["paths"]}
    return summary


# ---------------------------------------------------------------------------
# 5. the checks of PCHQ log 503 §3, line 1, and the count before the run

# run tlp1_l10's five branches the candidates traced did not take (log 501,
# Table 7), each with the record of the operators it was tried for
FIVE = ("CodeGenFunction::EmitStoreThroughLValue:2510->2527",
        "CodeGenFunction::EmitBitfieldConversionCheck:1400->1401",
        "CodeGenFunction::EmitStoreThroughExtVectorComponentLValue:2698->2701",
        "CodeGenFunction::EmitStoreThroughGlobalRegLValue:2776->2777",
        "CodeGenFunction::EmitStoreThroughGlobalRegLValue:2782->2783")
FIVE_RECORDS = ("tlp1_l10_traced_part_1_of_3", "tlp1_l10_traced_part_2_of_3", "tlp1_l10_traced_part_3_of_3")
# log 503 §3: the four functions trimmed and set beside log 502's Table 2
FOUR = ("StartFunction", "EmitSub", "BuildAtomicExpr", "CheckCompareOperands")
# the whole trimming pass: its bound, and each function's; each of the four's
TRIM_BOUND = 1200
TRIM_EACH = 60
FOUR_EACH = 300


def unlock_step(out: str) -> None:
    """The writer (the holder facts asked of clang once, FACTS_FILE); the
    five branches unlocked from run tlp1_l10's bases; the four functions
    trimmed; every function on the traced paths trimmed, within TRIM_BOUND."""
    trees = TREES
    loop = loop_module()
    writer = writer_of(loop.pool_of(loop.HOLDERS_FILE))
    usable = 0
    for held in writer.held_facts.values():
        if held is not None:
            usable += 1
    say(f"[unlock] the writer: {len(writer.pool)} holders written, facts for {usable} of {len(writer.held_facts)} "
        f"spellings, {len(all_holders(writer.held_facts))} holders a part may be")
    five = five_unlocked(trees, writer)
    write_json(five, os.path.join(out, "unlock_five.json"))
    four = four_trimmed(trees, writer.held_facts)
    write_json(four, os.path.join(out, "trimmed_four.json"))
    every = every_trimmed(trees, writer.held_facts)
    write_json(every, os.path.join(out, "trimmed_on_paths.json"))


def five_unlocked(trees: str, writer: CandidateWriter) -> list:
    """Each of the five, for each operator run tlp1_l10 tried it for: its
    chain, the states left for each binding, and the candidates written."""
    loop = loop_module()
    found = []
    for folder in FIVE_RECORDS:
        record = read_json(os.path.join(HERE, folder, "branch_candidates.json"))
        for key, entry in record["operators"].items():
            for name in FIVE:
                branch = entry["branches"].get(name)
                if branch is None:
                    continue
                try:
                    base = base_of_record(key, branch)
                    found.append(one_unlocked(key, name, branch, base, trees, writer))
                except Exception as error:
                    found.append({"operator": key, "branch": name, "error": error_text(error)})
                    say(f"[unlock] {key} {name}: {error_text(error)}")
    return found


def base_of_record(key: str, branch: dict):
    """The context that ran a branch's test, as its record names it
    (`ran_by`: a run's lines.json and the path's number there)."""
    from context import Context, Setup
    loop = loop_module()
    operator = loop.operator_of(key)
    for ran in branch.get("ran_by", []):
        record = read_json(os.path.join(HERE, ran["run"], "lines.json"))
        for path in record["operators"].get(key, {}).get("paths", []):
            if path["path"] == ran["path"] and "holders" in path:
                setup = Setup(path["setup"], tuple(path.get("preamble", ())))
                context = Context(operator, tuple(path["holders"]), setup, path.get("program", ""))
                return context
    return None


def one_unlocked(key: str, name: str, branch: dict, base, trees: str, writer: CandidateWriter) -> dict:
    shown = {"operator": key, "branch": name, "condition": branch.get("condition"), "outcome_l10": branch.get("outcome"),
             "base": None, "function": None, "chain": None, "states": [], "candidates": [], "why_none": ""}
    if base is None:
        shown["why_none"] = "no context of the record ran its test"
        say_unlocked(shown)
        return shown
    shown["base"] = {"holders": list(base.holders), "setup": base.setup.command, "own_lines": own_program_lines(base),
                     "read": base_reading(base)["parts"]}
    tree = tree_of_branch(branch, trees)
    if tree is None:
        shown["why_none"] = "no tree holds its function"
        say_unlocked(shown)
        return shown
    shown["function"] = [tree.function_name, tree.first_line, tree.last_line]
    chain = BranchTree.super_chain_of_branch(tree, branch["test"], branch["first"])
    shown["chain"] = chain_steps_shown(chain)
    part_count = len(base.holders)
    if chain is not None:
        for bound in bound_chains(chain, part_count):
            binding = bound_parts(bound)
            for state in states_after(bound, base, writer, part_count):
                shown["states"].append({"binding": binding, "constraint": constraint_shown(state, writer.held_facts)})
    for candidate in unlock_branch(branch, base, tree, writer):
        shown["candidates"].append({"holders": list(candidate.holders), "setup": candidate.setup.command,
                                    "preamble": list(candidate.setup.preamble),
                                    "own_lines": own_program_lines(candidate)})
    if not shown["candidates"]:
        shown["why_none"] = why_none(branch, base, tree, writer)
    say_unlocked(shown)
    return shown


def chain_steps_shown(chain) -> list:
    """Each step: the line of its test, the test's text (its operands'
    texts joined as written), the way."""
    if chain is None:
        return None
    shown = []
    for step_test, step_way in chain:
        texts = []
        line = None
        if step_test is not None:
            for leaf in leaves_of(step_test):
                texts.append(leaf.get("text") or "")
                if line is None:
                    line = leaf["line"]
        shown.append({"line": line, "test": " | ".join(texts), "op": (step_test or {}).get("op"), "way": step_way})
    return shown


def bound_parts(chain: list) -> dict:
    found = {}
    for step_test, step_way in chain:
        if step_test is None or not isinstance(step_way, bool):
            continue
        for leaf in leaves_of(step_test):
            if "bound" in leaf:
                found[leaf.get("text") or ""] = leaf["bound"]
    return found


def own_program_lines(context) -> list:
    """A context's own lines: what it declares, its P_k and its op_k."""
    own = []
    for line in (context.program or "").split("\n"):
        if line.startswith(("struct P_", "void op_", "register ", "typedef int m2")):
            own.append(line)
    return own


def say_unlocked(shown: dict) -> None:
    say(f"[unlock] {shown['operator']} {shown['branch']}: {shown['condition']}")
    if shown["base"] is not None:
        say(f"[unlock]   base {shown['base']['holders']} read as {shown['base']['read']}")
    for step in shown["chain"] or []:
        say(f"[unlock]   chain: {step['line']}: {step['test']} -> {step['way']}")
    say(f"[unlock]   {len(shown['states'])} states; {len(shown['candidates'])} candidates {shown['why_none']}")
    for candidate in shown["candidates"]:
        say(f"[unlock]     {candidate['holders']} {candidate['setup'].split(' -c', 1)[-1]} {candidate['own_lines']}")


def functions_named(trees: str, short: str) -> list:
    """Every tree of the trees step whose name ends with `short`."""
    found = []
    for relative in tree_files(trees):
        for tree in trees_in(trees, relative):
            if short_name(tree.function_name) == short:
                found.append((relative, tree))
    return found


def tree_files(trees: str) -> list:
    found = []
    for folder, sub_folders, files in os.walk(trees):
        for file in files:
            if file.endswith(".json"):
                found.append(os.path.relpath(os.path.join(folder, file), trees)[:-len(".json")])
    found.sort()
    return found


def error_text(error) -> str:
    import traceback
    lines = traceback.format_exception(type(error), error, error.__traceback__)
    text = (lines[-1].strip() + " at " + " | ".join(line.strip().split("\n")[0] for line in lines[-4:-1]))[:600]
    return text


def four_trimmed(trees: str, held_facts: dict) -> list:
    found = []
    for short in FOUR:
        for relative, tree in functions_named(trees, short):
            try:
                summary = trimmed_summary(tree, held_facts, FOUR_EACH)
            except TimeoutError:
                found.append({"function": tree.function_name, "file": relative, "first": tree.first_line,
                              "summary": None, "over": FOUR_EACH})
                say(f"[trim] {tree.function_name} ({relative} {tree.first_line}): over {FOUR_EACH} s")
                continue
            row = {"function": tree.function_name, "file": relative, "first": tree.first_line, "summary": summary}
            found.append(row)
            say(f"[trim] {tree.function_name} ({relative} {tree.first_line}): untrimmed {summary['untrimmed']['paths']} "
                f"paths, deepest {summary['untrimmed']['deepest']}; trimmed {summary['paths']} paths, deepest "
                f"{summary['deepest']}; {summary['constraints']} constraints, parts {summary['parts']}, capped "
                f"{summary['capped']} times, {summary['seconds']} s")
    return found


def every_trimmed(trees: str, held_facts: dict) -> dict:
    """trimmed_summary of every function the lines records name (on_paths),
    each within TRIM_EACH seconds, all within TRIM_BOUND."""
    started = time.time()
    rows = []
    over = []
    for relative in tree_files(trees):
        for function in read_json(os.path.join(trees, relative + ".json"))["functions"]:
            if not function.get("on_paths"):
                continue
            if time.time() - started > TRIM_BOUND:
                over.append(function["name"])
                continue
            try:
                summary = trimmed_summary(tree_of(function), held_facts, TRIM_EACH)
                rows.append({"function": function["name"], "file": relative, "first": function["first"],
                             "summary": summary})
            except TimeoutError:
                over.append(function["name"])
            say_now_and_then(f"[trim] {len(rows)} functions trimmed, {len(over)} over their time")
    say(f"[trim] {len(rows)} functions on the paths trimmed, {len(over)} over their time or the bound, "
        f"{time.time() - started:.0f} s")
    found = {"rows": rows, "over": over, "each": TRIM_EACH, "bound": TRIM_BOUND}
    return found


def dry_step(out: str) -> None:
    """Every branch the page reads as not reached (PCHQ log 500's classes:
    the condition not read yet, or the candidates traced did not take it),
    unlocked for one operator it is untaken for, from the context that ran
    its test, without tracing: how many get a candidate no context of the
    operator traced before; and the operators that hold them all, chosen
    greedily (as run tlp1_l10 chose), written to OUT/keys.txt."""
    page, keyed, gnu_c = gnu_c_reading()
    problems = page.problems_page()
    records = page.read_loop_records()
    newest = problems.newest_per_operator(records)
    sides = problems.open_sides(newest)
    sorting = problems.sorted_sides(sides, gnu_c)
    del records
    wanted = {}
    for side_id, sort in sorting.items():
        if sort["state"] in (problems.TOOK_NONE, problems.NOT_READ):
            wanted[side_id] = sort["state"]
    say(f"[dry] {len(newest)} operators; {len(wanted)} branches not reached: "
        f"{sum(1 for s in wanted.values() if s == problems.TOOK_NONE)} the candidates traced did not take, "
        f"{sum(1 for s in wanted.values() if s == problems.NOT_READ)} not read")
    loop = loop_module()
    keys = []
    for side_id in wanted:
        key = operator_for_side(sides[side_id])
        if key and key not in keys:
            keys.append(key)
    everywhere = {}
    lines = loop.lines_of(sorted(keys), loop.lines_records(), everywhere)
    writer = writer_of(loop.pool_of(loop.HOLDERS_FILE))
    trees = TREES
    rows = []
    started = time.time()
    errors = 0
    for number, side_id in enumerate(sorted(wanted)):
        try:
            rows.append(dry_row(side_id, wanted[side_id], sides[side_id], lines, trees, writer))
        except Exception as error:
            errors += 1
            rows.append({"branch": side_id, "state": wanted[side_id], "tree": False, "written": 0, "new": 0,
                         "why_none": "", "error": error_text(error)})
            if errors <= 5:
                say(f"[dry] {side_id}: {error_text(error)}")
        say_now_and_then(f"[dry] {number + 1} of {len(wanted)} branches, {time.time() - started:.0f} s")
    chosen = operators_covering(rows, sides)
    dry = {"branches": rows, "operators": chosen, "counts": dry_counts(rows)}
    write_json(dry, os.path.join(out, "dry.json"))
    with open(os.path.join(out, "keys.txt"), "w", encoding="utf-8") as written:
        written.write("# tlp1_l13: the operators that hold every not-reached branch a new candidate unlocks\n")
        for key in chosen:
            written.write(key + "\n")
    say(f"[dry] {dry['counts']}; {len(chosen)} operators to run")


def operator_for_side(entry: dict) -> str:
    """The operator a branch is unlocked for: the one its record is of, else
    the first it is untaken for."""
    key = entry["side"].get("operator") or ""
    if key in entry["operators"]:
        return key
    if entry["operators"]:
        return entry["operators"][0]
    return key


def dry_row(side_id: str, state: str, entry: dict, lines: dict, trees: str, writer: CandidateWriter) -> dict:
    loop = loop_module()
    side = entry["side"]
    key = operator_for_side(entry)
    row = {"branch": side_id, "state": state, "operator": key, "function": side.get("function"),
           "condition": str(side.get("condition"))[:200], "tree": False, "chain": None, "written": 0, "new": 0,
           "why_none": ""}
    paths = lines.get(key, [])
    base = None
    for ran in side.get("ran_by", []):
        # a record of run tlp1_l02's time names the context itself, not its run and path
        if "run" not in ran:
            continue
        for path in paths:
            if path["run"] == ran["run"] and path["path"] == ran["path"] and path["context"] is not None:
                base = path["context"]
                break
        if base is not None:
            break
    if base is None:
        base = loop.first_accepted(paths)
    if base is None:
        row["why_none"] = "no context of the operator to start from"
        return row
    tree = tree_of_branch(side, trees)
    if tree is None:
        row["why_none"] = "no tree holds its function"
        return row
    row["tree"] = True
    chain = BranchTree.super_chain_of_branch(tree, side["test"], side["first"])
    row["chain"] = chain_shown(chain)
    known = set()
    for path in paths:
        if path["context"] is not None:
            known.add(loop.check.key_of(path["context"]))
    written = unlock_branch(side, base, tree, writer)
    row["written"] = len(written)
    new = []
    for candidate in written:
        if loop.check.key_of(candidate) not in known:
            new.append(candidate)
    row["new"] = len(new)
    row["examples"] = []
    for candidate in new[:3]:
        row["examples"].append({"holders": list(candidate.holders), "setup": candidate.setup.command.split(" -c", 1)[-1],
                                "own_lines": own_program_lines(candidate)})
    if not new:
        row["why_none"] = why_none(side, base, tree, writer) if not written else "every candidate written was traced before"
    return row


def operators_covering(rows: list, sides: dict) -> list:
    """The fewest operators (greedily) that hold every branch with a new
    candidate: the one holding most of those left, first."""
    by_key = {}
    left = set()
    for row in rows:
        if row["new"] == 0:
            continue
        left.add(row["branch"])
        for key in sides[row["branch"]]["operators"]:
            by_key.setdefault(key, set()).add(row["branch"])
    chosen = []
    while left:
        best = None
        for key, held in by_key.items():
            if key in chosen:
                continue
            gain = len(held & left)
            if gain and (best is None or (gain, key) > best[0]):
                best = ((gain, key), key)
        if best is None:
            break
        chosen.append(best[1])
        left -= by_key[best[1]]
    return chosen


def dry_counts(rows: list) -> dict:
    counts = {"branches": len(rows), "with_a_tree": 0, "written": 0, "with_a_new_candidate": 0, "new_candidates": 0,
              "by_state": {}}
    for row in rows:
        state = counts["by_state"].setdefault(row["state"], {"branches": 0, "with_a_new_candidate": 0})
        state["branches"] += 1
        if row["tree"]:
            counts["with_a_tree"] += 1
        if row["written"]:
            counts["written"] += 1
        if row["new"]:
            counts["with_a_new_candidate"] += 1
            counts["new_candidates"] += row["new"]
            state["with_a_new_candidate"] += 1
    return counts


# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("files", "trees", "traced", "unlock", "dry"):
        print(__doc__)
        return 2
    step_name = sys.argv[1]
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if step_name == "files":
        files_step(out)
    if step_name == "trees":
        trees_step(out)
    if step_name == "traced":
        traced_step(out)
    if step_name == "unlock":
        unlock_step(out)
    if step_name == "dry":
        dry_step(out)
    return 0


def run_with_room() -> int:
    """main() in a thread with a deep stack: a long `else if` chain is read
    by recursion. Path counts can run to thousands of digits, written whole."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    sys.setrecursionlimit(200000)
    threading.stack_size(512 * 1024 * 1024)
    result = {}
    thread = threading.Thread(target=lambda: result.setdefault("code", main()))
    thread.start()
    thread.join()
    code = result.get("code", 1)
    return code


if __name__ == "__main__":
    sys.exit(run_with_room())
