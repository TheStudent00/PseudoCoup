"""map_HiOp_to_unit -- one HiOp, with its holders, lowered and sliced to its Unit.

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/`.

The dict's keys first, then its values, in the order they run:

    extract_lang_vocab        ->  dict_of_lang_HiOps: the keys, each labelled by its signature
    complex_signature_reader  ->  for the keys whose signature does not determine their holders
    dict_of_lang_HiOps + standard_HiOp_wrapper  ->  source to compile
    lower_HiOp                ->  LoHiOp
    extract_unit_from_LoHiOp  ->  Unit: the values
    DRY_mask_maker            ->  grid_mask_of_knowns: all the work already done, so none is redone

This module's own loop, `map_HiOp_to_unit`, runs the last three for many
HiOps at once: it puts many standard functions in one source, compiles the
source once (lower_HiOp), reads each standard function's words, and cuts its
Unit (extract_unit_from_LoHiOp). Moved here on 2026-10-13 from the research
runner `Research/lower_HiOp/lower_gnu_c.py` (PCHQ log 454), at the owner's word:
"okay lets move the tools into their places". The runner keeps what is a
run's: which HiOps it lowers, for which machine, and the records it writes.

    standard_HiOps = [StandardHiOp(key, symbol, lines), ...]        # each HiOp held, on its own line
    mapped = map_HiOp_to_unit("c", standard_HiOps, preamble)    # [MappedHiOp(key, LoHiOp, HiOp_line, unit), ...]

The standard-form is `standard_HiOp_wrapper`, moved from DRY_mask_maker the same
day (log 454). Not here yet, with its place in the plan: the keys
(`extract_lang_vocab` and `dict_of_lang_HiOps`; research's
`Research/extract_lang_vocabulary/run_elv3.py` reads them today).
`complex_signature_reader`'s checking half is here since 2026-10-16
(`complex_signature_reader/`: the walk, the checking reader, and the
signatures `extract()` tries from what it reads); its lowering half, bridge
and compose are research code for now
(`Research/extract_lang_vocabulary/complex_signature_reader/`).

Renamed and moved 2026-10-05 at the owner's word (PseudoCoupHQ log 361):
`extract_lang_vocabulary` became `extract_lang_vocab`, and `DRY_mask_maker`
moved up from it to here, because both stages use the mask.
"""
from typing import NamedTuple, Optional

from . import dict_of_lang_HiOps  # noqa: F401
from . import model_lang_parts  # noqa: F401
from . import lower_HiOp
from . import mask_maker
from . import lang_models  # noqa: F401
from .lower_HiOp import hijack_lowerer, read_words_at_symbol, standard_HiOp_wrapper, extract_unit_from_LoHiOp


def map_state_info_0_to_unit(state_info_0, key: str = "k", compile_command: Optional[str] = None, library_decl: str = "") -> "MappedHiOp":
    """Hijack the lowerer at the HiOp entry point with `state_info_0`, read the
    emitted `LoHiOp`, and extract the `Unit` between `__hiop_unit_begin` and
    `__hiop_unit_end`."""
    machine = state_info_0.target.replace("-", "_")
    mc, entry = hijack_lowerer.hijack_lowerer(
        state_info_0,
        key=key,
        compile_command=compile_command,
        library_decl=library_decl,
    )
    lo = lower_HiOp.read_words_at_symbol(mc, entry.symbol)
    unit = extract_unit_from_LoHiOp.extract_unit(lo, entry.hiop_line, machine=machine)
    return MappedHiOp(key, lo, entry.hiop_line, unit)

# How many standard functions go in one source: the source is compiled once,
# and a refused source is split until each refusal belongs to one HiOp.
BATCH_SIZE = 2000


class StandardHiOp(NamedTuple):
    """One HiOp held: its key, the name of its standard function, and the held
    lines, with the HiOp on a line of its own, indented with a tab
    (standard_HiOp_wrapper.HiOp_on_its_own_line)."""

    key: str
    symbol: str
    lines: tuple


class MappedHiOp(NamedTuple):
    """One HiOp lowered and cut: its LoHiOp, the line its HiOp is on in the
    compiled source (None when the compiler refused it), and its Unit."""

    key: str
    LoHiOp: object
    HiOp_line: Optional[int]
    unit: object


def map_HiOp_to_unit(lang: str, standard_HiOps: list, preamble: list, machine: str = "riscv64",
                     compile_command: Optional[str] = None) -> list:
    """Every held HiOp lowered and cut, BATCH_SIZE to a source. The preamble
    is the lines every standard source starts with: the held types and the
    library's declarations."""
    mapped = []
    for batch in batches_of(standard_HiOps):
        mapped += map_batch(lang, batch, preamble, machine, compile_command)
    return mapped


