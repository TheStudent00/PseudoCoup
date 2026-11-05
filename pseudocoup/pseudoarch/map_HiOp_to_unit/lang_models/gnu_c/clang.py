"""clang -- extract_lang_vocab's own steps for GNU C, through clang: what
PseudoCoup covers of clang's vocabulary, one holder of each kind of type C can
name, which holders cross which operators in each pass of the grid, and what
clang's syntax tree says each accepted cell is.

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/`
(`extract()`, the node's loop, calls this module for c).

    vocabulary = vocabulary("c")    # clang's operators and holders, as PseudoCoup covers them
    read = read_signatures("c", vocabulary, kept, work, small)   # the signatures clang's checking code accepts, read from it
    found = passes("c", vocabulary, kept, declarations, work, evidence, small, read)

Moved here on 2026-10-14 (PCHQ log 456), at the owner's word "lets do it", from the
research runner `Research/extract_lang_vocabulary/run_elv3.py` (GNU C's grid,
PCHQ log 367) and from
`Research/extract_lang_vocabulary/complex_signature_reader/covered_vocabulary.py`
(which made `vocabulary/c.json` on 2026-10-01). The code is as it was there,
but for four things:
- the work folder and the library declarations are handed in (they were
  run_elv3's globals WORK and DECLARATIONS), and so is the evidence's run name
  (run_elv3 wrote `elv3`);
- judge_pass answers its cells and verdicts with its rows (Judged), so that
  extract() can list the HiOps in the order they were first asked;
- the covered vocabulary is made from the readers' own reading
  (operator_reader, holder_reader), where run_elv3 read it from c.json, which
  covered_vocabulary.py made from the reading of 2026-09-30. Run elv2_l163
  read the vocabulary again: the same 2,829 operators, 514 holders and 541
  left out, and c.json's 1,254 builtins, 907 forms and 28 holders, made again
  the same;
- every holder the reading gives is asked, once per spelling, and then the
  representatives; run_elv3 asked only the holders C17 or C++20 accepted
  (judged in research, `judge/holders/`). Run elv2_l163: GNU C keeps the same
  52 either way.
The comprehensions and conditional expressions are as they were written there.
"""
import itertools
import json
import os
import re
import subprocess
import time
from typing import NamedTuple

from ...model_lang_parts import Holder, Judged, Operator, holder_reader, operator_reader
from ...model_lang_parts.HiOps.operator_reader import clang as clang_reader
from ... import mask_maker as mask_code
from ...model_lang_parts.holders import accepted_signatures
from ...dict_of_lang_HiOps import Variant


class Vocabulary(NamedTuple):
    """GNU C's vocabulary as the grid asks it: clang's operators and holders,
    as PseudoCoup covers them."""

    written: dict
    forms: list
    builtins: list
    operators: tuple
    holders: tuple


class Passes(NamedTuple):
    """GNU C's grid, pass by pass, as run_elv3 asked it (PCHQ log 367): every
    form over the small set (a), the forms it accepted over every holder kept
    (b), every builtin over every holder kept (c), and since 2026-10-16 each
    builtin with custom typechecking over the signatures its checking code
    accepts, read from it (read_signatures); for b and c, one accepted
    cell of each operator read back through clang's syntax tree (kinds), and
    every accepted cell of the operators read back as written, read back
    (variants); `&&m`, held in a function of its own (label)."""

    a: Judged
    b: Judged
    kinds_b: list
    variants_b: list
    label: dict
    c: Judged
    kinds_c: list
    variants_c: list
    judged: tuple
    as_written: set
    own_HiOps: list


def vocabulary(lang: str) -> Vocabulary:
    """GNU C's operators and holders, read from clang by the readers, as
    PseudoCoup covers them: the builtins of clang's generic list that C or C++
    has, clang's expressions and statements, and every holder."""
    whole = whole_reading(lang)
    written = covered_vocabulary(whole)
    forms = forms_of(written)
    builtins = builtins_of(written)
    operators = tuple(forms + builtins)
    holders = holders_of(whole)
    read = Vocabulary(written, forms, builtins, operators, holders)
    return read


def whole_reading(lang: str) -> dict:
    """Everything the readers give, in the form run_elv1.step_vocab wrote it on
    2026-09-30 (`.archive/c_json_whole_reading_2026-09-30/c.json`)."""
    operators, left_out = operator_reader.read_operators(lang)
    holders = holder_reader.read_holders(lang)
    whole = {"operators": operator_entries(lang, operators), "holders": holder_entries(lang, holders),
             "left_out": left_out_entries(left_out)}
    return whole


def operator_entries(lang: str, operators: tuple) -> list:
    entries = []
    for position, operator in enumerate(operators):
        entries.append({"lang": lang, "id": position, "name": operator.name, "spelling": operator.spelling,
                        "operands": list(operator.operands), "source": operator.source})
    return entries


def holder_entries(lang: str, holders: tuple) -> list:
    entries = []
    for position, holder in enumerate(holders):
        entries.append({"lang": lang, "id": position, "name": holder.name, "spelling": holder.spelling,
                        "source": holder.source})
    return entries


def left_out_entries(left_out: tuple) -> list:
    entries = []
    for name, reason in left_out:
        entries.append({"name": name, "reason": reason})
    return entries


def covered_vocabulary(whole: dict) -> dict:
    """c.json's builtins, forms and left-out entries, made from the whole
    reading as covered_vocabulary.main made them (its holders are not made
    here: holders_of asks every holder)."""
    clang = generic_list()
    builtins, moved, _missing = covered_builtins(whole, clang)
    forms = covered_forms(whole, moved)
    kept = set()
    for entry in builtins:
        kept.add(entry["builtin"])
    left_out = covered_left_out(whole, kept)
    written = {"builtins": builtins, "forms": forms, "left_out": left_out}
    return written


