func np_pack_vec3(d0 int64, d1 int64, d2 int64) int64 {
    u0 := (d0 & 65535)
    u1 := (d1 & 65535)
    u2 := (d2 & 65535)
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2)
}

func np_get_axis(vec3 int64, axis int64) int64 {
    shift := ((func() int64 { if (axis == 0) { return 32 } else { return func() int64 { if (axis == 1) { return 16 } else { return 0 } }() } }() << 32) >> 32)
    raw := ((vec3 >> (shift & 63)) & 65535)
    signed_val := ((((raw ^ 32768) - 32768) << 32) >> 32)
    return signed_val
}

func np_c_strides(shape3 int64) int64 {
    d1 := np_get_axis(shape3, ((1 << 32) >> 32))
    d2 := np_get_axis(shape3, ((2 << 32) >> 32))
    return np_pack_vec3((d1 * d2), d2, ((1 << 32) >> 32))
}

func np_f_strides(shape3 int64) int64 {
    d0 := np_get_axis(shape3, ((0 << 32) >> 32))
    d1 := np_get_axis(shape3, ((1 << 32) >> 32))
    return np_pack_vec3(((1 << 32) >> 32), d0, (d0 * d1))
}

func np_swapaxes_vec3(vec3 int64, ax1 int64, ax2 int64) int64 {
    v0 := np_get_axis(vec3, ((0 << 32) >> 32))
    v1 := np_get_axis(vec3, ((1 << 32) >> 32))
    v2 := np_get_axis(vec3, ((2 << 32) >> 32))
    n0 := ((func() int64 { if (ax1 == 0) { return np_get_axis(vec3, ax2) } else { return func() int64 { if (ax2 == 0) { return np_get_axis(vec3, ax1) } else { return v0 } }() } }() << 32) >> 32)
    n1 := ((func() int64 { if (ax1 == 1) { return np_get_axis(vec3, ax2) } else { return func() int64 { if (ax2 == 1) { return np_get_axis(vec3, ax1) } else { return v1 } }() } }() << 32) >> 32)
    n2 := ((func() int64 { if (ax1 == 2) { return np_get_axis(vec3, ax2) } else { return func() int64 { if (ax2 == 2) { return np_get_axis(vec3, ax1) } else { return v2 } }() } }() << 32) >> 32)
    return np_pack_vec3(n0, n1, n2)
}

func np_flip_offset(base_off int64, shape3 int64, strides3 int64, axis int64) int64 {
    dim := np_get_axis(shape3, axis)
    st := np_get_axis(strides3, axis)
    return (base_off + ((dim - 1) * st))
}

func np_flip_strides(strides3 int64, axis int64) int64 {
    s0 := np_get_axis(strides3, ((0 << 32) >> 32))
    s1 := np_get_axis(strides3, ((1 << 32) >> 32))
    s2 := np_get_axis(strides3, ((2 << 32) >> 32))
    n0 := ((func() int64 { if (axis == 0) { return -s0 } else { return s0 } }() << 32) >> 32)
    n1 := ((func() int64 { if (axis == 1) { return -s1 } else { return s1 } }() << 32) >> 32)
    n2 := ((func() int64 { if (axis == 2) { return -s2 } else { return s2 } }() << 32) >> 32)
    return np_pack_vec3(n0, n1, n2)
}

func np_flat_offset(base_off int64, strides3 int64, i0 int64, i1 int64, i2 int64) int64 {
    s0 := np_get_axis(strides3, ((0 << 32) >> 32))
    s1 := np_get_axis(strides3, ((1 << 32) >> 32))
    s2 := np_get_axis(strides3, ((2 << 32) >> 32))
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2))
}

func np_broadcast_axis(da int64, db int64) int64 {
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

func np_broadcast_shapes(shape_a int64, shape_b int64) int64 {
    d0 := np_broadcast_axis(np_get_axis(shape_a, ((0 << 32) >> 32)), np_get_axis(shape_b, ((0 << 32) >> 32)))
    d1 := np_broadcast_axis(np_get_axis(shape_a, ((1 << 32) >> 32)), np_get_axis(shape_b, ((1 << 32) >> 32)))
    d2 := np_broadcast_axis(np_get_axis(shape_a, ((2 << 32) >> 32)), np_get_axis(shape_b, ((2 << 32) >> 32)))
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1
    }
    return np_pack_vec3(((d0 << 32) >> 32), ((d1 << 32) >> 32), ((d2 << 32) >> 32))
}

