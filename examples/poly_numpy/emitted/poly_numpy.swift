func np_pack_vec3(_ d0: Int64, _ d1: Int64, _ d2: Int64) -> Int64 {
    var u0: Int64 = (d0 & 65535)
    var u1: Int64 = (d1 & 65535)
    var u2: Int64 = (d2 & 65535)
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2)
}

func np_get_axis(_ vec3: Int64, _ axis: Int64) -> Int64 {
    var shift: Int64 = ((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) << 32) >> 32)
    var raw: Int64 = ((vec3 >> (shift & 63)) & 65535)
    var signed_val: Int64 = ((((raw ^ 32768) - 32768) << 32) >> 32)
    return signed_val
}

func np_c_strides(_ shape3: Int64) -> Int64 {
    var d1: Int64 = np_get_axis(shape3, ((1 << 32) >> 32))
    var d2: Int64 = np_get_axis(shape3, ((2 << 32) >> 32))
    return np_pack_vec3((d1 * d2), d2, ((1 << 32) >> 32))
}

func np_f_strides(_ shape3: Int64) -> Int64 {
    var d0: Int64 = np_get_axis(shape3, ((0 << 32) >> 32))
    var d1: Int64 = np_get_axis(shape3, ((1 << 32) >> 32))
    return np_pack_vec3(((1 << 32) >> 32), d0, (d0 * d1))
}

func np_swapaxes_vec3(_ vec3: Int64, _ ax1: Int64, _ ax2: Int64) -> Int64 {
    var v0: Int64 = np_get_axis(vec3, ((0 << 32) >> 32))
    var v1: Int64 = np_get_axis(vec3, ((1 << 32) >> 32))
    var v2: Int64 = np_get_axis(vec3, ((2 << 32) >> 32))
    var n0: Int64 = ((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) << 32) >> 32)
    var n1: Int64 = ((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) << 32) >> 32)
    var n2: Int64 = ((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) << 32) >> 32)
    return np_pack_vec3(n0, n1, n2)
}

func np_flip_offset(_ base_off: Int64, _ shape3: Int64, _ strides3: Int64, _ axis: Int64) -> Int64 {
    var dim: Int64 = np_get_axis(shape3, axis)
    var st: Int64 = np_get_axis(strides3, axis)
    return (base_off + ((dim - 1) * st))
}

func np_flip_strides(_ strides3: Int64, _ axis: Int64) -> Int64 {
    var s0: Int64 = np_get_axis(strides3, ((0 << 32) >> 32))
    var s1: Int64 = np_get_axis(strides3, ((1 << 32) >> 32))
    var s2: Int64 = np_get_axis(strides3, ((2 << 32) >> 32))
    var n0: Int64 = ((((axis == 0) ? -s0 : s0) << 32) >> 32)
    var n1: Int64 = ((((axis == 1) ? -s1 : s1) << 32) >> 32)
    var n2: Int64 = ((((axis == 2) ? -s2 : s2) << 32) >> 32)
    return np_pack_vec3(n0, n1, n2)
}

func np_flat_offset(_ base_off: Int64, _ strides3: Int64, _ i0: Int64, _ i1: Int64, _ i2: Int64) -> Int64 {
    var s0: Int64 = np_get_axis(strides3, ((0 << 32) >> 32))
    var s1: Int64 = np_get_axis(strides3, ((1 << 32) >> 32))
    var s2: Int64 = np_get_axis(strides3, ((2 << 32) >> 32))
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2))
}

func np_broadcast_axis(_ da: Int64, _ db: Int64) -> Int64 {
    if ((da == db)) {
        return da
    }
    if ((da == 1)) {
        return db
    }
    if ((db == 1)) {
        return da
    }
    return -1
}

