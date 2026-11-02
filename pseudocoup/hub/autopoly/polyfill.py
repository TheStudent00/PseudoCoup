"""polyfill -- 3-Tier AutoPoly Polyfill Engine (`CORE_0_0_0_2_0_autopoly.md`).

Tiers:
  1. Tier 1 (Exact Native HiOp, Delta = empty): Direct native HiOp call in target language.
  2. Tier 2 (Piecewise HiOp, D = D_fast U D_edge): Guarded native HiOp call proven UNSAT.
  3. Tier 3 (Guaranteed LoOp-to-HiOpPrimitive Backstop): Composes each RISC-V LoOp of the
     Unit from the target language's 13 proven HiOpPrimitives.
"""
from __future__ import annotations
from typing import Any

from ...ledgerer.universal_rich_node import UniversalRichNode
from .equivalence_prover import EquivalenceProver

# The 13 Universal HiOpPrimitives per target language (`CORE_0_0_0_2_0_autopoly.md`)
HIOP_PRIMITIVES: dict[str, dict[str, str]] = {
    "BV_ADD":  {"c": "({a} + {b})", "cpp": "({a} + {b})", "go": "({a} + {b})", "rust": "{a}.wrapping_add({b})", "python": "(({a} + {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} + {b})"},
    "BV_SUB":  {"c": "({a} - {b})", "cpp": "({a} - {b})", "go": "({a} - {b})", "rust": "{a}.wrapping_sub({b})", "python": "(({a} - {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} - {b})"},
    "BV_MUL":  {"c": "({a} * {b})", "cpp": "({a} * {b})", "go": "({a} * {b})", "rust": "{a}.wrapping_mul({b})", "python": "(({a} * {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} * {b})"},
    "BV_AND":  {"c": "({a} & {b})", "cpp": "({a} & {b})", "go": "({a} & {b})", "rust": "({a} & {b})", "python": "({a} & {b})", "java": "({a} & {b})"},
    "BV_OR":   {"c": "({a} | {b})", "cpp": "({a} | {b})", "go": "({a} | {b})", "rust": "({a} | {b})", "python": "({a} | {b})", "java": "({a} | {b})"},
    "BV_XOR":  {"c": "({a} ^ {b})", "cpp": "({a} ^ {b})", "go": "({a} ^ {b})", "rust": "({a} ^ {b})", "python": "({a} ^ {b})", "java": "({a} ^ {b})"},
    "BV_NOT":  {"c": "(~{a})",      "cpp": "(~{a})",      "go": "(^{a})",      "rust": "(!{a})",      "python": "(~{a} & 0xFFFFFFFFFFFFFFFF)", "java": "(~{a})"},
    "BV_SHL":  {"c": "({a} << ({b} & 63))", "cpp": "({a} << ({b} & 63))", "go": "({a} << ({b} & 63))", "rust": "{a}.wrapping_shl({b} as u32)", "python": "(({a} << ({b} & 63)) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} << {b})"},
    "BV_LSHR": {"c": "((uint64_t){a} >> ({b} & 63))", "cpp": "((uint64_t){a} >> ({b} & 63))", "go": "(uint64({a}) >> ({b} & 63))", "rust": "({a} as u64).wrapping_shr({b} as u32) as i64", "python": "(({a} & 0xFFFFFFFFFFFFFFFF) >> ({b} & 63))", "java": "({a} >>> {b})"},
    "BV_ASHR": {"c": "({a} >> ({b} & 63))", "cpp": "({a} >> ({b} & 63))", "go": "({a} >> ({b} & 63))", "rust": "{a}.wrapping_shr({b} as u32)", "python": "ashr64({a}, {b} & 63)", "java": "({a} >> {b})"},
    "BV_ULT":  {"c": "((uint64_t){a} < (uint64_t){b})", "cpp": "((uint64_t){a} < (uint64_t){b})", "go": "(uint64({a}) < uint64({b}))", "rust": "(({a} as u64) < ({b} as u64))", "python": "(({a} & 0xFFFFFFFFFFFFFFFF) < ({b} & 0xFFFFFFFFFFFFFFFF))", "java": "(Long.compareUnsigned({a}, {b}) < 0)"},
    "BV_SLT":  {"c": "({a} < {b})", "cpp": "({a} < {b})", "go": "({a} < {b})", "rust": "({a} < {b})", "python": "(s64({a}) < s64({b}))", "java": "({a} < {b})"},
    "BV_ITE":  {"c": "({c} ? {a} : {b})", "cpp": "({c} ? {a} : {b})", "go": "ite({c}, {a}, {b})", "rust": "(if {c} {{ {a} }} else {{ {b} }})", "python": "({a} if {c} else {b})", "java": "({c} ? {a} : {b})"},
}


