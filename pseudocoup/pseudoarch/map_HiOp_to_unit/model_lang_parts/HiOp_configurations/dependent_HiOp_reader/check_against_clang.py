"""check_against_clang -- dependent_HiOp_reader's answer (out/places.json)
checked against clang's own checker, on the tower: step 2, a brute force
bounded at depth 2. Plan node
Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoir/
node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/
node_0_0_0_0_2_4_2_dependent_HiOp_reader, section 4.
out/ is the reader's: Research/extract_lang_vocabulary/dependent_HiOp_reader/out.

A dependent-HiOp is a statement or expression clang refuses unless
something stands around it or with it in the function (`break;` inside a
loop or a switch, `goto m;` with the label `m:`); its places are the kinds of
statement the reader says it may stand inside. A listing is one written form
of a HiOp, as Research/extract_lang_vocabulary/mask/gnu17/kinds_forms.json
lists it (and label_address.json, for `&&m`).

    python3 check_against_clang.py <work folder>     inside a run; clang 21.1.8 on PATH

A position is one body of a GNU C statement listing with a body: `{ a; b; }`
has two, `while (a) b;` one. Every program is `void f(int x) { ... }` (with
`void g(int *);` before it where a place needs it), compiled alone with
`clang -std=gnu17 --target=riscv64-unknown-linux-gnu -fsyntax-only`:

    1. chains, for each dependent the reader places by the statements around
       it: depth 0, the dependent alone; depth 1, in each position; depth 2,
       in each position inside each position
    2. two of it in one switch, for each dependent a rule over one switch is
       about
    3. the label, for each dependent that needs a label of the same name:
       the label missing, before it, after it; the label in each position
       with the dependent at the top; the dependent in each position with the
       label at the top
    4. the address, for each dependent that needs some label's address: with
       `&&m` in the function, without
    5. the places a jump may not enter, for each dependent that is a jump:
       for each of GNU C's 4 places, the label inside with the jump outside;
       the jump inside with the label outside; both inside

What the reader predicts:

    1. accepted when a statement of the chain is one of the dependent's
       places, with none after it of a kind that stops the place being
       passed on; else refused (so depth 0 is refused)
    2. refused
    3. accepted when the label stands anywhere in the function; refused when
       it is missing
    4. accepted with `&&m`, refused without
    5. the label inside: refused when the place has an in-note that the jump's
       refusal tests and that is not only a warning in C; the jump inside:
       not read; both inside: accepted (nothing is entered)

For a refusal it predicts, the reader names the refusal; clang's first error
is matched against that refusal's words (DiagnosticSemaKinds.td).

Every listing comes from kinds_forms.json or label_address.json:
  - a statement listing: its kind is not an expression in StmtNodes.td
  - a dependent: one of the 8 listings the reader read
  - a position: a statement listing clang parsed as written, not a
    dependent, with a body; one per body
  - the label `m: ;` and `&&m` in programs: the listings of the kinds the
    reader says the dependents need
Typed here, and why:
  - the 4 places, which no listing is (a declaration, and the statement
    expression, which kinds_forms.json leaves out): a variable length array
    `int v[x];`, a variable length array typedef `typedef int t[x];`, a
    variable with `__attribute__((cleanup(g)))` (`void g(int *);` declared
    first), and a statement expression `({ ... });`. Each is keyed by the
    in-note the reader reads for it.
  - `p` for the operand of `goto *a;`, declared `void *p = &&m;` (or `= 0`):
    clang converts that operand to `const void *` (SemaStmt.cpp 3252 to
    3262), and `x` is an int.

Placeholders are filled by one rule, letter by letter (step 1's, widened):
  - a name letter (`m`) is a label: `m`, or in a position, `m1` at depth 1
    and `m2` at depth 2, so two labels never share a name
  - a letter right after `case` or `...` is a case constant: `0`, then `1`
  - a letter that stands as a whole statement is a body: outside every
    parenthesis, right before `;`, and right after `{`, `;`, `)`, `:`,
    `else`, `do` or the start. The body being filled gets what is placed in
    it, every other body `;`; the letter and its `;` are replaced together
  - every other letter is a test or a value: `x` (`p` for `goto *a;`)

Writes out/check.json, one record per program (its text, clang's answer, its
first error line and notes, the reader's prediction, agree or not), and
out/check_summary.txt, the counts with their wholes and every disagreement.
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dependent_HiOp_reader as reader  # noqa: E402
from PseudoIR.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import LETTERS  # noqa: E402

PLACES = os.path.join(reader.OUT, "places.json")
CHECKED = os.path.join(reader.OUT, "check.json")
SUMMARY = os.path.join(reader.OUT, "check_summary.txt")

CLANG = ["clang", "-std=gnu17", "--target=riscv64-unknown-linux-gnu", "-fsyntax-only"]
FUNCTION = "{0}void f(int x) {{ {1} }}"

# The filling rule (see the docstring).
TEST_OR_VALUE = "x"
POINTER = "p"
CASE_CONSTANTS = ("0", "1")
OTHER_BODY = ";"
LABEL = "m"
NAME_LETTERS = LETTERS["name"]
PLACEHOLDERS = LETTERS["operand"] + LETTERS["name"]
STATEMENT_STARTS = ("", "{", ";", ")", ":", "else", "do")
TOKEN = re.compile(r"\.\.\.|\w+|[^\s\w]")

# Typed here (see the docstring): GNU C's 4 places, keyed by the in-note the
# reader reads for each; what each needs before the function; and the text
# around what is placed inside it.
PLACES_OF_GNU_C = {
    "note_protected_by_vla": ("a variable length array", "", "{{ int v[x]; {0} }}"),
    "note_protected_by_vla_typedef": ("a variable length array typedef", "", "{{ typedef int t[x]; {0} }}"),
    "note_protected_by_cleanup": ("a variable with __attribute__((cleanup))", "void g(int *); ",
                                  "{{ int c __attribute__((cleanup(g))); {0} }}"),
    "note_enters_statement_expression": ("a statement expression", "", "({{ {0} }});"),
}
# `goto *a;`'s operand, with the label's address taken, or not.
POINTER_WITH_AN_ADDRESS = "void *p = {0};"
POINTER_WITHOUT_AN_ADDRESS = "void *p = 0;"

DEPTH_0 = "depth 0: the dependent alone in the function"
DEPTH_1 = "depth 1: the dependent in a position"
DEPTH_2 = "depth 2: the dependent in a position inside a position"
TWO_IN_ONE_SWITCH = "two of it in one switch"
LABEL_MISSING = "the label missing"
LABEL_BEFORE = "the label before it"
LABEL_AFTER = "the label after it"
LABEL_IN_A_POSITION = "the label in a position, the dependent at the top"
DEPENDENT_IN_A_POSITION = "the dependent in a position, the label at the top"
WITH_AN_ADDRESS = "with `&&m` in the function"
WITHOUT_AN_ADDRESS = "without `&&m` in the function"
LABEL_INSIDE = "a place: the label inside it, the jump outside"
JUMP_INSIDE = "a place: the jump inside it, the label outside"
BOTH_INSIDE = "a place: the jump and the label inside it"
SHAPES = (DEPTH_0, DEPTH_1, DEPTH_2, TWO_IN_ONE_SWITCH, LABEL_MISSING, LABEL_BEFORE, LABEL_AFTER,
          LABEL_IN_A_POSITION, DEPENDENT_IN_A_POSITION, WITH_AN_ADDRESS, WITHOUT_AN_ADDRESS, LABEL_INSIDE,
          JUMP_INSIDE, BOTH_INSIDE)
PLACE_SHAPES = (LABEL_INSIDE, JUMP_INSIDE, BOTH_INSIDE)

ACCEPTED = "accepted"
REFUSED = "refused"
NOT_READ = "not read"


def main():
    work_folder = sys.argv[1]
    places = read_json(PLACES)
    texts = reader.diagnostic_texts(reader.CHECKOUT)
    listings = all_listings()
    statement_listings = statement_listings_of(listings)
    dependents = dependent_listings(listings, places)
    statements = statements_with_a_body(statement_listings, places)
    positions = positions_of(statements)
    programs = every_program(dependents, positions, listings, places)
    results = compiled_and_compared(programs, work_folder, texts, places)
    write_check(results, statement_listings, statements, positions, dependents, places)


# The listings


def all_listings() -> list:
    listings = reader.read_listings(reader.LISTINGS)
    listings.append(reader.label_address_listing(reader.LABEL_ADDRESS))
    return listings


def statement_listings_of(listings: list) -> list:
    """Every listing whose kind StmtNodes.td does not declare as an
    expression."""
    kinds = reader.statement_kinds(reader.CHECKOUT)
    found = []
    for listing in listings:
        if listing["name"] in kinds:
            found.append(listing)
    return found


def dependent_listings(listings: list, places: dict) -> list:
    """The listings the reader read, in the files' order."""
    found = []
    for listing in listings:
        read = places["by_listing"].get(listing["template"])
        if read is not None and read["kind"] == listing["name"] and read["placed"] is not None:
            found.append(listing)
    return found


