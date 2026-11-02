"""model_lang_parts -- language-agnostic machinery for modelling a language's parts
(HiOps, holders, infra, context, HiOp_complexities, HiOp_configurations).

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/`.
Citations: `dict_of_lang_HiOps/SUPPORT_declared_vocabularies.md`.

    lowerer   a language's compiler or interpreter: what lowers a HiOp to a Unit

THE RULE THIS MODULE EXISTS TO HOLD: the dict is DERIVED from the language,
never hand-written. Every one of the twelve languages declares its operators
and its holders in its lowerer's own source, so nothing here reads a list we
wrote.
"""

import importlib
import os
import re
from typing import Callable, NamedTuple

from ..dict_of_lang_HiOps import Variant


# Where the upstream checkouts live is configuration: this variable names
# the directory holding them, one sub-directory per checkout.
SOURCES_VARIABLE = "PSEUDOARCH_SOURCES"


class Declaration(NamedTuple):
    """Where one language's lowerer declares one list, and how to read it."""

    checkout: str
    files: tuple
    parse: Callable


def sources_root() -> str:
    """The directory holding the upstream checkouts. Refuses by name when the
    variable is not set, rather than guessing a path."""
    root = os.environ.get(SOURCES_VARIABLE)
    if root is None:
        message = f"{SOURCES_VARIABLE} is not set: it names the directory holding the lowerers' checkouts"
        raise LookupError(message)
    return root


def declaring_file_path(checkout: str, relative: str) -> str:
    """The path of one declaring file. Refuses by name when it is not on disk,
    so a missing checkout is reported and never read as an empty list."""
    root = sources_root()
    path = os.path.join(root, checkout, relative)
    if not os.path.isfile(path):
        message = f"declaring file not on disk: {checkout}/{relative}"
        raise FileNotFoundError(message)
    return path


# Where the files of a lowerer written in C++ sit as its own preprocessor
# writes them: every macro expanded, each line at its own line number, one
# sub-directory per checkout. the owner, 2026-10-16: "lets implement that so we
# never have to be bothered by these again." This project keeps them; the
# variable names another place (the checkouts' own directory, to read the
# files as written).
PREPROCESSED_VARIABLE = "PSEUDOARCH_PREPROCESSED"
HERE = os.path.dirname(os.path.abspath(__file__))
PREPROCESSED_DEFAULT = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "..", "Research", "extract_lang_vocabulary", "made_by_clang", "preprocessed")
)
PREPROCESSING_RUN = "Research/extract_lang_vocabulary/lanes_elv2/elv2_l173_clangs_read_files_preprocessed.sh"


def preprocessed_root() -> str:
    """The directory holding the preprocessed files: the variable's when it
    is set, this project's own otherwise."""
    root = os.environ.get(PREPROCESSED_VARIABLE, PREPROCESSED_DEFAULT)
    return root


def preprocessed_file_path(checkout: str, relative: str) -> str:
    """The path of one file of a C++ lowerer as its preprocessor writes it.
    Refuses by name when it is not on disk: read as written, the file would
    hide whatever its macros write."""
    root = preprocessed_root()
    path = os.path.join(root, checkout, relative)
    if not os.path.isfile(path):
        message = f"not preprocessed yet: {checkout}/{relative} (the run that makes it: {PREPROCESSING_RUN})"
        raise FileNotFoundError(message)
    return path


def declaration_of(declarations: dict, lang: str, reader: str) -> Declaration:
    """The Declaration a reader holds for `lang`. Refuses by name when there
    is none yet: a language no reader can read is reported, never skipped."""
    declaration = declarations.get(lang)
    if declaration is None:
        message = f"{reader}: no declaring file recorded for {lang!r} yet"
        raise LookupError(message)
    return declaration


class Operator(NamedTuple):
    """One operator, as the lowerer declares it.

    `name` is the lowerer's own identifier for it: clang `Mul`, go `MUL`,
    python `NB_MULTIPLY`. `spelling` is how a program writes it, as a
    template over its operands: `a * b`, `(T)a`, `a ? b : c`. The spelling
    writes the probe and is never a key.

    `operands` are the template's placeholders in order. `a` to `h` hold
    values; `T`, `U`, `V` and `W` name types, as the target of a cast does;
    `m` and `n` name a member of what an operand holds, as in `a.m`. Each one
    is a slot in the grid.
    """

    lang: str
    name: str
    spelling: str
    operands: tuple
    source: str


# An operand placeholder in a template: `a` to `h` hold values, `T`, `U`,
# `V`, `W` name types, `m`, `n` name members. Each stands as a word of its
# own.
PLACEHOLDER = re.compile(r"\b([a-hTUVWmn])\b")


def placeholders_of(spelling: str) -> list:
    """The operand placeholders in a template, in the order written."""
    found = PLACEHOLDER.findall(spelling)
    return found


class Holder(NamedTuple):
    """One holder type, as the lowerer declares it.

    `spelling` is how a program writes the type, which is not always the
    lowerer's own name for it: clang's `UInt` is written `unsigned int`.
    """

    lang: str
    name: str
    spelling: str
    source: str


class Judged(NamedTuple):
    """One pass of the grid: the operators it asked, its cells (an operator's
    position and one holder position per slot), the lowerer's verdict on each
    cell, one row per operator (its cells, the accepted ones, and the
    refusals by their words), and the verdicts set beside the past ones
    (`beside_past`: how many were answered before, how many the same)."""

    label: str
    operators: tuple
    cells: tuple
    verdicts: dict
    rows: list
    beside_past: object = None


