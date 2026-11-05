"""verify_tier1_tier2_12langs -- 12-Language Cross-Language Equivalence & Piecewise Polyfill Ledger.

Implements `log_528` Step 1.4 (`CORE_0_0_0_2_0_autopoly.md`, `SUPPORT_BRAINSTORM_hub.md` §3 rows 48-50):
  - Loads real Sail-derived `UnitLean` `UniversalRichNode`s across all 12 languages:
    `c`, `cpp`, `go`, `rust`, `python`, `java`, `typescript`, `csharp`, `ruby`, `php`, `dart`, `swift`.
  - Runs `EquivalenceProver.prove_domain_range_partition` and `AutoPoly.synthesize_from_sail_unit`
    across all 12 x 12 language pairs and operator families (plus whole-lowered `compiler-rt` caller units).
  - Classifies every synthesis into:
      1. `tier1_exact_native_hiop` (exact Z3 UNSAT equivalence across the full domain)
      2. `tier2_piecewise_hiop` (interior Z3 UNSAT agreement + guarded residual pieces)
      3. `tier3_loop_primitive_backstop` (guaranteed `LoOp`-to-`HiOpPrimitive` backstop)
  - Writes `Research/lower_HiOp/out/autopoly_12lang_tier_summary.json`.
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
for _anc in HERE.parents:
    if (_anc / "pseudocoup" / "__init__.py").exists():
        if str(_anc) not in sys.path:
            sys.path.insert(0, str(_anc))
        import pseudocoup  # noqa: F401
        break
PCHQ_ROOT = HERE.parents[3]
PROJECTS_DIR = PCHQ_ROOT / "Projects"
if PROJECTS_DIR.exists() and str(PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECTS_DIR))

from PseudoArch.map_HiOp_to_unit.lower_HiOp import Word
from PseudoArch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import Unit
from PseudoArch.map_unit_to_lean import compose_LoOp_leans
from PseudoCoup.ledgerer.universal_rich_node import UniversalRichNode
from PseudoCoup.hub.autopoly.polyfill import AutoPoly, HIOP_PRIMITIVES
from PseudoCoup.hub.autopoly.verify_hiop_primitives import (
    ALL_12_LANGUAGES,
    OUT_DIR,
    load_language_64bit_unit_leans,
)

SUMMARY_OUT = OUT_DIR / "autopoly_12lang_tier_summary.json"

CORE_OPS: tuple[str, ...] = (
    "BV_ADD",
    "BV_SUB",
    "BV_MUL",
    "BV_AND",
    "BV_OR",
    "BV_XOR",
    "BV_NOT",
    "BV_SHL",
    "BV_LSHR",
    "BV_ASHR",
    "BV_ULT",
    "BV_SLT",
    "BV_SDIV",
    "BV_UDIV",
    "BV_SREM",
    "BV_UREM",
)


def _load_compiler_rt_caller_nodes() -> list[UniversalRichNode]:
    """Load representative `compiler-rt` caller units (`__addtf3`, `__divti3`, `__modti3`, `__powisf2`)."""
    from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
    from PseudoArch.map_HiOp_to_unit.model_lang_parts import Operator
    from PseudoArch.map_HiOp_to_unit.model_lang_parts.context.entry_context import PartState0, StateInfo0

    wanted_syms = {"__modti3", "__powisf2"}
    found: dict[str, UniversalRichNode] = {}
    with gzip.open(OUT_DIR / "gnu_c_first_of_each_hijacked.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            if len(found) == len(wanted_syms):
                break
            rec = json.loads(line)
            unit_idxs = rec.get("unit") or []
            words = rec.get("words") or []
            if not unit_idxs:
                continue
            rels = [r for i in unit_idxs if i < len(words) for r in (words[i][4] or ())]
            for sym in wanted_syms:
                if sym not in found and any(sym in str(r) for r in rels):
                    raw_words = [words[i] for i in unit_idxs if i < len(words)]
                    base_addr = raw_words[0][0]
                    u_words = tuple(
                        Word(w[0] - base_addr, w[1], w[2], w[3], tuple(w[4]))
                        for w in raw_words
                    )
                    raw_hp = rec.get("holds_p")
                    if raw_hp is True:
                        hp = ((0, "a0"),)
                    elif isinstance(raw_hp, (list, tuple)):
                        hp = tuple((int(p[0]), str(p[1])) for p in raw_hp if isinstance(p, (list, tuple)) and len(p) == 2)
                    else:
                        hp = ()
                    parts = tuple(str(p) for p in (rec.get("parts") or ()))
                    u_obj = Unit(str(rec.get("symbol", "op")), u_words, parts, hp, None)
                    ul = compose_LoOp_leans(u_obj)
                    if ul.combined_term is not None and sym in ul.ext_calls:
                        found[sym] = UniversalRichNode(
                            hiop={
                                "lang": "c",
                                "operator": f"{rec.get('operator')}[{sym}]",
                                "spelling": sym,
                            },
                            meaning={"unit_obj": u_obj, "unit_lean": ul},
                        )

    for sym, op_name, tmpl, htype in [
        ("__addtf3", "BinaryOperator.Add", "a + b", "long double"),
        ("__divti3", "BinaryOperator.Div", "a / b", "__int128"),
    ]:
        si = StateInfo0(
            "c",
            Operator("c", f"{op_name}[{sym}]", tmpl, ("a", "b"), "verify_tier1_tier2"),
            (PartState0("a", htype), PartState0("b", htype)),
        )
        found[sym] = UniversalRichNode.from_mapped_hiop(map_state_info_0_to_unit(si), si)

    return [found[k] for k in sorted(found.keys())]


def run_12lang_tier_verification() -> dict[str, Any]:
    t0 = time.time()
    lang_uls = load_language_64bit_unit_leans()
    autopoly = AutoPoly()

    # Build UniversalRichNodes for every direct UnitLean in each of the 12 languages
    from PseudoCoup.hub.autopoly.polyfill import format_hiop_target_template

    nodes_by_lang: dict[str, dict[str, UniversalRichNode]] = {lang: {} for lang in ALL_12_LANGUAGES}
    for lang in ALL_12_LANGUAGES:
        for op_key, ul in lang_uls[lang].items():
            target_tmpl = format_hiop_target_template(op_key, lang)
            nodes_by_lang[lang][op_key] = UniversalRichNode(
                hiop={
                    "lang": lang,
                    "operator": op_key,
                    "spelling": op_key,
                    "target_code": target_tmpl,
                },
                meaning={"unit_lean": ul},
            )

    tier_counts = {
        "tier1_exact_native_hiop": 0,
        "tier2_piecewise_hiop": 0,
        "tier3_loop_primitive_backstop": 0,
    }
    by_lang_pair: dict[str, dict[str, int]] = {}
    sample_tier1: list[dict[str, Any]] = []
    sample_tier2: list[dict[str, Any]] = []
    sample_tier3: list[dict[str, Any]] = []

    total_syntheses = 0
    for src_lang in ALL_12_LANGUAGES:
        t_lang = time.time()
        for tgt_lang in ALL_12_LANGUAGES:
            pair_key = f"{src_lang}->{tgt_lang}"
            by_lang_pair[pair_key] = {
                "tier1_exact_native_hiop": 0,
                "tier2_piecewise_hiop": 0,
                "tier3_loop_primitive_backstop": 0,
            }
            for op_key, src_node in nodes_by_lang[src_lang].items():
                n_in = len(src_node.meaning["unit_lean"].inputs)
                cands: list[UniversalRichNode] = []
                if op_key in nodes_by_lang[tgt_lang]:
                    cands.append(nodes_by_lang[tgt_lang][op_key])
                for ck, c_node in nodes_by_lang[tgt_lang].items():
                    if c_node not in cands and len(c_node.meaning["unit_lean"].inputs) == n_in:
                        cands.append(c_node)
                res = autopoly.synthesize_from_sail_unit(
                    src_node, tgt_lang, candidate_target_nodes=cands, lhs="a", rhs="b", third="c"
                )
                tier = res["tier"]
                tier_counts[tier] += 1
                by_lang_pair[pair_key][tier] += 1
                total_syntheses += 1

                entry = {
                    "src_lang": src_lang,
                    "tgt_lang": tgt_lang,
                    "op": op_key,
                    "tier": tier,
                    "code": res["code"],
                }
                if tier == "tier1_exact_native_hiop" and len(sample_tier1) < 15:
                    sample_tier1.append(entry)
                elif tier == "tier2_piecewise_hiop" and len(sample_tier2) < 15:
                    sample_tier2.append(entry)
                elif tier == "tier3_loop_primitive_backstop" and len(sample_tier3) < 15:
                    sample_tier3.append(entry)
        print(
            f"[{src_lang}] completed 12 target languages in {time.time() - t_lang:.2f}s (total={total_syntheses})",
            flush=True,
        )

    # Also verify compiler-rt caller units across all 12 target languages
    crt_nodes = _load_compiler_rt_caller_nodes()
    crt_syntheses: list[dict[str, Any]] = []
    for crt_node in crt_nodes:
        for tgt_lang in ALL_12_LANGUAGES:
            res = autopoly.synthesize_from_sail_unit(
                crt_node, tgt_lang, candidate_target_nodes=(), lhs="a", rhs="b", third="c", fourth="d"
            )
            assert "in_off_24" not in res["code"], (
                f"Unbound 4th input word 'in_off_24' in {crt_node.qualified_name} -> {tgt_lang}: {res['code']}"
            )
            tier_counts[res["tier"]] += 1
            total_syntheses += 1
            crt_syntheses.append(
                {
                    "caller_node": crt_node.qualified_name,
                    "tgt_lang": tgt_lang,
                    "tier": res["tier"],
                    "ext_calls": res.get("ext_calls", []),
                    "code": res["code"],
                }
            )

    elapsed = round(time.time() - t0, 3)
    summary = {
        "languages": list(ALL_12_LANGUAGES),
        "total_cross_language_syntheses": total_syntheses,
        "tier_counts": tier_counts,
        "tier_percentages": {
            k: f"{100.0 * v / total_syntheses:.2f}%" for k, v in tier_counts.items()
        },
        "compiler_rt_caller_syntheses_count": len(crt_syntheses),
        "elapsed_seconds": elapsed,
        "sample_tier1": sample_tier1,
        "sample_tier2": sample_tier2,
        "sample_tier3": sample_tier3,
        "sample_compiler_rt_caller_syntheses": crt_syntheses[:12],
    }
    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    s = run_12lang_tier_verification()
    print(
        f"Completed {s['total_cross_language_syntheses']} 12-language cross-language syntheses in {s['elapsed_seconds']}s!"
    )
    print("Tier breakdown:", json.dumps(s["tier_counts"], indent=2))
    print("Tier percentages:", json.dumps(s["tier_percentages"], indent=2))
