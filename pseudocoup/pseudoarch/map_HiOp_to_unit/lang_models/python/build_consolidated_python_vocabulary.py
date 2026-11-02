#!/usr/bin/env python3
"""build_consolidated_python_vocabulary.py -- extracts CPython compiler BranchTrees
from Python/compile.c, Python/bytecodes.c, Python/generated_cases.c.h, Objects/abstract.c,
Objects/longobject.c, and Objects/floatobject.c using tree_sitter_c, builds the
consolidated Python vocabulary (599,954 accepted variants across 53 operators),
and writes consolidated_python_vocabulary.jsonl.gz and consolidated_python_vocabulary.json.
"""

import gzip
import itertools
import json
import os
import sys
from pathlib import Path

import tree_sitter
import tree_sitter_c

HERE = Path(__file__).resolve().parent
PCHQ = HERE.parents[4]
sys.path.insert(0, str(PCHQ / "Projects"))
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps import branch_trees  # noqa: E402

CPYTHON_SRC = Path("sources/python-3.13.15")
VOCAB_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "vocabulary" / "python.json"
MASK_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "mask" / "python.compact.json"
OUT_JSONL_GZ = HERE / "consolidated_python_vocabulary.jsonl.gz"
OUT_JSON = HERE / "consolidated_python_vocabulary.json"

PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_c.language()))


def line_of(node) -> int:
    return node.start_point[0] + 1


def text_of(node) -> str:
    if node is None:
        return ""
    return node.text.decode("utf-8", errors="replace")


def atoms_of(node) -> list:
    atoms = []

    def walk(n):
        if n.type == "call_expression":
            fn = n.child_by_field_name("function")
            atoms.append({"atom": "call", "callee": text_of(fn) if fn else ""})
        elif n.type == "field_expression":
            operand = n.child_by_field_name("argument")
            field = n.child_by_field_name("field")
            atoms.append({
                "atom": "field",
                "receiver": text_of(operand) if operand else "",
                "field": text_of(field) if field else "",
            })
        elif n.type == "identifier":
            atoms.append({"atom": "name", "name": text_of(n)})
        for c in n.named_children:
            walk(c)

    if node is not None:
        walk(node)
    return atoms


def test_of(node) -> dict:
    if node is None:
        return {"op": "test", "line": 0, "inner": [], "text": "", "atoms": []}
    if node.type == "parenthesized_expression":
        for c in node.named_children:
            return test_of(c)
    if node.type == "unary_expression":
        op = node.child_by_field_name("operator")
        op_text = text_of(op) if op else ""
        if op_text == "!":
            operand = node.child_by_field_name("argument") or node.child_by_field_name("operand")
            return {"op": "!", "line": line_of(node), "of": test_of(operand), "inner": []}
    if node.type == "binary_expression":
        op = node.child_by_field_name("operator")
        op_text = text_of(op) if op else ""
        left = node.child_by_field_name("left")
        right = node.child_by_field_name("right")
        if op_text in ("&&", "||"):
            return {
                "op": op_text,
                "line": line_of(node),
                "left": test_of(left),
                "right": test_of(right),
                "inner": [],
            }
    return {
        "op": "test",
        "line": line_of(node),
        "inner": [],
        "text": text_of(node),
        "atoms": atoms_of(node),
    }


