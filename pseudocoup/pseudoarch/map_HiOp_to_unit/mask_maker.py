# DRY: Dont Repeat Yourself
"""DRY_mask_maker -- makes grid_mask_of_knowns, the data structure: operators
crossed with holders, and the lowerer's verdict on every cell: accepted or
refused. Cells already known are carried over, so only the rest go to the
lowerer, and they go in bulk.

Plan: `.../node_0_0_0_0_2_5_DRY_mask_maker/`.

    cells  = grid(operators, holders)      # one holder per operand slot
    known  = knowns(lang, cells)           # judged before: accepted or refused
    judged = judge(lang, cells - known)    # the lowerer, many cells per file
    mask   = known + judged                # every cell accepted or refused

A compiler reports each refusal by line; an interpreter raises it when the
cell runs. Either way the refusal is the lowerer's own testimony.

When a language changes, only the cells whose declarations changed are
judged again. That is also the answer to churn.

Three judgements, in order, each one the lowerer's:

    holders   can a program keep a value of this type in a field of the
              held struct? A holder refused here is refused in every cell,
              so none of its cells is written.
    cells     every operator over the holders that passed, written in the
              standard form the probes compile in.
    kinds     one accepted cell per operator, read back through the
              lowerer's own syntax tree: did it parse as the operator it
              was written as? A printer can write a form that parses back
              as a different kind; those cells belong to that kind.
"""

import itertools
import gzip
import json
import os
import re
import shlex
import subprocess
from typing import Iterator, NamedTuple, Optional

from .dict_of_lang_HiOps import Variant
from .model_lang_parts import PLACEHOLDER, placeholders_of
from .lower_HiOp import standard_HiOp_wrapper
# The standard-form moved into standard_HiOp_wrapper on 2026-10-13 . The
# names below are its; this module and the code that reads them through it use
# them as before.
from .lower_HiOp.standard_HiOp_wrapper import (  # noqa: F401
    C_CONTEXT_NAMES_BY_HAND,
    C_FUNCTION_ANSWERS_BY_HAND,
    C_HELD_TYPES,
    C_JUMPS_BY_HAND,
    C_LIBRARY_RULE,
    C_PART_CONTEXTS_BY_HAND,
    C_RESULT_TYPE,
    C_STAND_IN,
    C_STATEMENT_CONTEXT_BY_HAND,
    FIELD_ACCESS,
    HiOp_on_its_own_line,
    INERT_PART_EXPRESSIONS_BY_HAND,
    INERT_PART_ROLES_BY_HAND,
    NAME_PLACEHOLDERS,
    PREAMBLE,
    TYPE_PLACEHOLDERS,
    VALUE_PLACEHOLDERS,
    builtin_name,
    custom_program_lines,
    filled,
    is_builtin_call,
    is_statement,
    listed_name,
    slots_of,
)


class Cell(NamedTuple):
    """One position in the grid: an operator and one holder per operand.

    Addressed by POSITION in the two declared lists, never by an operator's
    spelling: a spelling is a label, never a key.
    """

    operator: int
    holders: tuple


class Verdict(NamedTuple):
    """What the lowerer said about one cell.

    `result` is the position of the holder the cell answers, when the
    lowerer says it. `evidence` is the run, lane log or refusal line the
    verdict came from.
    """

    accepted: bool
    result: Optional[int]
    evidence: str


# How each lowerer is asked: the flags the held probes compile with, plus
# syntax-only and no cap on refusals, so a file's later refusals are never
# lost (clang stops at 20 by default).
#
# ADJACENT: the flags belong to `lower_HiOp`. They are written here because
# that node was not coded when they were; move them, and leave these as their
# callers. The source form that was written here too moved into
# `standard_HiOp_wrapper` on 2026-10-13 ; `standard_cell_lines`, below,
# is left as its caller.
JUDGE_COMMAND = {
    # GNU C, clang's default dialect (-std=gnu17): the owner, 2026-10-05, "we have
    # agreed to work with GNU-C" . Was -std=c17.
    "c": "clang -std=gnu17 -O1 --target=riscv64-unknown-linux-gnu -nostdlibinc -fsyntax-only -ferror-limit=0",
    "cpp": "clang++ -std=c++20 -O1 --target=riscv64-linux-gnu --gcc-toolchain=/usr -fsyntax-only -ferror-limit=0",
    # go's own compiler, not go/types: -e lifts its stop at 10 errors.
    "go": "env GOARCH=riscv64 GOOS=linux go tool compile -e -p main -o /dev/null",
    # the held rust probes' target; metadata stops after type-checking.
    # rustc writes its .rmeta into the working directory, so each file is
    # judged from a directory of its own.
    "rust": "rustc --edition 2021 --crate-type lib --emit=metadata --error-format=short --target riscv64gc-unknown-linux-gnu",
    # javac, stopped after flow analysis (nothing written but diagnostics),
    # with its stop at 100 errors lifted; judged from a directory of its own.
    "java": "javac -proc:none -Xlint:none -Xmaxerrs 1000000 -XDshould-stop.ifNoError=FLOW -d .",
}

# go's compiler does not type-check a file that has a syntax error, so one
# malformed cell would leave every other cell in its file unjudged. A cell
# refused with this prefix is taken out, and the rest are judged again.
SYNTAX_REFUSAL = {
    "go": "syntax error",
}

# The kind check reads clang's syntax tree for the probe functions only: the
# filter keeps the headers' declarations out, and clang then writes one JSON
# document per function it kept.
KIND_COMMAND_TAIL = "-Xclang -ast-dump=json -Xclang -ast-dump-filter=op_"
SUFFIX = {
    "c": ".c",
    "cpp": ".cpp",
    "go": ".go",
    "rust": ".rs",
    "java": ".java",
}
CLANG_DIAGNOSTIC = re.compile(r"^(?P<file>.*?):(?P<line>\d+):(?P<column>\d+): (error|fatal error): (?P<message>.*)$")
GO_DIAGNOSTIC = re.compile(r"^(?P<file>.*?\.go):(?P<line>\d+):(?P<column>\d+): (?P<message>.*)$")
RUST_DIAGNOSTIC = re.compile(r"^(?P<file>.*?\.rs):(?P<line>\d+):(?P<column>\d+): error(?:\[\w+\])?: (?P<message>.*)$")
JAVA_DIAGNOSTIC = re.compile(r"^(?P<file>.*?\.java):(?P<line>\d+): error: (?P<message>.*)$")
DIAGNOSTIC = {
    "c": CLANG_DIAGNOSTIC,
    "cpp": CLANG_DIAGNOSTIC,
    "go": GO_DIAGNOSTIC,
    "rust": RUST_DIAGNOSTIC,
    "java": JAVA_DIAGNOSTIC,
}


def grid(operators: tuple, holders: tuple) -> Iterator[Cell]:
    """Every cell: each operator with every holder in each of its operand
    slots. A unary operator has one slot, a binary operator two, a cast two
    (its operand and its target type)."""
    positions = range(len(holders))
    for operator_position, operator in enumerate(operators):
        slots = len(slots_of(operator))
        for chosen in itertools.product(positions, repeat=slots):
            cell = Cell(operator_position, tuple(chosen))
            yield cell


def standard_cell_lines(lang: str, key: str, operator, spellings: tuple, routing=None) -> list:
    """One HiOp's standard-form, written by standard_HiOp_wrapper since 2026-10-13
    , with ROUTING, read from the record, unless a caller hands
    another routing (ROUTING_BY_HAND, the check)."""
    if routing is None:
        routing = ROUTING
    lines = standard_HiOp_wrapper.standard_HiOp_wrapper(lang, key, operator, spellings, routing)
    return lines


# ---------------------------------------------------------------------------
# the routing: which configuration the standard-form gives each listing
#
# Read from the record of HiOp_configuration_solver : its
# configurations.json, one entry per listing, and the part records it is set
# together from (out/part_<part>.json.gz, and the small run's
# out/small_run_upgrades.json, rule 80): each group's kept arrangements in
# short form, with the reading of every inert call (rules 59 and 60). Each rule
# below is written once, about the record's fields, never about one listing.
# The rules, one line each, are routing_from_the_record's docstring.

MODULE_FOLDER = os.path.dirname(os.path.abspath(__file__))
PCHQ_FOLDER = os.path.normpath(os.path.join(MODULE_FOLDER, "..", "..", ".."))
SOLVER_RECORD_FOLDER = os.path.join(PCHQ_FOLDER, "Research", "extract_lang_vocabulary", "HiOp_configuration_solver",
                                    "out")