def covered_forms(whole: dict, moved: set) -> list:
    """Every expression and statement of the reading, but the calls moved into
    their builtins, numbered again (covered_vocabulary.main)."""
    forms = []
    for entry in whole["operators"]:
        if builtin_of(entry["name"]) is not None or entry["id"] in moved:
            continue
        forms.append(dict(entry, whole_id=entry["id"]))
    for position, entry in enumerate(forms):
        entry["id"] = position
    return forms


def covered_left_out(whole: dict, kept: set) -> list:
    left_out = []
    for item in whole["left_out"]:
        builtin = builtin_of(item["name"])
        if builtin is None or builtin in kept:
            left_out.append(item)
    return left_out


def holders_of(whole: dict) -> tuple:
    """Every holder the reading gives, once per spelling, then the
    representatives: one or more of each kind of type C can name that a
    spelling alone cannot."""
    holders = []
    seen = set()
    for entry in whole["holders"]:
        if entry["spelling"] in seen:
            continue
        seen.add(entry["spelling"])
        holders.append(Holder("c", entry["name"], entry["spelling"], entry["source"]))
    for kind, spelling in REPRESENTATIVES:
        if spelling in seen:
            continue
        seen.add(spelling)
        holders.append(Holder("c", kind, spelling, f"one {kind} (clang/include/clang/Basic/TypeNodes.td)"))
    found = tuple(holders)
    return found


def passes(lang: str, vocabulary: Vocabulary, kept: list, declarations: tuple, work: str, evidence: str,
           small: bool, read=None) -> Passes:
    """GNU C's grid, in the order run_elv3.step_grid asked it. `read` adds to
    pass c the signatures read from clang's checking code (read_signatures);
    its holders are at the end of `vocabulary.holders`."""
    suffix = small_suffix(small)
    holders = vocabulary.holders
    written = vocabulary.written
    a = judge_pass("a" + suffix, vocabulary.forms, holders, kept, False, small, work, evidence, declarations)
    accepted_forms = accepted_operators(vocabulary.forms, a)
    b = judge_pass("b" + suffix, accepted_forms, holders, kept, True, small, work, evidence, declarations)
    kinds_b = kinds_pass("kb" + suffix, first_forty(accepted_forms, small), holders, b.rows, written, work,
                         declarations)
    variants_b = variants_pass("vb" + suffix, accepted_forms, holders, rows_read_back(b.rows, kinds_b), written,
                               work, declarations)
    label = label_address_check(work)
    full = not small
    c = judge_pass("c" + suffix, vocabulary.builtins, holders, kept, full, small, work, evidence, declarations, read)
    kinds_c = kinds_pass("kc" + suffix, first_forty(vocabulary.builtins, small), holders, c.rows, written, work,
                         declarations)
    variants_c = variants_pass("vc" + suffix, vocabulary.builtins, holders, rows_read_back(c.rows, kinds_c),
                               written, work, declarations)
    as_written = read_back_as_written(kinds_b + kinds_c)
    own_HiOps = label_HiOps(lang, label, evidence)
    found = Passes(a, b, kinds_b, variants_b, label, c, kinds_c, variants_c, (a, b, c), as_written, own_HiOps)
    return found


def read_signatures(lang: str, vocabulary: Vocabulary, kept: list, work: str, small: bool):
    """For each builtin with custom typechecking (clang's list marks it `t`:
    "signature is meaningless, use custom typechecking", so clang checks its
    arguments with code written for that builtin, in SemaChecking.cpp), the
    signatures that code accepts (complex_signature_reader.accepted_signatures): each argument the
    code tests, tested on the holders kept and a pointer to each; an argument
    it does not test takes the holders holders_for gives the operator. A
    small run reads the first 40 builtins, as pass c asks them."""
    full = not small
    holders = vocabulary.holders
    kept_spellings = []
    for position in kept:
        kept_spellings.append(holders[position].spelling)

    def defaults_of(operator) -> list:
        spellings = []
        for position in holders_for(operator, kept, holders, full):
            spellings.append(holders[position].spelling)
        return spellings

    operators = first_forty(vocabulary.builtins, small)
    directory = os.path.join(work, "read_signatures")
    read = accepted_signatures.read_signatures(operators, kept_spellings, defaults_of, directory)
    return read


def small_suffix(small: bool) -> str:
    suffix = ""
    if small:
        suffix = ".small"
    return suffix


def accepted_operators(operators: list, judged: Judged) -> list:
    """The operators with at least one accepted cell, in the pass's order."""
    accepted = []
    for row in judged.rows:
        if row["accepted"]:
            accepted.append(operators[row["position"]])
    return accepted


def first_forty(operators: list, small: bool) -> list:
    """A small run reads back the first 40 operators, as it asks them."""
    if small:
        return operators[:40]
    return operators


def read_back_as_written(kinds: list) -> set:
    """(name, template) of every operator clang read back as written, or as
    the same builtin at another size: clang sizes a `__sync_*` builtin by
    what its pointer points to (`__sync_fetch_and_add_4` on a `char *` is
    `__sync_fetch_and_add_1`). Each such signature is a HiOp variant clang
    accepts, its holders the context that sets its size (the owner, 2026-10-15:
    "those signatures look like HiOp variants with context that modifies
    their meanings"; on keeping every one: "if it works, then yeah sure").
    Until 2026-10-16 the form was dropped (item 47 of the missing list)."""
    as_written = set()
    for kind in kinds:
        if kind["parsed_as_written"] or kind.get("same_builtin_other_size"):
            as_written.add((kind["name"], kind["template"]))
    return as_written


