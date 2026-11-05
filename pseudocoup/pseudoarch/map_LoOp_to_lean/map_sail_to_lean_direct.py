"""map_sail_to_lean_direct -- A LoOp's Lean is the body Sail already emitted for it.

Plan: `.../node_0_0_0_0_1_map_LoOp_to_lean/node_0_0_0_0_1_0_map_sail_to_lean_direct/`.

Decodes any 16-bit or 32-bit RISC-V machine word using the Sail model's own
`encdec_compressed_backwards` / `encdec_backwards` and evaluates the model's
own `execute` clause directly from `sail_model_of_riscv`.
"""

from typing import Any, NamedTuple, Tuple
import z3

from .. import sail_model_of_riscv as _sail_model  # noqa: F401
import lean_reader as LR
import lifter as _lifter

_ORIG_SPECIAL_FORM = LR.Reader.special_form
_ORIG_MERGE_VALUES = LR.merge_values
_HOOK_INSTALLED = False
_SAIL_LIFTER: _lifter.GeneratedLifter | None = None


class SailVector:
    def __init__(self, default: Any, items: dict[int, Any] | None = None, length: int | None = None) -> None:
        self.default = default
        self.items = dict(items) if items else {}
        self.length = length


def _hooked_merge_values(condition, yes, no):
    if isinstance(yes, SailVector) and isinstance(no, SailVector):
        keys = set(yes.items) | set(no.items)
        merged = {k: _hooked_merge_values(condition, yes.items.get(k, yes.default), no.items.get(k, no.default)) for k in keys}
        return SailVector(_hooked_merge_values(condition, yes.default, no.default), merged, yes.length or no.length)
    is_lint = isinstance(yes, LR.LInt) or isinstance(no, LR.LInt)
    yb = LR.int_of(yes) if is_lint else (yes if z3.is_bv(yes) else None)
    nb = LR.int_of(no) if is_lint else (no if z3.is_bv(no) else None)
    if yb is not None and nb is not None and yb.size() == nb.size():
        if yb.eq(nb):
            return yes
        if yb.num_args() == 2 and yb.arg(0).eq(nb):
            k, d, z = yb.decl().kind(), yb.arg(1), z3.BitVecVal(0, nb.size())
            if k == z3.Z3_OP_BADD:
                return LR.lint(nb + z3.If(condition, d, z)) if is_lint else (nb + z3.If(condition, d, z))
            if k == z3.Z3_OP_BSUB:
                return LR.lint(nb - z3.If(condition, d, z)) if is_lint else (nb - z3.If(condition, d, z))
            if k == z3.Z3_OP_BXOR:
                return LR.lint(nb ^ z3.If(condition, d, z)) if is_lint else (nb ^ z3.If(condition, d, z))
            if k == z3.Z3_OP_BOR:
                return LR.lint(nb | z3.If(condition, d, z)) if is_lint else (nb | z3.If(condition, d, z))
    return _ORIG_MERGE_VALUES(condition, yes, no)


