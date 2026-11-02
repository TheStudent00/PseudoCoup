"""dict_of_lang_HiOps -- per language, every HiOp: an operator with the holder
types it is applied to, one entry per variant (its CORE's definition).

Plan: `.../node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_0_dict_of_lang_HiOps/`.

    dict_of_lang_HiOps.write(path, HiOps)    # the HiOps extract_lang_vocab.extract() found
    HiOps = dict_of_lang_HiOps.read(path)    # every HiOp of a language, in the order extract() found them

The dict is derived from the language, never hand-written:
`extract_lang_vocab.extract()` fills it from the lowerer's own lists and the
lowerer's own verdicts. One JSON line per HiOp, compressed:

    {"lang": "c", "operator": "BinaryOperator.Add", "template": "a + b", "operands": ["a", "b"],
     "source": "...", "holders": [["Int", "int", "..."], ["Int", "int", "..."]], "evidence": "..."}

Written 2026-10-14 , at the owner's word "lets do it", with
`extract()`. Until then a language's HiOps were read straight from the
research grid's verdicts
(`Research/extract_lang_vocabulary/mask/gnu17/c.knowns.jsonl.gz`).
"""
import gzip
import json
from pathlib import Path
from typing import NamedTuple, Optional, Union


class Variant(NamedTuple):
    """One HiOp: an operator with the holders it is applied to, accepted by
    the lowerer.

    `result` is the holder the lowerer says the variant answers, when it says
    one, and None when it does not. `evidence` names how the cell became
    known, so any count built on this record is attributable.

    Moved here from extract_lang_vocab on 2026-10-14 , as the
    note on it there said it would be once this node was coded; the dict is
    what every reader of a language's HiOps reads. extract_lang_vocab keeps
    the name.
    """

    lang: str
    operator: object
    holders: tuple
    result: Optional[object]
    evidence: str


def write(path: str, HiOps: list) -> None:
    """The HiOps, one JSON line each, in the order given."""
    with gzip.open(path, "wt", encoding="utf-8") as written:
        for HiOp in HiOps:
            written.write(json.dumps(entry_of(HiOp)) + "\n")


def entry_of(HiOp: Variant) -> dict:
    holders = []
    for holder in HiOp.holders:
        holders.append([holder.name, holder.spelling, holder.source])
    operator = HiOp.operator
    entry = {"lang": HiOp.lang, "operator": operator.name, "template": operator.spelling,
             "operands": list(operator.operands), "source": operator.source, "holders": holders,
             "evidence": HiOp.evidence}
    return entry


def read(path: str) -> list:
    """Every HiOp the file holds, in its order."""
    HiOps = []
    with gzip.open(path, "rt", encoding="utf-8") as kept:
        for line in kept:
            HiOps.append(HiOp_of(json.loads(line)))
    return HiOps


def HiOp_of(entry: dict) -> Variant:
    # extract_lang_vocab defines the operator and holder records, and reads
    # Variant from this module, so it is imported here, when a file is read
    from .model_lang_parts import Holder, Operator
    lang = entry["lang"]
    operator = Operator(lang, entry["operator"], entry["template"], tuple(entry["operands"]), entry["source"])
    holders = []
    for name, spelling, source in entry["holders"]:
        holders.append(Holder(lang, name, spelling, source))
    HiOp = Variant(lang, operator, tuple(holders), None, entry["evidence"])
    return HiOp


def _load_c_vocab_metadata() -> tuple[dict, dict]:
    """Load fallback operator and holder metadata from consolidated_gnu_c_vocabulary.json
    or Research/extract_lang_vocabulary/vocabulary/c.json when reading a raw paths.json.
    """
    here = Path(__file__).resolve().parent
    consolidated = here / "lang_models" / "gnu_c" / "unreached_paths" / "consolidated_gnu_c_vocabulary.json"
    if consolidated.exists():
        with open(consolidated, "r", encoding="utf-8") as f:
            data = json.load(f)
        op_meta = {}
        for name, rec in data.get("operators", {}).items():
            if "template" in rec or "spelling" in rec:
                op_meta[name] = {
                    "template": rec.get("template", rec.get("spelling", "")),
                    "operands": rec.get("operands", []),
                    "source": rec.get("source", ""),
                }
        return op_meta, data.get("holders_by_spelling", {})
    c_vocab = here.parents[2] / "Research" / "extract_lang_vocabulary" / "vocabulary" / "c.json"
    if c_vocab.exists():
        with open(c_vocab, "r", encoding="utf-8") as f:
            data = json.load(f)
        op_meta = {
            op["name"]: {
                "template": op.get("spelling", ""),
                "operands": op.get("operands", []),
                "source": op.get("source", ""),
            }
            for op in data.get("operators", [])
        }
        holders_map = {
            h["spelling"]: [h["name"], h["spelling"], h.get("source", "")]
            for h in data.get("holders", [])
        }
        return op_meta, holders_map
    return {}, {}