def statements_with_a_body(statement_listings: list, places: dict) -> list:
    found = []
    for listing in statement_listings:
        if why_not_a_statement_with_a_body(listing, places) is None:
            found.append(listing)
    return found


def why_not_a_statement_with_a_body(listing: dict, places: dict):
    why = None
    if not listing["parsed_as_written"]:
        why = "clang did not parse it as written"
    elif listing["template"] in places["by_listing"]:
        why = "a dependent listing"
    elif count_bodies(listing["template"]) == 0:
        why = "it has no body"
    return why


def positions_of(statements: list) -> list:
    """One position per body of each statement listing."""
    positions = []
    for listing in statements:
        bodies = count_bodies(listing["template"])
        for body in range(bodies):
            positions.append({"listing": listing, "body": body})
    return positions


def listing_of_kind(listings: list, kind: str) -> dict:
    """The one listing of `kind` clang parsed as written."""
    found = []
    for listing in listings:
        if listing["name"] == kind and listing["parsed_as_written"]:
            found.append(listing)
    if len(found) != 1:
        raise LookupError(f"listings of {kind} parsed as written: {len(found)}, not 1")
    one = found[0]
    return one


# The programs


def every_program(dependents: list, positions: list, listings: list, places: dict) -> list:
    programs = []
    for dependent in dependents:
        add_programs_of(programs, dependent, positions, listings, places)
    return programs


