// 04_go_linalg_reduce.go -- NumPy `linalg` Strided MatMul, Axis Reductions, Trace & Argsort (Go)

func np_matmul_2x2(buf_a int64, off_a int64, str_a int64, buf_b int64, off_b int64, str_b int64) int64 {
    a00 := np_buf4_get(buf_a, np_flat_offset(off_a, str_a, 0, 0, 0))
    a01 := np_buf4_get(buf_a, np_flat_offset(off_a, str_a, 0, 0, 1))
    a10 := np_buf4_get(buf_a, np_flat_offset(off_a, str_a, 0, 1, 0))
    a11 := np_buf4_get(buf_a, np_flat_offset(off_a, str_a, 0, 1, 1))
    b00 := np_buf4_get(buf_b, np_flat_offset(off_b, str_b, 0, 0, 0))
    b01 := np_buf4_get(buf_b, np_flat_offset(off_b, str_b, 0, 0, 1))
    b10 := np_buf4_get(buf_b, np_flat_offset(off_b, str_b, 0, 1, 0))
    b11 := np_buf4_get(buf_b, np_flat_offset(off_b, str_b, 0, 1, 1))
    c00 := (a00 * b00) + (a01 * b10)
    c01 := (a00 * b01) + (a01 * b11)
    c10 := (a10 * b00) + (a11 * b10)
    c11 := (a10 * b01) + (a11 * b11)
    return np_pack_buf4(c00, c01, c10, c11)
}

func np_reduce_pair(a int64, b int64, red_op int32) int64 {
    if red_op == 0 {
        return a + b
    }
    if red_op == 1 {
        return func() int64 { if a >= b { return a } else { return b } }()
    }
    return func() int64 { if a <= b { return a } else { return b } }()
}

func np_reduce_all_2x2(buf int64, base_off int64, strides3 int64, red_op int32) int64 {
    v0 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 0, 0))
    v1 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 0, 1))
    v2 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 1, 0))
    v3 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 1, 1))
    if red_op == 3 {
        best_i := func() int64 { if v1 > v0 { return 1 } else { return 0 } }()
        best_v := func() int64 { if v1 > v0 { return v1 } else { return v0 } }()
        best_i = func() int64 { if v2 > best_v { return 2 } else { return best_i } }()
        best_v = func() int64 { if v2 > best_v { return v2 } else { return best_v } }()
        best_i = func() int64 { if v3 > best_v { return 3 } else { return best_i } }()
        return best_i
    }
    r01 := np_reduce_pair(v0, v1, red_op)
    r23 := np_reduce_pair(v2, v3, red_op)
    return np_reduce_pair(r01, r23, red_op)
}

func np_reduce_axis_2x2(buf int64, base_off int64, strides3 int64, axis int32, red_op int32) int64 {
    v00 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 0, 0))
    v01 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 0, 1))
    v10 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 1, 0))
    v11 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 1, 1))
    r0 := func() int64 { if axis == 0 { return np_reduce_pair(v00, v10, red_op) } else { return np_reduce_pair(v00, v01, red_op) } }()
    r1 := func() int64 { if axis == 0 { return np_reduce_pair(v01, v11, red_op) } else { return np_reduce_pair(v10, v11, red_op) } }()
    return np_pack_vec3(r0, r1, 0)
}

func np_trace_2x2(buf int64, base_off int64, strides3 int64) int64 {
    d00 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 0, 0))
    d11 := np_buf4_get(buf, np_flat_offset(base_off, strides3, 0, 1, 1))
    return d00 + d11
}

func np_select_idx(r0 int64, r1 int64, target int64) int64 {
    alt := func() int64 { if r1 == target { return 1 } else { return 2 } }()
    return func() int64 { if r0 == target { return 0 } else { return alt } }()
}

func np_argsort_vec3(vec3 int64) int64 {
    a0 := np_get_axis(vec3, 0)
    a1 := np_get_axis(vec3, 1)
    a2 := np_get_axis(vec3, 2)
    r0 := (func() int64 { if a0 > a1 { return 1 } else { return 0 } }()) + (func() int64 { if a0 > a2 { return 1 } else { return 0 } }())
    r1 := (func() int64 { if a1 >= a0 { return 1 } else { return 0 } }()) + (func() int64 { if a1 > a2 { return 1 } else { return 0 } }())
    p0 := np_select_idx(r0, r1, 0)
    p1 := np_select_idx(r0, r1, 1)
    p2 := np_select_idx(r0, r1, 2)
    return np_pack_vec3(p0, p1, p2)
}

func np_pipeline_digest(seed int32) int64 {
    sh_col := np_pack_vec3(1, 2, 1)
    sh_row := np_pack_vec3(1, 1, 2)
    sh_2x2 := np_pack_vec3(1, 2, 2)
    st_2x2 := np_c_strides(sh_2x2)
    buf_col := np_pack_buf4(seed + 3, seed - 5, 0, 0)
    buf_row := np_pack_buf4((seed * 2) + 1, (-seed) + 7, 0, 0)
    m_a := np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), 0)
    m_b := np_pack_buf4(seed + 2, (-seed) - 3, (seed * 3) - 1, seed + 4)
    st_a_t := np_swapaxes_vec3(st_2x2, 1, 2)
    off_b_f := np_flip_offset(0, sh_2x2, st_2x2, 1)
    st_b_f := np_flip_strides(st_2x2, 1)
    m_c := np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500)
    wrap_idx := np_ravel_multi_index(np_pack_vec3(-1, (-seed) - 7, seed + 9), np_pack_vec3(4, 5, 6), 1)
    s_all := np_reduce_all_2x2(m_c, 0, st_2x2, 0)
    amax := np_reduce_all_2x2(m_c, 0, st_2x2, 3)
    tr := np_trace_2x2(m_c, 0, st_2x2)
    asort := np_argsort_vec3(np_pack_vec3(s_all, tr, wrap_idx))
    return (s_all * 1000003) + (amax * 99991) + (tr * 31337) + (wrap_idx * 1337) + asort
}
