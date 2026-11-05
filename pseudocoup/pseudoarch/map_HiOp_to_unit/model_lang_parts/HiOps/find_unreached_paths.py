#!/usr/bin/env python3
"""what_is_left_for_each_hiop.py -- for each GNU C HiOp: its state in the
records, the branches the loop's records leave for it and where they sit (in
the code of clang's that names the HiOp, or in functions other HiOps' paths
run too), and the tests outside that code that name the HiOp.

the owner, 2026-10-23, on the page of a tree for each HiOp entry (1,472 of the
1,806 at depth 0): "have/can we not solve all of those 1472 HiOps at depth
0? solved so that we dont have to include them in any of the runs
anymore?"

The states are the clang's-code page's (SUPPORT_vocabulary_runs_clangs_code.py):
- not traced: no lines record holds the HiOp;
- refused: no traced path of it was accepted, in any lines record;
- accepted, branches not listed yet: no loop record holds it;
- solved: its newest loop record, merged as the page merges it
  (newest_per_operator), leaves no branch open or not reached;
- branches left: one or more branches open or not reached, each labelled
  as the page labels it (open_side_label).

The code that names a HiOp, and its depth, are the page of dots' data
(SUPPORT_in_file_trees_of_each_hiop.py, run bt1_l02). A test names the HiOp
when its text holds the HiOp's name in the form a case label would
(BI__builtin_ceil, BO_Add, UTT_IsSigned), or, for a HiOp clang tells apart
by its kind alone, the kind's name (ConvertVectorExpr, ConvertVectorExprClass).

    what_is_left_for_each_hiop.py TREES_DATA OUT
        TREES_DATA: the page of dots' data, hiop_entry_trees.json
        OUT: a folder; writes OUT/what_is_left.json
"""

import gc
import json
import os
import re
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NODE = os.path.normpath(os.path.join(HERE, "..", "..", "Planning", "node_0_1_research",
                                     "node_0_1_5_trace_logical_paths_clone"))
RUN_L14_KEYS = os.path.join(HERE, "tlp1_l14_the_trees_on_every_operator_with_branches_left", "keys_all.txt")
LEFT = ("open", "not reached (not read yet)", "not reached (candidates traced)")
MOST_EXAMPLES = 3
STATE = {"started": time.time()}


def say(text: str) -> None:
    stamp = time.strftime("%H:%M:%S", time.gmtime())
    elapsed = time.time() - STATE["started"]
    print(f"{stamp} ({elapsed:.0f} s) {text}", flush=True)


def read_json(path: str):
    with open(path, encoding="utf-8") as read:
        data = json.load(read)
    return data


