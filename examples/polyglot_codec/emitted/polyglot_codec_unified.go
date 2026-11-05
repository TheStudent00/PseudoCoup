func xxhash32_avalanche(h int64, seed int64) int64 {
    acc := (((h + seed) + 374761393) & 0xffffffff)
    acc = (((acc ^ (acc >> 15)) * 2246822519) & 0xffffffff)
    acc = (((acc ^ (acc >> 13)) * 3266489917) & 0xffffffff)
    return ((acc ^ (acc >> 16)) & 0xffffffff)
}

func zigzag_encode_i32(n int64) int64 {
    return (((n << 1) ^ (n >> 31)) & 0xffffffff)
}

func zigzag_decode_u32(z int64) int64 {
    return ((((z >> 1) ^ (0 - (z & 1))) << (32 & 63)) >> (32 & 63))
}

func fx_fold64(acc int64, word int64) int64 {
    rotated := (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word)
    return ((rotated * 2654435761) & 2147483647)
}

func verify_telemetry_frame(delta_a int64, delta_b int64, seed int64) int64 {
    zz_a := zigzag_encode_i32(((delta_a << (32 & 63)) >> (32 & 63)))
    zz_b := zigzag_encode_i32(((delta_b << (32 & 63)) >> (32 & 63)))
    h_a := xxhash32_avalanche(zz_a, (seed & 0xffffffff))
    h_b := xxhash32_avalanche(zz_b, h_a)
    digest := fx_fold64(h_a, h_b)
    dec_a := zigzag_decode_u32(zz_a)
    dec_b := zigzag_decode_u32(zz_b)
    if (((dec_a != delta_a) || (dec_b != delta_b))) {
        return -1
    }
    return (digest + (dec_a - dec_b))
}
