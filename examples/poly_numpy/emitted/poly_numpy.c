int64_t np_pack_vec3(int64_t d0, int64_t d1, int64_t d2) {
    int64_t u0 = (d0 & 65535);
    int64_t u1 = (d1 & 65535);
    int64_t u2 = (d2 & 65535);
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2);
}

int64_t np_get_axis(int64_t vec3, int64_t axis) {
    int64_t shift = (((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw = ((vec3 >> (shift & 63)) & 65535);
    int64_t signed_val = (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
    return signed_val;
}

int64_t np_c_strides(int64_t shape3) {
    int64_t d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((d1 * d2), d2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_f_strides(int64_t shape3) {
    int64_t d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), d0, (d0 * d1));
}

int64_t np_swapaxes_vec3(int64_t vec3, int64_t ax1, int64_t ax2) {
    int64_t v0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t n0 = (((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t n1 = (((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t n2 = (((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

int64_t np_flip_offset(int64_t base_off, int64_t shape3, int64_t strides3, int64_t axis) {
    int64_t dim = np_get_axis(shape3, axis);
    int64_t st = np_get_axis(strides3, axis);
    return (base_off + ((dim - 1) * st));
}

int64_t np_flip_strides(int64_t strides3, int64_t axis) {
    int64_t s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t n0 = (((((axis == 0) ? (-s0) : s0) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t n1 = (((((axis == 1) ? (-s1) : s1) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t n2 = (((((axis == 2) ? (-s2) : s2) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

int64_t np_flat_offset(int64_t base_off, int64_t strides3, int64_t i0, int64_t i1, int64_t i2) {
    int64_t s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2));
}

int64_t np_broadcast_axis(int64_t da, int64_t db) {
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

int64_t np_broadcast_shapes(int64_t shape_a, int64_t shape_b) {
    int64_t d0 = np_broadcast_axis(np_get_axis(shape_a, (((0 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    int64_t d1 = np_broadcast_axis(np_get_axis(shape_a, (((1 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    int64_t d2 = np_broadcast_axis(np_get_axis(shape_a, (((2 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1;
    }
    return np_pack_vec3((((d0 & 4294967295) ^ 2147483648) - 2147483648), (((d1 & 4294967295) ^ 2147483648) - 2147483648), (((d2 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_broadcast_strides(int64_t src_shape, int64_t src_strides, int64_t target_shape) {
    int64_t sd0 = np_get_axis(src_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sd1 = np_get_axis(src_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sd2 = np_get_axis(src_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t td0 = np_get_axis(target_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t td1 = np_get_axis(target_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t td2 = np_get_axis(target_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t s0 = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    int64_t s1 = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    int64_t s2 = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    return np_pack_vec3((((s0 & 4294967295) ^ 2147483648) - 2147483648), (((s1 & 4294967295) ^ 2147483648) - 2147483648), (((s2 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_normalize_index(int64_t idx, int64_t dim, int64_t mode) {
    if ((mode == 1)) {
        return ((((idx ^ dim) < 0) && ((idx % dim) != 0)) ? ((idx % dim) + dim) : (idx % dim));
    }
    if ((mode == 2)) {
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx));
    }
    int64_t norm = ((idx < 0) ? (idx + dim) : idx);
    if (((norm < 0) || (norm >= dim))) {
        return -1;
    }
    return norm;
}

int64_t np_ravel_multi_index(int64_t coords3, int64_t shape3, int64_t mode) {
    int64_t d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t i0 = np_normalize_index(np_get_axis(coords3, (((0 & 4294967295) ^ 2147483648) - 2147483648)), d0, mode);
    int64_t i1 = np_normalize_index(np_get_axis(coords3, (((1 & 4294967295) ^ 2147483648) - 2147483648)), d1, mode);
    int64_t i2 = np_normalize_index(np_get_axis(coords3, (((2 & 4294967295) ^ 2147483648) - 2147483648)), d2, mode);
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1;
    }
    return ((((i0 * d1) + i1) * d2) + i2);
}

int64_t np_unravel_index(int64_t flat_idx, int64_t shape3) {
    int64_t d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t i2 = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx % d2) + d2) : (flat_idx % d2));
    int64_t rem = ((((flat_idx ^ d2) < 0) && ((flat_idx % d2) != 0)) ? ((flat_idx / d2) - 1) : (flat_idx / d2));
    int64_t i1 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem % d1) + d1) : (rem % d1));
    int64_t i0 = ((((rem ^ d1) < 0) && ((rem % d1) != 0)) ? ((rem / d1) - 1) : (rem / d1));
    return np_pack_vec3((((i0 & 4294967295) ^ 2147483648) - 2147483648), (((i1 & 4294967295) ^ 2147483648) - 2147483648), (((i2 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_pack_buf4(int64_t e0, int64_t e1, int64_t e2, int64_t e3) {
    int64_t u0 = (e0 & 65535);
    int64_t u1 = ((e1 & 65535) << (16 & 63));
    int64_t u2 = ((e2 & 65535) << (32 & 63));
    int64_t u3 = ((e3 & 65535) << (48 & 63));
    return (((u0 | u1) | u2) | u3);
}

int64_t np_buf4_get(int64_t buf, int64_t idx) {
    int64_t shift = (((((idx & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t raw = ((buf >> (shift & 63)) & 65535);
    return ((raw ^ 32768) - 32768);
}

int64_t np_buf8_get(int64_t buf_lo, int64_t buf_hi, int64_t idx) {
    int64_t word = ((idx < 4) ? buf_lo : buf_hi);
    int64_t lane = ((((idx & 3) & 4294967295) ^ 2147483648) - 2147483648);
    return np_buf4_get(word, lane);
}

int64_t np_apply_ufunc(int64_t op_code, int64_t a, int64_t b) {
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

int64_t np_ufunc_2x2(int64_t buf_a, int64_t shape_a, int64_t str_a, int64_t buf_b, int64_t shape_b, int64_t str_b, int64_t op_code) {
    int64_t out_shape = np_broadcast_shapes(shape_a, shape_b);
    int64_t bstr_a = np_broadcast_strides(shape_a, str_a, out_shape);
    int64_t bstr_b = np_broadcast_strides(shape_b, str_b, out_shape);
    int64_t a00 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b00 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a01 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b01 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a10 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b10 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a11 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b11 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

int64_t np_clip_scalar(int64_t v, int64_t a_min, int64_t a_max) {
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v));
}

int64_t np_clip_buf4(int64_t buf, int64_t a_min, int64_t a_max) {
    int64_t c0 = np_clip_scalar(np_buf4_get(buf, (((0 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int64_t c1 = np_clip_scalar(np_buf4_get(buf, (((1 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int64_t c2 = np_clip_scalar(np_buf4_get(buf, (((2 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int64_t c3 = np_clip_scalar(np_buf4_get(buf, (((3 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}

int64_t np_matmul_2x2(int64_t buf_a, int64_t off_a, int64_t str_a, int64_t buf_b, int64_t off_b, int64_t str_b) {
    int64_t a00 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a01 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a10 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a11 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b00 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b01 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b10 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t b11 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t c00 = ((a00 * b00) + (a01 * b10));
    int64_t c01 = ((a00 * b01) + (a01 * b11));
    int64_t c10 = ((a10 * b00) + (a11 * b10));
    int64_t c11 = ((a10 * b01) + (a11 * b11));
    return np_pack_buf4(c00, c01, c10, c11);
}

int64_t np_reduce_pair(int64_t a, int64_t b, int64_t red_op) {
    if ((red_op == 0)) {
        return (a + b);
    }
    if ((red_op == 1)) {
        return ((a >= b) ? a : b);
    }
    return ((a <= b) ? a : b);
}

int64_t np_reduce_all_2x2(int64_t buf, int64_t base_off, int64_t strides3, int64_t red_op) {
    int64_t v0 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v1 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v2 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v3 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    if ((red_op == 3)) {
        int64_t best_i = ((v1 > v0) ? 1 : 0);
        int64_t best_v = ((v1 > v0) ? v1 : v0);
        best_i = ((v2 > best_v) ? 2 : best_i);
        best_v = ((v2 > best_v) ? v2 : best_v);
        best_i = ((v3 > best_v) ? 3 : best_i);
        return best_i;
    }
    int64_t r01 = np_reduce_pair(v0, v1, red_op);
    int64_t r23 = np_reduce_pair(v2, v3, red_op);
    return np_reduce_pair(r01, r23, red_op);
}

int64_t np_reduce_axis_2x2(int64_t buf, int64_t base_off, int64_t strides3, int64_t axis, int64_t red_op) {
    int64_t v00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v01 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v10 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t v11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t r0 = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op));
    int64_t r1 = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op));
    return np_pack_vec3((((r0 & 4294967295) ^ 2147483648) - 2147483648), (((r1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_trace_2x2(int64_t buf, int64_t base_off, int64_t strides3) {
    int64_t d00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int64_t d11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return (d00 + d11);
}

int64_t np_select_idx(int64_t r0, int64_t r1, int64_t target) {
    int64_t alt = ((r1 == target) ? 1 : 2);
    return ((r0 == target) ? 0 : alt);
}

int64_t np_argsort_vec3(int64_t vec3) {
    int64_t a0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t a2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t r0 = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0));
    int64_t r1 = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0));
    int64_t p0 = np_select_idx(r0, r1, 0);
    int64_t p1 = np_select_idx(r0, r1, 1);
    int64_t p2 = np_select_idx(r0, r1, 2);
    return np_pack_vec3((((p0 & 4294967295) ^ 2147483648) - 2147483648), (((p1 & 4294967295) ^ 2147483648) - 2147483648), (((p2 & 4294967295) ^ 2147483648) - 2147483648));
}

int64_t np_pipeline_digest(int64_t seed) {
    int64_t sh_col = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sh_row = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t sh_2x2 = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t st_2x2 = np_c_strides(sh_2x2);
    int64_t buf_col = np_pack_buf4((seed + 3), (seed - 5), 0, 0);
    int64_t buf_row = np_pack_buf4(((seed * 2) + 1), ((-seed) + 7), 0, 0);
    int64_t m_a = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t m_b = np_pack_buf4((seed + 2), ((-seed) - 3), ((seed * 3) - 1), (seed + 4));
    int64_t st_a_t = np_swapaxes_vec3(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t off_b_f = np_flip_offset(0, sh_2x2, st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t st_b_f = np_flip_strides(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t m_c = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500);
    int64_t wrap_idx = np_ravel_multi_index(np_pack_vec3((((-1 & 4294967295) ^ 2147483648) - 2147483648), ((-seed) - 7), (seed + 9)), np_pack_vec3((((4 & 4294967295) ^ 2147483648) - 2147483648), (((5 & 4294967295) ^ 2147483648) - 2147483648), (((6 & 4294967295) ^ 2147483648) - 2147483648)), 1);
    int64_t s_all = np_reduce_all_2x2(m_c, 0, st_2x2, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t amax = np_reduce_all_2x2(m_c, 0, st_2x2, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t tr = np_trace_2x2(m_c, 0, st_2x2);
    int64_t asort = np_argsort_vec3(np_pack_vec3((((s_all & 4294967295) ^ 2147483648) - 2147483648), (((tr & 4294967295) ^ 2147483648) - 2147483648), (((wrap_idx & 4294967295) ^ 2147483648) - 2147483648)));
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort);
}