SOLVER_RECORD = os.path.join(SOLVER_RECORD_FOLDER, "configurations.json")
# The small run's record is a file of its own (rule 74); every other part's is
# part_<part>.json.gz, `:` and `/` in the part's name written `_` and `_of_`
# (the solver's file_name_of_the_part).
SOLVER_SMALL_RUN_PART = "small_run_upgrades"
SOLVER_SMALL_RUN_RECORD = os.path.join(SOLVER_RECORD_FOLDER, "small_run_upgrades.json")
SOLVER_PART_RECORD = os.path.join(SOLVER_RECORD_FOLDER, "part_{0}.json.gz")
# A reading in a short form (rule 60): n never ran; b behind the branch; x
# behind the branch and again; o once; a again; t tested.
NEVER_RAN = "n"
BEHIND_THE_BRANCH = ("b", "x")
# A short form's line that is an inert call (rule 60).
INERT_LINE = "."
# The line a listing's run alone writes after it (rule 33).
LINE_AFTER = "inert_1();"
LINE_BEFORE = "inert_0();"
LINE_AFTER_IN_A_TRACE = "inert_1 (after)"
# A component with no keyword is a label (the solver's rule 7); its inert call
# is named so.
NO_KEYWORD = "label"


class Routing(NamedTuple):
    """Which configuration the standard-form gives each listing: one shape for the
    routing read from the record (ROUTING) and the routing written by hand
    (ROUTING_BY_HAND, the check).

        roles             listing -> {placeholder: role}, role one of value, body,
                          constant, name (INERT_PART_ROLES)
        expressions       the names of the expressions held with inert parts
                          (INERT_PART_EXPRESSIONS)
        jumps             the kinds of the statements that jump (C_JUMPS)
        contexts          kind -> what a dependent-HiOp stands in
                          (C_STATEMENT_CONTEXT): `{0}` the statement, `{1}` a value
                          the context takes, `{2}` a zero of that value, `{3}` a line
                          the context holds
        context_names     kind -> the names of a context's inert calls:
                          {"value": ..., "held": ...}
        part_contexts     listing -> {placeholder: what the part stands in}, `{0}` the
                          part, `{2}` a zero of the listing's first value
                          (switch_with_a_case_label)
        function_answers  listing -> the placeholder whose value the standard function
                          answers (statement_returns)
        local_answers     name -> listing, for each expression whose answer is kept in
                          a local of the standard function (`&&m`'s standard function)
        reasons           (table, listing[, placeholder]) -> why, as the record says it
    """

    roles: dict
    expressions: tuple
    jumps: tuple
    contexts: dict
    context_names: dict
    part_contexts: dict
    function_answers: dict
    local_answers: dict
    reasons: dict


def routing_from_the_record() -> Routing:
    """The routing read from the record. The rules:

    R1 roles (derived_roles): for each listing the standard-form holds with inert
       parts (a statement listing of the language, or an expression the record
       gives N > 0), each placeholder is a name when it is a name letter (`m`);
       a constant where the record needed a constant (the listing's fill is
       `constant`: the values its components take; or a fill override of form
       `constant`); a body when the record's configuration counts it one (the
       second reading of log 419 Table 2: a component of the listing holds it,
       or it runs behind the branch or again); a value otherwise.
    R2 expressions (derived_expressions): the names the record lists for every
       expression listing it gives N > 0.
    R3 jumps (derived_jumps): the kinds of the statement listings after which
       the record never sees the next line run, having seen it at least once:
       run alone, the line after the listing, when nothing the listing needs
       stands between them, in each base run that returned; in the groups, the
       inert call right after the listing's one component (when it holds
       nothing) in the same body, in every kept arrangement.
    R4 contexts (derived_contexts): for a dependent-HiOp the record keeps only
       held in holders, the holder that keeps it with the fewest placeholders;
       its context is written from the record's smallest group holding both
       (fewest components, then fewest placeholders beside the dependent, then
       the record's order) in which the dependent's held line, when it holds
       one, runs behind the branch: the first such kept arrangement there, the
       holder with what stands in it. For a dependent-HiOp that needs listings
       in the same function instead: those listings after it, each as its own
       text, as the record's run alone writes them.
    R5 part contexts (derived_part_contexts): a part the record reads as never
       running alone, which a component of its listing holds, stands inside the
       dependent-HiOp the record keeps only inside that listing and whose held
       line runs behind the branch in their group of two, the one with the
       fewest placeholders.
    R6 function answers (derived_function_answers): a listing the record ran in
       a function that answers a value has a standard function that answers the
       value of its first value placeholder.
    R7 local answers (derived_local_answers): an expression listing the record
       keeps as a dependent-HiOp keeps its answer in a local of the held
       function (C_LOCAL_ANSWER), with what it needs as its context (R4).
    """
    record = solver_record()
    listings = record["listings"]
    groups = solver_groups(record)
    reasons = {}
    roles = derived_roles(listings, reasons)
    expressions = derived_expressions(listings, reasons)
    jumps = derived_jumps(listings, groups, reasons)
    contexts, context_names = derived_contexts(listings, groups, reasons)
    part_contexts = derived_part_contexts(listings, groups, reasons)
    function_answers = derived_function_answers(listings, roles, reasons)
    local_answers = derived_local_answers(listings, reasons)
    routing = Routing(roles, expressions, jumps, contexts, context_names, part_contexts, function_answers,
                      local_answers, reasons)
    return routing


def routing_by_hand() -> Routing:
    """The routing written by hand until 
    the check the routing from the record is compared with. `&&m`'s held
    functions by hand are not here: Research/lower_HiOp/lower_gnu_c.py
    (WRITTEN_BY_HAND) and Research/extract_lang_vocabulary/run_elv3.py
    (LABEL_ADDRESS_HELD_BY_HAND) keep them."""
    routing = Routing(INERT_PART_ROLES_BY_HAND, INERT_PART_EXPRESSIONS_BY_HAND, C_JUMPS_BY_HAND,
                      C_STATEMENT_CONTEXT_BY_HAND, C_CONTEXT_NAMES_BY_HAND, C_PART_CONTEXTS_BY_HAND,
                      C_FUNCTION_ANSWERS_BY_HAND, {}, {})
    return routing


# --- reading the record


def solver_record() -> dict:
    """configurations.json. Refuses by name when it is not there: the standard-form
    has no routing without it."""
    if not os.path.isfile(SOLVER_RECORD):
        message = f"DRY_mask_maker: the record {SOLVER_RECORD} is not there; the standard-form takes its routing from it"
        raise FileNotFoundError(message)
    with open(SOLVER_RECORD, encoding="utf-8") as source:
        record = json.load(source)
    return record


def solver_groups(record: dict) -> list:
    """Every group of every part the record was set together from, in the
    record's order of its parts."""
    groups = []
    for part in record["parts"]:
        path = part_record_path(part["part"])
        part_record = read_part_record(path)
        for group in part_record["groups"]:
            groups.append(group)
    return groups


def part_record_path(part: str) -> str:
    if part == SOLVER_SMALL_RUN_PART:
        path = SOLVER_SMALL_RUN_RECORD
        return path
    name = part.replace(":", "_").replace("/", "_of_")
    path = SOLVER_PART_RECORD.format(name)
    return path


def read_part_record(path: str) -> dict:
    if not os.path.isfile(path):
        message = f"DRY_mask_maker: the part record {path} is not there; the standard-form takes its routing from it"
        raise FileNotFoundError(message)
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as source:
            part_record = json.load(source)
        return part_record
    with open(path, encoding="utf-8") as source:
        part_record = json.load(source)
    return part_record


def listing_kind(listing: dict) -> str:
    kind = listing["kind"].split(".")[0]
    return kind


def is_held_with_inert_parts(listing: dict) -> bool:
    """A statement listing of the language, or an expression the record gives
    bodies. A declaration in the record is the solver's own component (its
    rule 70), not a listing of the language."""
    if listing.get("role") == "declaration":
        return False
    if listing["is_statement"]:
        return True
    held = len(bodies_of(listing)) > 0
    return held


def bodies_of(listing: dict) -> list:
    configuration = listing.get("configuration") or {}
    bodies = configuration.get("bodies") or []
    return bodies


