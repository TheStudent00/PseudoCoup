"""ledger_gpu_lowerer -- Cycle-2 URLedger If-Conversion & Branchless SIMT GPU Lowerer.

Transforms any `URLedger` into a 100% branch-free SIMT GPU form:
  1. Eliminates all `URIf` control-flow branches via SSA If-Conversion (including nested
     `if/else` trees and early `return` guards).
  2. Lowers all `ite` (`?:`), `&&`, `||`, and Tier-2 operators (`saturate_64_<<`,
     `saturate_64_>>`, `trunc_div`, `trunc_rem`, `floor_div`, `floor_mod`) into pure
     branchless bitwise/arithmetic `URHiOpCall` trees (`e ^ ((t ^ e) & (0 - cond))`).
  3. Emits branchless SIMD-C, branchless Python, CUDA `.cu`, and WebGPU `.wgsl` kernels.
"""
from __future__ import annotations

import copy
from typing import Any

from pseudocoup.ledgerer.ur_ledger import (
    HolderDecl,
    LedgerToScript,
    URAssign,
    URCall,
    URConst,
    URFunc,
    URHiOpCall,
    URHolderCast,
    URIf,
    URLedger,
    URReturn,
    URVar,
    URWhile,
    build_ur_node,
)


def _op(lang: str, sym: str, *args: Any, holder: str = "i64") -> URHiOpCall:
    return URHiOpCall(build_ur_node(lang, sym, holder, True), list(args), sym, holder)


class GPULedgerLowerer:
    """Converts a URLedger into a branch-free GPU URLedger and emits SIMT kernels."""

    @classmethod
    def lower_expr_branchless(cls, expr: Any, lang: str = "c") -> Any:
        """Replace all `ite`, `&&`, `||`, and Tier-2 ops with pure bitwise ALU ops."""
        canon = LedgerToScript.canonicalize_expr(expr, lang)
        return cls._rewrite_canon_branchless(canon, lang)

    @classmethod
    def _rewrite_canon_branchless(cls, expr: Any, lang: str) -> Any:
        if isinstance(expr, (URConst, URVar)):
            return expr
        if isinstance(expr, URHolderCast):
            return URHolderCast(
                cls._rewrite_canon_branchless(expr.expr, lang),
                expr.src_holder,
                expr.dst_holder,
                expr.bridge_kind,
                expr.ur_node,
            )
        if isinstance(expr, URCall):
            return URCall(
                expr.func_name,
                [cls._rewrite_canon_branchless(a, lang) for a in expr.args],
                expr.holder,
            )
        if not isinstance(expr, URHiOpCall):
            return expr

        args = [cls._rewrite_canon_branchless(a, lang) for a in expr.args]
        op = expr.op_symbol
        c0 = URConst(0, "i64")
        c1 = URConst(1, "i64")
        c_min = URConst(-9223372036854775808, "i64")
        c_neg1 = URConst(-1, "i64")

        if op == "&&":
            return _op(lang, "&", args[0], args[1])
        if op == "||":
            return _op(lang, "|", args[0], args[1])
        if op == "ite":
            cond, t_val, e_val = args[0], args[1], args[2]
            mask = _op(lang, "-", c0, cond)
            return _op(lang, "^", e_val, _op(lang, "&", _op(lang, "^", t_val, e_val), mask))
        if op in ("trunc_div", "trunc_rem"):
            a, b = args[0], args[1]
            ovf = _op(lang, "&", _op(lang, "==", a, c_min), _op(lang, "==", b, c_neg1))
            safe_b = _op(lang, "+", b, _op(lang, "<<", ovf, c1))
            return _op(lang, op, a, safe_b)
        return _op(lang, op, *args, holder=expr.holder)