def add_programs_of(programs: list, dependent: dict, positions: list, listings: list, places: dict) -> None:
    """Every shape that applies to one dependent listing."""
    read = places["by_listing"][dependent["template"]]
    if read["placed"] == reader.BY_THE_SCOPES_AROUND_IT:
        add_chains(programs, dependent, read, positions)
    if read["one_switch"]:
        add_two_in_one_switch(programs, dependent, read, listings)
    needs = read["needs_in_the_same_function"]
    if needs is not None and needs["with_the_same_label"]:
        add_label_programs(programs, dependent, read, positions, listings)
    if needs is not None and not needs["with_the_same_label"]:
        add_address_programs(programs, dependent, read, listings)
    if read["placed"] == reader.BY_THE_WHOLE_FUNCTION and read["may_not_enter"]:
        add_place_programs(programs, dependent, read, listings, places)


# 1. Chains


def add_chains(programs: list, dependent: dict, read: dict, positions: list) -> None:
    written = filled(dependent["template"], OTHER_BODY, -1, LABEL, TEST_OR_VALUE)
    refusal = read["asks"]["refusal"]
    programs.append(program(DEPTH_0, dependent, [], written, "", predicted_in_chain([], read), [refusal]))
    for outer in positions:
        add_chains_in(programs, dependent, read, written, outer, positions)


def add_chains_in(programs: list, dependent: dict, read: dict, written: str, outer: dict, positions: list) -> None:
    refusal = read["asks"]["refusal"]
    text = in_position(outer, written, 1)
    chain = [outer]
    programs.append(program(DEPTH_1, dependent, chain, text, "", predicted_in_chain(chain, read), [refusal]))
    for inner in positions:
        inner_text = in_position(inner, written, 2)
        text = in_position(outer, inner_text, 1)
        chain = [outer, inner]
        programs.append(program(DEPTH_2, dependent, chain, text, "", predicted_in_chain(chain, read), [refusal]))


def predicted_in_chain(chain: list, read: dict) -> str:
    """Accepted when a statement of the chain (outermost first) is one of the
    places, with none after it of a kind that stops the place being passed
    on."""
    predicted = REFUSED
    stoppers = read["passed_on_unless"]["kinds_that_set_them"]
    for position in chain:
        kind = position["listing"]["name"]
        if kind in stoppers:
            predicted = REFUSED
        if kind in read["places"]:
            predicted = ACCEPTED
    return predicted


# 2. Two of it in one switch


def add_two_in_one_switch(programs: list, dependent: dict, read: dict, listings: list) -> None:
    """`switch (x) { D D }`, from the switch listing and the two-body block."""
    switch = listing_of_kind_with_bodies(listings, "SwitchStmt", 1)
    block = listing_of_kind_with_bodies(listings, "CompoundStmt", 2)
    written = filled(dependent["template"], OTHER_BODY, -1, LABEL, TEST_OR_VALUE)
    both = filled(block["template"], written, -2, LABEL, TEST_OR_VALUE)
    text = filled(switch["template"], both, 0, LABEL, TEST_OR_VALUE)
    refusals = refusal_names(read["one_switch"])
    chain = [{"listing": switch, "body": 0}, {"listing": block, "body": -2}]
    programs.append(program(TWO_IN_ONE_SWITCH, dependent, chain, text, "", REFUSED, refusals))