def rows_read_back(rows: list, kinds: list) -> list:
    """The pass's rows of the operators clang read back as written."""
    as_written = read_back_as_written(kinds)
    chosen = []
    for row in rows:
        if (row["name"], row["template"]) in as_written:
            chosen.append(row)
    return chosen


def label_HiOps(lang: str, label: dict, evidence: str) -> list:
    """`&&m`, as a HiOp with no holder, when clang accepted its standard function
    and read it back as written."""
    HiOps = []
    if label["accepted"] and label["parsed_as_written"]:
        HiOps.append(Variant(lang, LABEL_ADDRESS, (), None, f"{evidence} label".strip()))
    return HiOps


# What follows is moved from run_elv3.py and covered_vocabulary.py, as above.

C_OR_CXX = ("ALL_LANGUAGES", "CXX_LANG", "C23_LANG")
# One record per builtin in clang's generic list: name, type letters,
# attributes, header, language column.
RECORD = re.compile(r"StrOffsets\{\d+ /\* (.*?) \*/, \d+(?: /\* (.*?) \*/)?, \d+ /\* (.*?) \*/[^}]*\}, "
                    r"HeaderDesc::(\w+), ([\w |]+)\}")


def builtin_of(name: str):
    """The builtin a whole-reading entry calls, or None for a form."""
    for prefix in ("CallExpr.BI", "AtomicExpr.AO"):
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def generic_list() -> dict:
    """builtin -> (type letters, attributes, language), clang's generic list.
    (covered_vocabulary.py read the list from made_by_clang/Builtins.inc, which
    clang-tblgen made; here clang-tblgen makes it, as operator_reader does.)"""
    text = clang_reader.made_list(clang_reader.BUILTINS_TD)
    return {name: (letters or "", attributes or "", language.strip())
            for name, letters, attributes, _header, language in RECORD.findall(text)}


def covered_builtins(whole: dict, clang: dict) -> tuple:
    """One entry per builtin C or C++ has, its variants inside, and the
    forms that are calls to one of them (moved into it)."""
    covered = {name for name, (_l, _a, language) in clang.items() if language in C_OR_CXX}
    variants, moved = {}, set()
    for entry in whole["operators"]:
        builtin = builtin_of(entry["name"])
        if builtin is None:
            # a form that is a call to a covered builtin: clang writes
            # __builtin_shufflevector as its own kind of expression
            found = re.match(r"^(\w+)\s*\(", entry["spelling"])
            if found and found.group(1) in covered:
                builtin = found.group(1)
                moved.add(entry["id"])
        if builtin in covered:
            variants.setdefault(builtin, []).append(entry)
    entries = []
    for name in sorted(variants, key=lambda n: min(v["id"] for v in variants[n])):
        letters, attributes, language = clang[name]
        entries.append({
            "lang": "c", "id": len(entries), "builtin": name, "language": language,
            "custom_typechecking": "t" in attributes, "signature": letters,
            "variants": [{"name": v["name"], "spelling": v["spelling"], "operands": v["operands"],
                          "source": v["source"], "whole_id": v["id"]} for v in variants[name]],
        })
    return entries, moved, covered - set(variants)


# One or more of each kind of type in clang's TypeNodes.td that C can name
# and a spelling alone cannot: (clang's kind, the spelling). The declared
# names (struct S, fnptr, ...) are DRY_mask_maker.C_HELD_TYPES.
REPRESENTATIVES = [
    ("BuiltinType", "__float128"),
    ("BuiltinType", "__builtin_va_list"),
    ("ComplexType", "float _Complex"),
    ("ComplexType", "double _Complex"),
    ("ComplexType", "long double _Complex"),
    ("ComplexType", "_Complex int"),
    ("PointerType", "void *"),
    ("PointerType", "char *"),
    ("PointerType", "int *"),
    ("PointerType", "double *"),
    ("PointerType", "struct S *"),
    ("PointerType", "struct I *"),
    ("PointerType", "fnptr"),
    ("PointerType", "arrptr"),
    ("PointerType", "int **"),
    ("PointerType", "const int *"),
    ("ConstantArrayType", "arr4"),
    ("VectorType", "v4si"),
    ("VectorType", "v4sf"),
    ("ExtVectorType", "ev4si"),
    ("RecordType", "struct S"),
    ("RecordType", "union U"),
    ("RecordType", "struct I"),
    ("EnumType", "enum E"),
    ("AtomicType", "_Atomic int"),
    ("AtomicType", "_Atomic long"),
    ("AtomicType", "_Atomic double"),
    ("AtomicType", "_Atomic(int *)"),
    ("BitIntType", "_BitInt(37)"),
    ("BitIntType", "unsigned _BitInt(37)"),
    ("BitIntType", "_BitInt(128)"),
    ("FunctionProtoType", "fntype"),
    ("qualified", "const int"),
    ("qualified", "volatile int"),
]

# The small set: one holder of each group, for the passes that cross every
# form. For three to five operands, the smaller set below; for six or more,
# int and double. (An unsigned integer and an array added in run elv2_l72:
# without them `_Countof`, which takes an array, read as refused.)
SMALL = ["int", "unsigned int", "double", "double _Complex", "int *", "void *", "struct S", "struct S *",
         "fnptr", "__builtin_va_list", "v4si", "_Atomic int", "arr4"]