func np_broadcast_shapes(_ shape_a: Int64, _ shape_b: Int64) -> Int64 {
    var d0: Int64 = np_broadcast_axis(np_get_axis(shape_a, ((0 << 32) >> 32)), np_get_axis(shape_b, ((0 << 32) >> 32)))
    var d1: Int64 = np_broadcast_axis(np_get_axis(shape_a, ((1 << 32) >> 32)), np_get_axis(shape_b, ((1 << 32) >> 32)))
    var d2: Int64 = np_broadcast_axis(np_get_axis(shape_a, ((2 << 32) >> 32)), np_get_axis(shape_b, ((2 << 32) >> 32)))
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1
    }
    return np_pack_vec3(((d0 << 32) >> 32), ((d1 << 32) >> 32), ((d2 << 32) >> 32))
}

func np_broadcast_strides(_ src_shape: Int64, _ src_strides: Int64, _ target_shape: Int64) -> Int64 {
    var sd0: Int64 = np_get_axis(src_shape, ((0 << 32) >> 32))
    var sd1: Int64 = np_get_axis(src_shape, ((1 << 32) >> 32))
    var sd2: Int64 = np_get_axis(src_shape, ((2 << 32) >> 32))
    var td0: Int64 = np_get_axis(target_shape, ((0 << 32) >> 32))
    var td1: Int64 = np_get_axis(target_shape, ((1 << 32) >> 32))
    var td2: Int64 = np_get_axis(target_shape, ((2 << 32) >> 32))
    var s0: Int64 = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, ((0 << 32) >> 32)))
    var s1: Int64 = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, ((1 << 32) >> 32)))
    var s2: Int64 = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, ((2 << 32) >> 32)))
    return np_pack_vec3(((s0 << 32) >> 32), ((s1 << 32) >> 32), ((s2 << 32) >> 32))
}

func np_normalize_index(_ idx: Int64, _ dim: Int64, _ mode: Int64) -> Int64 {
    if ((mode == 1)) {
        return ((((idx ^ dim) < 0) && ((idx % dim) != 0)) ? ((idx % dim) + dim) : (idx % dim))
    }
    if ((mode == 2)) {
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx))
    }
    var norm: Int64 = ((idx < 0) ? (idx + dim) : idx)
    if (((norm < 0) || (norm >= dim))) {
        return -1
    }
    return norm
}

func np_ravel_multi_index(_ coords3: Int64, _ shape3: Int64, _ mode: Int64) -> Int64 {
    var d0: Int64 = np_get_axis(shape3, ((0 << 32) >> 32))
    var d1: Int64 = np_get_axis(shape3, ((1 << 32) >> 32))
    var d2: Int64 = np_get_axis(shape3, ((2 << 32) >> 32))
    var i0: Int64 = np_normalize_index(np_get_axis(coords3, ((0 << 32) >> 32)), d0, mode)
    var i1: Int64 = np_normalize_index(np_get_axis(coords3, ((1 << 32) >> 32)), d1, mode)
    var i2: Int64 = np_normalize_index(np_get_axis(coords3, ((2 << 32) >> 32)), d2, mode)
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1
    }
    return ((((i0 * d1) + i1) * d2) + i2)
}

func np_unravel_index(_ flat_idx: Int64, _ shape3: Int64) -> Int64 {
    var d1: Int64 = np_get_axis(shape3, ((1 << 32) >> 32))
    var d2: Int64 = np_get_axis(shape3, ((2 << 32) >> 32))
    var i2: Int64 = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx % d2) + d2) : (flat_idx % d2))
    var rem: Int64 = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx / d2) - 1) : (flat_idx / d2))
    var i1: Int64 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem % d1) + d1) : (rem % d1))
    var i0: Int64 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem / d1) - 1) : (rem / d1))
    return np_pack_vec3(((i0 << 32) >> 32), ((i1 << 32) >> 32), ((i2 << 32) >> 32))
}

func np_pack_buf4(_ e0: Int64, _ e1: Int64, _ e2: Int64, _ e3: Int64) -> Int64 {
    var u0: Int64 = (e0 & 65535)
    var u1: Int64 = ((e1 & 65535) << (16 & 63))
    var u2: Int64 = ((e2 & 65535) << (32 & 63))
    var u3: Int64 = ((e3 & 65535) << (48 & 63))
    return (((u0 | u1) | u2) | u3)
}

