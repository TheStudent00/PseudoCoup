#!/usr/bin/env python3
"""build_consolidated_rust_vocabulary.py -- extracts Rust compiler BranchTrees
from compiler/rustc_hir_typeck, compiler/rustc_mir_build, and
compiler/rustc_codegen_ssa using tree_sitter_rust, builds the consolidated
Rust vocabulary, and writes consolidated_rust_vocabulary.jsonl.gz and
consolidated_rust_vocabulary.json.
"""

import glob
import gzip
import json
import os
import sys
from pathlib import Path

import tree_sitter
import tree_sitter_rust

HERE = Path(__file__).resolve().parent
PCHQ = HERE.parents[4]
sys.path.insert(0, str(PCHQ / "Projects"))
from PseudoIR.map_HiOp_to_unit.model_lang_parts.HiOps import branch_trees  # noqa: E402

RUST_SRC = Path("sources/rust-1.96.1/compiler")
VOCAB_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "vocabulary" / "rust.json"
MASK_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "mask" / "rust.jsonl"
OUT_JSONL_GZ = HERE / "consolidated_rust_vocabulary.jsonl.gz"
OUT_JSON = HERE / "consolidated_rust_vocabulary.json"

PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_rust.language()))


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
            operand = n.child_by_field_name("value")
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
    kind = node.type
    if kind == "unary_expression":
        op = node.child_by_field_name("operator")
        op_text = text_of(op) if op else ""
        if op_text == "!":
            operand = node.child_by_field_name("operand")
            return {"op": "!", "line": line_of(node), "of": test_of(operand), "inner": []}
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
    if kind in ("block", "declaration_list"):
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind == "expression_statement":
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind == "let_declaration":
        val = node.child_by_field_name("value")
        if val:
            return statement_items(val)
        return []
    if kind == "if_expression":
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
    if kind == "match_expression":
        val = node.child_by_field_name("value")
        body = node.child_by_field_name("body")
        cases = []
        has_default = False
        if body:
            for c in body.named_children:
                if c.type == "match_arm":
                    pat = c.child_by_field_name("pattern")
                    v = c.child_by_field_name("value")
                    is_default = (text_of(pat) == "_")
                    if is_default:
                        has_default = True
                    cases.append({
                        "line": line_of(c),
                        "default": is_default,
                        "body": statement_items(v),
                        "span": [c.start_point[0] + 1, c.end_point[0] + 1],
                    })
        item = {
            "kind": "switch",
            "line": line_of(node),
            "test": test_of(val),
            "cases": cases,
            "default": has_default,
        }
        return [item]
    if kind in ("while_expression", "for_expression", "loop_expression"):
        body = node.child_by_field_name("body")
        cond = node.child_by_field_name("condition") if kind == "while_expression" else None
        item = {
            "kind": "while" if kind == "while_expression" else ("for" if kind == "for_expression" else "loop"),
            "line": line_of(node),
            "test": test_of(cond) if cond else None,
            "body": statement_items(body),
            "update": [],
        }
        return [item]
    if kind == "return_expression":
        return [{"kind": "return", "line": line_of(node)}]
    if kind == "break_expression":
        return [{"kind": "break", "line": line_of(node)}]
    if kind == "continue_expression":
        return [{"kind": "continue", "line": line_of(node)}]
    return []


def get_funcs(node, prefix=""):
    funcs = []
    if node.type == "impl_item":
        ty = node.child_by_field_name("type")
        ty_name = ty.text.decode("utf-8", errors="replace") if ty else "impl"
        sub_prefix = f"{ty_name}::"
        body = node.child_by_field_name("body")
        if body:
            for c in body.named_children:
                funcs.extend(get_funcs(c, sub_prefix))
        return funcs
    if node.type == "function_item":
        name = node.child_by_field_name("name")
        func_name = (prefix + name.text.decode("utf-8", errors="replace")) if name else f"{prefix}<anon>"
        funcs.append((func_name, node))
        return funcs
    for c in node.named_children:
        funcs.extend(get_funcs(c, prefix))
    return funcs


def extract_branch_trees_from_packages() -> tuple[dict, dict]:
    """Parse all .rs files across rustc_hir_typeck, rustc_mir_build, and rustc_codegen_ssa."""
    packages = ["rustc_hir_typeck", "rustc_mir_build", "rustc_codegen_ssa"]
    trees_by_file = {}
    total_funcs = 0
    total_branch_points = 0
    max_depth_overall = 0

    for pkg in packages:
        pkg_dir = RUST_SRC / pkg / "src"
        rs_files = sorted(glob.glob(str(pkg_dir / "**" / "*.rs"), recursive=True))
        for file_str in rs_files:
            file_path = Path(file_str)
            with open(file_path, "rb") as f:
                code = f.read()
            tree = PARSER.parse(code)
            rel_file = f"compiler/{pkg}/src/{file_path.relative_to(pkg_dir)}"
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
        "packages": [f"compiler/{p}" for p in packages],
    }
    return trees_by_file, summary


def main():
    print("Reading Rust vocabulary and verdicts...")
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    ops_by_id = {op["id"]: op for op in vocab["operators"]}
    holders_by_id = {h["id"]: h for h in vocab["holders"]}

    holders_by_spelling = {}
    for h in vocab["holders"]:
        holders_by_spelling[h["spelling"]] = [h["name"], h["spelling"], h.get("source", "")]

    print("Extracting BranchTrees from Rust compiler sources...")
    trees_by_file, branch_summary = extract_branch_trees_from_packages()
    print(f"Extracted branch trees from {branch_summary['total_files']} files, {branch_summary['total_functions']} functions.")

    # Read accepted variants from mask/rust.jsonl
    print("Reading accepted variants from mask/rust.jsonl...")
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
                "lang": "rust",
                "key": key,
                "operator": op_info["name"],
                "template": op_info["spelling"],
                "operands": op_info.get("operands", []),
                "source": op_info.get("source", ""),
                "holders": holders_tuples,
                "evidence": "elv1_rust",
                "accepted": True,
            }
            accepted_variants.append(rec)

    print(f"Total grid cells: {total_grid_cells}, accepted variants: {len(accepted_variants)}")

    # Write consolidated_rust_vocabulary.jsonl.gz
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
        "lang": "rust",
        "compiler": vocab.get("lowerer", "rustc 1.96.1 (rustup toolchain in the runner image), sources rust-1.96.1"),
        "latest_verification_run": "elv1_rust",
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

    print("Successfully built consolidated Rust vocabulary!")


if __name__ == "__main__":
    main()