SMALLER = ["int", "double", "int *", "struct S"]
SMALLEST = ["int", "double"]


# Forms holding C++'s scope operator `::`. clang 21 did not finish one such
# held cell in C mode (`__typeof__(::delete [] (int){0})`, run elv2_l63,
# stopped after 5 minutes), so in C they are recorded, not judged.
NOT_JUDGED_IN_C = "::"


# Two simple operators c.json leaves out, because the operator reader keeps
# only kinds that take an operand (PCHQ log 366, Table 1): reading a held
# value, and taking a label's address. Each is named from clang's own lists.
# The read is the conversion clang adds wherever a held value is used; a
# program writes only the holder, `a`.
THE_READ = Operator("c", "ImplicitCastExpr.LValueToRValue", "a", ("a",),
                    "clang/include/clang/AST/OperationKinds.def: CAST_OPERATION(LValueToRValue); "
                    "left out of c.json (DeclRefExpr: it takes no operand, only a name)")
# `&&m` takes a label, which only a function body can hold, so it has a
# standard form of its own (label_address_check).
LABEL_ADDRESS = Operator("c", "AddrLabelExpr", "&&m", ("m",),
                         "clang/include/clang/Basic/StmtNodes.td: def AddrLabelExpr; "
                         "left out of c.json (it takes no operand, only a name)")
# `&&m`'s standard function by hand, as the grid held it until PCHQ log 424: the
# check. Since then the routing read from the record holds it
# (DRY_mask_maker.ROUTING.local_answers: its answer in a local, its label
# after it).
LABEL_ADDRESS_HELD_BY_HAND = "void op_label(void) { m:; __typeof__(&&m) r = (&&m); (void)r; }"


def forms_of(written: dict) -> list:
    """Each expression and statement form, as an Operator, but those holding
    NOT_JUDGED_IN_C; then the read."""
    operators = []
    for entry in written["forms"]:
        if NOT_JUDGED_IN_C in entry["spelling"]:
            continue
        operators.append(Operator("c", entry["name"], entry["spelling"], tuple(entry["operands"]), entry["source"]))
    operators.append(THE_READ)
    return operators


def label_address_check(work: str) -> dict:
    """`&&m`, held as the routing read from the record says (PCHQ log 424): its
    answer in a local, its label after it. Accepted, and read back through
    clang's syntax tree: the local's initializer, through its parenthesis.

        void part_label_label(void); struct P_label { char unused_; };
        void op_label(struct P_label *p) { __typeof__(&&m) result = (&&m); m: part_label_label(); }

    Until log 424 the standard function was written by hand
    (LABEL_ADDRESS_HELD_BY_HAND), the local second, after the label."""
    directory = os.path.join(work, "label")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "label.c")
    held = mask_code.standard_cell_lines("c", "label", LABEL_ADDRESS, ())
    with open(path, "w") as out:
        out.write("\n".join(mask_code.PREAMBLE["c"] + held) + "\n")
    command = mask_code.JUDGE_COMMAND["c"].split() + mask_code.KIND_COMMAND_TAIL.split() + [path]
    with open(path + ".ast.json", "w") as tree_file, open(path + ".diag", "w") as diagnostics:
        done = subprocess.run(command, stdout=tree_file, stderr=diagnostics, check=False)
    with open(path + ".diag") as diagnostics:
        refusals = [line.strip() for line in diagnostics if " error: " in line]
    kind = None
    if done.returncode == 0:
        trees = mask_code.read_syntax_trees(path + ".ast.json")
        body = trees["op_label"]["inner"][-1]
        kind = initializer_kind(body)
    return {"name": LABEL_ADDRESS.name, "template": LABEL_ADDRESS.spelling, "held_form": "\n".join(held),
            "accepted": done.returncode == 0, "refusals": refusals, "parsed_as": kind,
            "parsed_as_written": kind == "AddrLabelExpr", "source": LABEL_ADDRESS.source}


def initializer_kind(body: dict):
    """The kind of the first local's initializer in a function body, through
    its parenthesis and clang's own conversions; None when the body declares
    no local with one."""
    for statement in body.get("inner", []):
        if statement.get("kind") != "DeclStmt":
            continue
        declaration = statement["inner"][0]
        initializer = declaration["inner"][-1]
        while initializer.get("kind") in ("ParenExpr", "ImplicitCastExpr") and initializer.get("inner"):
            initializer = initializer["inner"][0]
        kind = initializer.get("kind")
        return kind
    kind = None
    return kind


# One type in clang's type string for a builtin (Builtins.td's prototype,
# as c.json keeps it): prefix modifiers (I: must be a constant), the base,
# then pointer and qualifier marks.
TYPE_IN_SIGNATURE = re.compile(r"(I?)((?:LLL|LL|L|U|S|Z|W|N|O)*)((?:V|E|q)\d+|X)?(SJ|[vbcsihxyfdzwFGHMaAYPJKp])([*&CDR]*\d*[*&CDR]*)")


def constant_arguments(signature: str) -> dict:
    """argument position -> the constant written there, for each argument
    clang's type string marks `I` (it must be a constant): 8 for a size or an
    alignment (`z`), 0 for anything else (a level, a register number)."""
    types = []
    position = 0
    while position < len(signature) and signature[position] != ".":
        match = TYPE_IN_SIGNATURE.match(signature, position)
        if match is None:
            return {}
        types.append(match)
        position = match.end()
    constants = {}
    for argument, match in enumerate(types[1:]):
        if match.group(1) == "I":
            constants[argument] = "8" if match.group(4) == "z" else "0"
    return constants