func np_buf4_get(_ buf: Int64, _ idx: Int64) -> Int64 {
    var shift: Int64 = ((((idx & 3) * 16) << 32) >> 32)
    var raw: Int64 = ((buf >> (shift & 63)) & 65535)
    return ((raw ^ 32768) - 32768)
}

func np_buf8_get(_ buf_lo: Int64, _ buf_hi: Int64, _ idx: Int64) -> Int64 {
    var word: Int64 = ((idx < 4) ? buf_lo : buf_hi)
    var lane: Int64 = (((idx & 3) << 32) >> 32)
    return np_buf4_get(word, lane)
}

func np_apply_ufunc(_ op_code: Int64, _ a: Int64, _ b: Int64) -> Int64 {
    if ((op_code == 0)) {
        return (a + b)
    }
    if ((op_code == 1)) {
        return (a - b)
    }
    if ((op_code == 2)) {
        return (a * b)
    }
    if ((op_code == 3)) {
        return ((a < b) ? a : b)
    }
    if ((op_code == 4)) {
        return ((a > b) ? a : b)
    }
    return (a ^ b)
}

func np_ufunc_2x2(_ buf_a: Int64, _ shape_a: Int64, _ str_a: Int64, _ buf_b: Int64, _ shape_b: Int64, _ str_b: Int64, _ op_code: Int64) -> Int64 {
    var out_shape: Int64 = np_broadcast_shapes(shape_a, shape_b)
    var bstr_a: Int64 = np_broadcast_strides(shape_a, str_a, out_shape)
    var bstr_b: Int64 = np_broadcast_strides(shape_b, str_b, out_shape)
    var a00: Int64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var b00: Int64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var a01: Int64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var b01: Int64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var a10: Int64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var b10: Int64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var a11: Int64 = np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var b11: Int64 = np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11))
}

func np_clip_scalar(_ v: Int64, _ a_min: Int64, _ a_max: Int64) -> Int64 {
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v))
}

func np_clip_buf4(_ buf: Int64, _ a_min: Int64, _ a_max: Int64) -> Int64 {
    var c0: Int64 = np_clip_scalar(np_buf4_get(buf, ((0 << 32) >> 32)), a_min, a_max)
    var c1: Int64 = np_clip_scalar(np_buf4_get(buf, ((1 << 32) >> 32)), a_min, a_max)
    var c2: Int64 = np_clip_scalar(np_buf4_get(buf, ((2 << 32) >> 32)), a_min, a_max)
    var c3: Int64 = np_clip_scalar(np_buf4_get(buf, ((3 << 32) >> 32)), a_min, a_max)
    return np_pack_buf4(c0, c1, c2, c3)
}

func np_matmul_2x2(_ buf_a: Int64, _ off_a: Int64, _ str_a: Int64, _ buf_b: Int64, _ off_b: Int64, _ str_b: Int64) -> Int64 {
    var a00: Int64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var a01: Int64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var a10: Int64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var a11: Int64 = np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var b00: Int64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var b01: Int64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var b10: Int64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var b11: Int64 = np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var c00: Int64 = ((a00 * b00) + (a01 * b10))
    var c01: Int64 = ((a00 * b01) + (a01 * b11))
    var c10: Int64 = ((a10 * b00) + (a11 * b10))
    var c11: Int64 = ((a10 * b01) + (a11 * b11))
    return np_pack_buf4(c00, c01, c10, c11)
}

func np_reduce_pair(_ a: Int64, _ b: Int64, _ red_op: Int64) -> Int64 {
    if ((red_op == 0)) {
        return (a + b)
    }
    if ((red_op == 1)) {
        return ((a >= b) ? a : b)
    }
    return ((a <= b) ? a : b)
}

func np_reduce_all_2x2(_ buf: Int64, _ base_off: Int64, _ strides3: Int64, _ red_op: Int64) -> Int64 {
    var v0: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var v1: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var v2: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var v3: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    if ((red_op == 3)) {
        var best_i: Int64 = ((v1 > v0) ? 1 : 0)
        var best_v: Int64 = ((v1 > v0) ? v1 : v0)
        best_i = ((v2 > best_v) ? 2 : best_i)
        best_v = ((v2 > best_v) ? v2 : best_v)
        best_i = ((v3 > best_v) ? 3 : best_i)
        return best_i
    }
    var r01: Int64 = np_reduce_pair(v0, v1, red_op)
    var r23: Int64 = np_reduce_pair(v2, v3, red_op)
    return np_reduce_pair(r01, r23, red_op)
}

