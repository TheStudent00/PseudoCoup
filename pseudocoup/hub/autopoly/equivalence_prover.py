"""equivalence_prover -- proves Domain-to-Range & Piecewise equivalence between UR-Nodes.

Sits beside UniversalRichNode under AutoPoly (`Planning/CORE_0_0_0_pseudocoup.md,
`CORE_0_0_0_1_ledgerer.md` ## design). Uses Z3 BitVec64 / Lean 4 `bv_decide` to prove:
  1. Exact 1-to-1 Mode Equivalence (Delta = empty)
  2. Piecewise Guarded Equivalence (D = D_fast U D_edge)
  3. LoOp-to-HiOpPrimitive Composition Equivalence
"""
from __future__ import annotations
from typing import Any
import z3

from ...ledgerer.universal_rich_node import UniversalRichNode


class EquivalenceProver:
    """Symbolic BitVec64 EquivalenceProver for UR-Nodes and AutoPoly synthesis."""

    @staticmethod
    def build_bv64_formula(expr_kind: str, a: z3.BitVecRef, b: z3.BitVecRef) -> tuple[z3.BoolRef, z3.BoolRef, z3.BitVecRef]:
        """Return (D_ok, D_trap, R_val) for a canonical RISC-V Unit meaning."""
        ZERO = z3.BitVecVal(0, 64)
        ONE = z3.BitVecVal(1, 64)
        NEG1 = z3.BitVecVal((1 << 64) - 1, 64)
        MIN64 = z3.BitVecVal(1 << 63, 64)
        MASK63 = z3.BitVecVal(63, 64)

        if expr_kind == "bvadd":
            return z3.BoolVal(True), z3.BoolVal(False), a + b
        if expr_kind == "bvsub":
            return z3.BoolVal(True), z3.BoolVal(False), a - b
        if expr_kind == "bvmul":
            return z3.BoolVal(True), z3.BoolVal(False), a * b
        if expr_kind == "bvand":
            return z3.BoolVal(True), z3.BoolVal(False), a & b
        if expr_kind == "bvor":
            return z3.BoolVal(True), z3.BoolVal(False), a | b
        if expr_kind == "bvxor":
            return z3.BoolVal(True), z3.BoolVal(False), a ^ b
        if expr_kind == "bvnot":
            return z3.BoolVal(True), z3.BoolVal(False), ~a
        if expr_kind == "bvshl_mask63":
            return z3.BoolVal(True), z3.BoolVal(False), a << (b & MASK63)
        if expr_kind == "bvlshr_mask63":
            return z3.BoolVal(True), z3.BoolVal(False), z3.LShR(a, b & MASK63)
        if expr_kind == "bvashr_mask63":
            return z3.BoolVal(True), z3.BoolVal(False), a >> (b & MASK63)
        if expr_kind == "go_shl_64":
            return z3.BoolVal(True), z3.BoolVal(False), z3.If(z3.ULT(b, z3.BitVecVal(64, 64)), a << b, ZERO)
        if expr_kind == "c_sdiv":
            d_ok = z3.And(b != ZERO, z3.Not(z3.And(a == MIN64, b == NEG1)))
            return d_ok, z3.Not(d_ok), a / b
        if expr_kind == "go_java_sdiv":
            d_ok = (b != ZERO)
            r_val = z3.If(z3.And(a == MIN64, b == NEG1), MIN64, a / b)
            return d_ok, (b == ZERO), r_val
        if expr_kind == "rust_srem":
            d_ok = z3.And(b != ZERO, z3.Not(z3.And(a == MIN64, b == NEG1)))
            return d_ok, z3.Not(d_ok), z3.SRem(a, b)
        if expr_kind == "python_floordiv":
            d_ok = (b != ZERO)
            q = a / b
            r = z3.SRem(a, b)
            adj = z3.If(z3.And(r != ZERO, (a ^ b) < ZERO), q - ONE, q)
            return d_ok, (b == ZERO), adj
        if expr_kind == "spaceship_lcmp":
            r_val = z3.If(a > b, ONE, z3.If(a < b, NEG1, ZERO))
            return z3.BoolVal(True), z3.BoolVal(False), r_val
        raise ValueError(f"Unknown expr_kind: {expr_kind}")

    @classmethod
    def prove_nodes_equivalent(cls, node_a: UniversalRichNode, node_b: UniversalRichNode) -> dict[str, Any]:
        """Prove whether two UR-Nodes have identical (D_ok, D_trap, R_val) across all 2^128 BitVec64 inputs."""
        a = z3.BitVec("a", 64)
        b = z3.BitVec("b", 64)
        dok_a, dtrap_a, r_a = cls.build_bv64_formula(node_a.meaning["R_kind"], a, b)
        dok_b, dtrap_b, r_b = cls.build_bv64_formula(node_b.meaning["R_kind"], a, b)

        s = z3.Solver()
        # Check if either the defined domain differs or the value on the common defined domain differs
        s.add(z3.Or(dok_a != dok_b, z3.And(dok_a, r_a != r_b)))
        res = s.check()
        if res == z3.unsat:
            return {"equivalent": True, "tier": "tier1_exact_native_hiop", "z3_status": "unsat"}

        # Otherwise check if R_val agrees on the interior intersection (dok_a & dok_b & !(a==MIN & b==-1) & b<64)
        MIN64 = z3.BitVecVal(1 << 63, 64)
        NEG1 = z3.BitVecVal((1 << 64) - 1, 64)
        s_int = z3.Solver()
        interior = z3.And(dok_a, dok_b, z3.Not(z3.And(a == MIN64, b == NEG1)), z3.ULT(b, z3.BitVecVal(64, 64)))
        s_int.add(z3.And(interior, r_a != r_b))
        int_res = s_int.check()
        return {
            "equivalent": False,
            "interior_equivalent": (int_res == z3.unsat),
            "tier": "tier2_piecewise_hiop" if int_res == z3.unsat else "tier3_loop_primitive_backstop",
            "z3_status": str(int_res),
        }

    @classmethod
    def prove_piecewise_polyfill(cls, src_kind: str, polyfill_expr_fn) -> dict[str, Any]:
        """Prove a synthesized piecewise target expression equals `src_kind` on D_ok."""
        a = z3.BitVec("a", 64)
        b = z3.BitVec("b", 64)
        dok, _dtrap, r_src = cls.build_bv64_formula(src_kind, a, b)
        r_poly = polyfill_expr_fn(a, b)
        s = z3.Solver()
        s.add(z3.And(dok, r_src != r_poly))
        res = s.check()
        return {"verified": (res == z3.unsat), "z3_status": str(res)}
