#!/usr/bin/env python3
"""build_consolidated_java_vocabulary.py -- extracts Java compiler & native HotSpot BranchTrees
from Attr.java, Lower.java, Gen.java, Operators.java, templateTable_riscv.cpp, and
c1_LIRAssembler_arith_riscv.cpp using tree_sitter_java and tree_sitter_cpp, builds
the consolidated Java vocabulary (4,999 accepted variants across 42 accepted operators),
and writes consolidated_java_vocabulary.jsonl.gz and consolidated_java_vocabulary.json.
"""

import gzip
import json
import os
import sys
from pathlib import Path

import tree_sitter
import tree_sitter_cpp
import tree_sitter_java

HERE = Path(__file__).resolve().parent
PCHQ = HERE.parents[4]
sys.path.insert(0, str(PCHQ / "Projects"))
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps import branch_trees  # noqa: E402

JDK_SRC = Path("sources/jdk-25.0.4")
VOCAB_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "vocabulary" / "java.json"
MASK_PATH = PCHQ / "Research" / "extract_lang_vocabulary" / "mask" / "java.jsonl"
OUT_JSONL_GZ = HERE / "consolidated_java_vocabulary.jsonl.gz"
OUT_JSON = HERE / "consolidated_java_vocabulary.json"

JAVA_PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_java.language()))
CPP_PARSER = tree_sitter.Parser(tree_sitter.Language(tree_sitter_cpp.language()))

TARGET_SOURCES = [
    ("src/jdk.compiler/share/classes/com/sun/tools/javac/comp/Attr.java", "java"),
    ("src/jdk.compiler/share/classes/com/sun/tools/javac/comp/Lower.java", "java"),
    ("src/jdk.compiler/share/classes/com/sun/tools/javac/jvm/Gen.java", "java"),
    ("src/jdk.compiler/share/classes/com/sun/tools/javac/comp/Operators.java", "java"),
    ("src/hotspot/cpu/riscv/templateTable_riscv.cpp", "cpp"),
    ("src/hotspot/cpu/riscv/c1_LIRAssembler_arith_riscv.cpp", "cpp"),
]


def line_of(node) -> int:
    return node.start_point[0] + 1


def text_of(node) -> str:
    if node is None:
        return ""
    return node.text.decode("utf-8", errors="replace")


