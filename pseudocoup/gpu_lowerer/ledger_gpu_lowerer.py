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

    @classmethod
    def _extract_branch_assigns(cls, stmts: list[Any], lang: str, cur_vals: dict[str, Any]) -> dict[str, Any]:
        env = dict(cur_vals)
        for s in stmts:
            if isinstance(s, URAssign):
                env[s.target] = cls.lower_expr_branchless(s.expr, lang)
            elif isinstance(s, URIf):
                c = cls.lower_expr_branchless(s.cond, lang)
                t_env = cls._extract_branch_assigns(s.then_body, lang, env)
                e_env = cls._extract_branch_assigns(s.else_body, lang, env)
                for k in set(t_env) | set(e_env):
                    tv = t_env.get(k, URVar(k, "i64"))
                    ev = e_env.get(k, URVar(k, "i64"))
                    if tv is not ev:
                        env[k] = _select(lang, c, tv, ev)
        return env

    @classmethod
    def _if_convert_stmts(cls, stmts: list[Any], lang: str) -> list[Any]:
        out: list[Any] = []
        early_returns: list[tuple[Any, Any]] = []
        declared: set[str] = set()

        for s in stmts:
            if isinstance(s, URAssign):
                declared.add(s.target)
                out.append(URAssign(s.target, s.holder, cls.lower_expr_branchless(s.expr, lang), s.is_decl))
            elif isinstance(s, URWhile):
                out.append(URWhile(
                    cls.lower_expr_branchless(s.cond, lang),
                    cls._if_convert_stmts(s.body, lang),
                ))
            elif isinstance(s, URIf):
                c = cls.lower_expr_branchless(s.cond, lang)
                if len(s.then_body) == 1 and isinstance(s.then_body[0], URReturn) and not s.else_body:
                    early_returns.append((c, cls.lower_expr_branchless(s.then_body[0].expr, lang)))
                else:
                    t_env = cls._extract_branch_assigns(s.then_body, lang, {})
                    e_env = cls._extract_branch_assigns(s.else_body, lang, {})
                    for k in sorted(set(t_env) | set(e_env)):
                        tv = t_env.get(k, URVar(k, "i64"))
                        ev = e_env.get(k, URVar(k, "i64"))
                        merged = _select(lang, c, tv, ev)
                        is_decl = k not in declared
                        declared.add(k)
                        out.append(URAssign(k, "i64", merged, is_decl))
            elif isinstance(s, URReturn):
                ret_e = cls.lower_expr_branchless(s.expr, lang)
                for cond_e, early_e in reversed(early_returns):
                    ret_e = _select(lang, cond_e, early_e, ret_e)
                out.append(URReturn(ret_e))
        return out

    @classmethod
    def lower_ledger_to_gpu(cls, ledger: URLedger, lang: str = "c") -> URLedger:
        """Return a new URLedger with 0 URIf statements and 0 `ite` / Tier-2 branch ops."""
        gpu_funcs: list[URFunc] = []
        for fn in ledger.functions:
            new_body = cls._if_convert_stmts(fn.body, lang)
            gpu_funcs.append(URFunc(
                fn.func_name,
                fn.source_lang,
                copy.deepcopy(fn.params),
                copy.deepcopy(fn.locals),
                fn.return_holder,
                new_body,
            ))
        main_fn = gpu_funcs[-1]
        return URLedger(
            func_name=main_fn.func_name,
            source_lang=lang,
            params=main_fn.params,
            locals=main_fn.locals,
            return_holder=main_fn.return_holder,
            body=main_fn.body,
            functions=gpu_funcs,
            bridge_events=list(ledger.bridge_events),
        )

    @classmethod
    def emit_branchless_python(cls, ledger: URLedger) -> str:
        gpu_l = cls.lower_ledger_to_gpu(ledger, "python")
        return LedgerToScript.emit(gpu_l, "python")

    @classmethod
    def emit_simd_c(cls, ledger: URLedger) -> str:
        gpu_l = cls.lower_ledger_to_gpu(ledger, "c")
        return LedgerToScript.emit(gpu_l, "c")

    @classmethod
    def emit_cuda_kernel(cls, ledger: URLedger) -> str:
        gpu_l = cls.lower_ledger_to_gpu(ledger, "c")
        c_funcs = []
        for fn in gpu_l.functions:
            c_funcs.append("__device__ __forceinline__ " + LedgerToScript.emit_func(fn, "c"))
        main_fn = gpu_l.functions[-1]
        p_names = [p.name for p in main_fn.params]
        in_params = ", ".join(f"const int64_t* __restrict__ in_{n}" for n in p_names)
        call_args = ", ".join(f"in_{n}[tid]" for n in p_names)
        kernel = (
            f"extern \"C\" __global__ void {main_fn.func_name}_warp_kernel(\n"
            f"    {in_params},\n"
            f"    int64_t* __restrict__ out_res,\n"
            f"    int32_t n_elements\n"
            f") {{\n"
            f"    int32_t tid = (int32_t)(blockIdx.x * blockDim.x + threadIdx.x);\n"
            f"    if (tid < n_elements) {{\n"
            f"        out_res[tid] = {main_fn.func_name}({call_args});\n"
            f"    }}\n"
            f"}}"
        )
        return "#include <stdint.h>\n\n" + "\n\n".join(c_funcs) + "\n\n" + kernel + "\n"

    @classmethod
    def emit_wgsl_shader(cls, ledger: URLedger) -> str:
        gpu_l = cls.lower_ledger_to_gpu(ledger, "rust")
        rs_code = LedgerToScript.emit(gpu_l, "rust")
        wgsl_funcs = rs_code.replace("let mut ", "var ")
        main_fn = gpu_l.functions[-1]
        p_names = [p.name for p in main_fn.params]
        call_args = ", ".join(f"in_buf[tid * {len(p_names)}u + {i}u]" for i in range(len(p_names)))
        header = (
            "// WebGPU (WGSL) Branchless SIMT Compute Shader generated by PseudoCoup GPULedgerLowerer\n"
            "@group(0) @binding(0) var<storage, read> in_buf: array<i64>;\n"
            "@group(0) @binding(1) var<storage, read_write> out_buf: array<i64>;\n\n"
        )
        entry = (
            f"\n\n@compute @workgroup_size(64)\n"
            f"fn main(@builtin(global_invocation_id) gid: vec3<u32>) {{\n"
            f"    let tid: u32 = gid.x;\n"
            f"    out_buf[tid] = {main_fn.func_name}({call_args});\n"
            f"}}\n"
        )
        return header + wgsl_funcs + entry
