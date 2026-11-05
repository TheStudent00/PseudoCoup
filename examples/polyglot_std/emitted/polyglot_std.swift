func std_rotl32_c(_ x: Int64, _ r: Int64) -> Int64 {
    return (((x << r) | (x >> (32 - r))) & 4294967295)
}

func std_mul32(_ a: Int64, _ b: Int64) -> Int64 {
    var lo: Int64 = ((a * (b & 65535)) & 4294967295)
    var hi: Int64 = (((a * (b >> 16)) << 16) & 4294967295)
    return ((lo + hi) & 4294967295)
}

func std_xxh32_round(_ acc: Int64, _ input: Int64) -> Int64 {
    var step: Int64 = ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295)
    var rot: Int64 = std_rotl32_c(step, (13 & 4294967295))
    return std_mul32(rot, (2654435761 & 4294967295))
}

func std_xxh32_avalanche(_ h: Int64) -> Int64 {
    var h1: Int64 = std_mul32((h ^ (h >> 15)), (2246822519 & 4294967295))
    var h2: Int64 = std_mul32((h1 ^ (h1 >> 13)), (3266489917 & 4294967295))
    return ((h2 ^ (h2 >> 16)) & 4294967295)
}

func std_xxh32_word64(_ data: Int64, _ seed: Int64) -> Int64 {
    var lo: Int64 = ((data & 4294967295) & 4294967295)
    var hi: Int64 = (((data >> (32 & 63)) & 4294967295) & 4294967295)
    var v1: Int64 = std_xxh32_round(((seed + 374761393) + 8), lo)
    var v2: Int64 = std_xxh32_round(v1, hi)
    return std_xxh32_avalanche(v2)
}

func std_lz4_pack_token(_ lit_len: Int64, _ match_len: Int64, _ offset: Int64, _ literal_u32: Int64) -> Int64 {
    var lz4_hdr: Int64 = (((lit_len & 15) << 4) | (match_len & 15))
    var off_bits: Int64 = ((offset & 65535) << 8)
    var lit_bits: Int64 = ((literal_u32 & 4294967295) << 24)
    return ((lz4_hdr | off_bits) | lit_bits)
}

func std_lz4_token_lit_len(_ frame: Int64) -> Int64 {
    return (((frame >> (4 & 63)) & 15) & 255)
}

func std_lz4_token_match_len(_ frame: Int64) -> Int64 {
    return ((frame & 15) & 255)
}

func std_lz4_match_offset(_ frame: Int64) -> Int64 {
    return (((frame >> (8 & 63)) & 65535) & 65535)
}

func std_lz4_literal(_ frame: Int64) -> Int64 {
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295)
}

func std_rotl32_rs(_ x: Int64, _ b: Int64) -> Int64 {
    return (((x << b) | (x >> (32 - b))) & 4294967295)
}

func std_pack_u32_pair(_ lo: Int64, _ hi: Int64) -> Int64 {
    var ulo: Int64 = (lo & 4294967295)
    var uhi: Int64 = ((hi & 4294967295) << 32)
    return (ulo | uhi)
}

func std_pair_lo(_ p: Int64) -> Int64 {
    return ((p & 4294967295) & 4294967295)
}

func std_pair_hi(_ p: Int64) -> Int64 {
    return (((p >> (32 & 63)) & 4294967295) & 4294967295)
}

func std_sipround_half1(_ v0: Int64, _ v1: Int64, _ v2: Int64, _ v3: Int64) -> Int64 {
    var a0: Int64 = ((v0 + v1) & 4294967295)
    var b0: Int64 = std_rotl32_rs(a0, (16 & 4294967295))
    var a2: Int64 = ((v2 + v3) & 4294967295)
    var a3: Int64 = ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295)
    var c0: Int64 = ((b0 + a3) & 4294967295)
    var c3: Int64 = ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295)
    return std_pack_u32_pair(c0, c3)
}

func std_sipround_half2(_ v0: Int64, _ v1: Int64, _ v2: Int64, _ v3: Int64) -> Int64 {
    var a0: Int64 = ((v0 + v1) & 4294967295)
    var a1: Int64 = ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295)
    var a2: Int64 = ((v2 + v3) & 4294967295)
    var c2: Int64 = ((a2 + a1) & 4294967295)
    var c1: Int64 = ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295)
    var d2: Int64 = std_rotl32_rs(c2, (16 & 4294967295))
    return std_pack_u32_pair(c1, d2)
}

func std_halfsiphash_1_3(_ k0: Int64, _ k1: Int64, _ m0: Int64, _ m1: Int64) -> Int64 {
    var v0: Int64 = k0
    var v1: Int64 = k1
    var v2: Int64 = ((k0 ^ 1819895653) & 4294967295)
    var v3: Int64 = (((k1 ^ 1952801890) ^ m0) & 4294967295)
    var p03_a: Int64 = std_sipround_half1(v0, v1, v2, v3)
    var p12_a: Int64 = std_sipround_half2(v0, v1, v2, v3)
    var w0: Int64 = ((std_pair_lo(p03_a) ^ m0) & 4294967295)
    var w1: Int64 = std_pair_lo(p12_a)
    var w2: Int64 = ((std_pair_hi(p12_a) ^ 255) & 4294967295)
    var w3: Int64 = ((std_pair_hi(p03_a) ^ m1) & 4294967295)
    var p03_b: Int64 = std_sipround_half1(w0, w1, w2, w3)
    var p12_b: Int64 = std_sipround_half2(w0, w1, w2, w3)
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295)
}