def listing_of_kind_with_bodies(listings: list, kind: str, bodies: int) -> dict:
    found = []
    for listing in listings:
        if listing["name"] == kind and listing["parsed_as_written"] and count_bodies(listing["template"]) == bodies:
            found.append(listing)
    if len(found) != 1:
        raise LookupError(f"listings of {kind} with {bodies} bodies: {len(found)}, not 1")
    one = found[0]
    return one


# 3. The label


def add_label_programs(programs: list, dependent: dict, read: dict, positions: list, listings: list) -> None:
    label = label_statement(read, listings)
    written = dependent_statement(dependent)
    refusals = read["needs_in_the_same_function"]["refusal"]
    programs.append(program(LABEL_MISSING, dependent, [], written, "", REFUSED, refusals))
    programs.append(program(LABEL_BEFORE, dependent, [], label + " " + written, "", ACCEPTED, refusals))
    programs.append(program(LABEL_AFTER, dependent, [], written + " " + label, "", ACCEPTED, refusals))
    for position in positions:
        add_label_in_a_position(programs, dependent, label, written, position, refusals)


def add_label_in_a_position(programs: list, dependent: dict, label: str, written: str, position: dict,
                            refusals: list) -> None:
    chain = [position]
    text = written + " " + in_position(position, label, 1)
    programs.append(program(LABEL_IN_A_POSITION, dependent, chain, text, "", ACCEPTED, refusals))
    text = label + " " + in_position(position, written, 1)
    programs.append(program(DEPENDENT_IN_A_POSITION, dependent, chain, text, "", ACCEPTED, refusals))


def label_statement(read: dict, listings: list) -> str:
    """`m: ;`: the listing of the kind the dependent needs (LabelStmt)."""
    kinds = read["needs_in_the_same_function"]["kinds"]
    listing = listing_of_kind(listings, kinds[0])
    written = filled(listing["template"], OTHER_BODY, -1, LABEL, TEST_OR_VALUE)
    return written


def dependent_statement(dependent: dict) -> str:
    """The dependent as a statement: a statement listing as filled; an
    expression listing (`&&m`) followed by `;`."""
    written = filled(dependent["template"], OTHER_BODY, -1, LABEL, POINTER)
    if not written.endswith(";"):
        written = written + ";"
    return written


# 4. The address


def add_address_programs(programs: list, dependent: dict, read: dict, listings: list) -> None:
    """`void *p = &&m; goto *p; m: ;`, and the same with `void *p = 0;`."""
    address = address_expression(read, listings)
    label = label_of_an_address(listings)
    written = dependent_statement(dependent)
    refusals = read["needs_in_the_same_function"]["refusal"]
    with_address = POINTER_WITH_AN_ADDRESS.format(address) + " " + written + " " + label
    without_address = POINTER_WITHOUT_AN_ADDRESS + " " + written + " " + label
    programs.append(program(WITH_AN_ADDRESS, dependent, [], with_address, "", ACCEPTED, refusals))
    programs.append(program(WITHOUT_AN_ADDRESS, dependent, [], without_address, "", REFUSED, refusals))


def address_expression(read: dict, listings: list) -> str:
    """`&&m`: the listing of the kind the dependent needs (AddrLabelExpr)."""
    kinds = read["needs_in_the_same_function"]["kinds"]
    listing = listing_of_kind(listings, kinds[0])
    written = filled(listing["template"], OTHER_BODY, -1, LABEL, TEST_OR_VALUE)
    return written


def label_of_an_address(listings: list) -> str:
    listing = listing_of_kind(listings, "LabelStmt")
    written = filled(listing["template"], OTHER_BODY, -1, LABEL, TEST_OR_VALUE)
    return written


# 5. The places a jump may not enter


def add_place_programs(programs: list, dependent: dict, read: dict, listings: list, places: dict) -> None:
    for note, place in PLACES_OF_GNU_C.items():
        add_programs_in_a_place(programs, dependent, read, listings, places, note, place)


def add_programs_in_a_place(programs: list, dependent: dict, read: dict, listings: list, places: dict, note: str,
                            place: tuple) -> None:
    _name, before, around = place
    label = label_of_an_address(listings)
    jump = dependent_statement(dependent)
    start = jump_start(read, listings)
    refusals = refusal_names(read["may_not_enter"])
    entering = predicted_entering(read, places, note)
    texts = {
        LABEL_INSIDE: start + jump + " " + around.format(label),
        JUMP_INSIDE: start + around.format(jump) + " " + label,
        BOTH_INSIDE: start + around.format(jump + " " + label),
    }
    predictions = {LABEL_INSIDE: entering, JUMP_INSIDE: NOT_READ, BOTH_INSIDE: ACCEPTED}
    for shape in PLACE_SHAPES:
        made = program(shape, dependent, [], texts[shape], before, predictions[shape], refusals)
        made["place"] = note
        programs.append(made)


