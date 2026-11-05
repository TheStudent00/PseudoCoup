fn np_pack_vec3(d0: i64, d1: i64, d2: i64) -> i64 {
    let mut u0: i64 = (d0 & 65535);
    let mut u1: i64 = (d1 & 65535);
    let mut u2: i64 = (d2 & 65535);
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2);
}

fn np_get_axis(vec3: i64, axis: i64) -> i64 {
    let mut shift: i64 = (((if (axis == 0) { 32 } else { (if (axis == 1) { 16 } else { 0 }) }) << 32) >> 32);
    let mut raw: i64 = ((vec3 >> (shift & 63)) & 65535);
    let mut signed_val: i64 = ((((raw ^ 32768) - 32768) << 32) >> 32);
    return signed_val;
}

fn np_c_strides(shape3: i64) -> i64 {
    let mut d1: i64 = np_get_axis(shape3, ((1 << 32) >> 32));
    let mut d2: i64 = np_get_axis(shape3, ((2 << 32) >> 32));
    return np_pack_vec3((d1 * d2), d2, ((1 << 32) >> 32));
}

fn np_f_strides(shape3: i64) -> i64 {
    let mut d0: i64 = np_get_axis(shape3, ((0 << 32) >> 32));
    let mut d1: i64 = np_get_axis(shape3, ((1 << 32) >> 32));
    return np_pack_vec3(((1 << 32) >> 32), d0, (d0 * d1));
}

fn np_swapaxes_vec3(vec3: i64, ax1: i64, ax2: i64) -> i64 {
    let mut v0: i64 = np_get_axis(vec3, ((0 << 32) >> 32));
    let mut v1: i64 = np_get_axis(vec3, ((1 << 32) >> 32));
    let mut v2: i64 = np_get_axis(vec3, ((2 << 32) >> 32));
    let mut n0: i64 = (((if (ax1 == 0) { np_get_axis(vec3, ax2) } else { (if (ax2 == 0) { np_get_axis(vec3, ax1) } else { v0 }) }) << 32) >> 32);
    let mut n1: i64 = (((if (ax1 == 1) { np_get_axis(vec3, ax2) } else { (if (ax2 == 1) { np_get_axis(vec3, ax1) } else { v1 }) }) << 32) >> 32);
    let mut n2: i64 = (((if (ax1 == 2) { np_get_axis(vec3, ax2) } else { (if (ax2 == 2) { np_get_axis(vec3, ax1) } else { v2 }) }) << 32) >> 32);
    return np_pack_vec3(n0, n1, n2);
}

fn np_flip_offset(base_off: i64, shape3: i64, strides3: i64, axis: i64) -> i64 {
    let mut dim: i64 = np_get_axis(shape3, axis);
    let mut st: i64 = np_get_axis(strides3, axis);
    return (base_off + ((dim - 1) * st));
}

fn np_flip_strides(strides3: i64, axis: i64) -> i64 {
    let mut s0: i64 = np_get_axis(strides3, ((0 << 32) >> 32));
    let mut s1: i64 = np_get_axis(strides3, ((1 << 32) >> 32));
    let mut s2: i64 = np_get_axis(strides3, ((2 << 32) >> 32));
    let mut n0: i64 = (((if (axis == 0) { -s0 } else { s0 }) << 32) >> 32);
    let mut n1: i64 = (((if (axis == 1) { -s1 } else { s1 }) << 32) >> 32);
    let mut n2: i64 = (((if (axis == 2) { -s2 } else { s2 }) << 32) >> 32);
    return np_pack_vec3(n0, n1, n2);
}

fn np_flat_offset(base_off: i64, strides3: i64, i0: i64, i1: i64, i2: i64) -> i64 {
    let mut s0: i64 = np_get_axis(strides3, ((0 << 32) >> 32));
    let mut s1: i64 = np_get_axis(strides3, ((1 << 32) >> 32));
    let mut s2: i64 = np_get_axis(strides3, ((2 << 32) >> 32));
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2));
}

fn np_broadcast_axis(da: i64, db: i64) -> i64 {
    if ((da == db)) {
        return da;
    }
    if ((da == 1)) {
        return db;
    }
    if ((db == 1)) {
        return da;
    }
    return -1;
}

