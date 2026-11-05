function np_pack_vec3(int $d0, int $d1, int $d2): int {
    $u0 = ($d0 & 65535);
    $u1 = ($d1 & 65535);
    $u2 = ($d2 & 65535);
    return ((($u0 << (32 & 63)) | ($u1 << (16 & 63))) | $u2);
}

function np_get_axis(int $vec3, int $axis): int {
    $shift = (((($axis == 0) ? 32 : (($axis == 1) ? 16 : 0)) << 32) >> 32);
    $raw = (($vec3 >> ($shift & 63)) & 65535);
    $signed_val = (((($raw ^ 32768) - 32768) << 32) >> 32);
    return $signed_val;
}

function np_c_strides(int $shape3): int {
    $d1 = np_get_axis($shape3, ((1 << 32) >> 32));
    $d2 = np_get_axis($shape3, ((2 << 32) >> 32));
    return np_pack_vec3(($d1 * $d2), $d2, ((1 << 32) >> 32));
}

function np_f_strides(int $shape3): int {
    $d0 = np_get_axis($shape3, ((0 << 32) >> 32));
    $d1 = np_get_axis($shape3, ((1 << 32) >> 32));
    return np_pack_vec3(((1 << 32) >> 32), $d0, ($d0 * $d1));
}

function np_swapaxes_vec3(int $vec3, int $ax1, int $ax2): int {
    $v0 = np_get_axis($vec3, ((0 << 32) >> 32));
    $v1 = np_get_axis($vec3, ((1 << 32) >> 32));
    $v2 = np_get_axis($vec3, ((2 << 32) >> 32));
    $n0 = (((($ax1 == 0) ? np_get_axis($vec3, $ax2) : (($ax2 == 0) ? np_get_axis($vec3, $ax1) : $v0)) << 32) >> 32);
    $n1 = (((($ax1 == 1) ? np_get_axis($vec3, $ax2) : (($ax2 == 1) ? np_get_axis($vec3, $ax1) : $v1)) << 32) >> 32);
    $n2 = (((($ax1 == 2) ? np_get_axis($vec3, $ax2) : (($ax2 == 2) ? np_get_axis($vec3, $ax1) : $v2)) << 32) >> 32);
    return np_pack_vec3($n0, $n1, $n2);
}

function np_flip_offset(int $base_off, int $shape3, int $strides3, int $axis): int {
    $dim = np_get_axis($shape3, $axis);
    $st = np_get_axis($strides3, $axis);
    return ($base_off + (($dim - 1) * $st));
}

function np_flip_strides(int $strides3, int $axis): int {
    $s0 = np_get_axis($strides3, ((0 << 32) >> 32));
    $s1 = np_get_axis($strides3, ((1 << 32) >> 32));
    $s2 = np_get_axis($strides3, ((2 << 32) >> 32));
    $n0 = (((($axis == 0) ? -$s0 : $s0) << 32) >> 32);
    $n1 = (((($axis == 1) ? -$s1 : $s1) << 32) >> 32);
    $n2 = (((($axis == 2) ? -$s2 : $s2) << 32) >> 32);
    return np_pack_vec3($n0, $n1, $n2);
}

function np_flat_offset(int $base_off, int $strides3, int $i0, int $i1, int $i2): int {
    $s0 = np_get_axis($strides3, ((0 << 32) >> 32));
    $s1 = np_get_axis($strides3, ((1 << 32) >> 32));
    $s2 = np_get_axis($strides3, ((2 << 32) >> 32));
    return ((($base_off + ($i0 * $s0)) + ($i1 * $s1)) + ($i2 * $s2));
}

function np_broadcast_axis(int $da, int $db): int {
    if (($da == $db)) {
        return $da;
    }
    if (($da == 1)) {
        return $db;
    }
    if (($db == 1)) {
        return $da;
    }
    return -1;
}

function np_broadcast_shapes(int $shape_a, int $shape_b): int {
    $d0 = np_broadcast_axis(np_get_axis($shape_a, ((0 << 32) >> 32)), np_get_axis($shape_b, ((0 << 32) >> 32)));
    $d1 = np_broadcast_axis(np_get_axis($shape_a, ((1 << 32) >> 32)), np_get_axis($shape_b, ((1 << 32) >> 32)));
    $d2 = np_broadcast_axis(np_get_axis($shape_a, ((2 << 32) >> 32)), np_get_axis($shape_b, ((2 << 32) >> 32)));
    if (((($d0 < 0) || ($d1 < 0)) || ($d2 < 0))) {
        return -1;
    }
    return np_pack_vec3((($d0 << 32) >> 32), (($d1 << 32) >> 32), (($d2 << 32) >> 32));
}

