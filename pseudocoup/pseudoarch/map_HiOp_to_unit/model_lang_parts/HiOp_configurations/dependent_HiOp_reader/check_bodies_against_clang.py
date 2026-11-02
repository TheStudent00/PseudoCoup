"""check_bodies_against_clang -- dependent_HiOp_reader's step 3 answer
(out/bodies.json) checked against clang's own dump of its control-flow
builder, on the tower, and against two hand tables. Plan node
Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/
node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/
node_0_0_0_0_2_4_2_dependent_HiOp_reader, section 3.1
("Its checks"). out/ is the reader's: Research/extract_lang_vocabulary/dependent_HiOp_reader/out.

A listing is one written form of a HiOp, as
Research/extract_lang_vocabulary/mask/gnu17/kinds_forms.json lists it (and
label_address.json beside it, for `&&m`); its parts are the letters of its
`template`. For each part the reader says where clang's control-flow builder
runs it (tested, behind the branch, run again before the test, before, no
branch, not added) and whether it is a body. This check asks clang where it
runs each part, and compares.

    python3 check_bodies_against_clang.py <work folder>     inside a run; clang 21.1.8 on PATH

1. The command. The first step finds which form of asking clang prints its
   builder's dump (the analyzer's `debug.DumpCFG`), trying in order the forms
   of DUMP_COMMANDS on a probe program; the first whose output holds an
   (ENTRY) and an (EXIT) block is used. When none does, the check stops and
   says so.

2. The programs, one or more per listing, in Dee's examples' form:

       int inert_0(void); ... int inert_<n>(void);     declared, never defined
       void f(void) { inert_0(); <the listing>; inert_<n>(); }

   - each value letter, in order, an inert call: `a` is `inert_1()`, `b`
     `inert_2()`, and so on; a letter that stands as a statement keeps the
     listing's own `;`, so `b;` is `inert_2();`;
   - each type letter a type of its own: `T` int, `U` long, `V` short, `W`
     char; each name letter itself (`m`);
   - an expression listing used as a statement (`<listing>;`) and stored
     (`int r = (<listing>);`, in parentheses, so `a , b` stays one
     expression and is not read as two declarators); `a && b` and `a || b`
     also as an `if` test (`if (<listing>) inert_<n>();`);
   - `switch (a) b;` also with a label in its body: `b` as `default: b;`
     (the DefaultStmt listing) and as `case 0: b;` (the CaseStmt listing, its
     value the constant 0): a switch runs its body only through its labels,
     and links its block to a case label's (VisitCaseStmt), a `default:`
     taking the place of the code after it;
   - `return a;` in `int f(void)`: a void function returns no value;
   - when clang refuses a program, it is tried again with the first letter
     `x`, declared `int x;` first (an lvalue: `a = b`, `a++`, `&a`); then,
     for a listing with type letters, with `U` of `T`'s type (`_Generic(T, U:
     a)` needs an association of the controlling type: `T` int, `U` int, `V`
     long, `W` short); refused each time, that program is not checked, with
     clang's first error.

3. Which listings: every listing of kinds_forms.json and label_address.json
   that clang parsed as written and that has a value letter (a to h); the
   rest are counted with the reason. Two programs of kinds the reader says
   branch and no GNU C listing holds are added (EXTRA_PROGRAMS).

4. Reading the dump (CFG.cpp's print_block): a block starts at `[B<n>]` (or
   `[B<n> (ENTRY)]`, `(EXIT)`, `(INDIRECT GOTO DISPATCH)`, `(NORETURN)`); its
   numbered lines are its elements; `T:` its terminator; `Preds` and `Succs`
   its links, `NULL` a link to no block. A part's block is the block of the
   element that is its inert call's name (`inert_2`), or `x`. The branch
   block of a listing is the block whose terminator its kind writes as
   TERMINATOR_WRITTEN says (CFGBlockTerminatorPrint, CFG.cpp lines 5628 to
   5726).

5. Where a part runs in the dump: the reader's own rule 17
   (dependent_HiOp_reader.place_of) over the dump's blocks and links, the
   ENTRY block its start and the EXIT block its end:
     tested: in the branch block;
     run again before the test: in a block reached from the branch block
       that links back to it;
     behind the branch: every chain of links from ENTRY to its block passes
       the branch block, and some chain to it does not pass the join (the
       nearest block every chain of links from the branch block to EXIT
       passes);
     before: the branch block is reached from its block, and its block is not
       reached from the branch block;
     after the join: reached from the branch block, and not behind it;
     not reached: none of these.
   For a listing the reader says makes no branch: "no branch" when no block
   of the dump has two or more links; a part in no block is "not added".
   The inert calls before and after the listing are classified by the same rule,
   as a check of the rule itself. The rule places blocks, not the order
   inside one: the call before a listing whose HiOp starts with its test
   (`if`, `switch`, `?:`, `&&`, `||`) stands in the test's block, so it reads
   "tested"; and after a loop with no test, the call after is "not reached".

6. Compared part by part: the reader's place against the dump's; and the
   body the reader's rule 20 gives from the dump's place (the part written as
   the reader says) against the reader's body.

7. The hand tables, part by part:
   - INERT_PART_ROLES (Projects/PseudoArch/map_HiOp_to_unit/DRY_mask_maker.py,
     kept there as INERT_PART_ROLES_BY_HAND since 
     standard-form began to take its routing from HiOp_configuration_solver's record):
     for a statement, its "body" parts are its bodies, every other role not;
     for the 4 expressions its "value" marks a holder that matters, not "not
     a body", so they are set against the next table instead;
   - the by-hand abstract structure of the 8 listings (BY_HAND, typed here
     from : their bodies.

Writes out/bodies_check.json (each program, its dump, the parts compared) and
out/bodies_check_summary.txt (the counts with their wholes, every
difference with the dump's lines).
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dependent_HiOp_reader as reader  # noqa: E402
import check_against_clang as first_check  # noqa: E402
from PseudoArch.map_HiOp_to_unit import mask_maker as DRY_mask_maker  # noqa: E402

BODIES = os.path.join(reader.OUT, "bodies.json")
CHECKED = os.path.join(reader.OUT, "bodies_check.json")
SUMMARY = os.path.join(reader.OUT, "bodies_check_summary.txt")
CHECKED_FILES = ("kinds_forms.json", "label_address.json")

CLANG = ["clang", "-std=gnu17", "--target=riscv64-unknown-linux-gnu"]
DUMP_COMMANDS = (
    ("-fsyntax-only with -Xclang -analyze", CLANG + ["-fsyntax-only", "-Xclang", "-analyze", "-Xclang",
                                                     "-analyzer-checker=debug.DumpCFG"]),
    ("--analyze", CLANG + ["--analyze", "-Xclang", "-analyzer-checker=debug.DumpCFG", "-o", "{plist}"]),
    ("clang -cc1 -analyze", ["clang", "-cc1", "-std=gnu17", "-triple", "riscv64-unknown-linux-gnu", "-analyze",
                             "-analyzer-checker=debug.DumpCFG"]),
)
PROBE = "int inert_0(void);\nvoid f(void) { if (inert_0()) inert_0(); }\n"

# The fill (section 2).
INERT = "inert_{0}"
DECLARED = "int inert_{0}(void);"
FUNCTION = "{0} f(void) {{ {1}inert_0(); {2} {3}(); }}"
TYPE_FILLS = {"T": "int", "U": "long", "V": "short", "W": "char"}
TYPE_FILLS_OF_THE_CONTROLLING_TYPE = {"T": "int", "U": "int", "V": "long", "W": "short"}
LVALUE = "x"
LVALUE_DECLARED = "int x; "
VALUE_LETTERS = first_check.LETTERS["operand"]
ALL_LETTERS = first_check.PLACEHOLDERS + tuple(TYPE_FILLS)
RETURNS_A_VALUE = re.compile(r"^return\s+[a-h]\b")
STATEMENT_KINDS_END = ";"
AS_A_STATEMENT = "used as a statement"
STORED = "stored"
IN_AN_IF_TEST = "inside an if test"
PLAIN = "as listed"
WITH_A_LABEL = "with a label in its body (`default:`)"
WITH_A_CASE_LABEL = "with a label in its body (`case 0:`)"
LABEL_LISTING = "default: b;"
CASE_LABEL_LISTING = "case 0: b;"
SWITCH_LISTING = "switch (a) b;"
IF_TESTED = ("BinaryOperator.LAnd", "BinaryOperator.LOr")

# How the dump writes each kind's terminator (CFGBlockTerminatorPrint, CFG.cpp
# lines 5628 to 5726), as the start or end of its `T:` line.
TERMINATOR_WRITTEN = {
    "IfStmt": re.compile(r"^if "),
    "ForStmt": re.compile(r"^for \("),
    "WhileStmt": re.compile(r"^while "),
    "DoStmt": re.compile(r"^do \.\.\. while "),
    "SwitchStmt": re.compile(r"^switch "),
    "ConditionalOperator": re.compile(r" \? \.\.\. : \.\.\.$"),
    "BinaryConditionalOperator": re.compile(r" \? \.\.\. : \.\.\.$"),
    "BinaryOperator.LAnd": re.compile(r" && \.\.\.$"),
    "BinaryOperator.LOr": re.compile(r" \|\| \.\.\.$"),
    "ChooseExpr": re.compile(r"^__builtin_choose_expr\( "),
    "GCCAsmStmt": re.compile(r"\basm\b.*\bgoto\b"),
}
# Kinds the reader says make a branch that no GNU C listing holds (section 3).
EXTRA_PROGRAMS = (
    {"name": "ChooseExpr", "template": "__builtin_choose_expr(1, a, b)", "letters": ["a", "b"], "around": "{0};",
     "why": "no GNU C listing holds ChooseExpr (pass_a_forms.json's `__builtin_choose_expr(a, b, c)`: `accepted` 0"
            " of `cells` 64); its test must be a constant, so it is `1` here"},
    {"name": "GCCAsmStmt", "template": "__asm__ goto (\"\" : : : : m); a; m: ;", "letters": ["a"], "around": "{0}",
     "why": "no GNU C listing holds GCCAsmStmt; the reader says it makes a branch only as `asm goto`, with a"
            " label whose block is not the one after it (buildCFG skips that one), so a statement stands"
            " between"},
)

# The by-hand abstract structure of the 8 listings, in Dee's notation, and
# their bodies .
BY_HAND = {
    "a && b": ("HiOp[0](a): b", ["b"]),
    "a || b": ("HiOp[0](a): b", ["b"]),
    "a ? b : c": ("HiOp[0](a): b, HiOp[1]: c", ["b", "c"]),
    "a ?: b": ("HiOp[0](a): b", ["b"]),
    "for (a; b; c) d;": ("HiOp[0]: a, HiOp[1](b): d, HiOp[2]: c", ["a", "c", "d"]),
    "for (a; ; b) c;": ("HiOp[0]: a, HiOp[1](): c, HiOp[2]: b", ["a", "b", "c"]),
    "for (; a; b) c;": ("HiOp[0](a): c, HiOp[1]: b", ["b", "c"]),
    "for (;; a) b;": ("HiOp[0](): b, HiOp[1]: a", ["a", "b"]),
}
EXPRESSIONS_OF_THE_TABLE = ("a && b", "a || b", "a ? b : c", "a ?: b")

# Reading the dump (CFG.cpp's print_block).
BLOCK_HEADER = re.compile(r"^\s*\[B(\d+)(?: \(([A-Z ]+)\))?\]\s*$")
ELEMENT = re.compile(r"^\s*(\d+): (.*)$")
TERMINATOR = re.compile(r"^\s*T: (.*)$")
LINKS = re.compile(r"^\s*(Preds|Succs) \(\d+\):(.*)$")
MORE_LINKS = re.compile(r"^\s+((?:B\d+(?:\(Unreachable\))?|NULL)(?:\s+(?:B\d+(?:\(Unreachable\))?|NULL))*)\s*$")
LINK = re.compile(r"B(\d+)(?:\(Unreachable\))?|NULL")
LABEL_LINE = re.compile(r"^\s+(.+):\s*$")

AGREE = "agree"
DISAGREE = "disagree"
NOT_READ = "not read"


def main():
    work_folder = sys.argv[1]
    bodies = first_check.read_json(BODIES)
    command = command_that_dumps(work_folder)
    listings = listings_to_check(bodies)
    programs = every_program(listings)
    results = dumped_and_compared(programs, command, work_folder)
    oracles = hand_tables(bodies)
    write_bodies_check(results, listings, command, oracles)


# 1. The command


def command_that_dumps(work_folder: str) -> dict:
    """The first form of DUMP_COMMANDS whose output holds a dump; the check
    stops when none does."""
    os.makedirs(work_folder, exist_ok=True)
    path = os.path.join(work_folder, "probe.c")
    write_program(path, PROBE)
    tried = []
    for name, command in DUMP_COMMANDS:
        answer = asked_clang(command, "probe.c", work_folder)
        tried.append({"form": name, "exit": answer["exit"], "dumped": is_a_dump(answer["output"])})
        if is_a_dump(answer["output"]):
            found = {"form": name, "command": command, "tried": tried}
            return found
    print("no form of the command printed clang's dump of its control-flow builder; the check is not run")
    print(json.dumps(tried, indent=1))
    sys.exit(1)


def is_a_dump(output: str) -> bool:
    dumped = "(ENTRY)]" in output and "(EXIT)]" in output
    return dumped


def asked_clang(command: list, name: str, work_folder: str) -> dict:
    """clang's exit, and what it printed (the dump goes to its standard
    error)."""
    written = []
    for part in command:
        written.append(part.replace("{plist}", os.path.join(work_folder, name + ".plist")))
    finished = subprocess.run(written + [name], cwd=work_folder, capture_output=True, text=True)
    answer = {"exit": finished.returncode, "output": finished.stderr + finished.stdout,
              "first_error": first_check.first_error(finished.stderr)}
    return answer


def write_program(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as program_file:
        program_file.write(text)


# 3. Which listings


def listings_to_check(bodies: dict) -> dict:
    """Each listing of the checked files: with programs, or the reason it has
    none."""
    found = {"with_programs": [], "with_no_program": []}
    for file_name in CHECKED_FILES:
        for listing in bodies["by_file"][file_name]["listings"]:
            add_listing_to_check(found, file_name, listing)
    return found


def add_listing_to_check(found: dict, file_name: str, listing: dict) -> None:
    listing = dict(listing)
    listing["file"] = file_name
    why = why_no_program(listing)
    if why is None:
        found["with_programs"].append(listing)
        return
    found["with_no_program"].append({"listing": label_of(listing), "why": why})


def why_no_program(listing: dict):
    why = None
    if not listing["parsed_as_written"]:
        why = "clang did not parse it as written"
    elif not value_letters_of(listing["template"]):
        why = "it has no value letter: no part the builder runs"
    return why


def value_letters_of(template: str) -> list:
    found = []
    for letter in reader.placeholders_of(template):
        if letter in VALUE_LETTERS:
            found.append(letter)
    return found


def label_of(listing: dict) -> str:
    label = f"{listing.get('position')}: {listing['template']} ({listing['name']}, {listing.get('file', '')})"
    return label


# 2. The programs


def every_program(listings: dict) -> list:
    programs = []
    for listing in listings["with_programs"]:
        add_programs_of(programs, listing)
    for extra in EXTRA_PROGRAMS:
        programs.append(extra_program(extra))
    return programs


def add_programs_of(programs: list, listing: dict) -> None:
    """The listing as listed (a statement), or used as a statement and
    stored (an expression), `&&` and `||` also as an if test, and a switch
    also with a label in its body."""
    is_a_statement = statement_listing(listing)
    if is_a_statement:
        programs.append(program_of(listing, PLAIN, "{0}"))
    if not is_a_statement:
        programs.append(program_of(listing, AS_A_STATEMENT, "{0};"))
        programs.append(program_of(listing, STORED, "int r = ({0});"))
    if listing["name"] in IF_TESTED:
        programs.append(program_of(listing, IN_AN_IF_TEST, "if ({0}) {after}();"))
    if listing["template"] == SWITCH_LISTING:
        programs.append(switch_with_a_label(listing, WITH_A_LABEL, LABEL_LISTING))
        programs.append(switch_with_a_label(listing, WITH_A_CASE_LABEL, CASE_LABEL_LISTING))


def statement_listing(listing: dict) -> bool:
    """A listing whose kind StmtNodes.td does not declare as an expression."""
    found = listing["kind"] in statement_kinds()
    return found


def statement_kinds() -> list:
    kinds = reader.statement_kinds(reader.CHECKOUT)
    return kinds


def program_of(listing: dict, form: str, around: str) -> dict:
    letters = reader.placeholders_of(listing["template"])
    fills = fills_of(letters, False)
    made = {
        "listing": label_of(listing),
        "file": listing["file"],
        "position": listing["position"],
        "name": listing["name"],
        "template": listing["template"],
        "kind": listing["kind"],
        "form": form,
        "around": around,
        "letters": letters,
        "reader": reader_parts(listing),
        "reader_makes_a_branch": listing["listing_makes_a_branch"],
        "returns_a_value": RETURNS_A_VALUE.match(listing["template"]) is not None,
        "fills": fills,
    }
    return made


def switch_with_a_label(listing: dict, form: str, labelled: str) -> dict:
    """`switch (a) b;` with `b` labelled: `default: b;` or `case 0: b;`."""
    made = program_of(listing, form, "{0}")
    made["listing_used"] = listing["template"].replace("b;", labelled)
    return made


def extra_program(extra: dict) -> dict:
    made = {
        "listing": "not a GNU C listing: " + extra["template"] + " (" + extra["name"] + ")",
        "file": None,
        "position": None,
        "name": extra["name"],
        "template": extra["template"],
        "kind": extra["name"],
        "form": PLAIN,
        "around": extra["around"],
        "letters": extra["letters"],
        "reader": {},
        "reader_makes_a_branch": None,
        "returns_a_value": False,
        "fills": fills_of(extra["letters"], False),
        "extra_why": extra["why"],
    }
    return made


def reader_parts(listing: dict) -> dict:
    parts = {}
    for part in listing["parts"]:
        parts[part["letter"]] = {"place": part["place"], "body": part["body"], "written_as": part["written_as"],
                                 "getter": part.get("getter")}
    return parts


def fills_of(letters: list, first_as_an_lvalue: bool, types: dict = None) -> dict:
    """letter -> its fill (section 2): value letters inert calls in order, the
    first `x` when asked (the calls after it numbered from 1); type letters
    types; name letters themselves."""
    fills = {}
    number = 0
    if types is None:
        types = TYPE_FILLS
    for letter in letters:
        if first_as_an_lvalue and letter == letters[0] and letter in VALUE_LETTERS:
            fills[letter] = LVALUE
            continue
        number = add_fill(fills, letter, number, types)
    return fills


def add_fill(fills: dict, letter: str, number: int, types: dict) -> int:
    after = number
    if letter in VALUE_LETTERS:
        after = number + 1
        fills[letter] = INERT.format(after) + "()"
    if letter in types:
        fills[letter] = types[letter]
    if letter in first_check.NAME_LETTERS:
        fills[letter] = letter
    return after


def has_type_letters(letters: list) -> bool:
    found = False
    for letter in letters:
        if letter in TYPE_FILLS:
            found = True
    return found


def program_text(made: dict, fills: dict) -> str:
    """The program: the inert functions declared, then f with an inert call
    before the listing and one after."""
    count = inert_count(fills)
    filled = filled_listing(made.get("listing_used", made["template"]), fills)
    middle = made["around"].replace("{after}", INERT.format(count + 1)).replace("{0}", filled)
    declared = []
    for number in range(count + 3):
        declared.append(DECLARED.format(number))
    returned = "void"
    if made["returns_a_value"]:
        returned = "int"
    before = ""
    if LVALUE in fills.values():
        before = LVALUE_DECLARED
    last = INERT.format(count + 1)
    if made["form"] == IN_AN_IF_TEST:
        last = INERT.format(count + 2)
    text = "\n".join(declared) + "\n" + FUNCTION.format(returned, before, middle, last) + "\n"
    return text


def inert_count(fills: dict) -> int:
    count = 0
    for fill in fills.values():
        if fill.startswith("inert_"):
            count += 1
    return count


def filled_listing(written: str, fills: dict) -> str:
    """Each letter of a listing's `template` replaced by its fill, word for
    word."""
    pieces = []
    copied_up_to = 0
    for text, start, end in first_check.tokens_of(written):
        if text in fills:
            pieces.append(written[copied_up_to:start])
            pieces.append(fills[text])
            copied_up_to = end
    pieces.append(written[copied_up_to:])
    filled = "".join(pieces)
    return filled


# Asking clang, and comparing


def dumped_and_compared(programs: list, command: dict, work_folder: str) -> list:
    results = []
    number = 0
    for made in programs:
        number += 1
        results.append(dumped_and_compared_one(made, number, command, work_folder))
    return results


def dumped_and_compared_one(made: dict, number: int, command: dict, work_folder: str) -> dict:
    """One program: its dump, or clang's refusal; then with the first letter
    `x` when refused."""
    result = dict(made)
    result["refused"] = []
    answer = dumped(made, made["fills"], number, "", command, work_folder)
    if answer["exit"] != 0 and made["letters"]:
        result["refused"].append({"program": answer["program"], "first_error": answer["first_error"]})
        answer = dumped(made, fills_of(made["letters"], True), number, "_x", command, work_folder)
    if answer["exit"] != 0 and has_type_letters(made["letters"]):
        result["refused"].append({"program": answer["program"], "first_error": answer["first_error"]})
        types = TYPE_FILLS_OF_THE_CONTROLLING_TYPE
        answer = dumped(made, fills_of(made["letters"], False, types), number, "_t", command, work_folder)
    result.update(answer)
    if answer["exit"] != 0:
        result["checked"] = False
        return result
    result["checked"] = True
    result["blocks"] = blocks_of_a_dump(answer["output"])
    result["parts"] = parts_compared(result)
    return result


def dumped(made: dict, fills: dict, number: int, suffix: str, command: dict, work_folder: str) -> dict:
    name = f"program_{number:03d}{suffix}.c"
    text = program_text(made, fills)
    write_program(os.path.join(work_folder, name), text)
    answer = asked_clang(command["command"], name, work_folder)
    answer["program"] = text
    answer["fills_used"] = fills
    return answer


# 4. Reading the dump


def blocks_of_a_dump(output: str) -> dict:
    """B<n> -> its kind (ENTRY, EXIT, ...), label, elements, terminator,
    predecessors and successors (None for NULL), and its own lines."""
    blocks = {}
    current = None
    last_links = None
    for line in output.splitlines():
        current, last_links = read_dump_line(blocks, current, last_links, line)
    return blocks


def read_dump_line(blocks: dict, current, last_links, line: str) -> tuple:
    header = BLOCK_HEADER.match(line)
    if header is not None:
        current = "B" + header.group(1)
        blocks[current] = {"kind": header.group(2), "label": None, "elements": [], "terminator": None,
                           "preds": [], "succs": [], "lines": [line]}
        found = (current, None)
        return found
    if current is None or not line.strip():
        found = (current, last_links)
        return found
    block = blocks[current]
    block["lines"].append(line)
    last_links = read_block_line(block, line, last_links)
    found = (current, last_links)
    return found


def read_block_line(block: dict, line: str, last_links):
    element = ELEMENT.match(line)
    if element is not None:
        block["elements"].append(element.group(2))
        return None
    terminator = TERMINATOR.match(line)
    if terminator is not None:
        block["terminator"] = terminator.group(1).strip()
        return None
    links = LINKS.match(line)
    if links is not None:
        key = links.group(1).lower()
        block[key].extend(links_in(links.group(2)))
        return key
    more = MORE_LINKS.match(line)
    if more is not None and last_links is not None:
        block[last_links].extend(links_in(more.group(1)))
        return last_links
    label = LABEL_LINE.match(line)
    if label is not None and not block["elements"]:
        block["label"] = label.group(1).strip()
    return None


def links_in(text: str) -> list:
    found = []
    for link in LINK.finditer(text):
        found.append(block_name(link))
    return found


def block_name(link):
    name = None
    if link.group(1) is not None:
        name = "B" + link.group(1)
    return name


# 5. Where each part runs in the dump


def parts_compared(result: dict) -> dict:
    """letter -> the dump's place beside the reader's, for each part; and the
    inert calls before and after, as a check of the rule."""
    blocks = result["blocks"]
    graph = graph_of_a_dump(blocks)
    branch = branch_block(blocks, result)
    compared = {"branch_block": branch, "blocks_with_two_links": blocks_with_two_links(blocks), "by_letter": {},
                "before_and_after": {}}
    for letter in result["letters"]:
        compared["by_letter"][letter] = part_compared(result, letter, blocks, graph, branch, compared)
    add_before_and_after(compared, result, blocks, graph, branch)
    return compared


def graph_of_a_dump(blocks: dict) -> dict:
    graph = {"links": {}, "start": None, "end": None}
    for name, block in blocks.items():
        add_dump_block(graph, name, block)
    return graph


def add_dump_block(graph: dict, name: str, block: dict) -> None:
    targets = []
    for target in block["succs"]:
        if target is not None:
            targets.append(target)
    graph["links"][name] = targets
    if block["kind"] == "ENTRY":
        graph["start"] = name
    if block["kind"] == "EXIT":
        graph["end"] = name


def branch_block(blocks: dict, result: dict):
    """The block whose terminator is the listing's HiOp, as its kind writes it
    (TERMINATOR_WRITTEN); None when the kind writes none or no block has it."""
    pattern = TERMINATOR_WRITTEN.get(result["name"], TERMINATOR_WRITTEN.get(result["kind"]))
    found = None
    if pattern is None:
        return found
    for name, block in blocks.items():
        if block["terminator"] is not None and pattern.search(block["terminator"]) and found is None:
            found = name
    return found


def blocks_with_two_links(blocks: dict) -> list:
    found = []
    for name, block in blocks.items():
        if len(block["succs"]) >= 2 and block["kind"] not in ("ENTRY", "EXIT"):
            found.append(name)
    return found


def part_compared(result: dict, letter: str, blocks: dict, graph: dict, branch, compared: dict) -> dict:
    fill = result["fills_used"].get(letter, "")
    block = block_of_a_fill(blocks, fill)
    place = dump_place(graph, branch, block, compared["blocks_with_two_links"])
    read = result["reader"].get(letter, {})
    found = {
        "fill": fill,
        "dump_block": block,
        "dump_place": place,
        "reader_place": read.get("place"),
        "place": place_agreement(read.get("place"), place),
        "reader_body": read.get("body"),
        "body_from_the_dump": body_from_a_place(read.get("written_as"), place),
    }
    found["body"] = body_agreement(found["reader_body"], found["body_from_the_dump"])
    return found


def block_of_a_fill(blocks: dict, fill: str):
    """The block of the element that is the fill's name: `inert_2` for
    `inert_2()`, `x` for `x`."""
    name = fill.split("(")[0]
    found = None
    if not name:
        return found
    for block_name_, block in blocks.items():
        if name in block["elements"] and found is None:
            found = block_name_
    return found


def dump_place(graph: dict, branch, block, branching: list) -> str:
    """Section 5: the reader's rule 17 over the dump."""
    if block is None:
        place = reader.NOT_ADDED
        return place
    if branch is None and not branching:
        place = reader.NO_BRANCH
        return place
    if branch is None:
        place = "a branch the reader does not read: " + ", ".join(branching)
        return place
    place = reader.place_of(graph["links"], graph["start"], graph["end"], branch, block)
    return place


