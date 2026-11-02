"""control_flow -- Multi-body Control-Flow UR-Nodes & Complex Holders in the Hub.

Implements `SUPPORT_BRAINSTORM_hub.md` §2 (rows 19-39):
  - Multi-body HiOps (`HiOp[0](cond)`, `HiOp[1]`, `HiOp[2]`):
      `if (a) b;`, `if (a) b; else c;`, `while (a) b;`, `do b; while (a);`,
      `for (init; cond; step) body;`, `switch (a) { cases }`,
      short-circuit `a && b`, `a || b`, ternary `a ? b : c`, `a ?: b`,
      and dependent control-flow `break;`, `continue;`, `return a;`.
  - Complex Holders (`StructHolder`, `ArrayHolder`): compositions of simple
    machine-word holders backed by the Hub's RISC-V memory layout.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

from .unit_vm import BreakSignal, ContinueSignal, ReturnSignal


@dataclass
class ComplexHolder:
    """Composition of simple 64-bit machine-word holders (`SUPPORT_BRAINSTORM_hub.md` row 19)."""
    kind: str  # "struct" | "array"
    fields: dict[str, int] = field(default_factory=dict)
    elements: list[int] = field(default_factory=list)

    def get(self, key: str | int) -> int:
        if self.kind == "struct":
            return int(self.fields[str(key)])
        return int(self.elements[int(key)])

    def set(self, key: str | int, val: int) -> int:
        if self.kind == "struct":
            self.fields[str(key)] = int(val)
        else:
            self.elements[int(key)] = int(val)
        return int(val)

    def to_words(self) -> list[int]:
        if self.kind == "struct":
            return [int(v) for _k, v in sorted(self.fields.items())]
        return [int(x) for x in self.elements]


class MultiBodyEngine:
    """Executes and transpiles multi-body & control-flow UR-Nodes across languages."""

    @staticmethod
    def eval_short_circuit_and(part_a: Callable[[], int], part_b: Callable[[], int]) -> int:
        """`a && b`: evaluates `part_b` ONLY when `part_a() != 0`."""
        return 1 if (part_a() != 0 and part_b() != 0) else 0

    @staticmethod
    def eval_short_circuit_or(part_a: Callable[[], int], part_b: Callable[[], int]) -> int:
        """`a || b`: evaluates `part_b` ONLY when `part_a() == 0`."""
        return 1 if (part_a() != 0 or part_b() != 0) else 0

    @staticmethod
    def eval_ternary(part_a: Callable[[], int], part_b: Callable[[], int], part_c: Callable[[], int]) -> int:
        """`a ? b : c`: evaluates `part_b` if `part_a() != 0`, else `part_c`."""
        return part_b() if (part_a() != 0) else part_c()

    @staticmethod
    def exec_if_else(part_a: Callable[[], int], part_b: Callable[[], Any], part_c: Callable[[], Any] | None = None) -> None:
        """`if (a) b; else c;` (`HiOp` with 1 or 2 bodies)."""
        t = (part_a() != 0)  # Kept test (`SUPPORT_BRAINSTORM_hub.md` row 28)
        if t:
            part_b()
        elif part_c is not None:
            part_c()

    @staticmethod
    def exec_while(part_a: Callable[[], int], part_b: Callable[[], Any], max_iters: int = 10000) -> int:
        """`while (a) b;` with dependent `break;` and `continue;` support."""
        iters = 0
        while iters < max_iters and part_a() != 0:
            iters += 1
            try:
                part_b()
            except ContinueSignal:
                continue
            except BreakSignal:
                break
        return iters

    @staticmethod
    def exec_for(
        init_fn: Callable[[], Any],
        cond_a: Callable[[], int],
        step_b: Callable[[], Any],
        body_c: Callable[[], Any],
        max_iters: int = 10000,
    ) -> int:
        """`for (init; a; b) c;` with dependent `break;` and `continue;` support."""
        init_fn()
        iters = 0
        while iters < max_iters and cond_a() != 0:
            iters += 1
            try:
                body_c()
            except ContinueSignal:
                pass
            except BreakSignal:
                break
            step_b()
        return iters

    @staticmethod
    def exec_switch(part_a: Callable[[], int], cases: dict[int, Callable[[], Any]], default_fn: Callable[[], Any] | None = None) -> None:
        """`switch (a) { case k: ... }` with dependent `break;` support."""
        val = part_a()
        target = cases.get(val, default_fn)
        if target is not None:
            try:
                target()
            except BreakSignal:
                pass

    @staticmethod
    def transpile_multi_body(construct: str, target_lang: str, parts: list[str]) -> str:
        """Transpile a multi-body / control-flow UR-Node into `target_lang`."""
        t = target_lang.lower()
        if construct == "ternary":
            a, b, c = parts[0], parts[1], parts[2]
            if t == "python":
                return f"({b} if ({a} != 0) else {c})"
            if t == "rust":
                return f"(if ({a} != 0) {{ {b} }} else {{ {c} }})"
            if t == "go":
                return f"ite(({a} != 0), {b}, {c})"
            return f"(({a} != 0) ? {b} : {c})"
        if construct == "land":
            a, b = parts[0], parts[1]
            if t == "python":
                return f"(1 if (({a} != 0) and ({b} != 0)) else 0)"
            if t in ("rust", "go", "java"):
                return f"(if (({a} != 0) && ({b} != 0)) {{ 1 }} else {{ 0 }})" if t == "rust" else f"((({a} != 0) && ({b} != 0)) ? 1 : 0)"
            return f"(({a}) && ({b}))"
        if construct == "lor":
            a, b = parts[0], parts[1]
            if t == "python":
                return f"(1 if (({a} != 0) or ({b} != 0)) else 0)"
            if t in ("rust", "go", "java"):
                return f"(if (({a} != 0) || ({b} != 0)) {{ 1 }} else {{ 0 }})" if t == "rust" else f"((({a} != 0) || ({b} != 0)) ? 1 : 0)"
            return f"(({a}) || ({b}))"
        if construct == "if_else":
            a, b = parts[0], parts[1]
            c = parts[2] if len(parts) > 2 else None
            if t == "python":
                return f"if ({a} != 0):\n    {b}" + (f"\nelse:\n    {c}" if c else "")
            if t in ("rust", "go"):
                return f"if ({a} != 0) {{ {b} }}" + (f" else {{ {c} }}" if c else "")
            return f"if ({a} != 0) {{ {b}; }}" + (f" else {{ {c}; }}" if c else "")
        if construct == "while":
            a, b = parts[0], parts[1]
            if t == "python":
                return f"while ({a} != 0):\n    {b}"
            if t == "go":
                return f"for ({a} != 0) {{ {b} }}"
            return f"while ({a} != 0) {{ {b} }}"
        if construct in ("break", "continue"):
            return construct if t in ("python", "go") else f"{construct};"
        raise ValueError(f"Unknown multi-body construct: {construct}")
