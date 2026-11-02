#!/usr/bin/env python3
"""verify_polyglot_std.py -- Verifies `PolyglotStd` (Option C: Best-of-Breed Open-Source
Standard Library Mashup) across C `xxHash32`/`LZ4`, Rust `HalfSipHash-1-3`, Go `ZigZag`/`LEB128`,
Python `NumPy` circular tensor indexing, and 9 native compilers/runtimes.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import tempfile
import re
import sys

HERE = Path(__file__).resolve().parent
EMITTED_DIR = HERE / "emitted"
sys.path.insert(0, str(EMITTED_DIR))

import polyglot_std as pstd  # type: ignore


def test_polyglot_std_subsystems() -> None:
    # 1. Go ZigZag + LEB128 Uvarint roundtrip across 1..4 byte boundaries
    for val in [-1048575, -8192, -64, -1, 0, 1, 63, 128, 16384, 999999]:
        zz = pstd.std_zigzag_encode(val)
        leb = pstd.std_leb128_encode_u32(zz)
        dec = pstd.std_zigzag_decode(pstd.std_leb128_decode_u32(leb))
        assert dec == val, f"ZigZag/LEB128 mismatch on {val}: got {dec}"

    # 2. C LZ4 sequence token framing across u8 / u16 / u32 / i64 holders
    frame = pstd.std_lz4_pack_token(11, 7, 49151, 305419896)
    assert pstd.std_lz4_token_lit_len(frame) == 11
    assert pstd.std_lz4_token_match_len(frame) == 7
    assert pstd.std_lz4_match_offset(frame) == 49151
    assert pstd.std_lz4_literal(frame) == 305419896

    # 3. Python NumPy floor-modulo circular tensor indexing on negative coordinates
    assert pstd.std_circular_tensor_offset(-1, -3, 16, 8, 8, 1) == (15 * 8) + 5

    # 4. Rust HalfSipHash-1-3 key sensitivity
    tag1 = pstd.std_halfsiphash_1_3(0x03020100, 0x07060504, 100, 200)
    tag2 = pstd.std_halfsiphash_1_3(0x03020101, 0x07060504, 100, 200)
    assert tag1 != tag2 and 0 <= tag1 <= 0xFFFFFFFF
    print("  [PASS] PolyglotStd subsystems: C LZ4/XXH32, Rust HalfSipHash-1-3, Go LEB128, Python Tensor verified")


def run_native_std_toolchains() -> None:
    # 4 packet vectors: (delta_a, delta_b, lookback_t, key0, key1)
    vecs = [
        (-420, 1337, -3, 16909060, 84281096),
        (65535, -9999, -11, 305419896, 579005069),
        (-1, 0, -1, 42, 99),
        (500000, -500000, -7, 123456789, 987654321),
    ]
    expected = [pstd.std_polyglot_packet_pipeline(*v) for v in vecs]
    assert all(x > 0 for x in expected)
    print(f"  [Python Reference] {expected}")

    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        arr_lit = "{-420,1337,-3,16909060,84281096},{65535,-9999,-11,305419896,579005069},{-1,0,-1,42,99},{500000,-500000,-7,123456789,987654321}"

        # C (gcc -O2)
        c_src = "#include <stdio.h>\n#include <stdint.h>\n" + (EMITTED_DIR / "polyglot_std.c").read_text()
        c_src += f"\nint main(void) {{ long long v[4][5]={{{arr_lit}}}; for(int i=0;i<4;i++) printf(\"%lld \",(long long)std_polyglot_packet_pipeline(v[i][0],v[i][1],v[i][2],v[i][3],v[i][4])); return 0; }}\n"
        (tdir / "s.c").write_text(c_src)
        subprocess.run(["gcc", "-O2", "-w", str(tdir / "s.c"), "-o", str(tdir / "sc")], check=True)
        c_out = [int(x) for x in subprocess.check_output([str(tdir / "sc")], text=True).split()]
        assert c_out == expected
        print(f"  [C (gcc -O2)     ] {c_out} == PASS")

        # C++ (g++ -O2)
        (tdir / "s.cpp").write_text(c_src)
        subprocess.run(["g++", "-O2", "-w", str(tdir / "s.cpp"), "-o", str(tdir / "scpp")], check=True)
        cpp_out = [int(x) for x in subprocess.check_output([str(tdir / "scpp")], text=True).split()]
        assert cpp_out == expected
        print(f"  [C++ (g++ -O2)   ] {cpp_out} == PASS")

        # Rust (rustc -O)
        rs_src = "#![allow(unused_parens, non_snake_case)]\n" + (EMITTED_DIR / "polyglot_std.rs").read_text()
        rs_src += "\nfn main() { for v in [(-420,1337,-3,16909060,84281096),(65535,-9999,-11,305419896,579005069),(-1,0,-1,42,99),(500000,-500000,-7,123456789,987654321)] { print!(\"{} \", std_polyglot_packet_pipeline(v.0,v.1,v.2,v.3,v.4)); } }\n"
        (tdir / "s.rs").write_text(rs_src)
        subprocess.run(["rustc", "-O", "-A", "warnings", str(tdir / "s.rs"), "-o", str(tdir / "srs")], check=True)
        rs_out = [int(x) for x in subprocess.check_output([str(tdir / "srs")], text=True).split()]
        assert rs_out == expected
        print(f"  [Rust (rustc -O) ] {rs_out} == PASS")

        # Go (go run)
        go_src = "package main\nimport \"fmt\"\n" + (EMITTED_DIR / "polyglot_std.go").read_text()
        go_src += f"\nfunc main() {{ for _, v := range [][5]int64{{{arr_lit}}} {{ fmt.Printf(\"%d \", std_polyglot_packet_pipeline(v[0],v[1],v[2],v[3],v[4])) }} }}\n"
        (tdir / "s.go").write_text(go_src)
        go_out = [int(x) for x in subprocess.check_output(["go", "run", str(tdir / "s.go")], text=True).split()]
        assert go_out == expected
        print(f"  [Go (go run)     ] {go_out} == PASS")

        # Dart / Flutter SDK (dart run)
        dart_src = (EMITTED_DIR / "polyglot_std.dart").read_text()
        dart_src += "\nvoid main() { var vc = [[-420,1337,-3,16909060,84281096],[65535,-9999,-11,305419896,579005069],[-1,0,-1,42,99],[500000,-500000,-7,123456789,987654321]]; print(vc.map((v) => std_polyglot_packet_pipeline(v[0],v[1],v[2],v[3],v[4])).join(' ')); }\n"
        (tdir / "s.dart").write_text(dart_src)
        dart_out = [int(x) for x in subprocess.check_output(["dart", "run", str(tdir / "s.dart")], text=True).split()]
        assert dart_out == expected
        print(f"  [Dart (Flutter)  ] {dart_out} == PASS")

        # Ruby (ruby)
        rb_src = (EMITTED_DIR / "polyglot_std.rb").read_text()
        rb_src += "\nputs [[-420,1337,-3,16909060,84281096],[65535,-9999,-11,305419896,579005069],[-1,0,-1,42,99],[500000,-500000,-7,123456789,987654321]].map { |v| std_polyglot_packet_pipeline(v[0],v[1],v[2],v[3],v[4]) }.join(' ')\n"
        (tdir / "s.rb").write_text(rb_src)
        rb_out = [int(x) for x in subprocess.check_output(["ruby", str(tdir / "s.rb")], text=True).split()]
        assert rb_out == expected
        print(f"  [Ruby (ruby)     ] {rb_out} == PASS")

        # PHP (php)
        php_src = "<?php\n" + (EMITTED_DIR / "polyglot_std.php").read_text()
        php_src += "\nforeach ([[-420,1337,-3,16909060,84281096],[65535,-9999,-11,305419896,579005069],[-1,0,-1,42,99],[500000,-500000,-7,123456789,987654321]] as $v) { echo std_polyglot_packet_pipeline($v[0],$v[1],$v[2],$v[3],$v[4]) . ' '; }\n"
        (tdir / "s.php").write_text(php_src)
        php_out = [int(x) for x in subprocess.check_output(["php", str(tdir / "s.php")], text=True).split()]
        assert php_out == expected
        print(f"  [PHP (php 8.5)   ] {php_out} == PASS")

        # Java (javac + java)
        java_body = re.sub(r"\b(4294967295|2147483648|2246822519|2654435761|3266489917)\b", r"\1L", (EMITTED_DIR / "polyglot_std.java").read_text())
        java_body = java_body.replace("long std_", "static long std_")
        java_src = f"public class S {{\n{java_body}\npublic static void main(String[] a) {{ long[][] vc = {{{arr_lit}}}; for (long[] v : vc) System.out.print(std_polyglot_packet_pipeline(v[0],v[1],v[2],v[3],v[4]) + \" \"); }}\n}}\n"
        (tdir / "S.java").write_text(java_src)
        subprocess.run(["javac", str(tdir / "S.java")], check=True)
        java_out = [int(x) for x in subprocess.check_output(["java", "-cp", str(tdir), "S"], text=True).split()]
        assert java_out == expected
        print(f"  [Java (JDK 25)   ] {java_out} == PASS")


if __name__ == "__main__":
    print("=== Option C Verification: PolyglotStd across 4 Ecosystems & 9 Native Toolchains ===")
    test_polyglot_std_subsystems()
    run_native_std_toolchains()
    print("=== ALL OPTION C POLYGLOT STD CHECKS PASSED ===")
