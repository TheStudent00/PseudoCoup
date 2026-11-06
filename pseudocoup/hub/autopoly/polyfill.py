"""polyfill -- 3-Tier AutoPoly Polyfill Engine (`CORE_0_0_0_2_0_autopoly.md`).

Tiers:
  1. Tier 1 (Exact Native HiOp, Delta = empty): Direct native HiOp call in target language,
     proven equivalent (`UNSAT`) via Sail-derived `UnitLean`.
  2. Tier 2 (Piecewise HiOp, D = D_agree U D_residual): Guarded native HiOp call synthesized
     directly from the Sail-derived Domain-Range partition `(D_k, R_k)`.
  3. Tier 3 (Guaranteed LoOp-to-HiOpPrimitive Backstop): Translates the Sail-derived Z3/Lean
     AST of the Unit's LoOps directly into the target language's proven `HIOP_PRIMITIVES`.
"""
from __future__ import annotations
from typing import Any, Sequence
import z3

from ...ledgerer.universal_rich_node import UniversalRichNode
from .equivalence_prover import EquivalenceProver, canonicalize_unit_lean

_LANG_ALIASES: dict[str, str] = {
    "c": "c",
    "gnu_c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "go": "go",
    "rust": "rust",
    "python": "python",
    "java": "java",
    "typescript": "typescript",
    "ts": "typescript",
    "javascript": "typescript",
    "csharp": "csharp",
    "c#": "csharp",
    "cs": "csharp",
    "ruby": "ruby",
    "rb": "ruby",
    "php": "php",
    "dart": "dart",
    "swift": "swift",
}


def normalize_target_lang(target_lang: str) -> str:
    key = target_lang.strip().lower()
    if key not in _LANG_ALIASES:
        raise ValueError(f"Unsupported target language {target_lang!r}")
    return _LANG_ALIASES[key]