func std_zigzag_encode(_ n: Int64) -> Int64 {
    return (((n << 1) ^ (n >> 31)) & 4294967295)
}

func std_zigzag_decode(_ z: Int64) -> Int64 {
    return (((((z >> 1) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648)
}

func std_leb128_encode_u32(_ v: Int64) -> Int64 {
    var b0: Int64 = (((v & 127) | ((v >= 128) ? 128 : 0)) & 4294967295)
    var v1: Int64 = ((v >> 7) & 4294967295)
    var b1: Int64 = (((v1 & 127) | ((v1 >= 128) ? 128 : 0)) & 4294967295)
    var v2: Int64 = ((v >> 14) & 4294967295)
    var b2: Int64 = (((v2 & 127) | ((v2 >= 128) ? 128 : 0)) & 4294967295)
    var v3: Int64 = (((v >> 21) & 127) & 4294967295)
    var nbytes: Int64 = (((1 + ((v >= 128) ? 1 : 0)) + ((v >= 16384) ? 1 : 0)) + ((v >= 2097152) ? 1 : 0))
    var wire: Int64 = ((((b0 | (b1 << 8)) | (b2 << 16)) | (v3 << 24)) & 4294967295)
    return (wire | (((32 >= 0) && (32 < 64)) ? (nbytes << (32 & 63)) : 0))
}

func std_leb128_decode_u32(_ packed: Int64) -> Int64 {
    var b0: Int64 = (packed & 255)
    var b1: Int64 = ((((8 >= 0) && (8 < 64)) ? (packed >> (8 & 63)) : (packed >> 63)) & 255)
    var b2: Int64 = ((((16 >= 0) && (16 < 64)) ? (packed >> (16 & 63)) : (packed >> 63)) & 255)
    var b3: Int64 = ((((24 >= 0) && (24 < 64)) ? (packed >> (24 & 63)) : (packed >> 63)) & 255)
    var acc: Int64 = (b0 & 127)
    if (((b0 & 128) != 0)) {
        acc = (acc | (((7 >= 0) && (7 < 64)) ? ((b1 & 127) << (7 & 63)) : 0))
        if (((b1 & 128) != 0)) {
            acc = (acc | (((14 >= 0) && (14 < 64)) ? ((b2 & 127) << (14 & 63)) : 0))
            if (((b2 & 128) != 0)) {
                acc = (acc | (((21 >= 0) && (21 < 64)) ? ((b3 & 127) << (21 & 63)) : 0))
            }
        }
    }
    return (acc & 4294967295)
}

func std_ringbuf_push(_ head: Int64, _ tail: Int64, _ cap_mask: Int64, _ n_items: Int64) -> Int64 {
    var cap_size: Int64 = ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648)
    var used: Int64 = (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    var free_slots: Int64 = (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648)
    var accepted: Int64 = (((((n_items < free_slots) ? n_items : free_slots) & 4294967295) ^ 2147483648) - 2147483648)
    var new_tail: Int64 = (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    var new_used: Int64 = ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648)
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295))
}

func std_circular_tensor_offset(_ coord_t: Int64, _ coord_ch: Int64, _ dim_t: Int64, _ dim_ch: Int64, _ stride_t: Int64, _ stride_ch: Int64) -> Int64 {
    var wt: Int64 = ((((coord_t ^ dim_t) < 0) && ((coord_t % dim_t) != 0)) ? ((coord_t % dim_t) + dim_t) : (coord_t % dim_t))
    var wch: Int64 = ((((coord_ch ^ dim_ch) < 0) && ((coord_ch % dim_ch) != 0)) ? ((coord_ch % dim_ch) + dim_ch) : (coord_ch % dim_ch))
    return ((wt * stride_t) + (wch * stride_ch))
}

func std_polyglot_packet_pipeline(_ delta_a: Int64, _ delta_b: Int64, _ lookback_t: Int64, _ key0: Int64, _ key1: Int64) -> Int64 {
    var tensor_off: Int64 = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1)
    var ring_st: Int64 = std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648))
    var ring_occ: Int64 = std_pair_hi(ring_st)
    var zz_a: Int64 = std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648))
    var zz_b: Int64 = std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648))
    var leb_a: Int64 = std_leb128_encode_u32(zz_a)
    var leb_b: Int64 = std_leb128_encode_u32(zz_b)
    var dec_a: Int64 = std_zigzag_decode(std_leb128_decode_u32(leb_a))
    var dec_b: Int64 = std_zigzag_decode(std_leb128_decode_u32(leb_b))
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1
    }
    var wire_bytes: Int64 = (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15))
    var lz4_frame: Int64 = std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a)
    var xxh: Int64 = std_xxh32_word64(lz4_frame, (key0 & 4294967295))
    var mac: Int64 = std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b)
    var unpacked_lit: Int64 = std_lz4_literal(lz4_frame)
    if ((unpacked_lit != zz_a)) {
        return -2
    }
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ)
}
