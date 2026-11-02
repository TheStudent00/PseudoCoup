long np_pack_vec3(long d0, long d1, long d2) {
    long u0 = (d0 & 65535);
    long u1 = (d1 & 65535);
    long u2 = (d2 & 65535);
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2);
}

long np_get_axis(long vec3, long axis) {
    long shift = (((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long raw = ((vec3 >> (shift & 63)) & 65535);
    long signed_val = (((((raw ^ 32768) - 32768) & 4294967295L) ^ 2147483648L) - 2147483648L);
    return signed_val;
}

long np_c_strides(long shape3) {
    long d1 = np_get_axis(shape3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d2 = np_get_axis(shape3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    return np_pack_vec3((d1 * d2), d2, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_f_strides(long shape3) {
    long d0 = np_get_axis(shape3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d1 = np_get_axis(shape3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    return np_pack_vec3((((1 & 4294967295L) ^ 2147483648L) - 2147483648L), d0, (d0 * d1));
}

long np_swapaxes_vec3(long vec3, long ax1, long ax2) {
    long v0 = np_get_axis(vec3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v1 = np_get_axis(vec3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v2 = np_get_axis(vec3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long n0 = (((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long n1 = (((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long n2 = (((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) & 4294967295L) ^ 2147483648L) - 2147483648L);
    return np_pack_vec3(n0, n1, n2);
}

long np_flip_offset(long base_off, long shape3, long strides3, long axis) {
    long dim = np_get_axis(shape3, axis);
    long st = np_get_axis(strides3, axis);
    return (base_off + ((dim - 1) * st));
}

long np_flip_strides(long strides3, long axis) {
    long s0 = np_get_axis(strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long s1 = np_get_axis(strides3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long s2 = np_get_axis(strides3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long n0 = (((((axis == 0) ? (-s0) : s0) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long n1 = (((((axis == 1) ? (-s1) : s1) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long n2 = (((((axis == 2) ? (-s2) : s2) & 4294967295L) ^ 2147483648L) - 2147483648L);
    return np_pack_vec3(n0, n1, n2);
}

long np_flat_offset(long base_off, long strides3, long i0, long i1, long i2) {
    long s0 = np_get_axis(strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long s1 = np_get_axis(strides3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long s2 = np_get_axis(strides3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2));
}

long np_broadcast_axis(long da, long db) {
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

long np_broadcast_shapes(long shape_a, long shape_b) {
    long d0 = np_broadcast_axis(np_get_axis(shape_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)), np_get_axis(shape_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    long d1 = np_broadcast_axis(np_get_axis(shape_a, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)), np_get_axis(shape_b, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    long d2 = np_broadcast_axis(np_get_axis(shape_a, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L)), np_get_axis(shape_b, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1;
    }
    return np_pack_vec3((((d0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((d1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((d2 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_broadcast_strides(long src_shape, long src_strides, long target_shape) {
    long sd0 = np_get_axis(src_shape, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long sd1 = np_get_axis(src_shape, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long sd2 = np_get_axis(src_shape, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long td0 = np_get_axis(target_shape, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long td1 = np_get_axis(target_shape, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long td2 = np_get_axis(target_shape, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long s0 = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    long s1 = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    long s2 = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L)));
    return np_pack_vec3((((s0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((s1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((s2 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_normalize_index(long idx, long dim, long mode) {
    if ((mode == 1)) {
        return ((((idx ^ dim) < 0) && ((idx % dim) != 0)) ? ((idx % dim) + dim) : (idx % dim));
    }
    if ((mode == 2)) {
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx));
    }
    long norm = ((idx < 0) ? (idx + dim) : idx);
    if (((norm < 0) || (norm >= dim))) {
        return -1;
    }
    return norm;
}

long np_ravel_multi_index(long coords3, long shape3, long mode) {
    long d0 = np_get_axis(shape3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d1 = np_get_axis(shape3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d2 = np_get_axis(shape3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long i0 = np_normalize_index(np_get_axis(coords3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)), d0, mode);
    long i1 = np_normalize_index(np_get_axis(coords3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)), d1, mode);
    long i2 = np_normalize_index(np_get_axis(coords3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L)), d2, mode);
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1;
    }
    return ((((i0 * d1) + i1) * d2) + i2);
}

long np_unravel_index(long flat_idx, long shape3) {
    long d1 = np_get_axis(shape3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d2 = np_get_axis(shape3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long i2 = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx % d2) + d2) : (flat_idx % d2));
    long rem = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx / d2) - 1) : (flat_idx / d2));
    long i1 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem % d1) + d1) : (rem % d1));
    long i0 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem / d1) - 1) : (rem / d1));
    return np_pack_vec3((((i0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((i1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((i2 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_pack_buf4(long e0, long e1, long e2, long e3) {
    long u0 = (e0 & 65535);
    long u1 = ((e1 & 65535) << (16 & 63));
    long u2 = ((e2 & 65535) << (32 & 63));
    long u3 = ((e3 & 65535) << (48 & 63));
    return (((u0 | u1) | u2) | u3);
}

long np_buf4_get(long buf, long idx) {
    long shift = (((((idx & 3) * 16) & 4294967295L) ^ 2147483648L) - 2147483648L);
    long raw = ((buf >> (shift & 63)) & 65535);
    return ((raw ^ 32768) - 32768);
}

long np_buf8_get(long buf_lo, long buf_hi, long idx) {
    long word = ((idx < 4) ? buf_lo : buf_hi);
    long lane = ((((idx & 3) & 4294967295L) ^ 2147483648L) - 2147483648L);
    return np_buf4_get(word, lane);
}

long np_apply_ufunc(long op_code, long a, long b) {
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

long np_ufunc_2x2(long buf_a, long shape_a, long str_a, long buf_b, long shape_b, long str_b, long op_code) {
    long out_shape = np_broadcast_shapes(shape_a, shape_b);
    long bstr_a = np_broadcast_strides(shape_a, str_a, out_shape);
    long bstr_b = np_broadcast_strides(shape_b, str_b, out_shape);
    long a00 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b00 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a01 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b01 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a10 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b10 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a11 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b11 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

long np_clip_scalar(long v, long a_min, long a_max) {
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v));
}

long np_clip_buf4(long buf, long a_min, long a_max) {
    long c0 = np_clip_scalar(np_buf4_get(buf, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)), a_min, a_max);
    long c1 = np_clip_scalar(np_buf4_get(buf, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)), a_min, a_max);
    long c2 = np_clip_scalar(np_buf4_get(buf, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L)), a_min, a_max);
    long c3 = np_clip_scalar(np_buf4_get(buf, (((3 & 4294967295L) ^ 2147483648L) - 2147483648L)), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}

long np_matmul_2x2(long buf_a, long off_a, long str_a, long buf_b, long off_b, long str_b) {
    long a00 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a01 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a10 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a11 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b00 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b01 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b10 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long b11 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long c00 = ((a00 * b00) + (a01 * b10));
    long c01 = ((a00 * b01) + (a01 * b11));
    long c10 = ((a10 * b00) + (a11 * b10));
    long c11 = ((a10 * b01) + (a11 * b11));
    return np_pack_buf4(c00, c01, c10, c11);
}

long np_reduce_pair(long a, long b, long red_op) {
    if ((red_op == 0)) {
        return (a + b);
    }
    if ((red_op == 1)) {
        return ((a >= b) ? a : b);
    }
    return ((a <= b) ? a : b);
}

long np_reduce_all_2x2(long buf, long base_off, long strides3, long red_op) {
    long v0 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v1 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v2 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v3 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    if ((red_op == 3)) {
        long best_i = ((v1 > v0) ? 1 : 0);
        long best_v = ((v1 > v0) ? v1 : v0);
        best_i = ((v2 > best_v) ? 2 : best_i);
        best_v = ((v2 > best_v) ? v2 : best_v);
        best_i = ((v3 > best_v) ? 3 : best_i);
        return best_i;
    }
    long r01 = np_reduce_pair(v0, v1, red_op);
    long r23 = np_reduce_pair(v2, v3, red_op);
    return np_reduce_pair(r01, r23, red_op);
}

long np_reduce_axis_2x2(long buf, long base_off, long strides3, long axis, long red_op) {
    long v00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v01 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v10 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long v11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long r0 = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op));
    long r1 = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op));
    return np_pack_vec3((((r0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((r1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_trace_2x2(long buf, long base_off, long strides3) {
    long d00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    long d11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L)) & 4294967295L) ^ 2147483648L) - 2147483648L));
    return (d00 + d11);
}

long np_select_idx(long r0, long r1, long target) {
    long alt = ((r1 == target) ? 1 : 2);
    return ((r0 == target) ? 0 : alt);
}

long np_argsort_vec3(long vec3) {
    long a0 = np_get_axis(vec3, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a1 = np_get_axis(vec3, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long a2 = np_get_axis(vec3, (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long r0 = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0));
    long r1 = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0));
    long p0 = np_select_idx(r0, r1, 0);
    long p1 = np_select_idx(r0, r1, 1);
    long p2 = np_select_idx(r0, r1, 2);
    return np_pack_vec3((((p0 & 4294967295L) ^ 2147483648L) - 2147483648L), (((p1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((p2 & 4294967295L) ^ 2147483648L) - 2147483648L));
}

long np_pipeline_digest(long seed) {
    long sh_col = np_pack_vec3((((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((2 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long sh_row = np_pack_vec3((((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long sh_2x2 = np_pack_vec3((((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((2 & 4294967295L) ^ 2147483648L) - 2147483648L), (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long st_2x2 = np_c_strides(sh_2x2);
    long buf_col = np_pack_buf4((seed + 3), (seed - 5), 0, 0);
    long buf_row = np_pack_buf4(((seed * 2) + 1), ((-seed) + 7), 0, 0);
    long m_a = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long m_b = np_pack_buf4((seed + 2), ((-seed) - 3), ((seed * 3) - 1), (seed + 4));
    long st_a_t = np_swapaxes_vec3(st_2x2, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L), (((2 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long off_b_f = np_flip_offset(0, sh_2x2, st_2x2, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long st_b_f = np_flip_strides(st_2x2, (((1 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long m_c = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500);
    long wrap_idx = np_ravel_multi_index(np_pack_vec3((((-1 & 4294967295L) ^ 2147483648L) - 2147483648L), ((-seed) - 7), (seed + 9)), np_pack_vec3((((4 & 4294967295L) ^ 2147483648L) - 2147483648L), (((5 & 4294967295L) ^ 2147483648L) - 2147483648L), (((6 & 4294967295L) ^ 2147483648L) - 2147483648L)), 1);
    long s_all = np_reduce_all_2x2(m_c, 0, st_2x2, (((0 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long amax = np_reduce_all_2x2(m_c, 0, st_2x2, (((3 & 4294967295L) ^ 2147483648L) - 2147483648L));
    long tr = np_trace_2x2(m_c, 0, st_2x2);
    long asort = np_argsort_vec3(np_pack_vec3((((s_all & 4294967295L) ^ 2147483648L) - 2147483648L), (((tr & 4294967295L) ^ 2147483648L) - 2147483648L), (((wrap_idx & 4294967295L) ^ 2147483648L) - 2147483648L)));
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort);
}