def place_agreement(reader_place, place: str) -> str:
    agreement = DISAGREE
    if reader_place is None or reader_place == "not read" or reader_place.startswith(reader.DIFFERS_BY_PATH):
        agreement = NOT_READ
    if reader_place == place:
        agreement = AGREE
    return agreement


def body_from_a_place(written_as, place: str):
    """The reader's rule 20, with the dump's place."""
    body = None
    if written_as == reader.AS_STATEMENT:
        body = True
    if written_as in (reader.AS_OPERAND, reader.AS_TYPE, reader.AS_NAME):
        body = written_as == reader.AS_OPERAND and place in reader.BODY_PLACES
    return body


def body_agreement(reader_body, body) -> str:
    agreement = DISAGREE
    if reader_body is None or body is None:
        agreement = NOT_READ
    if reader_body is not None and reader_body == body:
        agreement = AGREE
    return agreement


def add_before_and_after(compared: dict, result: dict, blocks: dict, graph: dict, branch) -> None:
    """The inert calls before and after the listing, placed by the same rule:
    "before" and "after the join" when there is a branch."""
    count = inert_count(result["fills_used"])
    last = count + 1
    if result["form"] == IN_AN_IF_TEST:
        last = count + 2
    for number in (0, last):
        fill = INERT.format(number) + "()"
        block = block_of_a_fill(blocks, fill)
        compared["before_and_after"][fill] = dump_place(graph, branch, block, compared["blocks_with_two_links"])


