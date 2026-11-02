int np_pack_vec3(int d0, int d1, int d2) {
    int u0 = (d0 & 65535);
    int u1 = (d1 & 65535);
    int u2 = (d2 & 65535);
    return (((u0 << (32 & 63)) | (u1 << (16 & 63))) | u2);
}

int np_get_axis(int vec3, int axis) {
    int shift = (((((axis == 0) ? 32 : ((axis == 1) ? 16 : 0)) & 4294967295) ^ 2147483648) - 2147483648);
    int raw = ((vec3 >> (shift & 63)) & 65535);
    int signed_val = (((((raw ^ 32768) - 32768) & 4294967295) ^ 2147483648) - 2147483648);
    return signed_val;
}

int np_c_strides(int shape3) {
    int d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((d1 * d2), d2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_f_strides(int shape3) {
    int d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), d0, (d0 * d1));
}

int np_swapaxes_vec3(int vec3, int ax1, int ax2) {
    int v0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int v1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int v2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int n0 = (((((ax1 == 0) ? np_get_axis(vec3, ax2) : ((ax2 == 0) ? np_get_axis(vec3, ax1) : v0)) & 4294967295) ^ 2147483648) - 2147483648);
    int n1 = (((((ax1 == 1) ? np_get_axis(vec3, ax2) : ((ax2 == 1) ? np_get_axis(vec3, ax1) : v1)) & 4294967295) ^ 2147483648) - 2147483648);
    int n2 = (((((ax1 == 2) ? np_get_axis(vec3, ax2) : ((ax2 == 2) ? np_get_axis(vec3, ax1) : v2)) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

int np_flip_offset(int base_off, int shape3, int strides3, int axis) {
    int dim = np_get_axis(shape3, axis);
    int st = np_get_axis(strides3, axis);
    return (base_off + ((dim - 1) * st));
}

int np_flip_strides(int strides3, int axis) {
    int s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int n0 = (((((axis == 0) ? (-s0) : s0) & 4294967295) ^ 2147483648) - 2147483648);
    int n1 = (((((axis == 1) ? (-s1) : s1) & 4294967295) ^ 2147483648) - 2147483648);
    int n2 = (((((axis == 2) ? (-s2) : s2) & 4294967295) ^ 2147483648) - 2147483648);
    return np_pack_vec3(n0, n1, n2);
}

int np_flat_offset(int base_off, int strides3, int i0, int i1, int i2) {
    int s0 = np_get_axis(strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int s1 = np_get_axis(strides3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int s2 = np_get_axis(strides3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    return (((base_off + (i0 * s0)) + (i1 * s1)) + (i2 * s2));
}

int np_broadcast_axis(int da, int db) {
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

int np_broadcast_shapes(int shape_a, int shape_b) {
    int d0 = np_broadcast_axis(np_get_axis(shape_a, (((0 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    int d1 = np_broadcast_axis(np_get_axis(shape_a, (((1 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    int d2 = np_broadcast_axis(np_get_axis(shape_a, (((2 & 4294967295) ^ 2147483648) - 2147483648)), np_get_axis(shape_b, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    if ((((d0 < 0) || (d1 < 0)) || (d2 < 0))) {
        return -1;
    }
    return np_pack_vec3((((d0 & 4294967295) ^ 2147483648) - 2147483648), (((d1 & 4294967295) ^ 2147483648) - 2147483648), (((d2 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_broadcast_strides(int src_shape, int src_strides, int target_shape) {
    int sd0 = np_get_axis(src_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int sd1 = np_get_axis(src_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int sd2 = np_get_axis(src_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int td0 = np_get_axis(target_shape, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int td1 = np_get_axis(target_shape, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int td2 = np_get_axis(target_shape, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int s0 = (((sd0 == 1) && (td0 > 1)) ? 0 : np_get_axis(src_strides, (((0 & 4294967295) ^ 2147483648) - 2147483648)));
    int s1 = (((sd1 == 1) && (td1 > 1)) ? 0 : np_get_axis(src_strides, (((1 & 4294967295) ^ 2147483648) - 2147483648)));
    int s2 = (((sd2 == 1) && (td2 > 1)) ? 0 : np_get_axis(src_strides, (((2 & 4294967295) ^ 2147483648) - 2147483648)));
    return np_pack_vec3((((s0 & 4294967295) ^ 2147483648) - 2147483648), (((s1 & 4294967295) ^ 2147483648) - 2147483648), (((s2 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_normalize_index(int idx, int dim, int mode) {
    if ((mode == 1)) {
        return ((((idx ^ dim) < 0) && ((idx.remainder(dim)) != 0)) ? ((idx.remainder(dim)) + dim) : (idx.remainder(dim)));
    }
    if ((mode == 2)) {
        return ((idx < 0) ? 0 : ((idx >= dim) ? (dim - 1) : idx));
    }
    int norm = ((idx < 0) ? (idx + dim) : idx);
    if (((norm < 0) || (norm >= dim))) {
        return -1;
    }
    return norm;
}

int np_ravel_multi_index(int coords3, int shape3, int mode) {
    int d0 = np_get_axis(shape3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int i0 = np_normalize_index(np_get_axis(coords3, (((0 & 4294967295) ^ 2147483648) - 2147483648)), d0, mode);
    int i1 = np_normalize_index(np_get_axis(coords3, (((1 & 4294967295) ^ 2147483648) - 2147483648)), d1, mode);
    int i2 = np_normalize_index(np_get_axis(coords3, (((2 & 4294967295) ^ 2147483648) - 2147483648)), d2, mode);
    if ((((i0 < 0) || (i1 < 0)) || (i2 < 0))) {
        return -1;
    }
    return ((((i0 * d1) + i1) * d2) + i2);
}

int np_unravel_index(int flat_idx, int shape3) {
    int d1 = np_get_axis(shape3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int d2 = np_get_axis(shape3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int i2 = ((((flat_idx ^ d2) < 0) && ((flat_idx.remainder(d2)) != 0)) ? ((flat_idx.remainder(d2)) + d2) : (flat_idx.remainder(d2)));
    int rem = ((((flat_idx ^ d2) < 0) && ((flat_idx.remainder(d2)) != 0)) ? ((flat_idx ~/ d2) - 1) : (flat_idx ~/ d2));
    int i1 = ((((rem ^ d1) < 0) && ((rem.remainder(d1)) != 0)) ? ((rem.remainder(d1)) + d1) : (rem.remainder(d1)));
    int i0 = ((((rem ^ d1) < 0) && ((rem.remainder(d1)) != 0)) ? ((rem ~/ d1) - 1) : (rem ~/ d1));
    return np_pack_vec3((((i0 & 4294967295) ^ 2147483648) - 2147483648), (((i1 & 4294967295) ^ 2147483648) - 2147483648), (((i2 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_pack_buf4(int e0, int e1, int e2, int e3) {
    int u0 = (e0 & 65535);
    int u1 = ((e1 & 65535) << (16 & 63));
    int u2 = ((e2 & 65535) << (32 & 63));
    int u3 = ((e3 & 65535) << (48 & 63));
    return (((u0 | u1) | u2) | u3);
}

int np_buf4_get(int buf, int idx) {
    int shift = (((((idx & 3) * 16) & 4294967295) ^ 2147483648) - 2147483648);
    int raw = ((buf >> (shift & 63)) & 65535);
    return ((raw ^ 32768) - 32768);
}

int np_buf8_get(int buf_lo, int buf_hi, int idx) {
    int word = ((idx < 4) ? buf_lo : buf_hi);
    int lane = ((((idx & 3) & 4294967295) ^ 2147483648) - 2147483648);
    return np_buf4_get(word, lane);
}

int np_apply_ufunc(int op_code, int a, int b) {
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

int np_ufunc_2x2(int buf_a, int shape_a, int str_a, int buf_b, int shape_b, int str_b, int op_code) {
    int out_shape = np_broadcast_shapes(shape_a, shape_b);
    int bstr_a = np_broadcast_strides(shape_a, str_a, out_shape);
    int bstr_b = np_broadcast_strides(shape_b, str_b, out_shape);
    int a00 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b00 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a01 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b01 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a10 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b10 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a11 = np_buf4_get(buf_a, (((np_flat_offset(0, bstr_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b11 = np_buf4_get(buf_b, (((np_flat_offset(0, bstr_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return np_pack_buf4(np_apply_ufunc(op_code, a00, b00), np_apply_ufunc(op_code, a01, b01), np_apply_ufunc(op_code, a10, b10), np_apply_ufunc(op_code, a11, b11));
}

int np_clip_scalar(int v, int a_min, int a_max) {
    return ((v < a_min) ? a_min : ((v > a_max) ? a_max : v));
}

int np_clip_buf4(int buf, int a_min, int a_max) {
    int c0 = np_clip_scalar(np_buf4_get(buf, (((0 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int c1 = np_clip_scalar(np_buf4_get(buf, (((1 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int c2 = np_clip_scalar(np_buf4_get(buf, (((2 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    int c3 = np_clip_scalar(np_buf4_get(buf, (((3 & 4294967295) ^ 2147483648) - 2147483648)), a_min, a_max);
    return np_pack_buf4(c0, c1, c2, c3);
}

int np_matmul_2x2(int buf_a, int off_a, int str_a, int buf_b, int off_b, int str_b) {
    int a00 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a01 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a10 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int a11 = np_buf4_get(buf_a, (((np_flat_offset(off_a, str_a, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b00 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b01 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b10 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int b11 = np_buf4_get(buf_b, (((np_flat_offset(off_b, str_b, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int c00 = ((a00 * b00) + (a01 * b10));
    int c01 = ((a00 * b01) + (a01 * b11));
    int c10 = ((a10 * b00) + (a11 * b10));
    int c11 = ((a10 * b01) + (a11 * b11));
    return np_pack_buf4(c00, c01, c10, c11);
}

int np_reduce_pair(int a, int b, int red_op) {
    if ((red_op == 0)) {
        return (a + b);
    }
    if ((red_op == 1)) {
        return ((a >= b) ? a : b);
    }
    return ((a <= b) ? a : b);
}

int np_reduce_all_2x2(int buf, int base_off, int strides3, int red_op) {
    int v0 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v1 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v2 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v3 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    if ((red_op == 3)) {
        int best_i = ((v1 > v0) ? 1 : 0);
        int best_v = ((v1 > v0) ? v1 : v0);
        best_i = ((v2 > best_v) ? 2 : best_i);
        best_v = ((v2 > best_v) ? v2 : best_v);
        best_i = ((v3 > best_v) ? 3 : best_i);
        return best_i;
    }
    int r01 = np_reduce_pair(v0, v1, red_op);
    int r23 = np_reduce_pair(v2, v3, red_op);
    return np_reduce_pair(r01, r23, red_op);
}

int np_reduce_axis_2x2(int buf, int base_off, int strides3, int axis, int red_op) {
    int v00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v01 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v10 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int v11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int r0 = ((axis == 0) ? np_reduce_pair(v00, v10, red_op) : np_reduce_pair(v00, v01, red_op));
    int r1 = ((axis == 0) ? np_reduce_pair(v01, v11, red_op) : np_reduce_pair(v10, v11, red_op));
    return np_pack_vec3((((r0 & 4294967295) ^ 2147483648) - 2147483648), (((r1 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_trace_2x2(int buf, int base_off, int strides3) {
    int d00 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648), (((0 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    int d11 = np_buf4_get(buf, (((np_flat_offset(base_off, strides3, (((0 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648)) & 4294967295) ^ 2147483648) - 2147483648));
    return (d00 + d11);
}

int np_select_idx(int r0, int r1, int target) {
    int alt = ((r1 == target) ? 1 : 2);
    return ((r0 == target) ? 0 : alt);
}

int np_argsort_vec3(int vec3) {
    int a0 = np_get_axis(vec3, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int a1 = np_get_axis(vec3, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int a2 = np_get_axis(vec3, (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int r0 = (((a0 > a1) ? 1 : 0) + ((a0 > a2) ? 1 : 0));
    int r1 = (((a1 >= a0) ? 1 : 0) + ((a1 > a2) ? 1 : 0));
    int p0 = np_select_idx(r0, r1, 0);
    int p1 = np_select_idx(r0, r1, 1);
    int p2 = np_select_idx(r0, r1, 2);
    return np_pack_vec3((((p0 & 4294967295) ^ 2147483648) - 2147483648), (((p1 & 4294967295) ^ 2147483648) - 2147483648), (((p2 & 4294967295) ^ 2147483648) - 2147483648));
}

int np_pipeline_digest(int seed) {
    int sh_col = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int sh_row = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int sh_2x2 = np_pack_vec3((((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int st_2x2 = np_c_strides(sh_2x2);
    int buf_col = np_pack_buf4((seed + 3), (seed - 5), 0, 0);
    int buf_row = np_pack_buf4(((seed * 2) + 1), ((-seed) + 7), 0, 0);
    int m_a = np_ufunc_2x2(buf_col, sh_col, np_c_strides(sh_col), buf_row, sh_row, np_c_strides(sh_row), (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int m_b = np_pack_buf4((seed + 2), ((-seed) - 3), ((seed * 3) - 1), (seed + 4));
    int st_a_t = np_swapaxes_vec3(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648), (((2 & 4294967295) ^ 2147483648) - 2147483648));
    int off_b_f = np_flip_offset(0, sh_2x2, st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int st_b_f = np_flip_strides(st_2x2, (((1 & 4294967295) ^ 2147483648) - 2147483648));
    int m_c = np_clip_buf4(np_matmul_2x2(m_a, 0, st_a_t, m_b, off_b_f, st_b_f), -500, 500);
    int wrap_idx = np_ravel_multi_index(np_pack_vec3((((-1 & 4294967295) ^ 2147483648) - 2147483648), ((-seed) - 7), (seed + 9)), np_pack_vec3((((4 & 4294967295) ^ 2147483648) - 2147483648), (((5 & 4294967295) ^ 2147483648) - 2147483648), (((6 & 4294967295) ^ 2147483648) - 2147483648)), 1);
    int s_all = np_reduce_all_2x2(m_c, 0, st_2x2, (((0 & 4294967295) ^ 2147483648) - 2147483648));
    int amax = np_reduce_all_2x2(m_c, 0, st_2x2, (((3 & 4294967295) ^ 2147483648) - 2147483648));
    int tr = np_trace_2x2(m_c, 0, st_2x2);
    int asort = np_argsort_vec3(np_pack_vec3((((s_all & 4294967295) ^ 2147483648) - 2147483648), (((tr & 4294967295) ^ 2147483648) - 2147483648), (((wrap_idx & 4294967295) ^ 2147483648) - 2147483648)));
    return (((((s_all * 1000003) + (amax * 99991)) + (tr * 31337)) + (wrap_idx * 1337)) + asort);
}
