# 02_py_broadcast_index.py -- NumPy Broadcasting & Multi-Index Ravel/Unravel Engine (Python)
# Uses Python floor-modulo (%) and floor-division (//) for negative wrap indexing.

def np_broadcast_axis(da: int, db: int) -> int:
    if da == db:
        return da
    if da == 1:
        return db
    if db == 1:
        return da
    return -1

def np_broadcast_shapes(shape_a: int, shape_b: int) -> int:
    d0 = np_broadcast_axis(np_get_axis(shape_a, 0), np_get_axis(shape_b, 0))
    d1 = np_broadcast_axis(np_get_axis(shape_a, 1), np_get_axis(shape_b, 1))
    d2 = np_broadcast_axis(np_get_axis(shape_a, 2), np_get_axis(shape_b, 2))
    if d0 < 0 or d1 < 0 or d2 < 0:
        return -1
    return np_pack_vec3(d0, d1, d2)

def np_broadcast_strides(src_shape: int, src_strides: int, target_shape: int) -> int:
    sd0 = np_get_axis(src_shape, 0)
    sd1 = np_get_axis(src_shape, 1)
    sd2 = np_get_axis(src_shape, 2)
    td0 = np_get_axis(target_shape, 0)
    td1 = np_get_axis(target_shape, 1)
    td2 = np_get_axis(target_shape, 2)
    s0 = (0 if (sd0 == 1 and td0 > 1) else np_get_axis(src_strides, 0))
    s1 = (0 if (sd1 == 1 and td1 > 1) else np_get_axis(src_strides, 1))
    s2 = (0 if (sd2 == 1 and td2 > 1) else np_get_axis(src_strides, 2))
    return np_pack_vec3(s0, s1, s2)

def np_normalize_index(idx: int, dim: int, mode: int) -> int:
    if mode == 1:
        return idx % dim
    if mode == 2:
        return (0 if idx < 0 else ((dim - 1) if idx >= dim else idx))
    norm = (idx + dim if idx < 0 else idx)
    if norm < 0 or norm >= dim:
        return -1
    return norm

def np_ravel_multi_index(coords3: int, shape3: int, mode: int) -> int:
    d0 = np_get_axis(shape3, 0)
    d1 = np_get_axis(shape3, 1)
    d2 = np_get_axis(shape3, 2)
    i0 = np_normalize_index(np_get_axis(coords3, 0), d0, mode)
    i1 = np_normalize_index(np_get_axis(coords3, 1), d1, mode)
    i2 = np_normalize_index(np_get_axis(coords3, 2), d2, mode)
    if i0 < 0 or i1 < 0 or i2 < 0:
        return -1
    return ((i0 * d1) + i1) * d2 + i2

def np_unravel_index(flat_idx: int, shape3: int) -> int:
    d1 = np_get_axis(shape3, 1)
    d2 = np_get_axis(shape3, 2)
    i2 = flat_idx % d2
    rem = flat_idx // d2
    i1 = rem % d1
    i0 = rem // d1
    return np_pack_vec3(i0, i1, i2)