def jump_start(read: dict, listings: list) -> str:
    """What a jump needs before it in these programs: `void *p = &&m; ` for
    one that needs some label's address."""
    start = ""
    needs = read["needs_in_the_same_function"]
    if not needs["with_the_same_label"]:
        start = POINTER_WITH_AN_ADDRESS.format(address_expression(read, listings)) + " "
    return start


def predicted_entering(read: dict, places: dict, note: str) -> str:
    """The label inside the place, the jump outside: refused when the place
    is one the reader read (an in-note), the jump's refusal tests the in-note,
    and C makes it no mere warning; accepted when C makes it a warning; not
    read when the reader did not read the place."""
    protected = places["function_rules"]["places_a_jump_may_not_enter"]
    predicted = NOT_READ
    if note not in notes_of(protected["places"]):
        return predicted
    predicted = ACCEPTED
    if note in warned_in_c(protected["only_a_warning_in_c"]):
        return predicted
    if tests_an_in_note(read["may_not_enter"]):
        predicted = REFUSED
    return predicted


def notes_of(notes: list) -> list:
    found = []
    for note in notes:
        add_once(found, note["note"])
    return found


def warned_in_c(functions: list) -> list:
    found = []
    for function in functions:
        if function["holds_in_c"]:
            add_all_once(found, function["notes"])
    return found


def tests_an_in_note(rules: list) -> bool:
    found = False
    for rule in rules:
        if rule["tests_the_in_note"]:
            found = True
    return found


# Writing a program


def program(shape: str, dependent: dict, chain: list, text: str, before: str, predicted: str,
            refusals: list) -> dict:
    made = {
        "shape": shape,
        "dependent": dependent["template"],
        "kind": dependent["name"],
        "chain": chain_written(chain),
        "chain_kinds": chain_kinds(chain),
        "program": FUNCTION.format(before, text),
        "reader_predicts": predicted,
        "reader_refusals": [],
    }
    if predicted == REFUSED:
        made["reader_refusals"] = refusals
    return made


def chain_written(chain: list) -> list:
    written = []
    for position in chain:
        body = f"body {position['body'] + 1}"
        if position["body"] == -2:
            body = "every body"
        written.append(f"{position['listing']['template']} ({body})")
    return written


def chain_kinds(chain: list) -> list:
    kinds = []
    for position in chain:
        kinds.append(position["listing"]["name"])
    return kinds


def refusal_names(rules: list) -> list:
    names = []
    for rule in rules:
        add_once(names, rule["refusal"])
    return names


def in_position(position: dict, inside: str, depth: int) -> str:
    """A statement listing with `inside` in its body number `position["body"]`,
    its label (if it has one) named for its depth."""
    written = filled(position["listing"]["template"], inside, position["body"], LABEL + str(depth), TEST_OR_VALUE)
    return written


# Filling a listing's placeholders


def filled(template: str, inside: str, body: int, label: str, value: str) -> str:
    """The written form with its placeholders filled by the rule: body number
    `body` gets `inside` (every body, for -2; none, for -1), every other body
    `;`, a case constant `0` then `1`, a label `label`, every other letter
    `value`."""
    tokens = tokens_of(template)
    roles = roles_of(tokens)
    counters = {"bodies": 0, "case constants": 0}
    pieces = []
    copied_up_to = 0
    for index, role in roles:
        start = tokens[index][1]
        end = tokens[index][2]
        if role == "body":
            end = tokens[index + 1][2]
        pieces.append(template[copied_up_to:start])
        pieces.append(written_for(role, counters, inside, body, label, value))
        copied_up_to = end
    pieces.append(template[copied_up_to:])
    written = "".join(pieces)
    return written


def written_for(role: str, counters: dict, inside: str, body: int, label: str, value: str) -> str:
    written = value
    if role == "label":
        written = label
    if role == "case constant":
        written = CASE_CONSTANTS[counters["case constants"]]
        counters["case constants"] += 1
    if role == "body":
        written = OTHER_BODY
        if counters["bodies"] == body or body == -2:
            written = inside
        counters["bodies"] += 1
    return written


def count_bodies(template: str) -> int:
    bodies = 0
    roles = roles_of(tokens_of(template))
    for _index, role in roles:
        if role == "body":
            bodies += 1
    return bodies


def tokens_of(template: str) -> list:
    """(text, start, end) for each word, `...`, or other mark."""
    tokens = []
    for found in TOKEN.finditer(template):
        tokens.append((found.group(0), found.start(), found.end()))
    return tokens


