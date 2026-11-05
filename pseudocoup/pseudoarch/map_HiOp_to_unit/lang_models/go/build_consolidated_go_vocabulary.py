#!/usr/bin/env python3
"""build_consolidated_go_vocabulary.py -- extracts Go compiler BranchTrees from
cmd/compile/internal/ssagen, walk, and typecheck using tree_sitter_go, builds
the consolidated Go vocabulary (1,654 accepted variants across 41 operators),
and writes consolidated_go_vocabulary.jsonl.gz and consolidated_go_vocabulary.json.
"""

import glob
import gzip
import json
import os
import sys
from pathlib import Path

import tree_sitter
import tree_sitter_go

HERE = Path(__file__).resolve().parent
PCHQ = HERE.parents[4]
sys.path.insert(0, str(PCHQ / "Projects"))
from PseudoIR.map_HiOp_to_unit.model_lang_parts.HiOps import branch_trees  # noqa: E402

GO_SRC = Path("/usr/lib/go-1.26/src/cmd/compile/internal")
VOCAB_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "vocabulary" / "go.json"
MASK_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "mask" / "go.jsonl"
OUT_JSONL_GZ = HERE / "consolidated_go_vocabulary.jsonl.gz"
OUT_JSON = HERE / "consolidated_go_vocabulary.json"

PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_go.language()))


def line_of(node) -> int:
    return node.start_point[0] + 1


def text_of(node) -> str:
    return node.text.decode("utf-8", errors="replace")


def atoms_of(node) -> list:
    atoms = []

    def walk(n):
        if n.type == "call_expression":
            fn = n.child_by_field_name("function")
            atoms.append({"atom": "call", "callee": text_of(fn) if fn else ""})
        elif n.type == "selector_expression":
            operand = n.child_by_field_name("operand")
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

    walk(node)
    return atoms


def test_of(node) -> dict:
    if node is None:
        return {"op": "test", "line": 0, "inner": [], "text": "", "atoms": []}
    kind = node.type
    if kind == "unary_expression":
        op = node.child_by_field_name("operator")
        op_text = text_of(op) if op else ""
        if op_text == "!":
            operand = node.child_by_field_name("operand")
            return {"op": "!", "line": line_of(node), "of": test_of(operand)}
    if kind == "binary_expression":
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
    if kind in ("block", "statement_list"):
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
        init = node.child_by_field_name("initializer")
        before = statement_items(init) if init else []
        return before + [item]
    if kind in ("expression_switch_statement", "type_switch_statement"):
        val = node.child_by_field_name("value")
        init = node.child_by_field_name("initializer")
        before = statement_items(init) if init else []
        cases = []
        has_default = False
        for c in node.named_children:
            if "case" in c.type:
                is_default = c.type == "default_case"
                if is_default:
                    has_default = True
                cases.append({
                    "line": line_of(c),
                    "default": is_default,
                    "body": statement_items(c),
                    "span": [c.start_point[0] + 1, c.end_point[0] + 1],
                })
        item = {
            "kind": "switch",
            "line": line_of(node),
            "test": test_of(val),
            "cases": cases,
            "default": has_default,
        }
        return before + [item]
    if kind == "select_statement":
        cases = []
        has_default = False
        for c in node.named_children:
            if "case" in c.type:
                is_default = c.type == "default_case"
                if is_default:
                    has_default = True
                cases.append({
                    "line": line_of(c),
                    "default": is_default,
                    "body": statement_items(c),
                    "span": [c.start_point[0] + 1, c.end_point[0] + 1],
                })
        item = {
            "kind": "switch",
            "line": line_of(node),
            "test": {"op": "test", "line": line_of(node), "inner": [], "text": "select", "atoms": []},
            "cases": cases,
            "default": has_default,
        }
        return [item]
    if kind in ("expression_case", "type_case", "default_case", "communication_case"):
        items = []
        for c in node.named_children:
            if c.type not in ("expression_list", "type_identifier", "receive_statement"):
                items.extend(statement_items(c))
        return items
    if kind == "for_statement":
        body = node.child_by_field_name("body")
        cond = None
        for c in node.named_children:
            if c.type == "for_clause":
                cond = c.child_by_field_name("condition")
            elif c.type == "binary_expression":
                cond = c
        item = {
            "kind": "for",
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
    if kind == "expression_statement":
        text = text_of(node).strip()
        if text.startswith("panic("):
            return [{"kind": "throw", "line": line_of(node)}]
    return []


def function_name_of(node) -> str:
    name_node = node.child_by_field_name("name")
    func_name = text_of(name_node) if name_node else "<unnamed>"
    recv_node = node.child_by_field_name("receiver")
    if recv_node:
        recv_text = text_of(recv_node).strip()
        func_name = f"({recv_text}).{func_name}"
    return func_name


def extract_branch_trees_from_packages() -> tuple[dict, dict]:
    """Parse all .go files across ssagen, walk, and typecheck into BranchTree records."""
    packages = ["ssagen", "walk", "typecheck"]
    trees_by_file = {}
    total_funcs = 0
    total_branch_points = 0
    max_depth_overall = 0

    for pkg in packages:
        pkg_dir = GO_SRC / pkg
        for file_path in sorted(pkg_dir.glob("*.go")):
            if file_path.name.endswith("_test.go"):
                continue
            with open(file_path, "rb") as f:
                code = f.read()
            tree = PARSER.parse(code)
            rel_file = f"cmd/compile/internal/{pkg}/{file_path.name}"
            func_records = []
            for node in tree.root_node.named_children:
                if node.type not in ("function_declaration", "method_declaration"):
                    continue
                name = function_name_of(node)
                first = line_of(node)
                last = node.end_point[0] + 1
                body = node.child_by_field_name("body")
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
        "packages": [f"cmd/compile/internal/{p}" for p in packages],
    }
    return trees_by_file, summary