def builtins_of(written: dict) -> list:
    """Each builtin's call forms (its variants), as Operators. An argument
    clang's type string marks as a constant is written as one, and takes no
    holder."""
    operators = []
    for entry in written["builtins"]:
        constants = constant_arguments(entry["signature"])
        for variant in entry["variants"]:
            spelling = variant["spelling"]
            operands = list(variant["operands"])
            for argument in sorted(constants, reverse=True):
                if argument < len(operands):
                    spelling = re.sub(r"\b" + operands[argument] + r"\b", constants[argument], spelling, count=1)
                    del operands[argument]
            operators.append(Operator("c", variant["name"], spelling, tuple(operands), variant["source"]))
    return operators


def holders_for(operator, kept_positions: list, holders: tuple, full: bool) -> list:
    """The holder positions to cross over this operator's slots: every kept
    holder when `full` and the operator has at most two slots, the small set
    when `full` and it has three; otherwise the small sets, by slot count."""
    slots = len(mask_code.slots_of(operator))
    if full and slots <= 2:
        return kept_positions
    by_spelling = {holders[p].spelling: p for p in kept_positions}
    if slots <= 2 or (full and slots == 3):
        chosen = SMALL
    elif slots <= 5:
        chosen = SMALLER
    else:
        chosen = SMALLEST
    return [by_spelling[s] for s in chosen if s in by_spelling]


def cells_for(operators: list, holders: tuple, kept: list, full: bool, read=None) -> list:
    """Every operator's cells over the holders holders_for chooses; then, for
    an operator the reading gave signatures, each signature not among them
    (its holders found by spelling among the holders the grid can hold)."""
    cells = []
    for position, operator in enumerate(operators):
        chosen = holders_for(operator, kept, holders, full)
        for combo in itertools.product(chosen, repeat=len(mask_code.slots_of(operator))):
            cells.append(mask_code.Cell(position, tuple(combo)))
    if read is None:
        return cells
    position_of = {}
    for position in kept + list(read.kept_added):
        position_of[holders[position].spelling] = position
    present = set(cells)
    for position, operator in enumerate(operators):
        made = read.by_operator.get((operator.name, operator.spelling))
        if made is None:
            continue
        for signature in made.signatures:
            if any(spelling not in position_of for spelling in signature):
                continue
            cell = mask_code.Cell(position, tuple(position_of[spelling] for spelling in signature))
            if cell in present:
                continue
            present.add(cell)
            cells.append(cell)
    return cells


def not_judged(written: dict) -> list:
    """The forms forms_of leaves out, each with why."""
    return [{"name": e["name"], "template": e["spelling"],
             "why": "holds C++'s `::`; clang 21 did not finish such a held cell in C mode (run elv2_l63)"}
            for e in written["forms"] if NOT_JUDGED_IN_C in e["spelling"]]


def summarize(operators: list, holders: tuple, cells: list, verdicts: dict) -> list:
    """Per operator: cells, accepted, every accepted holder combination, and
    the refusals by their words with a count."""
    per = {}
    for cell in cells:
        verdict = verdicts.get(cell)
        entry = per.setdefault(cell.operator, {"cells": 0, "accepted": 0, "accepted_holders": [], "refusals": {}})
        entry["cells"] += 1
        if verdict is None:
            entry["unfinished"] = entry.get("unfinished", 0) + 1
            continue
        if verdict.accepted:
            entry["accepted"] += 1
            entry["accepted_holders"].append([holders[h].spelling for h in cell.holders])
        else:
            words = verdict.evidence.split(": ", 1)[-1]
            entry["refusals"][words] = entry["refusals"].get(words, 0) + 1
    rows = []
    for position, operator in enumerate(operators):
        entry = per.get(position, {"cells": 0, "accepted": 0, "accepted_holders": [], "refusals": {}})
        refusals = sorted(entry["refusals"].items(), key=lambda item: -item[1])
        if any("undeclared library function" in words for words, _count in refusals):
            # clang names a library function's missing declaration only at its
            # first use in a file, so every later cell of it would read as
            # accepted: none of its cells is a verdict
            entry["accepted"] = 0
            entry["accepted_holders"] = []
            refusals = [("needs its declaring header: clang, call to undeclared library function", entry["cells"])]
        elif any("call to undeclared function" in words for words, _count in refusals):
            # the same for any name clang does not know: the first call declares
            # it, so the later cells read as accepted (`typeid(a)`, run elv2_l66)
            entry["accepted"] = 0
            entry["accepted_holders"] = []
            refusals = [("not GNU C: clang, call to undeclared function", entry["cells"])]
        rows.append({"position": position, "name": operator.name, "template": operator.spelling,
                     "slots": list(mask_code.slots_of(operator)), "cells": entry["cells"],
                     "accepted": entry["accepted"], "accepted_holders": entry["accepted_holders"],
                     "unfinished": entry.get("unfinished", 0),
                     "refusals": [{"words": w, "count": c} for w, c in refusals[:12]],
                     "distinct_refusals": len(refusals)})
    return rows


