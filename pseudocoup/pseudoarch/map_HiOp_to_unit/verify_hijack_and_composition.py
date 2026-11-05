"""End-to-end verification of:
1. Direct lowerer hijacking (`map_state_info_0_to_unit`) across a 16-HiOp GNU C
   sample on riscv64, x86_64, and aarch64.
2. Abstract token stack compositional proof (`while` -> `while + if` ->
   `while + if + break` -> `while + if + continue` -> nested `while + while + if + break`)
   across riscv64, x86_64, and aarch64.
"""

import subprocess
import sys
import tempfile

import pathlib as _pl; sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))

from map_HiOp_to_unit import map_state_info_0_to_unit
from map_HiOp_to_unit.lower_HiOp import read_words_at_symbol, MachineCode
from map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import extract_unit
from map_HiOp_to_unit.lower_HiOp.hijack_lowerer import HIJACK_CLANG, ARCH_TRIPLE
from map_HiOp_to_unit.model_lang_parts.context.entry_context import (
    Operator,
    PartState0,
    StateInfo0,
    enclosing_scope_for_operator,
)


def build_samples(target: str):
    specs = [
        ("BinaryOperator.Add", "a + b", ("a", "b"), (PartState0("a", "int"), PartState0("b", "int"))),
        ("BinaryOperator.Mul", "a * b", ("a", "b"), (PartState0("a", "double"), PartState0("b", "double"))),
        ("BinaryOperator.Shl", "a << b", ("a", "b"), (PartState0("a", "int", place="bit-field"), PartState0("b", "int"))),
        ("UnaryOperator.Not", "~a", ("a",), (PartState0("a", "v4si"),)),
        ("IfStmt", "if (a) b;", ("a", "b"), (PartState0("a", "int"),)),
        ("IfStmt.Else", "if (a) b; else c;", ("a", "b", "c"), (PartState0("a", "int"),)),
        ("WhileStmt", "while (a) b;", ("a", "b"), (PartState0("a", "int"),)),
        ("DoStmt", "do a; while (b);", ("a", "b"), (PartState0("b", "int"),)),
        ("ForStmt", "for (a; b; c) d;", ("a", "b", "c", "d"), (PartState0("b", "int"),)),
        ("SwitchStmt", "switch (a) b;", ("a", "b"), (PartState0("a", "int"),)),
        ("CaseStmt", "case a: b;", ("a", "b"), (PartState0("a", "int"),)),
        ("DefaultStmt", "default: a;", ("a",), ()),
        ("BreakStmt", "break;", (), ()),
        ("ContinueStmt", "continue;", (), ()),
        ("GotoStmt", "goto m;", ("m",), ()),
        ("IndirectGotoStmt", "goto *a;", ("a",), (PartState0("a", "void *"),)),
        ("ReturnStmt", "return a;", ("a",), (PartState0("a", "int"),)),
        ("AddrLabelExpr", "&&m", ("m",), ()),
        ("CallExpr.BI__builtin_clz", "__builtin_clz(a)", ("a",), (PartState0("a", "unsigned int"),)),
    ]
    out = []
    for name, spelling, operands, parts in specs:
        op = Operator(name=name, spelling=spelling, operands=operands)
        scope = enclosing_scope_for_operator(op)
        out.append(StateInfo0("c", op, parts, target=target, enclosing_scope=scope))
    return out


def lower_explicit_snippet(body_c: str, target: str):
    """Compile an explicit bracketed snippet at -O0 without depth==2 stubbing,
    so we can compare the compiler's multi-level lowering against composing the
    hijacked single-HiOp units."""
    triple = ARCH_TRIPLE[target]
    src = (
        "void __hiop_unit_begin(void);\n"
        "void __hiop_unit_end(void);\n"
        "void part_b(void);\n"
        "struct P { int a; int b; int c; int d; };\n"
        "void op_comp(struct P *p) {\n"
        "\t__hiop_unit_begin();\n"
        f"\t{body_c}\n"
        "\t__hiop_unit_end();\n"
        "}\n"
    )
    with tempfile.TemporaryDirectory() as d:
        c_path = f"{d}/comp.c"
        o_path = f"{d}/comp.o"
        with open(c_path, "w") as f:
            f.write(src)
        cmd = [
            "clang-21", "-x", "c", "-std=gnu17", "-O0", "-g",
            "-mllvm", "-fast-isel=0", f"--target={triple}",
            "-nostdlibinc",
        ]
        if target == "riscv64":
            cmd.append("-mno-relax")
        cmd.extend(["-c", c_path, "-o", o_path])
        subprocess.run(cmd, check=True)
        lo = read_words_at_symbol(MachineCode(o_path, None), "op_comp")
        return extract_unit(lo, None, machine=target)


