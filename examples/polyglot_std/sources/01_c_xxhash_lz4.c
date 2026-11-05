// 01_c_xxhash_lz4.c -- C `xxHash32` (`XXH32`) & `LZ4` Sequence Token Framing (C)

uint32_t std_rotl32_c(uint32_t x, uint32_t r) {
    return (x << r) | (x >> (32 - r));
}

uint32_t std_mul32(uint32_t a, uint32_t b) {
    uint32_t lo = a * (b & 65535);
    uint32_t hi = (a * (b >> 16)) << 16;
    return lo + hi;
}

uint32_t std_xxh32_round(uint32_t acc, uint32_t input) {
    uint32_t step = acc + std_mul32(input, 2246822519);
    uint32_t rot = std_rotl32_c(step, 13);
    return std_mul32(rot, 2654435761);
}

uint32_t std_xxh32_avalanche(uint32_t h) {
    uint32_t h1 = std_mul32(h ^ (h >> 15), 2246822519);
    uint32_t h2 = std_mul32(h1 ^ (h1 >> 13), 3266489917);
    return h2 ^ (h2 >> 16);
}

uint32_t std_xxh32_word64(int64_t data, uint32_t seed) {
    uint32_t lo = data & 4294967295;
    uint32_t hi = (data >> 32) & 4294967295;
    uint32_t v1 = std_xxh32_round(seed + 374761393 + 8, lo);
    uint32_t v2 = std_xxh32_round(v1, hi);
    return std_xxh32_avalanche(v2);
}

int64_t std_lz4_pack_token(uint8_t lit_len, uint8_t match_len, uint16_t offset, uint32_t literal_u32) {
    int64_t lz4_hdr = ((lit_len & 15) << 4) | (match_len & 15);
    int64_t off_bits = (offset & 65535) << 8;
    int64_t lit_bits = (literal_u32 & 4294967295) << 24;
    return lz4_hdr | off_bits | lit_bits;
}

uint8_t std_lz4_token_lit_len(int64_t frame) {
    return (frame >> 4) & 15;
}

uint8_t std_lz4_token_match_len(int64_t frame) {
    return frame & 15;
}

uint16_t std_lz4_match_offset(int64_t frame) {
    return (frame >> 8) & 65535;
}

uint32_t std_lz4_literal(int64_t frame) {
    return (frame >> 24) & 4294967295;
}
