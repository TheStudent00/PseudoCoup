// 03_rust_umath_ufunc.rs -- NumPy `umath` Packed Tensor Buffer & Broadcasted `ufunc` Engine (Rust)

fn np_pack_buf4(e0: i64, e1: i64, e2: i64, e3: i64) -> i64 {
    let u0: i64 = e0 & 65535;
    let u1: i64 = (e1 & 65535) << 16;
    let u2: i64 = (e2 & 65535) << 32;
    let u3: i64 = (e3 & 65535) << 48;
    return u0 | u1 | u2 | u3;
}

fn np_buf4_get(buf: i64, idx: i32) -> i64 {
    let shift: i32 = (idx & 3) * 16;
    let raw: i64 = (buf >> shift) & 65535;
    return (raw ^ 32768) - 32768;
}

fn np_buf8_get(buf_lo: i64, buf_hi: i64, idx: i64) -> i64 {
    let word: i64 = (if idx < 4 { buf_lo } else { buf_hi });
    let lane: i32 = idx & 3;
    return np_buf4_get(word, lane);
}

fn np_apply_ufunc(op_code: i32, a: i64, b: i64) -> i64 {
    if op_code == 0 {
        return a + b;
    }
    if op_code == 1 {
        return a - b;
    }
    if op_code == 2 {
        return a * b;
    }
    if op_code == 3 {
        return (if a < b { a } else { b });
    }
    if op_code == 4 {
        return (if a > b { a } else { b });
    }
    return a ^ b;
}

fn np_ufunc_2x2(buf_a: i64, shape_a: i64, str_a: i64, buf_b: i64, shape_b: i64, str_b: i64, op_code: i32) -> i64 {
    let out_shape: i64 = np_broadcast_shapes(shape_a, shape_b);
    let bstr_a: i64 = np_broadcast_strides(shape_a, str_a, out_shape);
    let bstr_b: i64 = np_broadcast_strides(shape_b, str_b, out_shape);
    let a00: i64 = np_buf4_get(buf_a, np_flat_offset(0, bstr_a, 0, 0, 0));
    let b00: i64 = np_buf4_get(buf_b, np_flat_offset(0, bstr_b, 0, 0, 0));
    let a01: i64 = np_buf4_get(buf_a, np_flat_offset(0, bstr_a, 0, 0, 1));
    let b01: i64 = np_buf4_get(buf_b, np_flat_offset(0, bstr_b, 0, 0, 1));
    let a10: i64 = np_buf4_get(buf_a, np_flat_offset(0, bstr_a, 0, 1, 0));
    let b10: i64 = np_buf4_get(buf_b, np_flat_offset(0, bstr_b, 0, 1, 0));
    let a11: i64 = np_buf4_get(buf_a, np_flat_offset(0, bstr_a, 0, 1, 1));
    let b11: i64 = np_buf4_get(buf_b, np_flat_offset(0, bstr_b, 0, 1, 1));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

fn np_clip_scalar(v: i64, a_min: i64, a_max: i64) -> i64 {
    return (if v < a_min { a_min } else { (if v > a_max { a_max } else { v }) });
}

fn np_clip_buf4(buf: i64, a_min: i64, a_max: i64) -> i64 {
    let c0: i64 = np_clip_scalar(np_buf4_get(buf, 0), a_min, a_max);
    let c1: i64 = np_clip_scalar(np_buf4_get(buf, 1), a_min, a_max);
    let c2: i64 = np_clip_scalar(np_buf4_get(buf, 2), a_min, a_max);
    let c3: i64 = np_clip_scalar(np_buf4_get(buf, 3), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}
