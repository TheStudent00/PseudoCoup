def np_pack_vec3(d0, d1, d2)
    u0 = (d0 & 65535)
    u1 = (d1 & 65535)
    u2 = (d2 & 65535)
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2)
end

def np_get_axis(vec3, axis)
    shift = (((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) & 4294967295) ^ 2147483648) - 2147483648)
    raw = ((vec3 >> (shift & 63)) & 65535)
    signed_val = (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648)
    return signed_val
end

def np_c_strides(shape3)
    d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    return np_pack_vec3((d1 * d2), d2, (((1 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_f_strides(shape3)
    d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    return np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), d0, (d0 * d1))
end

def np_swapaxes_vec3(vec3, ax1, ax2)
    v0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    v1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    v2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    n0 = (((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) & 4294967295) ^ 2147483648) - 2147483648)
    n1 = (((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) & 4294967295) ^ 2147483648) - 2147483648)
    n2 = (((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) & 4294967295) ^ 2147483648) - 2147483648)
    return np_pack_vec3(n0, n1, n2)
end

def np_flip_offset(base_off, shape3, strides3, axis)
    dim = np_get_axis(shape3, axis)
    st = np_get_axis(strides3, axis)
    return (base_off + ((dim - 1) * st))
end

def np_flip_strides(strides3, axis)
    s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    n0 = (((((axis == 0) ? (-s0) : s0) & 4294967295) ^ 2147483648) - 2147483648)
    n1 = (((((axis == 1) ? (-s1) : s1) & 4294967295) ^ 2147483648) - 2147483648)
    n2 = (((((axis == 2) ? (-s2) : s2) & 4294967295) ^ 2147483648) - 2147483648)
    return np_pack_vec3(n0, n1, n2)
end

def np_flat_offset(base_off, strides3, i0, i1, i2)
    s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2))
end

def np_broadcast_axis(da, db)
    if (da == db)
        return da
    end
    if (da == 1)
        return db
    end
    if (db == 1)
        return da
    end
    return -1
end

