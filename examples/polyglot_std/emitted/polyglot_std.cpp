int64_t std_rotl32_c(int64_t x, int64_t r) {
    return (((x << r) | (x >> (32 - r))) & 4294967295);
}

int64_t std_mul32(int64_t a, int64_t b) {
    int64_t lo = ((a * (b & 65535)) & 4294967295);
    int64_t hi = (((a * (b >> 16)) << 16) & 4294967295);
    return ((lo + hi) & 4294967295);
}

int64_t std_xxh32_round(int64_t acc, int64_t input) {
    int64_t step = ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295);
    int64_t rot = std_rotl32_c(step, (13 & 4294967295));
    return std_mul32(rot, (2654435761 & 4294967295));
}

int64_t std_xxh32_avalanche(int64_t h) {
    int64_t h1 = std_mul32((h ^ (h >> 15)), (2246822519 & 4294967295));
    int64_t h2 = std_mul32((h1 ^ (h1 >> 13)), (3266489917 & 4294967295));
    return ((h2 ^ (h2 >> 16)) & 4294967295);
}

int64_t std_xxh32_word64(int64_t data, int64_t seed) {
    int64_t lo = ((data & 4294967295) & 4294967295);
    int64_t hi = (((data >> (32 & 63)) & 4294967295) & 4294967295);
    int64_t v1 = std_xxh32_round(((seed + 374761393) + 8), lo);
    int64_t v2 = std_xxh32_round(v1, hi);
    return std_xxh32_avalanche(v2);
}

int64_t std_lz4_pack_token(int64_t lit_len, int64_t match_len, int64_t offset, int64_t literal_u32) {
    int64_t lz4_hdr = (((lit_len & 15) << 4) | (match_len & 15));
    int64_t off_bits = ((offset & 65535) << 8);
    int64_t lit_bits = ((literal_u32 & 4294967295) << 24);
    return ((lz4_hdr | off_bits) | lit_bits);
}

int64_t std_lz4_token_lit_len(int64_t frame) {
    return (((frame >> (4 & 63)) & 15) & 255);
}

int64_t std_lz4_token_match_len(int64_t frame) {
    return ((frame & 15) & 255);
}

int64_t std_lz4_match_offset(int64_t frame) {
    return (((frame >> (8 & 63)) & 65535) & 65535);
}

int64_t std_lz4_literal(int64_t frame) {
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295);
}

int64_t std_rotl32_rs(int64_t x, int64_t b) {
    return (((x << b) | (x >> (32 - b))) & 4294967295);
}

int64_t std_pack_u32_pair(int64_t lo, int64_t hi) {
    int64_t ulo = (lo & 4294967295);
    int64_t uhi = ((hi & 4294967295) << 32);
    return (ulo | uhi);
}

int64_t std_pair_lo(int64_t p) {
    return ((p & 4294967295) & 4294967295);
}

int64_t std_pair_hi(int64_t p) {
    return (((p >> (32 & 63)) & 4294967295) & 4294967295);
}

int64_t std_sipround_half1(int64_t v0, int64_t v1, int64_t v2, int64_t v3) {
    int64_t a0 = ((v0 + v1) & 4294967295);
    int64_t b0 = std_rotl32_rs(a0, (16 & 4294967295));
    int64_t a2 = ((v2 + v3) & 4294967295);
    int64_t a3 = ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295);
    int64_t c0 = ((b0 + a3) & 4294967295);
    int64_t c3 = ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295);
    return std_pack_u32_pair(c0, c3);
}

int64_t std_sipround_half2(int64_t v0, int64_t v1, int64_t v2, int64_t v3) {
    int64_t a0 = ((v0 + v1) & 4294967295);
    int64_t a1 = ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295);
    int64_t a2 = ((v2 + v3) & 4294967295);
    int64_t c2 = ((a2 + a1) & 4294967295);
    int64_t c1 = ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295);
    int64_t d2 = std_rotl32_rs(c2, (16 & 4294967295));
    return std_pack_u32_pair(c1, d2);
}

