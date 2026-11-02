"""ledger_gpu_lowerer -- Cycle-2 URLedger If-Conversion & Branchless SIMT GPU Lowerer."""
from __future__ import annotations

import copy
from typing import Any

from pseudocoup.ledgerer.ur_ledger import (
    RISCV64_HOLDER_LAYOUT,
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


def _select(lang: str, cond: Any, t_val: Any, e_val: Any) -> URHiOpCall:
    c0 = URConst(0, "i64")
    mask = _op(lang, "-", c0, cond)
    return _op(lang, "^", e_val, _op(lang, "&", _op(lang, "^", t_val, e_val), mask))


class GPULedgerLowerer:
    """Converts a URLedger into a branch-free GPU URLedger and emits SIMT kernels."""

    @classmethod
    def lower_expr_branchless(cls, expr: Any, lang: str = "c") -> Any:
        """Directly lower any URLedger expression to Z3-proved branchless ALU ops."""
        if isinstance(expr, (URConst, URVar)):
            return expr
        if isinstance(expr, URHolderCast):
            inner = cls.lower_expr_branchless(expr.expr, lang)
            if expr.src_holder == expr.dst_holder or expr.dst_holder in ("i64", "u64"):
                return inner
            sz, _, signed = RISCV64_HOLDER_LAYOUT.get(expr.dst_holder, (8, 8, True))
            bits = sz * 8
            masked = _op(lang, "&", inner, URConst((1 << bits) - 1, expr.dst_holder), holder=expr.dst_holder)
            if not signed:
                return masked
            sb = URConst(1 << (bits - 1), expr.dst_holder)
            return _op(lang, "-", _op(lang, "^", masked, sb, holder=expr.dst_holder), sb, holder=expr.dst_holder)
        if isinstance(expr, URCall):
            return URCall(expr.func_name, [cls.lower_expr_branchless(a, lang) for a in expr.args], expr.holder)
        if not isinstance(expr, URHiOpCall):
            return expr

        args = [cls.lower_expr_branchless(a, lang) for a in expr.args]
        op = expr.op_symbol
        meaning = expr.ur_node.meaning
        r_val = meaning.get("R_val", "")
        c0, c1, c63, c64 = URConst(0, "i64"), URConst(1, "i64"), URConst(63, "i64"), URConst(64, "i64")
        c_min, c_neg1 = URConst(-9223372036854775808, "i64"), URConst(-1, "i64")

        if op == "&&":
            return _op(lang, "&", args[0], args[1])
        if op == "||":
            return _op(lang, "|", args[0], args[1])
        if op == "ite":
            return _select(lang, args[0], args[1], args[2])

        if len(args) == 2:
            a, b = args[0], args[1]
            ovf = _op(lang, "&", _op(lang, "==", a, c_min), _op(lang, "==", b, c_neg1))
            safe_b = _op(lang, "+", b, _op(lang, "<<", ovf, c1))
            if r_val == "saturate_64_<<":
                in_rng = _op(lang, "&", _op(lang, ">=", b, c0), _op(lang, "<", b, c64))
                return _op(lang, "&", _op(lang, "<<", a, _op(lang, "&", b, c63)), _op(lang, "-", c0, in_rng))
            if r_val == "saturate_64_>>":
                out_rng = _op(lang, "|", _op(lang, "<", b, c0), _op(lang, ">=", b, c64))
                sh_amt = _op(lang, "|", _op(lang, "&", b, c63), _op(lang, "&", _op(lang, "-", c0, out_rng), c63))
                return _op(lang, ">>", a, sh_amt)
            if r_val in ("mask_63_<<", "mask_63_>>"):
                return _op(lang, op, a, _op(lang, "&", b, c63))
            if r_val == "trunc_div" or op == "trunc_div":
                return _op(lang, "trunc_div", a, safe_b)
            if r_val == "trunc_rem" or op == "trunc_rem":
                return _op(lang, "trunc_rem", a, safe_b)
            if r_val == "floor_div":
                q = _op(lang, "trunc_div", a, safe_b)
                r = _op(lang, "trunc_rem", a, safe_b)
                adj = _op(lang, "&", _op(lang, "<", _op(lang, "^", a, b), c0), _op(lang, "!=", r, c0))
                return _op(lang, "-", q, adj)
            if r_val == "floor_mod":
                r = _op(lang, "trunc_rem", a, safe_b)
                adj = _op(lang, "&", _op(lang, "<", _op(lang, "^", a, b), c0), _op(lang, "!=", r, c0))
                return _op(lang, "+", r, _op(lang, "&", b, _op(lang, "-", c0, adj)))
        return _op(lang, op, *args, holder=expr.holder)