def np_broadcast_shapes(shape_a, shape_b)
    d0 = np_broadcast_axis(np_get_axis(shape_a, (((0 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((0 & 4294967295) ^ 2147483648) - 2147483648)))
    d1 = np_broadcast_axis(np_get_axis(shape_a, (((1 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((1 & 4294967295) ^ 2147483648) - 2147483648)))
    d2 = np_broadcast_axis(np_get_axis(shape_a, (((2 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((2 & 4294967295) ^ 2147483648) - 2147483648)))
    if (((d0 < 0) || (d1 < 0)) || (d2 < 0))
        return -1
    end
    return np_pack_vec3((((d0 & 4294967295) ^ 2147483648) - 2147483648), (((d1 & 4294967295) ^ 2147483648) - 2147483648), (((d2 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_broadcast_strides(src_shape, src_strides, target_shape)
    sd0 = np_get_axis(src_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    sd1 = np_get_axis(src_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    sd2 = np_get_axis(src_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    td0 = np_get_axis(target_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    td1 = np_get_axis(target_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    td2 = np_get_axis(target_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    s0 = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, (((0 & 4294967295) ^ 2147483648) - 2147483648)))
    s1 = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, (((1 & 4294967295) ^ 2147483648) - 2147483648)))
    s2 = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, (((2 & 4294967295) ^ 2147483648) - 2147483648)))
    return np_pack_vec3((((s0 & 4294967295) ^ 2147483648) - 2147483648), (((s1 & 4294967295) ^ 2147483648) - 2147483648), (((s2 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_normalize_index(idx, dim, mode)
    if (mode == 1)
        return ((((idx ^ dim) < 0) && ((idx.remainder(dim)) != 0)) ? ((idx.remainder(dim)) + dim) : (idx.remainder(dim)))
    end
    if (mode == 2)
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx))
    end
    norm = ((idx < 0) ? (idx + dim) : idx)
    if ((norm < 0) || (norm >= dim))
        return -1
    end
    return norm
end

def np_ravel_multi_index(coords3, shape3, mode)
    d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    i0 = np_normalize_index(np_get_axis(coords3, (((0 & 4294967295) ^ 2147483648) - 2147483648)), d0, mode)
    i1 = np_normalize_index(np_get_axis(coords3, (((1 & 4294967295) ^ 2147483648) - 2147483648)), d1, mode)
    i2 = np_normalize_index(np_get_axis(coords3, (((2 & 4294967295) ^ 2147483648) - 2147483648)), d2, mode)
    if (((i0 < 0) || (i1 < 0)) || (i2 < 0))
        return -1
    end
    return ((((i0 * d1) + i1) * d2) + i2)
end

def np_unravel_index(flat_idx, shape3)
    d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    i2 = ((((flat_idx ^ d2) < 0) && ((flat_idx.remainder(d2)) != 0)) ? ((flat_idx.remainder(d2)) + d2) : (flat_idx.remainder(d2)))
    rem = ((((flat_idx ^ d2) < 0) && ((flat_idx.remainder(d2)) != 0)) ? ((flat_idx.fdiv(d2).truncate) - 1) : (flat_idx.fdiv(d2).truncate))
    i1 = ((((rem ^ d1) < 0) && ((rem.remainder(d1)) != 0)) ? ((rem.remainder(d1)) + d1) : (rem.remainder(d1)))
    i0 = ((((rem ^ d1) < 0) && ((rem.remainder(d1)) != 0)) ? ((rem.fdiv(d1).truncate) - 1) : (rem.fdiv(d1).truncate))
    return np_pack_vec3((((i0 & 4294967295) ^ 2147483648) - 2147483648), (((i1 & 4294967295) ^ 2147483648) - 2147483648), (((i2 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_pack_buf4(e0, e1, e2, e3)
    u0 = (e0 & 65535)
    u1 = ((e1 & 65535) << (16 & 63))
    u2 = ((e2 & 65535) << (32 & 63))
    u3 = ((e3 & 65535) << (48 & 63))
    return (((u0 | u1) | u2) | u3)
end

def np_buf4_get(buf, idx)
    shift = (((((idx & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648)
    raw = ((buf >> (shift & 63)) & 65535)
    return ((raw ^ 32768) - 32768)
end

def np_buf8_get(buf_lo, buf_hi, idx)
    word = ((idx < 4) ? buf_lo : buf_hi)
    lane = ((((idx & 3) & 4294967295) ^ 2147483648) - 2147483648)
    return np_buf4_get(word, lane)
end

def np_apply_ufunc(op_code, a, b)
    if (op_code == 0)
        return (a + b)
    end
    if (op_code == 1)
        return (a - b)
    end
    if (op_code == 2)
        return (a * b)
    end
    if (op_code == 3)
        return ((a < b) ? a : b)
    end
    if (op_code == 4)
        return ((a > b) ? a : b)
    end
    return (a ^ b)
end

def np_ufunc_2x2(buf_a, shape_a, str_a, buf_b, shape_b, str_b, op_code)
    out_shape = np_broadcast_shapes(shape_a, shape_b)
    bstr_a = np_broadcast_strides(shape_a, str_a, out_shape)
    bstr_b = np_broadcast_strides(shape_b, str_b, out_shape)
    a00 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b00 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a01 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b01 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a10 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b10 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a11 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b11 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11))
end

def np_clip_scalar(v, a_min, a_max)
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v))
end

def np_clip_buf4(buf, a_min, a_max)
    c0 = np_clip_scalar(np_buf4_get(buf, (((0 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max)
    c1 = np_clip_scalar(np_buf4_get(buf, (((1 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max)
    c2 = np_clip_scalar(np_buf4_get(buf, (((2 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max)
    c3 = np_clip_scalar(np_buf4_get(buf, (((3 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max)
    return np_pack_buf4(c0, c1, c2, c3)
end

def np_matmul_2x2(buf_a, off_a, str_a, buf_b, off_b, str_b)
    a00 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a01 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a10 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    a11 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b00 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b01 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b10 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    b11 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    c00 = ((a00 * b00) + (a01 * b10))
    c01 = ((a00 * b01) + (a01 * b11))
    c10 = ((a10 * b00) + (a11 * b10))
    c11 = ((a10 * b01) + (a11 * b11))
    return np_pack_buf4(c00, c01, c10, c11)
end

def np_reduce_pair(a, b, red_op)
    if (red_op == 0)
        return (a + b)
    end
    if (red_op == 1)
        return ((a >= b) ? a : b)
    end
    return ((a <= b) ? a : b)
end

def np_reduce_all_2x2(buf, base_off, strides3, red_op)
    v0 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v1 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v2 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v3 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    if (red_op == 3)
        best_i = ((v1 > v0) ? 1 : 0)
        best_v = ((v1 > v0) ? v1 : v0)
        best_i = ((v2 > best_v) ? 2 : best_i)
        best_v = ((v2 > best_v) ? v2 : best_v)
        best_i = ((v3 > best_v) ? 3 : best_i)
        return best_i
    end
    r01 = np_reduce_pair(v0, v1, red_op)
    r23 = np_reduce_pair(v2, v3, red_op)
    return np_reduce_pair(r01, r23, red_op)
end

def np_reduce_axis_2x2(buf, base_off, strides3, axis, red_op)
    v00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v01 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v10 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    v11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    r0 = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op))
    r1 = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op))
    return np_pack_vec3((((r0 & 4294967295) ^ 2147483648) - 2147483648), (((r1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_trace_2x2(buf, base_off, strides3)
    d00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    d11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648))
    return (d00 + d11)
end

def np_select_idx(r0, r1, target)
    alt = ((r1 == target) ? 1 : 2)
    return ((r0 == target) ? 0 : alt)
end

def np_argsort_vec3(vec3)
    a0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    a1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    a2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648))
    r0 = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0))
    r1 = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0))
    p0 = np_select_idx(r0, r1, 0)
    p1 = np_select_idx(r0, r1, 1)
    p2 = np_select_idx(r0, r1, 2)
    return np_pack_vec3((((p0 & 4294967295) ^ 2147483648) - 2147483648), (((p1 & 4294967295) ^ 2147483648) - 2147483648), (((p2 & 4294967295) ^ 2147483648) - 2147483648))
end

def np_pipeline_digest(seed)
    sh_col = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648))
    sh_row = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648))
    sh_2x2 = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648))
    st_2x2 = np_c_strides(sh_2x2)
    buf_col = np_pack_buf4((seed + 3), (seed - 5), 0, 0)
    buf_row = np_pack_buf4(((seed * 2) + 1), ((-seed) + 7), 0, 0)
    m_a = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), (((0 & 4294967295) ^ 2147483648) - 2147483648))
    m_b = np_pack_buf4((seed + 2), ((-seed) - 3), ((seed * 3) - 1), (seed + 4))
    st_a_t = np_swapaxes_vec3(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648))
    off_b_f = np_flip_offset(0, sh_2x2, st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    st_b_f = np_flip_strides(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648))
    m_c = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500)
    wrap_idx = np_ravel_multi_index(np_pack_vec3((((-1 & 4294967295) ^ 2147483648) - 2147483648), ((-seed) - 7), (seed + 9)), np_pack_vec3((((4 & 4294967295) ^ 2147483648) - 2147483648), (((5 & 4294967295) ^ 2147483648) - 2147483648), (((6 & 4294967295) ^ 2147483648) - 2147483648)), 1)
    s_all = np_reduce_all_2x2(m_c, 0, st_2x2, (((0 & 4294967295) ^ 2147483648) - 2147483648))
    amax = np_reduce_all_2x2(m_c, 0, st_2x2, (((3 & 4294967295) ^ 2147483648) - 2147483648))
    tr = np_trace_2x2(m_c, 0, st_2x2)
    asort = np_argsort_vec3(np_pack_vec3((((s_all & 4294967295) ^ 2147483648) - 2147483648), (((tr & 4294967295) ^ 2147483648) - 2147483648), (((wrap_idx & 4294967295) ^ 2147483648) - 2147483648)))
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort)
end