def _hooked_special_form(self, name, arg_nodes, env, machine):
    if name in ("vmem_read_addr", "mem_read"):
        addr_idx, width_idx = (0, 1) if name == "vmem_read_addr" else (2, 3)
        vaddr = self.eval(arg_nodes[addr_idx], env, machine)
        width = LR.concrete_int(self.eval(arg_nodes[width_idx], env, machine))
        addr_bv = vaddr.args[0] if isinstance(vaddr, LR.Ctor) else LR.bv_of(vaddr)
        if hasattr(machine, "state") and hasattr(machine.state, "read_mem_bytes"):
            val = machine.state.read_mem_bytes(addr_bv, width)
        else:
            val = z3.BitVec(f"mem_{z3.simplify(addr_bv)}_{width}", width * 8)
        return LR.Ctor("Ok", [val])
    if name in ("vmem_write_addr", "mem_write_value"):
        vaddr = self.eval(arg_nodes[0], env, machine)
        width = LR.concrete_int(self.eval(arg_nodes[1], env, machine))
        data = LR.bv_of(self.eval(arg_nodes[2], env, machine))
        addr_bv = vaddr.args[0] if isinstance(vaddr, LR.Ctor) else LR.bv_of(vaddr)
        if hasattr(machine, "state") and hasattr(machine.state, "write_mem_bytes"):
            machine.state.write_mem_bytes(addr_bv, width, data)
        return LR.Ctor("Ok", [z3.BoolVal(True)])
    if name in ("mem_write_ea", "phys_access_check"):
        return LR.Ctor("Ok", [None])
    if name == "count_ones" and len(arg_nodes) == 1:
        bv = LR.bv_of(self.eval(arg_nodes[0], env, machine))
        w = bv.size()
        total = z3.BitVecVal(0, LR.INT_WIDTH)
        for i in range(w):
            total = total + z3.ZeroExt(LR.INT_WIDTH - 1, z3.Extract(i, i, bv))
        return LR.lint(z3.simplify(total))
    if name == "Vector.length" and len(arg_nodes) == 1:
        vec = self.eval(arg_nodes[0], env, machine)
        if isinstance(vec, SailVector):
            if vec.length is not None:
                return LR.lint(vec.length)
            if vec.items:
                return LR.lint(len(vec.items))
        if "nf" in env and arg_nodes[0] == ("var", "vreg_list"):
            return env["nf"]
        if "num_elem" in env:
            return env["num_elem"]
    if name == "currentlyEnabled" and len(arg_nodes) == 1:
        ext_val = self.eval(arg_nodes[0], env, machine)
        try:
            return self.call("currentlyEnabled", [ext_val], machine)
        except LR.ReadRefused:
            return self.call("hartSupports", [ext_val], machine)
    return _ORIG_SPECIAL_FORM(self, name, arg_nodes, env, machine)


def _prim_clz(x):
    bv = LR.bv_of(x)
    w = bv.size()
    acc = LR.lint(w)
    for i in range(w):
        acc = LR.merge_values(z3.Extract(i, i, bv) == z3.BitVecVal(1, 1), LR.lint(w - 1 - i), acc)
    return acc


def _prim_ctz(x):
    bv = LR.bv_of(x)
    w = bv.size()
    acc = LR.lint(w)
    for i in range(w - 1, -1, -1):
        acc = LR.merge_values(z3.Extract(i, i, bv) == z3.BitVecVal(1, 1), LR.lint(i), acc)
    return acc


def _float_exp_mant(x):
    bv = LR.bv_of(x)
    w = bv.size()
    if w == 16:
        exp, mant = z3.Extract(14, 10, bv), z3.Extract(9, 0, bv)
    elif w == 32:
        exp, mant = z3.Extract(30, 23, bv), z3.Extract(22, 0, bv)
    elif w == 64:
        exp, mant = z3.Extract(62, 52, bv), z3.Extract(51, 0, bv)
    else:
        exp, mant = z3.Extract(126, 112, bv), z3.Extract(111, 0, bv)
    exp_ones = exp == z3.BitVecVal((1 << exp.size()) - 1, exp.size())
    exp_zeros = exp == z3.BitVecVal(0, exp.size())
    mant_zeros = mant == z3.BitVecVal(0, mant.size())
    mant_msb = z3.Extract(mant.size() - 1, mant.size() - 1, mant) == z3.BitVecVal(1, 1)
    return exp_ones, exp_zeros, mant_zeros, mant_msb


def _vec_update(vec: SailVector, idx: Any, val: Any) -> SailVector:
    i = LR.concrete_int(idx)
    new_items = dict(vec.items)
    new_items[i] = val
    return SailVector(vec.default, new_items, max(vec.length or 0, i + 1))


def _vec_get(vec: SailVector, idx: Any) -> Any:
    try:
        return vec.items.get(LR.concrete_int(idx), vec.default)
    except LR.ReadRefused:
        idx_bv = LR.int_of(idx)
        acc = vec.default
        for k, v in sorted(vec.items.items()):
            acc = _hooked_merge_values(idx_bv == z3.BitVecVal(k, idx_bv.size()), v, acc)
        return acc