func np_broadcast_strides(src_shape int64, src_strides int64, target_shape int64) int64 {
    sd0 := np_get_axis(src_shape, ((0 << 32) >> 32))
    sd1 := np_get_axis(src_shape, ((1 << 32) >> 32))
    sd2 := np_get_axis(src_shape, ((2 << 32) >> 32))
    td0 := np_get_axis(target_shape, ((0 << 32) >> 32))
    td1 := np_get_axis(target_shape, ((1 << 32) >> 32))
    td2 := np_get_axis(target_shape, ((2 << 32) >> 32))
    s0 := func() int64 { if ((sd0 == 1) && (td0 > 1)) { return 0 } else { return np_get_axis(src_strides, ((0 << 32) >> 32)) } }()
    s1 := func() int64 { if ((sd1 == 1) && (td1 > 1)) { return 0 } else { return np_get_axis(src_strides, ((1 << 32) >> 32)) } }()
    s2 := func() int64 { if ((sd2 == 1) && (td2 > 1)) { return 0 } else { return np_get_axis(src_strides, ((2 << 32) >> 32)) } }()
    return np_pack_vec3(((s0 << 32) >> 32), ((s1 << 32) >> 32), ((s2 << 32) >> 32))
}

func np_normalize_index(idx int64, dim int64, mode int64) int64 {
    if ((mode == 1)) {
        return func() int64 { if (((idx ^ dim) < 0) && ((idx % dim) != 0)) { return ((idx % dim) + dim) } else { return (idx % dim) } }()
    }
    if ((mode == 2)) {
        return func() int64 { if (idx < 0) { return 0 } else { return func() int64 { if (idx >= dim) { return (dim - 1) } else { return idx } }() } }()
    }
    norm := func() int64 { if (idx < 0) { return (idx + dim) } else { return idx } }()
    if (((norm < 0) || (norm >= dim))) {
        return -1
    }
    return norm
}

func np_ravel_multi_index(coords3 int64, shape3 int64, mode int64) int64 {
    d0 := np_get_axis(shape3, ((0 << 32) >> 32))
    d1 := np_get_axis(shape3, ((1 << 32) >> 32))
    d2 := np_get_axis(shape3, ((2 << 32) >> 32))
    i0 := np_normalize_index(np_get_axis(coords3, ((0 << 32) >> 32)), d0, mode)
    i1 := np_normalize_index(np_get_axis(coords3, ((1 << 32) >> 32)), d1, mode)
    i2 := np_normalize_index(np_get_axis(coords3, ((2 << 32) >> 32)), d2, mode)
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1
    }
    return ((((i0 * d1) + i1) * d2) + i2)
}