fn np_broadcast_shapes(shape_a: i64, shape_b: i64) -> i64 {
    let mut d0: i64 = np_broadcast_axis(np_get_axis(shape_a, ((0 << 32) >> 32)), np_get_axis(shape_b, ((0 << 32) >> 32)));
    let mut d1: i64 = np_broadcast_axis(np_get_axis(shape_a, ((1 << 32) >> 32)), np_get_axis(shape_b, ((1 << 32) >> 32)));
    let mut d2: i64 = np_broadcast_axis(np_get_axis(shape_a, ((2 << 32) >> 32)), np_get_axis(shape_b, ((2 << 32) >> 32)));
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1;
    }
    return np_pack_vec3(((d0 << 32) >> 32), ((d1 << 32) >> 32), ((d2 << 32) >> 32));
}

fn np_broadcast_strides(src_shape: i64, src_strides: i64, target_shape: i64) -> i64 {
    let mut sd0: i64 = np_get_axis(src_shape, ((0 << 32) >> 32));
    let mut sd1: i64 = np_get_axis(src_shape, ((1 << 32) >> 32));
    let mut sd2: i64 = np_get_axis(src_shape, ((2 << 32) >> 32));
    let mut td0: i64 = np_get_axis(target_shape, ((0 << 32) >> 32));
    let mut td1: i64 = np_get_axis(target_shape, ((1 << 32) >> 32));
    let mut td2: i64 = np_get_axis(target_shape, ((2 << 32) >> 32));
    let mut s0: i64 = (if ((sd0 == 1) && (td0 > 1)) { 0 } else { np_get_axis(src_strides, ((0 << 32) >> 32)) });
    let mut s1: i64 = (if ((sd1 == 1) && (td1 > 1)) { 0 } else { np_get_axis(src_strides, ((1 << 32) >> 32)) });
    let mut s2: i64 = (if ((sd2 == 1) && (td2 > 1)) { 0 } else { np_get_axis(src_strides, ((2 << 32) >> 32)) });
    return np_pack_vec3(((s0 << 32) >> 32), ((s1 << 32) >> 32), ((s2 << 32) >> 32));
}

fn np_normalize_index(idx: i64, dim: i64, mode: i64) -> i64 {
    if ((mode == 1)) {
        return (if (((idx ^ dim) < 0) && ((idx % dim) != 0)) { ((idx % dim) + dim) } else { (idx % dim) });
    }
    if ((mode == 2)) {
        return (if (idx < 0) { 0 } else { (if (idx >= dim) { (dim - 1) } else { idx }) });
    }
    let mut norm: i64 = (if (idx < 0) { (idx + dim) } else { idx });
    if (((norm < 0) || (norm >= dim))) {
        return -1;
    }
    return norm;
}

fn np_ravel_multi_index(coords3: i64, shape3: i64, mode: i64) -> i64 {
    let mut d0: i64 = np_get_axis(shape3, ((0 << 32) >> 32));
    let mut d1: i64 = np_get_axis(shape3, ((1 << 32) >> 32));
    let mut d2: i64 = np_get_axis(shape3, ((2 << 32) >> 32));
    let mut i0: i64 = np_normalize_index(np_get_axis(coords3, ((0 << 32) >> 32)), d0, mode);
    let mut i1: i64 = np_normalize_index(np_get_axis(coords3, ((1 << 32) >> 32)), d1, mode);
    let mut i2: i64 = np_normalize_index(np_get_axis(coords3, ((2 << 32) >> 32)), d2, mode);
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1;
    }
    return ((((i0 * d1) + i1) * d2) + i2);
}