def atoms_of(node) -> list:
    atoms = []

    def walk(n):
        if n.type in ("method_invocation", "call_expression"):
            fn = n.child_by_field_name("name") or n.child_by_field_name("function")
            atoms.append({"atom": "call", "callee": text_of(fn) if fn else ""})
        elif n.type in ("field_access", "field_expression"):
            rec = n.child_by_field_name("object") or n.child_by_field_name("argument")
            field = n.child_by_field_name("field")
            atoms.append({
                "atom": "field",
                "receiver": text_of(rec) if rec else "",
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
    if node.type in ("parenthesized_expression",):
        for c in node.named_children:
            return test_of(c)
    if node.type == "unary_expression":
        op = node.child_by_field_name("operator")
        op_text = text_of(op) if op else ""
        if op_text == "!":
            operand = node.child_by_field_name("operand") or node.child_by_field_name("argument")
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
    if kind in ("block", "compound_statement", "declaration_list"):
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind == "expression_statement":
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
            "then_span": [line_of(conseq), conseq.end_point[0] + 1] if conseq else None,
            "else_span": [line_of(alt), alt.end_point[0] + 1] if alt else None,
        }
        return [item]
    if kind == "else_clause":
        items = []
        for c in node.named_children:
            items.extend(statement_items(c))
        return items
    if kind in ("switch_statement", "switch_expression"):
        val = node.child_by_field_name("condition") or node.child_by_field_name("value")
        cases = []
        for c in node.named_children:
            if "switch_block" in c.type or "compound_statement" in c.type:
                for grp in c.named_children:
                    if grp.type in ("switch_block_statement_group", "case_statement"):
                        cases.append({
                            "line": line_of(grp),
                            "body": statement_items(grp),
                            "span": [line_of(grp), grp.end_point[0] + 1],
                        })
        return [{
            "kind": "switch",
            "line": line_of(node),
            "value": text_of(val),
            "cases": cases,
            "default": None,
            "atoms": atoms_of(val),
        }]
    return []


def extract_branch_trees() -> tuple[dict, dict]:
    """Parse javac and HotSpot RISC-V lowering sources into BranchTree records."""
    trees_by_file = {}
    total_funcs = 0
    total_branch_points = 0
    max_depth_overall = 0

    for rel_path, lang in TARGET_SOURCES:
        full_path = JDK_SRC / rel_path
        if not full_path.exists():
            print(f"[warning] File not found: {full_path}")
            continue

        with open(full_path, "rb") as f:
            code = f.read()

        parser = JAVA_PARSER if lang == "java" else CPP_PARSER
        tree = parser.parse(code)

        funcs = []

        def find_funcs(n):
            if lang == "java" and n.type in ("method_declaration", "constructor_declaration"):
                name_node = n.child_by_field_name("name")
                body_node = n.child_by_field_name("body")
                if name_node and body_node:
                    funcs.append((text_of(name_node), body_node, [line_of(n), n.end_point[0] + 1]))
            elif lang == "cpp" and n.type == "function_definition":
                decl = n.child_by_field_name("declarator")
                body = n.child_by_field_name("body")
                if decl and body:
                    funcs.append((text_of(decl), body, [line_of(n), n.end_point[0] + 1]))
            for c in n.named_children:
                find_funcs(c)

        find_funcs(tree.root_node)

        func_records = []
        for name, body, span in funcs:
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
                "first": span[0],
                "last": span[1],
                "lambda": False,
                "parse_errors": 0,
                "tree": items,
                "A": sum_a,
                "B": sum_b,
            })
            total_funcs += 1

        trees_by_file[rel_path] = {
            "file": rel_path,
            "functions": func_records,
        }

    summary = {
        "total_files": len(trees_by_file),
        "total_functions": total_funcs,
        "total_top_level_branch_items": total_branch_points,
        "max_depth": max_depth_overall,
        "sources": [s[0] for s in TARGET_SOURCES],
    }
    return trees_by_file, summary


def main():
    print("Reading Java vocabulary and mask verdicts...")
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    ops_by_id = {op["id"]: op for op in vocab["operators"]}
    holders_by_id = {h["id"]: h for h in vocab["holders"]}

    holders_by_spelling = {}
    for h in vocab["holders"]:
        holders_by_spelling[h["spelling"]] = [h["name"], h["spelling"], h.get("source", "")]

    print("Extracting BranchTrees from Java compiler and HotSpot RISC-V sources...")
    trees_by_file, branch_summary = extract_branch_trees()
    print(
        f"Extracted branch trees from {branch_summary['total_files']} files, "
        f"{branch_summary['total_functions']} functions, max_depth={branch_summary['max_depth']}."
    )

    print("Reading accepted variants from mask/java.jsonl...")
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
                "lang": "java",
                "key": key,
                "operator": op_info["name"],
                "template": op_info["spelling"],
                "operands": op_info.get("operands", []),
                "source": op_info.get("source", ""),
                "holders": holders_tuples,
                "evidence": "elv1_java",
                "accepted": True,
            }
            accepted_variants.append(rec)

    print(f"Total grid cells: {total_grid_cells}, accepted variants: {len(accepted_variants)}")

    print(f"Writing {OUT_JSONL_GZ}...")
    with gzip.open(OUT_JSONL_GZ, "wt", encoding="utf-8") as gz_out:
        for v in accepted_variants:
            gz_out.write(json.dumps(v) + "\n")

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
        "lang": "java",
        "compiler": vocab.get("lowerer", "javac 25.0.4.1 (openjdk-25 in the runner image), sources jdk-25.0.4"),
        "latest_verification_run": "elv1_java",
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

    print("Successfully built consolidated Java vocabulary!")


if __name__ == "__main__":
    main()
