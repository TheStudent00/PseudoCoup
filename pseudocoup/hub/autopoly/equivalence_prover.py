"""equivalence_prover -- proves Domain-to-Range & Piecewise equivalence between UR-Nodes.

Uses `PseudoArch.map_unit_to_lean` (`compose_LoOp_leans`) to extract the exact
piecewise Domain-Range partition `(D_k, R_k)` of any lowered Unit directly from
its machine words via the Sail RISC-V model (`Sl1Lean`), and uses Z3 to prove:
  1. Exact 1-to-1 Mode Equivalence (Delta = empty)
  2. Joint Domain-Partition Refinement (`D_{s,i} && D_{t,j}`) & Sub-Cell Splitting
  3. Symbolic `HiOp`-Variant Guard & Range Composition Synthesis (proven `UNSAT` in Z3)
  4. LoOp-to-HiOpPrimitive Composition Backstop
"""
from __future__ import annotations
from typing import Any, List, Tuple
import z3

from ...ledgerer.universal_rich_node import UniversalRichNode


def _adapt_bv_width(sym: z3.BitVecRef, target_width: int) -> z3.BitVecRef:
    if sym.size() == target_width:
        return sym
    if sym.size() > target_width:
        return z3.Extract(target_width - 1, 0, sym)
    return z3.SignExt(target_width - sym.size(), sym)


def _norm_out_bv(expr: z3.ExprRef | None, target_width: int = 64) -> z3.ExprRef | None:
    """Normalize a UnitLean piece output to `target_width` bits, zero-extending 1-bit/8-bit boolean results."""
    if expr is None or not z3.is_bv(expr):
        return expr
    if expr.size() == target_width:
        return expr
    if expr.size() < target_width:
        if expr.size() in (1, 8):
            return z3.simplify(z3.ZeroExt(target_width - expr.size(), expr))
        return z3.simplify(z3.SignExt(target_width - expr.size(), expr))
    return z3.simplify(z3.Extract(target_width - 1, 0, expr))


_CANON_UL_CACHE: dict[tuple, Tuple[List[Tuple[z3.BoolRef, z3.ExprRef]], z3.ExprRef]] = {}


def simplify_domain_predicate_via_z3(
    cond: z3.BoolRef, a: z3.BitVecRef, b: z3.BitVecRef
) -> z3.BoolRef:
    """Use Z3 model uniqueness to canonicalize 132-bit Sail predicates into minimal
    64-bit hyperplane/point guards when mathematically equivalent (`UNSAT`)."""
    cond = z3.simplify(cond)
    if z3.is_true(cond) or z3.is_false(cond):
        return cond
    abs_conds, div_axioms = _abstract_132bit_div_rem_terms([cond], a, b)
    cond_abs = abs_conds[0]
    s = z3.Solver()
    if s.check(z3.And(div_axioms, cond_abs)) != z3.sat:
        return z3.BoolVal(False)
    m = s.model()
    ca = m.eval(a, model_completion=True)
    cb = m.eval(b, model_completion=True)
    for cand in (b == cb, a == ca, z3.And(a == ca, b == cb)):
        s_eq = z3.Solver()
        if s_eq.check(z3.And(div_axioms, cond_abs != cand)) == z3.unsat:
            return cand
    return cond


_BASE_CANON_UL_CACHE: dict[int, Tuple[List[Tuple[z3.BitVecRef, int]], List[Tuple[z3.BoolRef, z3.ExprRef]], z3.ExprRef]] = {}