def reading_alone(listing: dict, placeholder: str):
    """How the record read the placeholder's inert call in the listing's run
    alone (never, once, tested, behind the branch, again), or None."""
    alone = listing["signal_2"].get("alone") or {}
    for part in alone.get("parts") or []:
        if part["letter"] == placeholder:
            reading = part["reading"]
            return reading
    reading = None
    return reading


def listings_by_text(listings: list) -> dict:
    by_text = {}
    for listing in listings:
        by_text[listing["listing"]] = listing
    return by_text


# --- R1 roles


def derived_roles(listings: list, reasons: dict) -> dict:
    roles = {}
    for listing in listings:
        if not is_held_with_inert_parts(listing):
            continue
        roles[listing["listing"]] = roles_of_listing(listing, reasons)
    return roles


def roles_of_listing(listing: dict, reasons: dict) -> dict:
    roles = {}
    for placeholder in placeholders_of(listing["listing"]):
        role, why = role_of_placeholder(listing, placeholder)
        roles[placeholder] = role
        reasons[("roles", listing["listing"], placeholder)] = why
    return roles


def role_of_placeholder(listing: dict, placeholder: str) -> tuple:
    reading = reading_alone(listing, placeholder)
    if placeholder in NAME_PLACEHOLDERS:
        found = ("name", "a name: the record writes it as it is")
        return found
    if placeholder in constants_of(listing):
        found = ("constant", f"the record wrote it as a constant (fill {listing['fill']})")
        return found
    if placeholder in bodies_of(listing):
        why = listing["configuration"]["why"][placeholder]
        found = ("body", f"a body in the record: {why}")
        return found
    found = ("value", f"not a body in the record; alone it runs {reading}")
    return found


def constants_of(listing: dict) -> list:
    """The placeholders the record wrote as constants: every value the
    listing's components take, when its fill is `constant` (rule 35); and each
    fill override of form `constant` (rule 66)."""
    constants = []
    if listing.get("fill") == "constant":
        for component in listing["components"]:
            add_taken_values(constants, component)
    overrides = listing.get("fill_overrides") or {}
    for placeholder, override in overrides.items():
        if override.get("form") == "constant":
            constants.append(placeholder)
    return constants


def add_taken_values(found: list, component: dict) -> None:
    for placeholder in component["takes"]:
        if placeholder not in NAME_PLACEHOLDERS:
            found.append(placeholder)


# --- R2 expressions


def derived_expressions(listings: list, reasons: dict) -> tuple:
    names = []
    for listing in listings:
        if listing["is_statement"]:
            continue
        if not is_held_with_inert_parts(listing):
            continue
        add_listed_names(names, listing)
        reasons[("expressions", listing["listing"])] = f"an expression with N = {len(bodies_of(listing))} in the record"
    expressions = tuple(names)
    return expressions


def add_listed_names(names: list, listing: dict) -> None:
    for entry in listing["listed_as"]:
        if entry["name"] not in names:
            names.append(entry["name"])


# --- R3 jumps


def derived_jumps(listings: list, groups: list, reasons: dict) -> tuple:
    jumping_by_kind = {}
    for listing in listings:
        if not listing["is_statement"] or not is_held_with_inert_parts(listing):
            continue
        seen = next_line_seen(listing, groups)
        jumps = seen["ran"] == 0 and seen["never"] > 0
        by_listing = jumping_by_kind.setdefault(listing_kind(listing), {})
        by_listing[listing["listing"]] = jumps
        reasons[("jumps", listing["listing"])] = next_line_reason(seen, jumps)
    kinds = kinds_that_jump(jumping_by_kind)
    return kinds


def kinds_that_jump(jumping_by_kind: dict) -> tuple:
    """The kinds whose listings jump. The jumps are named by kind (as
    C_JUMPS_BY_HAND names them), so listings of one kind that differ stop the
    standard-form here rather than being guessed at."""
    kinds = []
    for kind, by_listing in jumping_by_kind.items():
        answers = set(by_listing.values())
        if len(answers) > 1:
            message = f"DRY_mask_maker: listings of {kind} differ on whether they jump: {by_listing}"
            raise ValueError(message)
        if True in answers:
            kinds.append(kind)
    jumps = tuple(kinds)
    return jumps


def next_line_seen(listing: dict, groups: list) -> dict:
    """How often the record saw the line right after the listing run, and how
    often it saw it never run: alone, and in the groups."""
    seen = {"ran": 0, "never": 0, "alone": "", "groups": 0}
    add_seen_alone(seen, listing)
    component = component_that_holds_nothing(listing)
    if component is None:
        return seen
    for group in groups:
        if listing["listing"] not in group["listings"]:
            continue
        add_seen_in_group(seen, group, component["component"])
    return seen


def add_seen_alone(seen: dict, listing: dict) -> None:
    """Each base run alone that returned: did the line after the listing run?
    Only when the listing's line is right before that line, with nothing it
    needs between them."""
    alone = listing["signal_2"].get("alone") or {}
    if not line_after_follows(alone.get("program") or ""):
        return
    for base, trace in sorted((alone.get("traces") or {}).items()):
        if not trace.endswith("(returned)"):
            continue
        if LINE_AFTER_IN_A_TRACE in trace:
            seen["ran"] += 1
            seen["alone"] += f"{base}: ran; "
        else:
            seen["never"] += 1
            seen["alone"] += f"{base}: never; "


def line_after_follows(program: str) -> bool:
    lines = []
    for line in program.split("\n"):
        lines.append(line.strip())
    if LINE_BEFORE not in lines:
        return False
    before = lines.index(LINE_BEFORE)
    follows = before + 2 < len(lines) and lines[before + 2] == LINE_AFTER
    return follows


def component_that_holds_nothing(listing: dict):
    """The listing's one component, when it holds nothing and is written (a
    block is written as nothing, the solver's rule 30); else None."""
    components = listing["components"]
    if len(components) != 1:
        component = None
        return component
    component = components[0]
    if component["holds"] or not component["written"]:
        component = None
        return component
    return component


def add_seen_in_group(seen: dict, group: dict, component_name: str) -> None:
    letter = letter_of(group, component_name)
    if letter is None:
        return
    for short in group["kept_arrangements"]:
        lines, levels, readings = decoded_arrangement(short)
        for position in range(len(lines) - 1):
            reading = next_inert_reading(lines, levels, readings, position, letter)
            if reading is None:
                continue
            seen["groups"] += 1
            if reading == NEVER_RAN:
                seen["never"] += 1
            else:
                seen["ran"] += 1


def next_inert_reading(lines: str, levels: str, readings: str, position: int, letter: str):
    """The reading of the inert call right after the component at `position`,
    at its own level (the next line of the same body), or None."""
    if lines[position] != letter:
        reading = None
        return reading
    if lines[position + 1] != INERT_LINE or levels[position + 1] != levels[position]:
        reading = None
        return reading
    number = lines[:position + 1].count(INERT_LINE)
    if number >= len(readings):
        # an arrangement kept and not run has no readings (rule 47)
        reading = None
        return reading
    reading = readings[number]
    return reading


def letter_of(group: dict, component_name: str):
    """The short form's letter for a component in a group (copies share it)."""
    for letter, names in group["letters"].items():
        if component_name in names:
            return letter
    letter = None
    return letter


def decoded_arrangement(short: str) -> tuple:
    """A kept arrangement in short form (rule 60): its lines, its levels, the
    reading of each inert number."""
    pieces = short.split("|")
    decoded = (pieces[0], pieces[1], pieces[2])
    return decoded


def next_line_reason(seen: dict, jumps: bool) -> str:
    said = "jumps" if jumps else "does not jump"
    alone = seen["alone"].rstrip("; ")
    if not alone:
        alone = "not seen"
    reason = (f"{said}: the next line seen run {seen['ran']} times, never run {seen['never']} times "
              f"(alone: {alone}; in the groups: {seen['groups']} kept arrangements with an inert call right "
              f"after it)")
    return reason


# --- R4 contexts


def derived_contexts(listings: list, groups: list, reasons: dict) -> tuple:
    by_text = listings_by_text(listings)
    contexts = {}
    names = {}
    for listing in listings:
        if listing.get("role") != "dependent":
            continue
        context, context_names, why = context_of_dependent(listing, by_text, groups)
        add_context(contexts, names, listing, context, context_names)
        reasons[("contexts", listing["listing"])] = why
    found = (contexts, names)
    return found