def roles_of(tokens: list) -> list:
    """(token index, role) for each placeholder letter."""
    roles = []
    depth = 0
    for index in range(len(tokens)):
        text = tokens[index][0]
        depth = depth_after(text, depth)
        if text in PLACEHOLDERS:
            roles.append((index, role_of(tokens, index, depth)))
    return roles


def depth_after(text: str, depth: int) -> int:
    after = depth
    if text == "(":
        after = depth + 1
    if text == ")":
        after = depth - 1
    return after


def role_of(tokens: list, index: int, depth: int) -> str:
    text = tokens[index][0]
    before = token_text(tokens, index - 1)
    after = token_text(tokens, index + 1)
    role = "test or value"
    if text in NAME_LETTERS:
        role = "label"
    elif before in ("case", "..."):
        role = "case constant"
    elif depth == 0 and after == ";" and before in STATEMENT_STARTS:
        role = "body"
    return role


def token_text(tokens: list, index: int) -> str:
    text = ""
    if 0 <= index < len(tokens):
        text = tokens[index][0]
    return text


# Compiling


def compiled_and_compared(programs: list, work_folder: str, texts: dict, places: dict) -> list:
    os.makedirs(work_folder, exist_ok=True)
    results = []
    number = 0
    for made in programs:
        number += 1
        results.append(compiled(made, number, work_folder, texts, places))
    return results


def compiled(made: dict, number: int, work_folder: str, texts: dict, places: dict) -> dict:
    """One program compiled alone: clang's answer beside the reader's."""
    name = f"program_{number:04d}.c"
    path = os.path.join(work_folder, name)
    with open(path, "w", encoding="utf-8") as source_file:
        source_file.write(made["program"] + "\n")
    finished = subprocess.run(CLANG + [name], cwd=work_folder, capture_output=True, text=True)
    answer = REFUSED
    if finished.returncode == 0:
        answer = ACCEPTED
    result = {"number": number}
    result.update(made)
    result["clang"] = answer
    result["clang_exit"] = finished.returncode
    result["clang_first_error"] = first_error(finished.stderr)
    result["clang_notes"] = notes_in(finished.stderr)
    result["agree"] = agreement(made["reader_predicts"], answer)
    result["refusal_matches"] = refusal_matches(result, texts)
    add_place_named(result, places)
    return result


def agreement(predicted: str, answer: str):
    agree = None
    if predicted != NOT_READ:
        agree = predicted == answer
    return agree


def refusal_matches(result: dict, texts: dict):
    """When the reader predicted a refusal and clang refused: whether clang's
    first error carries the words of one of the refusals the reader named."""
    matches = None
    if result["reader_predicts"] != REFUSED or result["clang"] != REFUSED:
        return matches
    matches = False
    for refusal in result["reader_refusals"]:
        if says(texts, refusal, result["clang_first_error"]):
            matches = True
    return matches


def add_place_named(result: dict, places: dict) -> None:
    """For a program in a place: whether one of clang's notes carries the
    words of the place's in-note."""
    if "place" not in result:
        return
    words = words_of_a_note(places, result["place"])
    result["clang_named_the_place"] = False
    for note in result["clang_notes"]:
        if words is not None and words in note:
            result["clang_named_the_place"] = True


def words_of_a_note(places: dict, note: str):
    words = None
    protected = places["function_rules"]["places_a_jump_may_not_enter"]
    for place in protected["places"]:
        if place["note"] == note:
            words = place["says"]
    return words


def says(texts: dict, diagnostic: str, line) -> bool:
    """Whether `line` carries the words of `diagnostic`, its `%0` and
    `%select{...}0` read as anything."""
    found = False
    if line is None or diagnostic not in texts:
        return found
    pattern = words_pattern(texts[diagnostic]["text"])
    found = re.search(pattern, line) is not None
    return found


def words_pattern(words: str) -> str:
    pieces = re.split(r"(%select\{[^}]*\}\d|%\w*\d)", words)
    written = []
    for piece in pieces:
        if piece.startswith("%"):
            written.append(".*")
        else:
            written.append(re.escape(piece))
    pattern = "".join(written)
    return pattern


def first_error(stderr: str):
    found = None
    for line in stderr.splitlines():
        if ": error: " in line:
            found = line
            break
    return found


def notes_in(stderr: str) -> list:
    notes = []
    for line in stderr.splitlines():
        if ": note: " in line:
            notes.append(line)
    return notes


def clang_version() -> str:
    finished = subprocess.run(["clang", "--version"], capture_output=True, text=True)
    version = finished.stdout.splitlines()[0]
    return version


# Writing


