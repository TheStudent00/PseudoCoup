func std_rotl32_c(x int64, r int64) int64 {
    return (((x << r) | (x >> (32 - r))) & 4294967295)
}

func std_mul32(a int64, b int64) int64 {
    lo := ((a * (b & 65535)) & 4294967295)
    hi := (((a * (b >> 16)) << 16) & 4294967295)
    return ((lo + hi) & 4294967295)
}

func std_xxh32_round(acc int64, input int64) int64 {
    step := ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295)
    rot := std_rotl32_c(step, (13 & 4294967295))
    return std_mul32(rot, (2654435761 & 4294967295))
}

func std_xxh32_avalanche(h int64) int64 {
    h1 := std_mul32((h ^ (h >> 15)), (2246822519 & 4294967295))
    h2 := std_mul32((h1 ^ (h1 >> 13)), (3266489917 & 4294967295))
    return ((h2 ^ (h2 >> 16)) & 4294967295)
}

func std_xxh32_word64(data int64, seed int64) int64 {
    lo := ((data & 4294967295) & 4294967295)
    hi := (((data >> (32 & 63)) & 4294967295) & 4294967295)
    v1 := std_xxh32_round(((seed + 374761393) + 8), lo)
    v2 := std_xxh32_round(v1, hi)
    return std_xxh32_avalanche(v2)
}

func std_lz4_pack_token(lit_len int64, match_len int64, offset int64, literal_u32 int64) int64 {
    lz4_hdr := (((lit_len & 15) << 4) | (match_len & 15))
    off_bits := ((offset & 65535) << 8)
    lit_bits := ((literal_u32 & 4294967295) << 24)
    return ((lz4_hdr | off_bits) | lit_bits)
}

func std_lz4_token_lit_len(frame int64) int64 {
    return (((frame >> (4 & 63)) & 15) & 255)
}

func std_lz4_token_match_len(frame int64) int64 {
    return ((frame & 15) & 255)
}

func std_lz4_match_offset(frame int64) int64 {
    return (((frame >> (8 & 63)) & 65535) & 65535)
}

func std_lz4_literal(frame int64) int64 {
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295)
}

func std_rotl32_rs(x int64, b int64) int64 {
    return (((x << b) | (x >> (32 - b))) & 4294967295)
}

func std_pack_u32_pair(lo int64, hi int64) int64 {
    ulo := (lo & 4294967295)
    uhi := ((hi & 4294967295) << 32)
    return (ulo | uhi)
}

func std_pair_lo(p int64) int64 {
    return ((p & 4294967295) & 4294967295)
}

func std_pair_hi(p int64) int64 {
    return (((p >> (32 & 63)) & 4294967295) & 4294967295)
}

func std_sipround_half1(v0 int64, v1 int64, v2 int64, v3 int64) int64 {
    a0 := ((v0 + v1) & 4294967295)
    b0 := std_rotl32_rs(a0, (16 & 4294967295))
    a2 := ((v2 + v3) & 4294967295)
    a3 := ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295)
    c0 := ((b0 + a3) & 4294967295)
    c3 := ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295)
    return std_pack_u32_pair(c0, c3)
}

func std_sipround_half2(v0 int64, v1 int64, v2 int64, v3 int64) int64 {
    a0 := ((v0 + v1) & 4294967295)
    a1 := ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295)
    a2 := ((v2 + v3) & 4294967295)
    c2 := ((a2 + a1) & 4294967295)
    c1 := ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295)
    d2 := std_rotl32_rs(c2, (16 & 4294967295))
    return std_pack_u32_pair(c1, d2)
}

func std_halfsiphash_1_3(k0 int64, k1 int64, m0 int64, m1 int64) int64 {
    v0 := k0
    v1 := k1
    v2 := ((k0 ^ 1819895653) & 4294967295)
    v3 := (((k1 ^ 1952801890) ^ m0) & 4294967295)
    p03_a := std_sipround_half1(v0, v1, v2, v3)
    p12_a := std_sipround_half2(v0, v1, v2, v3)
    w0 := ((std_pair_lo(p03_a) ^ m0) & 4294967295)
    w1 := std_pair_lo(p12_a)
    w2 := ((std_pair_hi(p12_a) ^ 255) & 4294967295)
    w3 := ((std_pair_hi(p03_a) ^ m1) & 4294967295)
    p03_b := std_sipround_half1(w0, w1, w2, w3)
    p12_b := std_sipround_half2(w0, w1, w2, w3)
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295)
}

func std_zigzag_encode(n int64) int64 {
    return (((n << 1) ^ (n >> 31)) & 4294967295)
}