HIOP_PRIMITIVES: dict[str, dict[str, str]] = {
    "BV_ADD": {
        "c": "({a} + {b})", "cpp": "({a} + {b})", "go": "({a} + {b})", "rust": "({a}).wrapping_add({b})",
        "python": "(({a} + {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} + {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) + BigInt({b}))", "csharp": "unchecked({a} + {b})",
        "ruby": "(({a} + {b}) & 0xFFFFFFFFFFFFFFFF)", "php": "({a} + {b})",
        "dart": "({a} + {b})", "swift": "({a} &+ {b})",
    },
    "BV_SUB": {
        "c": "({a} - {b})", "cpp": "({a} - {b})", "go": "({a} - {b})", "rust": "({a}).wrapping_sub({b})",
        "python": "(({a} - {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} - {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) - BigInt({b}))", "csharp": "unchecked({a} - {b})",
        "ruby": "(({a} - {b}) & 0xFFFFFFFFFFFFFFFF)", "php": "({a} - {b})",
        "dart": "({a} - {b})", "swift": "({a} &- {b})",
    },
    "BV_MUL": {
        "c": "({a} * {b})", "cpp": "({a} * {b})", "go": "({a} * {b})", "rust": "({a}).wrapping_mul({b})",
        "python": "(({a} * {b}) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} * {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) * BigInt({b}))", "csharp": "unchecked({a} * {b})",
        "ruby": "(({a} * {b}) & 0xFFFFFFFFFFFFFFFF)", "php": "({a} * {b})",
        "dart": "({a} * {b})", "swift": "({a} &* {b})",
    },
    "BV_AND": {
        "c": "({a} & {b})", "cpp": "({a} & {b})", "go": "({a} & {b})", "rust": "({a} & {b})",
        "python": "({a} & {b})", "java": "({a} & {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) & BigInt({b}))", "csharp": "({a} & {b})",
        "ruby": "({a} & {b})", "php": "({a} & {b})",
        "dart": "({a} & {b})", "swift": "({a} & {b})",
    },
    "BV_OR": {
        "c": "({a} | {b})", "cpp": "({a} | {b})", "go": "({a} | {b})", "rust": "({a} | {b})",
        "python": "({a} | {b})", "java": "({a} | {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) | BigInt({b}))", "csharp": "({a} | {b})",
        "ruby": "({a} | {b})", "php": "({a} | {b})",
        "dart": "({a} | {b})", "swift": "({a} | {b})",
    },
    "BV_XOR": {
        "c": "({a} ^ {b})", "cpp": "({a} ^ {b})", "go": "({a} ^ {b})", "rust": "({a} ^ {b})",
        "python": "({a} ^ {b})", "java": "({a} ^ {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) ^ BigInt({b}))", "csharp": "({a} ^ {b})",
        "ruby": "({a} ^ {b})", "php": "({a} ^ {b})",
        "dart": "({a} ^ {b})", "swift": "({a} ^ {b})",
    },
    "BV_NOT": {
        "c": "(~{a})", "cpp": "(~{a})", "go": "(^{a})", "rust": "(!({a}))",
        "python": "(~{a} & 0xFFFFFFFFFFFFFFFF)", "java": "(~{a})",
        "typescript": "BigInt.asIntN(64, ~BigInt({a}))", "csharp": "(~{a})",
        "ruby": "(~{a} & 0xFFFFFFFFFFFFFFFF)", "php": "(~{a})",
        "dart": "(~{a})", "swift": "(~{a})",
    },
    "BV_SHL": {
        "c": "({a} << ({b} & 63))", "cpp": "({a} << ({b} & 63))", "go": "({a} << ({b} & 63))", "rust": "({a}).wrapping_shl({b} as u32)",
        "python": "(({a} << ({b} & 63)) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} << {b})",
        "typescript": "BigInt.asIntN(64, BigInt({a}) << (BigInt({b}) & 63n))", "csharp": "({a} << (int)({b} & 63))",
        "ruby": "(({a} << ({b} & 63)) & 0xFFFFFFFFFFFFFFFF)", "php": "({a} << ({b} & 63))",
        "dart": "({a} << ({b} & 63))", "swift": "({a} << ({b} & 63))",
    },
    "BV_LSHR": {
        "c": "((uint64_t){a} >> ({b} & 63))", "cpp": "((uint64_t){a} >> ({b} & 63))", "go": "(uint64({a}) >> ({b} & 63))", "rust": "((({a}) as u64).wrapping_shr({b} as u32) as i64)",
        "python": "(({a} & 0xFFFFFFFFFFFFFFFF) >> ({b} & 63))", "java": "({a} >>> {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asUintN(64, BigInt({a})) >> (BigInt({b}) & 63n))",
        "csharp": "unchecked((long)((ulong)({a}) >> (int)({b} & 63)))",
        "ruby": "(({a} & 0xFFFFFFFFFFFFFFFF) >> ({b} & 63))",
        "php": "(({b} & 63) === 0 ? {a} : (({a} >> ({b} & 63)) & ~(PHP_INT_MIN >> ((({b} & 63) - 1)))))",
        "dart": "({a} >>> ({b} & 63))",
        "swift": "Int64(bitPattern: UInt64(bitPattern: {a}) >> UInt64(bitPattern: {b} & 63))",
    },
    "BV_ASHR": {
        "c": "({a} >> ({b} & 63))", "cpp": "({a} >> ({b} & 63))", "go": "({a} >> ({b} & 63))", "rust": "({a}).wrapping_shr({b} as u32)",
        "python": "((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) >> ({b} & 63)) & 0xFFFFFFFFFFFFFFFF)", "java": "({a} >> {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asIntN(64, BigInt({a})) >> (BigInt({b}) & 63n))",
        "csharp": "({a} >> (int)({b} & 63))",
        "ruby": "((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) >> ({b} & 63)) & 0xFFFFFFFFFFFFFFFF)",
        "php": "({a} >> ({b} & 63))",
        "dart": "({a} >> ({b} & 63))",
        "swift": "({a} >> ({b} & 63))",
    },
    "BV_ULT": {
        "c": "((uint64_t){a} < (uint64_t){b})", "cpp": "((uint64_t){a} < (uint64_t){b})", "go": "(uint64({a}) < uint64({b}))", "rust": "((({a}) as u64) < (({b}) as u64))",
        "python": "(({a} & 0xFFFFFFFFFFFFFFFF) < ({b} & 0xFFFFFFFFFFFFFFFF))", "java": "(Long.compareUnsigned({a}, {b}) < 0)",
        "typescript": "(BigInt.asUintN(64, BigInt({a})) < BigInt.asUintN(64, BigInt({b})))",
        "csharp": "((ulong)({a}) < (ulong)({b}))",
        "ruby": "(({a} & 0xFFFFFFFFFFFFFFFF) < ({b} & 0xFFFFFFFFFFFFFFFF))",
        "php": "((({a} ^ PHP_INT_MIN) < ({b} ^ PHP_INT_MIN)))",
        "dart": "((({a} ^ 0x8000000000000000) < ({b} ^ 0x8000000000000000)))",
        "swift": "(UInt64(bitPattern: {a}) < UInt64(bitPattern: {b}))",
    },
    "BV_SLT": {
        "c": "({a} < {b})", "cpp": "({a} < {b})", "go": "({a} < {b})", "rust": "({a} < {b})",
        "python": "(((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < ((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000))", "java": "({a} < {b})",
        "typescript": "(BigInt.asIntN(64, BigInt({a})) < BigInt.asIntN(64, BigInt({b})))",
        "csharp": "({a} < {b})",
        "ruby": "(((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < ((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000))",
        "php": "({a} < {b})",
        "dart": "({a} < {b})",
        "swift": "({a} < {b})",
    },
    "BV_SDIV": {
        "c": "((((uint64_t)({a})) == 0x8000000000000000ULL && ({b}) == -1) ? ({a}) : (({a}) / ({b})))",
        "cpp": "((((uint64_t)({a})) == 0x8000000000000000ULL && ({b}) == -1) ? ({a}) : (({a}) / ({b})))",
        "go": "({a} / {b})", "rust": "({a}).wrapping_div({b})",
        "python": "((((abs(((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000)) // abs(((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000))) * (-1 if ((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0) ^ (((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0)) else 1)) & 0xFFFFFFFFFFFFFFFF))",
        "java": "({a} / {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asIntN(64, BigInt({a})) / BigInt.asIntN(64, BigInt({b})))",
        "csharp": "(((ulong)({a}) == 0x8000000000000000UL && ({b}) == -1L) ? ({a}) : (({a}) / ({b})))",
        "ruby": "((((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000).abs / ((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000).abs) * (((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0) ^ (((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0)) ? -1 : 1)) & 0xFFFFFFFFFFFFFFFF))",
        "php": "(({a} === PHP_INT_MIN && {b} === -1) ? PHP_INT_MIN : intdiv({a}, {b}))",
        "dart": "(({a} == -0x8000000000000000 && {b} == -1) ? {a} : ({a} ~/ {b}))",
        "swift": "(({a} == Int64.min && {b} == -1) ? Int64.min : ({a} / {b}))",
    },
    "BV_UDIV": {
        "c": "((int64_t)((uint64_t)({a}) / (uint64_t)({b})))",
        "cpp": "((int64_t)((uint64_t)({a}) / (uint64_t)({b})))",
        "go": "int64(uint64({a}) / uint64({b}))", "rust": "((({a}) as u64).wrapping_div(({b}) as u64) as i64)",
        "python": "(({a} & 0xFFFFFFFFFFFFFFFF) // ({b} & 0xFFFFFFFFFFFFFFFF))", "java": "Long.divideUnsigned({a}, {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asUintN(64, BigInt({a})) / BigInt.asUintN(64, BigInt({b})))",
        "csharp": "unchecked((long)((ulong)({a}) / (ulong)({b})))",
        "ruby": "(({a} & 0xFFFFFFFFFFFFFFFF) / ({b} & 0xFFFFFFFFFFFFFFFF))",
        "php": "(({b} < 0) ? ((({a} ^ PHP_INT_MIN) < ({b} ^ PHP_INT_MIN)) ? 0 : 1) : (($__q = (intdiv((({a} >> 1) & PHP_INT_MAX), {b}) << 1)) + (((({a} - $__q * {b}) ^ PHP_INT_MIN) < ({b} ^ PHP_INT_MIN)) ? 0 : 1)))",
        "dart": "(({b} < 0) ? ((({a} ^ 0x8000000000000000) < ({b} ^ 0x8000000000000000)) ? 0 : 1) : ((((({a} >>> 1) ~/ {b}) << 1) + (((({a} - (((({a} >>> 1) ~/ {b}) << 1) * {b})) ^ 0x8000000000000000) < ({b} ^ 0x8000000000000000)) ? 0 : 1))))",
        "swift": "Int64(bitPattern: UInt64(bitPattern: {a}) / UInt64(bitPattern: {b}))",
    },
    "BV_SREM": {
        "c": "((((uint64_t)({a})) == 0x8000000000000000ULL && ({b}) == -1) ? 0 : (({a}) % ({b})))",
        "cpp": "((((uint64_t)({a})) == 0x8000000000000000ULL && ({b}) == -1) ? 0 : (({a}) % ({b})))",
        "go": "({a} % {b})", "rust": "({a}).wrapping_rem({b})",
        "python": "((((abs(((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000)) % abs(((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000))) * (-1 if (((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0) else 1)) & 0xFFFFFFFFFFFFFFFF))",
        "java": "({a} % {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asIntN(64, BigInt({a})) % BigInt.asIntN(64, BigInt({b})))",
        "csharp": "(((ulong)({a}) == 0x8000000000000000UL && ({b}) == -1L) ? 0L : (({a}) % ({b})))",
        "ruby": "((((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000).abs % ((({b} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000).abs) * ((((({a} + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000) < 0 ? -1 : 1)) & 0xFFFFFFFFFFFFFFFF))",
        "php": "(({a} === PHP_INT_MIN && {b} === -1) ? 0 : ({a} % {b}))",
        "dart": "(({a} == -0x8000000000000000 && {b} == -1) ? 0 : ({a}.remainder({b})))",
        "swift": "(({a} == Int64.min && {b} == -1) ? 0 : ({a} % {b}))",
    },
    "BV_UREM": {
        "c": "((int64_t)((uint64_t)({a}) % (uint64_t)({b})))",
        "cpp": "((int64_t)((uint64_t)({a}) % (uint64_t)({b})))",
        "go": "int64(uint64({a}) % uint64({b}))", "rust": "((({a}) as u64).wrapping_rem(({b}) as u64) as i64)",
        "python": "(({a} & 0xFFFFFFFFFFFFFFFF) % ({b} & 0xFFFFFFFFFFFFFFFF))", "java": "Long.remainderUnsigned({a}, {b})",
        "typescript": "BigInt.asIntN(64, BigInt.asUintN(64, BigInt({a})) % BigInt.asUintN(64, BigInt({b})))",
        "csharp": "unchecked((long)((ulong)({a}) % (ulong)({b})))",
        "ruby": "(({a} & 0xFFFFFFFFFFFFFFFF) % ({b} & 0xFFFFFFFFFFFFFFFF))",
        "php": "(({a} - (({b} < 0) ? ((({a} ^ PHP_INT_MIN) < ({b} ^ PHP_INT_MIN)) ? 0 : 1) : ((intdiv((({a} >> 1) & PHP_INT_MAX), {b}) << 1) + (((({a} - ((intdiv((({a} >> 1) & PHP_INT_MAX), {b}) << 1) * {b})) ^ PHP_INT_MIN) < ({b} ^ PHP_INT_MIN)) ? 0 : 1))) * {b}))",
        "dart": "(({a} - (({b} < 0) ? ((({a} ^ 0x8000000000000000) < ({b} ^ 0x8000000000000000)) ? 0 : 1) : ((((({a} >>> 1) ~/ {b}) << 1) + (((({a} - (((({a} >>> 1) ~/ {b}) << 1) * {b})) ^ 0x8000000000000000) < ({b} ^ 0x8000000000000000)) ? 0 : 1)))) * {b}))",
        "swift": "Int64(bitPattern: UInt64(bitPattern: {a}) % UInt64(bitPattern: {b}))",
    },
    "BV_ITE": {
        "c": "({c} ? {a} : {b})", "cpp": "({c} ? {a} : {b})", "go": "ite({c}, {a}, {b})", "rust": "(if {c} {{ {a} }} else {{ {b} }})",
        "python": "({a} if {c} else {b})", "java": "({c} ? {a} : {b})",
        "typescript": "({c} ? {a} : {b})", "csharp": "({c} ? {a} : {b})",
        "ruby": "({c} ? {a} : {b})", "php": "({c} ? {a} : {b})",
        "dart": "({c} ? {a} : {b})", "swift": "({c} ? {a} : {b})",
    },
}