def write_json(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as written:
        json.dump(data, written, indent=1)


def trees_page():
    """The page of dots' writer, whose readings of a HiOp's name and of the
    kept trees this count reuses."""
    if NODE not in sys.path:
        sys.path.insert(0, NODE)
    import SUPPORT_in_file_trees_of_each_hiop as module  # noqa: E402
    return module


MEMORY_LIMIT_BYTES = 2 * 1024 * 1024 * 1024


def main() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    data = read_json(sys.argv[1])
    page = trees_page()
    bt = page.branch_trees()
    clangs_code, keyed, gnu_c = bt.gnu_c_reading()
    say(f"[start] {len(data['hiops'])} HiOps in the page's data, made {data['made']}")
    accepted = accepted_ever(bt, clangs_code, keyed, gnu_c)
    trees = page.tree_functions(bt)
    named = named_lines(data)
    naming = naming_tests(data, bt, page, trees, named)
    left, operators_of_side = left_branches(clangs_code, keyed, gnu_c)
    in_l14 = run_l14_keys(clangs_code, keyed)
    say(f"[run tlp1_l14] {len(in_l14)} HiOps in its key list")
    rows = rows_of(data, accepted, named, naming, left, operators_of_side, in_l14)
    summary = summary_of(rows)
    add_distinct_left(summary, rows, left)
    made = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    write_json({"made": made, "trees_data": data["made"], "summary": summary, "rows": rows},
               os.path.join(sys.argv[2], "what_is_left.json"))
    say_summary(summary)


# ---------------------------------------------------------------------------
# accepted: any traced path of the HiOp accepted, in any lines record

def accepted_ever(bt, clangs_code, keyed, gnu_c) -> dict:
    """key -> {"accepted": paths accepted, "paths": paths}, summed over every
    lines record (a context traced in two records counts twice)."""
    records = clangs_code.lines_records()
    found = {}
    for number in range(len(records)):
        data = read_json(records[number])
        run = clangs_code.run_folder_name(records[number])
        add_accepted(found, data, run, clangs_code, keyed, gnu_c)
        del data
        gc.collect()
        say(f"[accepted] {number + 1} of {len(records)} lines records read; {len(found)} HiOps so far")
    return found


def add_accepted(found: dict, data: dict, run: str, clangs_code, keyed: dict, gnu_c: dict) -> None:
    for key, entry in data.get("operators", {}).items():
        vocabulary = clangs_code.vocabulary_key(key, None, run, keyed)
        if vocabulary not in gnu_c:
            continue
        counts = found.setdefault(vocabulary, {"accepted": 0, "paths": 0})
        for path in entry.get("paths", []):
            counts["paths"] += 1
            if path.get("accepted", True):
                counts["accepted"] += 1


# ---------------------------------------------------------------------------
# the code that names each HiOp, as lines of functions

def named_lines(data: dict) -> dict:
    """key -> [(function name, first line, last line)]: each function named
    for the HiOp whole, and each case that names it from its first label to
    its last line."""
    found = {}
    for hiop in data["hiops"]:
        spans = []
        for which in hiop["checking_and_lowering"]:
            for code_id in which["code"]:
                spans.append(span_of(data, data["code"][code_id]))
        found[hiop["key"]] = spans
    return found


def span_of(data: dict, code: dict) -> tuple:
    name = data["functions"][code["f"]][0]
    if code["case"] is None:
        span = (name, code["first"], code["last"])
        return span
    first = code["case"]["labels"][0][0]
    last = first
    for line, _label in code["case"]["labels"]:
        last = max(last, line)
    last = max(last, last_line_of(code["i"]))
    span = (name, first, last)
    return span


def last_line_of(items: list) -> int:
    last = 0
    pending = list(items)
    while pending:
        item = pending.pop()
        last = max(last, item.get("l") or 0)
        for outcome in item.get("o", []):
            if outcome.get("s"):
                last = max(last, outcome["s"][1])
            pending.extend(outcome.get("i", []))
    return last


def inside(spans: list, function: str, line) -> bool:
    if line is None:
        return False
    for name, first, last in spans:
        if name == function and first <= line <= last:
            return True
    return False


def branch_inside(spans: list, function: str, line, side_id: str) -> bool:
    """Whether both the test line and the untaken block's first line lie
    inside one of the HiOp's named spans (so a switch jump-table edge into
    another builtin's case is not counted as inside this HiOp's case)."""
    if line is None:
        return False
    first_line = None
    if "->" in side_id:
        tail = side_id.split("->")[-1].split()[0]
        if tail.isdigit():
            first_line = int(tail)
    for name, first, last in spans:
        if name == function and first <= line <= last:
            if first_line is None or first <= first_line <= last:
                return True
    return False


# ---------------------------------------------------------------------------
# the tests outside that code that name the HiOp

def naming_tests(data: dict, bt, page, trees: dict, named: dict) -> dict:
    """key -> [[function, line, test]]: every test of a function the HiOp's
    traced paths ran (if, switch, the loops, `?:`, `&&`, `||`) whose text
    names the HiOp, outside the code that names it."""
    found = {}
    tests_cache = {}
    for number in range(len(data["hiops"])):
        hiop = data["hiops"][number]
        pattern = name_pattern(page, hiop["key"])
        hits = []
        for function_id in functions_ran(hiop):
            name, relative, first = data["functions"][function_id]
            for line, text in tests_of(bt, trees, name, relative, first, tests_cache):
                if pattern.search(text) and not inside(named[hiop["key"]], name, line):
                    hits.append([name, line, text])
        found[hiop["key"]] = hits
        if (number + 1) % 300 == 0:
            say(f"[tests] {number + 1} of {len(data['hiops'])} HiOps searched")
    return found


def name_pattern(page, key: str):
    kind, inner = page.kind_and_name(key)
    if inner is not None:
        pattern = page.label_pattern(kind, inner)
        return pattern
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(kind) + r"(?:Class)?(?![A-Za-z0-9_])")
    return pattern


