"""End-to-end verification of the complete PseudoArch -> Ledgerer -> AutoPoly
pipeline with zero hardcoded opcode or operator tables.
"""

import subprocess
import sys
import tempfile
import z3

import pathlib as _pl; sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))

import PseudoArch
from PseudoArch.sail_model_of_riscv import sail_model_commit
from PseudoArch.map_LoOp_to_lean import list_gmp_axiom_bodies, list_flattened_slices
from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit
from PseudoArch.map_HiOp_to_unit.model_lang_parts.context.entry_context import (
    Operator,
    PartState0,
    StateInfo0,
)
from PseudoArch.map_unit_to_lean import DomainRangePiece, UnitLean
from PseudoCoup.ledgerer.universal_rich_node import UniversalRichNode
from PseudoCoup.hub.autopoly.polyfill import AutoPoly, translate_z3_to_hiop_primitives


def eval_c_expr(expr_c: str, a_val: int, b_val: int) -> int:
    src = (
        "#include <stdint.h>\n#include <stdio.h>\n"
        f"int main(void) {{ int64_t a = {a_val}LL, b = {b_val}LL; "
        f"int64_t r = {expr_c}; printf(\"%lld\\n\", (long long)r); return 0; }}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["clang", "-x", "c", "-", "-o", f"{td}/t"], input=src, text=True, check=True)
        out = subprocess.run([f"{td}/t"], capture_output=True, text=True, check=True).stdout.strip()
        return int(out)


def eval_rust_expr(expr_rs: str, a_val: int, b_val: int) -> int:
    src = (
        "#![allow(unused_parens, unused_variables)]\n"
        f"fn main() {{ let a: i64 = {a_val}; let b: i64 = {b_val}; "
        f"let r: i64 = {expr_rs}; println!(\"{{}}\", r); }}\n"
    )
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["rustc", "-", "-o", f"{td}/t"], input=src, text=True, check=True)
        out = subprocess.run([f"{td}/t"], capture_output=True, text=True, check=True).stdout.strip()
        return int(out)


def make_ur_node(name: str, spelling: str, ops: tuple, parts: tuple) -> UniversalRichNode:
    op = Operator(name=name, spelling=spelling, operands=ops)
    s0 = StateInfo0("c", op, parts, target="riscv64")
    mapped = map_state_info_0_to_unit(s0)
    return UniversalRichNode.from_mapped_hiop(mapped, s0)


