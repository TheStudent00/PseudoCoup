"""hub -- The Hub (`CORE_0_0_0_2_hub.md` & `SUPPORT_BRAINSTORM_hub.md`).

A modified Python language that holds AutoPoly:
  - Supports qualified cross-language operators across all 12 languages (`y = (m C.* x) C.+ b`,
    `a Go./ b`, `a Rust.% b`, `a Java.>>> b`, `a C++.<=> b`, `a Python.// b`, `a TypeScript.>>> b`,
    `a C#.>>> b`, `a Ruby.+ b`, `a PHP.+ b`, `a Dart.>>> b`, `a Swift.&+ b`, `C.?:(cond, a, b)`)
  - Groups UniversalRichNodes into Equivalence Modes by canonical Unit and `(D_ok, D_trap, R_val)`
  - Dispatches execution (including whole-lowered `compiler-rt` and IEEE-754 FPU) and
    target-language code emission through AutoPoly
"""
from __future__ import annotations

import math
import re
import struct
from typing import Any

import z3

from ..ledgerer.universal_rich_node import UniversalRichNode
from .autopoly import AutoPoly, EquivalenceProver
from .autopoly.compiler_rt_lifter import eval_compiler_rt_routine
from .autopoly.polyfill import HIOP_PRIMITIVES, normalize_target_lang
from .control_flow import ComplexHolder, MultiBodyEngine
from .unit_vm import BreakSignal, ContinueSignal, ReturnSignal, RiscvUnitVM


_GLOBAL_UNIT_LEAN_CACHE: dict[tuple, Any] = {}
_MASK64 = (1 << 64) - 1