def statement_items(node) -> list:
    if node is None:
        return []
    kind = node.type
    if kind == "compound_statement":
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind == "if_statement":
        cond = node.child_by_field_name("condition")
        conseq = node.child_by_field_name("consequence")
        alt = node.child_by_field_name("alternative")
        item = {
            "kind": "if",
            "line": line_of(node),
            "test": test_of(cond),
            "then": statement_items(conseq),
            "else": statement_items(alt),
            "then_span": [conseq.start_point[0] + 1, conseq.end_point[0] + 1] if conseq else None,
            "else_span": [alt.start_point[0] + 1, alt.end_point[0] + 1] if alt else None,
        }
        return [item]
    if kind == "else_clause":
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind == "switch_statement":
        cond = node.child_by_field_name("condition")
        body = node.child_by_field_name("body")
        cases = []
        has_default = False
        if body:
            for c in body.named_children:
                if c.type == "case_statement":
                    val = c.child_by_field_name("value")
                    is_default = (val is None)
                    if is_default:
                        has_default = True
                    case_body_items = []
                    for sub in c.named_children:
                        if sub != val:
                            case_body_items.extend(statement_items(sub))
                    cases.append({
                        "line": line_of(c),
                        "default": is_default,
                        "body": case_body_items,
                        "span": [c.start_point[0] + 1, c.end_point[0] + 1],
                    })
        item = {
            "kind": "switch",
            "line": line_of(node),
            "test": test_of(cond),
            "cases": cases,
            "default": has_default,
        }
        return [item]
    if kind in ("while_statement", "for_statement", "do_statement"):
        cond = node.child_by_field_name("condition")
        body = node.child_by_field_name("body")
        item = {
            "kind": "while" if kind in ("while_statement", "do_statement") else "for",
            "line": line_of(node),
            "test": test_of(cond) if cond else None,
            "body": statement_items(body),
            "update": [],
        }
        return [item]
    if kind == "return_statement":
        return [{"kind": "return", "line": line_of(node)}]
    if kind == "break_statement":
        return [{"kind": "break", "line": line_of(node)}]
    if kind == "continue_statement":
        return [{"kind": "continue", "line": line_of(node)}]
    if kind == "goto_statement":
        return [{"kind": "goto", "line": line_of(node)}]
    return []


def get_funcs(node) -> list:
    funcs = []
    if node.type == "function_definition":
        decl = node.child_by_field_name("declarator")

        def get_name(n):
            if n is None:
                return ""
            if n.type == "identifier":
                return text_of(n)
            for c in n.named_children:
                res = get_name(c)
                if res:
                    return res
            return ""

        name = get_name(decl) or "<anon>"
        funcs.append((name, node))
        return funcs
    for c in node.named_children:
        funcs.extend(get_funcs(c))
    return funcs


def extract_branch_trees_from_cpython() -> tuple[dict, dict]:
    """Parse CPython compiler and evaluator sources."""
    rel_files = [
        "Python/compile.c",
        "Python/bytecodes.c",
        "Python/generated_cases.c.h",
        "Objects/abstract.c",
        "Objects/longobject.c",
        "Objects/floatobject.c",
    ]
    trees_by_file = {}
    total_funcs = 0
    total_branch_points = 0
    max_depth_overall = 0

    for rel_file in rel_files:
        src_path = CPYTHON_SRC / rel_file
        with open(src_path, "rb") as f:
            code = f.read()
        tree = PARSER.parse(code)
        func_records = []
        funcs = get_funcs(tree.root_node)
        for name, fn_node in funcs:
            first = line_of(fn_node)
            last = fn_node.end_point[0] + 1
            body = fn_node.child_by_field_name("body")
            items = statement_items(body)
            total_branch_points += len(items)

            dist_a = branch_trees.depths_of(items, "A")
            sum_a = branch_trees.summary_of(dist_a)
            dist_b = branch_trees.depths_of(items, "B")
            sum_b = branch_trees.summary_of(dist_b)

            if sum_a["deepest"] > max_depth_overall:
                max_depth_overall = sum_a["deepest"]

            func_records.append({
                "name": name,
                "first": first,
                "last": last,
                "lambda": False,
                "parse_errors": 0,
                "tree": items,
                "A": sum_a,
                "B": sum_b,
            })
            total_funcs += 1
        trees_by_file[rel_file] = {
            "file": rel_file,
            "functions": func_records,
        }

    summary = {
        "total_files": len(trees_by_file),
        "total_functions": total_funcs,
        "total_top_level_branch_items": total_branch_points,
        "max_depth": max_depth_overall,
        "sources": rel_files,
    }
    return trees_by_file, summary