def canonicalize_unit_lean(
    unit_lean: Any,
    a: z3.BitVecRef,
    b: z3.BitVecRef,
    c: z3.BitVecRef | None = None,
    d: z3.BitVecRef | None = None,
    *extra_syms: z3.BitVecRef,
) -> Tuple[List[Tuple[z3.BoolRef, z3.ExprRef]], z3.ExprRef]:
    """Substitute canonical symbols `(a, b[, c, d, ...])` for `in_off_*` in a Sail-derived `UnitLean`."""
    ul_id = id(unit_lean)
    if ul_id not in _BASE_CANON_UL_CACHE:
        offsets = sorted(unit_lean.inputs.keys())
        max_in_w = max((unit_lean.inputs[off].size() for off in offsets), default=64)
        base_vars: List[Tuple[z3.BitVecRef, int]] = []
        base_subs = []
        for idx, off in enumerate(offsets):
            in_k = unit_lean.inputs[off]
            v_name = chr(ord("a") + idx) if idx < 26 else f"arg{idx}"
            if in_k.size() == 8 and max_in_w == 64:
                v_sym = z3.BitVec(v_name, 64)
                base_vars.append((v_sym, 64))
                base_subs.append(
                    (in_k, z3.If(v_sym == z3.BitVecVal(0, 64), z3.BitVecVal(0, 8), z3.BitVecVal(1, 8)))
                )
            else:
                v_sym = z3.BitVec(v_name, in_k.size())
                base_vars.append((v_sym, in_k.size()))
                base_subs.append((in_k, v_sym))
        v_a = base_vars[0][0] if len(base_vars) >= 1 else z3.BitVec("a", 64)
        v_b = base_vars[1][0] if len(base_vars) >= 2 else z3.BitVec("b", 64)
        base_pieces = []
        for p in unit_lean.pieces:
            d_sub = z3.simplify(z3.substitute(p.domain, *base_subs)) if base_subs else p.domain
            if v_a.size() == 64 and v_b.size() == 64:
                d_sub = simplify_domain_predicate_via_z3(d_sub, v_a, v_b)
            r_sub = (
                z3.simplify(z3.substitute(p.range_term, *base_subs))
                if (p.range_term is not None and base_subs)
                else p.range_term
            )
            base_pieces.append((d_sub, r_sub))
        valid_base = [(d_s, r_s) for d_s, r_s in base_pieces if r_s is not None]
        if valid_base:
            base_comb = valid_base[-1][1]
            for d_s, r_s in reversed(valid_base[:-1]):
                base_comb = z3.If(d_s, r_s, base_comb)
        else:
            base_comb = (
                z3.simplify(z3.substitute(unit_lean.combined_term, *base_subs))
                if (unit_lean.combined_term is not None and base_subs)
                else unit_lean.combined_term
            )
        _BASE_CANON_UL_CACHE[ul_id] = (base_vars, base_pieces, base_comb)

    base_vars, base_pieces, base_comb = _BASE_CANON_UL_CACHE[ul_id]
    explicit_syms: list[z3.BitVecRef | None] = [a, b, c, d, *extra_syms]
    caller_subs = []
    is_identity = True
    for idx, (v_sym, v_size) in enumerate(base_vars):
        sym_k = explicit_syms[idx] if idx < len(explicit_syms) else None
        if sym_k is not None:
            adapted = _adapt_bv_width(sym_k, v_size)
            if not adapted.eq(v_sym):
                is_identity = False
                caller_subs.append((v_sym, adapted))
    if is_identity or not caller_subs:
        return base_pieces, base_comb

    pieces = [
        (
            z3.simplify(z3.substitute(d_b, *caller_subs)),
            z3.simplify(z3.substitute(r_b, *caller_subs)) if r_b is not None else None,
        )
        for d_b, r_b in base_pieces
    ]
    comb = z3.simplify(z3.substitute(base_comb, *caller_subs)) if base_comb is not None else None
    return pieces, comb


def _abstract_132bit_div_rem_terms(
    exprs: List[z3.ExprRef | None], a: z3.BitVecRef, b: z3.BitVecRef
) -> Tuple[List[z3.ExprRef | None], z3.BoolRef]:
    """Abstract 132-bit Sail `bvsdiv_i`/`bvsrem_i`/`bvudiv_i`/`bvurem_i` nodes using Ackermann congruence
    (`If(And(num == num_0, den == den_0), sym_0, sym_k)`) and range/sign axioms so two 132-bit division/remainder
    applications share a symbol if and only if Z3 proves their 132-bit dividend and divisor operands equal."""
    buckets: dict[str, list[Tuple[z3.ExprRef, z3.ExprRef, z3.BitVecRef]]] = {
        "sdiv": [],
        "srem": [],
        "udiv": [],
        "urem": [],
    }
    subs_map: dict[int, Tuple[z3.ExprRef, z3.ExprRef]] = {}
    seen: set[int] = set()
    stack = [e for e in exprs if e is not None]
    while stack:
        cur = stack.pop()
        cid = cur.get_id()
        if cid in seen:
            continue
        seen.add(cid)
        if z3.is_bv(cur) and cur.size() == 132 and cur.num_args() == 2:
            k = cur.decl().kind()
            nm = cur.decl().name()
            tag: str | None = None
            if k == z3.Z3_OP_BSDIV or nm in ("bvsdiv_i", "bvsdiv"):
                tag = "sdiv"
            elif k == z3.Z3_OP_BSREM or nm in ("bvsrem_i", "bvsrem"):
                tag = "srem"
            elif k == z3.Z3_OP_BUDIV or nm in ("bvudiv_i", "bvudiv"):
                tag = "udiv"
            elif k == z3.Z3_OP_BUREM or nm in ("bvurem_i", "bvurem"):
                tag = "urem"
            if tag is not None:
                num = z3.simplify(cur.arg(0))
                den = z3.simplify(cur.arg(1))
                b_list = buckets[tag]
                if not b_list:
                    sym0 = z3.BitVec(f"q_{tag}_132_0", 132)
                    b_list.append((num, den, sym0))
                    subs_map[cid] = (cur, sym0)
                else:
                    sym_k = z3.BitVec(f"q_{tag}_132_{len(b_list)}", 132)
                    ack_expr: z3.ExprRef = sym_k
                    for b_num, b_den, b_sym in reversed(b_list):
                        if num.eq(b_num) and den.eq(b_den):
                            ack_expr = b_sym
                            break
                        ack_expr = z3.If(z3.And(num == b_num, den == b_den), b_sym, ack_expr)
                    b_list.append((num, den, sym_k))
                    subs_map[cid] = (cur, ack_expr)
                continue
        for i in range(cur.num_args()):
            stack.append(cur.arg(i))

    subs = list(subs_map.values())
    if not subs:
        return exprs, z3.BoolVal(True)

    out = [z3.substitute(e, *subs) if e is not None else None for e in exprs]
    if a.size() == 64 and b.size() == 64 and (buckets["sdiv"] or buckets["srem"]):
        msb = z3.BitVecVal(0x8000000000000000, 64)
        neg1 = z3.BitVecVal(-1, 64)
        zero64 = z3.BitVecVal(0, 64)
        ax_list = []
        for _b_num, _b_den, q_sdiv in buckets["sdiv"]:
            ax_list.append(
                z3.And(
                    q_sdiv >= z3.BitVecVal(-(1 << 63), 132),
                    q_sdiv <= z3.BitVecVal(1 << 63, 132),
                    (q_sdiv == z3.BitVecVal(1 << 63, 132)) == z3.And(a == msb, b == neg1),
                )
            )
        for _b_num, _b_den, r_srem in buckets["srem"]:
            r_64 = z3.Extract(63, 0, r_srem)
            ax_list.append(
                z3.And(
                    z3.Implies(
                        z3.And(a == msb, b == neg1),
                        r_srem == z3.BitVecVal(0, 132),
                    ),
                    (r_64 == zero64) == (r_srem == z3.BitVecVal(0, 132)),
                    z3.Implies(
                        z3.And(b != zero64, r_64 != zero64),
                        z3.And(
                            (r_64 < zero64) == (a < zero64),
                            r_64 + b != zero64,
                        ),
                    ),
                )
            )
        axioms = z3.And(*ax_list) if ax_list else z3.BoolVal(True)
    else:
        axioms = z3.BoolVal(True)
    return out, axioms