def main():
    print("Reading Go vocabulary and verdicts...")
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    ops_by_id = {op["id"]: op for op in vocab["operators"]}
    holders_by_id = {h["id"]: h for h in vocab["holders"]}

    holders_by_spelling = {}
    for h in vocab["holders"]:
        holders_by_spelling[h["spelling"]] = [h["name"], h["spelling"], h.get("source", "")]

    print("Extracting BranchTrees from Go compiler sources...")
    trees_by_file, branch_summary = extract_branch_trees_from_packages()
    print(f"Extracted branch trees from {branch_summary['total_files']} files, {branch_summary['total_functions']} functions.")

    # Read accepted variants from mask/go.jsonl
    print("Reading accepted variants from mask/go.jsonl...")
    accepted_variants = []
    per_op_accepted = {}
    per_op_total = {}
    total_grid_cells = 0

    with open(MASK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            total_grid_cells += 1
            d = json.loads(line)
            op_id = d["operator"]
            per_op_total[op_id] = per_op_total.get(op_id, 0) + 1
            if not d.get("accepted"):
                continue
            per_op_accepted[op_id] = per_op_accepted.get(op_id, 0) + 1

            op_info = ops_by_id[op_id]
            hids = d["holders"]
            holders_tuples = [
                [holders_by_id[hid]["name"], holders_by_id[hid]["spelling"], holders_by_id[hid].get("source", "")]
                for hid in hids
            ]
            key = str(len(accepted_variants))
            rec = {
                "lang": "go",
                "key": key,
                "operator": op_info["name"],
                "template": op_info["spelling"],
                "operands": op_info.get("operands", []),
                "source": op_info.get("source", ""),
                "holders": holders_tuples,
                "evidence": "elv1_go",
                "accepted": True,
            }
            accepted_variants.append(rec)

    print(f"Total grid cells: {total_grid_cells}, accepted variants: {len(accepted_variants)}")

    # Write consolidated_go_vocabulary.jsonl.gz
    print(f"Writing {OUT_JSONL_GZ}...")
    with gzip.open(OUT_JSONL_GZ, "wt", encoding="utf-8") as gz_out:
        for v in accepted_variants:
            gz_out.write(json.dumps(v) + "\n")

    # Build operators map for JSON summary
    operators_map = {}
    for op_id, op_info in ops_by_id.items():
        op_name = op_info["name"]
        acc_count = per_op_accepted.get(op_id, 0)
        tot_count = per_op_total.get(op_id, 0)
        op_variants = [v for v in accepted_variants if v["operator"] == op_name]
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
            "variants": op_variants,
            "operator_name": op_name,
        }

    full_vocab_record = {
        "lang": "go",
        "compiler": vocab.get("lowerer", "go1.26.0 (golang-1.26 in the runner image), sources /usr/lib/go-1.26/src"),
        "latest_verification_run": "elv1_go",
        "summary": {
            "total_operators": len(ops_by_id),
            "accepted_operators": len(per_op_accepted),
            "refused_operators": len(ops_by_id) - len(per_op_accepted),
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

    print("Successfully built consolidated Go vocabulary!")


if __name__ == "__main__":
    main()
