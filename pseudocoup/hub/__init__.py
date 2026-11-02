"""hub -- The Hub (`CORE_0_0_0_2_hub.md` & `SUPPORT_BRAINSTORM_hub.md`).

A modified Python language that holds AutoPoly:
  - Supports qualified cross-language operators (`y = (m C.* x) C.+ b`, `a Go./ b`, `a Rust.% b`, `a Java.>>> b`, `a C++.<=> b`, `a Python.// b`)
  - Groups UniversalRichNodes into Equivalence Modes by canonical Unit / (D_ok, D_trap, R_val)
  - Dispatches execution and target-language code emission through AutoPoly
"""
from __future__ import annotations
import re
from typing import Any

from ..ledgerer.universal_rich_node import UniversalRichNode
from .autopoly import AutoPoly, EquivalenceProver
from .control_flow import ComplexHolder, MultiBodyEngine
from .unit_vm import BreakSignal, ContinueSignal, ReturnSignal, RiscvUnitVM


class Hub:
    """The Hub: holds AutoPoly, UR-Node registry, Equivalence Mode index, UnitVM, and MultiBodyEngine."""

    def __init__(self) -> None:
        self.autopoly = AutoPoly()
        self.vm = RiscvUnitVM()
        self.multi_body = MultiBodyEngine()
        self.nodes: dict[str, UniversalRichNode] = {}
        self.modes: dict[tuple[str, str, str], list[str]] = {}
        self._register_core_vocabulary()

    def register(self, node: UniversalRichNode) -> None:
        self.nodes[node.qualified_name] = node
        key = node.mode_key()
        self.modes.setdefault(key, []).append(node.qualified_name)

    def _register_core_vocabulary(self) -> None:
        specs = [
            ("C", "+", ("int64_t", "int64_t"), ["add"], "True", "False", "bvadd"),
            ("C++", "+", ("int64_t", "int64_t"), ["add"], "True", "False", "bvadd"),
            ("Go", "+", ("int64", "int64"), ["add"], "True", "False", "bvadd"),
            ("Rust", "wrapping_add", ("i64", "i64"), ["add"], "True", "False", "bvadd"),
            ("Java", "+", ("long", "long"), ["add"], "True", "False", "bvadd"),
            ("C", "*", ("int64_t", "int64_t"), ["mul"], "True", "False", "bvmul"),
            ("Go", "*", ("int64", "int64"), ["mul"], "True", "False", "bvmul"),
            ("Java", "*", ("long", "long"), ["mul"], "True", "False", "bvmul"),
            ("C", "/", ("int64_t", "int64_t"), ["div"], "b!=0 && !(a==MIN&&b==-1)", "b==0 || (a==MIN&&b==-1)", "c_sdiv"),
            ("Go", "/", ("int64", "int64"), ["beq", "addi", "beq", "div"], "b!=0", "b==0", "go_java_sdiv"),
            ("Java", "/", ("long", "long"), ["beq", "addi", "beq", "div"], "b!=0", "b==0", "go_java_sdiv"),
            ("Rust", "%", ("i64", "i64"), ["beqz", "li", "beq", "rem"], "b!=0 && !(a==MIN&&b==-1)", "b==0 || (a==MIN&&b==-1)", "rust_srem"),
            ("Python", "//", ("int", "int"), ["beq", "div", "rem", "xor", "bltz", "addi"], "b!=0", "b==0", "python_floordiv"),
            ("Go", "<<", ("int64", "uint64"), ["sltiu", "sll", "czero.nez"], "True", "False", "go_shl_64"),
            ("Java", ">>>", ("long", "int"), ["srl"], "True", "False", "bvlshr_mask63"),
            ("C++", "<=>", ("int64_t", "int64_t"), ["slt", "slt", "sub"], "True", "False", "spaceship_lcmp"),
            ("Java", "lcmp", ("long", "long"), ["slt", "slt", "sub"], "True", "False", "spaceship_lcmp"),
            ("Ruby", "<=>", ("Integer", "Integer"), ["slt", "slt", "sub"], "True", "False", "spaceship_lcmp"),
            ("PHP", "<=>", ("int", "int"), ["slt", "slt", "sub"], "True", "False", "spaceship_lcmp"),
            ("TypeScript", ">>>", ("int32", "int32"), ["srlw"], "True", "False", "ts_ushr32"),
            ("C#", ">>>", ("long", "int"), ["srl"], "True", "False", "bvlshr_mask63"),
            ("Dart", "%", ("int", "int"), ["rem", "bltz", "add"], "b!=0", "b==0", "dart_euclid_mod"),
            ("Swift", "&+", ("Int", "Int"), ["add"], "True", "False", "bvadd"),
            ("Swift", "&*", ("Int", "Int"), ["mul"], "True", "False", "bvmul"),
        ]
        for lang, op, holders, lo_ops, dok, dtrap, rkind in specs:
            self.register(UniversalRichNode(
                hiop={"lang": lang, "operator": op, "holders": holders},
                units={"riscv64": [{"opcode": m} for m in lo_ops]},
                meaning={"D_ok": dok, "D_trap": dtrap, "R_val": rkind, "R_kind": rkind},
            ))

    def eval_node(self, qualified_op: str, a: int, b: int = 0) -> int | str:
        """Execute a UR-Node's exact RISC-V Unit semantics on 64-bit integer holders."""
        node = self.nodes[qualified_op]
        r_kind = node.meaning["R_kind"]
        MASK = (1 << 64) - 1
        MIN64 = -(1 << 63)

        def to_s64(u: int) -> int:
            u &= MASK
            return u - (1 << 64) if u >= (1 << 63) else u

        if r_kind == "bvadd":
            return to_s64((a & MASK) + (b & MASK))
        if r_kind == "bvmul":
            return to_s64((a & MASK) * (b & MASK))
        if r_kind == "bvlshr_mask63":
            return to_s64((a & MASK) >> (b & 63))
        if r_kind == "go_shl_64":
            return to_s64((a & MASK) << b) if (0 <= b < 64) else 0
        if r_kind == "c_sdiv":
            if b == 0 or (a == MIN64 and b == -1):
                return "TRAP:UB_or_SIGFPE"
            return int(a / b)
        if r_kind == "go_java_sdiv":
            if b == 0:
                return "PANIC:DivisionByZero"
            return MIN64 if (a == MIN64 and b == -1) else int(a / b)
        if r_kind == "rust_srem":
            if b == 0:
                return "PANIC:DivisionByZero"
            if a == MIN64 and b == -1:
                return "PANIC:SignedOverflow"
            return a - int(a / b) * b
        if r_kind == "python_floordiv":
            if b == 0:
                return "PANIC:ZeroDivisionError"
            return a // b
        if r_kind == "spaceship_lcmp":
            return 1 if a > b else (-1 if a < b else 0)
        if r_kind == "ts_ushr32":
            return (a & 0xFFFFFFFF) >> (b & 31)
        if r_kind == "dart_euclid_mod":
            if b == 0:
                return "PANIC:IntegerDivisionByZeroException"
            r = a - int(a / b) * b
            return r + abs(b) if r < 0 else r
        raise KeyError(qualified_op)

    LANG_PATTERN = r"(?:C\+\+|C#|C|Go|Rust|Python|Java|TypeScript|Ruby|PHP|Dart|Swift)"

    def eval_qualified_expr(self, expr: str, env: dict[str, int]) -> int | str:
        """Evaluate a Hub expression with qualified operators (`y = (m C.* x) C.+ b`)."""
        work = dict(env)
        pat = re.compile(rf"\(\s*([A-Za-z0-9_]+)\s+({self.LANG_PATTERN})\.(\S+)\s+([A-Za-z0-9_]+)\s*\)")
        while True:
            m = pat.search(expr)
            if not m:
                break
            lhs, lang, op, rhs = m.groups()
            res = self.eval_node(f"{lang}.{op}", work[lhs], work[rhs])
            tmp = f"__hub_t{len(work)}"
            work[tmp] = res
            expr = expr[:m.start()] + tmp + expr[m.end():]
        m2 = re.match(rf"^\s*([A-Za-z0-9_]+)\s+({self.LANG_PATTERN})\.(\S+)\s+([A-Za-z0-9_]+)\s*$", expr)
        if m2:
            lhs, lang, op, rhs = m2.groups()
            return self.eval_node(f"{lang}.{op}", work[lhs], work[rhs])
        return work.get(expr.strip(), expr)

    def transpile_qualified_op(self, qualified_op: str, target_lang: str, lhs: str = "a", rhs: str = "b") -> dict[str, Any]:
        """Transpile `qualified_op` (e.g. `Go./`, `Java.>>>`) into `target_lang` via AutoPoly."""
        node = self.nodes[qualified_op]
        return self.autopoly.emit_target_code(node, target_lang, lhs, rhs)

    def load_lowered_vocabularies(self, out_dir: str | None = None) -> dict[str, int]:
        """Ingest lowered RISC-V Units from disk into UniversalRichNodes indexed by mode."""
        import gzip
        import json
        from pathlib import Path

        if out_dir is None:
            pkg_dir = Path(__file__).resolve().parents[1] / "pseudoarch" / "map_HiOp_to_unit" / "lowered_units"
            hq_dir = Path(__file__).resolve().parents[3] / "Research" / "lower_HiOp" / "out"
            base = pkg_dir if pkg_dir.exists() else hq_dir
        else:
            base = Path(out_dir)
        sources = [
            ("C", base / "gnu_c_first_of_each.jsonl.gz"),
            ("ClangOther", base / "clang_other_langs_all.jsonl.gz"),
            ("Go", base / "go_all.jsonl.gz"),
            ("Rust", base / "rust_all.jsonl.gz"),
            ("Python", base / "python_first_of_each.jsonl.gz"),
            ("Java", base / "java_all.jsonl.gz"),
            ("TypeScript", base / "typescript_all.jsonl.gz"),
            ("C#", base / "csharp_all.jsonl.gz"),
            ("Ruby", base / "ruby_all.jsonl.gz"),
            ("PHP", base / "php_all.jsonl.gz"),
            ("Dart", base / "dart_all.jsonl.gz"),
            ("Swift", base / "swift_all.jsonl.gz"),
        ]
        counts: dict[str, int] = {}
        for default_lang, path in sources:
            if not path.exists():
                continue
            loaded = 0
            with gzip.open(path, "rt") as gz:
                for line in gz:
                    rec = json.loads(line)
                    words = rec.get("words") or []
                    unit_idxs = rec.get("unit") or list(range(len(words)))
                    lo_ops = [words[i][2] for i in unit_idxs if isinstance(i, int) and i < len(words) and len(words[i]) > 2]
                    if not lo_ops:
                        continue
                    lang = rec.get("dialect") or default_lang
                    op = rec.get("operator") or rec.get("op_key") or rec.get("op") or ""
                    raw_h = rec.get("holders") or ()
                    holders = tuple(h[1] if isinstance(h, list) and len(h) > 1 else str(h) for h in raw_h)
                    sig = f"{lang}.{op}[{','.join(holders)}]"
                    WRAPPER_INSNS = {
                        "ld", "c.ld", "lw", "c.lw", "lwu", "lh", "lhu", "lb", "lbu", "flw", "fld", "c.fld",
                        "sd", "c.sd", "sw", "c.sw", "sh", "sb", "fsw", "fsd", "c.fsd",
                        "c.sdsp", "c.ldsp", "c.swsp", "c.lwsp", "c.addi4spn", "c.addi16sp", "c.jr", "ret", "c.mv", "mv",
                    }
                    UNCOMPRESS = {
                        "c.add": "add", "c.addw": "addw", "c.sub": "sub", "c.subw": "subw",
                        "c.and": "and", "c.or": "or", "c.xor": "xor", "c.slli": "slli",
                        "c.srli": "srli", "c.srai": "srai", "c.li": "li", "c.lui": "lui",
                        "c.beqz": "beqz", "c.bnez": "bnez", "c.j": "j",
                    }
                    core_ops = []
                    for i in unit_idxs:
                        if not (isinstance(i, int) and i < len(words) and len(words[i]) > 3):
                            continue
                        mnem, ops_str = words[i][2], str(words[i][3])
                        if mnem in WRAPPER_INSNS:
                            continue
                        if mnem in ("addi", "c.addi") and ("sp" in ops_str or "s0" in ops_str):
                            continue
                        core_ops.append(UNCOMPRESS.get(mnem, mnem))
                    if not core_ops:
                        core_ops = [UNCOMPRESS.get(m, m) for m in lo_ops]
                    canon_str = ";".join(core_ops)
                    node = UniversalRichNode(
                        hiop={"lang": lang, "operator": op, "holders": holders, "template": rec.get("template", "")},
                        units={"riscv64": [{"opcode": m} for m in lo_ops]},
                        meaning={"D_ok": "unit_defined", "D_trap": "unit_trap", "R_val": canon_str, "R_kind": canon_str},
                    )
                    self.nodes[sig] = node
                    self.modes.setdefault(node.mode_key(), []).append(sig)
                    loaded += 1
            counts[default_lang] = loaded
        return counts

    def transpile_hub_expr(self, expr: str, target_lang: str) -> dict[str, Any]:
        """Transpile a Hub expression with qualified operators (`(m C.* x) C.+ b`) into `target_lang`."""
        steps: list[dict[str, Any]] = []
        subs: dict[str, str] = {}
        work_expr = expr
        pat = re.compile(r"\(\s*([A-Za-z0-9_]+)\s+(C\+\+|C|Go|Rust|Python|Java)\.(\S+)\s+([A-Za-z0-9_]+)\s*\)")
        while True:
            m = pat.search(work_expr)
            if not m:
                break
            lhs, lang, op, rhs = m.groups()
            qop = f"{lang}.{op}"
            lhs_code = subs.get(lhs, lhs)
            rhs_code = subs.get(rhs, rhs)
            emitted = self.transpile_qualified_op(qop, target_lang, lhs_code, rhs_code)
            tok = f"__hub_s{len(subs)}"
            subs[tok] = emitted["code"]
            steps.append({"ur_node": qop, "tier": emitted["tier"], "code": emitted["code"]})
            work_expr = work_expr[:m.start()] + tok + work_expr[m.end():]
        m2 = re.match(r"^\s*([A-Za-z0-9_]+)\s+(C\+\+|C|Go|Rust|Python|Java)\.(\S+)\s+([A-Za-z0-9_]+)\s*$", work_expr)
        if m2:
            lhs, lang, op, rhs = m2.groups()
            qop = f"{lang}.{op}"
            lhs_code = subs.get(lhs, lhs)
            rhs_code = subs.get(rhs, rhs)
            emitted = self.transpile_qualified_op(qop, target_lang, lhs_code, rhs_code)
            steps.append({"ur_node": qop, "tier": emitted["tier"], "code": emitted["code"]})
            work_expr = emitted["code"]
        else:
            work_expr = subs.get(work_expr.strip(), work_expr)
        return {"target_lang": target_lang, "source_expr": expr, "transpiled_code": work_expr, "steps": steps}
