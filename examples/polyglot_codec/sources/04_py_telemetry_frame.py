# Python: Telemetry frame integrity verifier & roundtrip decoder.
# Orchestrates Go's ZigZag (i32 <-> u32), C's xxHash32 (u32), and Rust's fx_fold64 (i64).
def verify_telemetry_frame(delta_a: int, delta_b: int, seed: int) -> int:
    zz_a = zigzag_encode_i32(delta_a)
    zz_b = zigzag_encode_i32(delta_b)
    h_a = xxhash32_avalanche(zz_a, seed)
    h_b = xxhash32_avalanche(zz_b, h_a)
    digest = fx_fold64(h_a, h_b)
    dec_a = zigzag_decode_u32(zz_a)
    dec_b = zigzag_decode_u32(zz_b)
    if dec_a != delta_a or dec_b != delta_b:
        return -1
    return (digest + (dec_a - dec_b))