RISCV64_ORDERING_PER_TARGET_LANGUAGE: dict[str, dict[str, str]] = {
    "c": {
        "shared_load_store": "atomic_load_explicit(acquire), atomic_store_explicit(release)",
        "fence": "atomic_thread_fence(memory_order_seq_cst)",
        "amo": "atomic_fetch_add_explicit / atomic_fetch_op_explicit",
        "lr_sc": "atomic_compare_exchange_strong_explicit",
    },
    "cpp": {
        "shared_load_store": "std::atomic_ref::load(acquire), store(release)",
        "fence": "std::atomic_thread_fence(std::memory_order_seq_cst)",
        "amo": "std::atomic_ref::fetch_add / fetch_op",
        "lr_sc": "std::atomic_ref::compare_exchange_strong",
    },
    "csharp": {
        "shared_load_store": "Volatile.Read, Volatile.Write",
        "fence": "Interlocked.MemoryBarrier()",
        "amo": "Interlocked.Add / Exchange / And / Or / CompareExchange",
        "lr_sc": "Interlocked.CompareExchange",
    },
    "dart": {
        "shared_load_store": "kept (isolates share no memory: one thread at a time)",
        "fence": "kept",
        "amo": "kept",
        "lr_sc": "kept",
    },
    "go": {
        "shared_load_store": "sync/atomic (sequentially consistent)",
        "fence": "kept (sync/atomic is sequentially consistent)",
        "amo": "atomic.AddInt64 / SwapInt64 / AndInt64 / OrInt64 / CompareAndSwapInt64",
        "lr_sc": "atomic.CompareAndSwapInt64",
    },
    "java": {
        "shared_load_store": "VarHandle.getAcquire, VarHandle.setRelease",
        "fence": "VarHandle.fullFence()",
        "amo": "VarHandle.getAndAdd / getAndSet / getAndBitwiseAnd / compareAndExchange",
        "lr_sc": "VarHandle.compareAndSet",
    },
    "typescript": {
        "shared_load_store": "Atomics.load, Atomics.store on SharedArrayBuffer",
        "fence": "kept (Atomics operations are sequentially consistent)",
        "amo": "Atomics.add / sub / and / or / xor / exchange / compareExchange",
        "lr_sc": "Atomics.compareExchange",
    },
    "php": {
        "shared_load_store": "kept (no threads sharing memory: one thread at a time)",
        "fence": "kept",
        "amo": "kept",
        "lr_sc": "kept",
    },
    "python": {
        "shared_load_store": "kept (one thread at a time)",
        "fence": "kept",
        "amo": "kept",
        "lr_sc": "kept",
    },
    "ruby": {
        "shared_load_store": "kept (one thread at a time under GVL; Ractors share no memory)",
        "fence": "kept",
        "amo": "kept",
        "lr_sc": "kept",
    },
    "rust": {
        "shared_load_store": "AtomicU64::load(Ordering::Acquire), store(Ordering::Release)",
        "fence": "std::sync::atomic::fence(Ordering::SeqCst)",
        "amo": "AtomicU64::fetch_add / fetch_and / fetch_or / fetch_xor / fetch_max / fetch_min / fetch_nand / swap",
        "lr_sc": "AtomicU64::compare_exchange",
    },
    "swift": {
        "shared_load_store": "Atomic.load(ordering: .acquiring), store(ordering: .releasing)",
        "fence": "atomicMemoryFence(ordering: .sequentiallyConsistent)",
        "amo": "Atomic.wrappingAdd / bitwiseAnd / bitwiseOr / bitwiseXor / exchange / compareExchange",
        "lr_sc": "Atomic.compareExchange",
    },
}


def _classify_concat_extension(expr: z3.ExprRef) -> tuple[str | None, z3.ExprRef | None]:
    """Identify whether a Z3 bitvector is a zero-extension ('zext') or sign-extension ('sext')
    of its low slice, either via ZeroExt/SignExt or via Sail's multi-slice Concat (including
    when Z3 flattens nested Concats into the suffix)."""
    k = expr.decl().kind()
    if k == z3.Z3_OP_ZERO_EXT:
        return "zext", expr.arg(0)
    if k == z3.Z3_OP_SIGN_EXT:
        return "sext", expr.arg(0)
    if k == z3.Z3_OP_CONCAT and expr.num_args() >= 2:
        n = expr.num_args()
        # 1. Check leading zero slices
        z_count = 0
        while z_count < n - 1 and z3.is_bv_value(expr.arg(z_count)) and expr.arg(z_count).as_long() == 0:
            z_count += 1
        if z_count > 0:
            rem = [expr.arg(i) for i in range(z_count, n)]
            low = rem[0] if len(rem) == 1 else z3.Concat(*rem)
            if low.size() <= 64:
                return "zext", low
        # 2. Check leading replicated 1-bit sign slices
        first = z3.simplify(expr.arg(0))
        if first.size() == 1:
            s_count = 1
            while s_count < n - 1 and z3.simplify(expr.arg(s_count)).eq(first):
                s_count += 1
            rem = [expr.arg(i) for i in range(s_count, n)]
            low = rem[0] if len(rem) == 1 else z3.Concat(*rem)
            if low.size() <= 64:
                msb_bit = z3.simplify(z3.Extract(low.size() - 1, low.size() - 1, low))
                if msb_bit.eq(first):
                    return "sext", low
                if s_count >= 8 and (low.size() + 1) <= 64:
                    return "sext", z3.Concat(first, low)
    return None, None


