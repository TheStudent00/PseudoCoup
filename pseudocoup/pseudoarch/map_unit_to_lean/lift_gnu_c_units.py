"""lift_gnu_c_units -- Runs `map_unit_to_lean` (`compose_LoOp_leans`, `map_sail_to_lean_direct`,
and `map_sail_to_lean_by_gmp`) over lowered GNU C RISC-V Units (`gnu_c_*.jsonl.gz`) and writes
a complete `UnitLean` summary.
"""
from __future__ import annotations

import gzip
import json
import multiprocessing
import os
import re
import resource
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PSEUDOARCH_DIR = os.path.normpath(os.path.join(HERE, ".."))
PCHQ = os.path.normpath(os.path.join(PSEUDOARCH_DIR, "..", ".."))
PROJECTS_DIR = os.path.normpath(os.path.join(PSEUDOARCH_DIR, ".."))
if PROJECTS_DIR not in sys.path:
    sys.path.insert(0, PROJECTS_DIR)

from PseudoArch.map_HiOp_to_unit.lower_HiOp import Word
from PseudoArch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import Unit
from PseudoArch.map_LoOp_to_lean import decode_word
from PseudoArch.map_LoOp_to_lean.map_sail_to_lean_direct import shared_sail_lifter
from PseudoArch.map_unit_to_lean import compose_LoOp_leans
from PseudoArch.map_unit_to_lean.compose_LoOp_leans import TRAP_ARCH_OPCODES
import lifter as _lifter


def reconstruct_unit(rec: dict) -> Unit:
    words = rec.get("words") or []
    unit_idxs = rec.get("unit") or []
    raw_words = [
        words[i]
        for i in unit_idxs
        if isinstance(i, int) and i < len(words)
    ]
    base_addr = raw_words[0][0] if raw_words else 0
    unit_words = tuple(
        Word(w[0] - base_addr, w[1], w[2], w[3], tuple(w[4]))
        for w in raw_words
    )
    holds_p = tuple((int(p[0]), str(p[1])) for p in (rec.get("holds_p") or ()))
    parts = tuple(str(p) for p in (rec.get("parts") or ()))
    return Unit(str(rec.get("symbol", "op")), unit_words, parts, holds_p, rec.get("refusal"))


import z3
import lean_reader as LR


def _to_picklable(x: object) -> object:
    if isinstance(x, LR.Ctor):
        return ("Ctor", x.name, [_to_picklable(a) for a in x.args])
    if isinstance(x, LR.LInt):
        return ("LInt", int(z3.simplify(x.term).as_signed_long()))
    if isinstance(x, tuple):
        return ("tuple", [_to_picklable(a) for a in x])
    if z3.is_bv(x):
        s = z3.simplify(x)
        return ("bv", int(s.as_long()), int(s.size()))
    if z3.is_bool(x):
        return ("bool", bool(z3.is_true(z3.simplify(x))))
    return x


def _from_picklable(x: object) -> object:
    if isinstance(x, tuple) and x:
        tag = x[0]
        if tag == "Ctor":
            return LR.Ctor(x[1], [_from_picklable(a) for a in x[2]])
        if tag == "LInt":
            return LR.lint(x[1])
        if tag == "tuple":
            return tuple(_from_picklable(a) for a in x[1])
        if tag == "bv":
            return z3.BitVecVal(x[1], x[2])
        if tag == "bool":
            return z3.BoolVal(x[1])
    return x


def _decode_one_word(ws: tuple[int, int]) -> tuple[tuple[int, int], object]:
    gl = shared_sail_lifter()
    try:
        return ws, _to_picklable(gl.decode(ws[0], ws[1]))
    except Exception:
        return ws, None


def _lift_one_unit(u: Unit) -> dict:
    try:
        resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    except Exception:
        pass
    os.environ["SL1_WORK"] = f"/tmp/sl1_lifter_{os.getpid()}"
    direct_ops = []
    ext_ops = []
    all_direct = True
    for w in u.words:
        if any(r.split()[-1].startswith("part_") for r in w.relocations):
            continue
        if w.arch_opcode in TRAP_ARCH_OPCODES:
            direct_ops.append(w.arch_opcode)
            continue
        try:
            ll = decode_word(int(w.bytes_hex, 16), 2 if len(w.bytes_hex) == 4 else 4)
            if ll is not None:
                direct_ops.append(w.arch_opcode)
            else:
                all_direct = False
                ext_ops.append(w.arch_opcode)
        except _lifter.LiftRefused:
            all_direct = False
            ext_ops.append(w.arch_opcode)
    try:
        ulean = compose_LoOp_leans(u)
        return {
            "ok": True,
            "all_direct": all_direct,
            "direct_ops": direct_ops,
            "ext_ops": ext_ops,
            "ext_calls": ulean.ext_calls,
            "num_pieces": len(ulean.pieces),
            "combined_term": str(ulean.combined_term) if ulean.combined_term is not None else None,
        }
    except _lifter.LiftRefused as exc:
        return {
            "ok": False,
            "all_direct": all_direct,
            "direct_ops": direct_ops,
            "ext_ops": ext_ops,
            "reason": str(exc).split("\n")[0][:120],
        }