def main() -> None:
    print(f"=== 1. PseudoArch Sail Model & GMP Slices ===")
    commit = sail_model_commit()
    gmp_bodies = list_gmp_axiom_bodies()
    flat_slices = list_flattened_slices()
    print(f"  Sail model commit : {commit}")
    print(f"  GMP axiom bodies  : {len(gmp_bodies)} (e.g. {sorted(gmp_bodies)[:3]})")
    print(f"  Flattened slices  : {len(flat_slices)}")
    assert len(gmp_bodies) == 67 and len(flat_slices) >= 670

    autopoly = AutoPoly()

    print("\n=== 2. Tier 1: Exact Domain-Range Match from Hijacked Machine Words ===")
    node_add = make_ur_node(
        "BinaryOperator.Add", "a + b", ("a", "b"), (PartState0("a", "long"), PartState0("b", "long"))
    )
    cand_add = make_ur_node(
        "BinaryOperator.Add", "a + b", ("a", "b"), (PartState0("a", "long"), PartState0("b", "long"))
    )
    cand_add.hiop["target_code"] = "(a + b)"
    t1 = autopoly.synthesize_from_sail_unit(node_add, "python", [cand_add])
    print(f"  LoOps             : {node_add.canonical_lo_ops()}")
    print(f"  Tier              : {t1['tier']} (Z3 status: {t1['proof']['z3_status']})")
    print(f"  Emitted code      : {t1['code']}")
    assert t1["tier"] == "tier1_exact_native_hiop"

    print("\n=== 3. Tier 2: Piecewise Domain-Range Guarded Synthesis (Div) ===")
    node_div = make_ur_node(
        "BinaryOperator.Div", "a / b", ("a", "b"), (PartState0("a", "long"), PartState0("b", "long"))
    )
    ul_div = node_div.meaning["unit_lean"]
    print(f"  LoOps             : {node_div.canonical_lo_ops()}")
    print(f"  Sail DR Pieces    : {len(ul_div.pieces)} disjoint pieces")
    # Candidate target operator has the interior division domain & range (Piece 2 of ul_div)
    interior_d = ul_div.pieces[2].domain
    interior_r = ul_div.pieces[2].range_term
    cand_ul = UnitLean(
        loop_leans=(),
        inputs=ul_div.inputs,
        output_offset=16,
        output_width=8,
        combined_term=interior_r,
        pieces=(DomainRangePiece(interior_d, interior_r, (), None),),
        is_straight_line=True,
    )
    cand_div = UniversalRichNode(
        hiop={"lang": "target", "operator": "trunc_div", "target_code": "trunc_div(a, b)"},
        units={},
        meaning={"unit_lean": cand_ul},
    )
    for lang in ("c", "rust", "python"):
        t2 = autopoly.synthesize_from_sail_unit(node_div, lang, [cand_div])
        print(f"  [{lang:6s}] {t2['tier']} -> {t2['code']}")
        assert t2["tier"] == "tier2_piecewise_hiop"

    print("\n=== 4. Tier 3: Guaranteed LoOp-to-HiOpPrimitive Synthesis (13-bit Bit-Field Shl) ===")
    node_bf_shl = make_ur_node(
        "BinaryOperator.Shl",
        "a << b",
        ("a", "b"),
        (PartState0("a", "int", place="bit-field"), PartState0("b", "int")),
    )
    for lang in ("c", "rust", "python"):
        t3 = autopoly.synthesize_from_sail_unit(node_bf_shl, lang, [])
        print(f"  [{lang:6s}] {t3['tier']} -> {t3['code']}")
        assert t3["tier"] == "tier3_loop_primitive_backstop"
        if lang == "python":
            val = eval(t3["code"], {"a": 0xFFFF, "b": 2})
            assert val == ((0xFFFF & 0x1FFF) << 2)
            print(f"  Verified execution on (a=0xFFFF, b=2): {hex(val)} == {hex((0xFFFF & 0x1FFF) << 2)}")

    print("\n=== 5. Adversarial Audit Check: Constant Shift a << 3 (Z3_OP_CONCAT) ===")
    node_const_shl = make_ur_node(
        "BinaryOperator.Shl",
        "a << b",
        ("a", "b"),
        (PartState0("a", "long"), PartState0("b", "int", constant_value="3")),
    )
    for lang in ("python", "c", "rust"):
        tc = autopoly.synthesize_from_sail_unit(node_const_shl, lang, [])
        print(f"  [{lang:6s}] {tc['tier']} -> {tc['code']}")
        if lang == "python":
            res = eval(tc["code"], {"a": 7, "b": 3})
        elif lang == "c":
            res = eval_c_expr(tc["code"], 7, 3)
        else:
            res = eval_rust_expr(tc["code"], 7, 3)
        assert res == 56, f"Expected 56 for {lang}, got {res}"

    print("\n=== 6. Adversarial Audit Check: BinaryOperator.Rem (bvsrem_i) ===")
    node_rem = make_ur_node(
        "BinaryOperator.Rem",
        "a % b",
        ("a", "b"),
        (PartState0("a", "long"), PartState0("b", "long")),
    )
    for lang in ("python", "c", "rust"):
        tr = autopoly.synthesize_from_sail_unit(node_rem, lang, [])
        print(f"  [{lang:6s}] {tr['tier']} -> {tr['code']}")
        for (av, bv), expected in (((17, 5), 2), ((-17, 5), -2)):
            if lang == "python":
                raw = eval(tr["code"], {"__builtins__": {"int": int, "abs": abs}}, {"a": av, "b": bv}) & ((1 << 64) - 1)
                res = raw - (1 << 64) if raw >= (1 << 63) else raw
            elif lang == "c":
                res = eval_c_expr(tr["code"], av, bv)
            else:
                res = eval_rust_expr(tr["code"], av, bv)
            assert res == expected, f"Expected {expected} for {lang} on ({av}, {bv}), got {res}"

    print("\n=== 7. Adversarial Checks (Tier 3 Div/UDiv/URem, INT64_MIN % -1, Float Precision, Rust Sub) ===")
    s64 = lambda v: (v & ((1 << 64) - 1)) - ((1 << 64) if (v & ((1 << 64) - 1)) >= (1 << 63) else 0)
    for lang in ("python", "c", "rust"):
        tr_div = autopoly.emit_target_code(node_div, lang)
        assert tr_div["tier"] == "tier3_loop_primitive_backstop"
        for av, bv, expected in (
            (20, 5, 4),
            (-20, 5, -4),
            (0x7FFFFFFFFFFFFFFF, 1, 0x7FFFFFFFFFFFFFFF),
            (-9223372036854775808, -1, -9223372036854775808),
            (20, 0, -1),
        ):
            res = (
                s64(eval(tr_div["code"], {"a": av, "b": bv}))
                if lang == "python"
                else (eval_c_expr(tr_div["code"], av, bv) if lang == "c" else eval_rust_expr(tr_div["code"], av, bv))
            )
            assert res == expected, f"Tier 3 Div mismatch in {lang} on ({av}, {bv}): {res} != {expected}"
        tr_rem = autopoly.emit_target_code(node_rem, lang)
        for av, bv, expected in ((-9223372036854775808, -1, 0), (0x7FFFFFFFFFFFFFFF, 1, 0)):
            res = (
                s64(eval(tr_rem["code"], {"a": av, "b": bv}))
                if lang == "python"
                else (eval_c_expr(tr_rem["code"], av, bv) if lang == "c" else eval_rust_expr(tr_rem["code"], av, bv))
            )
            assert res == expected, f"Tier 3 Rem mismatch in {lang} on ({av}, {bv}): {res} != {expected}"

    node_udiv = make_ur_node("BinaryOperator.Div", "a / b", ("a", "b"), (PartState0("a", "unsigned long"), PartState0("b", "unsigned long")))
    node_urem = make_ur_node("BinaryOperator.Rem", "a % b", ("a", "b"), (PartState0("a", "unsigned long"), PartState0("b", "unsigned long")))
    node_sub = make_ur_node("BinaryOperator.Sub", "a - b", ("a", "b"), (PartState0("a", "long"), PartState0("b", "long")))
    for lang in ("python", "c", "rust"):
        c_udiv = autopoly.emit_target_code(node_udiv, lang)["code"]
        c_urem = autopoly.emit_target_code(node_urem, lang)["code"]
        c_sub = autopoly.emit_target_code(node_sub, lang)["code"]
        r_udiv = s64(eval(c_udiv, {"a": -2, "b": 2})) if lang == "python" else (eval_c_expr(c_udiv, -2, 2) if lang == "c" else eval_rust_expr(c_udiv, -2, 2))
        r_urem = s64(eval(c_urem, {"a": -3, "b": 2})) if lang == "python" else (eval_c_expr(c_urem, -3, 2) if lang == "c" else eval_rust_expr(c_urem, -3, 2))
        r_sub = s64(eval(c_sub, {"a": 10, "b": -9223372036854775808})) if lang == "python" else (eval_c_expr(c_sub, 10, -9223372036854775808) if lang == "c" else eval_rust_expr(c_sub, 10, -9223372036854775808))
        assert r_udiv == 0x7FFFFFFFFFFFFFFF, f"UDiv mismatch in {lang}: {r_udiv}"
        assert r_urem == 1, f"URem mismatch in {lang}: {r_urem}"
        assert r_sub == -9223372036854775798, f"Sub mismatch in {lang}: {r_sub}"
    print("  [PASS] Tier 3 Div/UDiv/URem, INT64_MIN % -1, 64-bit precision, and Rust Sub verified across Python, C, and Rust")

    print("\n=== 8. Negative Control: Zero Silent Fallbacks ===")
    unlifted = UniversalRichNode(hiop={"lang": "C", "operator": "+"}, units={}, meaning={})
    try:
        autopoly.emit_target_code(unlifted, "python")
        raise AssertionError("Should have raised ValueError for unlifted node")
    except ValueError as e:
        print(f"  [PASS] Unlifted UR-Node refused: {e}")

    unhandled_f = z3.Function("custom_unhandled_op", z3.BitVecSort(64), z3.BitVecSort(64))
    try:
        translate_z3_to_hiop_primitives(unhandled_f(z3.BitVec("a", 64)), "python")
        raise AssertionError("Should have raised NotImplementedError for unhandled Z3 op")
    except NotImplementedError as e:
        print(f"  [PASS] Unhandled Z3 op refused: {e}")

    print("\n=== 9. Sail Lifter Integrity & URLedger End-to-End Checks ===")
    from PseudoArch.map_LoOp_to_lean.map_sail_to_lean_direct import decode_word, _lifter
    from PseudoArch.map_HiOp_to_unit.lower_HiOp import Word
    from PseudoArch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import Unit
    from PseudoArch.map_unit_to_lean import compose_LoOp_leans
    from PseudoCoup.ledgerer.ur_ledger import ScriptToLedger, LedgerToScript, link_ledgers, eval_ledger

    for bad_w, bad_sz in ((0xFFFFFFFF, 4), (0x0000, 2)):
        try:
            decode_word(bad_w, bad_sz)
            raise AssertionError(f"decode_word(0x{bad_w:x}) should have raised LiftRefused")
        except _lifter.LiftRefused as e:
            print(f"  [PASS] ILLEGAL instruction refused: {e}")

    amo_lean = decode_word(0x06F5352F, 4)
    vset_lean = decode_word(0xC9027057, 4)
    assert amo_lean.constructor == "AMO" and vset_lean.constructor == "VSETIVLI"
    print(f"  [PASS] Atomic & Vector decoded via Sail: {amo_lean.constructor}, {vset_lean.constructor}")

    reloc_unit = Unit(
        symbol="got_reloc",
        words=(Word(0x100, "00000097", "auipc", "ra, 0", ("00000100 R_RISCV_GOT_HI20 ext_global",)),),
        parts=(),
        holds_p=(),
        refusal=None,
    )
    try:
        compose_LoOp_leans(reloc_unit)
        raise AssertionError("compose_LoOp_leans should have raised LiftRefused on R_RISCV_GOT_HI20 ext_global")
    except _lifter.LiftRefused as e:
        print(f"  [PASS] Unlinked relocation refused: {e}")

    abort_call_unit = Unit(
        symbol="abort_call",
        words=(Word(0x100, "00000097", "auipc", "ra, 0", ("00000100 R_RISCV_CALL_PLT abort",)),),
        parts=(),
        holds_p=(),
        refusal=None,
    )
    try:
        compose_LoOp_leans(abort_call_unit)
        raise AssertionError("compose_LoOp_leans should have raised LiftRefused(TRAP_ONLY_UNIT) on R_RISCV_CALL_PLT abort")
    except _lifter.LiftRefused as e:
        assert "TRAP_ONLY_UNIT" in str(e), f"Expected TRAP_ONLY_UNIT, got {e}"
        print(f"  [PASS] Non-returning trap call (abort) refused as TRAP_ONLY_UNIT: {e}")

    node_cond = make_ur_node(
        "ConditionalOperator", "a ? b : c", ("a", "b", "c"),
        (PartState0("a", "long"), PartState0("b", "long"), PartState0("c", "long")),
    )
    r_val_cond = node_cond.meaning["R_val"]
    assert "in_off_16" in r_val_cond and "in_off_8" in r_val_cond, f"Unexpected ConditionalOperator R_val: {r_val_cond}"
    print(f"  [PASS] ConditionalOperator 3-operand R_val: {r_val_cond}")

    cond_part_unit = Unit(
        symbol="cond_part",
        words=(
            Word(0x10, "00000097", "auipc", "ra, 0", ("00000010 R_RISCV_CALL_PLT part_func_0_a",)),
            Word(0x14, "000080e7", "jalr", "ra, 0(ra)", ()),
            Word(0x1A, "c901", "c.beqz", "a0, 0x2a", ()),
            Word(0x1C, "00000097", "auipc", "ra, 0", ("0000001c R_RISCV_CALL_PLT part_func_0_b",)),
            Word(0x20, "000080e7", "jalr", "ra, 0(ra)", ()),
            Word(0x24, "fea43023", "sd", "a0, -0x20(s0)", ()),
            Word(0x28, "a039", "c.j", "0x36", ()),
            Word(0x2A, "00000097", "auipc", "ra, 0", ("0000002a R_RISCV_CALL_PLT part_func_0_c",)),
            Word(0x2E, "000080e7", "jalr", "ra, 0(ra)", ()),
            Word(0x32, "fea43023", "sd", "a0, -0x20(s0)", ()),
            Word(0x36, "fe043503", "ld", "a0, -0x20(s0)", ()),
            Word(0x3A, "ed88", "c.sd", "a0, 0x18(a1)", ()),
        ),
        parts=("a", "b", "c"),
        holds_p=((11, "a1"),),
        refusal=None,
    )
    ul_part = compose_LoOp_leans(cond_part_unit)
    assert str(ul_part.combined_term) == "If(part_a_ret == 0, part_c_ret, part_b_ret)", f"Got: {ul_part.combined_term}"
    print(f"  [PASS] ConditionalOperator part_* return value bound: {ul_part.combined_term}")

    trap_only_unit = Unit("trap_only", (Word(0x0, "0000", "c.unimp", "", ()),), (), (), None)
    try:
        compose_LoOp_leans(trap_only_unit)
        raise AssertionError("trap_only_unit should have raised LiftRefused")
    except _lifter.LiftRefused as e:
        assert "TRAP_ONLY_UNIT" in str(e), f"Expected TRAP_ONLY_UNIT, got {e}"
        print(f"  [PASS] Trap-only unit refused: {e}")

    trapv_add_unit = Unit(
        symbol="trapv_add",
        words=(
            Word(0x00, "4188", "c.lw", "a0, 0x0(a1)", ()),
            Word(0x02, "41d0", "c.lw", "a2, 0x4(a1)", ()),
            Word(0x04, "00c505b3", "add", "a1, a0, a2", ()),
            Word(0x08, "feb43023", "sd", "a1, -0x20(s0)", ()),
            Word(0x0C, "9d31", "c.addw", "a0, a2", ()),
            Word(0x0E, "00b50463", "beq", "a0, a1, 0x16", ()),
            Word(0x12, "a009", "c.j", "0x14", ()),
            Word(0x14, "0000", "c.unimp", "", ()),
            Word(0x16, "fe043503", "ld", "a0, -0x20(s0)", ()),
            Word(0x1E, "c588", "c.sw", "a0, 0x8(a1)", ()),
        ),
        parts=("a", "b"),
        holds_p=((0, "a1"), (9, "a1")),
        refusal=None,
    )
    ul_trapv = compose_LoOp_leans(trapv_add_unit)
    assert len(ul_trapv.pieces) == 2 and ul_trapv.pieces[0].range_term is not None and ul_trapv.pieces[1].range_term is None
    print(f"  [PASS] -ftrapv Add lifted to (D_ok, R_ok) + (D_trap, None): D_ok={ul_trapv.pieces[0].domain}, R_ok={ul_trapv.pieces[0].range_term}")

    lcpi_unit = Unit(
        symbol="op_467",
        words=(
            Word(0x00, "00000597", "auipc", "a1, 0x0", ("R_RISCV_PCREL_HI20 .LCPI104_0",)),
            Word(0x04, "00058593", "addi", "a1, a1, 0x0", ("R_RISCV_PCREL_LO12_I .Lpcrel_hi1",)),
            Word(0x08, "00059787", "flh", "fa5, 0x0(a1)", ()),
            Word(0x0C, "00f51027", "fsh", "fa5, 0x0(a0)", ()),
        ),
        parts=(),
        holds_p=((0, "a0"),),
        refusal=None,
    )
    ul_lcpi = compose_LoOp_leans(lcpi_unit)
    assert ul_lcpi.ext_calls == () and ul_lcpi.combined_term is not None and ul_lcpi.combined_term.as_long() == 0x7C00, f"Got: {ul_lcpi}"
    print(f"  [PASS] .LCPI* .rodata constant-pool load resolved to exact 0x{ul_lcpi.combined_term.as_long():04x}")

    addtf3_unit = Unit(
        symbol="op_addtf3",
        words=(
            Word(0x00, "6188", "c.ld", "a0, 0x0(a1)", ()),
            Word(0x02, "6990", "c.ld", "a2, 0x10(a1)", ()),
            Word(0x04, "6d94", "c.ld", "a3, 0x18(a1)", ()),
            Word(0x06, "658c", "c.ld", "a1, 0x8(a1)", ()),
            Word(0x08, "00000097", "auipc", "ra, 0x0", ("R_RISCV_CALL_PLT __addtf3",)),
            Word(0x0C, "000080e7", "jalr", "ra, 0x0(ra)", ()),
            Word(0x10, "f188", "c.sd", "a0, 0x20(a1)", ()),
        ),
        parts=("a", "b"),
        holds_p=((0, "a1"), (6, "a1")),
        refusal=None,
    )
    ul_addtf3 = compose_LoOp_leans(addtf3_unit)
    assert ul_addtf3.ext_calls == ("__addtf3",) and ul_addtf3.pieces[0].part_calls == ()
    assert all(f"in_off_{off}" in str(ul_addtf3.combined_term) for off in (0, 8, 16, 24)), f"Got: {ul_addtf3.combined_term}"
    print(f"  [PASS] R_RISCV_CALL_PLT __addtf3 parameterized over a0..a3: {ul_addtf3.combined_term}")

    c_src = "int32_t step1(int64_t x, int64_t y) {\n    int64_t z = x * y + 10;\n    return z;\n}\n"
    rs_src = "fn main_fn(a: i64, b: i64) -> i64 {\n    let w: i64 = step1(a, b);\n    if w > 0 {\n        return w;\n    } else {\n        return -w;\n    }\n}\n"
    linked = link_ledgers([ScriptToLedger.parse(c_src, "c"), ScriptToLedger.parse(rs_src, "rust")])
    assert eval_ledger(linked, {"a": 3, "b": -4}) == 2
    assert eval_ledger(linked, {"a": 3, "b": 4}) == 22
    for lang in ("c", "python", "rust"):
        emitted = LedgerToScript.emit(linked, lang)
        assert "step1" in emitted and "main_fn" in emitted
    print("  [PASS] ScriptToLedger -> link_ledgers -> LedgerToScript -> eval_ledger verified")

    print("\nALL PSEUDOARCH -> AUTOPOLY CHECKS PASSED.")


if __name__ == "__main__":
    main()