def batches_of(standard_HiOps: list) -> list:
    batches = []
    for start in range(0, len(standard_HiOps), BATCH_SIZE):
        batches.append(standard_HiOps[start:start + BATCH_SIZE])
    return batches


def map_batch(lang: str, batch: list, preamble: list, machine: str,
              compile_command: Optional[str] = None) -> list:
    """One source for the whole batch, compiled once, and each symbol read
    from it and cut. A refused source is split by the lines its errors name,
    or in halves when they name none, until each refusal belongs to one
    HiOp."""
    source, line_ranges, HiOp_lines = standard_source_of(batch, preamble)
    machine_code = lower_HiOp.compile_standard_source(lang, source, compile_command)
    if machine_code.refusal is None:
        mapped = mapped_symbols(machine_code, batch, HiOp_lines, machine)
        return mapped
    if len(batch) == 1:
        refused = lower_HiOp.LoHiOp(batch[0].symbol, (), machine_code.refusal)
        mapped = [mapped_one(batch[0], refused, None, machine)]
        return mapped
    named = errors_by_HiOp(lang, machine_code.refusal, line_ranges)
    if named:
        mapped = refused_and_the_rest(lang, batch, named, preamble, machine, compile_command)
        return mapped
    mapped = mapped_in_halves(lang, batch, preamble, machine, compile_command)
    return mapped


def standard_source_of(batch: list, preamble: list) -> tuple:
    """One source holding every HiOp's standard function, the lines each held
    function takes in it, and the line each HiOp is on (counted from 1, as
    the compiler counts)."""
    lines = list(preamble)
    line_ranges = []
    HiOp_lines = []
    for held in batch:
        first = len(lines) + 1
        HiOp_lines.append(first + HiOp_line_within(held.lines))
        lines.extend(held.lines)
        line_ranges.append((first, len(lines)))
    text = "\n".join(lines) + "\n"
    source = standard_HiOp_wrapper.StandardSource(text, batch[0].symbol)
    standard_source = (source, line_ranges, HiOp_lines)
    return standard_source


def HiOp_line_within(lines: tuple) -> int:
    """Where the HiOp is among a standard function's lines, counted from 0: the
    one line standard_HiOp_wrapper.HiOp_on_its_own_line indents with a tab."""
    position = 0
    for index, line in enumerate(lines):
        if line.startswith("\t"):
            position = index
    return position


def mapped_symbols(machine_code, batch: list, HiOp_lines: list, machine: str) -> list:
    mapped = []
    for held, HiOp_line in zip(batch, HiOp_lines):
        LoHiOp = lower_HiOp.read_words_at_symbol(machine_code, held.symbol)
        mapped.append(mapped_one(held, LoHiOp, HiOp_line, machine))
    return mapped


def mapped_one(held: StandardHiOp, LoHiOp, HiOp_line: Optional[int], machine: str) -> MappedHiOp:
    unit = extract_unit_from_LoHiOp.extract_unit(LoHiOp, HiOp_line, machine)
    mapped = MappedHiOp(held.key, LoHiOp, HiOp_line, unit)
    return mapped


def errors_by_HiOp(lang: str, refusal: str, line_ranges: list) -> dict:
    """The position of each HiOp in the batch -> the errors the compiler gave
    on its lines, read with the lowerer's own diagnostic form
    (mask_maker.DIAGNOSTIC)."""
    named = {}
    diagnostic = mask_maker.DIAGNOSTIC[lang]
    for line in refusal.splitlines():
        found = diagnostic.match(line)
        if found is None:
            continue
        position = position_of_line(int(found.group("line")), line_ranges)
        if position is None:
            continue
        if position not in named:
            named[position] = []
        named[position].append(found.group("message"))
    return named


def position_of_line(line_number: int, line_ranges: list) -> Optional[int]:
    for position, (first, last) in enumerate(line_ranges):
        if first <= line_number <= last:
            return position
    return None


def refused_and_the_rest(lang: str, batch: list, named: dict, preamble: list, machine: str,
                         compile_command: Optional[str] = None) -> list:
    """The HiOps the errors name are refused with those errors; the rest are
    lowered again without them."""
    mapped = []
    rest = []
    for position, held in enumerate(batch):
        if position in named:
            words = "; ".join(named[position])
            refused = lower_HiOp.LoHiOp(held.symbol, (), f"error: {words}")
            mapped.append(mapped_one(held, refused, None, machine))
            continue
        rest.append(held)
    if rest:
        mapped += map_batch(lang, rest, preamble, machine, compile_command)
    return mapped


def mapped_in_halves(lang: str, batch: list, preamble: list, machine: str,
                     compile_command: Optional[str] = None) -> list:
    middle = len(batch) // 2
    mapped = map_batch(lang, batch[:middle], preamble, machine, compile_command)
    mapped += map_batch(lang, batch[middle:], preamble, machine, compile_command)
    return mapped