func np_unravel_index(flat_idx int64, shape3 int64) int64 {
    d1 := np_get_axis(shape3, ((1 << 32) >> 32))
    d2 := np_get_axis(shape3, ((2 << 32) >> 32))
    i2 := func() int64 { if (((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) { return ((flat_idx % d2) + d2) } else { return (flat_idx % d2) } }()
    rem := func() int64 { if (((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) { return ((flat_idx / d2) - 1) } else { return (flat_idx / d2) } }()
    i1 := func() int64 { if (((rem ^ d1) < 0) && ((rem % d1) != 0)) { return ((rem % d1) + d1) } else { return (rem % d1) } }()
    i0 := func() int64 { if (((rem ^ d1) < 0) && ((rem % d1) != 0)) { return ((rem / d1) - 1) } else { return (rem / d1) } }()
    return np_pack_vec3(((i0 << 32) >> 32), ((i1 << 32) >> 32), ((i2 << 32) >> 32))
}

func np_pack_buf4(e0 int64, e1 int64, e2 int64, e3 int64) int64 {
    u0 := (e0 & 65535)
    u1 := ((e1 & 65535) << (16 & 63))
    u2 := ((e2 & 65535) << (32 & 63))
    u3 := ((e3 & 65535) << (48 & 63))
    return (((u0 | u1) | u2) | u3)
}

func np_buf4_get(buf int64, idx int64) int64 {
    shift := ((((idx & 3) * 16) << 32) >> 32)
    raw := ((buf >> (shift & 63)) & 65535)
    return ((raw ^ 32768) - 32768)
}

func np_buf8_get(buf_lo int64, buf_hi int64, idx int64) int64 {
    word := func() int64 { if (idx < 4) { return buf_lo } else { return buf_hi } }()
    lane := (((idx & 3) << 32) >> 32)
    return np_buf4_get(word, lane)
}

func np_apply_ufunc(op_code int64, a int64, b int64) int64 {
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
        return func() int64 { if (a < b) { return a } else { return b } }()
    }
    if ((op_code == 4)) {
        return func() int64 { if (a > b) { return a } else { return b } }()
    }
    return (a ^ b)
}

func np_ufunc_2x2(buf_a int64, shape_a int64, str_a int64, buf_b int64, shape_b int64, str_b int64, op_code int64) int64 {
    out_shape := np_broadcast_shapes(shape_a, shape_b)
    bstr_a := np_broadcast_strides(shape_a, str_a, out_shape)
    bstr_b := np_broadcast_strides(shape_b, str_b, out_shape)
    a00 := np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    b00 := np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    a01 := np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    b01 := np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    a10 := np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    b10 := np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    a11 := np_buf4_get(buf_a, ((np_flat_offset(0, bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    b11 := np_buf4_get(buf_b, ((np_flat_offset(0, bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11))
}

func np_clip_scalar(v int64, a_min int64, a_max int64) int64 {
    return func() int64 { if (v < a_min) { return a_min } else { return func() int64 { if (v > a_max) { return a_max } else { return v } }() } }()
}

func np_clip_buf4(buf int64, a_min int64, a_max int64) int64 {
    c0 := np_clip_scalar(np_buf4_get(buf, ((0 << 32) >> 32)), a_min, a_max)
    c1 := np_clip_scalar(np_buf4_get(buf, ((1 << 32) >> 32)), a_min, a_max)
    c2 := np_clip_scalar(np_buf4_get(buf, ((2 << 32) >> 32)), a_min, a_max)
    c3 := np_clip_scalar(np_buf4_get(buf, ((3 << 32) >> 32)), a_min, a_max)
    return np_pack_buf4(c0, c1, c2, c3)
}

func np_matmul_2x2(buf_a int64, off_a int64, str_a int64, buf_b int64, off_b int64, str_b int64) int64 {
    a00 := np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    a01 := np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    a10 := np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    a11 := np_buf4_get(buf_a, ((np_flat_offset(off_a, str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    b00 := np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    b01 := np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    b10 := np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    b11 := np_buf4_get(buf_b, ((np_flat_offset(off_b, str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    c00 := ((a00 * b00) + (a01 * b10))
    c01 := ((a00 * b01) + (a01 * b11))
    c10 := ((a10 * b00) + (a11 * b10))
    c11 := ((a10 * b01) + (a11 * b11))
    return np_pack_buf4(c00, c01, c10, c11)
}

func np_reduce_pair(a int64, b int64, red_op int64) int64 {
    if ((red_op == 0)) {
        return (a + b)
    }
    if ((red_op == 1)) {
        return func() int64 { if (a >= b) { return a } else { return b } }()
    }
    return func() int64 { if (a <= b) { return a } else { return b } }()
}

func np_reduce_all_2x2(buf int64, base_off int64, strides3 int64, red_op int64) int64 {
    v0 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    v1 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    v2 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    v3 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    if ((red_op == 3)) {
        best_i := func() int64 { if (v1 > v0) { return 1 } else { return 0 } }()
        best_v := func() int64 { if (v1 > v0) { return v1 } else { return v0 } }()
        best_i = func() int64 { if (v2 > best_v) { return 2 } else { return best_i } }()
        best_v = func() int64 { if (v2 > best_v) { return v2 } else { return best_v } }()
        best_i = func() int64 { if (v3 > best_v) { return 3 } else { return best_i } }()
        return best_i
    }
    r01 := np_reduce_pair(v0, v1, red_op)
    r23 := np_reduce_pair(v2, v3, red_op)
    return np_reduce_pair(r01, r23, red_op)
}

func np_reduce_axis_2x2(buf int64, base_off int64, strides3 int64, axis int64, red_op int64) int64 {
    v00 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    v01 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    v10 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    v11 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    r0 := func() int64 { if (axis == 0) { return np_reduce_pair(v00, v10, red_op) } else { return np_reduce_pair(v00, v01, red_op) } }()
    r1 := func() int64 { if (axis == 0) { return np_reduce_pair(v01, v11, red_op) } else { return np_reduce_pair(v10, v11, red_op) } }()
    return np_pack_vec3(((r0 << 32) >> 32), ((r1 << 32) >> 32), ((0 << 32) >> 32))
}

func np_trace_2x2(buf int64, base_off int64, strides3 int64) int64 {
    d00 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32))
    d11 := np_buf4_get(buf, ((np_flat_offset(base_off, strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32))
    return (d00 + d11)
}

func np_select_idx(r0 int64, r1 int64, target int64) int64 {
    alt := func() int64 { if (r1 == target) { return 1 } else { return 2 } }()
    return func() int64 { if (r0 == target) { return 0 } else { return alt } }()
}

func np_argsort_vec3(vec3 int64) int64 {
    a0 := np_get_axis(vec3, ((0 << 32) >> 32))
    a1 := np_get_axis(vec3, ((1 << 32) >> 32))
    a2 := np_get_axis(vec3, ((2 << 32) >> 32))
    r0 := (func() int64 { if (a0 > a1) { return 1 } else { return 0 } }() + func() int64 { if (a0 > a2) { return 1 } else { return 0 } }())
    r1 := (func() int64 { if (a1 >= a0) { return 1 } else { return 0 } }() + func() int64 { if (a1 > a2) { return 1 } else { return 0 } }())
    p0 := np_select_idx(r0, r1, 0)
    p1 := np_select_idx(r0, r1, 1)
    p2 := np_select_idx(r0, r1, 2)
    return np_pack_vec3(((p0 << 32) >> 32), ((p1 << 32) >> 32), ((p2 << 32) >> 32))
}

func np_pipeline_digest(seed int64) int64 {
    sh_col := np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((1 << 32) >> 32))
    sh_row := np_pack_vec3(((1 << 32) >> 32), ((1 << 32) >> 32), ((2 << 32) >> 32))
    sh_2x2 := np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((2 << 32) >> 32))
    st_2x2 := np_c_strides(sh_2x2)
    buf_col := np_pack_buf4((seed + 3), (seed - 5), 0, 0)
    buf_row := np_pack_buf4(((seed * 2) + 1), (-seed + 7), 0, 0)
    m_a := np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), ((0 << 32) >> 32))
    m_b := np_pack_buf4((seed + 2), (-seed - 3), ((seed * 3) - 1), (seed + 4))
    st_a_t := np_swapaxes_vec3(st_2x2, ((1 << 32) >> 32), ((2 << 32) >> 32))
    off_b_f := np_flip_offset(0, sh_2x2, st_2x2, ((1 << 32) >> 32))
    st_b_f := np_flip_strides(st_2x2, ((1 << 32) >> 32))
    m_c := np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500)
    wrap_idx := np_ravel_multi_index(np_pack_vec3(((-1 << 32) >> 32), (-seed - 7), (seed + 9)), np_pack_vec3(((4 << 32) >> 32), ((5 << 32) >> 32), ((6 << 32) >> 32)), 1)
    s_all := np_reduce_all_2x2(m_c, 0, st_2x2, ((0 << 32) >> 32))
    amax := np_reduce_all_2x2(m_c, 0, st_2x2, ((3 << 32) >> 32))
    tr := np_trace_2x2(m_c, 0, st_2x2)
    asort := np_argsort_vec3(np_pack_vec3(((s_all << 32) >> 32), ((tr << 32) >> 32), ((wrap_idx << 32) >> 32)))
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort)
}