# 7. The hand tables


def hand_tables(bodies: dict) -> dict:
    listings = parsed_listings(bodies["by_file"]["kinds_forms.json"]["listings"])
    tables = {
        "inert_part_roles": against_inert_part_roles(listings),
        "by_hand": against_the_table_by_hand(listings),
    }
    return tables


def parsed_listings(listings: list) -> dict:
    """template -> the listing clang parsed as written."""
    found = {}
    for listing in listings:
        if listing["parsed_as_written"]:
            found[listing["template"]] = listing
    return found


def against_inert_part_roles(listings: dict) -> dict:
    """INERT_PART_ROLES part by part: a "body" part against the reader's body,
    every other role against not a body; the 4 expressions left to the table
    by hand."""
    compared = {"parts": [], "left_to_the_table_by_hand": []}
    for template, roles in DRY_mask_maker.INERT_PART_ROLES_BY_HAND.items():
        add_roles_compared(compared, template, roles, listings)
    return compared


def add_roles_compared(compared: dict, template: str, roles: dict, listings: dict) -> None:
    for letter, role in roles.items():
        part = reader_part(listings.get(template), letter)
        record = {"listing": template, "letter": letter, "role": role, "reader_body": part.get("body"),
                  "reader_place": part.get("place"), "reader_written_as": part.get("written_as")}
        if template in EXPRESSIONS_OF_THE_TABLE:
            compared["left_to_the_table_by_hand"].append(record)
            continue
        record["agree"] = (role == "body") == (part.get("body") is True)
        compared["parts"].append(record)