func np_reduce_axis_2x2(_ buf: Int64, _ base_off: Int64, _ strides3: Int64, _ axis: Int64, _ red_op: Int64) -> Int64 {
    var v00: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var v01: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var v10: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var v11: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    var r0: Int64 = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op))
    var r1: Int64 = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op))
    return np_pack_vec3(((r0 << 32) >> 32), ((r1 << 32) >> 32), ((0 << 32) >> 32))
}

func np_trace_2x2(_ buf: Int64, _ base_off: Int64, _ strides3: Int64) -> Int64 {
    var d00: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    var d11: Int64 = np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    return (d00 + d11)
}

func np_select_idx(_ r0: Int64, _ r1: Int64, _ target: Int64) -> Int64 {
    var alt: Int64 = ((r1 == target) ? 1 : 2)
    return ((r0 == target) ? 0 : alt)
}

func np_argsort_vec3(_ vec3: Int64) -> Int64 {
    var a0: Int64 = np_get_axis(vec3, ((0 << 32) >> 32))
    var a1: Int64 = np_get_axis(vec3, ((1 << 32) >> 32))
    var a2: Int64 = np_get_axis(vec3, ((2 << 32) >> 32))
    var r0: Int64 = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0))
    var r1: Int64 = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0))
    var p0: Int64 = np_select_idx(r0, r1, 0)
    var p1: Int64 = np_select_idx(r0, r1, 1)
    var p2: Int64 = np_select_idx(r0, r1, 2)
    return np_pack_vec3(((p0 << 32) >> 32), ((p1 << 32) >> 32), ((p2 << 32) >> 32))
}

func np_pipeline_digest(_ seed: Int64) -> Int64 {
    var sh_col: Int64 = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((1 << 32) >> 32))
    var sh_row: Int64 = np_pack_vec3(((1 << 32) >> 32), ((1 << 32) >> 32), ((2 << 32) >> 32))
    var sh_2x2: Int64 = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((2 << 32) >> 32))
    var st_2x2: Int64 = np_c_strides(sh_2x2)
    var buf_col: Int64 = np_pack_buf4((seed + 3), (seed - 5), 0, 0)
    var buf_row: Int64 = np_pack_buf4(((seed * 2) + 1), (-seed + 7), 0, 0)
    var m_a: Int64 = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), ((0 << 32) >> 32))
    var m_b: Int64 = np_pack_buf4((seed + 2), (-seed - 3), ((seed * 3) - 1), (seed + 4))
    var st_a_t: Int64 = np_swapaxes_vec3(st_2x2, ((1 << 32) >> 32), ((2 << 32) >> 32))
    var off_b_f: Int64 = np_flip_offset(0, sh_2x2, st_2x2, ((1 << 32) >> 32))
    var st_b_f: Int64 = np_flip_strides(st_2x2, ((1 << 32) >> 32))
    var m_c: Int64 = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500)
    var wrap_idx: Int64 = np_ravel_multi_index(np_pack_vec3(((-1 << 32) >> 32), (-seed - 7), (seed + 9)), np_pack_vec3(((4 << 32) >> 32), ((5 << 32) >> 32), ((6 << 32) >> 32)), 1)
    var s_all: Int64 = np_reduce_all_2x2(m_c, 0, st_2x2, ((0 << 32) >> 32))
    var amax: Int64 = np_reduce_all_2x2(m_c, 0, st_2x2, ((3 << 32) >> 32))
    var tr: Int64 = np_trace_2x2(m_c, 0, st_2x2)
    var asort: Int64 = np_argsort_vec3(np_pack_vec3(((s_all << 32) >> 32), ((tr << 32) >> 32), ((wrap_idx << 32) >> 32)))
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort)
}
