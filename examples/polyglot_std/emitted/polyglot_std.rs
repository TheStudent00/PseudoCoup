fn std_rotl32_c(x: i64, r: i64) -> i64 {
    return (((x << (r & 63)) | (x >> ((32 - r) & 63))) & 4294967295);
}

fn std_mul32(a: i64, b: i64) -> i64 {
    let mut lo: i64 = ((a * (b & 65535)) & 4294967295);
    let mut hi: i64 = (((a * (b >> (16 & 63))) << (16 & 63)) & 4294967295);
    return ((lo + hi) & 4294967295);
}

fn std_xxh32_round(acc: i64, input: i64) -> i64 {
    let mut step: i64 = ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295);
    let mut rot: i64 = std_rotl32_c(step, (13 & 4294967295));
    return std_mul32(rot, (2654435761 & 4294967295));
}

fn std_xxh32_avalanche(h: i64) -> i64 {
    let mut h1: i64 = std_mul32((h ^ (h >> (15 & 63))), (2246822519 & 4294967295));
    let mut h2: i64 = std_mul32((h1 ^ (h1 >> (13 & 63))), (3266489917 & 4294967295));
    return ((h2 ^ (h2 >> (16 & 63))) & 4294967295);
}

fn std_xxh32_word64(data: i64, seed: i64) -> i64 {
    let mut lo: i64 = ((data & 4294967295) & 4294967295);
    let mut hi: i64 = (((data >> (32 & 63)) & 4294967295) & 4294967295);
    let mut v1: i64 = std_xxh32_round(((seed + 374761393) + 8), lo);
    let mut v2: i64 = std_xxh32_round(v1, hi);
    return std_xxh32_avalanche(v2);
}

fn std_lz4_pack_token(lit_len: i64, match_len: i64, offset: i64, literal_u32: i64) -> i64 {
    let mut token: i64 = (((lit_len & 15) << (4 & 63)) | (match_len & 15));
    let mut off_bits: i64 = ((offset & 65535) << (8 & 63));
    let mut lit_bits: i64 = ((literal_u32 & 4294967295) << (24 & 63));
    return ((token | off_bits) | lit_bits);
}

fn std_lz4_token_lit_len(frame: i64) -> i64 {
    return (((frame >> (4 & 63)) & 15) & 255);
}

fn std_lz4_token_match_len(frame: i64) -> i64 {
    return ((frame & 15) & 255);
}

fn std_lz4_match_offset(frame: i64) -> i64 {
    return (((frame >> (8 & 63)) & 65535) & 65535);
}

fn std_lz4_literal(frame: i64) -> i64 {
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295);
}

fn std_rotl32_rs(x: i64, b: i64) -> i64 {
    return (((x << (b & 63)) | (x >> ((32 - b) & 63))) & 4294967295);
}

fn std_pack_u32_pair(lo: i64, hi: i64) -> i64 {
    let mut ulo: i64 = (lo & 4294967295);
    let mut uhi: i64 = ((hi & 4294967295) << (32 & 63));
    return (ulo | uhi);
}

fn std_pair_lo(p: i64) -> i64 {
    return ((p & 4294967295) & 4294967295);
}

fn std_pair_hi(p: i64) -> i64 {
    return (((p >> (32 & 63)) & 4294967295) & 4294967295);
}

fn std_sipround_half1(v0: i64, v1: i64, v2: i64, v3: i64) -> i64 {
    let mut a0: i64 = ((v0 + v1) & 4294967295);
    let mut b0: i64 = std_rotl32_rs(a0, (16 & 4294967295));
    let mut a2: i64 = ((v2 + v3) & 4294967295);
    let mut a3: i64 = ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295);
    let mut c0: i64 = ((b0 + a3) & 4294967295);
    let mut c3: i64 = ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295);
    return std_pack_u32_pair(c0, c3);
}

fn std_sipround_half2(v0: i64, v1: i64, v2: i64, v3: i64) -> i64 {
    let mut a0: i64 = ((v0 + v1) & 4294967295);
    let mut a1: i64 = ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295);
    let mut a2: i64 = ((v2 + v3) & 4294967295);
    let mut c2: i64 = ((a2 + a1) & 4294967295);
    let mut c1: i64 = ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295);
    let mut d2: i64 = std_rotl32_rs(c2, (16 & 4294967295));
    return std_pack_u32_pair(c1, d2);
}

fn std_halfsiphash_1_3(k0: i64, k1: i64, m0: i64, m1: i64) -> i64 {
    let mut v0: i64 = k0;
    let mut v1: i64 = k1;
    let mut v2: i64 = ((k0 ^ 1819895653) & 4294967295);
    let mut v3: i64 = (((k1 ^ 1952801890) ^ m0) & 4294967295);
    let mut p03_a: i64 = std_sipround_half1(v0, v1, v2, v3);
    let mut p12_a: i64 = std_sipround_half2(v0, v1, v2, v3);
    let mut w0: i64 = ((std_pair_lo(p03_a) ^ m0) & 4294967295);
    let mut w1: i64 = std_pair_lo(p12_a);
    let mut w2: i64 = ((std_pair_hi(p12_a) ^ 255) & 4294967295);
    let mut w3: i64 = ((std_pair_hi(p03_a) ^ m1) & 4294967295);
    let mut p03_b: i64 = std_sipround_half1(w0, w1, w2, w3);
    let mut p12_b: i64 = std_sipround_half2(w0, w1, w2, w3);
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295);
}

fn std_zigzag_encode(n: i64) -> i64 {
    return (((if ((1 >= 0) && (1 < 64)) { (n << (1 & 63)) } else { 0 }) ^ (if ((31 >= 0) && (31 < 64)) { (n >> (31 & 63)) } else { (n >> (63 & 63)) })) & 4294967295);
}