def add_context(contexts: dict, names: dict, listing: dict, context: str, context_names: dict) -> None:
    """The contexts are named by kind (as C_STATEMENT_CONTEXT_BY_HAND names
    them), so listings of one kind whose contexts differ stop the standard-form
    here rather than being guessed at."""
    kind = listing_kind(listing)
    if kind in contexts and (contexts[kind], names[kind]) != (context, context_names):
        message = f"DRY_mask_maker: listings of {kind} differ in their contexts: {contexts[kind]} and {context}"
        raise ValueError(message)
    contexts[kind] = context
    names[kind] = context_names


def context_of_dependent(listing: dict, by_text: dict, groups: list) -> tuple:
    holders = holders_that_keep(listing)
    if holders:
        found = context_in_a_holder(listing, holders, by_text, groups)
        return found
    needs = needs_of(listing, groups)
    context, context_names = needs_written_after(needs, by_text)
    why = (f"needs {', '.join(needs)} in the same function (the record's groups beside it); "
           f"after it, as its run alone writes them")
    found = (context, context_names, why)
    return found


def holders_that_keep(listing: dict) -> list:
    """The holder listings the record accepted it held in (rule 32), in the
    record's order."""
    holders = []
    for asked, answer in listing.get("fill_answers", {}).items():
        if not asked.startswith("held in ") or answer != "accepted":
            continue
        holder = asked[len("held in "):].rpartition(", ")[0]
        if holder not in holders:
            holders.append(holder)
    return holders


def fewest_placeholders(listing_texts: list) -> str:
    """The listing with the fewest placeholders; the first in order on a tie."""
    chosen = None
    for text in listing_texts:
        if chosen is None or len(placeholders_of(text)) < len(placeholders_of(chosen)):
            chosen = text
    return chosen


def context_in_a_holder(listing: dict, holders: list, by_text: dict, groups: list) -> tuple:
    holder = fewest_placeholders(holders)
    group, arrangement = context_arrangement(listing, holder, by_text, groups)
    context, context_names = context_written_from(arrangement, group, listing, holder, by_text)
    why = (f"kept only held in {', '.join(holders)}; {holder} has the fewest placeholders; written from "
           f"the group {group['group']!r} ({group['family']}), its kept arrangement {arrangement}")
    found = (context, context_names, why)
    return found


def context_arrangement(listing: dict, holder: str, by_text: dict, groups: list) -> tuple:
    """The record's smallest group holding the dependent and its holder in
    which the dependent's held line, when it holds one, runs behind the
    branch; and its first such kept arrangement."""
    chosen = None
    for position, group in enumerate(groups):
        if listing["listing"] not in group["listings"] or holder not in group["listings"]:
            continue
        arrangement = first_arrangement_for_the_context(group, listing, by_text[holder])
        if arrangement is None:
            continue
        size = group_size(group, listing, position)
        if chosen is None or size < chosen[0]:
            chosen = (size, group, arrangement)
    if chosen is None:
        message = f"DRY_mask_maker: no group of the record keeps {listing['listing']} in {holder} as its context needs"
        raise ValueError(message)
    found = (chosen[1], chosen[2])
    return found


def group_size(group: dict, listing: dict, position: int) -> tuple:
    """Fewest components, then fewest placeholders beside the dependent, then
    the record's order."""
    beside = 0
    for text in group["listings"]:
        if text != listing["listing"]:
            beside += len(placeholders_of(text))
    size = (len(group["components"]), beside, position)
    return size


def first_arrangement_for_the_context(group: dict, listing: dict, holder: dict):
    """The group's first kept arrangement in which the dependent stands in the
    holder, the holder at the top of the function (so what decides how the
    dependent's lines run is in the context written from it), and the
    dependent's held line, when it holds one, runs behind the branch. None
    when there is none."""
    component = listing["components"][0]
    letter = letter_of(group, component["component"])
    if letter is None:
        arrangement = None
        return arrangement
    for short in group["kept_arrangements"]:
        if not holder_at_the_top(short, letter, group, holder):
            continue
        if not component["holds"]:
            return short
        if held_line_runs_behind_the_branch(short, letter):
            return short
    arrangement = None
    return arrangement


def holder_at_the_top(short: str, letter: str, group: dict, holder: dict) -> bool:
    """Whether the dependent's first line stands in a line of the holder, and
    that line stands at the top of the function (level 0)."""
    lines, levels, readings = decoded_arrangement(short)
    position = lines.index(letter)
    top = holder_line_or_none(lines, levels, position, group, holder)
    at_the_top = top is not None and int(levels[top]) == 0
    return at_the_top


def held_line_runs_behind_the_branch(short: str, letter: str) -> bool:
    lines, levels, readings = decoded_arrangement(short)
    for position in range(len(lines) - 1):
        if lines[position] != letter or lines[position + 1] != INERT_LINE:
            continue
        if int(levels[position + 1]) != int(levels[position]) + 1:
            continue
        number = lines[:position + 1].count(INERT_LINE)
        if number < len(readings) and readings[number] in BEHIND_THE_BRANCH:
            return True
    return False


def context_written_from(short: str, group: dict, listing: dict, holder: str, by_text: dict) -> tuple:
    """The holder and what stands in it in the arrangement, as a context: the
    holder's component as its listing writes it, its value `{1}`, its held
    lines in a block; the dependent `{0}` (its own held lines are its own
    parts); another component as written, a constant it takes `{2}`, a body it
    holds `{ }` or its one inert line `{3}`."""
    lines, levels, readings = decoded_arrangement(short)
    components = components_of_group(group, by_text)
    dependent = letter_of(group, listing["components"][0]["component"])
    position = lines.index(dependent)
    top = holder_line(lines, levels, position, group, by_text[holder])
    holder_component = components[letter_name(group, lines[top])]
    names = {}
    holder_text = written_with_holes(holder_component, by_text[holder], "{1}")
    if "{1}" in holder_text:
        names["value"] = keyword_of(holder_component)
    inner = context_lines(lines, levels, top, dependent, group, components, names)
    context = f"{holder_text} {{{{ {inner} }}}}"
    found = (context, names)
    return found


def components_of_group(group: dict, by_text: dict) -> dict:
    """Each component of the group's listings by its name, with the listing it
    comes from."""
    components = {}
    for text in group["listings"]:
        for component in by_text[text]["components"]:
            entry = dict(component)
            entry["listing_record"] = by_text[text]
            components[component["component"]] = entry
    return components


def letter_name(group: dict, letter: str) -> str:
    """The component a letter stands for (a copy's name ends `, second`)."""
    name = group["letters"][letter][0]
    return name


def holder_line(lines: str, levels: str, position: int, group: dict, holder: dict) -> int:
    """The line of the holder's component the dependent stands in."""
    top = holder_line_or_none(lines, levels, position, group, holder)
    if top is None:
        message = f"DRY_mask_maker: no holder line above the dependent in {lines}"
        raise ValueError(message)
    return top


def holder_line_or_none(lines: str, levels: str, position: int, group: dict, holder: dict):
    """The nearest line before the dependent's, at a lower level, that is one
    of the holder's components; None when the dependent stands in none."""
    holder_names = []
    for component in holder["components"]:
        holder_names.append(component["component"])
    level = int(levels[position])
    for top in range(position - 1, -1, -1):
        if int(levels[top]) >= level or lines[top] == INERT_LINE:
            continue
        if letter_name(group, lines[top]) in holder_names:
            return top
        level = int(levels[top])
    top = None
    return top


def context_lines(lines: str, levels: str, top: int, dependent: str, group: dict, components: dict,
                  names: dict) -> str:
    """What stands in the holder's body, line by line, one level under it."""
    pieces = []
    level = int(levels[top]) + 1
    holder_component = components[letter_name(group, lines[top])]
    position = top + 1
    while position < len(lines) and int(levels[position]) >= level:
        piece, position = context_line(lines, levels, position, dependent, group, components, names,
                                       holder_component)
        pieces.append(piece)
    inner = " ".join(pieces)
    return inner


def context_line(lines: str, levels: str, position: int, dependent: str, group: dict, components: dict,
                 names: dict, holder_component: dict) -> tuple:
    """One line in the holder's body and the position after what it holds."""
    after = end_of_held_lines(levels, position)
    if lines[position] == dependent:
        found = ("{0}", after)
        return found
    if lines[position] == INERT_LINE:
        add_held_name(names, holder_component)
        found = ("{3};", after)
        return found
    component = components[letter_name(group, lines[position])]
    text = written_with_holes(component, component["listing_record"], None)
    held = held_block(lines, levels, position, after, component, names)
    found = (f"{text} {held}".strip(), after)
    return found