function np_broadcast_strides(int $src_shape, int $src_strides, int $target_shape): int {
    $sd0 = np_get_axis($src_shape, ((0 << 32) >> 32));
    $sd1 = np_get_axis($src_shape, ((1 << 32) >> 32));
    $sd2 = np_get_axis($src_shape, ((2 << 32) >> 32));
    $td0 = np_get_axis($target_shape, ((0 << 32) >> 32));
    $td1 = np_get_axis($target_shape, ((1 << 32) >> 32));
    $td2 = np_get_axis($target_shape, ((2 << 32) >> 32));
    $s0 = ((($sd0 == 1) && ($td0 > 1)) ? 0 : np_get_axis($src_strides, ((0 << 32) >> 32)));
    $s1 = ((($sd1 == 1) && ($td1 > 1)) ? 0 : np_get_axis($src_strides, ((1 << 32) >> 32)));
    $s2 = ((($sd2 == 1) && ($td2 > 1)) ? 0 : np_get_axis($src_strides, ((2 << 32) >> 32)));
    return np_pack_vec3((($s0 << 32) >> 32), (($s1 << 32) >> 32), (($s2 << 32) >> 32));
}

function np_normalize_index(int $idx, int $dim, int $mode): int {
    if (($mode == 1)) {
        return (((($idx ^ $dim) < 0) && (($idx % $dim) != 0)) ? (($idx % $dim) + $dim) : ($idx % $dim));
    }
    if (($mode == 2)) {
        return (($idx < 0) ? 0 : (($idx >= $dim) ? ($dim - 1) : $idx));
    }
    $norm = (($idx < 0) ? ($idx + $dim) : $idx);
    if ((($norm < 0) || ($norm >= $dim))) {
        return -1;
    }
    return $norm;
}

function np_ravel_multi_index(int $coords3, int $shape3, int $mode): int {
    $d0 = np_get_axis($shape3, ((0 << 32) >> 32));
    $d1 = np_get_axis($shape3, ((1 << 32) >> 32));
    $d2 = np_get_axis($shape3, ((2 << 32) >> 32));
    $i0 = np_normalize_index(np_get_axis($coords3, ((0 << 32) >> 32)), $d0, $mode);
    $i1 = np_normalize_index(np_get_axis($coords3, ((1 << 32) >> 32)), $d1, $mode);
    $i2 = np_normalize_index(np_get_axis($coords3, ((2 << 32) >> 32)), $d2, $mode);
    if (((($i0 < 0) || ($i1 < 0)) || ($i2 < 0))) {
        return -1;
    }
    return (((($i0 * $d1) + $i1) * $d2) + $i2);
}

function np_unravel_index(int $flat_idx, int $shape3): int {
    $d1 = np_get_axis($shape3, ((1 << 32) >> 32));
    $d2 = np_get_axis($shape3, ((2 << 32) >> 32));
    $i2 = (((($flat_idx ^ $d2) < 0) && (($flat_idx % $d2) != 0)) ? (($flat_idx % $d2) + $d2) : ($flat_idx % $d2));
    $rem = (((($flat_idx ^ $d2) < 0) && (($flat_idx % $d2) != 0)) ? (($flat_idx / $d2) - 1) : ($flat_idx / $d2));
    $i1 = (((($rem ^ $d1) < 0) && (($rem % $d1) != 0)) ? (($rem % $d1) + $d1) : ($rem % $d1));
    $i0 = (((($rem ^ $d1) < 0) && (($rem % $d1) != 0)) ? (($rem / $d1) - 1) : ($rem / $d1));
    return np_pack_vec3((($i0 << 32) >> 32), (($i1 << 32) >> 32), (($i2 << 32) >> 32));
}

function np_pack_buf4(int $e0, int $e1, int $e2, int $e3): int {
    $u0 = ($e0 & 65535);
    $u1 = (($e1 & 65535) << (16 & 63));
    $u2 = (($e2 & 65535) << (32 & 63));
    $u3 = (($e3 & 65535) << (48 & 63));
    return ((($u0 | $u1) | $u2) | $u3);
}

function np_buf4_get(int $buf, int $idx): int {
    $shift = (((($idx & 3) * 16) << 32) >> 32);
    $raw = (($buf >> ($shift & 63)) & 65535);
    return (($raw ^ 32768) - 32768);
}

function np_buf8_get(int $buf_lo, int $buf_hi, int $idx): int {
    $word = (($idx < 4) ? $buf_lo : $buf_hi);
    $lane = ((($idx & 3) << 32) >> 32);
    return np_buf4_get($word, $lane);
}