fn std_zigzag_decode(z: i64) -> i64 {
    return (((((if ((1 >= 0) && (1 < 64)) { (z >> (1 & 63)) } else { (z >> (63 & 63)) }) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648);
}

fn std_leb128_encode_u32(v: i64) -> i64 {
    let mut b0: i64 = (((v & 127) | (if (v >= 128) { 128 } else { 0 })) & 4294967295);
    let mut v1: i64 = ((if ((7 >= 0) && (7 < 64)) { (v >> (7 & 63)) } else { (v >> (63 & 63)) }) & 4294967295);
    let mut b1: i64 = (((v1 & 127) | (if (v1 >= 128) { 128 } else { 0 })) & 4294967295);
    let mut v2: i64 = ((if ((14 >= 0) && (14 < 64)) { (v >> (14 & 63)) } else { (v >> (63 & 63)) }) & 4294967295);
    let mut b2: i64 = (((v2 & 127) | (if (v2 >= 128) { 128 } else { 0 })) & 4294967295);
    let mut v3: i64 = (((if ((21 >= 0) && (21 < 64)) { (v >> (21 & 63)) } else { (v >> (63 & 63)) }) & 127) & 4294967295);
    let mut nbytes: i64 = (((1 + (if (v >= 128) { 1 } else { 0 })) + (if (v >= 16384) { 1 } else { 0 })) + (if (v >= 2097152) { 1 } else { 0 }));
    let mut wire: i64 = ((((b0 | (if ((8 >= 0) && (8 < 64)) { (b1 << (8 & 63)) } else { 0 })) | (if ((16 >= 0) && (16 < 64)) { (b2 << (16 & 63)) } else { 0 })) | (if ((24 >= 0) && (24 < 64)) { (v3 << (24 & 63)) } else { 0 })) & 4294967295);
    return (wire | (if ((32 >= 0) && (32 < 64)) { (nbytes << (32 & 63)) } else { 0 }));
}

fn std_leb128_decode_u32(packed: i64) -> i64 {
    let mut b0: i64 = (packed & 255);
    let mut b1: i64 = ((if ((8 >= 0) && (8 < 64)) { (packed >> (8 & 63)) } else { (packed >> (63 & 63)) }) & 255);
    let mut b2: i64 = ((if ((16 >= 0) && (16 < 64)) { (packed >> (16 & 63)) } else { (packed >> (63 & 63)) }) & 255);
    let mut b3: i64 = ((if ((24 >= 0) && (24 < 64)) { (packed >> (24 & 63)) } else { (packed >> (63 & 63)) }) & 255);
    let mut acc: i64 = (b0 & 127);
    if (((b0 & 128) != 0)) {
        acc = (acc | (if ((7 >= 0) && (7 < 64)) { ((b1 & 127) << (7 & 63)) } else { 0 }));
        if (((b1 & 128) != 0)) {
            acc = (acc | (if ((14 >= 0) && (14 < 64)) { ((b2 & 127) << (14 & 63)) } else { 0 }));
            if (((b2 & 128) != 0)) {
                acc = (acc | (if ((21 >= 0) && (21 < 64)) { ((b3 & 127) << (21 & 63)) } else { 0 }));
            }
        }
    }
    return (acc & 4294967295);
}

fn std_ringbuf_push(head: i64, tail: i64, cap_mask: i64, n_items: i64) -> i64 {
    let mut cap_size: i64 = ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648);
    let mut used: i64 = (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    let mut free_slots: i64 = (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648);
    let mut accepted: i64 = ((((if (n_items < free_slots) { n_items } else { free_slots }) & 4294967295) ^ 2147483648) - 2147483648);
    let mut new_tail: i64 = (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    let mut new_used: i64 = ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648);
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295));
}

fn std_circular_tensor_offset(coord_t: i64, coord_ch: i64, dim_t: i64, dim_ch: i64, stride_t: i64, stride_ch: i64) -> i64 {
    let mut wt: i64 = (if (((coord_t ^ dim_t) < 0) && ((coord_t % dim_t) != 0)) { ((coord_t % dim_t) + dim_t) } else { (coord_t % dim_t) });
    let mut wch: i64 = (if (((coord_ch ^ dim_ch) < 0) && ((coord_ch % dim_ch) != 0)) { ((coord_ch % dim_ch) + dim_ch) } else { (coord_ch % dim_ch) });
    return ((wt * stride_t) + (wch * stride_ch));
}

fn std_polyglot_packet_pipeline(delta_a: i64, delta_b: i64, lookback_t: i64, key0: i64, key1: i64) -> i64 {
    let mut tensor_off: i64 = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1);
    let mut ring_st: i64 = std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648));
    let mut ring_occ: i64 = std_pair_hi(ring_st);
    let mut zz_a: i64 = std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648));
    let mut zz_b: i64 = std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648));
    let mut leb_a: i64 = std_leb128_encode_u32(zz_a);
    let mut leb_b: i64 = std_leb128_encode_u32(zz_b);
    let mut dec_a: i64 = std_zigzag_decode(std_leb128_decode_u32(leb_a));
    let mut dec_b: i64 = std_zigzag_decode(std_leb128_decode_u32(leb_b));
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    let mut wire_bytes: i64 = (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15));
    let mut lz4_frame: i64 = std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a);
    let mut xxh: i64 = std_xxh32_word64(lz4_frame, (key0 & 4294967295));
    let mut mac: i64 = std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b);
    let mut unpacked_lit: i64 = std_lz4_literal(lz4_frame);
    if ((unpacked_lit != zz_a)) {
        return -2;
    }
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ);
}