def judge_pass(label: str, operators: list, holders: tuple, kept: list, full: bool, small: bool, work: str,
               evidence: str, declarations: tuple, read=None) -> Judged:
    if small:
        operators = operators[:40]
    cells = cells_for(operators, holders, kept, full, read)
    directory = os.path.join(work, label)
    os.makedirs(directory, exist_ok=True)
    start = time.time()
    print(f"[{label}] {len(operators)} operators, {len(cells)} cells", flush=True)
    # Every cell is asked of clang again. Until PseudoCoup is done, no past
    # answer is taken as correct (the owner, 2026-10-16: "until PseudoCoup is
    # completed, i dont want to assume that our past answers are correct");
    # the past answers are read only to set the new ones beside them (the owner,
    # 2026-10-14: "it can easily generate a new list and it can validate the
    # past findings").
    past = mask_code.knowns("c", cells, tuple(operators), holders)
    verdicts = mask_code.judge("c", cells, tuple(operators), holders, directory, f"{evidence} {label}".strip(),
                               workers=4, declarations=declarations)
    mask_code.record_knowns("c", verdicts, tuple(operators), holders)
    beside = beside_past(verdicts, past, tuple(operators), holders)
    rows = summarize(operators, holders, cells, verdicts)
    accepted_cells = sum(row["accepted"] for row in rows)
    accepted_operators = sum(1 for row in rows if row["accepted"])
    print(f"[{label}] {accepted_cells} of {len(cells)} cells accepted; {accepted_operators} of {len(operators)} "
          f"operators with at least one; all {len(verdicts)} asked now; {beside['answered_before']} of them answered "
          f"before: {beside['same']} the same, {beside['changed']} changed; {time.time() - start:.0f} s", flush=True)
    judged_pass = Judged(label, tuple(operators), tuple(cells), verdicts, rows, beside)
    return judged_pass


def beside_past(verdicts: dict, past: dict, operators: tuple, holders: tuple) -> dict:
    """The new answers set beside the past ones: how many cells had a past
    answer, how many got the same answer now, and the first cells whose answer
    changed, each by its operator and holders."""
    answered_before = 0
    same = 0
    changed = []
    for cell, verdict in verdicts.items():
        before = past.get(cell)
        if before is None:
            continue
        answered_before += 1
        if before.accepted == verdict.accepted:
            same += 1
        else:
            changed.append(cell)
    examples = []
    for cell in changed[:20]:
        spellings = []
        for position in cell.holders:
            spellings.append(holders[position].spelling)
        operator = operators[cell.operator]
        examples.append({"operator": operator.name, "template": operator.spelling, "holders": spellings,
                         "accepted_before": past[cell].accepted, "accepted_now": verdicts[cell].accepted})
    found = {"answered_before": answered_before, "same": same, "changed": len(changed), "changed_examples": examples}
    return found


def never_written_kinds(written: dict) -> set:
    """The kinds a program never writes, from c.json's left-out list: every
    entry of the kind left out because its code writes no text, and no form
    of it kept."""
    form_kinds = {entry["name"].split(".")[0] for entry in written["forms"]}
    reasons = {}
    for entry in written["left_out"]:
        reasons.setdefault(entry["name"].split(".")[0], []).append(entry["reason"])
    never = {kind for kind, kind_reasons in reasons.items()
             if kind not in form_kinds and all(r.startswith("a program never writes it") for r in kind_reasons)}
    never |= {"ImplicitCastExpr", "ConstantExpr", "FullExpr", "ExprWithCleanups"}
    return never


def parsed_node_c(trees: dict, function_name: str, never_written: set, operator) -> tuple:
    """(node, why): the node clang parsed one held cell's operator as, or None
    and why not. The expression form through `p->result = (...)` and its one
    parenthesis, a statement as the function's first statement, a builtin's
    call through `(void)(...)`."""
    function = trees.get(function_name)
    if function is None:
        return (None, "no such function in the tree")
    body = function["inner"][-1]
    if mask_code.is_statement(operator):
        first = mask_code.through(body["inner"][0], never_written)
        return (first, None)
    if mask_code.is_builtin_call(operator):
        node = mask_code.through(body["inner"][0], never_written)
        while node.get("kind") in ("CStyleCastExpr", "ParenExpr") and node.get("inner"):
            node = mask_code.through(node["inner"][0], never_written)
        return (node, None)
    assignment = mask_code.through(body["inner"][0], never_written)
    right_side = mask_code.through(assignment["inner"][-1], never_written)
    if right_side.get("kind") != "ParenExpr":
        return (None, f"not the standard form: {right_side.get('kind', 'unknown')}")
    written_kind = operator.name.split(".")[0]
    if written_kind in never_written:
        # an operator a program never writes (the read) is the first node of
        # its kind on the way down from the assignment's right side: clang
        # reads the parenthesis as a whole, so the read sits above it
        node = assignment["inner"][-1]
        while node is not None and node.get("kind") != written_kind:
            node = node["inner"][0] if node.get("inner") else None
        if node is None:
            return (None, f"no {written_kind} in the standard form")
        return (node, None)
    return (mask_code.through(right_side["inner"][0], never_written), None)


def callee_of(node: dict):
    """The name a call node calls, from its first declaration reference."""
    if node.get("kind") != "CallExpr" or not node.get("inner"):
        return None
    reference = node["inner"][0]
    while reference.get("inner") and reference.get("kind") != "DeclRefExpr":
        reference = reference["inner"][0]
    return (reference.get("referencedDecl") or {}).get("name")


# The size-or-alignment traits' spellings, as clang's dump writes them
# (JSONNodeDumper writes getTraitSpelling, which is TokenKinds.def's first
# argument of the trait's line).
TOKEN_KINDS = "clang/include/clang/Basic/TokenKinds.def"
TRAIT_LINE = re.compile(r"^(?:CXX11_)?UNARY_EXPR_OR_TYPE_TRAIT\((\w+),\s*(\w+),", re.M)