def write_check(results: list, statement_listings: list, statements: list, positions: list, dependents: list,
                places: dict) -> None:
    counts = counted(results, dependents)
    record = {
        "what": "dependent_HiOp_reader step 2 checked against clang's own checker: a brute force bounded at depth 2",
        "clang": clang_version(),
        "command": " ".join(CLANG) + " <program>.c",
        "places_read": PLACES,
        "positions": positions_written(positions),
        "counts": counts,
        "programs": results,
    }
    reader.write_json(record, CHECKED)
    lines = summary_lines(record, statement_listings, statements, positions, dependents, places)
    write_text(lines, SUMMARY)
    print("\n".join(lines))


def positions_written(positions: list) -> list:
    written = []
    for position in positions:
        written.append({"listing": position["listing"]["template"], "kind": position["listing"]["name"],
                        "body": position["body"] + 1})
    return written


def counted(results: list, dependents: list) -> dict:
    counts = new_counts()
    counts["by_shape"] = {}
    counts["by_dependent"] = {}
    for shape in SHAPES:
        counts["by_shape"][shape] = new_counts()
    for dependent in dependents:
        counts["by_dependent"][dependent["template"]] = new_counts()
    for result in results:
        add_result(counts, result)
        add_result(counts["by_shape"][result["shape"]], result)
        add_result(counts["by_dependent"][result["dependent"]], result)
    return counts


def new_counts() -> dict:
    counts = {"programs": 0, ACCEPTED: 0, REFUSED: 0, "agree": 0, "disagree": 0, "not read": 0,
              "refusal matches": 0, "refusal does not match": 0}
    return counts


def add_result(counts: dict, result: dict) -> None:
    counts["programs"] += 1
    counts[result["clang"]] += 1
    if result["agree"] is None:
        counts["not read"] += 1
    elif result["agree"]:
        counts["agree"] += 1
    else:
        counts["disagree"] += 1
    if result["refusal_matches"] is True:
        counts["refusal matches"] += 1
    if result["refusal_matches"] is False:
        counts["refusal does not match"] += 1


def summary_lines(record: dict, statement_listings: list, statements: list, positions: list, dependents: list,
                  places: dict) -> list:
    counts = record["counts"]
    lines = [
        record["what"],
        f"clang: {record['clang']}",
        f"command: {record['command']}",
        "",
    ]
    add_listing_lines(lines, statement_listings, statements, dependents, places)
    add_position_lines(lines, positions)
    lines.append("")
    add_count_lines(lines, "all programs", counts)
    lines.append("")
    lines.append("by shape:")
    add_table_lines(lines, counts["by_shape"])
    lines.append("")
    lines.append("by dependent:")
    add_table_lines(lines, counts["by_dependent"])
    lines.append("")
    add_disagreement_lines(lines, record["programs"])
    lines.append("")
    add_refusal_mismatch_lines(lines, record["programs"])
    lines.append("")
    add_place_lines(lines, record["programs"])
    lines.append("")
    add_dangling_else_lines(lines, record["programs"])
    return lines


def add_listing_lines(lines: list, statement_listings: list, statements: list, dependents: list,
                      places: dict) -> None:
    lines.append(f"dependent listings the reader read: {len(dependents)}: {written_list(templates_of(dependents))}")
    lines.append(f"statement listings in kinds_forms.json: {len(statement_listings)}")
    lines.append(f"  with a body, used for positions: {len(statements)} of {len(statement_listings)}:"
                 f" {written_list(templates_of(statements))}")
    others = len(statement_listings) - len(statements)
    lines.append(f"  not used: {others} of {len(statement_listings)}:")
    for listing in statement_listings:
        why = why_not_a_statement_with_a_body(listing, places)
        if why is not None:
            lines.append(f"    {str(listing['position']):>4s} {listing['template']:20s} {listing['name']:18s} {why}")


def add_position_lines(lines: list, positions: list) -> None:
    lines.append(f"positions: {len(positions)} (one per body of the {count_listings(positions)} statement listings"
                 f" with a body):")
    number = 0
    for position in positions:
        number += 1
        listing = position["listing"]
        lines.append(f"  {number:2d}. {listing['template']:20s} {listing['name']:14s} body {position['body'] + 1}")


def count_listings(positions: list) -> int:
    templates = []
    for position in positions:
        add_once(templates, position["listing"]["template"])
    number = len(templates)
    return number


def add_count_lines(lines: list, what: str, counts: dict) -> None:
    whole = counts["programs"]
    read = whole - counts["not read"]
    lines.append(f"{what}: {whole} programs; there are no others")
    lines.append(f"  clang accepted {counts[ACCEPTED]} of {whole}; refused {counts[REFUSED]} of {whole}")
    lines.append(f"  the reader agrees with clang on {counts['agree']} of {whole}; disagrees on {counts['disagree']}"
                 f" of {whole}; not read {counts['not read']} of {whole}"
                 f" (so agrees on {counts['agree']} of the {read} it read)")
    refused_both = counts["refusal matches"] + counts["refusal does not match"]
    lines.append(f"  of the {refused_both} programs both refused, clang's first error carries the words of the"
                 f" refusal the reader named in {counts['refusal matches']} of {refused_both}")