def reader_part(listing, letter: str) -> dict:
    found = {}
    if listing is None or not listing.get("read"):
        return found
    for part in listing["parts"]:
        if part["letter"] == letter:
            found = part
    return found


def against_the_table_by_hand(listings: dict) -> list:
    compared = []
    for template, (structure, bodies) in BY_HAND.items():
        listing = listings.get(template, {})
        read = listing.get("bodies")
        compared.append({"listing": template, "structure": structure, "bodies_by_hand": bodies,
                         "bodies_read": read, "N_by_hand": len(bodies), "N_read": listing.get("N"),
                         "agree": read == bodies, "parts": parts_written_short(listing)})
    return compared


def parts_written_short(listing: dict) -> list:
    found = []
    for part in listing.get("parts", []):
        found.append(f"{part['letter']}: {part.get('getter')}, written as {part['written_as']}, {part['place']},"
                     f" body {part['body']}")
    return found


# Writing


def write_bodies_check(results: list, listings: dict, command: dict, oracles: dict) -> None:
    counts = counted(results, listings)
    record = {
        "what": "dependent_HiOp_reader step 3 checked against clang's dump of its control-flow builder"
                " (debug.DumpCFG), and against INERT_PART_ROLES and the table of the 8 by hand",
        "clang": first_check.clang_version(),
        "command": command,
        "bodies_read": BODIES,
        "counts": counts,
        "listings_with_no_program": listings["with_no_program"],
        "oracles": oracles,
        "programs": results,
    }
    reader.write_json(record, CHECKED)
    lines = summary_lines(record, results)
    first_check.write_text(lines, SUMMARY)
    print("\n".join(lines))


