function np_pack_vec3(d0: number, d1: number, d2: number): number {
    let u0: number = (d0 & 65535);
    let u1: number = (d1 & 65535);
    let u2: number = (d2 & 65535);
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2);
}

function np_get_axis(vec3: number, axis: number): number {
    let shift: number = (((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) & 4294967295) ^ 2147483648) - 2147483648);
    let raw: number = ((vec3 >> (shift & 63)) & 65535);
    let signed_val: number = (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
    return signed_val;
}

function np_c_strides(shape3: number): number {
    let d1: number = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let d2: number = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((d1 * d2), d2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_f_strides(shape3: number): number {
    let d0: number = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let d1: number = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), d0, (d0 * d1));
}

function np_swapaxes_vec3(vec3: number, ax1: number, ax2: number): number {
    let v0: number = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let v1: number = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let v2: number = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let n0: number = (((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) & 4294967295) ^ 2147483648) - 2147483648);
    let n1: number = (((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) & 4294967295) ^ 2147483648) - 2147483648);
    let n2: number = (((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

function np_flip_offset(base_off: number, shape3: number, strides3: number, axis: number): number {
    let dim: number = np_get_axis(shape3, axis);
    let st: number = np_get_axis(strides3, axis);
    return (base_off + ((dim - 1) * st));
}

function np_flip_strides(strides3: number, axis: number): number {
    let s0: number = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let s1: number = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let s2: number = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let n0: number = (((((axis == 0) ? -s0 : s0) & 4294967295) ^ 2147483648) - 2147483648);
    let n1: number = (((((axis == 1) ? -s1 : s1) & 4294967295) ^ 2147483648) - 2147483648);
    let n2: number = (((((axis == 2) ? -s2 : s2) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

function np_flat_offset(base_off: number, strides3: number, i0: number, i1: number, i2: number): number {
    let s0: number = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let s1: number = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let s2: number = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2));
}

function np_broadcast_axis(da: number, db: number): number {
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

function np_broadcast_shapes(shape_a: number, shape_b: number): number {
    let d0: number = np_broadcast_axis(np_get_axis(shape_a, (((0 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    let d1: number = np_broadcast_axis(np_get_axis(shape_a, (((1 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    let d2: number = np_broadcast_axis(np_get_axis(shape_a, (((2 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1;
    }
    return np_pack_vec3((((d0 & 4294967295) ^ 2147483648) - 2147483648), (((d1 & 4294967295) ^ 2147483648) - 2147483648), (((d2 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_broadcast_strides(src_shape: number, src_strides: number, target_shape: number): number {
    let sd0: number = np_get_axis(src_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let sd1: number = np_get_axis(src_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let sd2: number = np_get_axis(src_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let td0: number = np_get_axis(target_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let td1: number = np_get_axis(target_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let td2: number = np_get_axis(target_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let s0: number = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    let s1: number = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    let s2: number = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    return np_pack_vec3((((s0 & 4294967295) ^ 2147483648) - 2147483648), (((s1 & 4294967295) ^ 2147483648) - 2147483648), (((s2 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_normalize_index(idx: number, dim: number, mode: number): number {
    if ((mode == 1)) {
        return ((((idx ^ dim) < 0) && ((idx % dim) != 0)) ? ((idx % dim) + dim) : (idx % dim));
    }
    if ((mode == 2)) {
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx));
    }
    let norm: number = ((idx < 0) ? (idx + dim) : idx);
    if (((norm < 0) || (norm >= dim))) {
        return -1;
    }
    return norm;
}

function np_ravel_multi_index(coords3: number, shape3: number, mode: number): number {
    let d0: number = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let d1: number = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let d2: number = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let i0: number = np_normalize_index(np_get_axis(coords3, (((0 & 4294967295) ^ 2147483648) - 2147483648)), d0, mode);
    let i1: number = np_normalize_index(np_get_axis(coords3, (((1 & 4294967295) ^ 2147483648) - 2147483648)), d1, mode);
    let i2: number = np_normalize_index(np_get_axis(coords3, (((2 & 4294967295) ^ 2147483648) - 2147483648)), d2, mode);
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1;
    }
    return ((((i0 * d1) + i1) * d2) + i2);
}

function np_unravel_index(flat_idx: number, shape3: number): number {
    let d1: number = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let d2: number = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let i2: number = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx % d2) + d2) : (flat_idx % d2));
    let rem: number = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx / d2) - 1) : (flat_idx / d2));
    let i1: number = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem % d1) + d1) : (rem % d1));
    let i0: number = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem / d1) - 1) : (rem / d1));
    return np_pack_vec3((((i0 & 4294967295) ^ 2147483648) - 2147483648), (((i1 & 4294967295) ^ 2147483648) - 2147483648), (((i2 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_pack_buf4(e0: number, e1: number, e2: number, e3: number): number {
    let u0: number = (e0 & 65535);
    let u1: number = ((e1 & 65535) << (16 & 63));
    let u2: number = ((e2 & 65535) << (32 & 63));
    let u3: number = ((e3 & 65535) << (48 & 63));
    return (((u0 | u1) | u2) | u3);
}

function np_buf4_get(buf: number, idx: number): number {
    let shift: number = (((((idx & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    let raw: number = ((buf >> (shift & 63)) & 65535);
    return ((raw ^ 32768) - 32768);
}

function np_buf8_get(buf_lo: number, buf_hi: number, idx: number): number {
    let word: number = ((idx < 4) ? buf_lo : buf_hi);
    let lane: number = ((((idx & 3) & 4294967295) ^ 2147483648) - 2147483648);
    return np_buf4_get(word, lane);
}

function np_apply_ufunc(op_code: number, a: number, b: number): number {
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
        return ((a < b) ? a : b);
    }
    if ((op_code == 4)) {
        return ((a > b) ? a : b);
    }
    return (a ^ b);
}

function np_ufunc_2x2(buf_a: number, shape_a: number, str_a: number, buf_b: number, shape_b: number, str_b: number, op_code: number): number {
    let out_shape: number = np_broadcast_shapes(shape_a, shape_b);
    let bstr_a: number = np_broadcast_strides(shape_a, str_a, out_shape);
    let bstr_b: number = np_broadcast_strides(shape_b, str_b, out_shape);
    let a00: number = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b00: number = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a01: number = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b01: number = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a10: number = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b10: number = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a11: number = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b11: number = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

function np_clip_scalar(v: number, a_min: number, a_max: number): number {
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v));
}

function np_clip_buf4(buf: number, a_min: number, a_max: number): number {
    let c0: number = np_clip_scalar(np_buf4_get(buf, (((0 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    let c1: number = np_clip_scalar(np_buf4_get(buf, (((1 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    let c2: number = np_clip_scalar(np_buf4_get(buf, (((2 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    let c3: number = np_clip_scalar(np_buf4_get(buf, (((3 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}

function np_matmul_2x2(buf_a: number, off_a: number, str_a: number, buf_b: number, off_b: number, str_b: number): number {
    let a00: number = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a01: number = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a10: number = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let a11: number = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b00: number = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b01: number = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b10: number = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let b11: number = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let c00: number = ((a00 * b00) + (a01 * b10));
    let c01: number = ((a00 * b01) + (a01 * b11));
    let c10: number = ((a10 * b00) + (a11 * b10));
    let c11: number = ((a10 * b01) + (a11 * b11));
    return np_pack_buf4(c00, c01, c10, c11);
}

function np_reduce_pair(a: number, b: number, red_op: number): number {
    if ((red_op == 0)) {
        return (a + b);
    }
    if ((red_op == 1)) {
        return ((a >= b) ? a : b);
    }
    return ((a <= b) ? a : b);
}

function np_reduce_all_2x2(buf: number, base_off: number, strides3: number, red_op: number): number {
    let v0: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v1: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v2: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v3: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    if ((red_op == 3)) {
        let best_i: number = ((v1 > v0) ? 1 : 0);
        let best_v: number = ((v1 > v0) ? v1 : v0);
        best_i = ((v2 > best_v) ? 2 : best_i);
        best_v = ((v2 > best_v) ? v2 : best_v);
        best_i = ((v3 > best_v) ? 3 : best_i);
        return best_i;
    }
    let r01: number = np_reduce_pair(v0, v1, red_op);
    let r23: number = np_reduce_pair(v2, v3, red_op);
    return np_reduce_pair(r01, r23, red_op);
}

function np_reduce_axis_2x2(buf: number, base_off: number, strides3: number, axis: number, red_op: number): number {
    let v00: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v01: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v10: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let v11: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let r0: number = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op));
    let r1: number = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op));
    return np_pack_vec3((((r0 & 4294967295) ^ 2147483648) - 2147483648), (((r1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_trace_2x2(buf: number, base_off: number, strides3: number): number {
    let d00: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    let d11: number = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return (d00 + d11);
}

function np_select_idx(r0: number, r1: number, target: number): number {
    let alt: number = ((r1 == target) ? 1 : 2);
    return ((r0 == target) ? 0 : alt);
}

function np_argsort_vec3(vec3: number): number {
    let a0: number = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let a1: number = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let a2: number = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let r0: number = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0));
    let r1: number = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0));
    let p0: number = np_select_idx(r0, r1, 0);
    let p1: number = np_select_idx(r0, r1, 1);
    let p2: number = np_select_idx(r0, r1, 2);
    return np_pack_vec3((((p0 & 4294967295) ^ 2147483648) - 2147483648), (((p1 & 4294967295) ^ 2147483648) - 2147483648), (((p2 & 4294967295) ^ 2147483648) - 2147483648));
}

function np_pipeline_digest(seed: number): number {
    let sh_col: number = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let sh_row: number = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let sh_2x2: number = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let st_2x2: number = np_c_strides(sh_2x2);
    let buf_col: number = np_pack_buf4((seed + 3), (seed - 5), 0, 0);
    let buf_row: number = np_pack_buf4(((seed * 2) + 1), (-seed + 7), 0, 0);
    let m_a: number = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let m_b: number = np_pack_buf4((seed + 2), (-seed - 3), ((seed * 3) - 1), (seed + 4));
    let st_a_t: number = np_swapaxes_vec3(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    let off_b_f: number = np_flip_offset(0, sh_2x2, st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let st_b_f: number = np_flip_strides(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    let m_c: number = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500);
    let wrap_idx: number = np_ravel_multi_index(np_pack_vec3((((-1 & 4294967295) ^ 2147483648) - 2147483648), (-seed - 7), (seed + 9)), np_pack_vec3((((4 & 4294967295) ^ 2147483648) - 2147483648), (((5 & 4294967295) ^ 2147483648) - 2147483648), (((6 & 4294967295) ^ 2147483648) - 2147483648)), 1);
    let s_all: number = np_reduce_all_2x2(m_c, 0, st_2x2, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    let amax: number = np_reduce_all_2x2(m_c, 0, st_2x2, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    let tr: number = np_trace_2x2(m_c, 0, st_2x2);
    let asort: number = np_argsort_vec3(np_pack_vec3((((s_all & 4294967295) ^ 2147483648) - 2147483648), (((tr & 4294967295) ^ 2147483648) - 2147483648), (((wrap_idx & 4294967295) ^ 2147483648) - 2147483648)));
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort);
}