function np_apply_ufunc(int $op_code, int $a, int $b): int {
    if (($op_code == 0)) {
        return ($a + $b);
    }
    if (($op_code == 1)) {
        return ($a - $b);
    }
    if (($op_code == 2)) {
        return ($a * $b);
    }
    if (($op_code == 3)) {
        return (($a < $b) ? $a : $b);
    }
    if (($op_code == 4)) {
        return (($a > $b) ? $a : $b);
    }
    return ($a ^ $b);
}

function np_ufunc_2x2(int $buf_a, int $shape_a, int $str_a, int $buf_b, int $shape_b, int $str_b, int $op_code): int {
    $out_shape = np_broadcast_shapes($shape_a, $shape_b);
    $bstr_a = np_broadcast_strides($shape_a, $str_a, $out_shape);
    $bstr_b = np_broadcast_strides($shape_b, $str_b, $out_shape);
    $a00 = np_buf4_get($buf_a, ((np_flat_offset(0, $bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $b00 = np_buf4_get($buf_b, ((np_flat_offset(0, $bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $a01 = np_buf4_get($buf_a, ((np_flat_offset(0, $bstr_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $b01 = np_buf4_get($buf_b, ((np_flat_offset(0, $bstr_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $a10 = np_buf4_get($buf_a, ((np_flat_offset(0, $bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $b10 = np_buf4_get($buf_b, ((np_flat_offset(0, $bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $a11 = np_buf4_get($buf_a, ((np_flat_offset(0, $bstr_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $b11 = np_buf4_get($buf_b, ((np_flat_offset(0, $bstr_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    return np_pack_buf4(np_apply_ufunc($op_code, $a00, $b00), np_apply_ufunc($op_code, $a01, $b01), np_apply_ufunc($op_code, $a10, $b10), np_apply_ufunc($op_code, $a11, $b11));
}

function np_clip_scalar(int $v, int $a_min, int $a_max): int {
    return (($v < $a_min) ? $a_min : (($v > $a_max) ? $a_max : $v));
}

function np_clip_buf4(int $buf, int $a_min, int $a_max): int {
    $c0 = np_clip_scalar(np_buf4_get($buf, ((0 << 32) >> 32)), $a_min, $a_max);
    $c1 = np_clip_scalar(np_buf4_get($buf, ((1 << 32) >> 32)), $a_min, $a_max);
    $c2 = np_clip_scalar(np_buf4_get($buf, ((2 << 32) >> 32)), $a_min, $a_max);
    $c3 = np_clip_scalar(np_buf4_get($buf, ((3 << 32) >> 32)), $a_min, $a_max);
    return np_pack_buf4($c0, $c1, $c2, $c3);
}

function np_matmul_2x2(int $buf_a, int $off_a, int $str_a, int $buf_b, int $off_b, int $str_b): int {
    $a00 = np_buf4_get($buf_a, ((np_flat_offset($off_a, $str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $a01 = np_buf4_get($buf_a, ((np_flat_offset($off_a, $str_a, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $a10 = np_buf4_get($buf_a, ((np_flat_offset($off_a, $str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $a11 = np_buf4_get($buf_a, ((np_flat_offset($off_a, $str_a, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $b00 = np_buf4_get($buf_b, ((np_flat_offset($off_b, $str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $b01 = np_buf4_get($buf_b, ((np_flat_offset($off_b, $str_b, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $b10 = np_buf4_get($buf_b, ((np_flat_offset($off_b, $str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $b11 = np_buf4_get($buf_b, ((np_flat_offset($off_b, $str_b, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $c00 = (($a00 * $b00) + ($a01 * $b10));
    $c01 = (($a00 * $b01) + ($a01 * $b11));
    $c10 = (($a10 * $b00) + ($a11 * $b10));
    $c11 = (($a10 * $b01) + ($a11 * $b11));
    return np_pack_buf4($c00, $c01, $c10, $c11);
}

function np_reduce_pair(int $a, int $b, int $red_op): int {
    if (($red_op == 0)) {
        return ($a + $b);
    }
    if (($red_op == 1)) {
        return (($a >= $b) ? $a : $b);
    }
    return (($a <= $b) ? $a : $b);
}

function np_reduce_all_2x2(int $buf, int $base_off, int $strides3, int $red_op): int {
    $v0 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $v1 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $v2 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $v3 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    if (($red_op == 3)) {
        $best_i = (($v1 > $v0) ? 1 : 0);
        $best_v = (($v1 > $v0) ? $v1 : $v0);
        $best_i = (($v2 > $best_v) ? 2 : $best_i);
        $best_v = (($v2 > $best_v) ? $v2 : $best_v);
        $best_i = (($v3 > $best_v) ? 3 : $best_i);
        return $best_i;
    }
    $r01 = np_reduce_pair($v0, $v1, $red_op);
    $r23 = np_reduce_pair($v2, $v3, $red_op);
    return np_reduce_pair($r01, $r23, $red_op);
}

function np_reduce_axis_2x2(int $buf, int $base_off, int $strides3, int $axis, int $red_op): int {
    $v00 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $v01 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $v10 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $v11 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    $r0 = (($axis == 0) ? np_reduce_pair($v00, $v10, $red_op) : np_reduce_pair($v00, $v01, $red_op));
    $r1 = (($axis == 0) ? np_reduce_pair($v01, $v11, $red_op) : np_reduce_pair($v10, $v11, $red_op));
    return np_pack_vec3((($r0 << 32) >> 32), (($r1 << 32) >> 32), ((0 << 32) >> 32));
}

function np_trace_2x2(int $buf, int $base_off, int $strides3): int {
    $d00 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((0 << 32) >> 32), ((0 << 32) >> 32)) << 32) >> 32));
    $d11 = np_buf4_get($buf, ((np_flat_offset($base_off, $strides3, ((0 << 32) >> 32), ((1 << 32) >> 32), ((1 << 32) >> 32)) << 32) >> 32));
    return ($d00 + $d11);
}

function np_select_idx(int $r0, int $r1, int $target): int {
    $alt = (($r1 == $target) ? 1 : 2);
    return (($r0 == $target) ? 0 : $alt);
}

function np_argsort_vec3(int $vec3): int {
    $a0 = np_get_axis($vec3, ((0 << 32) >> 32));
    $a1 = np_get_axis($vec3, ((1 << 32) >> 32));
    $a2 = np_get_axis($vec3, ((2 << 32) >> 32));
    $r0 = ((($a0 > $a1) ? 1 : 0) + (($a0 > $a2) ? 1 : 0));
    $r1 = ((($a1 >= $a0) ? 1 : 0) + (($a1 > $a2) ? 1 : 0));
    $p0 = np_select_idx($r0, $r1, 0);
    $p1 = np_select_idx($r0, $r1, 1);
    $p2 = np_select_idx($r0, $r1, 2);
    return np_pack_vec3((($p0 << 32) >> 32), (($p1 << 32) >> 32), (($p2 << 32) >> 32));
}

function np_pipeline_digest(int $seed): int {
    $sh_col = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((1 << 32) >> 32));
    $sh_row = np_pack_vec3(((1 << 32) >> 32), ((1 << 32) >> 32), ((2 << 32) >> 32));
    $sh_2x2 = np_pack_vec3(((1 << 32) >> 32), ((2 << 32) >> 32), ((2 << 32) >> 32));
    $st_2x2 = np_c_strides($sh_2x2);
    $buf_col = np_pack_buf4(($seed + 3), ($seed - 5), 0, 0);
    $buf_row = np_pack_buf4((($seed * 2) + 1), (-$seed + 7), 0, 0);
    $m_a = np_ufunc_2x2($buf_col, $sh_col, np_c_strides($sh_col), $buf_row, $sh_row, np_c_strides($sh_row), ((0 << 32) >> 32));
    $m_b = np_pack_buf4(($seed + 2), (-$seed - 3), (($seed * 3) - 1), ($seed + 4));
    $st_a_t = np_swapaxes_vec3($st_2x2, ((1 << 32) >> 32), ((2 << 32) >> 32));
    $off_b_f = np_flip_offset(0, $sh_2x2, $st_2x2, ((1 << 32) >> 32));
    $st_b_f = np_flip_strides($st_2x2, ((1 << 32) >> 32));
    $m_c = np_clip_buf4(np_matmul_2x2($m_a, 0, $st_a_t, $m_b, $off_b_f, $st_b_f), -500, 500);
    $wrap_idx = np_ravel_multi_index(np_pack_vec3(((-1 << 32) >> 32), (-$seed - 7), ($seed + 9)), np_pack_vec3(((4 << 32) >> 32), ((5 << 32) >> 32), ((6 << 32) >> 32)), 1);
    $s_all = np_reduce_all_2x2($m_c, 0, $st_2x2, ((0 << 32) >> 32));
    $amax = np_reduce_all_2x2($m_c, 0, $st_2x2, ((3 << 32) >> 32));
    $tr = np_trace_2x2($m_c, 0, $st_2x2);
    $asort = np_argsort_vec3(np_pack_vec3((($s_all << 32) >> 32), (($tr << 32) >> 32), (($wrap_idx << 32) >> 32)));
    return ((((($s_all * 1000003) + ($amax * 99991)) + ($tr * 31337)) + ($wrap_idx * 1337)) + $asort);
}
