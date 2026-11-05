def xxhash32_avalanche(h, seed):
    acc = (((h + seed) + 374761393) & 4294967295)
    acc = (((acc ^ (acc >> 15)) * 2246822519) & 4294967295)
    acc = (((acc ^ (acc >> 13)) * 3266489917) & 4294967295)
    return ((acc ^ (acc >> 16)) & 4294967295)

def zigzag_encode_i32(n):
    return (((n << 1) ^ (n >> 31)) & 4294967295)

def zigzag_decode_u32(z):
    return ((((z >> 1) ^ (0 - (z & 1))) << 32) >> 32)

def fx_fold64(acc, word):
    rotated = (((acc << (5 & 63)) | ((acc >> (59 & 63)) & 31)) ^ word)
    return ((rotated * 2654435761) & 2147483647)

def verify_telemetry_frame(delta_a, delta_b, seed):
    zz_a = zigzag_encode_i32(((delta_a << 32) >> 32))
    zz_b = zigzag_encode_i32(((delta_b << 32) >> 32))
    h_a = xxhash32_avalanche(zz_a, (seed & 4294967295))
    h_b = xxhash32_avalanche(zz_b, h_a)
    digest = fx_fold64(h_a, h_b)
    dec_a = zigzag_decode_u32(zz_a)
    dec_b = zigzag_decode_u32(zz_b)
    if ((dec_a != delta_a) or (dec_b != delta_b)):
        return -1
    return (digest + (dec_a - dec_b))