def _synthesize_cell_guard_and_range_specs(
    d_res: z3.BoolRef,
    r_s: z3.ExprRef,
    r_t: z3.ExprRef | None,
    delta: z3.ExprRef | None,
    tgt_comb: z3.ExprRef | None,
    d_active: z3.BoolRef,
    a: z3.BitVecRef,
    b: z3.BitVecRef,
) -> dict[str, Any]:
    """Synthesize Z3-proven (`UNSAT`) symbolic `guard_spec` and `range_spec` for a residual cell."""
    zero = z3.BitVecVal(0, 64)
    one = z3.BitVecVal(1, 64)
    neg1 = z3.BitVecVal(-1, 64)
    min_i64 = z3.BitVecVal(0x8000000000000000, 64)

    # 1. Range composition synthesis (proven UNSAT in Z3 on d_res)
    range_spec: dict[str, Any] | None = None
    if r_t is not None and delta is not None and a.size() == 64:
        if delta.eq(one):
            range_spec = {"kind": "base_op", "op": "+", "rhs": ("const", 1)}
        elif delta.eq(neg1):
            range_spec = {"kind": "base_op", "op": "-", "rhs": ("const", 1)}
        elif delta.eq(b):
            range_spec = {"kind": "base_op", "op": "+", "rhs": ("arg", 1)}
        elif delta.eq(-b):
            range_spec = {"kind": "base_op", "op": "-", "rhs": ("arg", 1)}

    if range_spec is None and a.size() == 64 and z3.is_bv(r_s) and r_s.size() == 64:
        range_cands: list[tuple[z3.ExprRef, dict[str, Any]]] = [
            (zero, {"kind": "const", "value": 0}),
            (neg1, {"kind": "const", "value": -1}),
            (min_i64, {"kind": "const", "value": -9223372036854775808}),
            (a, {"kind": "arg", "index": 0}),
            (b, {"kind": "arg", "index": 1}),
        ]
        if r_t is not None and r_t.size() == 64:
            range_cands.extend(
                [
                    (r_t + one, {"kind": "base_op", "op": "+", "rhs": ("const", 1)}),
                    (r_t - one, {"kind": "base_op", "op": "-", "rhs": ("const", 1)}),
                    (r_t + b, {"kind": "base_op", "op": "+", "rhs": ("arg", 1)}),
                    (r_t - b, {"kind": "base_op", "op": "-", "rhs": ("arg", 1)}),
                ]
            )
        if tgt_comb is not None and z3.is_bv(tgt_comb) and tgt_comb.size() == 64:
            tc_63 = z3.simplify(z3.substitute(tgt_comb, (b, z3.BitVecVal(63, 64))))
            range_cands.append((tc_63, {"kind": "base_const_arg1", "const": 63}))

        for cand_expr, spec in range_cands:
            abs_r, ax_r = _abstract_132bit_div_rem_terms([d_res, r_s, cand_expr], a, b)
            s_r = z3.Solver()
            if s_r.check(z3.And(ax_r, abs_r[0], abs_r[1] != abs_r[2])) == z3.unsat:
                range_spec = spec
                break

    if range_spec is None:
        range_spec = {"kind": "z3_backstop", "expr": r_s}

    # 2. Domain guard composition synthesis (proven UNSAT in Z3 on d_active)
    guard_spec: dict[str, Any] | None = None
    if a.size() == 64 and b.size() == 64:
        sext_a = z3.Concat(*([z3.Extract(63, 63, a)] * 68), a)
        sext_b = z3.Concat(*([z3.Extract(63, 63, b)] * 68), b)
        srem_fn = z3.Function("bvsrem_i", z3.BitVecSort(132), z3.BitVecSort(132), z3.BitVecSort(132))
        rem_64 = z3.If(b == zero, a, z3.Extract(63, 0, srem_fn(sext_a, sext_b)))
        opp_rem_nz = z3.And((a ^ b) < zero, rem_64 != zero)

        guard_cands: list[tuple[z3.BoolRef, dict[str, Any]]] = [
            (b == zero, {"kind": "eq_const", "arg": 1, "value": 0}),
            (a == zero, {"kind": "eq_const", "arg": 0, "value": 0}),
            (a != zero, {"kind": "neq_const", "arg": 0, "value": 0}),
            (z3.And(a == min_i64, b == neg1), {"kind": "int64_min_div_neg1"}),
            (z3.UGE(b, z3.BitVecVal(64, 64)), {"kind": "shift_out_of_bounds"}),
            (opp_rem_nz, {"kind": "opp_sign_rem_nonzero"}),
        ]
        for cand_g, g_spec in guard_cands:
            abs_g, ax_g = _abstract_132bit_div_rem_terms([d_active, d_res, cand_g], a, b)
            s_g = z3.Solver()
            if s_g.check(z3.And(ax_g, abs_g[0], abs_g[1] != abs_g[2])) == z3.unsat:
                guard_spec = g_spec
                break
            # Also check under (d_active && b != 0) when b == 0 is either outside domain or guarded separately
            s_g_nz = z3.Solver()
            if (
                g_spec["kind"] == "opp_sign_rem_nonzero"
                and s_g_nz.check(z3.And(ax_g, abs_g[0], b != zero, abs_g[1] != abs_g[2])) == z3.unsat
            ):
                guard_spec = g_spec
                break

    if guard_spec is None:
        guard_spec = {"kind": "z3_backstop", "expr": d_res}

    return {"domain": d_res, "src_range": r_s, "guard": guard_spec, "range": range_spec}