def from_consolidated_paths(
    paths_record_or_path: Union[str, Path, dict, None] = None,
    lang: str = "gnu_c",
    *,
    expand_contexts: bool = False,
) -> list[Variant]:
    """Convert solved `paths.json` or `consolidated_gnu_c_vocabulary.json` variants
    into `Variant` entries for `dict_of_lang_HiOps`.
    """
    from .model_lang_parts import Holder, Operator

    if paths_record_or_path is None:
        paths_record_or_path = (
            Path(__file__).resolve().parent
            / "lang_models"
            / "gnu_c"
            / "unreached_paths"
            / "consolidated_gnu_c_vocabulary.json"
        )

    if isinstance(paths_record_or_path, (str, Path)):
        path_obj = Path(paths_record_or_path)
        name_lower = path_obj.name.lower()
        opener = gzip.open if name_lower.endswith(".gz") else open
        if ".jsonl" in name_lower:
            HiOps = []
            with opener(path_obj, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    if "operator" in row and "holders" in row and "template" in row:
                        HiOps.append(HiOp_of(row))
            return HiOps
        with opener(path_obj, "rt", encoding="utf-8") as f:
            record = json.load(f)
    elif isinstance(paths_record_or_path, dict):
        record = paths_record_or_path
    else:
        raise TypeError(f"Unsupported paths_record_or_path type: {type(paths_record_or_path)!r}")

    operators_map = record.get("operators", record)
    holders_map = dict(record.get("holders_by_spelling", {}))
    fallback_ops: Optional[dict] = None

    HiOps: list[Variant] = []
    for op_name, op_record in operators_map.items():
        if not isinstance(op_record, dict):
            continue
        variants = op_record.get("variants", [])
        if not variants:
            continue

        template = op_record.get("template", op_record.get("spelling"))
        operands = op_record.get("operands")
        op_source = op_record.get("source")
        if template is None or operands is None or not holders_map:
            if fallback_ops is None:
                fallback_ops, fallback_holders = _load_c_vocab_metadata()
                if not holders_map:
                    holders_map.update(fallback_holders)
            meta = fallback_ops.get(op_name, {})
            if template is None:
                template = meta.get("template", op_name)
            if operands is None:
                operands = meta.get("operands", [])
            if op_source is None:
                op_source = meta.get("source", "")

        operator = Operator(
            lang,
            op_name,
            template or op_name,
            tuple(operands or ()),
            op_source or "",
        )
        default_run = op_record.get("latest_paths_run") or record.get("run") or "consolidated_gnu_c_vocabulary"

        for variant in variants:
            if not variant.get("accepted", True):
                continue
            contexts = variant.get("contexts", [])
            if not contexts:
                if len(operator.operands) == 0:
                    contexts = [[]]
                else:
                    continue
            chosen_contexts = contexts if expand_contexts else contexts[:1]
            evidence = (
                variant.get("evidence")
                or variant.get("run")
                or default_run
            )
            for ctx in chosen_contexts:
                holder_objs = []
                for h in ctx:
                    if isinstance(h, (list, tuple)) and len(h) >= 3:
                        holder_objs.append(Holder(lang, h[0], h[1], h[2]))
                    elif isinstance(h, dict):
                        holder_objs.append(
                            Holder(lang, h["name"], h["spelling"], h.get("source", ""))
                        )
                    else:
                        spelling = str(h)
                        h_meta = holders_map.get(spelling)
                        if h_meta is not None:
                            holder_objs.append(Holder(lang, h_meta[0], h_meta[1], h_meta[2]))
                        else:
                            holder_objs.append(Holder(lang, spelling, spelling, ""))
                HiOps.append(Variant(lang, operator, tuple(holder_objs), None, str(evidence)))

    return HiOps