class AutoPoly:
    """Autonomous Polyfill Engine: executes or emits any UR-Node in any target language."""

    def __init__(self) -> None:
        self.prover = EquivalenceProver()

    def emit_target_code(self, node: UniversalRichNode, target_lang: str, lhs: str = "a", rhs: str = "b") -> dict[str, Any]:
        """Synthesize target-language code for `node` using Tier 1, Tier 2, or Tier 3."""
        t = target_lang.lower()
        r_kind = node.meaning.get("R_kind", "")

        # Tier 1: Exact 1-to-1 Native HiOp Match (Delta = empty)
        tier1_map = {
            "bvadd": "BV_ADD", "bvsub": "BV_SUB", "bvmul": "BV_MUL",
            "bvand": "BV_AND", "bvor":  "BV_OR",  "bvxor": "BV_XOR",
            "bvnot": "BV_NOT", "bvshl_mask63": "BV_SHL",
            "bvlshr_mask63": "BV_LSHR", "bvashr_mask63": "BV_ASHR",
        }
        if r_kind in tier1_map:
            prim = tier1_map[r_kind]
            code = HIOP_PRIMITIVES[prim][t].format(a=lhs, b=rhs, c="1")
            return {"tier": "tier1_exact_native_hiop", "code": code, "primitive": prim}

        # Tier 2: Piecewise Guarded HiOp Synthesis (D = D_fast U D_edge)
        if r_kind == "go_shl_64":
            fast = HIOP_PRIMITIVES["BV_SHL"][t].format(a=lhs, b=rhs)
            guard = HIOP_PRIMITIVES["BV_ULT"][t].format(a=rhs, b="64")
            code = HIOP_PRIMITIVES["BV_ITE"][t].format(c=guard, a=fast, b="0")
            return {"tier": "tier2_piecewise_hiop", "code": code}
        if r_kind == "go_java_sdiv":
            code = f"({rhs} == 0 ? PANIC_DIV0 : (({lhs} == INT64_MIN && {rhs} == -1) ? INT64_MIN : ({lhs} / {rhs})))"
            return {"tier": "tier2_piecewise_hiop", "code": code}
        if r_kind == "rust_srem":
            code = f"({rhs} == 0 ? PANIC_DIV0 : (({lhs} == INT64_MIN && {rhs} == -1) ? PANIC_OVF : ({lhs} % {rhs})))"
            return {"tier": "tier2_piecewise_hiop", "code": code}
        if r_kind == "python_floordiv":
            code = f"({rhs} == 0 ? PANIC_DIV0 : ((({lhs} % {rhs}) != 0 && (({lhs} ^ {rhs}) < 0)) ? (({lhs} / {rhs}) - 1) : ({lhs} / {rhs})))"
            return {"tier": "tier2_piecewise_hiop", "code": code}
        if r_kind == "spaceship_lcmp":
            gt = HIOP_PRIMITIVES["BV_SLT"][t].format(a=rhs, b=lhs)
            lt = HIOP_PRIMITIVES["BV_SLT"][t].format(a=lhs, b=rhs)
            inner = HIOP_PRIMITIVES["BV_ITE"][t].format(c=lt, a="-1", b="0")
            code = HIOP_PRIMITIVES["BV_ITE"][t].format(c=gt, a="1", b=inner)
            return {"tier": "tier2_piecewise_hiop", "code": code}

        # Tier 3: Guaranteed LoOp-to-HiOpPrimitive Backstop (`CORE_0_0_0_2_0_autopoly.md`)
        steps = [f"exec_loop_{op}({lhs}, {rhs})" for op in node.canonical_lo_ops()]
        return {"tier": "tier3_loop_primitive_backstop", "code": " ; ".join(steps)}