def add_held_name(names: dict, component: dict) -> None:
    """The name of the inert call for the one line a context holds: the
    keyword of the component that holds it. A second such line stops the
    standard-form here rather than being guessed at."""
    if "held" in names:
        message = "DRY_mask_maker: a context holds two lines; the standard-form writes one"
        raise ValueError(message)
    names["held"] = keyword_of(component)


def end_of_held_lines(levels: str, position: int) -> int:
    after = position + 1
    while after < len(levels) and int(levels[after]) > int(levels[position]):
        after += 1
    return after


def held_block(lines: str, levels: str, position: int, after: int, component: dict, names: dict) -> str:
    """A body the component holds: `{ }` when it holds nothing, `{ {3}; }` for
    its one inert line; its listing's own end when it holds no body."""
    if not component["holds"]:
        block = component["ends_with"]
        return block
    held_lines = lines[position + 1:after]
    if held_lines == "":
        block = "{{ }}"
        return block
    if held_lines != INERT_LINE:
        message = f"DRY_mask_maker: a context's component holds {held_lines!r}; the standard-form writes one inert line"
        raise ValueError(message)
    add_held_name(names, component)
    block = "{{ {3}; }}"
    return block


def written_with_holes(component: dict, listing: dict, value_hole) -> str:
    """A component as its listing writes it: a name as it is; a value it takes
    as `{2}` when its listing's fill is constant, else as `value_hole` (one at
    most; a component given no value hole that takes a value stops the
    standard-form here rather than being guessed at)."""
    text = component["written"]
    holes = 0
    for placeholder in component["takes"]:
        if placeholder in NAME_PLACEHOLDERS:
            continue
        hole = value_hole
        if listing.get("fill") == "constant":
            hole = "{2}"
        if hole is None:
            message = f"DRY_mask_maker: {component['component']} takes a value in a context; no rule holds it"
            raise ValueError(message)
        text = re.sub(r"\b" + placeholder + r"\b", hole, text, count=1)
        holes += 1
    if holes > 1:
        message = f"DRY_mask_maker: a context's component takes {holes} values; the standard-form writes one"
        raise ValueError(message)
    return text


def keyword_of(component: dict) -> str:
    """A component's keyword: its first word that is not a placeholder; a
    component with none is a label (the solver's rule 7)."""
    for word in re.findall(r"\w+", component["written"]):
        if word not in VALUE_PLACEHOLDERS and word not in NAME_PLACEHOLDERS and word not in TYPE_PLACEHOLDERS:
            return word
    keyword = NO_KEYWORD
    return keyword


def needs_of(listing: dict, groups: list) -> list:
    """What the dependent needs in the same function: the listings beside it in
    every one of its groups of two with a holder (the record's pairs, rule 41;
    a holder that is itself what it needs is not written twice there), in the
    order the record lists them."""
    needs = None
    for group in groups:
        if group.get("dependent") != listing["listing"] or group["family"] != "pair":
            continue
        needs = beside_in_every_group(needs, group, listing["listing"])
    if not needs:
        message = f"DRY_mask_maker: {listing['listing']} is kept in no holder and needs nothing in the record"
        raise ValueError(message)
    return needs


def beside_in_every_group(needs, group: dict, dependent: str) -> list:
    """The listings beside the dependent in this group that were beside it in
    every group before (all of them, for the first group)."""
    beside = []
    for text in group["listings"]:
        if text == dependent:
            continue
        if needs is None or text in needs:
            beside.append(text)
    return beside


def needs_written_after(needs: list, by_text: dict) -> tuple:
    """`{0}`, then each listing it needs as its own text: a name as it is, a
    statement it holds as `{3}` (one at most), an expression standing as a line
    with its `;` (the solver's rules 31 and 33)."""
    names = {}
    pieces = ["{0}"]
    for text in needs:
        pieces.append(own_text_with_holes(by_text[text], names))
    context = " ".join(pieces)
    found = (context, names)
    return found


def own_text_with_holes(listing: dict, names: dict) -> str:
    text = listing["listing"]
    for component in listing["components"]:
        for placeholder in component["holds"]:
            add_held_name(names, component)
            text = re.sub(r"\b" + placeholder + r"\b", "{3}", text, count=1)
        for placeholder in component["takes"]:
            if placeholder not in NAME_PLACEHOLDERS:
                message = f"DRY_mask_maker: {listing['listing']} takes a value; the standard-form has no rule for it here"
                raise ValueError(message)
    if not listing["is_statement"]:
        text = text + ";"
    return text


# --- R5 part contexts


def derived_part_contexts(listings: list, groups: list, reasons: dict) -> dict:
    by_text = listings_by_text(listings)
    part_contexts = {}
    for listing in listings:
        if not is_held_with_inert_parts(listing):
            continue
        for placeholder in parts_never_reached(listing):
            template, why = part_context_of(listing, listings, groups)
            part_contexts.setdefault(listing["listing"], {})[placeholder] = template
            reasons[("part_contexts", listing["listing"], placeholder)] = why
    return part_contexts


def parts_never_reached(listing: dict) -> list:
    """The listing's parts that a component holds and that never ran alone."""
    found = []
    held_by = (listing.get("configuration") or {}).get("held_by") or {}
    for placeholder in held_by:
        if reading_alone(listing, placeholder) == "never":
            found.append(placeholder)
    return found


def part_context_of(listing: dict, listings: list, groups: list) -> tuple:
    candidates = []
    for dependent in listings:
        if dependent.get("role") != "dependent":
            continue
        if holders_that_keep(dependent) != [listing["listing"]]:
            continue
        if held_line_runs_in_its_pair(dependent, listing, groups):
            candidates.append(dependent["listing"])
    if not candidates:
        message = f"DRY_mask_maker: no dependent-HiOp of {listing['listing']} lets its part run"
        raise ValueError(message)
    chosen = fewest_placeholders(candidates)
    template = "{{ " + own_text_around_the_part(listings_by_text(listings)[chosen]) + " }}"
    why = (f"never runs alone; stands in {chosen}, kept only inside {listing['listing']}, whose held line runs "
           f"behind the branch in their group of two (of {', '.join(candidates)}, the fewest placeholders)")
    found = (template, why)
    return found


def held_line_runs_in_its_pair(dependent: dict, listing: dict, groups: list) -> bool:
    for group in groups:
        if sorted(group["listings"]) != sorted([dependent["listing"], listing["listing"]]):
            continue
        if first_arrangement_for_the_context(group, dependent, listing) is not None:
            return True
    return False


def own_text_around_the_part(dependent: dict) -> str:
    """The dependent's own text, its held statement the part `{0}`, a constant
    it takes `{2}`."""
    text = dependent["listing"]
    for component in dependent["components"]:
        for placeholder in component["holds"]:
            text = re.sub(r"\b" + placeholder + r"\b", "{0}", text, count=1)
        for placeholder in component["takes"]:
            if placeholder in NAME_PLACEHOLDERS:
                continue
            text = re.sub(r"\b" + placeholder + r"\b", "{2}", text, count=1)
    return text


# --- R6 function answers


def derived_function_answers(listings: list, roles: dict, reasons: dict) -> dict:
    answers = {}
    for listing in listings:
        if listing["listing"] not in roles:
            continue
        returns = listing.get("context", "").split(" f(")[0]
        if returns == "void":
            continue
        placeholder = first_value_placeholder(roles[listing["listing"]])
        answers[listing["listing"]] = placeholder
        reasons[("function_answers", listing["listing"])] = (f"the record ran it in `{listing['context']}`, a "
                                                            f"function that answers a value")
    return answers


def first_value_placeholder(roles: dict):
    for placeholder, role in roles.items():
        if role == "value":
            return placeholder
    placeholder = None
    return placeholder


# --- R7 local answers


def derived_local_answers(listings: list, reasons: dict) -> dict:
    answers = {}
    for listing in listings:
        if listing["is_statement"] or listing.get("role") != "dependent":
            continue
        for entry in listing["listed_as"]:
            answers[entry["name"]] = listing["listing"]
        reasons[("local_answers", listing["listing"])] = (f"an expression the record keeps as a dependent-HiOp: "
                                                         f"{listing.get('without_what_it_needs')} without what it "
                                                         f"needs")
    return answers