def trait_spellings() -> dict:
    """UnaryExprOrTypeTrait entry -> its spelling in clang's dump."""
    path = clang_reader.declaring_file_path(clang_reader.CHECKOUT, TOKEN_KINDS)
    with open(path, encoding="utf-8") as declaring:
        text = declaring.read()
    return {entry: spelling for spelling, entry in TRAIT_LINE.findall(text)}


def bare_operator(operator) -> str:
    """The template with its placeholders taken out: `a *= b` -> `*=`."""
    written = operator.spelling
    for placeholder in operator.operands:
        written = re.sub(r"\b" + placeholder + r"\b", "", written)
    return written.replace(" ", "")


def read_back(operator, node: dict, nodes: dict, spellings: dict) -> tuple:
    """(as written?, what was compared). As written: the kind clang built is
    the written kind or a kind StmtNodes.td derives from it (a *= b is a
    CompoundAssignOperator, which derives from BinaryOperator), and what the
    dump records of the entry agrees with the template: the opcode, prefix or
    postfix, the trait, arrow or dot, a type or a value as the argument."""
    written_kind, _, entry = operator.name.partition(".")
    kind = node.get("kind", "unknown")
    if written_kind not in clang_reader.chain_of(kind, nodes):
        return (False, "kind")
    compared = ["kind"]
    if "opcode" in node:
        compared.append("opcode")
        if bare_operator(operator) != node["opcode"]:
            return (False, "+".join(compared))
    if "isPostfix" in node:
        compared.append("prefix or postfix")
        postfix = operator.spelling.lstrip().startswith(tuple(operator.operands)) if operator.operands else False
        if node["isPostfix"] != postfix:
            return (False, "+".join(compared))
    if kind == "UnaryExprOrTypeTraitExpr" and entry:
        compared.append("trait")
        if node.get("name") != spellings.get(entry):
            return (False, "+".join(compared))
        compared.append("type or value")
        if ("argType" in node) != any(p in mask_code.TYPE_PLACEHOLDERS for p in operator.operands):
            return (False, "+".join(compared))
    if kind == "AtomicExpr" and entry:
        compared.append("atomic operation")
        if "AO" + node.get("name", "") != entry:
            return (False, "+".join(compared))
    if "castKind" in node and entry:
        compared.append("cast kind")
        if node["castKind"] != entry:
            return (False, "+".join(compared))
    if "isArrow" in node:
        compared.append("arrow or dot")
        if node["isArrow"] != ("->" in operator.spelling):
            return (False, "+".join(compared))
    return (True, "+".join(compared))


SIZE_SUFFIX = re.compile(r"_(1|2|4|8|16)$")


def kinds_pass(label: str, operators: list, holders: tuple, rows: list, written: dict, work: str,
               declarations: tuple) -> list:
    """One accepted cell per operator, read back through clang's syntax tree."""
    cells = []
    for row in rows:
        if not row["accepted"]:
            continue
        spellings = row["accepted_holders"][0]
        by_spelling = {h.spelling: p for p, h in enumerate(holders)}
        cells.append(mask_code.Cell(row["position"], tuple(by_spelling[s] for s in spellings)))
    directory = os.path.join(work, label)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "kinds.c")
    mask_code.write_cells("c", tuple(operators), holders, cells, path, declarations)
    command = mask_code.JUDGE_COMMAND["c"].split() + mask_code.KIND_COMMAND_TAIL.split() + [path]
    with open(path + ".ast.json", "w") as tree_file, open(path + ".diag", "w") as diagnostics:
        subprocess.run(command, stdout=tree_file, stderr=diagnostics, check=False)
    trees = mask_code.read_syntax_trees(path + ".ast.json")
    never_written = never_written_kinds(written)
    nodes = clang_reader.read_clang_stmt_nodes(clang_reader.CHECKOUT, clang_reader.STMT_NODES)
    spellings = trait_spellings()
    out = []
    for cell in cells:
        operator = operators[cell.operator]
        key = f"{cell.operator}_{'_'.join(str(h) for h in cell.holders)}"
        node, why = parsed_node_c(trees, f"op_{key}", never_written, operator)
        row = {"position": cell.operator, "name": operator.name, "template": operator.spelling,
               "holders": [holders[h].spelling for h in cell.holders]}
        if node is None:
            row.update({"parsed_as": why, "detail": None, "parsed_as_written": False, "compared": None})
            out.append(row)
            continue
        kind = node.get("kind", "unknown")
        detail = node.get("opcode") or node.get("name") or callee_of(node)
        if mask_code.is_statement(operator):
            written_kind = operator.name.split(".")[0]
            # since PCHQ log 402 `break;` sits behind an `if` in a `for (;;)`,
            # and `goto m;` behind an `if`, so each jump goes over reached code
            # (a do-while held `break;` in log 399, a bare `for (;;)` before);
            # since log 405 every statement that jumps does; since log 424 the
            # contexts and the jumps are read from the record (ROUTING)
            held_inside = written_kind in mask_code.ROUTING.contexts or written_kind in mask_code.ROUTING.jumps
            if held_inside and kind in ("ForStmt", "IfStmt", "SwitchStmt"):
                kind = written_kind + " (inside the held loop or switch)"
            as_written, compared = (kind.split(" ")[0] == written_kind, "kind")
        elif mask_code.is_builtin_call(operator) and kind != "CallExpr" and not operator.name.startswith("CallExpr."):
            # an atomic builtin, which clang builds as an AtomicExpr
            as_written, compared = read_back(operator, node, nodes, spellings)
        elif mask_code.is_builtin_call(operator):
            callee = callee_of(node)
            as_written = kind == "CallExpr" and callee is not None and operator.name == "CallExpr.BI" + callee
            compared = "kind+callee"
            asked = operator.name[len("CallExpr.BI"):]
            row["kept_as"] = callee
            row["same_builtin_other_size"] = bool(
                callee and not as_written and SIZE_SUFFIX.sub("", asked) == SIZE_SUFFIX.sub("", callee))
        else:
            as_written, compared = read_back(operator, node, nodes, spellings)
        row.update({"parsed_as": kind, "detail": detail, "parsed_as_written": as_written, "compared": compared})
        out.append(row)
    print(f"[{label}] {sum(1 for o in out if o['parsed_as_written'])} of {len(out)} read back as written", flush=True)
    return out