int64_t std_halfsiphash_1_3(int64_t k0, int64_t k1, int64_t m0, int64_t m1) {
    int64_t v0 = k0;
    int64_t v1 = k1;
    int64_t v2 = ((k0 ^ 1819895653) & 4294967295);
    int64_t v3 = (((k1 ^ 1952801890) ^ m0) & 4294967295);
    int64_t p03_a = std_sipround_half1(v0, v1, v2, v3);
    int64_t p12_a = std_sipround_half2(v0, v1, v2, v3);
    int64_t w0 = ((std_pair_lo(p03_a) ^ m0) & 4294967295);
    int64_t w1 = std_pair_lo(p12_a);
    int64_t w2 = ((std_pair_hi(p12_a) ^ 255) & 4294967295);
    int64_t w3 = ((std_pair_hi(p03_a) ^ m1) & 4294967295);
    int64_t p03_b = std_sipround_half1(w0, w1, w2, w3);
    int64_t p12_b = std_sipround_half2(w0, w1, w2, w3);
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295);
}

int64_t std_zigzag_encode(int64_t n) {
    return (((n << 1) ^ (n >> 31)) & 4294967295);
}

int64_t std_zigzag_decode(int64_t z) {
    return (((((z >> 1) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648);
}

int64_t std_leb128_encode_u32(int64_t v) {
    int64_t b0 = (((v & 127) | ((v >= 128) ? 128 : 0)) & 4294967295);
    int64_t v1 = ((v >> 7) & 4294967295);
    int64_t b1 = (((v1 & 127) | ((v1 >= 128) ? 128 : 0)) & 4294967295);
    int64_t v2 = ((v >> 14) & 4294967295);
    int64_t b2 = (((v2 & 127) | ((v2 >= 128) ? 128 : 0)) & 4294967295);
    int64_t v3 = (((v >> 21) & 127) & 4294967295);
    int64_t nbytes = (((1 + ((v >= 128) ? 1 : 0)) + ((v >= 16384) ? 1 : 0)) + ((v >= 2097152) ? 1 : 0));
    int64_t wire = ((((b0 | (b1 << 8)) | (b2 << 16)) | (v3 << 24)) & 4294967295);
    return (wire | (((32 >= 0) && (32 < 64)) ? (nbytes << (32 & 63)) : 0));
}

int64_t std_leb128_decode_u32(int64_t packed) {
    int64_t b0 = (packed & 255);
    int64_t b1 = ((((8 >= 0) && (8 < 64)) ? (packed >> (8 & 63)) : (packed >> 63)) & 255);
    int64_t b2 = ((((16 >= 0) && (16 < 64)) ? (packed >> (16 & 63)) : (packed >> 63)) & 255);
    int64_t b3 = ((((24 >= 0) && (24 < 64)) ? (packed >> (24 & 63)) : (packed >> 63)) & 255);
    int64_t acc = (b0 & 127);
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

int64_t std_ringbuf_push(int64_t head, int64_t tail, int64_t cap_mask, int64_t n_items) {
    int64_t cap_size = ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t used = (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t free_slots = (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t accepted = (((((n_items < free_slots) ? n_items : free_slots) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t new_tail = (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648);
    int64_t new_used = ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648);
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295));
}

int64_t std_circular_tensor_offset(int64_t coord_t, int64_t coord_ch, int64_t dim_t, int64_t dim_ch, int64_t stride_t, int64_t stride_ch) {
    int64_t wt = ((((coord_t ^ dim_t) < 0) && ((coord_t % dim_t) != 0)) ? ((coord_t % dim_t) + dim_t) : (coord_t % dim_t));
    int64_t wch = ((((coord_ch ^ dim_ch) < 0) && ((coord_ch % dim_ch) != 0)) ? ((coord_ch % dim_ch) + dim_ch) : (coord_ch % dim_ch));
    return ((wt * stride_t) + (wch * stride_ch));
}

int64_t std_polyglot_packet_pipeline(int64_t delta_a, int64_t delta_b, int64_t lookback_t, int64_t key0, int64_t key1) {
    int64_t tensor_off = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1);
    int64_t ring_st = std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648));
    int64_t ring_occ = std_pair_hi(ring_st);
    int64_t zz_a = std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648));
    int64_t zz_b = std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648));
    int64_t leb_a = std_leb128_encode_u32(zz_a);
    int64_t leb_b = std_leb128_encode_u32(zz_b);
    int64_t dec_a = std_zigzag_decode(std_leb128_decode_u32(leb_a));
    int64_t dec_b = std_zigzag_decode(std_leb128_decode_u32(leb_b));
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    int64_t wire_bytes = (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15));
    int64_t lz4_frame = std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a);
    int64_t xxh = std_xxh32_word64(lz4_frame, (key0 & 4294967295));
    int64_t mac = std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b);
    int64_t unpacked_lit = std_lz4_literal(lz4_frame);
    if ((unpacked_lit != zz_a)) {
        return -2;
    }
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ);
}