func std_zigzag_decode(z int64) int64 {
    return (((((z >> 1) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648)
}

func std_leb128_encode_u32(v int64) int64 {
    b0 := (((v & 127) | func() int64 { if (v >= 128) { return 128 } else { return 0 } }()) & 4294967295)
    v1 := ((v >> 7) & 4294967295)
    b1 := (((v1 & 127) | func() int64 { if (v1 >= 128) { return 128 } else { return 0 } }()) & 4294967295)
    v2 := ((v >> 14) & 4294967295)
    b2 := (((v2 & 127) | func() int64 { if (v2 >= 128) { return 128 } else { return 0 } }()) & 4294967295)
    v3 := (((v >> 21) & 127) & 4294967295)
    nbytes := (((1 + func() int64 { if (v >= 128) { return 1 } else { return 0 } }()) + func() int64 { if (v >= 16384) { return 1 } else { return 0 } }()) + func() int64 { if (v >= 2097152) { return 1 } else { return 0 } }())
    wire := ((((b0 | (b1 << 8)) | (b2 << 16)) | (v3 << 24)) & 4294967295)
    return (wire | func() int64 { if ((32 >= 0) && (32 < 64)) { return (nbytes << (32 & 63)) } else { return 0 } }())
}

func std_leb128_decode_u32(packed int64) int64 {
    b0 := (packed & 255)
    b1 := (func() int64 { if ((8 >= 0) && (8 < 64)) { return (packed >> (8 & 63)) } else { return (packed >> 63) } }() & 255)
    b2 := (func() int64 { if ((16 >= 0) && (16 < 64)) { return (packed >> (16 & 63)) } else { return (packed >> 63) } }() & 255)
    b3 := (func() int64 { if ((24 >= 0) && (24 < 64)) { return (packed >> (24 & 63)) } else { return (packed >> 63) } }() & 255)
    acc := (b0 & 127)
    if (((b0 & 128) != 0)) {
        acc = (acc | func() int64 { if ((7 >= 0) && (7 < 64)) { return ((b1 & 127) << (7 & 63)) } else { return 0 } }())
        if (((b1 & 128) != 0)) {
            acc = (acc | func() int64 { if ((14 >= 0) && (14 < 64)) { return ((b2 & 127) << (14 & 63)) } else { return 0 } }())
            if (((b2 & 128) != 0)) {
                acc = (acc | func() int64 { if ((21 >= 0) && (21 < 64)) { return ((b3 & 127) << (21 & 63)) } else { return 0 } }())
            }
        }
    }
    return (acc & 4294967295)
}

func std_ringbuf_push(head int64, tail int64, cap_mask int64, n_items int64) int64 {
    cap_size := ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648)
    used := (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    free_slots := (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648)
    accepted := (((func() int64 { if (n_items < free_slots) { return n_items } else { return free_slots } }() & 4294967295) ^ 2147483648) - 2147483648)
    new_tail := (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    new_used := ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648)
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295))
}

func std_circular_tensor_offset(coord_t int64, coord_ch int64, dim_t int64, dim_ch int64, stride_t int64, stride_ch int64) int64 {
    wt := func() int64 { if (((coord_t ^ dim_t) < 0) && ((coord_t % dim_t) != 0)) { return ((coord_t % dim_t) + dim_t) } else { return (coord_t % dim_t) } }()
    wch := func() int64 { if (((coord_ch ^ dim_ch) < 0) && ((coord_ch % dim_ch) != 0)) { return ((coord_ch % dim_ch) + dim_ch) } else { return (coord_ch % dim_ch) } }()
    return ((wt * stride_t) + (wch * stride_ch))
}

func std_polyglot_packet_pipeline(delta_a int64, delta_b int64, lookback_t int64, key0 int64, key1 int64) int64 {
    tensor_off := std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1)
    ring_st := std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648))
    ring_occ := std_pair_hi(ring_st)
    zz_a := std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648))
    zz_b := std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648))
    leb_a := std_leb128_encode_u32(zz_a)
    leb_b := std_leb128_encode_u32(zz_b)
    dec_a := std_zigzag_decode(std_leb128_decode_u32(leb_a))
    dec_b := std_zigzag_decode(std_leb128_decode_u32(leb_b))
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1
    }
    wire_bytes := (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15))
    lz4_frame := std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a)
    xxh := std_xxh32_word64(lz4_frame, (key0 & 4294967295))
    mac := std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b)
    unpacked_lit := std_lz4_literal(lz4_frame)
    if ((unpacked_lit != zz_a)) {
        return -2
    }
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ)
}
