fn xxhash32_avalanche(h: i64, seed: i64) -> i64 {
    let mut acc: i64 = (((h + seed) + 374761393) & 4294967295);
    acc = (((acc ^ (acc >> 15)) * 2246822519) & 4294967295);
    acc = (((acc ^ (acc >> 13)) * 3266489917) & 4294967295);
    return ((acc ^ (acc >> 16)) & 4294967295);
}

fn zigzag_encode_i32(n: i64) -> i64 {
    return (((n << 1) ^ (n >> 31)) & 4294967295);
}

fn zigzag_decode_u32(z: i64) -> i64 {
    return ((((z >> 1) ^ (0 - (z & 1))) << 32) >> 32);
}

fn fx_fold64(acc: i64, word: i64) -> i64 {
    let mut rotated: i64 = (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word);
    return ((rotated * 2654435761) & 2147483647);
}

fn verify_telemetry_frame(delta_a: i64, delta_b: i64, seed: i64) -> i64 {
    let mut zz_a: i64 = zigzag_encode_i32(((delta_a << 32) >> 32));
    let mut zz_b: i64 = zigzag_encode_i32(((delta_b << 32) >> 32));
    let mut h_a: i64 = xxhash32_avalanche(zz_a, (seed & 4294967295));
    let mut h_b: i64 = xxhash32_avalanche(zz_b, h_a);
    let mut digest: i64 = fx_fold64(h_a, h_b);
    let mut dec_a: i64 = zigzag_decode_u32(zz_a);
    let mut dec_b: i64 = zigzag_decode_u32(zz_b);
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    return (digest + (dec_a - dec_b));
}