# The routing the standard-form uses, read from the record; and the routing by
# hand, the check. The tables' names before log 424 (INERT_PART_ROLES,
# INERT_PART_EXPRESSIONS, C_JUMPS, C_STATEMENT_CONTEXT) are not kept for the
# routing from the record: its tables are ROUTING's fields, and the names with
# _BY_HAND are the tables by hand, so a reader of an old name stops by name
# rather than reading the other table.
ROUTING = routing_from_the_record()
ROUTING_BY_HAND = routing_by_hand()


def write_holder_check(lang: str, holders: tuple, path: str) -> list:
    """One struct per holder, each keeping one field of it. Returns the line
    each holder's field sits on."""
    lines = list(PREAMBLE[lang])
    line_of_holder = []
    for position, holder in enumerate(holders):
        if lang == "go":
            lines.append(f"type H_{position} struct {{ a {holder.spelling} }}")
        elif lang == "rust":
            lines.append(f"#[repr(C)] pub struct H_{position} {{ pub a: {holder.spelling} }}")
        elif lang == "java":
            lines.append(f"final class H_{position} {{ {holder.spelling} a; }}")
        else:
            lines.append(f"struct H_{position} {{ {holder.spelling} a; }};")
        line_of_holder.append(len(lines))
    with open(path, "w", encoding="utf-8") as check_file:
        check_file.write("\n".join(lines) + "\n")
    return line_of_holder


def write_cells(lang: str, operators: tuple, holders: tuple, cells: list, path: str,
                declarations: tuple = ()) -> list:
    """The standard form of every cell in one file, after the preamble and any
    `declarations` (library_declarations). Returns each cell's first line;
    its second line follows it."""
    lines = list(PREAMBLE[lang]) + list(declarations)
    first_line_of_cell = []
    for position, cell in enumerate(cells):
        operator = operators[cell.operator]
        spellings = []
        for holder_position in cell.holders:
            spellings.append(holders[holder_position].spelling)
        key = f"{cell.operator}_{'_'.join(str(h) for h in cell.holders)}"
        first_line_of_cell.append(len(lines) + 1)
        lines.extend(standard_cell_lines(lang, key, operator, tuple(spellings)))
    with open(path, "w", encoding="utf-8") as cell_file:
        cell_file.write("\n".join(lines) + "\n")
    return first_line_of_cell


# A library function among clang's builtins (abs, printf, sin) is accepted
# only after its declaration, which a program takes from its header. clang
# names the type it expects in the refusal: "call to undeclared library
# function 'abs' with type 'int (int)'" (DiagnosticSemaKinds.td line 822),
# and only at the first call in a file. So one probe file calls each builtin
# once, and every held file then starts with the declarations clang asked
# for, as the headers would give them. A type C cannot declare as written (a
# reference, `__builtin_va_list &`, which clang gives va_start) is left out,
# and its builtin stays refused.
C_UNDECLARED_LIBRARY = re.compile(r"call to undeclared library function '(?P<name>[^']+)' with type '(?P<type>[^']+)'")


def declaration_from_type(name: str, function_type: str) -> Optional[str]:
    """`int (int)` and `abs` -> `int abs(int);`: the name goes before the
    parameter list. None when the type cannot be written that way (its
    return type holds a parenthesis, or a parameter is a reference)."""
    if "&" in function_type:
        return None
    opening = function_type.find("(")
    if opening <= 0:
        return None
    depth = 0
    for index in range(opening, len(function_type)):
        if function_type[index] == "(":
            depth += 1
        elif function_type[index] == ")":
            depth -= 1
            if depth == 0:
                break
    else:
        return None
    returns = function_type[:opening].rstrip()
    after = function_type[index + 1:].strip()
    if after and not after.startswith("__attribute__"):
        return None
    joiner = "" if returns.endswith("*") else " "
    declaration = f"{returns}{joiner}{name}{function_type[opening:index + 1]}{(' ' + after) if after else ''};"
    return declaration


def library_declarations(lang: str, operators: tuple, directory: str) -> tuple:
    """The declarations clang asks for before the builtins among `operators`
    that are library functions: one probe call each, read from clang's
    refusals. Empty for a language other than c."""
    if lang != "c":
        return ()
    names = sorted({builtin_name(operator) for operator in operators if is_builtin_call(operator)})
    if not names:
        return ()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"library_probe{SUFFIX[lang]}")
    lines = list(PREAMBLE[lang])
    for number, name in enumerate(names):
        lines.append(f"void probe_{number}(void) {{ (void){name}(); }}")
    with open(path, "w", encoding="utf-8") as probe:
        probe.write("\n".join(lines) + "\n")
    diagnostics_path = f"{path}.diag"
    run_judge(lang, path, diagnostics_path, timeout=JUDGE_SECONDS)
    declared = {}
    with open(diagnostics_path, encoding="utf-8", errors="replace") as diagnostics:
        for line in diagnostics:
            found = C_UNDECLARED_LIBRARY.search(line)
            if found and found.group("name") not in declared:
                declaration = declaration_from_type(found.group("name"), found.group("type"))
                if declaration is not None:
                    declared[found.group("name")] = declaration
    return tuple(declared[name] for name in sorted(declared))


def refusals_by_line(lang: str, diagnostics_path: str) -> dict:
    """line -> the first error the lowerer wrote about that line."""
    refusals = {}
    pattern = DIAGNOSTIC[lang]
    with open(diagnostics_path, encoding="utf-8", errors="replace") as diagnostics:
        for line in diagnostics:
            match = pattern.match(line.rstrip("\n"))
            if match is None:
                continue
            line_number = int(match.group("line"))
            if line_number not in refusals:
                refusals[line_number] = match.group("message")
    return refusals


def verdicts_of_lines(lang: str, first_lines: list, lines_per_item: int, diagnostics_path: str, evidence: str) -> list:
    """One Verdict per item written at `first_lines`, from the diagnostics
    the lowerer wrote about the file."""
    refusals = refusals_by_line(lang, diagnostics_path)
    with open(diagnostics_path, encoding="utf-8", errors="replace") as diagnostics:
        written = diagnostics.read()
    if "error" in written.lower() and not refusals:
        message = (f"DRY_mask_maker: {diagnostics_path} reports an error, but no line of it reads as a "
                   f"refusal; nothing is taken as accepted")
        raise RuntimeError(message)
    verdicts = []
    for first_line in first_lines:
        refusal = None
        for line_number in range(first_line, first_line + lines_per_item):
            if line_number in refusals:
                refusal = refusals[line_number]
                break
        if refusal is None:
            verdict = Verdict(True, None, evidence)
        else:
            verdict = Verdict(False, None, f"{evidence}: {refusal}")
        verdicts.append(verdict)
    return verdicts


def read_syntax_trees(ast_path: str) -> dict:
    """function name -> its syntax tree, from clang's filtered JSON dump,
    which is one JSON document per function, one after another."""
    with open(ast_path, encoding="utf-8") as ast_file:
        text = ast_file.read()
    decoder = json.JSONDecoder()
    trees = {}
    position = 0
    while position < len(text):
        while position < len(text) and text[position] in " \n\r\t":
            position += 1
        if position >= len(text):
            break
        tree, position = decoder.raw_decode(text, position)
        if tree.get("kind") == "FunctionDecl":
            trees[tree.get("name")] = tree
    return trees


def through(node: dict, never_written: set) -> dict:
    """The node, looking through every node a program never writes -- the
    lowerer's own conversions and temporaries."""
    while node.get("kind") in never_written and node.get("inner"):
        node = node["inner"][0]
    return node


def parsed_kind(trees: dict, function_name: str, never_written: set) -> tuple:
    """(kind, opcode) the lowerer parsed `p->result = (...)` 's right side
    as, in the function `function_name`: through the nodes a program never
    writes, and through the one parenthesis the standard form adds. The opcode
    is None for a kind that has none."""
    function = trees.get(function_name)
    if function is None:
        return ("no such function in the tree", None)
    body = function["inner"][-1]
    assignment = through(body["inner"][0], never_written)
    right_side = through(assignment["inner"][-1], never_written)
    if right_side.get("kind") != "ParenExpr":
        return (f"not the standard form: {right_side.get('kind', 'unknown')}", None)
    applied = through(right_side["inner"][0], never_written)
    kind = applied.get("kind", "unknown")
    opcode = applied.get("opcode")
    return (kind, opcode)