def ensure_memory_hook() -> None:
    global _HOOK_INSTALLED
    if not _HOOK_INSTALLED:
        LR.Reader.special_form = _hooked_special_form
        LR.merge_values = _hooked_merge_values
        LR.PRIMITIVES["BitVec.countLeadingZeros"] = _prim_clz
        LR.PRIMITIVES["BitVec.countTrailingZeros"] = _prim_ctz
        LR.PRIMITIVES["BitVec.addInt"] = lambda v, n: LR.bv_of(v) + LR.shift_amount_bits(n, LR.bv_of(v).size())
        LR.PRIMITIVES["BitVec.subInt"] = lambda v, n: LR.bv_of(v) - LR.shift_amount_bits(n, LR.bv_of(v).size())
        LR.PRIMITIVES["BitVec.access"] = lambda v, i: z3.Extract(LR.concrete_int(i), LR.concrete_int(i), LR.bv_of(v))
        LR.PRIMITIVES["BitVec.ofBool"] = lambda b: LR.bv_of(b)
        LR.PRIMITIVES["BitVec.join1"] = lambda lst: LR.bv_of(lst[0]) if len(lst) == 1 else z3.Concat(*[LR.bv_of(x) for x in lst])
        LR.PRIMITIVES["vectorInit"] = lambda d: SailVector(d)
        LR.PRIMITIVES["vectorUpdate"] = _vec_update
        LR.PRIMITIVES["GetElem?.getElem!"] = _vec_get
        LR.PRIMITIVES["Vector.length"] = lambda vec: LR.lint(vec.length if vec.length is not None else len(vec.items))
        LR.PRIMITIVES["PreSail.undefined_vector"] = lambda n, d: SailVector(d, {}, LR.concrete_int(n))
        LR.PRIMITIVES["PreSail.undefined_bitvector"] = LR.prim_bv_zero
        LR.PRIMITIVES["PreSail.undefined_bool"] = lambda _: z3.BoolVal(False)
        LR.PRIMITIVES["PreSail.undefined_bit"] = lambda _: z3.BitVecVal(0, 1)
        LR.PRIMITIVES["PreSail.undefined_int"] = lambda _: LR.lint(0)
        LR.PRIMITIVES["PreSail.undefined_nat"] = lambda _: LR.lint(0)
        LR.PRIMITIVES["float_is_nan"] = lambda x: z3.And(_float_exp_mant(x)[0], z3.Not(_float_exp_mant(x)[2]))
        LR.PRIMITIVES["float_is_snan"] = lambda x: z3.And(_float_exp_mant(x)[0], z3.Not(_float_exp_mant(x)[2]), z3.Not(_float_exp_mant(x)[3]))
        LR.PRIMITIVES["float_is_qnan"] = lambda x: z3.And(_float_exp_mant(x)[0], _float_exp_mant(x)[3])
        LR.PRIMITIVES["float_is_inf"] = lambda x: z3.And(_float_exp_mant(x)[0], _float_exp_mant(x)[2])
        LR.PRIMITIVES["float_is_normal"] = lambda x: z3.And(z3.Not(_float_exp_mant(x)[0]), z3.Not(_float_exp_mant(x)[1]))
        LR.PRIMITIVES["float_is_subnormal"] = lambda x: z3.And(_float_exp_mant(x)[1], z3.Not(_float_exp_mant(x)[2]))
        LR.PRIMITIVES["float_is_zero"] = lambda x: z3.And(_float_exp_mant(x)[1], _float_exp_mant(x)[2])
        _HOOK_INSTALLED = True


class LoOpLean(NamedTuple):
    """The decoded constructor, execute clause name, and Lean origin for one LoOp word."""

    word: int
    size: int
    constructor: str
    decoded_ast: Any
    execute_clause: str
    origin_file: str