def add_table_lines(lines: list, table: dict) -> None:
    lines.append(f"  {'programs':>8s} {'accepted':>8s} {'refused':>8s} {'agree':>6s} {'disagree':>8s}"
                 f" {'not read':>8s}  ")
    for name, counts in table.items():
        if counts["programs"] == 0:
            continue
        lines.append(f"  {counts['programs']:8d} {counts[ACCEPTED]:8d} {counts[REFUSED]:8d} {counts['agree']:6d}"
                     f" {counts['disagree']:8d} {counts['not read']:8d}  {name}")


def add_disagreement_lines(lines: list, results: list) -> None:
    disagreeing = results_where(results, "agree", False)
    lines.append(f"disagreements: {len(disagreeing)} of {len(results)}")
    number = 0
    for result in disagreeing:
        number += 1
        lines.append(f"  disagreement {number}: program {result['number']} ({result['shape']}): {result['program']}")
        lines.append(f"      reader: {result['reader_predicts']}; clang: {result['clang']};"
                     f" clang's first error: {result['clang_first_error']}")
    if not disagreeing:
        lines.append("  (none)")


def add_refusal_mismatch_lines(lines: list, results: list) -> None:
    mismatching = results_where(results, "refusal_matches", False)
    both_refused = len(mismatching) + len(results_where(results, "refusal_matches", True))
    lines.append(f"both refused, but clang's first error is not the refusal the reader named:"
                 f" {len(mismatching)} of {both_refused}")
    for result in mismatching:
        lines.append(f"  program {result['number']} ({result['shape']}): {result['program']}")
        lines.append(f"      the reader named {', '.join(result['reader_refusals'])}; clang's first error:"
                     f" {result['clang_first_error']}")
    if not mismatching:
        lines.append("  (none)")


def results_where(results: list, key: str, value) -> list:
    """The results whose `key` is `value` (True, False or None, by identity)."""
    found = []
    for result in results:
        if result[key] is value:
            found.append(result)
    return found


def add_place_lines(lines: list, results: list) -> None:
    """The places, program by program: what clang did, and the reader. "in-note
    named": whether one of clang's notes carries the words of the place's
    in-note; clang's first error and notes follow."""
    in_places = results_in_places(results)
    lines.append(f"the places a jump may not enter: {len(in_places)} programs")
    for result in in_places:
        lines.append(f"  {result['dependent']:9s} {result['place']:34s} {result['shape']:46s}"
                     f" clang {result['clang']:8s} reader {result['reader_predicts']:8s}"
                     f" in-note named: {result['clang_named_the_place']}")
        add_error_and_notes(lines, result)


def add_error_and_notes(lines: list, result: dict) -> None:
    if result["clang_first_error"] is None:
        return
    lines.append(f"      error: {result['clang_first_error'].split(': error: ')[-1]}")
    for note in result["clang_notes"]:
        lines.append(f"      note: {note.split(': note: ')[-1]}")


def results_in_places(results: list) -> list:
    found = []
    for result in results:
        if "place" in result:
            found.append(result)
    return found


def add_dangling_else_lines(lines: list, results: list) -> None:
    """Chains where an `if (a) b;` stands in the first body of `if (a) b;
    else c;`: clang reads the `else` as the inner `if`'s."""
    dangling = 0
    chains = 0
    for result in results:
        if result["shape"] != DEPTH_2:
            continue
        chains += 1
        if result["chain"][0].startswith("if (a) b; else c; (body 1)") and result["chain"][1].startswith("if (a) b; ("):
            dangling += 1
    lines.append(f"depth-2 chains with `if (a) b;` in the first body of `if (a) b; else c;`: {dangling} of {chains};"
                 f" clang reads the `else` as the inner `if`'s, so the outer `if` has one body and the inner two;"
                 f" the kinds around the dependent are the same (IfStmt in IfStmt)")


def templates_of(listings: list) -> list:
    templates = []
    for listing in listings:
        templates.append(listing["template"])
    return templates


def written_list(items: list) -> str:
    written = ", ".join(items)
    if not items:
        written = "(none)"
    return written


def add_once(items: list, item) -> None:
    if item not in items:
        items.append(item)


def add_all_once(items: list, more: list) -> None:
    for item in more:
        add_once(items, item)


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as read_file:
        read = json.load(read_file)
    return read


def write_text(lines: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as written_file:
        written_file.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
