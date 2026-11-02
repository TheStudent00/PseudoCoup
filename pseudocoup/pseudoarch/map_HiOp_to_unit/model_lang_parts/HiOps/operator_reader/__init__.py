"""operator_reader -- the module that reads the operators one language's
lowerer declares, from the lowerer's own source, in the order it declares
them. Its function `read_operators(lang)` returns them.

Plan: `.../node_0_0_0_0_2_4_0_operator_reader/`, and its five sub-nodes:

    operator_list        per lowerer   the lowerer's own lists of operator names,
                                       each keyed by the call that writes a
                                       name from it
    expression_kinds     per lowerer   the lowerer's own list of every kind of
                                       expression
    write_back_as_text   per lowerer   for one kind, every way the lowerer's code
                                       can write that kind back into source
                                       text, each as the pieces it writes
    spelling_of          shared        one way's pieces made into the spelling a
                                       program writes
    left_out             shared        every kind, or way through one, not turned
                                       into an operator, with its reason

Each lowerer answers the three per-lowerer parts in its own module beside this
one: clang.py, for c and cpp. The walk through a lowerer's code is shared
(ways.py), and so is reading code in the language a lowerer is written in
(cpp_code.py, for clang). Nothing in this file names a language, except
LOWERERS, the table that says which module answers for which language.

    def read_operators(lang):
        operators, left_out = [], []
        for kind in expression_kinds(lang):
            ways, reason = write_back_as_text(lang, kind)
            if reason:
                left_out.append((kind, reason))
            for way in ways:
                if the way stopped, or its spelling has no operand, no text, or
                an operand joined to text:
                    left_out.append((way, why))
                else:
                    operators.append((way, spelling_of(way)))
        return operators, left_out
"""

from ... import Operator, declaring_file_path, placeholders_of
from . import clang

# Which module answers operator_list, expression_kinds and write_back_as_text
# for each language. clang lowers both c and cpp from the same lists.
LOWERERS = {
    "c": clang,
    "cpp": clang,
}

# The letters a spelling writes for each sort of piece, in order. Eight value
# letters: clang's atomics take up to six operands, and its fortified
# library builtins up to seven.
LETTERS = {
    "operand": ("a", "b", "c", "d", "e", "f", "g", "h"),
    "type": ("T", "U", "V", "W"),
    "name": ("m", "n"),
}


def read_operators(lang: str) -> tuple:
    """(operators, left_out) for `lang`: every Operator its lowerer's code can
    write, kind by kind in the order the lowerer declares them, and every
    kind, or way through one, that is not turned into an operator, with the
    reason. Refuses by name a language no module answers for yet."""
    operators = []
    left_out = []
    for kind, declared_at in expression_kinds(lang):
        ways, reason, written_at = write_back_as_text(lang, kind)
        if reason is not None:
            left_out.append((kind, reason))
            continue
        for way in ways:
            name = name_of(kind, way)
            if way.status == "stop":
                left_out.append((name, way.reason))
                continue
            try:
                spelling, operands = spelling_of(way.pieces)
            except ValueError as too_many:
                left_out.append((name, str(too_many)))
                continue
            kept_without_operands = lowerer_of(lang).declares_no_operand(kind, way)
            if not operands and not kept_without_operands:
                left_out.append((name, "it takes no operand"))
                continue
            if (operands and not any(letter not in LETTERS["name"] for letter in operands)
                    and not kept_without_operands):
                left_out.append((name, "it takes no operand, only a name"))
                continue
            if not any(piece[0] == "text" for piece in way.pieces):
                left_out.append((name, "a program never writes it: its code writes no text"))
                continue
            if tuple(placeholders_of(spelling)) != tuple(operands):
                left_out.append((name, f"its code joins an operand to text (`{spelling}`), so no operand can be written in"))
                continue
            operators.append(Operator(lang, name, spelling, operands, source_of(declared_at, written_at, way)))
    found = (tuple(operators), tuple(left_out))
    return found