def shared_sail_lifter() -> _lifter.GeneratedLifter:
    global _SAIL_LIFTER
    ensure_memory_hook()
    if _SAIL_LIFTER is None:
        gl = _lifter.GeneratedLifter(emit_dir=_sail_model.EMIT_DIR)
        for k in list(gl.definitions):
            if LR.softfloat(k) is not None:
                del gl.definitions[k]
        if "zero_extend" not in gl.definitions:
            gl.definitions["zero_extend"] = (
                [("m", "_"), ("v", "BitVec k_n")],
                ("app", ("var", "Sail.BitVec.zeroExtend"), [("var", "v"), ("var", "m")]),
            )
        for i in range(32):
            gl.widths[f"vr{i}"] = 256
            gl.reader.widths[f"vr{i}"] = 256
        gl.reset_registers["mstatus"] = z3.simplify(gl.reset_registers["mstatus"] | z3.BitVecVal(0x6600, 64))
        gl.reset_registers["vstart"] = z3.BitVecVal(0, 64)
        gl.reset_registers["vl"] = z3.BitVecVal(0, 64)
        gl.reset_registers["vtype"] = z3.BitVecVal(0x10, 64)
        gl.reset_registers["vcsr"] = z3.BitVecVal(0, 3)
        _SAIL_LIFTER = gl
    return _SAIL_LIFTER


_DECODE_CACHE: dict[tuple[int, int], LoOpLean] = {}


def decode_word(word: int, size: int) -> LoOpLean:
    """Decode a 2-byte or 4-byte machine word via Sail's own `encdec` backwards clauses."""
    key = (int(word), int(size))
    if key in _DECODE_CACHE:
        return _DECODE_CACHE[key]
    gl = shared_sail_lifter()
    instr = gl.decode(word, size)
    ctor_name = instr.name if isinstance(instr, LR.Ctor) else str(instr)
    if ctor_name in ("ILLEGAL", "C_ILLEGAL"):
        raise _lifter.LiftRefused(f"DECODE_ILLEGAL: word 0x{word:x} (size={size}) decoded to {ctor_name}")
    exec_name = f"execute_{ctor_name}"
    origin = gl.origin.get(exec_name, "Sl1Lean/InstsEnd.lean")
    res = LoOpLean(
        word=word,
        size=size,
        constructor=ctor_name,
        decoded_ast=instr,
        execute_clause=exec_name,
        origin_file=origin,
    )
    _DECODE_CACHE[key] = res
    return res


def _non_retire_name(res: Any) -> str | None:
    if not isinstance(res, LR.Ctor):
        return None
    if res.name == "ite" and len(res.args) == 3:
        return _non_retire_name(res.args[1]) or _non_retire_name(res.args[2])
    if res.name not in ("Retire_Success", "RETIRE_SUCCESS"):
        return res.name
    return None


def execute_word(word: int, size: int, state: Any, pc: int = 0) -> Tuple[Any, Any, LoOpLean]:
    """Decode and execute one machine word against `state` using the Sail Lean model."""
    gl = shared_sail_lifter()
    loop_lean = decode_word(word, size)
    saved_reset = dict(gl.reset_registers)
    try:
        if hasattr(state, "registers"):
            for k, v in state.registers.items():
                if isinstance(k, str) and not _lifter.X_REGISTER.match(k) and not _lifter.F_REGISTER.match(k):
                    gl.reset_registers[k] = v
            state.registers["PC"] = z3.BitVecVal(pc, 64)
            state.registers["nextPC"] = z3.BitVecVal(pc + size, 64)
        gl.reset_registers["PC"] = z3.BitVecVal(pc, 64)
        gl.reset_registers["nextPC"] = z3.BitVecVal(pc + size, 64)
        result, machine = gl.execute(loop_lean.decoded_ast, state)
        if hasattr(state, "registers"):
            for name, _ in machine.writes:
                if not _lifter.X_REGISTER.match(name) and not _lifter.F_REGISTER.match(name):
                    if name in machine.registers:
                        state.registers[name] = machine.registers[name]
    finally:
        gl.reset_registers = saved_reset
    bad = _non_retire_name(result)
    if bad is not None:
        raise _lifter.LiftRefused(
            f"EXECUTE_NON_RETIRE for {loop_lean.constructor} (word 0x{word:x}): {bad}"
        )
    return result, machine, loop_lean