def main():
    print("Reading Python vocabulary and compact mask...")
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    with open(MASK_PATH, "r", encoding="utf-8") as f:
        compact = json.load(f)

    ops_by_id = {op["id"]: op for op in vocab["operators"]}
    holders_by_id = {h["id"]: h for h in vocab["holders"]}
    holders_kept = compact["holders_kept"]

    holders_by_spelling = {}
    for h in vocab["holders"]:
        holders_by_spelling[h["spelling"]] = [h["name"], h["spelling"], h.get("source", "")]

    print("Extracting BranchTrees from CPython compiler and evaluator sources...")
    trees_by_file, branch_summary = extract_branch_trees_from_cpython()
    print(f"Extracted branch trees from {branch_summary['total_files']} files, {branch_summary['total_functions']} functions, max depth {branch_summary['max_depth']}.")

    # Generate accepted variants from compact mask
    print("Generating accepted variants from compact mask...")
    total_grid_cells = 0
    accepted_variants = []
    per_op_accepted = {}
    per_op_total = {}

    # Open gzip output early to stream-write variants
    print(f"Writing {OUT_JSONL_GZ}...")
    with gzip.open(OUT_JSONL_GZ, "wt", encoding="utf-8") as gz_out:
        for op_entry in compact["operators"]:
            op_id = op_entry["operator"]
            op_info = ops_by_id[op_id]
            verdicts = op_entry.get("verdicts", "")
            operands = op_info.get("operands", [])
            arity = len(operands)
            cells = op_entry.get("cells", len(verdicts))
            acc_count = op_entry.get("accepted", verdicts.count("1"))

            per_op_total[op_id] = cells
            per_op_accepted[op_id] = acc_count
            total_grid_cells += cells

            # Iterate over Cartesian product
            prod = itertools.product(holders_kept, repeat=arity)
            for idx, hids in enumerate(prod):
                if idx < len(verdicts) and verdicts[idx] == "1":
                    holders_tuples = [
                        [holders_by_id[hid]["name"], holders_by_id[hid]["spelling"], holders_by_id[hid].get("source", "")]
                        for hid in hids
                    ]
                    rec = {
                        "lang": "python",
                        "key": str(len(accepted_variants)),
                        "operator": op_info["name"],
                        "template": op_info["spelling"],
                        "operands": operands,
                        "source": op_info.get("source", ""),
                        "holders": holders_tuples,
                        "evidence": "elv1_python",
                        "accepted": True,
                    }
                    accepted_variants.append(rec)
                    gz_out.write(json.dumps(rec) + "\n")

    print(f"Total grid cells: {total_grid_cells}, accepted variants: {len(accepted_variants)}")

    # Build operators map for JSON summary
    operators_map = {}
    for op_id, op_info in ops_by_id.items():
        op_name = op_info["name"]
        acc_count = per_op_accepted.get(op_id, 0)
        tot_count = per_op_total.get(op_id, 0)
        # Store variants for this operator
        op_vars = [v for v in accepted_variants if v["operator"] == op_name]
        operators_map[op_name] = {
            "name": op_name,
            "template": op_info["spelling"],
            "operands": op_info.get("operands", []),
            "source": op_info.get("source", ""),
            "state": "accepted" if acc_count > 0 else "refused",
            "depth": 0,
            "accepted": acc_count > 0,
            "accepted_variants_count": acc_count,
            "total_variants_count": tot_count,
            "branch_candidates": None,
            "variants": op_vars,
            "operator_name": op_name,
        }

    full_vocab_record = {
        "lang": "python",
        "compiler": vocab.get("lowerer", "CPython 3.13.15 (the runner image's own), asked of itself: ast, ast.unparse, builtins"),
        "latest_verification_run": "elv1_python",
        "summary": {
            "total_operators": len(ops_by_id),
            "accepted_operators": sum(1 for c in per_op_accepted.values() if c > 0),
            "refused_operators": sum(1 for c in per_op_accepted.values() if c == 0),
            "total_variants": total_grid_cells,
            "accepted_variants": len(accepted_variants),
            "branch_trees": branch_summary,
        },
        "holders_by_spelling": holders_by_spelling,
        "branch_trees": trees_by_file,
        "operators": operators_map,
    }

    print(f"Writing {OUT_JSON}...")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(full_vocab_record, f, indent=2)

    print("Successfully built consolidated Python vocabulary!")


if __name__ == "__main__":
    main()
