int64_t xxhash32_avalanche(int64_t h, int64_t seed) {
    int64_t acc = (((h + seed) + 374761393) & 4294967295);
    acc = (((acc ^ (acc >> (15 & 63))) * 2246822519) & 4294967295);
    acc = (((acc ^ (acc >> (13 & 63))) * 3266489917) & 4294967295);
    return ((acc ^ (acc >> (16 & 63))) & 4294967295);
}

int64_t zigzag_encode_i32(int64_t n) {
    return (((((1 >= 0) && (1 < 64)) ? (n << (1 & 63)) : 0) ^ (((31 >= 0) && (31 < 64)) ? (n >> (31 & 63)) : (n >> (63 & 63)))) & 4294967295);
}

int64_t zigzag_decode_u32(int64_t z) {
    return (((((((1 >= 0) && (1 < 64)) ? (z >> (1 & 63)) : (z >> (63 & 63))) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648);
}

int64_t fx_fold64(int64_t acc, int64_t word) {
    int64_t rotated = (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word);
    return ((rotated * 2654435761) & 2147483647);
}

int64_t verify_telemetry_frame(int64_t delta_a, int64_t delta_b, int64_t seed) {
    int64_t zz_a = zigzag_encode_i32((((delta_a & 4294967295) ^ 2147483648) - 2147483648));
    int64_t zz_b = zigzag_encode_i32((((delta_b & 4294967295) ^ 2147483648) - 2147483648));
    int64_t h_a = xxhash32_avalanche(zz_a, (seed & 4294967295));
    int64_t h_b = xxhash32_avalanche(zz_b, h_a);
    int64_t digest = fx_fold64(h_a, h_b);
    int64_t dec_a = zigzag_decode_u32(zz_a);
    int64_t dec_b = zigzag_decode_u32(zz_b);
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    return (digest + (dec_a - dec_b));
}