def _u64_to_f64(u: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", int(u) & _MASK64))[0]


def _f64_to_u64(f: float) -> int:
    if math.isnan(f):
        return 0x7FF8000000000000
    return struct.unpack("<Q", struct.pack("<d", float(f)))[0]


def _s64(u: int) -> int:
    u &= _MASK64
    return u - (1 << 64) if u >= (1 << 63) else u


class _HubEvalGlobals(dict):
    """Execution globals for `Hub.eval_node` providing IEEE-754 FPU helpers and
    on-demand whole-lowered `compiler-rt` routine execution via `eval_compiler_rt_routine`."""

    def __init__(self) -> None:
        super().__init__(
            {
                "__builtins__": {"int": int, "abs": abs},
                "int": int,
                "abs": abs,
                "f64_add": lambda a, b: _f64_to_u64(_u64_to_f64(a) + _u64_to_f64(b)),
                "f64_sub": lambda a, b: _f64_to_u64(_u64_to_f64(a) - _u64_to_f64(b)),
                "f64_mul": lambda a, b: _f64_to_u64(_u64_to_f64(a) * _u64_to_f64(b)),
                "f64_div": lambda a, b: _f64_to_u64(
                    _u64_to_f64(a) / _u64_to_f64(b) if _u64_to_f64(b) != 0.0 else float("nan")
                ),
                "f64_sqrt": lambda a: _f64_to_u64(
                    math.sqrt(_u64_to_f64(a)) if _u64_to_f64(a) >= 0.0 else float("nan")
                ),
                "f64_eq": lambda a, b: int(_u64_to_f64(a) == _u64_to_f64(b)),
                "f64_lt": lambda a, b: int(_u64_to_f64(a) < _u64_to_f64(b)),
                "f64_le": lambda a, b: int(_u64_to_f64(a) <= _u64_to_f64(b)),
                "f64_gt": lambda a, b: int(_u64_to_f64(a) > _u64_to_f64(b)),
                "f64_ge": lambda a, b: int(_u64_to_f64(a) >= _u64_to_f64(b)),
                "fcvt_to_bv64": lambda rm, x: (int(_u64_to_f64(x)) & _MASK64),
                "memcpy_bytes": lambda dst, src, n=8: int(src) & _MASK64,
            }
        )

    def __missing__(self, key: str) -> Any:
        if key.startswith("compiler_rt_"):
            rest = key[len("compiler_rt_") :]
            ret_reg = "a0"
            for suffix in ("_a0", "_a1", "_fa0", "_fa1"):
                if rest.endswith(suffix):
                    ret_reg = suffix[1:]
                    sym = rest[: -len(suffix)]
                    break
            else:
                sym = rest

            def _crt_runner(*args: int) -> int:
                # Populate both integer (a0..a7) and float (fa0..fa7) ABI argument registers
                a_regs = [int(x) & _MASK64 for x in args[:8]]
                while len(a_regs) < 8:
                    a_regs.append(0)
                res = eval_compiler_rt_routine(
                    sym,
                    iregs=a_regs,
                    fregs=a_regs,
                )
                return int(res[ret_reg]) & _MASK64

            self[key] = _crt_runner
            return _crt_runner
        raise KeyError(key)


_HUB_EVAL_GLOBALS = _HubEvalGlobals()


class LazyUnitLeanDict(dict):
    """Dictionary for `UniversalRichNode.meaning` that lifts `unit_obj` to `unit_lean`
    via `compose_LoOp_leans` on first access and caches by canonical unit key."""

    def _ensure_lifted(self) -> Any:
        if super().__contains__("unit_lean") and super().__getitem__("unit_lean") is not None:
            return super().__getitem__("unit_lean")
        unit_obj = super().get("unit_obj")
        if unit_obj is None:
            return None
        cache_key = super().get("_cache_key")
        if cache_key is not None and cache_key in _GLOBAL_UNIT_LEAN_CACHE:
            ul = _GLOBAL_UNIT_LEAN_CACHE[cache_key]
            super().__setitem__("unit_lean", ul)
            return ul
        from PseudoArch.map_unit_to_lean import compose_LoOp_leans

        ul = compose_LoOp_leans(unit_obj)
        if cache_key is not None:
            _GLOBAL_UNIT_LEAN_CACHE[cache_key] = ul
        super().__setitem__("unit_lean", ul)
        return ul

    def __getitem__(self, key: str) -> Any:
        if key == "unit_lean":
            return self._ensure_lifted()
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "unit_lean":
            res = self._ensure_lifted()
            return default if res is None else res
        return super().get(key, default)


LANG_CANONICAL_DISPLAY: dict[str, str] = {
    "c": "C",
    "cpp": "C++",
    "c++": "C++",
    "cxx": "C++",
    "go": "Go",
    "rust": "Rust",
    "python": "Python",
    "java": "Java",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "csharp": "C#",
    "c#": "C#",
    "cs": "C#",
    "ruby": "Ruby",
    "php": "PHP",
    "dart": "Dart",
    "swift": "Swift",
}

PRIMITIVE_SHORT_SPELLING: dict[str, dict[str, tuple[str, ...]]] = {
    "BV_ADD": {
        "c": ("+",), "cpp": ("+",), "go": ("+",), "rust": ("+",), "python": ("+",),
        "java": ("+",), "typescript": ("+",), "csharp": ("+",), "ruby": ("+",),
        "php": ("+",), "dart": ("+",), "swift": ("&+", "+"),
    },
    "BV_SUB": {
        "c": ("-",), "cpp": ("-",), "go": ("-",), "rust": ("-",), "python": ("-",),
        "java": ("-",), "typescript": ("-",), "csharp": ("-",), "ruby": ("-",),
        "php": ("-",), "dart": ("-",), "swift": ("&-", "-"),
    },
    "BV_MUL": {
        "c": ("*",), "cpp": ("*",), "go": ("*",), "rust": ("*",), "python": ("*",),
        "java": ("*",), "typescript": ("*",), "csharp": ("*",), "ruby": ("*",),
        "php": ("*",), "dart": ("*",), "swift": ("&*", "*"),
    },
    "BV_AND": {k: ("&",) for k in HIOP_PRIMITIVES["BV_AND"]},
    "BV_OR": {k: ("|",) for k in HIOP_PRIMITIVES["BV_OR"]},
    "BV_XOR": {k: ("^",) for k in HIOP_PRIMITIVES["BV_XOR"]},
    "BV_NOT": {
        "c": ("~",), "cpp": ("~",), "go": ("^~", "~"), "rust": ("!", "~"), "python": ("~",),
        "java": ("~",), "typescript": ("~",), "csharp": ("~",), "ruby": ("~",),
        "php": ("~",), "dart": ("~",), "swift": ("~",),
    },
    "BV_SHL": {k: ("<<",) for k in HIOP_PRIMITIVES["BV_SHL"]},
    "BV_ASHR": {k: (">>",) for k in HIOP_PRIMITIVES["BV_ASHR"]},
    "BV_LSHR": {
        "c": ("u>>", ">>>"), "cpp": ("u>>", ">>>"), "go": ("u>>", ">>>"), "rust": ("u>>", ">>>"),
        "python": (">>>",), "java": (">>>",), "typescript": (">>>",), "csharp": (">>>",),
        "ruby": (">>>",), "php": (">>>",), "dart": (">>>",), "swift": ("u>>", ">>>"),
    },
    "BV_SLT": {k: ("<",) for k in HIOP_PRIMITIVES["BV_SLT"]},
    "BV_ULT": {k: ("u<",) for k in HIOP_PRIMITIVES["BV_ULT"]},
    "BV_SDIV": {
        "c": ("/",), "cpp": ("/",), "go": ("/",), "rust": ("/",), "python": ("trunc_div",),
        "java": ("/",), "typescript": ("/",), "csharp": ("/",), "ruby": ("/",),
        "php": ("/",), "dart": ("~/", "/"), "swift": ("/",),
    },
    "BV_UDIV": {k: ("u/",) for k in HIOP_PRIMITIVES["BV_UDIV"]},
    "BV_SREM": {
        "c": ("%",), "cpp": ("%",), "go": ("%",), "rust": ("%",), "python": ("trunc_mod",),
        "java": ("%",), "typescript": ("%",), "csharp": ("%",), "ruby": ("%",),
        "php": ("%",), "dart": ("remainder",), "swift": ("%",),
    },
    "BV_UREM": {k: ("u%",) for k in HIOP_PRIMITIVES["BV_UREM"]},
    "BV_ITE": {k: ("?:",) for k in HIOP_PRIMITIVES["BV_ITE"]},
    "DART_EUCLID_MOD": {
        "dart": ("%",),
    },
    "SPACESHIP": {
        "cpp": ("<=>",),
        "ruby": ("<=>",),
        "php": ("<=>",),
    },
}


class Hub:
    """The Hub: holds AutoPoly, UR-Node registry, Equivalence Mode index, UnitVM, and MultiBodyEngine."""

    LANG_PATTERN = (
        r"(?:C\+\+|C#|TypeScript|Python|Swift|Rust|Java|Ruby|Dart|PHP|Go|C"
        r"|typescript|python|csharp|swift|rust|java|ruby|dart|cpp|cxx|php|go|c)"
    )

    def __init__(self) -> None:
        self.autopoly = AutoPoly()
        self.vm = RiscvUnitVM()
        self.multi_body = MultiBodyEngine()
        self.nodes: dict[str, UniversalRichNode] = {}
        self._ci_nodes: dict[str, UniversalRichNode] = {}
        self.modes: dict[tuple[str, str, str], list[str]] = {}
        self.semantic_modes: dict[tuple[str, str, str], list[str]] = {}
        self._lang_prim_nodes: dict[tuple[str, str], UniversalRichNode] = {}
        self._node_prim_family: dict[int, str] = {}

    def register(self, node: UniversalRichNode, alias: str | None = None) -> None:
        if not isinstance(node.meaning, LazyUnitLeanDict):
            if node.meaning.get("unit_lean") is None and node.meaning.get("unit_obj") is not None:
                from PseudoArch.map_unit_to_lean import compose_LoOp_leans

                node.meaning["unit_lean"] = compose_LoOp_leans(node.meaning["unit_obj"])
            if node.meaning.get("unit_lean") is None:
                raise ValueError(
                    f"Cannot register UniversalRichNode {node.qualified_name!r} without Sail-derived 'unit_lean'; refusing silent fallback."
                )
        elif node.meaning.get("unit_obj") is None and not dict.__contains__(node.meaning, "unit_lean"):
            raise ValueError(
                f"Cannot register UniversalRichNode {node.qualified_name!r} without 'unit_obj' or 'unit_lean'; refusing silent fallback."
            )
        self.nodes[node.qualified_name] = node
        self._ci_nodes[node.qualified_name.lower()] = node
        if alias is not None:
            self.nodes[alias] = node
            self._ci_nodes[alias.lower()] = node
        key = node.mode_key()
        self.modes.setdefault(key, []).append(node.qualified_name)

    def resolve_node(self, qualified_op: str | UniversalRichNode) -> UniversalRichNode:
        """Look up a `UniversalRichNode` by exact name, case-insensitive alias, or canonical display prefix."""
        if isinstance(qualified_op, UniversalRichNode):
            return qualified_op
        q = qualified_op.strip()
        if q in self.nodes:
            return self.nodes[q]
        ql = q.lower()
        if ql in self._ci_nodes:
            return self._ci_nodes[ql]
        if "." in q:
            prefix, rest = q.split(".", 1)
            disp = LANG_CANONICAL_DISPLAY.get(prefix.lower())
            if disp is not None:
                cand = f"{disp}.{rest}"
                if cand in self.nodes:
                    return self.nodes[cand]
                if cand.lower() in self._ci_nodes:
                    return self._ci_nodes[cand.lower()]
        raise KeyError(f"Unknown Hub qualified operator: {qualified_op!r}")

    def compute_semantic_mode_key(self, qualified_op: str | UniversalRichNode) -> tuple[str, str, str]:
        """Compute the Z3-simplified `(D_ok, D_trap, R_val)` equivalence mode key from the node's Sail `UnitLean`."""
        node = self.resolve_node(qualified_op)
        a = z3.BitVec("a", 64)
        b = z3.BitVec("b", 64)
        d_ok, d_trap, r_val = EquivalenceProver.build_bv64_formula(node, a, b)
        skey = (str(z3.simplify(d_ok)), str(z3.simplify(d_trap)), str(z3.simplify(r_val)))
        qname = node.qualified_name
        bucket = self.semantic_modes.setdefault(skey, [])
        if qname not in bucket:
            bucket.append(qname)
        return skey

    def register_state_info_0(self, state_info_0: Any, alias: str | None = None) -> UniversalRichNode:
        """Lower `state_info_0` via `map_state_info_0_to_unit`, lift via `compose_LoOp_leans`, and register."""
        from PseudoArch.map_HiOp_to_unit import map_state_info_0_to_unit

        mapped = map_state_info_0_to_unit(state_info_0)
        node = UniversalRichNode.from_mapped_hiop(mapped, state_info_0)
        self.register(node, alias=alias)
        return node

    def eval_node(
        self,
        qualified_op: str | UniversalRichNode,
        a: int,
        b: int = 0,
        c: int = 0,
        d: int = 0,
        *extra_args: int,
    ) -> int:
        """Execute a UR-Node's Sail-derived `UnitLean` semantics on 64-bit integer holders."""
        node = self.resolve_node(qualified_op)
        extra_names = tuple(chr(ord("e") + i) for i in range(len(extra_args)))
        emitted = self.autopoly.synthesize_from_sail_unit(
            node, "python", lhs="a", rhs="b", third="c", fourth="d", extra_names=extra_names
        )
        for crt_sym in re.findall(r"compiler_rt_[A-Za-z0-9_]+", emitted["code"]):
            _ = _HUB_EVAL_GLOBALS[crt_sym]
        loc_env = {
            "a": int(a),
            "b": int(b),
            "c": int(c),
            "d": int(d),
            **{name: int(val) for name, val in zip(extra_names, extra_args)},
        }
        raw = int(eval(emitted["code"], _HUB_EVAL_GLOBALS, loc_env))
        return _s64(raw)

    def _candidate_target_nodes_for(self, src_node: UniversalRichNode, target_lang: str) -> list[UniversalRichNode]:
        t_norm = normalize_target_lang(target_lang)
        ul_src = src_node.meaning.get("unit_lean")
        n_in = len(ul_src.inputs) if ul_src is not None else None
        cands: list[UniversalRichNode] = []
        prim_fam = self._node_prim_family.get(id(src_node))
        if prim_fam is not None:
            direct = self._lang_prim_nodes.get((t_norm, prim_fam))
            if direct is not None:
                cands.append(direct)
        for (lang_k, _op_k), cand in self._lang_prim_nodes.items():
            if lang_k == t_norm and cand not in cands:
                ul_c = cand.meaning.get("unit_lean")
                if n_in is None or (ul_c is not None and len(ul_c.inputs) == n_in):
                    cands.append(cand)
        return cands

    def transpile_qualified_op(
        self,
        qualified_op: str | UniversalRichNode,
        target_lang: str,
        lhs: str = "a",
        rhs: str = "b",
        third: str = "c",
        fourth: str = "d",
        extra_names: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Transpile `qualified_op` (e.g. `Go./`, `Java.>>>`, `Python.//`) into `target_lang` via AutoPoly."""
        node = self.resolve_node(qualified_op)
        cands = self._candidate_target_nodes_for(node, target_lang)
        return self.autopoly.synthesize_from_sail_unit(
            node,
            target_lang,
            candidate_target_nodes=cands,
            lhs=lhs,
            rhs=rhs,
            third=third,
            fourth=fourth,
            extra_names=extra_names,
        )

    @staticmethod
    def _parse_atom_val(tok: str, env: dict[str, int]) -> int:
        tok = tok.strip()
        if tok in env:
            return int(env[tok])
        if re.match(r"^-?(?:0x[0-9a-fA-F]+|\d+)$", tok):
            return int(tok, 0)
        raise KeyError(f"Unbound Hub identifier or literal: {tok!r}")

    def _eval_flat_clause(self, clause: str, work: dict[str, int]) -> int | str:
        s = clause.strip()
        # 1. Function-style qualified call: `Lang.op(arg1, arg2[, arg3, arg4, ...])`
        m_call = re.match(rf"^({self.LANG_PATTERN})\.([^\s(]+)\(\s*(.*)\s*\)$", s)
        if m_call:
            lang, op, arg_str = m_call.groups()
            args = [self._parse_atom_val(x, work) for x in arg_str.split(",") if x.strip()]
            a0 = args[0] if len(args) >= 1 else 0
            a1 = args[1] if len(args) >= 2 else 0
            a2 = args[2] if len(args) >= 3 else 0
            a3 = args[3] if len(args) >= 4 else 0
            return self.eval_node(f"{lang}.{op}", a0, a1, a2, a3, *args[4:])

        # 2. Unary prefix qualified operator: `Lang.op rhs`
        m_un = re.match(rf"^({self.LANG_PATTERN})\.(\S+)\s+([^\s()]+)$", s)
        if m_un:
            lang, op, rhs = m_un.groups()
            return self.eval_node(f"{lang}.{op}", self._parse_atom_val(rhs, work))

        # 3. Binary infix qualified operator: `lhs Lang.op rhs`
        m_bin = re.match(rf"^([^\s()]+)\s+({self.LANG_PATTERN})\.(\S+)\s+([^\s()]+)$", s)
        if m_bin:
            lhs, lang, op, rhs = m_bin.groups()
            return self.eval_node(
                f"{lang}.{op}",
                self._parse_atom_val(lhs, work),
                self._parse_atom_val(rhs, work),
            )

        if s in work:
            return int(work[s])
        if re.match(r"^-?(?:0x[0-9a-fA-F]+|\d+)$", s):
            return int(s, 0)
        return s

    def eval_qualified_expr(self, expr: str, env: dict[str, int]) -> int | str:
        """Evaluate a Hub expression with qualified operators across all 12 languages."""
        work = dict(env)
        s = expr.strip()
        assign_target: str | None = None
        m_assign = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", s)
        if m_assign:
            assign_target, s = m_assign.group(1), m_assign.group(2).strip()

        call_pat = re.compile(rf"({self.LANG_PATTERN})\.([^\s()]+)\(\s*([^()]*)\s*\)")
        paren_pat = re.compile(r"\(([^()]+)\)")

        while True:
            mc = call_pat.search(s)
            if mc:
                val = self._eval_flat_clause(mc.group(0), work)
                if isinstance(val, int):
                    tmp = f"__hub_t{len(work)}"
                    work[tmp] = val
                    s = s[: mc.start()] + tmp + s[mc.end() :]
                    continue
            mp = paren_pat.search(s)
            if not mp:
                break
            inner = mp.group(1).strip()
            val = self._eval_flat_clause(inner, work)
            if not isinstance(val, int):
                break
            tmp = f"__hub_t{len(work)}"
            work[tmp] = val
            s = s[: mp.start()] + tmp + s[mp.end() :]

        res = self._eval_flat_clause(s, work)
        if assign_target is not None and isinstance(res, int):
            env[assign_target] = res
        return res

    def _transpile_flat_clause(
        self,
        clause: str,
        target_lang: str,
        subs: dict[str, str],
        steps: list[dict[str, Any]],
    ) -> str:
        s = clause.strip()
        m_call = re.match(rf"^({self.LANG_PATTERN})\.([^\s(]+)\(\s*(.*)\s*\)$", s)
        if m_call:
            lang, op, arg_str = m_call.groups()
            qop = f"{lang}.{op}"
            raw_args = [subs.get(x.strip(), x.strip()) for x in arg_str.split(",") if x.strip()]
            a0 = raw_args[0] if len(raw_args) >= 1 else "a"
            a1 = raw_args[1] if len(raw_args) >= 2 else "b"
            a2 = raw_args[2] if len(raw_args) >= 3 else "c"
            a3 = raw_args[3] if len(raw_args) >= 4 else "d"
            emitted = self.transpile_qualified_op(qop, target_lang, a0, a1, a2, a3, extra_names=raw_args[4:])
            steps.append({"ur_node": qop, "tier": emitted["tier"], "code": emitted["code"]})
            return emitted["code"]

        m_un = re.match(rf"^({self.LANG_PATTERN})\.(\S+)\s+([^\s()]+)$", s)
        if m_un:
            lang, op, rhs = m_un.groups()
            qop = f"{lang}.{op}"
            rhs_code = subs.get(rhs, rhs)
            emitted = self.transpile_qualified_op(qop, target_lang, rhs_code, "0")
            steps.append({"ur_node": qop, "tier": emitted["tier"], "code": emitted["code"]})
            return emitted["code"]

        m_bin = re.match(rf"^([^\s()]+)\s+({self.LANG_PATTERN})\.(\S+)\s+([^\s()]+)$", s)
        if m_bin:
            lhs, lang, op, rhs = m_bin.groups()
            qop = f"{lang}.{op}"
            lhs_code = subs.get(lhs, lhs)
            rhs_code = subs.get(rhs, rhs)
            emitted = self.transpile_qualified_op(qop, target_lang, lhs_code, rhs_code)
            steps.append({"ur_node": qop, "tier": emitted["tier"], "code": emitted["code"]})
            return emitted["code"]

        return subs.get(s, s)

    def transpile_hub_expr(self, expr: str, target_lang: str) -> dict[str, Any]:
        """Transpile a Hub expression with qualified operators across all 12 languages into `target_lang`."""
        steps: list[dict[str, Any]] = []
        subs: dict[str, str] = {}
        work_expr = expr.strip()
        assign_target: str | None = None
        m_assign = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", work_expr)
        if m_assign:
            assign_target, work_expr = m_assign.group(1), m_assign.group(2).strip()

        call_pat = re.compile(rf"({self.LANG_PATTERN})\.([^\s()]+)\(\s*([^()]*)\s*\)")
        paren_pat = re.compile(r"\(([^()]+)\)")

        while True:
            mc = call_pat.search(work_expr)
            if mc:
                code = self._transpile_flat_clause(mc.group(0), target_lang, subs, steps)
                tok = f"__hub_s{len(subs)}"
                subs[tok] = code
                work_expr = work_expr[: mc.start()] + tok + work_expr[mc.end() :]
                continue
            mp = paren_pat.search(work_expr)
            if not mp:
                break
            inner = mp.group(1).strip()
            code = self._transpile_flat_clause(inner, target_lang, subs, steps)
            tok = f"__hub_s{len(subs)}"
            subs[tok] = code
            work_expr = work_expr[: mp.start()] + tok + work_expr[mp.end() :]

        final_code = self._transpile_flat_clause(work_expr, target_lang, subs, steps)
        if assign_target is not None:
            final_code = f"{assign_target} = {final_code}"
        return {
            "target_lang": target_lang,
            "source_expr": expr,
            "transpiled_code": final_code,
            "steps": steps,
        }

    def _register_12lang_short_aliases(self) -> None:
        """Register short qualified operator aliases (`C.+`, `Go./`, `Java.>>>`, `Python.//`, etc.)
        backed directly by the 12 languages' Sail-lifted 64-bit `UnitLean`s."""
        from .autopoly.polyfill import format_hiop_target_template
        from .autopoly.verify_hiop_primitives import ALL_12_LANGUAGES, load_language_64bit_unit_leans

        lang_uls = load_language_64bit_unit_leans()
        for lang in ALL_12_LANGUAGES:
            disp = LANG_CANONICAL_DISPLAY[lang]
            for op_key, ul in lang_uls[lang].items():
                target_tmpl = format_hiop_target_template(op_key, lang)
                prim_node = UniversalRichNode(
                    hiop={
                        "lang": disp,
                        "operator": op_key,
                        "spelling": op_key,
                        "target_code": target_tmpl,
                    },
                    meaning={"unit_lean": ul},
                )
                self.register(prim_node, alias=f"{lang}.{op_key}")
                self._lang_prim_nodes[(lang, op_key)] = prim_node
                self._node_prim_family[id(prim_node)] = op_key
                for short_op in PRIMITIVE_SHORT_SPELLING.get(op_key, {}).get(lang, ()):
                    short_node = UniversalRichNode(
                        hiop={
                            "lang": disp,
                            "operator": short_op,
                            "spelling": short_op,
                            "target_code": target_tmpl,
                        },
                        meaning={"unit_lean": ul},
                    )
                    self.register(short_node, alias=f"{lang}.{short_op}")
                    self._node_prim_family[id(short_node)] = op_key
                if lang == "python" and op_key == "PY_FLOORDIV":
                    for sp in ("//",):
                        n_fd = UniversalRichNode(
                            hiop={"lang": disp, "operator": sp, "spelling": sp, "target_code": "({a} // {b})"},
                            meaning={"unit_lean": ul},
                        )
                        self.register(n_fd, alias=f"python.{sp}")
                        self._node_prim_family[id(n_fd)] = "PY_FLOORDIV"
                elif lang == "python" and op_key == "PY_MOD":
                    for sp in ("%",):
                        n_md = UniversalRichNode(
                            hiop={"lang": disp, "operator": sp, "spelling": sp, "target_code": "({a} % {b})"},
                            meaning={"unit_lean": ul},
                        )
                        self.register(n_md, alias=f"python.{sp}")
                        self._node_prim_family[id(n_md)] = "PY_MOD"

    def load_lowered_vocabularies(
        self,
        out_dir: str | None = None,
        include_all_gnu_c: bool = False,
        register_short_aliases: bool = True,
    ) -> dict[str, int]:
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

        if include_all_gnu_c and (base / "gnu_c_all_hijacked.jsonl.gz").exists():
            c_path = base / "gnu_c_all_hijacked.jsonl.gz"
        elif (base / "gnu_c_first_of_each_hijacked.jsonl.gz").exists():
            c_path = base / "gnu_c_first_of_each_hijacked.jsonl.gz"
        else:
            c_path = base / "gnu_c_first_of_each.jsonl.gz"

        sources = [
            ("C", c_path),
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
        from PseudoArch.map_HiOp_to_unit.lower_HiOp import Word
        from PseudoArch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import Unit

        for default_lang, path in sources:
            if not path.exists():
                continue
            loaded = 0
            with gzip.open(path, "rt", encoding="utf-8") as gz:
                for line in gz:
                    rec = json.loads(line)
                    if rec.get("refusal") is not None:
                        continue
                    words = rec.get("words") or []
                    unit_idxs = rec.get("unit") or []
                    raw_words = [
                        words[i]
                        for i in unit_idxs
                        if isinstance(i, int) and i < len(words)
                    ]
                    if not raw_words:
                        continue
                    base_addr = raw_words[0][0]
                    unit_words = tuple(
                        Word(w[0] - base_addr, w[1], w[2], w[3], tuple(w[4]))
                        for w in raw_words
                    )
                    raw_hp = rec.get("holds_p")
                    if raw_hp is True:
                        holds_p = ((0, "a0"),)
                    elif isinstance(raw_hp, (list, tuple)):
                        holds_p = tuple(
                            (int(p[0]), str(p[1]))
                            for p in raw_hp
                            if isinstance(p, (list, tuple)) and len(p) == 2
                        )
                    else:
                        holds_p = ()
                    parts = tuple(str(p) for p in (rec.get("parts") or ()))
                    unit_obj = Unit(str(rec.get("symbol", "op")), unit_words, parts, holds_p, None)
                    cache_key = (
                        tuple((w.address, w.bytes_hex, w.relocations) for w in unit_words),
                        holds_p,
                        parts,
                    )
                    lang_raw = rec.get("dialect") or default_lang
                    lang = LANG_CANONICAL_DISPLAY.get(str(lang_raw).lower(), str(lang_raw))
                    op = rec.get("operator") or rec.get("op_key") or rec.get("op") or ""
                    raw_h = rec.get("holders") or ()
                    holders = tuple(h[1] if isinstance(h, list) and len(h) > 1 else str(h) for h in raw_h)
                    node = UniversalRichNode(
                        hiop={
                            "lang": lang,
                            "operator": f"{op}[{','.join(holders)}]",
                            "holders": holders,
                            "template": rec.get("template", ""),
                        },
                        meaning=LazyUnitLeanDict({"unit_obj": unit_obj, "_cache_key": cache_key}),
                    )
                    self.register(node)
                    loaded += 1
            counts[default_lang] = loaded

        if register_short_aliases:
            self._register_12lang_short_aliases()
        return counts