def counted(results: list, listings: dict) -> dict:
    refused = listings_every_program_refused(results)
    counts = {"listings": len(listings["with_programs"]) + len(listings["with_no_program"]),
              "listings_checked_against_the_dump": listings_dumped(listings, refused),
              "listings_every_program_refused": refused,
              "listings_with_no_program": len(listings["with_no_program"]),
              "programs": len(results), "programs_dumped": 0, "programs_refused": 0,
              "places": new_tally(), "bodies": new_tally(), "by_listing": {}}
    for result in results:
        add_result_counts(counts, result)
    return counts


def listings_dumped(listings: dict, refused: dict) -> int:
    """The listings with programs, less those whose every program clang
    refused."""
    dumped = 0
    for listing in listings["with_programs"]:
        if label_of(listing) not in refused:
            dumped += 1
    return dumped


def listings_every_program_refused(results: list) -> dict:
    """listing -> clang's first error, for each listing whose every program
    clang refused, with the first letter as x too."""
    dumped = []
    refused = {}
    for result in results:
        if result["checked"]:
            add_once(dumped, result["listing"])
        if not result["checked"]:
            refused[result["listing"]] = result["first_error"]
    found = {}
    for listing, error in refused.items():
        if listing not in dumped:
            found[listing] = error
    return found


