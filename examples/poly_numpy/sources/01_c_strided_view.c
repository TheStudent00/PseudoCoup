// 01_c_strided_view.c -- NumPy `multiarray` 3D Strided Memory & View Engine (C)
// Packs 3D shapes and signed strides (d0, d1, d2) into 64-bit descriptors (3x signed 16-bit lanes).

int64_t np_pack_vec3(int32_t d0, int32_t d1, int32_t d2) {
    int64_t u0 = d0 & 65535;
    int64_t u1 = d1 & 65535;
    int64_t u2 = d2 & 65535;
    return (u0 << 32) | (u1 << 16) | u2;
}

int32_t np_get_axis(int64_t vec3, int32_t axis) {
    int32_t shift = (axis == 0 ? 32 : (axis == 1 ? 16 : 0));
    int64_t raw = (vec3 >> shift) & 65535;
    int32_t signed_val = (raw ^ 32768) - 32768;
    return signed_val;
}

int64_t np_c_strides(int64_t shape3) {
    int32_t d1 = np_get_axis(shape3, 1);
    int32_t d2 = np_get_axis(shape3, 2);
    return np_pack_vec3(d1 * d2, d2, 1);
}

int64_t np_f_strides(int64_t shape3) {
    int32_t d0 = np_get_axis(shape3, 0);
    int32_t d1 = np_get_axis(shape3, 1);
    return np_pack_vec3(1, d0, d0 * d1);
}

int64_t np_swapaxes_vec3(int64_t vec3, int32_t ax1, int32_t ax2) {
    int32_t v0 = np_get_axis(vec3, 0);
    int32_t v1 = np_get_axis(vec3, 1);
    int32_t v2 = np_get_axis(vec3, 2);
    int32_t n0 = (ax1 == 0 ? np_get_axis(vec3, ax2) : (ax2 == 0 ? np_get_axis(vec3, ax1) : v0));
    int32_t n1 = (ax1 == 1 ? np_get_axis(vec3, ax2) : (ax2 == 1 ? np_get_axis(vec3, ax1) : v1));
    int32_t n2 = (ax1 == 2 ? np_get_axis(vec3, ax2) : (ax2 == 2 ? np_get_axis(vec3, ax1) : v2));
    return np_pack_vec3(n0, n1, n2);
}

int64_t np_flip_offset(int64_t base_off, int64_t shape3, int64_t strides3, int32_t axis) {
    int32_t dim = np_get_axis(shape3, axis);
    int32_t st = np_get_axis(strides3, axis);
    return base_off + ((dim - 1) * st);
}

int64_t np_flip_strides(int64_t strides3, int32_t axis) {
    int32_t s0 = np_get_axis(strides3, 0);
    int32_t s1 = np_get_axis(strides3, 1);
    int32_t s2 = np_get_axis(strides3, 2);
    int32_t n0 = (axis == 0 ? (-s0) : s0);
    int32_t n1 = (axis == 1 ? (-s1) : s1);
    int32_t n2 = (axis == 2 ? (-s2) : s2);
    return np_pack_vec3(n0, n1, n2);
}

int64_t np_flat_offset(int64_t base_off, int64_t strides3, int32_t i0, int32_t i1, int32_t i2) {
    int32_t s0 = np_get_axis(strides3, 0);
    int32_t s1 = np_get_axis(strides3, 1);
    int32_t s2 = np_get_axis(strides3, 2);
    return base_off + (i0 * s0) + (i1 * s1) + (i2 * s2);
}