def parsed_as_written(operator, kind: str, opcode) -> bool:
    """Whether a cell of `operator` parsed as that operator: the same kind,
    or, for an opcode operator, an opcode kind carrying the very opcode its
    template writes. An operator read from one of the lowerer's lists is
    named `Kind.Entry` (`UnaryExprOrTypeTraitExpr.SizeOf`); its kind is the
    part before the dot.

    ADJACENT, NOT YET CODED: this compares the kind, or the opcode, never
    both, so an entry clang builds as another kind with the same opcode
    passes (`a *= b` under `BinaryOperator.MulAssign`); log 310 section 2."""
    if kind == operator.name.split(".")[0]:
        return True
    if opcode is None:
        return False
    written = operator.spelling
    for placeholder in operator.operands:
        written = re.sub(r"\b" + placeholder + r"\b", "", written)
    same_opcode = written.replace(" ", "") == opcode
    return same_opcode


# Where the verdicts already given are kept, one JSON line per cell, by the
# operator's and the holders' own names (never their positions, which move
# when a list changes): <directory>/<lang>.knowns.jsonl.gz, compressed (C's
# 394,000 verdicts are 97 MB as text, 2.4 MB compressed; a file over 100 MB
# cannot be pushed). Configuration, as PSEUDOARCH_SOURCES is.
KNOWNS_VARIABLE = "PSEUDOARCH_KNOWNS"
CELLS_PER_FILE = 20000


def judged_under(lang: str) -> str:
    """What a verdict is given under: the lowerer's command and, for c, the
    standard form's stand-in and result type. A verdict kept under anything else
    is not known, so it is judged again (the knowns once kept no such mark,
    and the change of stand-in in ."""
    under = JUDGE_COMMAND[lang]
    if lang == "c":
        under = f"{under} | {C_STAND_IN} | {C_RESULT_TYPE} | {C_LIBRARY_RULE}"
    return under


def cell_identity(cell: Cell, operators: tuple, holders: tuple) -> tuple:
    """What a cell IS, independent of where its operator and holders sit in
    the two lists: the operator's name and template, and each holder's name
    and spelling."""
    operator = operators[cell.operator]
    held = tuple((holders[h].name, holders[h].spelling) for h in cell.holders)
    identity = (operator.name, operator.spelling, held)
    return identity


def knowns_path(lang: str) -> Optional[str]:
    directory = os.environ.get(KNOWNS_VARIABLE)
    if directory is None:
        return None
    path = os.path.join(directory, f"{lang}.knowns.jsonl.gz")
    return path


def knowns(lang: str, cells: tuple, operators: tuple = (), holders: tuple = ()) -> dict:
    """Cell -> Verdict, for every cell already judged: read from the knowns
    file, matched by identity. `operators` and `holders` are the lists the
    cells' positions refer to. With no knowns file, nothing is known."""
    path = knowns_path(lang)
    if path is None or not os.path.exists(path):
        return {}
    given = {}
    under = judged_under(lang)
    with gzip.open(path, "rt", encoding="utf-8") as kept:
        for line in kept:
            record = json.loads(line)
            if record.get("under") != under:
                continue
            identity = (record["operator"], record["template"],
                        tuple(tuple(pair) for pair in record["holders"]))
            given[identity] = Verdict(record["accepted"], None, record["evidence"])
    known = {}
    for cell in cells:
        verdict = given.get(cell_identity(cell, operators, holders))
        if verdict is not None:
            known[cell] = verdict
    return known


def record_knowns(lang: str, judged: dict, operators: tuple, holders: tuple) -> None:
    """Add the verdicts just given to the knowns file, so no cell is judged
    twice."""
    path = knowns_path(lang)
    if path is None:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    under = judged_under(lang)
    with gzip.open(path, "at", encoding="utf-8") as kept:
        for cell, verdict in judged.items():
            operator_name, template, held = cell_identity(cell, operators, holders)
            record = {"operator": operator_name, "template": template, "holders": [list(pair) for pair in held],
                      "accepted": verdict.accepted, "evidence": verdict.evidence, "under": under}
            kept.write(json.dumps(record) + "\n")


# A file the lowerer has not finished in this many seconds is cut where its
# diagnostics stop (clang 21 did not finish one held cell in C mode, PCHQ
# log 367); a held file of 20,000 cells takes seconds.
JUDGE_SECONDS = 120


def judge_one_file(lang: str, operators: tuple, holders: tuple, cells: list, path: str, evidence: str,
                   declarations: tuple = ()) -> list:
    """One file of cells through the lowerer: write it, judge it, read each
    cell's verdict from what the lowerer wrote about its two lines. A verdict
    is None where the lowerer did not finish: if it stops answering, the
    cells before its last diagnostic keep their verdicts, the next cell is
    the one it did not finish (None), and the cells after it are judged again
    in a file of their own."""
    first_lines = write_cells(lang, operators, holders, cells, path, declarations)
    diagnostics_path = f"{path}.diag"
    try:
        exit_code = run_judge(lang, path, diagnostics_path, timeout=JUDGE_SECONDS)
    except subprocess.TimeoutExpired:
        refusals = refusals_by_line(lang, diagnostics_path)
        last_line = max(refusals) if refusals else 0
        passed = [i for i, first_line in enumerate(first_lines) if first_line + 1 <= last_line]
        verdicts = [None] * len(cells)
        if passed:
            partial = verdicts_of_lines(lang, [first_lines[i] for i in passed], 2, diagnostics_path, evidence)
            for i, verdict in zip(passed, partial):
                verdicts[i] = verdict
        stuck = len(passed)
        rest = cells[stuck + 1:]
        if rest:
            again = judge_one_file(lang, operators, holders, rest, f"{path}.after{stuck}{SUFFIX[lang]}", evidence,
                                   declarations)
            verdicts[stuck + 1:] = again
        return verdicts
    verdicts = verdicts_of_lines(lang, first_lines, 2, diagnostics_path, evidence)
    refused = sum(1 for verdict in verdicts if not verdict.accepted)
    if exit_code != 0 and refused == 0:
        message = (f"DRY_mask_maker: the lowerer exited {exit_code} on {path} but no refusal could be read "
                   f"from {diagnostics_path}; nothing is taken as accepted")
        raise RuntimeError(message)
    return verdicts


def judge(lang: str, cells: tuple, operators: tuple = (), holders: tuple = (),
          directory: str = ".", evidence: str = "", workers: int = 4, declarations: tuple = ()) -> dict:
    """Cell -> Verdict, from the lowerer itself, many cells per file.

    Where the lowerer runs on this machine, this is write_cells, then
    JUDGE_COMMAND over the file, then verdicts_of_lines, for each file of
    CELLS_PER_FILE cells, `workers` files at a time. Where it runs
    elsewhere, the three are called on either side of the run. Every file
    starts with `declarations` (library_declarations)."""
    from concurrent.futures import ProcessPoolExecutor
    cells = list(cells)
    files = []
    for start in range(0, len(cells), CELLS_PER_FILE):
        number = len(files)
        path = os.path.join(directory, f"cells_{number:03d}{SUFFIX[lang]}")
        files.append((cells[start:start + CELLS_PER_FILE], path))
    judged = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = []
        for chosen, path in files:
            label = f"{evidence} {os.path.basename(path)}".strip()
            futures.append((chosen, pool.submit(judge_one_file, lang, operators, holders, chosen, path, label,
                                                declarations)))
        for chosen, future in futures:
            for cell, verdict in zip(chosen, future.result()):
                if verdict is not None:
                    judged[cell] = verdict
    return judged


def judge_holders(lang: str, holders: tuple, directory: str, evidence: str) -> list:
    """One Verdict per holder: can a program keep a value of it in a field
    of the held struct? A holder refused here is refused in every cell."""
    path = os.path.join(directory, f"holders{SUFFIX[lang]}")
    lines = write_holder_check(lang, holders, path)
    diagnostics_path = f"{path}.diag"
    run_judge(lang, path, diagnostics_path)
    verdicts = verdicts_of_lines(lang, lines, 1, diagnostics_path, evidence)
    return verdicts