def add_once(items: list, item) -> None:
    if item not in items:
        items.append(item)


def new_tally() -> dict:
    tally = {AGREE: 0, DISAGREE: 0, NOT_READ: 0}
    return tally


def add_result_counts(counts: dict, result: dict) -> None:
    if not result["checked"]:
        counts["programs_refused"] += 1
        return
    counts["programs_dumped"] += 1
    listing = result["listing"]
    if listing not in counts["by_listing"]:
        counts["by_listing"][listing] = {"programs": 0, "places": new_tally(), "bodies": new_tally()}
    counts["by_listing"][listing]["programs"] += 1
    for part in result["parts"]["by_letter"].values():
        add_part_counts(counts, counts["by_listing"][listing], part)


def add_part_counts(counts: dict, by_listing: dict, part: dict) -> None:
    counts["places"][part["place"]] += 1
    counts["bodies"][part["body"]] += 1
    by_listing["places"][part["place"]] += 1
    by_listing["bodies"][part["body"]] += 1


def summary_lines(record: dict, results: list) -> list:
    counts = record["counts"]
    lines = [record["what"], f"clang: {record['clang']}", "command: " + " ".join(record["command"]["command"]),
             f"  (the form `{record['command']['form']}`; forms tried: {json.dumps(record['command']['tried'])})", ""]
    add_listing_count_lines(lines, record)
    add_program_count_lines(lines, counts)
    add_by_listing_lines(lines, counts)
    add_difference_lines(lines, results)
    add_before_and_after_lines(lines, results)
    add_extra_lines(lines, results)
    add_refused_lines(lines, results)
    add_oracle_lines(lines, record["oracles"])
    return lines


