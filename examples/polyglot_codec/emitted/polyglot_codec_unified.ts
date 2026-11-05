function xxhash32_avalanche(h: number, seed: number): number {
    let acc: number = BigInt.asIntN(64, BigInt(((h + seed) + 374761393)) & BigInt(0xffffffffn));
    acc = BigInt.asIntN(64, BigInt(((acc ^ (acc >> 15)) * 2246822519)) & BigInt(0xffffffffn));
    acc = BigInt.asIntN(64, BigInt(((acc ^ (acc >> 13)) * 3266489917)) & BigInt(0xffffffffn));
    return BigInt.asIntN(64, BigInt((acc ^ (acc >> 16))) & BigInt(0xffffffffn));
}

function zigzag_encode_i32(n: number): number {
    return BigInt.asIntN(64, BigInt(((n << 1) ^ (n >> 31))) & BigInt(0xffffffffn));
}

function zigzag_decode_u32(z: number): number {
    return BigInt.asIntN(64, BigInt.asIntN(64, BigInt(BigInt.asIntN(64, BigInt(((z >> 1) ^ (0 - (z & 1)))) << (BigInt(32n) & 63n)))) >> (BigInt(32n) & 63n));
}

function fx_fold64(acc: number, word: number): number {
    let rotated: number = (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word);
    return ((rotated * 2654435761) & 2147483647);
}

function verify_telemetry_frame(delta_a: number, delta_b: number, seed: number): number {
    let zz_a: number = zigzag_encode_i32(BigInt.asIntN(64, BigInt.asIntN(64, BigInt(BigInt.asIntN(64, BigInt(delta_a) << (BigInt(32n) & 63n)))) >> (BigInt(32n) & 63n)));
    let zz_b: number = zigzag_encode_i32(BigInt.asIntN(64, BigInt.asIntN(64, BigInt(BigInt.asIntN(64, BigInt(delta_b) << (BigInt(32n) & 63n)))) >> (BigInt(32n) & 63n)));
    let h_a: number = xxhash32_avalanche(zz_a, BigInt.asIntN(64, BigInt(seed) & BigInt(0xffffffffn)));
    let h_b: number = xxhash32_avalanche(zz_b, h_a);
    let digest: number = fx_fold64(h_a, h_b);
    let dec_a: number = zigzag_decode_u32(zz_a);
    let dec_b: number = zigzag_decode_u32(zz_b);
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1;
    }
    return (digest + (dec_a - dec_b));
}
