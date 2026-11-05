function xxhash32_avalanche(h: number, seed: number): number {
    let acc: number = (((h + seed) + 374761393) & 4294967295);
    acc = (((acc ^ (acc >> 15)) * 2246822519) & 4294967295);
    acc = (((acc ^ (acc >> 13)) * 3266489917) & 4294967295);
    return ((acc ^ (acc >> 16)) & 4294967295);
}

function zigzag_encode_i32(n: number): number {
    return (((n << 1) ^ (n >> 31)) & 4294967295);
}

function zigzag_decode_u32(z: number): number {
    return ((((z >> 1) ^ (0 - (z & 1))) << 32) >> 32);
}

function fx_fold64(acc: number, word: number): number {
    let rotated: number = (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word);
    return ((rotated * 2654435761) & 2147483647);
}

function verify_telemetry_frame(delta_a: number, delta_b: number, seed: number): number {
    let zz_a: number = zigzag_encode_i32(((delta_a << 32) >> 32));
    let zz_b: number = zigzag_encode_i32(((delta_b << 32) >> 32));
    let h_a: number = xxhash32_avalanche(zz_a, (seed & 4294967295));
    let h_b: number = xxhash32_avalanche(zz_b, h_a);
    let digest: number = fx_fold64(h_a, h_b);
    let dec_a: number = zigzag_decode_u32(zz_a);
    let dec_b: number = zigzag_decode_u32(zz_b);
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    return (digest + (dec_a - dec_b));
}