def operator_list(lang: str) -> dict:
    """call -> entries: each of the lowerer's own lists of operator names,
    keyed by the call in its code that writes a name from the list."""
    listed = lowerer_of(lang).operator_list()
    return listed


def expression_kinds(lang: str) -> tuple:
    """(kind, where it is declared) for every kind of expression the lowerer
    declares, in its order."""
    listed = lowerer_of(lang).expression_kinds()
    return listed


def write_back_as_text(lang: str, kind: str) -> tuple:
    """(ways, reason, where) for one kind: see the lowerer's module."""
    found = lowerer_of(lang).write_back_as_text(kind)
    return found


def spelling_of(pieces: tuple) -> tuple:
    """(spelling, operands) of one way's pieces: fixed text as it is, each
    operand as a, b, c, d in order, each type as T, U, V, W, each name as m,
    n. `operands` lists those letters in the order they appear. Refuses with
    ValueError a way that has more of one sort than there are letters."""
    spelling = []
    operands = []
    seen = {sort: 0 for sort in LETTERS}
    for piece in pieces:
        sort = piece[0]
        if sort == "text":
            spelling.append(piece[1])
            continue
        letters = LETTERS[sort]
        if seen[sort] == len(letters):
            message = f"it writes more than {len(letters)} of one sort ({sort}), more than there are letters"
            raise ValueError(message)
        letter = letters[seen[sort]]
        seen[sort] += 1
        spelling.append(letter)
        operands.append(letter)
    # Indentation and line breaks are spaces: one between words, none at the ends.
    written = " ".join("".join(spelling).split())
    found = (written, tuple(operands))
    return found


def name_of(kind: str, way) -> str:
    """The kind, and the lowerer's name for each list entry the way chose:
    `UnaryOperator.PostInc`, or `MemberExpr` when it chose none."""
    name = kind + "".join(f".{entry.name}" for _keyed_on, entry in way.chosen)
    return name


def source_of(declared_at: str, written_at: str, way) -> str:
    """Where the operator comes from: its kind, the code that writes it, each
    list entry it chose, and how each choice went on its way."""
    parts = [declared_at, f"written at {written_at}"]
    for _keyed_on, entry in way.chosen:
        parts.append(f"{entry.label} at {entry.source}")
    for condition, how in way.taken:
        parts.append(f"{condition}: {how}")
    source = "; ".join(parts)
    return source


def lowerer_of(lang: str):
    """The module that answers the three per-lowerer parts for `lang`. Refuses
    by name a language none answers for yet."""
    if lang not in LOWERERS:
        message = (f"read_operators: no module answers for {lang} yet. The readers written before the "
                   f"split (go, rust, python, java) are in old_readers.py, not yet split into the five parts.")
        raise LookupError(message)
    module = LOWERERS[lang]
    return module


def sources(lang: str) -> tuple:
    """The files read for `lang`, so a run is attributable to a version of the
    lowerer rather than to the language's name."""
    module = lowerer_of(lang)
    paths = []
    for relative in module.FILES:
        paths.append(declaring_file_path(module.CHECKOUT, relative))
    read = tuple(paths)
    return read


# ADJACENT, NOT YET CODED:
#
#   The short-circuit operators are control flow in some lowerers, so their
#   operation lists leave them out: V8's operation.h has no `&&`, `||` or
#   `??` (its token table has all three, src/parsing/token.h:34-36), and
#   python's `and` and `or` are in its grammar (Grammar/python.gram), not
#   in _nb_ops. The held wrapper showed they lower to real branches, so
#   they are HiOps; for these lowerers the token table or the grammar is
#   a second file to open.
#
#   Asking beats parsing where the lowerer can be asked. go's `go/token`
#   is importable, so a short go program can print the list; python and
#   ruby can list their own operator methods at run time. Such an answer
#   cannot drift from the lowerer we compile with. It runs the language, so
#   it goes through Airlock like any other run.
#
#   java's Operators.java names the JVM instruction for each pairing -- the
#   lowering, already named by the language. A free cross-check against
#   `lower_HiOp`'s carve.