class Extracted(NamedTuple):
    """What extract() read and asked for one language, and the HiOps it found;
    and what the lowerer's checking code was read to accept (`read`)."""

    vocabulary: object
    holder_verdicts: list
    kept: list
    declarations: tuple
    passes: object
    HiOps: list
    read: object = None


# Each language's own module of steps for `extract()`.
LOWERERS = {
    "c": "PseudoArch.map_HiOp_to_unit.lang_models.gnu_c.clang",
}


def extract(lang: str, work_folder: str, evidence: str = "", small: bool = False) -> Extracted:
    """One language's vocabulary read from its lowerer, its holders and
    cells asked of that lowerer, and the accepted cells returned as
    Variants for `dict_of_lang_HiOps`."""
    from .. import mask_maker

    lowerer = lowerer_of(lang)
    work = os.path.abspath(work_folder)
    os.makedirs(work, exist_ok=True)
    vocabulary = lowerer.vocabulary(lang)
    library = os.path.join(work, "library")
    declarations = mask_maker.library_declarations(lang, vocabulary.operators, library)
    holder_evidence = f"{evidence} holders".strip()
    holder_verdicts = mask_maker.judge_holders(lang, vocabulary.holders, work, holder_evidence)
    kept = kept_positions(holder_verdicts)
    read = lowerer.read_signatures(lang, vocabulary, kept, work, small)
    vocabulary, holder_verdicts, read = with_read_holders(
        lang, vocabulary, holder_verdicts, read, work, holder_evidence
    )
    passes = lowerer.passes(lang, vocabulary, kept, declarations, work, evidence, small, read)
    HiOps = HiOps_of(lang, vocabulary.holders, passes)
    extracted = Extracted(vocabulary, holder_verdicts, kept, declarations, passes, HiOps, read)
    return extracted


def with_read_holders(lang: str, vocabulary, holder_verdicts: list, read, work: str, evidence: str) -> tuple:
    """The vocabulary with the holders the reading adds at the end of its
    holder list (those not spelled there already), each tried as a holder as
    the others were; the verdicts on them after the others'; and the
    reading, with the positions of those the lowerer keeps."""
    from .. import mask_maker

    spelled = set()
    for holder in vocabulary.holders:
        spelled.add(holder.spelling)
    added = []
    for holder in read.added:
        if holder.spelling not in spelled:
            added.append(holder)
    read = read._replace(added=tuple(added))
    if not added:
        return (vocabulary, holder_verdicts, read)
    directory = os.path.join(work, "read_holders")
    os.makedirs(directory, exist_ok=True)
    added_verdicts = mask_maker.judge_holders(lang, tuple(added), directory, f"{evidence} read".strip())
    first = len(vocabulary.holders)
    kept_added = []
    for offset, verdict in enumerate(added_verdicts):
        if verdict.accepted:
            kept_added.append(first + offset)
    vocabulary = vocabulary._replace(holders=tuple(vocabulary.holders) + tuple(added))
    holder_verdicts = list(holder_verdicts) + list(added_verdicts)
    read = read._replace(kept_added=tuple(kept_added))
    found = (vocabulary, holder_verdicts, read)
    return found


def lowerer_of(lang: str):
    """The module of `lang`'s own steps. Refuses by name a language none is
    written for yet."""
    name = LOWERERS.get(lang)
    if name is None:
        message = f"model_lang_parts: no module of {lang!r}'s own steps yet"
        raise LookupError(message)
    module = importlib.import_module(name)
    return module


def kept_positions(holder_verdicts: list) -> list:
    kept = []
    for position, verdict in enumerate(holder_verdicts):
        if verdict.accepted:
            kept.append(position)
    return kept


def HiOps_of(lang: str, holders: tuple, passes) -> list:
    """The accepted cells of the operators the lowerer read back as written,
    each once, in the order the passes first asked them, which is the order
    the knowns file keeps them in; then the HiOps held in a form of their own,
    which take no holder (`&&m`)."""
    HiOps = []
    seen = set()
    for judged in passes.judged:
        add_HiOps(HiOps, seen, lang, holders, judged, passes.as_written)
    for HiOp in passes.own_HiOps:
        HiOps.append(HiOp)
    return HiOps


def add_HiOps(HiOps: list, seen: set, lang: str, holders: tuple, judged: Judged, as_written: set) -> None:
    for cell in judged.cells:
        operator = judged.operators[cell.operator]
        held = held_holders(holders, cell)
        identity = identity_of(operator, held)
        if identity in seen:
            continue
        seen.add(identity)
        verdict = judged.verdicts.get(cell)
        if verdict is None or not verdict.accepted:
            continue
        if (operator.name, operator.spelling) not in as_written:
            continue
        HiOps.append(Variant(lang, operator, held, None, verdict.evidence))


def held_holders(holders: tuple, cell) -> tuple:
    held = []
    for position in cell.holders:
        held.append(holders[position])
    found = tuple(held)
    return found


def identity_of(operator: Operator, held: tuple) -> tuple:
    """What a cell is, whatever positions its operator and holders hold: the
    operator's name and template, and each holder's name and spelling (as
    mask_maker.cell_identity reads it)."""
    names = []
    for holder in held:
        names.append((holder.name, holder.spelling))
    identity = (operator.name, operator.spelling, tuple(names))
    return identity


from . import HiOps, holders, infra, context, HiOp_complexities, HiOp_configurations  # noqa: E402,F401
from .HiOps import operator_reader  # noqa: E402,F401
from .holders import holder_reader  # noqa: E402,F401