def main() -> None:
    in_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(PCHQ, "Research", "lower_HiOp", "out", "gnu_c_first_of_each_hijacked.jsonl.gz")
    )
    out_summary_path = in_path.replace(".jsonl.gz", "_unit_lean_summary.json")

    total = 0
    lowered = 0
    empty_units = 0
    lifted_units = 0
    sail_refused_units = 0
    value_producing_units = 0
    multi_piece_units = 0
    all_words_direct_sail = 0
    units_with_calls = 0
    opcode_direct_counts: Counter[str] = Counter()
    opcode_ext_counts: Counter[str] = Counter()
    sail_refusal_reasons: Counter[str] = Counter()
    piece_count_hist: Counter[int] = Counter()
    sample_lifted = []

    unique_units: dict[tuple, Unit] = {}
    records_with_keys: list[tuple[dict, tuple]] = []

    with gzip.open(in_path, "rt", encoding="utf-8") as gz:
        for line in gz:
            rec = json.loads(line)
            total += 1
            if rec.get("refusal") is not None:
                continue
            lowered += 1
            u = reconstruct_unit(rec)
            if not u.words:
                empty_units += 1
                continue
            has_call = any(
                w.arch_opcode in ("jal", "jalr", "c.jalr") or any("CALL" in r for r in w.relocations)
                for w in u.words
            )
            if has_call:
                units_with_calls += 1
            ukey = (
                tuple(
                    (
                        w.address,
                        w.bytes_hex,
                        tuple(re.sub(r"part_func_\d+_", "part_", r) for r in w.relocations),
                    )
                    for w in u.words
                ),
                u.holds_p,
            )
            if ukey not in unique_units:
                unique_units[ukey] = u
            records_with_keys.append((rec, ukey))

    ukeys_list = list(unique_units.keys())
    units_list = [unique_units[k] for k in ukeys_list]
    gl = shared_sail_lifter()
    unique_ws = {
        (int(w.bytes_hex, 16), 2 if len(w.bytes_hex) == 4 else 4)
        for u in units_list
        for w in u.words
    }
    n_workers = min(16, os.cpu_count() or 8)
    ctx = multiprocessing.get_context("fork")
    print(f"Pre-decoding {len(unique_ws)} unique words across {n_workers} workers...", flush=True)
    with ctx.Pool(n_workers) as pool:
        for ws, decoded_ast in pool.imap_unordered(_decode_one_word, sorted(unique_ws), chunksize=16):
            if decoded_ast is not None:
                gl.decoded[ws] = _from_picklable(decoded_ast)
    print(f"Pre-decoded {len(gl.decoded)} words. Lifting {len(units_list)} unique units...", flush=True)
    results_list = []
    with ctx.Pool(n_workers) as pool:
        for idx, res in enumerate(pool.imap(_lift_one_unit, units_list, chunksize=4), 1):
            results_list.append(res)
            if idx % 200 == 0 or idx == len(units_list):
                print(f"  Lifted {idx}/{len(units_list)} unique units...", flush=True)
    ukey_to_res = dict(zip(ukeys_list, results_list))

    refused_unlinked_reloc = 0
    refused_illegal_isa_ext = 0
    refused_gmp_or_other = 0
    self_contained_direct_sail_units = 0
    caller_units_with_ext_calls = 0
    caller_units_compiler_rt = 0
    caller_units_libc_or_os = 0
    non_reloc_refusal_reasons: Counter[str] = Counter()

    crt_path = os.path.join(PCHQ, "Research", "lower_HiOp", "out", "infrastructure_l157", "compiler_rt_riscv64.jsonl.gz")
    compiler_rt_syms: set[str] = set()
    if os.path.isfile(crt_path):
        with gzip.open(crt_path, "rt", encoding="utf-8") as _cf:
            for _line in _cf:
                _r = json.loads(_line)
                if _r.get("words"):
                    compiler_rt_syms.add(str(_r.get("routine") or _r.get("symbol") or _r.get("name")))

    for rec, ukey in records_with_keys:
        res = ukey_to_res[ukey]
        for op in res["direct_ops"]:
            opcode_direct_counts[op] += 1
        for op in res["ext_ops"]:
            opcode_ext_counts[op] += 1
        if not res["ok"]:
            sail_refused_units += 1
            reason = res["reason"]
            sail_refusal_reasons[reason] += 1
            if "UNLINKED_RELOC" in reason:
                refused_unlinked_reloc += 1
            elif "DECODE_ILLEGAL" in reason or "EXECUTE_NON_RETIRE" in reason or "TRAP_ONLY_UNIT" in reason:
                refused_illegal_isa_ext += 1
                non_reloc_refusal_reasons[f"{rec['operator']}: {reason}"] += 1
            else:
                refused_gmp_or_other += 1
                non_reloc_refusal_reasons[f"{rec['operator']}: {reason}"] += 1
            continue
        lifted_units += 1
        ext_calls = res.get("ext_calls", ())
        if not ext_calls:
            self_contained_direct_sail_units += 1
        else:
            caller_units_with_ext_calls += 1
            if all(ec in compiler_rt_syms for ec in ext_calls):
                caller_units_compiler_rt += 1
            else:
                caller_units_libc_or_os += 1
        if res["all_direct"]:
            all_words_direct_sail += 1
        n_pieces = res["num_pieces"]
        piece_count_hist[n_pieces] += 1
        if n_pieces > 1:
            multi_piece_units += 1
        if res["combined_term"] is not None:
            value_producing_units += 1
            if len(sample_lifted) < 25 and res["all_direct"]:
                u = unique_units[ukey]
                sample_lifted.append({
                    "operator": rec["operator"],
                    "template": rec["template"],
                    "holders": [h[1] for h in rec.get("holders", ())],
                    "lo_ops": [w.arch_opcode for w in u.words],
                    "num_pieces": n_pieces,
                    "combined_term": res["combined_term"],
                })

    summary = {
        "input_path": in_path,
        "total_variants": total,
        "lowered_variants": lowered,
        "empty_units": empty_units,
        "lifted_units": lifted_units,
        "self_contained_direct_sail_units": self_contained_direct_sail_units,
        "caller_units_with_ext_calls": caller_units_with_ext_calls,
        "caller_units_compiler_rt": caller_units_compiler_rt,
        "caller_units_libc_or_os": caller_units_libc_or_os,
        "sail_refused_units": sail_refused_units,
        "refused_unlinked_reloc": refused_unlinked_reloc,
        "refused_illegal_isa_ext": refused_illegal_isa_ext,
        "refused_gmp_or_other": refused_gmp_or_other,
        "all_words_direct_sail_units": all_words_direct_sail,
        "value_producing_units": value_producing_units,
        "multi_piece_units": multi_piece_units,
        "units_with_calls": units_with_calls,
        "piece_count_histogram": {str(k): v for k, v in sorted(piece_count_hist.items())},
        "direct_sail_opcodes": dict(opcode_direct_counts.most_common(50)),
        "extension_or_call_opcodes": dict(opcode_ext_counts.most_common(50)),
        "sail_refusal_reasons": dict(sail_refusal_reasons.most_common(30)),
        "non_reloc_refusal_reasons": dict(non_reloc_refusal_reasons.most_common(50)),
        "sample_lifted": sample_lifted,
    }
    with open(out_summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"=== UnitLean Lifting Summary ({os.path.basename(in_path)}) ===")
    print(f"  Total variants            : {total}")
    print(f"  Lowered variants          : {lowered}")
    print(f"  Non-empty Units lifted    : {lifted_units} (empty/no-op: {empty_units}, Sail-refused: {sail_refused_units})")
    print(f"    Self-contained Direct   : {self_contained_direct_sail_units}")
    print(f"    Caller Units (ext_calls): {caller_units_with_ext_calls} (compiler-rt: {caller_units_compiler_rt}, libc/libm/OS: {caller_units_libc_or_os})")
    print(f"  100% Direct-Sail Units    : {all_words_direct_sail}")
    print(f"  Value-producing UnitLeans : {value_producing_units}")
    print(f"  Multi-piece DR UnitLeans  : {multi_piece_units}")
    print(f"  Piece count histogram     : {dict(sorted(piece_count_hist.items()))}")
    print(f"  Distinct Direct-Sail ops  : {len(opcode_direct_counts)}")
    print(f"  Distinct Ext/Call ops     : {len(opcode_ext_counts)}")
    if non_reloc_refusal_reasons:
        print("  Non-reloc refusal reasons :")
        for reason, cnt in non_reloc_refusal_reasons.most_common(20):
            print(f"    {cnt:5d}  {reason}")
    if sail_refusal_reasons:
        print("  Top Sail refusal reasons  :")
        for reason, cnt in sail_refusal_reasons.most_common(10):
            print(f"    {cnt:5d}  {reason}")


if __name__ == "__main__":
    main()