_PARTITION_PROOF_CACHE: dict[tuple[int, int], dict[str, Any]] = {}
_UL_FINGERPRINT_CACHE: dict[int, tuple[int, int, int] | None] = {}


def _eval_bv_sample(
    comb: z3.ExprRef,
    a: z3.BitVecRef,
    b: z3.BitVecRef,
    c: z3.BitVecRef,
    d: z3.BitVecRef,
    av: int,
    bv: int,
    cv: int,
    dv: int,
) -> int | None:
    w = a.size()
    av_u = av & ((1 << w) - 1)
    av_s = av_u - (1 << w) if av_u >= (1 << (w - 1)) else av_u
    sub_e = z3.simplify(
        z3.substitute(
            comb,
            (a, z3.BitVecVal(av_u, w)),
            (b, z3.BitVecVal(bv, w)),
            (c, z3.BitVecVal(cv, w)),
            (d, z3.BitVecVal(dv, w)),
        )
    )
    if z3.is_bv_value(sub_e):
        return int(sub_e.as_long())
    if bv > 0:
        qs_val = -(abs(av_s) // bv) if av_s < 0 else (av_s // bv)
        rs_val = -(abs(av_s) % bv) if av_s < 0 else (av_s % bv)
        qu_val = av_u // bv
        ru_val = av_u % bv
        qs_132 = z3.BitVecVal(qs_val, 132)
        rs_132 = z3.BitVecVal(rs_val, 132)
        qu_132 = z3.BitVecVal(qu_val, 132)
        ru_132 = z3.BitVecVal(ru_val, 132)
        repls: list[tuple[z3.ExprRef, z3.ExprRef]] = []
        stack = [sub_e]
        seen: set[int] = set()
        while stack:
            cur = stack.pop()
            cid = cur.get_id()
            if cid in seen:
                continue
            seen.add(cid)
            if z3.is_bv(cur) and cur.size() == 132:
                k = cur.decl().kind()
                nm = cur.decl().name()
                if k == z3.Z3_OP_BSDIV or nm in ("bvsdiv_i", "bvsdiv"):
                    repls.append((cur, qs_132))
                    continue
                if k == z3.Z3_OP_BUDIV or nm in ("bvudiv_i", "bvudiv"):
                    repls.append((cur, qu_132))
                    continue
                if k == z3.Z3_OP_BSREM or nm in ("bvsrem_i", "bvsrem"):
                    repls.append((cur, rs_132))
                    continue
                if k == z3.Z3_OP_BUREM or nm in ("bvurem_i", "bvurem"):
                    repls.append((cur, ru_132))
                    continue
            for i in range(cur.num_args()):
                stack.append(cur.arg(i))
        if repls:
            sub_e = z3.simplify(z3.substitute(sub_e, *repls))
            if z3.is_bv_value(sub_e):
                return int(sub_e.as_long())
    return None


def _ul_interior_fingerprint(
    ul: UnitLean,
    comb: z3.ExprRef | None,
    a: z3.BitVecRef,
    b: z3.BitVecRef,
    c: z3.BitVecRef,
    d: z3.BitVecRef,
) -> tuple[int, int, int] | None:
    uid = id(ul)
    if uid in _UL_FINGERPRINT_CACHE:
        return _UL_FINGERPRINT_CACHE[uid]
    if comb is None or not z3.is_bv(comb) or a.size() != 64:
        _UL_FINGERPRINT_CACHE[uid] = None
        return None
    v1 = _eval_bv_sample(comb, a, b, c, d, 19, 5, 3, 1)
    v2 = _eval_bv_sample(comb, a, b, c, d, 5, 19, 0, 1)
    v3 = _eval_bv_sample(comb, a, b, c, d, -18, 3, 3, 1)
    fp = (v1, v2, v3) if (v1 is not None and v2 is not None and v3 is not None) else None
    _UL_FINGERPRINT_CACHE[uid] = fp
    return fp


class EquivalenceProver:
    """Symbolic EquivalenceProver powered by Sail-derived UnitLean Domain-Range partitions."""

    @classmethod
    def prove_domain_range_partition(
        cls, node_src: UniversalRichNode, node_tgt: UniversalRichNode
    ) -> dict[str, Any]:
        """Compare the Sail-derived piecewise `(D_k, R_k)` partitions of two UR-Nodes in Z3,
        performing Joint Partition Refinement (`D_{s,i} && D_{t,j}`) and synthesizing
        Z3-proven (`UNSAT`) `HiOp`-variant composition plans for any residual cells."""
        ul_src = node_src.meaning.get("unit_lean")
        if ul_src is None and node_src.meaning.get("unit_obj") is not None:
            from PseudoArch.map_unit_to_lean import compose_LoOp_leans
            ul_src = compose_LoOp_leans(node_src.meaning["unit_obj"])
            node_src.meaning["unit_lean"] = ul_src
        ul_tgt = node_tgt.meaning.get("unit_lean")
        if ul_tgt is None and node_tgt.meaning.get("unit_obj") is not None:
            from PseudoArch.map_unit_to_lean import compose_LoOp_leans
            ul_tgt = compose_LoOp_leans(node_tgt.meaning["unit_obj"])
            node_tgt.meaning["unit_lean"] = ul_tgt
        if ul_src is None or ul_tgt is None:
            raise ValueError(
                f"Both UR-Nodes must carry Sail-derived 'unit_lean' (got src={ul_src is not None}, tgt={ul_tgt is not None}); refusing silent fallback."
            )

        cache_key = (id(ul_src), id(ul_tgt))
        if cache_key in _PARTITION_PROOF_CACHE:
            return _PARTITION_PROOF_CACHE[cache_key]

        if len(ul_src.inputs) != len(ul_tgt.inputs):
            res = {
                "equivalent": False,
                "interior_equivalent": False,
                "tier": "tier3_loop_primitive_backstop",
                "matching_pieces": [],
                "residual_pieces": [],
                "residual_steps": [],
                "composition_plan": {"kind": "tier3_backstop"},
                "z3_status": "sat",
            }
            _PARTITION_PROOF_CACHE[cache_key] = res
            return res

        w_in = 64
        if ul_src.inputs:
            w_in = max(v.size() for v in ul_src.inputs.values())
            if w_in == 8:
                w_in = 8
        a = z3.BitVec("a", w_in)
        b = z3.BitVec("b", w_in)
        c = z3.BitVec("c", w_in)
        d = z3.BitVec("d", w_in)

        src_pieces_raw, src_comb_raw = canonicalize_unit_lean(ul_src, a, b, c, d)
        tgt_pieces_raw, tgt_comb_raw = canonicalize_unit_lean(ul_tgt, a, b, c, d)
        src_val_pieces = [
            (d_s, _norm_out_bv(r_s, w_in)) for d_s, r_s in src_pieces_raw if r_s is not None
        ]
        tgt_val_pieces = [
            (d_t, _norm_out_bv(r_t, w_in)) for d_t, r_t in tgt_pieces_raw if r_t is not None
        ]
        src_comb = _norm_out_bv(src_comb_raw, w_in)
        tgt_comb = _norm_out_bv(tgt_comb_raw, w_in)
        if src_comb is None or tgt_comb is None or src_comb.sort() != tgt_comb.sort():
            res = {
                "equivalent": False,
                "interior_equivalent": False,
                "tier": "tier3_loop_primitive_backstop",
                "matching_pieces": [],
                "residual_pieces": [],
                "residual_steps": [],
                "composition_plan": {"kind": "tier3_backstop"},
                "z3_status": "sat",
            }
            _PARTITION_PROOF_CACHE[cache_key] = res
            return res

        fp_src = _ul_interior_fingerprint(ul_src, src_comb, a, b, c, d)
        fp_tgt = _ul_interior_fingerprint(ul_tgt, tgt_comb, a, b, c, d)
        if fp_src is not None and fp_tgt is not None and fp_src != fp_tgt:
            res = {
                "equivalent": False,
                "interior_equivalent": False,
                "tier": "tier3_loop_primitive_backstop",
                "matching_pieces": [],
                "residual_pieces": [],
                "residual_steps": [],
                "composition_plan": {"kind": "tier3_backstop"},
                "z3_status": "sat",
            }
            _PARTITION_PROOF_CACHE[cache_key] = res
            return res

        src_domain = z3.simplify(z3.Or(*[d_s for d_s, _ in src_val_pieces])) if src_val_pieces else z3.BoolVal(True)
        tgt_domain = z3.simplify(z3.Or(*[d_t for d_t, _ in tgt_val_pieces])) if tgt_val_pieces else z3.BoolVal(True)

        # Helper to check if target UnitLean masks its 2nd argument by `& 63`
        tgt_masks_arg1_63 = False
        if w_in == 64 and len(ul_tgt.inputs) == 2 and tgt_comb is not None and z3.is_bv(tgt_comb):
            tc_masked = z3.simplify(z3.substitute(tgt_comb, (b, b & z3.BitVecVal(63, 64))))
            s_m = z3.Solver()
            s_non_const = z3.Solver()
            if (
                s_m.check(z3.And(tgt_domain, tgt_comb != tc_masked)) == z3.unsat
                and s_non_const.check(tgt_comb != z3.substitute(tgt_comb, (b, z3.BitVecVal(0, 64)))) == z3.sat
            ):
                tgt_masks_arg1_63 = True

        # Check explicit constant point-guard pieces in src_val_pieces (e.g. INT64_MIN / -1 -> INT64_MIN)
        explicit_point_guards: list[dict[str, Any]] = []
        if w_in == 64 and len(src_val_pieces) == 2:
            min_i64 = z3.BitVecVal(0x8000000000000000, 64)
            neg1 = z3.BitVecVal(-1, 64)
            for d_p, r_p in src_val_pieces:
                if z3.is_bv_value(r_p) and r_p.as_long() == 0x8000000000000000:
                    s_pt = z3.Solver()
                    if s_pt.check(d_p != z3.And(a == min_i64, b == neg1)) == z3.unsat:
                        explicit_point_guards.append(
                            {
                                "guard": {"kind": "int64_min_div_neg1"},
                                "range": {"kind": "const", "value": -9223372036854775808},
                            }
                        )

        if src_comb is not None and tgt_comb is not None and src_comb.sort() == tgt_comb.sort():
            abs_terms, div_axioms = _abstract_132bit_div_rem_terms(
                [src_domain, tgt_domain, src_comb, tgt_comb], a, b
            )
            sd_abs, td_abs, sc_abs, tc_abs = abs_terms[0], abs_terms[1], abs_terms[2], abs_terms[3]
            s_all = z3.Solver()
            s_all.add(z3.And(div_axioms, sd_abs, z3.Or(z3.Not(td_abs), sc_abs != tc_abs)))
            if s_all.check() == z3.unsat:
                res = {
                    "equivalent": True,
                    "tier": "tier1_exact_native_hiop",
                    "matching_pieces": src_val_pieces,
                    "residual_pieces": [],
                    "residual_steps": [],
                    "composition_plan": {
                        "kind": "arg1_mask_63" if tgt_masks_arg1_63 else "exact",
                        "explicit_point_guards": explicit_point_guards,
                    },
                    "z3_status": "unsat",
                }
                _PARTITION_PROOF_CACHE[cache_key] = res
                return res

        # Joint Partition Refinement: refine each (d_s, r_s) against target pieces (d_t, r_t)
        matching_pieces: list[Tuple[z3.BoolRef, z3.ExprRef]] = []
        raw_residual_cells: list[dict[str, Any]] = []

        for d_s, r_s in src_val_pieces:
            if tgt_comb is None or r_s.sort() != tgt_comb.sort():
                raw_residual_cells.append(
                    {"domain": d_s, "src_range": r_s, "tgt_range": None, "delta": None}
                )
                continue

            # Fast path: check if the entire unsplit source piece matches target
            abs_terms, div_axioms = _abstract_132bit_div_rem_terms([d_s, tgt_domain, r_s, tgt_comb], a, b)
            ds_abs, td_abs, rs_abs, tc_abs = abs_terms[0], abs_terms[1], abs_terms[2], abs_terms[3]
            s_piece = z3.Solver()
            s_piece.add(z3.And(div_axioms, ds_abs, z3.Or(z3.Not(td_abs), rs_abs != tc_abs)))
            if s_piece.check() == z3.unsat:
                matching_pieces.append((d_s, r_s))
                continue

            # Refine (d_s, r_s) across target pieces (d_t, r_t)
            for d_t, r_t in tgt_val_pieces:
                if r_s.sort() != r_t.sort():
                    continue
                d_ij = z3.simplify(z3.And(d_s, d_t))
                if z3.is_false(d_ij):
                    continue
                abs_ij, ax_ij = _abstract_132bit_div_rem_terms([d_ij, r_s, r_t], a, b)
                dij_abs, rs_ij, rt_ij = abs_ij[0], abs_ij[1], abs_ij[2]
                s_sat = z3.Solver()
                if s_sat.check(z3.And(ax_ij, dij_abs)) != z3.sat:
                    continue

                s_eq = z3.Solver()
                if s_eq.check(z3.And(ax_ij, dij_abs, rs_ij != rt_ij)) == z3.unsat:
                    matching_pieces.append((d_ij, r_s))
                    continue

                # Sub-cell refinement: check if rs_ij == rt_ij on a sub-cell and rs_ij == rt_ij + delta on its complement
                if w_in == 64 and z3.is_bv(r_s) and r_s.size() == 64:
                    s_sub = z3.Solver()
                    if s_sub.check(z3.And(ax_ij, dij_abs, rs_ij == rt_ij)) == z3.sat:
                        split_delta = None
                        for d_cand in (
                            z3.BitVecVal(1, 64),
                            z3.BitVecVal(-1, 64),
                            b,
                            -b,
                        ):
                            s_del = z3.Solver()
                            if (
                                s_del.check(
                                    z3.And(ax_ij, dij_abs, rs_ij != rt_ij, rs_ij != rt_ij + d_cand)
                                )
                                == z3.unsat
                            ):
                                split_delta = d_cand
                                break
                        if split_delta is not None:
                            d_eq = z3.simplify(z3.And(d_ij, r_s == r_t))
                            d_neq = z3.simplify(z3.And(d_ij, r_s != r_t))
                            r_s_neq = z3.simplify(r_t + split_delta)
                            matching_pieces.append((d_eq, r_s))
                            raw_residual_cells.append(
                                {
                                    "domain": d_neq,
                                    "src_range": r_s_neq,
                                    "tgt_range": r_t,
                                    "delta": split_delta,
                                }
                            )
                            continue

                # Check if rs_ij == rt_ij + delta across the entire cell d_ij (when r_s is not already a constant or argument)
                cell_delta = None
                if (
                    w_in == 64
                    and z3.is_bv(r_s)
                    and r_s.size() == 64
                    and not z3.is_bv_value(r_s)
                    and not r_s.eq(a)
                    and not r_s.eq(b)
                ):
                    for d_cand in (
                        z3.BitVecVal(1, 64),
                        z3.BitVecVal(-1, 64),
                        b,
                        -b,
                    ):
                        s_del = z3.Solver()
                        if s_del.check(z3.And(ax_ij, dij_abs, rs_ij != rt_ij + d_cand)) == z3.unsat:
                            cell_delta = d_cand
                            break
                d_ij_simp = simplify_domain_predicate_via_z3(d_ij, a, b) if w_in == 64 else d_ij
                raw_residual_cells.append(
                    {
                        "domain": d_ij_simp,
                        "src_range": r_s,
                        "tgt_range": r_t,
                        "delta": cell_delta,
                    }
                )

            # Check outside-target-domain cell: d_s && Not(tgt_domain)
            d_out = z3.simplify(z3.And(d_s, z3.Not(tgt_domain)))
            if not z3.is_false(d_out):
                abs_out, ax_out = _abstract_132bit_div_rem_terms([d_out], a, b)
                s_out = z3.Solver()
                if s_out.check(z3.And(ax_out, abs_out[0])) == z3.sat:
                    d_out_simp = simplify_domain_predicate_via_z3(d_out, a, b) if w_in == 64 else d_out
                    raw_residual_cells.append(
                        {"domain": d_out_simp, "src_range": r_s, "tgt_range": None, "delta": None}
                    )

        # Merge residual cells that share the same non-None delta (e.g. PY_FLOORDIV pieces 3 and 4)
        merged_cells: list[dict[str, Any]] = []
        for cell in raw_residual_cells:
            del_c = cell["delta"]
            if del_c is not None:
                found_m = False
                for prev in merged_cells:
                    if prev["delta"] is not None and prev["delta"].eq(del_c):
                        prev["domain"] = z3.simplify(z3.Or(prev["domain"], cell["domain"]))
                        found_m = True
                        break
                if found_m:
                    continue
            merged_cells.append(dict(cell))

        residual_pieces = [(c_item["domain"], c_item["src_range"]) for c_item in merged_cells]

        if matching_pieces and not residual_pieces:
            res = {
                "equivalent": True,
                "tier": "tier1_exact_native_hiop",
                "matching_pieces": matching_pieces,
                "residual_pieces": [],
                "residual_steps": [],
                "composition_plan": {
                    "kind": "arg1_mask_63" if tgt_masks_arg1_63 else "exact",
                    "explicit_point_guards": explicit_point_guards,
                },
                "z3_status": "unsat",
            }
            _PARTITION_PROOF_CACHE[cache_key] = res
            return res

        if matching_pieces and residual_pieces:
            # Check if masking 2nd argument by `& 63` eliminates all residual pieces (e.g. C.BV_SHL -> Go.BV_SHL)
            if (
                w_in == 64
                and len(ul_src.inputs) == 2
                and src_comb is not None
                and tgt_comb is not None
                and z3.is_bv(src_comb)
                and z3.is_bv(tgt_comb)
            ):
                tc_masked63 = z3.simplify(z3.substitute(tgt_comb, (b, b & z3.BitVecVal(63, 64))))
                td_masked63 = z3.simplify(z3.substitute(tgt_domain, (b, b & z3.BitVecVal(63, 64))))
                abs_m, ax_m = _abstract_132bit_div_rem_terms(
                    [src_domain, td_masked63, src_comb, tc_masked63], a, b
                )
                s_mask = z3.Solver()
                if (
                    s_mask.check(
                        z3.And(ax_m, abs_m[0], z3.Or(z3.Not(abs_m[1]), abs_m[2] != abs_m[3]))
                    )
                    == z3.unsat
                ):
                    res = {
                        "equivalent": False,
                        "interior_equivalent": True,
                        "tier": "tier2_piecewise_hiop",
                        "matching_pieces": matching_pieces,
                        "residual_pieces": residual_pieces,
                        "residual_steps": [],
                        "composition_plan": {"kind": "arg1_mask_63", "explicit_point_guards": []},
                        "z3_status": "unsat",
                    }
                    _PARTITION_PROOF_CACHE[cache_key] = res
                    return res

            residual_steps = [
                _synthesize_cell_guard_and_range_specs(
                    c_item["domain"],
                    c_item["src_range"],
                    c_item["tgt_range"],
                    c_item["delta"],
                    tgt_comb,
                    src_domain,
                    a,
                    b,
                )
                for c_item in merged_cells
            ]
            res = {
                "equivalent": False,
                "interior_equivalent": True,
                "tier": "tier2_piecewise_hiop",
                "matching_pieces": matching_pieces,
                "residual_pieces": residual_pieces,
                "residual_steps": residual_steps,
                "composition_plan": {
                    "kind": "piecewise_ite",
                    "base_masks_arg1_63": tgt_masks_arg1_63,
                    "steps": residual_steps,
                    "explicit_point_guards": explicit_point_guards,
                },
                "z3_status": "unsat",
            }
            _PARTITION_PROOF_CACHE[cache_key] = res
            return res

        res = {
            "equivalent": False,
            "interior_equivalent": False,
            "tier": "tier3_loop_primitive_backstop",
            "matching_pieces": matching_pieces,
            "residual_pieces": residual_pieces,
            "residual_steps": [],
            "composition_plan": {"kind": "tier3_backstop"},
            "z3_status": "sat",
        }
        _PARTITION_PROOF_CACHE[cache_key] = res
        return res

    @staticmethod
    def build_bv64_formula(
        node: UniversalRichNode, a: z3.BitVecRef, b: z3.BitVecRef
    ) -> tuple[z3.BoolRef, z3.BoolRef, z3.BitVecRef]:
        """Return (D_ok, D_trap, R_val) purely from the node's Sail-derived `UnitLean`."""
        if not isinstance(node, UniversalRichNode):
            raise ValueError(f"Expected UniversalRichNode with Sail-derived 'unit_lean', got {node!r}")
        ul = node.meaning.get("unit_lean")
        if ul is None and node.meaning.get("unit_obj") is not None:
            from PseudoArch.map_unit_to_lean import compose_LoOp_leans
            ul = compose_LoOp_leans(node.meaning["unit_obj"])
            node.meaning["unit_lean"] = ul
        if ul is None:
            raise ValueError(
                f"UniversalRichNode {node.qualified_name!r} lacks Sail-derived 'unit_lean'; refusing silent fallback."
            )
        pieces, comb = canonicalize_unit_lean(ul, a, b)
        d_ok = z3.Or(*[d for d, r in pieces if r is not None]) if pieces else z3.BoolVal(True)
        d_ok = z3.simplify(d_ok)
        if comb is None:
            raise ValueError(f"UniversalRichNode {node.qualified_name!r} has no value-producing pieces in UnitLean.")
        return d_ok, z3.simplify(z3.Not(d_ok)), _norm_out_bv(comb, 64)

    @classmethod
    def prove_nodes_equivalent(cls, node_a: UniversalRichNode, node_b: UniversalRichNode) -> dict[str, Any]:
        """Prove whether two UR-Nodes are equivalent via their Sail-derived `UnitLean` partitions."""
        return cls.prove_domain_range_partition(node_a, node_b)

    @classmethod
    def prove_piecewise_polyfill(cls, src_node: UniversalRichNode, polyfill_expr_fn) -> dict[str, Any]:
        """Prove a synthesized piecewise target expression equals `src_node`'s Sail-derived `UnitLean` on D_ok."""
        a = z3.BitVec("a", 64)
        b = z3.BitVec("b", 64)
        dok, _dtrap, r_src = cls.build_bv64_formula(src_node, a, b)
        r_poly = polyfill_expr_fn(a, b)
        s = z3.Solver()
        s.add(z3.And(dok, r_src != r_poly))
        res = s.check()
        return {"verified": (res == z3.unsat), "z3_status": str(res)}