def add_listing_count_lines(lines: list, record: dict) -> None:
    counts = record["counts"]
    whole = counts["listings"]
    refused = counts["listings_every_program_refused"]
    dumped = counts["listings_checked_against_the_dump"]
    lines.append(f"listings of {', '.join(CHECKED_FILES)}: {whole}; checked against the dump {dumped} of {whole};"
                 f" not checked {whole - dumped} of {whole}:")
    lines.append(f"  {len(refused)}: clang refused every program of it, however it was filled:"
                 f" {'; '.join(refused)}")
    reasons = {}
    for kept in record["listings_with_no_program"]:
        reader.add_to_list(reasons, kept["why"], kept["listing"])
    for why, kept in reasons.items():
        lines.append(f"  {len(kept)}: {why}")
    lines.append("")


def add_program_count_lines(lines: list, counts: dict) -> None:
    whole = counts["programs"]
    lines.append(f"programs: {whole}; dumped {counts['programs_dumped']} of {whole}; refused by clang (each fill)"
                 f" {counts['programs_refused']} of {whole}")
    for what in ("places", "bodies"):
        tally = counts[what]
        parts = tally[AGREE] + tally[DISAGREE] + tally[NOT_READ]
        lines.append(f"  parts compared, {what}: {parts}; agree {tally[AGREE]} of {parts}; disagree"
                     f" {tally[DISAGREE]} of {parts}; not read by the reader {tally[NOT_READ]} of {parts}")
    lines.append("")


def add_by_listing_lines(lines: list, counts: dict) -> None:
    lines.append("by listing (programs; places agree/disagree/not read; bodies agree/disagree/not read):")
    for listing, by in counts["by_listing"].items():
        places = by["places"]
        bodies = by["bodies"]
        lines.append(f"  {by['programs']:2d}  places {places[AGREE]}/{places[DISAGREE]}/{places[NOT_READ]}"
                     f"  bodies {bodies[AGREE]}/{bodies[DISAGREE]}/{bodies[NOT_READ]}  {listing}")
    lines.append("")