def fmt_unit(unit):
    return [
        f"{w.arch_opcode} {w.operands}".strip()
        + (f" [{', '.join(w.relocations)}]" if w.relocations else "")
        for w in unit.words
    ]


def compose_units_opcodes(parent_opcodes, child_opcodes, machine: str, child_is_terminator: bool = False):
    """Substitute `child_opcodes` into `parent_opcodes` at the `part_b` call slot."""
    call_len = 2 if machine == "riscv64" else 1
    call_op = "auipc" if machine == "riscv64" else ("callq" if machine == "x86_64" else "bl")
    idx = parent_opcodes.index(call_op)
    suffix = parent_opcodes[idx + call_len :]
    if child_is_terminator and suffix:
        suffix = suffix[1:]
    return parent_opcodes[:idx] + child_opcodes + suffix


def main():
    hijacked_by_target = {}
    for target in ("riscv64", "x86_64", "aarch64"):
        samples = build_samples(target)
        hijacked_by_target[target] = {}
        print(f"=== PART A: 19 SAMPLE HIOPS ON {target} ===")
        for idx, s0 in enumerate(samples):
            mapped = map_state_info_0_to_unit(s0, key=f"{target}_{idx}")
            u = mapped.unit
            assert u.refusal is None, f"{s0.operator.name} refused on {target}: {u.refusal}"
            assert len(u.words) > 0, f"{s0.operator.name} produced 0 words on {target}"
            hijacked_by_target[target][s0.operator.name] = u
            print(
                f"  [{target}] {s0.operator.name:28s} ({s0.operator.spelling:18s}) "
                f"scope={str(s0.enclosing_scope):9s} -> {len(u.words):2d} words, "
                f"parts={u.parts}, holds_p={u.holds_p} | {'; '.join(fmt_unit(u)[:4])}"
            )

    print("\n=== PART B: COMPOSITIONAL PROGRESSION (WHILE + IF + BREAK/CONTINUE) ===")
    steps = [
        ("Step 0: while (a) P_1", "while (p->a) part_b();"),
        ("Step 1: while (a) { if (b) P_2 }", "while (p->a) { if (p->b) part_b(); }"),
        ("Step 2a: while (a) { if (b) break }", "while (p->a) { if (p->b) break; }"),
        ("Step 2b: while (a) { if (b) continue }", "while (p->a) { if (p->b) continue; }"),
        ("Step 3: while (a) { while (c) { if (b) break } if (d) break }",
         "while (p->a) { while (p->c) { if (p->b) break; } if (p->d) break; }"),
    ]
    for target in ("riscv64", "x86_64", "aarch64"):
        print(f"\n--- Target: {target} ---")
        w_ops = [w.arch_opcode for w in hijacked_by_target[target]["WhileStmt"].words]
        if_ops = [w.arch_opcode for w in hijacked_by_target[target]["IfStmt"].words]
        brk_ops = [w.arch_opcode for w in hijacked_by_target[target]["BreakStmt"].words]
        cnt_ops = [w.arch_opcode for w in hijacked_by_target[target]["ContinueStmt"].words]

        if_break_ops = compose_units_opcodes(if_ops, brk_ops, target, child_is_terminator=True)
        if_cont_ops = compose_units_opcodes(if_ops, cnt_ops, target, child_is_terminator=True)
        expected_opcodes = {
            "Step 0: while (a) P_1": w_ops,
            "Step 1: while (a) { if (b) P_2 }": compose_units_opcodes(w_ops, if_ops, target),
            "Step 2a: while (a) { if (b) break }": compose_units_opcodes(w_ops, if_break_ops, target),
            "Step 2b: while (a) { if (b) continue }": compose_units_opcodes(w_ops, if_cont_ops, target),
            "Step 3: while (a) { while (c) { if (b) break } if (d) break }": compose_units_opcodes(
                w_ops,
                compose_units_opcodes(w_ops, if_break_ops, target) + if_break_ops,
                target,
            ),
        }
        for label, code in steps:
            u = lower_explicit_snippet(code, target)
            actual_ops = [w.arch_opcode for w in u.words]
            assert actual_ops == expected_opcodes[label], (
                f"Composition mismatch on {target} {label}:\n"
                f"  actual:   {actual_ops}\n"
                f"  expected: {expected_opcodes[label]}"
            )
            print(f"  {label}: ({len(u.words)} words, holds_p={u.holds_p}) [EXACT COMPOSITION MATCH]")
            for idx, w_str in enumerate(fmt_unit(u)):
                print(f"    {idx:2d}: {w_str}")


if __name__ == "__main__":
    main()