def make_mask(lang: str, operators: tuple, holders: tuple, directory: str = ".", evidence: str = "", workers: int = 4):
    """Makes grid_mask_of_knowns: the grid for `lang`, every cell with the
    lowerer's verdict. (Named by the owner, 2026-10-01; it was
    `grid_mask_of_knowns()`, the data structure's own name.)

        kept   = holders the held struct can keep a field of
        cells  = grid(operators, kept)
        known  = knowns(lang, cells)
        judged = judge(lang, cells - known), each library builtin declared
                 as the lowerer asks
        mask   = known + judged
    """
    os.makedirs(directory, exist_ok=True)
    holder_verdicts = judge_holders(lang, holders, directory, f"{evidence} holders".strip())
    kept = [position for position, verdict in enumerate(holder_verdicts) if verdict.accepted]
    kept_holders = tuple(holders[position] for position in kept)
    cells = []
    for cell in grid(operators, kept_holders):
        cells.append(Cell(cell.operator, tuple(kept[h] for h in cell.holders)))
    known = knowns(lang, cells, operators, holders)
    unknown = [cell for cell in cells if cell not in known]
    declarations = library_declarations(lang, operators, directory)
    judged = judge(lang, unknown, operators, holders, directory, evidence, workers, declarations)
    record_knowns(lang, judged, operators, holders)
    verdicts = dict(known)
    verdicts.update(judged)
    mask = Mask(lang, operators, holders, holder_verdicts, cells, verdicts)
    return mask


class Mask:
    """The grid, with a Verdict on every cell."""

    def __init__(self, lang: str, operators: tuple, holders: tuple, holder_verdicts: list,
                 cells: list, verdicts: dict):
        self.lang = lang
        self.operators = operators
        self.holders = holders
        self.holder_verdicts = holder_verdicts
        self.cells = cells
        self.verdicts = verdicts

    def accepted(self) -> Iterator[Variant]:
        """Every accepted cell, as a HiOp variant."""
        for cell in self.cells:
            verdict = self.verdicts.get(cell)
            if verdict is not None and verdict.accepted:
                held = tuple(self.holders[h] for h in cell.holders)
                yield Variant(self.lang, self.operators[cell.operator], held, None, verdict.evidence)

    def refused(self) -> Iterator[Cell]:
        """Every refused cell. Its Verdict carries the lowerer's refusal."""
        for cell in self.cells:
            verdict = self.verdicts.get(cell)
            if verdict is not None and not verdict.accepted:
                yield cell

    def unknown(self) -> Iterator[Cell]:
        """Cells with no verdict yet. Empty once the mask is complete."""
        for cell in self.cells:
            if cell not in self.verdicts:
                yield cell


def judge_until_parsed(lang: str, items: list, write, lines_per_item: int, path: str, evidence: str) -> list:
    """One Verdict per item, judged where the lowerer runs on this machine.

    `write(items, path)` writes the items and returns each one's first line.
    A lowerer that stops at a syntax error (SYNTAX_REFUSAL) leaves the rest
    of the file unjudged, so after a pass with any syntax refusal, those
    items keep that refusal and every other item is judged again, alone,
    until a pass has none. Each pass keeps its own diagnostics file."""
    verdicts = [None] * len(items)
    remaining = list(range(len(items)))
    prefix = SYNTAX_REFUSAL.get(lang)
    passes = 0
    while remaining:
        passes += 1
        chosen = []
        for position in remaining:
            chosen.append(items[position])
        first_lines = write(chosen, path)
        diagnostics_path = f"{path}.pass{passes}.diag"
        exit_code = run_judge(lang, path, diagnostics_path)
        judged = verdicts_of_lines(lang, first_lines, lines_per_item, diagnostics_path, f"{evidence}, pass {passes}")
        refused = 0
        for verdict in judged:
            if not verdict.accepted:
                refused += 1
        if exit_code != 0 and refused == 0:
            message = (f"DRY_mask_maker: the lowerer exited {exit_code} on {path} but no refusal "
                       f"could be read from {diagnostics_path}; nothing is taken as accepted")
            raise RuntimeError(message)
        judge_again = []
        for position, verdict in zip(remaining, judged):
            verdicts[position] = verdict
            refused_for_syntax = prefix is not None and not verdict.accepted and prefix in verdict.evidence
            if not refused_for_syntax:
                judge_again.append(position)
        if len(judge_again) == len(remaining):
            break
        remaining = judge_again
    return verdicts


# An interpreter judges by running. python's cells run IN the python that
# judges. Each operand is a fresh value of its holder, made the way the
# language makes a value of a type given nothing, `T()`; the operator is
# applied over the fields of a held object, as the compiled languages apply
# it over the fields of a held struct. A TypeError is the language refusing
# the types. Any other outcome -- a value, or another exception such as
# ZeroDivisionError -- is the types accepted: the refusal of a VALUE is not
# the refusal of a type.
PYTHON_STATEMENT_PREFIX = "AugAssign."


class PythonHeld:
    """The held object: the operands are its fields, and the caller owns it."""

    __slots__ = ("a", "b", "c", "d")


def python_fresh(spelling: str):
    """A fresh value of the built-in type `spelling`, made as T()."""
    import builtins
    kind = getattr(builtins, spelling)
    value = kind()
    return value


def judge_python_holders(holders: tuple) -> list:
    """One Verdict per holder: can the language make a value of it given
    nothing? A holder it cannot is refused in every cell."""
    verdicts = []
    for holder in holders:
        try:
            python_fresh(holder.spelling)
        except Exception as problem:
            verdicts.append(Verdict(False, None, f"{type(problem).__name__}: {problem}"))
            continue
        verdicts.append(Verdict(True, None, "T() made a value"))
    return verdicts


def python_code(operator):
    """(code, refusal): the operator over the held object's fields, compiled
    once. A statement kind runs as itself; an expression is kept in `r`."""
    fields = {"a": "p.a", "b": "p.b", "c": "p.c", "d": "p.d"}
    applied = filled(operator.spelling, fields)
    text = applied if operator.name.startswith(PYTHON_STATEMENT_PREFIX) else f"r = ({applied})"
    try:
        code = compile(text, f"<{operator.name}>", "exec")
    except SyntaxError as problem:
        return None, f"SyntaxError: {problem.msg}"
    return code, None


def judge_python_cell(code, operator, spellings: tuple) -> Verdict:
    """One cell, run: fresh operands in the held object, the operator over
    them."""
    import warnings
    held = PythonHeld()
    for placeholder, spelling in zip(operator.operands, spellings):
        setattr(held, placeholder, python_fresh(spelling))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            exec(code, {"p": held})
        except TypeError as problem:
            return Verdict(False, None, f"TypeError: {problem}")
        except Exception as problem:
            return Verdict(True, None, f"accepted; this value raised {type(problem).__name__}")
    return Verdict(True, None, "accepted")


def run_judge(lang: str, source_path: str, diagnostics_path: str, timeout: Optional[float] = None) -> int:
    """JUDGE_COMMAND over one file, everything it writes kept beside it:
    clang writes its diagnostics to standard error, go's compiler to
    standard output, so both go to the one file. With a timeout, a lowerer
    that has not finished is stopped and TimeoutExpired raised."""
    command = shlex.split(JUDGE_COMMAND[lang]) + [source_path]
    with open(diagnostics_path, "w", encoding="utf-8") as diagnostics:
        finished = subprocess.run(command, stdout=diagnostics, stderr=subprocess.STDOUT, check=False,
                                  timeout=timeout)
    return finished.returncode


# ADJACENT, NOT YET CODED:
#
#   Where the knowns come from today: the probe runs of record, per
#   language -- every cell already lowered or refused, placed at its
#   position by the lowerer's own names for the operator and the holders.
#   The stdint names those probes use (`int32_t`) are the lowerer's
#   typedefs of its builtin types; which builtin each one is, the lowerer
#   can say (`__builtin_types_compatible_p`).
#
#   The pairings a language writes down as data (java, dart, rust, swift,
#   ruby, csharp, go, and php for long and double) are an ORACLE here. A
#   judged cell that disagrees with its language's own pairing is a
#   finding, never a correction to either side.
#
#   An interpreter judges by running: one process per language, one
#   attempt per cell, the raised error recorded as the refusal. It runs the
#   language, so it goes through Airlock.
#
#   A refusal can belong to the standard form rather than to the language: a
#   cast to `void` is legal, but no struct can hold its void result, and a
#   sizeless vector type cannot be a field at all. Those refusals are kept
#   with their words, so the form can be answered for separately.
#
#   `lower_HiOp` already refuses what the lowerer declines. Judging with the
#   type checker first costs one cheap pass per language and keeps refused
#   cells out of compile-and-carve; sending every unknown cell straight to
#   `lower_HiOp` costs nothing extra up front. Either fills the same mask.
#
#   What "changed" means for churn: the source line that declares an
#   operator or a holder, hashed. A cell is judged again when either of its
#   lines changes, or when the lowerer's version does.
