function std_rotl32_c(x: number, r: number): number {
    return (((x << r) | (x >> (32 - r))) & 4294967295);
}

function std_mul32(a: number, b: number): number {
    let lo: number = ((a * (b & 65535)) & 4294967295);
    let hi: number = (((a * (b >> 16)) << 16) & 4294967295);
    return ((lo + hi) & 4294967295);
}

function std_xxh32_round(acc: number, input: number): number {
    let step: number = ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295);
    let rot: number = std_rotl32_c(step, (13 & 4294967295));
    return std_mul32(rot, (2654435761 & 4294967295));
}

function std_xxh32_avalanche(h: number): number {
    let h1: number = std_mul32((h ^ (h >> 15)), (2246822519 & 4294967295));
    let h2: number = std_mul32((h1 ^ (h1 >> 13)), (3266489917 & 4294967295));
    return ((h2 ^ (h2 >> 16)) & 4294967295);
}

function std_xxh32_word64(data: number, seed: number): number {
    let lo: number = ((data & 4294967295) & 4294967295);
    let hi: number = (((data >> (32 & 63)) & 4294967295) & 4294967295);
    let v1: number = std_xxh32_round(((seed + 374761393) + 8), lo);
    let v2: number = std_xxh32_round(v1, hi);
    return std_xxh32_avalanche(v2);
}

function std_lz4_pack_token(lit_len: number, match_len: number, offset: number, literal_u32: number): number {
    let lz4_hdr: number = (((lit_len & 15) << 4) | (match_len & 15));
    let off_bits: number = ((offset & 65535) << 8);
    let lit_bits: number = ((literal_u32 & 4294967295) << 24);
    return ((lz4_hdr | off_bits) | lit_bits);
}

function std_lz4_token_lit_len(frame: number): number {
    return (((frame >> (4 & 63)) & 15) & 255);
}

function std_lz4_token_match_len(frame: number): number {
    return ((frame & 15) & 255);
}

function std_lz4_match_offset(frame: number): number {
    return (((frame >> (8 & 63)) & 65535) & 65535);
}

function std_lz4_literal(frame: number): number {
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295);
}

function std_rotl32_rs(x: number, b: number): number {
    return (((x << b) | (x >> (32 - b))) & 4294967295);
}

function std_pack_u32_pair(lo: number, hi: number): number {
    let ulo: number = (lo & 4294967295);
    let uhi: number = ((hi & 4294967295) << 32);
    return (ulo | uhi);
}

function std_pair_lo(p: number): number {
    return ((p & 4294967295) & 4294967295);
}

function std_pair_hi(p: number): number {
    return (((p >> (32 & 63)) & 4294967295) & 4294967295);
}

function std_sipround_half1(v0: number, v1: number, v2: number, v3: number): number {
    let a0: number = ((v0 + v1) & 4294967295);
    let b0: number = std_rotl32_rs(a0, (16 & 4294967295));
    let a2: number = ((v2 + v3) & 4294967295);
    let a3: number = ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295);
    let c0: number = ((b0 + a3) & 4294967295);
    let c3: number = ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295);
    return std_pack_u32_pair(c0, c3);
}

function std_sipround_half2(v0: number, v1: number, v2: number, v3: number): number {
    let a0: number = ((v0 + v1) & 4294967295);
    let a1: number = ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295);
    let a2: number = ((v2 + v3) & 4294967295);
    let c2: number = ((a2 + a1) & 4294967295);
    let c1: number = ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295);
    let d2: number = std_rotl32_rs(c2, (16 & 4294967295));
    return std_pack_u32_pair(c1, d2);
}

function std_halfsiphash_1_3(k0: number, k1: number, m0: number, m1: number): number {
    let v0: number = k0;
    let v1: number = k1;
    let v2: number = ((k0 ^ 1819895653) & 4294967295);
    let v3: number = (((k1 ^ 1952801890) ^ m0) & 4294967295);
    let p03_a: number = std_sipround_half1(v0, v1, v2, v3);
    let p12_a: number = std_sipround_half2(v0, v1, v2, v3);
    let w0: number = ((std_pair_lo(p03_a) ^ m0) & 4294967295);
    let w1: number = std_pair_lo(p12_a);
    let w2: number = ((std_pair_hi(p12_a) ^ 255) & 4294967295);
    let w3: number = ((std_pair_hi(p03_a) ^ m1) & 4294967295);
    let p03_b: number = std_sipround_half1(w0, w1, w2, w3);
    let p12_b: number = std_sipround_half2(w0, w1, w2, w3);
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295);
}