fn np_unravel_index(flat_idx: i64, shape3: i64) -> i64 {
    let mut d1: i64 = np_get_axis(shape3, ((1 << 32) >> 32));
    let mut d2: i64 = np_get_axis(shape3, ((2 << 32) >> 32));
    let mut i2: i64 = (if (((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) { ((flat_idx % d2) + d2) } else { (flat_idx % d2) });
    let mut rem: i64 = (if (((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) { ((flat_idx / d2) - 1) } else { (flat_idx / d2) });
    let mut i1: i64 = (if (((rem ^ d1) < 0) && ((rem % d1) != 0)) { ((rem % d1) + d1) } else { (rem % d1) });
    let mut i0: i64 = (if (((rem ^ d1) < 0) && ((rem % d1) != 0)) { ((rem / d1) - 1) } else { (rem / d1) });
    return np_pack_vec3(((i0 << 32) >> 32), ((i1 << 32) >> 32), ((i2 << 32) >> 32));
}

fn np_pack_buf4(e0: i64, e1: i64, e2: i64, e3: i64) -> i64 {
    let mut u0: i64 = (e0 & 65535);
    let mut u1: i64 = ((e1 & 65535) << (16 & 63));
    let mut u2: i64 = ((e2 & 65535) << (32 & 63));
    let mut u3: i64 = ((e3 & 65535) << (48 & 63));
    return (((u0 | u1) | u2) | u3);
}

fn np_buf4_get(buf: i64, idx: i64) -> i64 {
    let mut shift: i64 = ((((idx & 3) * 16) << 32) >> 32);
    let mut raw: i64 = ((buf >> (shift & 63)) & 65535);
    return ((raw ^ 32768) - 32768);
}

fn np_buf8_get(buf_lo: i64, buf_hi: i64, idx: i64) -> i64 {
    let mut word: i64 = (if (idx < 4) { buf_lo } else { buf_hi });
    let mut lane: i64 = (((idx & 3) << 32) >> 32);
    return np_buf4_get(word, lane);
}

fn np_apply_ufunc(op_code: i64, a: i64, b: i64) -> i64 {
    if ((op_code == 0)) {
        return (a + b);
    }
    if ((op_code == 1)) {
        return (a - b);
    }
    if ((op_code == 2)) {
        return (a * b);
    }
    if ((op_code == 3)) {
        return (if (a < b) { a } else { b });
    }
    if ((op_code == 4)) {
        return (if (a > b) { a } else { b });
    }
    return (a ^ b);
}

fn np_ufunc_2x2(buf_a: i64, shape_a: i64, str_a: i64, buf_b: i64, shape_b: i64, str_b: i64, op_code: i64) -> i64 {
    let mut out_shape: i64 = np_broadcast_shapes(shape_a, shape_b);
    let mut bstr_a: i64 = np_broadcast_strides(shape_a, str_a, out_shape);
    let mut bstr_b: i64 = np_broadcast_strides(shape_b, str_b, out_shape);
    let mut a00: i64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut b00: i64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut a01: i64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut b01: i64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut a10: i64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut b10: i64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut a11: i64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut b11: i64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

fn np_clip_scalar(v: i64, a_min: i64, a_max: i64) -> i64 {
    return (if (v < a_min) { a_min } else { (if (v > a_max) { a_max } else { v }) });
}

fn np_clip_buf4(buf: i64, a_min: i64, a_max: i64) -> i64 {
    let mut c0: i64 = np_clip_scalar(np_buf4_get(buf, ((0 << 32) >> 32)), a_min, a_max);
    let mut c1: i64 = np_clip_scalar(np_buf4_get(buf, ((1 << 32) >> 32)), a_min, a_max);
    let mut c2: i64 = np_clip_scalar(np_buf4_get(buf, ((2 << 32) >> 32)), a_min, a_max);
    let mut c3: i64 = np_clip_scalar(np_buf4_get(buf, ((3 << 32) >> 32)), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}

fn np_matmul_2x2(buf_a: i64, off_a: i64, str_a: i64, buf_b: i64, off_b: i64, str_b: i64) -> i64 {
    let mut a00: i64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut a01: i64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut a10: i64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut a11: i64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut b00: i64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut b01: i64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut b10: i64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut b11: i64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut c00: i64 = ((a00 * b00) + (a01 * b10));
    let mut c01: i64 = ((a00 * b01) + (a01 * b11));
    let mut c10: i64 = ((a10 * b00) + (a11 * b10));
    let mut c11: i64 = ((a10 * b01) + (a11 * b11));
    return np_pack_buf4(c00, c01, c10, c11);
}

fn np_reduce_pair(a: i64, b: i64, red_op: i64) -> i64 {
    if ((red_op == 0)) {
        return (a + b);
    }
    if ((red_op == 1)) {
        return (if (a >= b) { a } else { b });
    }
    return (if (a <= b) { a } else { b });
}

fn np_reduce_all_2x2(buf: i64, base_off: i64, strides3: i64, red_op: i64) -> i64 {
    let mut v0: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut v1: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut v2: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut v3: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    if ((red_op == 3)) {
        let mut best_i: i64 = (if (v1 > v0) { 1 } else { 0 });
        let mut best_v: i64 = (if (v1 > v0) { v1 } else { v0 });
        best_i = (if (v2 > best_v) { 2 } else { best_i });
        best_v = (if (v2 > best_v) { v2 } else { best_v });
        best_i = (if (v3 > best_v) { 3 } else { best_i });
        return best_i;
    }
    let mut r01: i64 = np_reduce_pair(v0, v1, red_op);
    let mut r23: i64 = np_reduce_pair(v2, v3, red_op);
    return np_reduce_pair(r01, r23, red_op);
}

fn np_reduce_axis_2x2(buf: i64, base_off: i64, strides3: i64, axis: i64, red_op: i64) -> i64 {
    let mut v00: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut v01: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut v10: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut v11: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    let mut r0: i64 = (if (axis == 0) { np_reduce_pair(v00, v10, red_op) } else { np_reduce_pair(v00, v01, red_op) });
    let mut r1: i64 = (if (axis == 0) { np_reduce_pair(v01, v11, red_op) } else { np_reduce_pair(v10, v11, red_op) });
    return np_pack_vec3(((r0 << 32) >> 32), ((r1 << 32) >> 32), ((0 << 32) >> 32));
}

fn np_trace_2x2(buf: i64, base_off: i64, strides3: i64) -> i64 {
    let mut d00: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    let mut d11: i64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    return (d00 + d11);
}

fn np_select_idx(r0: i64, r1: i64, target: i64) -> i64 {
    let mut alt: i64 = (if (r1 == target) { 1 } else { 2 });
    return (if (r0 == target) { 0 } else { alt });
}

fn np_argsort_vec3(vec3: i64) -> i64 {
    let mut a0: i64 = np_get_axis(vec3, ((0 << 32) >> 32));
    let mut a1: i64 = np_get_axis(vec3, ((1 << 32) >> 32));
    let mut a2: i64 = np_get_axis(vec3, ((2 << 32) >> 32));
    let mut r0: i64 = ((if (a0 > a1) { 1 } else { 0 }) + (if (a0 > a2) { 1 } else { 0 }));
    let mut r1: i64 = ((if (a1 >= a0) { 1 } else { 0 }) + (if (a1 > a2) { 1 } else { 0 }));
    let mut p0: i64 = np_select_idx(r0, r1, 0);
    let mut p1: i64 = np_select_idx(r0, r1, 1);
    let mut p2: i64 = np_select_idx(r0, r1, 2);
    return np_pack_vec3(((p0 << 32) >> 32), ((p1 << 32) >> 32), ((p2 << 32) >> 32));
}

fn np_pipeline_digest(seed: i64) -> i64 {
    let mut sh_col: i64 = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((1 << 32) >> 32));
    let mut sh_row: i64 = np_pack_vec3(((1 << 32) >> 32), ((1 << 32) >> 32), ((2 << 32) >> 32));
    let mut sh_2x2: i64 = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((2 << 32) >> 32));
    let mut st_2x2: i64 = np_c_strides(sh_2x2);
    let mut buf_col: i64 = np_pack_buf4((seed + 3), (seed - 5), 0, 0);
    let mut buf_row: i64 = np_pack_buf4(((seed * 2) + 1), (-seed + 7), 0, 0);
    let mut m_a: i64 = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), ((0 << 32) >> 32));
    let mut m_b: i64 = np_pack_buf4((seed + 2), (-seed - 3), ((seed * 3) - 1), (seed + 4));
    let mut st_a_t: i64 = np_swapaxes_vec3(st_2x2, ((1 << 32) >> 32), ((2 << 32) >> 32));
    let mut off_b_f: i64 = np_flip_offset(0, sh_2x2, st_2x2, ((1 << 32) >> 32));
    let mut st_b_f: i64 = np_flip_strides(st_2x2, ((1 << 32) >> 32));
    let mut m_c: i64 = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500);
    let mut wrap_idx: i64 = np_ravel_multi_index(np_pack_vec3(((-1 << 32) >> 32), (-seed - 7), (seed + 9)), np_pack_vec3(((4 << 32) >> 32), ((5 << 32) >> 32), ((6 << 32) >> 32)), 1);
    let mut s_all: i64 = np_reduce_all_2x2(m_c, 0, st_2x2, ((0 << 32) >> 32));
    let mut amax: i64 = np_reduce_all_2x2(m_c, 0, st_2x2, ((3 << 32) >> 32));
    let mut tr: i64 = np_trace_2x2(m_c, 0, st_2x2);
    let mut asort: i64 = np_argsort_vec3(np_pack_vec3(((s_all << 32) >> 32), ((tr << 32) >> 32), ((wrap_idx << 32) >> 32)));
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort);
}
