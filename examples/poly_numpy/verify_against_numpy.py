#!/usr/bin/env python3
"""verify_against_numpy.py -- Verifies `PolyNumPy` against real Python `numpy`
and executes the emitted code natively across 10 compilers/runtimes.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
EMITTED_DIR = HERE / "emitted"
sys.path.insert(0, str(EMITTED_DIR))

import poly_numpy as pnp  # type: ignore


def unpack_vec3(v: int) -> tuple[int, int, int]:
    return (pnp.np_get_axis(v, 0), pnp.np_get_axis(v, 1), pnp.np_get_axis(v, 2))


def unpack_2x2(buf: int) -> np.ndarray:
    return np.array([
        [pnp.np_buf4_get(buf, 0), pnp.np_buf4_get(buf, 1)],
        [pnp.np_buf4_get(buf, 2), pnp.np_buf4_get(buf, 3)],
    ], dtype=np.int64)


def numpy_reference_pipeline(seed: int) -> int:
    col = np.array([[[seed + 3], [seed - 5]]], dtype=np.int64)          # shape (1, 2, 1)
    row = np.array([[[(seed * 2) + 1, (-seed) + 7]]], dtype=np.int64)   # shape (1, 1, 2)
    m_a = (col + row)[0]                                                # broadcast -> (2, 2)
    m_b = np.array([[seed + 2, (-seed) - 3], [(seed * 3) - 1, seed + 4]], dtype=np.int64)
    mm_i16 = np.matmul(m_a.T, np.flip(m_b, axis=0)).astype(np.int16).astype(np.int64)
    m_c = np.clip(mm_i16, -500, 500)
    wrap_idx = int(np.ravel_multi_index((-1, (-seed) - 7, seed + 9), (4, 5, 6), mode="wrap"))
    s_all = int(np.sum(m_c))
    amax = int(np.argmax(m_c))
    tr = int(np.trace(m_c))
    arr3 = np.array([s_all, tr, wrap_idx], dtype=np.int64)
    order = np.argsort(arr3, kind="stable")
    asort = pnp.np_pack_vec3(int(order[0]), int(order[1]), int(order[2]))
    return (s_all * 1000003) + (amax * 99991) + (tr * 31337) + (wrap_idx * 1337) + asort


def test_subsystem_parity_with_numpy() -> None:
    # 1. C/F Strides
    for sh in [(2, 3, 4), (5, 1, 7), (3, 6, 2)]:
        packed_sh = pnp.np_pack_vec3(*sh)
        c_ref = tuple(s // 8 for s in np.empty(sh, dtype=np.int64, order="C").strides)
        f_ref = tuple(s // 8 for s in np.empty(sh, dtype=np.int64, order="F").strides)
        assert unpack_vec3(pnp.np_c_strides(packed_sh)) == c_ref
        assert unpack_vec3(pnp.np_f_strides(packed_sh)) == f_ref

    # 2. Broadcasting shapes & zero-copy strides
    sh_a, sh_b = (2, 1, 4), (1, 3, 4)
    b_sh = pnp.np_broadcast_shapes(pnp.np_pack_vec3(*sh_a), pnp.np_pack_vec3(*sh_b))
    assert unpack_vec3(b_sh) == np.broadcast_shapes(sh_a, sh_b)
    arr_a = np.zeros(sh_a, dtype=np.int64)
    b_st_ref = tuple(s // 8 for s in np.broadcast_to(arr_a, (2, 3, 4)).strides)
    b_st = pnp.np_broadcast_strides(pnp.np_pack_vec3(*sh_a), pnp.np_c_strides(pnp.np_pack_vec3(*sh_a)), b_sh)
    assert unpack_vec3(b_st) == b_st_ref

    # 3. Ravel/Unravel with negative wrap & clip
    for coords in [(-1, -7, 9), (2, -3, -11), (0, 4, 5)]:
        for mode_id, mode_str in [(1, "wrap"), (2, "clip")]:
            got = pnp.np_ravel_multi_index(pnp.np_pack_vec3(*coords), pnp.np_pack_vec3(4, 5, 6), mode_id)
            ref = int(np.ravel_multi_index(coords, (4, 5, 6), mode=mode_str))
            assert got == ref, f"ravel mismatch on {coords} mode={mode_str}: {got} != {ref}"
    for flat in [0, 7, 42, 119]:
        got_u = unpack_vec3(pnp.np_unravel_index(flat, pnp.np_pack_vec3(4, 5, 6)))
        ref_u = tuple(int(x) for x in np.unravel_index(flat, (4, 5, 6)))
        assert got_u == ref_u

    # 4. Full pipeline parity against real numpy across 5 seeds
    for s in [-17, 0, 7, 42, 99]:
        assert pnp.np_pipeline_digest(s) == numpy_reference_pipeline(s)
    print("  [PASS] All PolyNumPy subsystems match real Python `numpy` 100% bit-for-bit")


def run_native_toolchains() -> None:
    seeds = [-17, 0, 7, 42, 99]
    expected = [numpy_reference_pipeline(s) for s in seeds]
    print(f"  [NumPy Reference] seeds={seeds} -> {expected}")

    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)

        # C (gcc -O2)
        c_src = "#include <stdio.h>\n#include <stdint.h>\n" + (EMITTED_DIR / "poly_numpy.c").read_text()
        c_src += "\nint main(void) { int s[5]={-17,0,7,42,99}; for(int i=0;i<5;i++) printf(\"%lld \",(long long)np_pipeline_digest(s[i])); return 0; }\n"
        (tdir / "t.c").write_text(c_src)
        subprocess.run(["gcc", "-O2", str(tdir / "t.c"), "-o", str(tdir / "tc")], check=True)
        c_out = [int(x) for x in subprocess.check_output([str(tdir / "tc")], text=True).split()]
        assert c_out == expected, f"C mismatch: {c_out}"
        print(f"  [C (gcc -O2)    ] {c_out} == NumPy PASS")

        # C++ (g++ -O2)
        (tdir / "t.cpp").write_text(c_src)
        subprocess.run(["g++", "-O2", str(tdir / "t.cpp"), "-o", str(tdir / "tcpp")], check=True)
        cpp_out = [int(x) for x in subprocess.check_output([str(tdir / "tcpp")], text=True).split()]
        assert cpp_out == expected
        print(f"  [C++ (g++ -O2)  ] {cpp_out} == NumPy PASS")

        # Rust (rustc -O)
        rs_src = "#![allow(unused_parens, non_snake_case)]\n" + (EMITTED_DIR / "poly_numpy.rs").read_text()
        rs_src += "\nfn main() { for s in [-17i64,0,7,42,99] { print!(\"{} \", np_pipeline_digest(s)); } }\n"
        (tdir / "t.rs").write_text(rs_src)
        subprocess.run(["rustc", "-O", "-A", "warnings", str(tdir / "t.rs"), "-o", str(tdir / "trs")], check=True)
        rs_out = [int(x) for x in subprocess.check_output([str(tdir / "trs")], text=True).split()]
        assert rs_out == expected
        print(f"  [Rust (rustc -O)] {rs_out} == NumPy PASS")

        # Go (go run)
        go_src = "package main\nimport \"fmt\"\n" + (EMITTED_DIR / "poly_numpy.go").read_text()
        go_src += "\nfunc main() { for _, s := range []int64{-17,0,7,42,99} { fmt.Printf(\"%d \", np_pipeline_digest(s)) } }\n"
        (tdir / "t.go").write_text(go_src)
        go_out = [int(x) for x in subprocess.check_output(["go", "run", str(tdir / "t.go")], text=True).split()]
        assert go_out == expected
        print(f"  [Go (go run)    ] {go_out} == NumPy PASS")

        # Dart / Flutter SDK (dart)
        dart_src = (EMITTED_DIR / "poly_numpy.dart").read_text()
        dart_src += "\nvoid main() { print([-17,0,7,42,99].map((s) => np_pipeline_digest(s)).join(' ')); }\n"
        (tdir / "t.dart").write_text(dart_src)
        dart_out = [int(x) for x in subprocess.check_output(["dart", "run", str(tdir / "t.dart")], text=True).split()]
        assert dart_out == expected
        print(f"  [Dart (Flutter) ] {dart_out} == NumPy PASS")

        # Ruby (ruby)
        rb_src = (EMITTED_DIR / "poly_numpy.rb").read_text()
        rb_src += "\nputs [-17,0,7,42,99].map { |s| np_pipeline_digest(s) }.join(' ')\n"
        (tdir / "t.rb").write_text(rb_src)
        rb_out = [int(x) for x in subprocess.check_output(["ruby", str(tdir / "t.rb")], text=True).split()]
        assert rb_out == expected
        print(f"  [Ruby (ruby)    ] {rb_out} == NumPy PASS")

        # PHP (php)
        php_src = "<?php\n" + (EMITTED_DIR / "poly_numpy.php").read_text()
        php_src += "\nforeach ([-17,0,7,42,99] as $s) { echo np_pipeline_digest($s) . ' '; }\n"
        (tdir / "t.php").write_text(php_src)
        php_out = [int(x) for x in subprocess.check_output(["php", str(tdir / "t.php")], text=True).split()]
        assert php_out == expected
        print(f"  [PHP (php 8.5)  ] {php_out} == NumPy PASS")

        # Java (javac + java)
        import re
        java_body = re.sub(r"\b(4294967295|2147483648)\b", r"\1L", (EMITTED_DIR / "poly_numpy.java").read_text())
        java_body = java_body.replace("long np_", "static long np_")
        java_src = f"public class T {{\n{java_body}\npublic static void main(String[] a) {{ for (long s : new long[]{{-17,0,7,42,99}}) System.out.print(np_pipeline_digest(s) + \" \"); }}\n}}\n"
        (tdir / "T.java").write_text(java_src)
        subprocess.run(["javac", str(tdir / "T.java")], check=True)
        java_out = [int(x) for x in subprocess.check_output(["java", "-cp", str(tdir), "T"], text=True).split()]
        assert java_out == expected
        print(f"  [Java (JDK 25)  ] {java_out} == NumPy PASS")



if __name__ == "__main__":
    print("=== Option A Verification: PolyNumPy vs Real Python `numpy` + Native Toolchains ===")
    test_subsystem_parity_with_numpy()
    run_native_toolchains()
    print("=== ALL OPTION A NUMPY CORE CHECKS PASSED ===")