function std_zigzag_encode(n: number): number {
    return (((n << 1) ^ (n >> 31)) & 4294967295);
}

function std_zigzag_decode(z: number): number {
    return (((((z >> 1) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648);
}

function std_leb128_encode_u32(v: number): number {
    let b0: number = (((v & 127) | ((v >= 128) ? 128 : 0)) & 4294967295);
    let v1: number = ((v >> 7) & 4294967295);
    let b1: number = (((v1 & 127) | ((v1 >= 128) ? 128 : 0)) & 4294967295);
    let v2: number = ((v >> 14) & 4294967295);
    let b2: number = (((v2 & 127) | ((v2 >= 128) ? 128 : 0)) & 4294967295);
    let v3: number = (((v >> 21) & 127) & 4294967295);
    let nbytes: number = (((1 + ((v >= 128) ? 1 : 0)) + ((v >= 16384) ? 1 : 0)) + ((v >= 2097152) ? 1 : 0));
    let wire: number = ((((b0 | (b1 << 8)) | (b2 << 16)) | (v3 << 24)) & 4294967295);
    return (wire | (((32 >= 0) && (32 < 64)) ? (nbytes << (32 & 63)) : 0));
}

function std_leb128_decode_u32(packed: number): number {
    let b0: number = (packed & 255);
    let b1: number = ((((8 >= 0) && (8 < 64)) ? (packed >> (8 & 63)) : (packed >> 63)) & 255);
    let b2: number = ((((16 >= 0) && (16 < 64)) ? (packed >> (16 & 63)) : (packed >> 63)) & 255);
    let b3: number = ((((24 >= 0) && (24 < 64)) ? (packed >> (24 & 63)) : (packed >> 63)) & 255);
    let acc: number = (b0 & 127);
    if (((b0 & 128) != 0)) {
        acc = (acc | (((7 >= 0) && (7 < 64)) ? ((b1 & 127) << (7 & 63)) : 0));
        if (((b1 & 128) != 0)) {
            acc = (acc | (((14 >= 0) && (14 < 64)) ? ((b2 & 127) << (14 & 63)) : 0));
            if (((b2 & 128) != 0)) {
                acc = (acc | (((21 >= 0) && (21 < 64)) ? ((b3 & 127) << (21 & 63)) : 0));
            }
        }
    }
    return (acc & 4294967295);
}

function std_ringbuf_push(head: number, tail: number, cap_mask: number, n_items: number): number {
    let cap_size: number = ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648);
    let used: number = (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    let free_slots: number = (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648);
    let accepted: number = (((((n_items < free_slots) ? n_items : free_slots) & 4294967295) ^ 2147483648) - 2147483648);
    let new_tail: number = (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    let new_used: number = ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648);
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295));
}

function std_circular_tensor_offset(coord_t: number, coord_ch: number, dim_t: number, dim_ch: number, stride_t: number, stride_ch: number): number {
    let wt: number = ((((coord_t ^ dim_t) < 0) && ((coord_t % dim_t) != 0)) ? ((coord_t % dim_t) + dim_t) : (coord_t % dim_t));
    let wch: number = ((((coord_ch ^ dim_ch) < 0) && ((coord_ch % dim_ch) != 0)) ? ((coord_ch % dim_ch) + dim_ch) : (coord_ch % dim_ch));
    return ((wt * stride_t) + (wch * stride_ch));
}

function std_polyglot_packet_pipeline(delta_a: number, delta_b: number, lookback_t: number, key0: number, key1: number): number {
    let tensor_off: number = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1);
    let ring_st: number = std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648));
    let ring_occ: number = std_pair_hi(ring_st);
    let zz_a: number = std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648));
    let zz_b: number = std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648));
    let leb_a: number = std_leb128_encode_u32(zz_a);
    let leb_b: number = std_leb128_encode_u32(zz_b);
    let dec_a: number = std_zigzag_decode(std_leb128_decode_u32(leb_a));
    let dec_b: number = std_zigzag_decode(std_leb128_decode_u32(leb_b));
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    let wire_bytes: number = (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15));
    let lz4_frame: number = std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a);
    let xxh: number = std_xxh32_word64(lz4_frame, (key0 & 4294967295));
    let mac: number = std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b);
    let unpacked_lit: number = std_lz4_literal(lz4_frame);
    if ((unpacked_lit != zz_a)) {
        return -2;
    }
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ);
}