def translate_z3_to_hiop_primitives(
    expr: z3.ExprRef,
    target_lang: str,
    lhs: str = "a",
    rhs: str = "b",
    third: str = "c",
    fourth: str = "d",
    extra_names: Sequence[str] = (),
) -> str:
    """Recursively translate a Sail-derived Z3 bitvector/boolean/FP AST into target
    `HIOP_PRIMITIVES` across all 12 languages (`c`, `cpp`, `go`, `rust`, `python`,
    `java`, `typescript`, `csharp`, `ruby`, `php`, `dart`, `swift`)."""
    t = normalize_target_lang(target_lang)
    expr = z3.simplify(expr)
    if z3.is_true(expr):
        return "True" if t == "python" else ("1" if t == "c" else "true")
    if z3.is_false(expr):
        return "False" if t == "python" else ("0" if t == "c" else "false")
    if z3.is_bv_value(expr):
        val = expr.as_long()
        w = expr.size()
        if w in (32, 64) and val == (1 << w) - 1:
            if t == "rust":
                return "(-1i64)"
            if t == "typescript":
                return "(-1n)"
            if t in ("csharp", "java"):
                return "(-1L)"
            return "(-1)"
        if t == "typescript":
            return f"{hex(val)}n"
        if val >= (1 << 63):
            if t == "rust":
                return f"({hex(val)}u64 as i64)"
            if t == "csharp":
                return f"unchecked((long){hex(val)}UL)"
            if t == "java":
                return f"({hex(val - (1 << 64))}L)"
            if t == "swift":
                return f"Int64(bitPattern: {hex(val)} as UInt64)"
        return hex(val)

    k = expr.decl().kind()
    name = expr.decl().name()
    if k in (
        z3.Z3_OP_FPA_RM_NEAREST_TIES_TO_EVEN,
        z3.Z3_OP_FPA_RM_TOWARD_ZERO,
        z3.Z3_OP_FPA_RM_TOWARD_POSITIVE,
        z3.Z3_OP_FPA_RM_TOWARD_NEGATIVE,
        z3.Z3_OP_FPA_RM_NEAREST_TIES_TO_AWAY,
    ):
        return name
    if expr.num_args() == 0:
        if name in ("a", "in_off_0") or name.endswith("_a_ret"):
            return lhs
        if name in ("b", "in_off_4", "in_off_8") or name.endswith("_b_ret"):
            return rhs
        if name in ("c", "in_off_12", "in_off_16") or name.endswith("_c_ret"):
            return third
        if name in ("d", "in_off_20", "in_off_24") or name.endswith("_d_ret"):
            return fourth
        for idx, ex_name in enumerate(extra_names, start=4):
            letter = chr(ord("a") + idx) if idx < 26 else f"arg{idx}"
            if name in (letter, f"in_off_{idx * 4}", f"in_off_{idx * 8}") or name.endswith(f"_{letter}_ret"):
                return ex_name
        return name

    if k == z3.Z3_OP_BSDIV or name in ("bvsdiv_i", "bvsdiv") or k == z3.Z3_OP_BSREM or name in ("bvsrem_i", "bvsrem"):
        is_rem = k == z3.Z3_OP_BSREM or name in ("bvsrem_i", "bvsrem")
        k0, low0 = _classify_concat_extension(expr.arg(0))
        k1, low1 = _classify_concat_extension(expr.arg(1))
        if k0 == "zext" and k1 == "zext" and low0 is not None and low1 is not None:
            e0 = z3.ZeroExt(64 - low0.size(), low0) if low0.size() < 64 else low0
            e1 = z3.ZeroExt(64 - low1.size(), low1) if low1.size() < 64 else low1
            a0 = translate_z3_to_hiop_primitives(e0, t, lhs, rhs, third, fourth, extra_names)
            a1 = translate_z3_to_hiop_primitives(e1, t, lhs, rhs, third, fourth, extra_names)
            prim = "BV_UREM" if is_rem else "BV_UDIV"
            return HIOP_PRIMITIVES[prim][t].format(a=a0, b=a1)
        if k0 == "sext" and k1 == "sext" and low0 is not None and low1 is not None:
            e0 = z3.SignExt(64 - low0.size(), low0) if low0.size() < 64 else low0
            e1 = z3.SignExt(64 - low1.size(), low1) if low1.size() < 64 else low1
            a0 = translate_z3_to_hiop_primitives(e0, t, lhs, rhs, third, fourth, extra_names)
            a1 = translate_z3_to_hiop_primitives(e1, t, lhs, rhs, third, fourth, extra_names)
            prim = "BV_SREM" if is_rem else "BV_SDIV"
            return HIOP_PRIMITIVES[prim][t].format(a=a0, b=a1)

    if k in (
        z3.Z3_OP_SLT, z3.Z3_OP_SLEQ, z3.Z3_OP_SGT, z3.Z3_OP_SGEQ,
        z3.Z3_OP_ULT, z3.Z3_OP_ULEQ, z3.Z3_OP_UGT, z3.Z3_OP_UGEQ,
        z3.Z3_OP_EQ, z3.Z3_OP_DISTINCT,
    ) and expr.arg(0).size() > 64:
        op0, op1 = expr.arg(0), expr.arg(1)
        div_e = None
        div_on_left = True
        if (
            (op0.decl().kind() == z3.Z3_OP_BSDIV or op0.decl().name() in ("bvsdiv_i", "bvsdiv"))
            and z3.is_bv_value(op1)
            and op1.as_long() == (1 << 63)
        ):
            div_e, div_on_left = op0, True
        elif (
            z3.is_bv_value(op0)
            and op0.as_long() == (1 << 63)
            and (op1.decl().kind() == z3.Z3_OP_BSDIV or op1.decl().name() in ("bvsdiv_i", "bvsdiv"))
        ):
            div_e, div_on_left = op1, False
        if div_e is not None:
            dk0, dlow0 = _classify_concat_extension(div_e.arg(0))
            dk1, dlow1 = _classify_concat_extension(div_e.arg(1))
            if dk0 == "sext" and dk1 == "sext" and dlow0 is not None and dlow1 is not None and dlow0.size() == 64 and dlow1.size() == 64:
                ovf = z3.And(dlow0 == z3.BitVecVal(0x8000000000000000, 64), dlow1 == z3.BitVecVal(-1, 64))
                if div_on_left:
                    ovf_cmp = (
                        z3.Not(ovf) if k in (z3.Z3_OP_SLT, z3.Z3_OP_DISTINCT) else
                        ovf if k in (z3.Z3_OP_SGEQ, z3.Z3_OP_EQ) else
                        z3.BoolVal(True) if k == z3.Z3_OP_SLEQ else
                        z3.BoolVal(False)
                    )
                else:
                    ovf_cmp = (
                        ovf if k in (z3.Z3_OP_SLEQ, z3.Z3_OP_EQ) else
                        z3.Not(ovf) if k in (z3.Z3_OP_SGT, z3.Z3_OP_DISTINCT) else
                        z3.BoolVal(True) if k == z3.Z3_OP_SGEQ else
                        z3.BoolVal(False)
                    )
                return translate_z3_to_hiop_primitives(ovf_cmp, t, lhs, rhs, third, fourth, extra_names)
        def _narrow_ext_64(op_e: z3.ExprRef) -> tuple[str | None, z3.ExprRef | None]:
            if z3.is_bv_value(op_e):
                uv = op_e.as_long()
                sv = op_e.as_signed_long()
                if 0 <= uv < (1 << 64):
                    return "const", z3.BitVecVal(uv, 64)
                if -(1 << 63) <= sv < (1 << 63):
                    return "sext", z3.BitVecVal(sv, 64)
            ek, low = _classify_concat_extension(op_e)
            if ek == "sext" and low is not None and low.size() <= 64:
                return "sext", (z3.SignExt(64 - low.size(), low) if low.size() < 64 else low)
            if ek == "zext" and low is not None and low.size() <= 64:
                return "zext", (z3.ZeroExt(64 - low.size(), low) if low.size() < 64 else low)
            return None, None

        k0, n0 = _narrow_ext_64(expr.arg(0))
        k1, n1 = _narrow_ext_64(expr.arg(1))
        if n0 is not None and n1 is not None:
            if k0 in ("zext", "const") and k1 in ("zext", "const") and ("zext" in (k0, k1)):
                narrow_cmp = (
                    z3.ULT(n0, n1) if k in (z3.Z3_OP_SLT, z3.Z3_OP_ULT) else
                    z3.ULE(n0, n1) if k in (z3.Z3_OP_SLEQ, z3.Z3_OP_ULEQ) else
                    z3.UGT(n0, n1) if k in (z3.Z3_OP_SGT, z3.Z3_OP_UGT) else
                    z3.UGE(n0, n1) if k in (z3.Z3_OP_SGEQ, z3.Z3_OP_UGEQ) else
                    (n0 == n1) if k == z3.Z3_OP_EQ else
                    (n0 != n1)
                )
                return translate_z3_to_hiop_primitives(narrow_cmp, t, lhs, rhs, third, fourth, extra_names)
            if k0 in ("sext", "const") and k1 in ("sext", "const"):
                narrow_cmp = (
                    (n0 < n1) if k == z3.Z3_OP_SLT else
                    (n0 <= n1) if k == z3.Z3_OP_SLEQ else
                    (n0 > n1) if k == z3.Z3_OP_SGT else
                    (n0 >= n1) if k == z3.Z3_OP_SGEQ else
                    z3.ULT(n0, n1) if k == z3.Z3_OP_ULT else
                    z3.ULE(n0, n1) if k == z3.Z3_OP_ULEQ else
                    z3.UGT(n0, n1) if k == z3.Z3_OP_UGT else
                    z3.UGE(n0, n1) if k == z3.Z3_OP_UGEQ else
                    (n0 == n1) if k == z3.Z3_OP_EQ else
                    (n0 != n1)
                )
                return translate_z3_to_hiop_primitives(narrow_cmp, t, lhs, rhs, third, fourth, extra_names)

    if k == z3.Z3_OP_CONCAT:
        ext_kind, low = _classify_concat_extension(expr)
        if ext_kind == "zext" and low is not None and low.size() <= 64:
            a_low = translate_z3_to_hiop_primitives(low, t, lhs, rhs, third, fourth, extra_names)
            if low.size() < 64:
                mask = f"{hex((1 << low.size()) - 1)}n" if t == "typescript" else hex((1 << low.size()) - 1)
                return HIOP_PRIMITIVES["BV_AND"][t].format(a=a_low, b=mask)
            return a_low
        if ext_kind == "sext" and low is not None and low.size() <= 64:
            a_low = translate_z3_to_hiop_primitives(low, t, lhs, rhs, third, fourth, extra_names)
            if low.size() < 64:
                sh = f"{64 - low.size()}n" if t == "typescript" else str(64 - low.size())
                shl = HIOP_PRIMITIVES["BV_SHL"][t].format(a=a_low, b=sh)
                return HIOP_PRIMITIVES["BV_ASHR"][t].format(a=shl, b=sh)
            return a_low
        if expr.size() > 64:
            low_last = expr.arg(expr.num_args() - 1)
            if low_last.size() >= 64:
                return translate_z3_to_hiop_primitives(z3.Extract(63, 0, expr), t, lhs, rhs, third, fourth, extra_names)
            raise NotImplementedError(
                f"Unsupported >64-bit Concat in translate_z3_to_hiop_primitives: {expr}"
            )

    if k == z3.Z3_OP_EXTRACT:
        hi, lo = expr.params()[0], expr.params()[1]
        inner = expr.arg(0)
        if lo == 64 and hi == 127 and inner.decl().kind() == z3.Z3_OP_BMUL and inner.num_args() == 2:
            k0, low0 = _classify_concat_extension(inner.arg(0))
            k1, low1 = _classify_concat_extension(inner.arg(1))
            if low0 is not None and low1 is not None and low0.size() <= 64 and low1.size() <= 64:
                a_s = translate_z3_to_hiop_primitives(low0, t, lhs, rhs, third, fourth, extra_names)
                b_s = translate_z3_to_hiop_primitives(low1, t, lhs, rhs, third, fourth, extra_names)
                m32 = "0xffffffffn" if t == "typescript" else "0xffffffff"
                sh32 = "32n" if t == "typescript" else "32"
                sh63 = "63n" if t == "typescript" else "63"
                a0 = HIOP_PRIMITIVES["BV_AND"][t].format(a=a_s, b=m32)
                a1 = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=a_s, b=sh32)
                b0 = HIOP_PRIMITIVES["BV_AND"][t].format(a=b_s, b=m32)
                b1 = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=b_s, b=sh32)
                p00 = HIOP_PRIMITIVES["BV_MUL"][t].format(a=a0, b=b0)
                p01 = HIOP_PRIMITIVES["BV_MUL"][t].format(a=a0, b=b1)
                p10 = HIOP_PRIMITIVES["BV_MUL"][t].format(a=a1, b=b0)
                p11 = HIOP_PRIMITIVES["BV_MUL"][t].format(a=a1, b=b1)
                p00_hi = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=p00, b=sh32)
                p01_lo = HIOP_PRIMITIVES["BV_AND"][t].format(a=p01, b=m32)
                p10_lo = HIOP_PRIMITIVES["BV_AND"][t].format(a=p10, b=m32)
                mid1 = HIOP_PRIMITIVES["BV_ADD"][t].format(a=p00_hi, b=p01_lo)
                mid = HIOP_PRIMITIVES["BV_ADD"][t].format(a=mid1, b=p10_lo)
                mid_hi = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=mid, b=sh32)
                p01_hi = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=p01, b=sh32)
                p10_hi = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=p10, b=sh32)
                s1 = HIOP_PRIMITIVES["BV_ADD"][t].format(a=p11, b=p01_hi)
                s2 = HIOP_PRIMITIVES["BV_ADD"][t].format(a=s1, b=p10_hi)
                mulhu = HIOP_PRIMITIVES["BV_ADD"][t].format(a=s2, b=mid_hi)
                if k0 == "sext" and k1 == "sext":
                    sa = HIOP_PRIMITIVES["BV_AND"][t].format(
                        a=HIOP_PRIMITIVES["BV_ASHR"][t].format(a=a_s, b=sh63), b=b_s
                    )
                    sb = HIOP_PRIMITIVES["BV_AND"][t].format(
                        a=HIOP_PRIMITIVES["BV_ASHR"][t].format(a=b_s, b=sh63), b=a_s
                    )
                    sub1 = HIOP_PRIMITIVES["BV_SUB"][t].format(a=mulhu, b=sa)
                    return HIOP_PRIMITIVES["BV_SUB"][t].format(a=sub1, b=sb)
                if k0 == "sext" and k1 == "zext":
                    sa = HIOP_PRIMITIVES["BV_AND"][t].format(
                        a=HIOP_PRIMITIVES["BV_ASHR"][t].format(a=a_s, b=sh63), b=b_s
                    )
                    return HIOP_PRIMITIVES["BV_SUB"][t].format(a=mulhu, b=sa)
                return mulhu

    args = [translate_z3_to_hiop_primitives(expr.arg(i), t, lhs, rhs, third, fourth, extra_names) for i in range(expr.num_args())]
    if k == z3.Z3_OP_UNINTERPRETED and name.startswith("call_"):
        from .compiler_rt_lifter import emit_compiler_rt_call_expr
        return emit_compiler_rt_call_expr(name, args, t)
    if k == z3.Z3_OP_UNINTERPRETED and name.startswith("mem_load_"):
        return f"{name}(mem, {args[0]})"
    if k == z3.Z3_OP_UNINTERPRETED and name.startswith("mem_store_"):
        return f"{name}(mem, {args[0]}, {args[1]})"
    if k == z3.Z3_OP_FPA_TO_FP:
        return args[-1]
    if k == z3.Z3_OP_FPA_TO_IEEE_BV:
        return args[0]
    if k in (z3.Z3_OP_FPA_TO_UBV, z3.Z3_OP_FPA_TO_SBV):
        return f"fcvt_to_bv64({args[-1]})"
    if k in (z3.Z3_OP_FPA_ADD, z3.Z3_OP_FPA_SUB, z3.Z3_OP_FPA_MUL, z3.Z3_OP_FPA_DIV):
        fop = {
            z3.Z3_OP_FPA_ADD: "f64_add",
            z3.Z3_OP_FPA_SUB: "f64_sub",
            z3.Z3_OP_FPA_MUL: "f64_mul",
            z3.Z3_OP_FPA_DIV: "f64_div",
        }[k]
        return f"{fop}({args[1]}, {args[2]})"
    if k == z3.Z3_OP_FPA_SQRT:
        return f"f64_sqrt({args[1]})"
    if k == z3.Z3_OP_FPA_FMA:
        return f"f64_fma({args[1]}, {args[2]}, {args[3]})"
    if k in (z3.Z3_OP_FPA_MIN, z3.Z3_OP_FPA_MAX):
        fn = "f64_min" if k == z3.Z3_OP_FPA_MIN else "f64_max"
        return f"{fn}({args[0]}, {args[1]})"
    if k in (
        z3.Z3_OP_FPA_ABS,
        z3.Z3_OP_FPA_NEG,
        z3.Z3_OP_FPA_IS_NAN,
        z3.Z3_OP_FPA_IS_INF,
        z3.Z3_OP_FPA_IS_ZERO,
        z3.Z3_OP_FPA_IS_NORMAL,
        z3.Z3_OP_FPA_IS_SUBNORMAL,
        z3.Z3_OP_FPA_IS_NEGATIVE,
        z3.Z3_OP_FPA_IS_POSITIVE,
    ):
        fn = {
            z3.Z3_OP_FPA_ABS: "f64_abs",
            z3.Z3_OP_FPA_NEG: "f64_neg",
            z3.Z3_OP_FPA_IS_NAN: "f64_is_nan",
            z3.Z3_OP_FPA_IS_INF: "f64_is_inf",
            z3.Z3_OP_FPA_IS_ZERO: "f64_is_zero",
            z3.Z3_OP_FPA_IS_NORMAL: "f64_is_normal",
            z3.Z3_OP_FPA_IS_SUBNORMAL: "f64_is_subnormal",
            z3.Z3_OP_FPA_IS_NEGATIVE: "f64_is_negative",
            z3.Z3_OP_FPA_IS_POSITIVE: "f64_is_positive",
        }[k]
        return f"{fn}({args[0]})"
    if k in (z3.Z3_OP_FPA_EQ, z3.Z3_OP_FPA_LT, z3.Z3_OP_FPA_LE, z3.Z3_OP_FPA_GT, z3.Z3_OP_FPA_GE):
        fcmp = {
            z3.Z3_OP_FPA_EQ: "f64_eq",
            z3.Z3_OP_FPA_LT: "f64_lt",
            z3.Z3_OP_FPA_LE: "f64_le",
            z3.Z3_OP_FPA_GT: "f64_gt",
            z3.Z3_OP_FPA_GE: "f64_ge",
        }[k]
        return f"{fcmp}({args[0]}, {args[1]})"
    if k == z3.Z3_OP_BADD:
        res = args[0]
        for x in args[1:]:
            res = HIOP_PRIMITIVES["BV_ADD"][t].format(a=res, b=x)
        return res
    if k == z3.Z3_OP_BSUB:
        return HIOP_PRIMITIVES["BV_SUB"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BMUL:
        res = args[0]
        for x in args[1:]:
            res = HIOP_PRIMITIVES["BV_MUL"][t].format(a=res, b=x)
        return res
    if k == z3.Z3_OP_BAND:
        res = args[0]
        for x in args[1:]:
            res = HIOP_PRIMITIVES["BV_AND"][t].format(a=res, b=x)
        return res
    if k == z3.Z3_OP_BOR:
        res = args[0]
        for x in args[1:]:
            res = HIOP_PRIMITIVES["BV_OR"][t].format(a=res, b=x)
        return res
    if k == z3.Z3_OP_BXOR:
        res = args[0]
        for x in args[1:]:
            res = HIOP_PRIMITIVES["BV_XOR"][t].format(a=res, b=x)
        return res
    if k == z3.Z3_OP_BNOT:
        return HIOP_PRIMITIVES["BV_NOT"][t].format(a=args[0])
    if k == z3.Z3_OP_BNEG:
        z_lit = "0n" if t == "typescript" else "0"
        return HIOP_PRIMITIVES["BV_SUB"][t].format(a=z_lit, b=args[0])
    if k == z3.Z3_OP_BSHL:
        return HIOP_PRIMITIVES["BV_SHL"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BLSHR:
        return HIOP_PRIMITIVES["BV_LSHR"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BASHR:
        return HIOP_PRIMITIVES["BV_ASHR"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BSDIV or name in ("bvsdiv_i", "bvsdiv"):
        return HIOP_PRIMITIVES["BV_SDIV"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BUDIV or name in ("bvudiv_i", "bvudiv"):
        return HIOP_PRIMITIVES["BV_UDIV"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BSREM or name in ("bvsrem_i", "bvsrem"):
        return HIOP_PRIMITIVES["BV_SREM"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_BUREM or name in ("bvurem_i", "bvurem"):
        return HIOP_PRIMITIVES["BV_UREM"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_ULT:
        return HIOP_PRIMITIVES["BV_ULT"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_UGT:
        return HIOP_PRIMITIVES["BV_ULT"][t].format(a=args[1], b=args[0])
    if k == z3.Z3_OP_ULEQ:
        gt = HIOP_PRIMITIVES["BV_ULT"][t].format(a=args[1], b=args[0])
        return f"(not {gt})" if t == "python" else f"(!{gt})"
    if k == z3.Z3_OP_UGEQ:
        lt = HIOP_PRIMITIVES["BV_ULT"][t].format(a=args[0], b=args[1])
        return f"(not {lt})" if t == "python" else f"(!{lt})"
    if k == z3.Z3_OP_SLT:
        return HIOP_PRIMITIVES["BV_SLT"][t].format(a=args[0], b=args[1])
    if k == z3.Z3_OP_SGT:
        return HIOP_PRIMITIVES["BV_SLT"][t].format(a=args[1], b=args[0])
    if k == z3.Z3_OP_SLEQ:
        gt = HIOP_PRIMITIVES["BV_SLT"][t].format(a=args[1], b=args[0])
        return f"(not {gt})" if t == "python" else f"(!{gt})"
    if k == z3.Z3_OP_SGEQ:
        lt = HIOP_PRIMITIVES["BV_SLT"][t].format(a=args[0], b=args[1])
        return f"(not {lt})" if t == "python" else f"(!{lt})"
    if k == z3.Z3_OP_EQ:
        return f"({args[0]} === {args[1]})" if t in ("typescript", "php") else f"({args[0]} == {args[1]})"
    if k == z3.Z3_OP_DISTINCT:
        return f"({args[0]} !== {args[1]})" if t in ("typescript", "php") else f"({args[0]} != {args[1]})"
    if k == z3.Z3_OP_NOT:
        return f"(not {args[0]})" if t == "python" else f"(!{args[0]})"
    if k == z3.Z3_OP_AND:
        if expr.num_args() <= 4 and len(str(expr)) <= 240:
            kept_exprs = [expr.arg(i) for i in range(expr.num_args())]
            pruned_args = []
            for idx, sub in enumerate(kept_exprs):
                others = [kept_exprs[j] for j in range(len(kept_exprs)) if j != idx]
                if others:
                    s = z3.Solver()
                    if s.check(z3.And(*others, z3.Not(sub))) == z3.unsat:
                        kept_exprs[idx] = z3.BoolVal(True)
                        continue
                pruned_args.append(args[idx])
        else:
            pruned_args = list(args)
        if not pruned_args:
            return args[0]
        if len(pruned_args) == 1:
            return pruned_args[0]
        op_s = " and " if t == "python" else " && "
        return "(" + op_s.join(pruned_args) + ")"
    if k == z3.Z3_OP_OR:
        op_s = " or " if t == "python" else " || "
        return "(" + op_s.join(args) + ")"
    if k == z3.Z3_OP_ITE:
        return HIOP_PRIMITIVES["BV_ITE"][t].format(c=args[0], a=args[1], b=args[2])
    if k == z3.Z3_OP_EXTRACT:
        hi, lo = expr.params()[0], expr.params()[1]
        if hi == expr.arg(0).size() - 1 and lo == 0:
            return args[0]
        if lo == 0 and (hi - lo + 1) >= 64:
            return f"({args[0]} & 0xFFFFFFFFFFFFFFFF)" if t in ("python", "ruby") else args[0]
        mask = f"{hex((1 << (hi - lo + 1)) - 1)}n" if t == "typescript" else hex((1 << (hi - lo + 1)) - 1)
        if lo == 0:
            return HIOP_PRIMITIVES["BV_AND"][t].format(a=args[0], b=mask)
        sh_lo = f"{lo}n" if t == "typescript" else str(lo)
        shifted = HIOP_PRIMITIVES["BV_LSHR"][t].format(a=args[0], b=sh_lo)
        return HIOP_PRIMITIVES["BV_AND"][t].format(a=shifted, b=mask)
    if k == z3.Z3_OP_CONCAT:
        segments: list[str] = []
        for i in range(expr.num_args()):
            sub_e = expr.arg(i)
            if z3.is_bv_value(sub_e) and sub_e.as_long() == 0:
                continue
            shift = sum(expr.arg(j).size() for j in range(i + 1, expr.num_args()))
            seg = args[i]
            if sub_e.size() < 64 and sub_e.decl().kind() != z3.Z3_OP_EXTRACT:
                mask = f"{hex((1 << sub_e.size()) - 1)}n" if t == "typescript" else hex((1 << sub_e.size()) - 1)
                seg = HIOP_PRIMITIVES["BV_AND"][t].format(a=seg, b=mask)
            if shift > 0:
                sh_s = f"{shift}n" if t == "typescript" else str(shift)
                seg = HIOP_PRIMITIVES["BV_SHL"][t].format(a=seg, b=sh_s)
            segments.append(seg)
        if not segments:
            return "0n" if t == "typescript" else "0x0"
        res = segments[0]
        for s_part in segments[1:]:
            res = HIOP_PRIMITIVES["BV_OR"][t].format(a=res, b=s_part)
        return res
    if k == z3.Z3_OP_ZERO_EXT:
        w_c = expr.arg(0).size()
        if w_c < 64:
            mask = f"{hex((1 << w_c) - 1)}n" if t == "typescript" else hex((1 << w_c) - 1)
            return HIOP_PRIMITIVES["BV_AND"][t].format(a=args[0], b=mask)
        return args[0]
    if k == z3.Z3_OP_SIGN_EXT:
        w_c = expr.arg(0).size()
        if w_c < 64:
            sh = f"{64 - w_c}n" if t == "typescript" else str(64 - w_c)
            shl = HIOP_PRIMITIVES["BV_SHL"][t].format(a=args[0], b=sh)
            return HIOP_PRIMITIVES["BV_ASHR"][t].format(a=shl, b=sh)
        return args[0]
    raise NotImplementedError(
        f"Unhandled Z3 operator in translate_z3_to_hiop_primitives: kind={k}, name={name!r}, expr={expr}"
    )


_TARGET_VOCAB_CACHE: dict[str, list[UniversalRichNode]] = {}


def format_hiop_target_template(op_key: str, lang: str) -> str | None:
    """Return the `{a}`, `{b}`, `{c}` target-code template for `(op_key, lang)`,
    normalizing `BV_ITE`'s `(cond={c}, then={a}, else={b})` placeholders to the
    `UnitLean`'s positional input order `(0: cond={a}, 1: then={b}, 2: else={c})`."""
    import re as _re

    t = normalize_target_lang(lang)
    if op_key == "BV_ITE" and t in HIOP_PRIMITIVES["BV_ITE"]:
        return _re.sub(
            r"\{([cab])\}",
            lambda m: {"c": "{a}", "a": "{b}", "b": "{c}"}[m.group(1)],
            HIOP_PRIMITIVES["BV_ITE"][t],
        )
    if op_key in HIOP_PRIMITIVES and t in HIOP_PRIMITIVES[op_key]:
        return HIOP_PRIMITIVES[op_key][t]
    if t == "python" and op_key == "PY_FLOORDIV":
        return "({a} // {b})"
    if t == "python" and op_key == "PY_MOD":
        return "({a} % {b})"
    if t == "dart" and op_key == "DART_EUCLID_MOD":
        return "({a} % {b})"
    if t in ("cpp", "ruby", "php") and op_key == "SPACESHIP":
        return "({a} <=> {b})"
    return None


class AutoPoly:
    """Autonomous Polyfill Engine: executes or emits any UR-Node in any target language."""

    def __init__(self) -> None:
        self.prover = EquivalenceProver()

    @staticmethod
    def get_target_vocab_nodes(target_lang: str) -> list[UniversalRichNode]:
        """Return the target language's native 64-bit `HiOp` `UR-Node` vocabulary backed by Sail `UnitLean`s."""
        t = normalize_target_lang(target_lang)
        if t in _TARGET_VOCAB_CACHE:
            return _TARGET_VOCAB_CACHE[t]
        from .verify_hiop_primitives import load_language_64bit_unit_leans

        lang_uls = load_language_64bit_unit_leans()
        vocab: list[UniversalRichNode] = []
        for op_key, ul in lang_uls.get(t, {}).items():
            vocab.append(
                UniversalRichNode(
                    hiop={
                        "lang": t,
                        "operator": op_key,
                        "spelling": op_key,
                        "target_code": format_hiop_target_template(op_key, t),
                    },
                    meaning={"unit_lean": ul},
                )
            )
        _TARGET_VOCAB_CACHE[t] = vocab
        return vocab

    def _render_tier2_composition(
        self,
        cand: UniversalRichNode,
        proof: dict[str, Any],
        t: str,
        lhs: str,
        rhs: str,
        third: str,
        fourth: str,
        extra_names: Sequence[str],
    ) -> str:
        plan = proof.get("composition_plan") or {}
        base_tmpl = cand.hiop.get("target_code") or f"({lhs} {cand.hiop.get('spelling', '/')} {rhs})"
        if plan.get("kind") == "arg1_mask_63":
            if "& 63" in base_tmpl or "& 63n" in base_tmpl or "wrapping_sh" in base_tmpl:
                if "{a}" in base_tmpl or "{b}" in base_tmpl or "{c}" in base_tmpl or "{d}" in base_tmpl:
                    return base_tmpl.format(a=lhs, b=rhs, c=third, d=fourth)
                return base_tmpl
            mask_lit = "63n" if t == "typescript" else "63"
            masked_rhs = HIOP_PRIMITIVES["BV_AND"][t].format(a=rhs, b=mask_lit)
            if "{a}" in base_tmpl or "{b}" in base_tmpl or "{c}" in base_tmpl or "{d}" in base_tmpl:
                return base_tmpl.format(a=lhs, b=masked_rhs, c=third, d=fourth)
            return base_tmpl

        base_code = base_tmpl
        if "{a}" in base_code or "{b}" in base_code or "{c}" in base_code or "{d}" in base_code:
            base_code = base_code.format(a=lhs, b=rhs, c=third, d=fourth)

        arg_list = [lhs, rhs, third, fourth]
        steps = list(proof.get("residual_steps") or ())
        if not steps:
            for d_res, r_res in reversed(proof.get("residual_pieces", ())):
                cond_code = translate_z3_to_hiop_primitives(d_res, t, lhs, rhs, third, fourth, extra_names)
                val_code = translate_z3_to_hiop_primitives(r_res, t, lhs, rhs, third, fourth, extra_names)
                base_code = HIOP_PRIMITIVES["BV_ITE"][t].format(c=cond_code, a=val_code, b=base_code)
            return base_code

        # Ensure boundary/trap guards (e.g. b == 0, INT64_MIN / -1) are placed first in `steps`
        # so they wrap outermost when iterating `reversed(steps)`.
        steps.sort(
            key=lambda st: 0
            if st["guard"]["kind"] in ("eq_const", "int64_min_div_neg1", "shift_out_of_bounds")
            else 1
        )

        orig_base_code = base_code
        for step in reversed(steps):
            g_spec = step["guard"]
            r_spec = step["range"]

            rk = r_spec["kind"]
            if rk == "base_op":
                op_sym = r_spec["op"]
                rhs_kind, rhs_val = r_spec["rhs"]
                if rhs_kind == "const":
                    rhs_s = f"{rhs_val}n" if t == "typescript" else str(rhs_val)
                else:
                    rhs_s = arg_list[int(rhs_val)]
                prim_k = "BV_ADD" if op_sym == "+" else "BV_SUB"
                val_code = HIOP_PRIMITIVES[prim_k][t].format(a=orig_base_code, b=rhs_s)
            elif rk == "const":
                val_code = translate_z3_to_hiop_primitives(
                    z3.BitVecVal(int(r_spec["value"]), 64), t, lhs, rhs, third, fourth, extra_names
                )
            elif rk == "arg":
                val_code = arg_list[int(r_spec["index"])]
            elif rk == "base_const_arg1":
                c_lit = f"{r_spec['const']}n" if t == "typescript" else str(r_spec["const"])
                clean_tmpl = base_tmpl.replace("({b} & 63)", "{b}").replace("(BigInt({b}) & 63n)", "BigInt({b})")
                val_code = clean_tmpl.format(a=lhs, b=c_lit, c=third, d=fourth)
            else:
                val_code = translate_z3_to_hiop_primitives(
                    r_spec["expr"], t, lhs, rhs, third, fourth, extra_names
                )

            gk = g_spec["kind"]
            if gk == "opp_sign_rem_nonzero":
                xor_ab = HIOP_PRIMITIVES["BV_XOR"][t].format(a=lhs, b=rhs)
                zero_lit = "0n" if t == "typescript" else "0"
                sign_lt = HIOP_PRIMITIVES["BV_SLT"][t].format(a=xor_ab, b=zero_lit).replace(
                    "(((0 + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000)", "0"
                )
                if t == "python" and cand.hiop.get("operator") in ("PY_FLOORDIV", "PY_MOD"):
                    rem_ab = f"({lhs} % {rhs})"
                else:
                    rem_ab = HIOP_PRIMITIVES["BV_SREM"][t].format(a=lhs, b=rhs)
                neq_op = "!==" if t in ("typescript", "php") else "!="
                rem_nz = f"({rem_ab} {neq_op} {zero_lit})"
                and_op = " and " if t == "python" else " && "
                cond_code = f"({sign_lt}{and_op}{rem_nz})"
            elif gk == "eq_const":
                arg_s = arg_list[int(g_spec["arg"])]
                val_s = f"{g_spec['value']}n" if t == "typescript" else str(g_spec["value"])
                eq_op = "===" if t in ("typescript", "php") else "=="
                cond_code = f"({arg_s} {eq_op} {val_s})"
            elif gk == "neq_const":
                arg_s = arg_list[int(g_spec["arg"])]
                val_s = f"{g_spec['value']}n" if t == "typescript" else str(g_spec["value"])
                neq_op = "!==" if t in ("typescript", "php") else "!="
                cond_code = f"({arg_s} {neq_op} {val_s})"
            elif gk == "int64_min_div_neg1":
                min_lit = translate_z3_to_hiop_primitives(
                    z3.BitVecVal(0x8000000000000000, 64), t, lhs, rhs, third, fourth, extra_names
                )
                neg1_lit = translate_z3_to_hiop_primitives(
                    z3.BitVecVal(-1, 64), t, lhs, rhs, third, fourth, extra_names
                )
                eq_op = "===" if t in ("typescript", "php") else "=="
                and_op = " and " if t == "python" else " && "
                cond_code = f"(({lhs} {eq_op} {min_lit}){and_op}({rhs} {eq_op} {neg1_lit}))"
            elif gk == "shift_out_of_bounds":
                zero_lit = "0n" if t == "typescript" else "0"
                sixtyfour_lit = "64n" if t == "typescript" else "64"
                lt0 = HIOP_PRIMITIVES["BV_SLT"][t].format(a=rhs, b=zero_lit)
                lt64 = HIOP_PRIMITIVES["BV_SLT"][t].format(a=rhs, b=sixtyfour_lit)
                ge64 = f"(not {lt64})" if t == "python" else f"(!{lt64})"
                or_op = " or " if t == "python" else " || "
                cond_code = f"({lt0}{or_op}{ge64})"
            else:
                cond_code = translate_z3_to_hiop_primitives(
                    g_spec["expr"], t, lhs, rhs, third, fourth, extra_names
                )

            base_code = HIOP_PRIMITIVES["BV_ITE"][t].format(c=cond_code, a=val_code, b=base_code)
        return base_code

    def synthesize_from_sail_unit(
        self,
        node: UniversalRichNode,
        target_lang: str,
        candidate_target_nodes: Sequence[UniversalRichNode] = (),
        lhs: str = "a",
        rhs: str = "b",
        third: str = "c",
        fourth: str = "d",
        extra_names: Sequence[str] = (),
        search_target_vocab: bool = False,
    ) -> dict[str, Any]:
        """Synthesize Tier 1, Tier 2, or Tier 3 target code purely from Sail-derived `UnitLean`s."""
        t = normalize_target_lang(target_lang)
        ul_src = node.meaning.get("unit_lean")
        if ul_src is None and node.meaning.get("unit_obj") is not None:
            from PseudoArch.map_unit_to_lean import compose_LoOp_leans
            ul_src = compose_LoOp_leans(node.meaning["unit_obj"])
            node.meaning["unit_lean"] = ul_src
        if ul_src is None:
            raise ValueError(
                f"UniversalRichNode {node.qualified_name!r} lacks Sail-derived 'unit_lean'; refusing silent fallback."
            )

        cands: Sequence[UniversalRichNode] = candidate_target_nodes
        if not cands and search_target_vocab and not getattr(ul_src, "ext_calls", ()):
            n_in = len(ul_src.inputs)
            cands = [
                c_node
                for c_node in self.get_target_vocab_nodes(t)
                if len(c_node.meaning["unit_lean"].inputs) == n_in
            ]

        # Tier 1: Exact Domain-Range Match against any candidate target UR-Node
        tier2_matches: list[tuple[tuple[int, int, int], UniversalRichNode, dict[str, Any]]] = []
        for cand in cands:
            proof = self.prover.prove_domain_range_partition(node, cand)
            if proof.get("equivalent"):
                sp = cand.hiop.get("target_code") or f"({lhs} {cand.hiop.get('spelling', '+')} {rhs})"
                if "{a}" in sp or "{b}" in sp or "{c}" in sp or "{d}" in sp:
                    sp = sp.format(a=lhs, b=rhs, c=third, d=fourth)
                return {
                    "tier": "tier1_exact_native_hiop",
                    "code": sp,
                    "matched_candidate": cand.qualified_name,
                    "proof": proof,
                }
            if proof.get("tier") == "tier2_piecewise_hiop":
                plan = proof.get("composition_plan") or {}
                steps = proof.get("residual_steps") or ()
                is_mask = 0 if plan.get("kind") == "arg1_mask_63" else 1
                backstop_cnt = sum(
                    1
                    for st in steps
                    if st["guard"]["kind"] == "z3_backstop" or st["range"]["kind"] == "z3_backstop"
                )
                rank = (is_mask, backstop_cnt, len(steps))
                tier2_matches.append((rank, cand, proof))

        # Tier 2: Piecewise Domain-Range Guarded Match against the highest-ranked candidate UR-Node
        if tier2_matches:
            tier2_matches.sort(key=lambda item: item[0])
            _rank, best_cand, best_proof = tier2_matches[0]
            composed_code = self._render_tier2_composition(
                best_cand, best_proof, t, lhs, rhs, third, fourth, extra_names
            )
            return {
                "tier": "tier2_piecewise_hiop",
                "code": composed_code,
                "matched_candidate": best_cand.qualified_name,
                "proof": best_proof,
            }

        # Tier 3: Guaranteed LoOp-to-HiOpPrimitive Backstop from Sail-derived UnitLean
        w_in = 64
        if ul_src.inputs:
            first_k = sorted(ul_src.inputs.keys())[0]
            w_in = ul_src.inputs[first_k].size()
        a_sym = z3.BitVec("a", w_in)
        b_sym = z3.BitVec("b", w_in)
        c_sym = z3.BitVec("c", w_in)
        d_sym = z3.BitVec("d", w_in)
        _pieces, comb = canonicalize_unit_lean(ul_src, a_sym, b_sym, c_sym, d_sym)
        code = translate_z3_to_hiop_primitives(comb, t, lhs, rhs, third, fourth, extra_names)
        lo_ctors = [l.constructor for l in ul_src.loop_leans]
        return {
            "tier": "tier3_loop_primitive_backstop",
            "code": code,
            "lo_ops": lo_ctors,
            "ext_calls": list(getattr(ul_src, "ext_calls", ())),
            "ordering_model": RISCV64_ORDERING_PER_TARGET_LANGUAGE[t],
        }

    def emit_target_code(
        self,
        node: UniversalRichNode,
        target_lang: str,
        lhs: str = "a",
        rhs: str = "b",
        candidate_target_nodes: Sequence[UniversalRichNode] = (),
        third: str = "c",
        fourth: str = "d",
        extra_names: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Synthesize target-language code for `node` purely from its Sail-derived `UnitLean`."""
        return self.synthesize_from_sail_unit(
            node, target_lang, candidate_target_nodes, lhs, rhs, third, fourth, extra_names
        )