def functions_ran(hiop: dict) -> list:
    found = []
    for which in hiop["checking_and_lowering"]:
        for function_id in which["ran"]:
            if function_id not in found:
                found.append(function_id)
    return found


def tests_of(bt, trees: dict, name: str, relative: str, first, cache: dict) -> list:
    """[(line, test text)] of every tree function the name is (candidates_for),
    found once per name."""
    if name in cache:
        found = cache[name]
        return found
    found = []
    for function in bt.candidates_for(name, relative, first, trees["by_name"], trees["by_file"]):
        add_tests(found, function["tree"])
    cache[name] = found
    return found


def add_tests(found: list, items: list) -> None:
    page = trees_page()
    pending = list(items)
    while pending:
        item = pending.pop()
        if isinstance(item.get("test"), dict):
            found.append((item.get("line") or item["test"].get("line"), page.test_text(item["test"])))
        for held in ("then", "else", "body", "update"):
            if isinstance(item.get(held), list):
                pending.extend(item[held])
        for case in item.get("cases") or []:
            pending.extend(case.get("body", []))


# ---------------------------------------------------------------------------
# the branches left, from the loop's records, as the clang's-code page reads them

def left_branches(clangs_code, keyed: dict, gnu_c: dict) -> tuple:
    """(key -> side id -> (label, function, test line), side id -> how many
    HiOps it is left for)."""
    loop_read = clangs_code.read_loop_records()
    say(f"[loop] {len(loop_read)} loop records read")
    problems = clangs_code.problems_page()
    newest = problems.newest_per_operator(loop_read)
    del loop_read
    found = {}
    cache = {}
    for key, entry in newest.items():
        vocabulary = clangs_code.vocabulary_key(key, None, entry["run"], keyed)
        if vocabulary not in gnu_c:
            continue
        sides = found.setdefault(vocabulary, {})
        for side_id, side in entry["sides"].items():
            label = label_of(side_id, side, gnu_c, problems, clangs_code, cache)
            if label == "not reached":
                label = not_reached_kind(side, problems)
            sides[side_id] = (label, side.get("function") or "", side.get("test"))
    operators_of_side = {}
    for sides in found.values():
        for side_id, (label, _function, _line) in sides.items():
            if label in LEFT:
                operators_of_side[side_id] = operators_of_side.get(side_id, 0) + 1
    say(f"[loop] {len(found)} GNU C HiOps hold a loop record; {len(operators_of_side)} distinct branches left")
    found_both = (found, operators_of_side)
    return found_both


def label_of(side_id: str, side: dict, gnu_c: dict, problems, clangs_code, cache: dict) -> str:
    """The page's label (summarize_loop_step): taken, not needed, open or not
    reached."""
    outcome = side.get("outcome", "")
    if outcome == "taken":
        label = "taken"
        return label
    if outcome != "open":
        label = "not needed"
        return label
    cache_key = (side_id, side.get("why") or "")
    if cache_key not in cache:
        cache[cache_key] = clangs_code.open_side_label(side, gnu_c, problems)
    label = cache[cache_key]
    return label


def not_reached_kind(side: dict, problems) -> str:
    """The page's two kinds of not reached (summarize_latest_branches): the
    candidates traced did not take it, or its condition is not read yet."""
    kind = "not reached (not read yet)"
    if (side.get("why") or "") == problems.TAKEN_ON_NONE:
        kind = "not reached (candidates traced)"
    return kind


def run_l14_keys(clangs_code, keyed: dict) -> set:
    """The HiOps run tlp1_l14 works through: its key list's lines are a key,
    a tab and the key's branches not reached; lines starting with # are its
    header."""
    found = set()
    if not os.path.isfile(RUN_L14_KEYS):
        return found
    with open(RUN_L14_KEYS, encoding="utf-8") as read:
        for line in read:
            if not line.strip() or line.startswith("#"):
                continue
            key = line.split("\t")[0].strip()
            found.add(clangs_code.vocabulary_key(key, None, "tlp1_l14", keyed) or key)
    return found


# ---------------------------------------------------------------------------
# one row a HiOp, and the sums