# Every accepted cell read back, in files of this many cells: clang's syntax
# tree of one held cell is about 10 KB as JSON, so a file's tree is tens of MB.
VARIANT_CELLS_PER_FILE = 4000


def type_of(node: dict):
    """The type clang gives a node, as the program names it."""
    return (node.get("type") or {}).get("qualType")


def operand_nodes(node: dict) -> list:
    """The nodes an operator node is applied to: every node under it, but a
    call's callee."""
    inner = node.get("inner", [])
    if node.get("kind") == "CallExpr":
        return inner[1:]
    return inner


def received(operand: dict) -> tuple:
    """(the type the operator receives, the conversions clang added on the
    way, outermost first, and the type before them)."""
    conversions = []
    node = operand
    while node.get("kind") == "ImplicitCastExpr" and node.get("inner"):
        conversions.append(node.get("castKind"))
        node = node["inner"][0]
    return (type_of(operand), conversions, type_of(node))


def variant_of(node: dict) -> dict:
    """What clang made of one accepted cell: the kind, the types the operator
    receives after clang's own conversions, the conversions, the types before
    them, and the type it answers. A variant is the kind, what it receives
    and what it answers; the conversions are other operators clang applies
    first."""
    operands = [received(o) for o in operand_nodes(node)]
    if node.get("kind") == "UnaryExprOrTypeTraitExpr" and "argType" in node:
        operands = [(node["argType"].get("qualType"), [], node["argType"].get("qualType"))]
    variant = {"kind": node.get("kind"), "receives": [o[0] for o in operands],
               "conversions": [o[1] for o in operands], "before": [o[2] for o in operands],
               "answers": type_of(node)}
    for extra in ("opcode", "castKind", "computeLHSType", "computeResultType", "name"):
        if extra in node:
            value = node[extra]
            variant[extra] = value.get("qualType") if isinstance(value, dict) else value
    return variant


def variants_pass(label: str, operators: list, holders: tuple, rows: list, written: dict, work: str,
                  declarations: tuple) -> list:
    """Every accepted cell of every expression and builtin read back through
    clang's syntax tree: per operator, the distinct variants clang makes of
    it, each with the holder combinations that make it."""
    never_written = never_written_kinds(written)
    cells = []
    for row in rows:
        operator = operators[row["position"]]
        if mask_code.is_statement(operator):
            continue
        by_spelling = {h.spelling: p for p, h in enumerate(holders)}
        for spellings in row["accepted_holders"]:
            cells.append(mask_code.Cell(row["position"], tuple(by_spelling[s] for s in spellings)))
    directory = os.path.join(work, label)
    os.makedirs(directory, exist_ok=True)
    per_operator = {}
    unread = 0
    for start in range(0, len(cells), VARIANT_CELLS_PER_FILE):
        chosen = cells[start:start + VARIANT_CELLS_PER_FILE]
        path = os.path.join(directory, f"variants_{start // VARIANT_CELLS_PER_FILE:03d}.c")
        mask_code.write_cells("c", tuple(operators), holders, chosen, path, declarations)
        command = mask_code.JUDGE_COMMAND["c"].split() + mask_code.KIND_COMMAND_TAIL.split() + [path]
        with open(path + ".ast.json", "w") as tree_file, open(path + ".diag", "w") as diagnostics:
            subprocess.run(command, stdout=tree_file, stderr=diagnostics, check=False)
        trees = mask_code.read_syntax_trees(path + ".ast.json")
        os.remove(path + ".ast.json")
        for cell in chosen:
            operator = operators[cell.operator]
            key = f"{cell.operator}_{'_'.join(str(h) for h in cell.holders)}"
            node, _why = parsed_node_c(trees, f"op_{key}", never_written, operator)
            if node is None:
                unread += 1
                continue
            variant = variant_of(node)
            conversions = variant.pop("conversions")
            variant.pop("before")
            found = per_operator.setdefault(cell.operator, {})
            identity = json.dumps(variant, sort_keys=True)
            found.setdefault(identity, []).append(
                {"holders": [holders[h].spelling for h in cell.holders], "conversions": conversions})
        del trees
    out = []
    for position in sorted(per_operator):
        operator = operators[position]
        variants = [dict(json.loads(identity), cells=made) for identity, made in per_operator[position].items()]
        variants.sort(key=lambda v: -len(v["cells"]))
        out.append({"position": position, "name": operator.name, "template": operator.spelling,
                    "cells": sum(len(v["cells"]) for v in variants), "variants": variants})
    total = sum(len(o["variants"]) for o in out)
    print(f"[{label}] {len(cells)} accepted cells read back, {unread} unread; {total} distinct variants "
          f"over {len(out)} operators", flush=True)
    return out