def add_difference_lines(lines: list, results: list) -> None:
    """Every part whose place or body is not agreed, with the dump's lines of
    the branch block and the part's block."""
    count = 0
    for result in results:
        count += add_differences_of(lines, result)
    if count == 0:
        lines.append("parts where the reader and the dump differ: none")
    lines.append("")


def add_differences_of(lines: list, result: dict) -> int:
    count = 0
    if not result["checked"] or not result["letters"]:
        return count
    for letter, part in result["parts"]["by_letter"].items():
        if part["place"] == AGREE and part["body"] == AGREE:
            continue
        count += 1
        lines.append(f"difference: {result['listing']}, {result['form']}, part {letter} ({part['fill']}):"
                     f" reader {part['reader_place']} (body {part['reader_body']}); dump {part['dump_place']}"
                     f" (body {part['body_from_the_dump']}); place {part['place']}, body {part['body']}")
        lines.append("    program: " + result["program"].splitlines()[-1])
        add_dump_lines(lines, result, part)
    return count


def add_dump_lines(lines: list, result: dict, part: dict) -> None:
    shown = []
    for name in (result["parts"]["branch_block"], part["dump_block"]):
        if name is not None and name not in shown:
            shown.append(name)
            for line in result["blocks"][name]["lines"]:
                lines.append("    | " + line)


def add_before_and_after_lines(lines: list, results: list) -> None:
    """The rule checked on the inert calls around each listing with a branch:
    the one before is "before", the one after "after the join"."""
    seen = {}
    for result in results:
        if result["checked"] and result["parts"]["branch_block"] is not None:
            for fill, place in result["parts"]["before_and_after"].items():
                reader.add_to_list(seen, side_of(fill) + ": " + place, result["listing"] + ", " + result["form"])
    lines.append("the inert calls around a listing with a branch, placed by the same rule (it places blocks, not"
                 " the order inside one: the call before a HiOp that starts with its test stands in the test's"
                 " block):")
    for key, where_seen in seen.items():
        lines.append(f"  {key}: {len(where_seen)} programs")
    lines.append("")


def side_of(fill: str) -> str:
    side = "after"
    if fill == INERT.format(0) + "()":
        side = "before"
    return side


def add_extra_lines(lines: list, results: list) -> None:
    lines.append("kinds the reader says make a branch, held by no GNU C listing:")
    for result in results:
        if "extra_why" not in result:
            continue
        lines.append(f"  {result['listing']}: {result['extra_why']}")
        if not result["checked"]:
            lines.append(f"    refused: {result['first_error']}")
            continue
        lines.append(f"    the dump's branch block: {result['parts']['branch_block']}; blocks with two or more links:"
                     f" {reader.joined_or_none(result['parts']['blocks_with_two_links'], ', ')}")
        for letter, part in result["parts"]["by_letter"].items():
            lines.append(f"    {letter} ({part['fill']}): {part['dump_place']}")
        for line in result["output"].splitlines():
            if line.strip():
                lines.append("    | " + line)
    lines.append("")


def add_refused_lines(lines: list, results: list) -> None:
    lines.append("programs clang refused however they were filled (not checked):")
    for result in results:
        if not result["checked"]:
            lines.append(f"  {result['listing']}, {result['form']}: {result['first_error']}")
    lines.append("")


def add_oracle_lines(lines: list, oracles: dict) -> None:
    roles = oracles["inert_part_roles"]
    agreeing = 0
    for part in roles["parts"]:
        if part["agree"]:
            agreeing += 1
    whole = len(roles["parts"]) + len(roles["left_to_the_table_by_hand"])
    lines.append(f"INERT_PART_ROLES: {whole} parts; {len(roles['parts'])} of {whole} are statements' parts, compared"
                 f" with the reader's bodies: agree {agreeing} of {len(roles['parts'])}, differ"
                 f" {len(roles['parts']) - agreeing} of {len(roles['parts'])}; the other"
                 f" {len(roles['left_to_the_table_by_hand'])} of {whole} are the 4 expressions' parts, set against"
                 f" the table by hand instead")
    for part in roles["parts"]:
        if not part["agree"]:
            lines.append(f"  differs: {part['listing']} {part['letter']}: INERT_PART_ROLES {part['role']}; reader"
                         f" body {part['reader_body']} ({part['reader_written_as']}, {part['reader_place']})")
    table = oracles["by_hand"]
    agreeing = 0
    for row in table:
        if row["agree"]:
            agreeing += 1
    lines.append(f"the table of the 8 by hand: {len(table)} rows; agree {agreeing} of {len(table)}; differ"
                 f" {len(table) - agreeing} of {len(table)}")
    for row in table:
        mark = "DIFFERS"
        if row["agree"]:
            mark = "agree"
        lines.append(f"  {mark:7s} {row['listing']:18s} {row['structure']:40s} by hand {', '.join(row['bodies_by_hand'])}"
                     f" (N {row['N_by_hand']}); read {', '.join(row['bodies_read'] or [])} (N {row['N_read']})")
        if not row["agree"]:
            for part in row["parts"]:
                lines.append(f"      {part}")


if __name__ == "__main__":
    main()