def rows_of(data: dict, accepted: dict, named: dict, naming: dict, left: dict, operators_of_side: dict,
            in_l14: set) -> list:
    rows = []
    for hiop in data["hiops"]:
        rows.append(row_of(hiop, accepted, named, naming, left, operators_of_side, in_l14))
    return rows


def row_of(hiop: dict, accepted: dict, named: dict, naming: dict, left: dict, operators_of_side: dict,
           in_l14: set) -> dict:
    key = hiop["key"]
    counts = accepted.get(key, {"accepted": 0, "paths": 0})
    sides = left.get(key)
    row = {"key": key, "depth": hiop["depth"], "paths": counts["paths"], "accepted": counts["accepted"],
           "state": state_of(hiop, counts, sides), "in_run_tlp1_l14": key in in_l14,
           "left": 0, "left_in_named_code": 0, "left_elsewhere": 0, "left_for_it_alone": 0,
           "left_for_two_or_more": 0, "tests_naming_it_elsewhere": len(naming.get(key, [])),
           "examples": naming.get(key, [])[:MOST_EXAMPLES]}
    if sides is None:
        return row
    for side_id, (label, function, line) in sides.items():
        if label not in LEFT:
            continue
        row["left"] += 1
        if branch_inside(named[key], function, line, side_id):
            row["left_in_named_code"] += 1
        else:
            row["left_elsewhere"] += 1
        if operators_of_side.get(side_id, 0) == 1:
            row["left_for_it_alone"] += 1
        else:
            row["left_for_two_or_more"] += 1
    if row["state"] == "branches left" and row["left"] == 0:
        row["state"] = "solved"
    return row


def state_of(hiop: dict, counts: dict, sides) -> str:
    if hiop["depth"] is None or counts["paths"] == 0:
        state = "not traced"
        return state
    if counts["accepted"] == 0:
        state = "refused"
        return state
    if sides is None:
        state = "accepted, branches not listed yet"
        return state
    state = "branches left"
    return state


def group_of(row: dict) -> str:
    group = "depth 1 or more"
    if row["depth"] is None:
        group = "not traced"
    elif row["depth"] == 0:
        group = "depth 0"
    return group


def summary_of(rows: list) -> dict:
    found = {}
    for row in rows:
        sums = found.setdefault(group_of(row), {"HiOps": 0, "by state": {}, "in run tlp1_l14": 0,
                                                "branches left in run tlp1_l14": 0, "left": 0,
                                                "left in named code": 0, "left elsewhere": 0,
                                                "left for it alone": 0, "left for two or more": 0,
                                                "HiOps with a branch left for it alone": 0,
                                                "HiOps named by a test elsewhere": 0})
        sums["HiOps"] += 1
        sums["by state"][row["state"]] = sums["by state"].get(row["state"], 0) + 1
        if row["in_run_tlp1_l14"]:
            sums["in run tlp1_l14"] += 1
            if row["state"] == "branches left":
                sums["branches left in run tlp1_l14"] += 1
        sums["left"] += row["left"]
        sums["left in named code"] += row["left_in_named_code"]
        sums["left elsewhere"] += row["left_elsewhere"]
        sums["left for it alone"] += row["left_for_it_alone"]
        sums["left for two or more"] += row["left_for_two_or_more"]
        if row["left_for_it_alone"]:
            sums["HiOps with a branch left for it alone"] += 1
        if row["tests_naming_it_elsewhere"]:
            sums["HiOps named by a test elsewhere"] += 1
    return found


def add_distinct_left(summary: dict, rows: list, left: dict) -> None:
    """Each group's distinct branches left: one branch left for many HiOps of
    the group counts once."""
    distinct = {}
    for row in rows:
        sides = left.get(row["key"]) or {}
        seen = distinct.setdefault(group_of(row), {})
        for side_id, (label, _function, _line) in sides.items():
            if label in LEFT:
                seen[side_id] = label
    for group, seen in distinct.items():
        by_label = {}
        for label in seen.values():
            by_label[label] = by_label.get(label, 0) + 1
        summary[group]["distinct branches left"] = len(seen)
        summary[group]["distinct branches left, by label"] = by_label


def say_summary(summary: dict) -> None:
    for group in ("depth 0", "depth 1 or more", "not traced"):
        if group in summary:
            say(f"[summary] {group}: {json.dumps(summary[group])}")


if __name__ == "__main__":
    main()
