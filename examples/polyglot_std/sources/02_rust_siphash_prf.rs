// 02_rust_siphash_prf.rs -- Rust `siphasher` Keyed Cryptographic PRF (`HalfSipHash-1-3`) (Rust)

fn std_rotl32_rs(x: u32, b: u32) -> u32 {
    return (x << b) | (x >> (32 - b));
}

fn std_pack_u32_pair(lo: u32, hi: u32) -> i64 {
    let ulo: i64 = lo & 4294967295;
    let uhi: i64 = (hi & 4294967295) << 32;
    return ulo | uhi;
}

fn std_pair_lo(p: i64) -> u32 {
    return p & 4294967295;
}

fn std_pair_hi(p: i64) -> u32 {
    return (p >> 32) & 4294967295;
}

fn std_sipround_half1(v0: u32, v1: u32, v2: u32, v3: u32) -> i64 {
    let a0: u32 = v0 + v1;
    let b0: u32 = std_rotl32_rs(a0, 16);
    let a2: u32 = v2 + v3;
    let a3: u32 = std_rotl32_rs(v3, 8) ^ a2;
    let c0: u32 = b0 + a3;
    let c3: u32 = std_rotl32_rs(a3, 7) ^ c0;
    return std_pack_u32_pair(c0, c3);
}

fn std_sipround_half2(v0: u32, v1: u32, v2: u32, v3: u32) -> i64 {
    let a0: u32 = v0 + v1;
    let a1: u32 = std_rotl32_rs(v1, 5) ^ a0;
    let a2: u32 = v2 + v3;
    let c2: u32 = a2 + a1;
    let c1: u32 = std_rotl32_rs(a1, 13) ^ c2;
    let d2: u32 = std_rotl32_rs(c2, 16);
    return std_pack_u32_pair(c1, d2);
}

fn std_halfsiphash_1_3(k0: u32, k1: u32, m0: u32, m1: u32) -> u32 {
    let v0: u32 = k0;
    let v1: u32 = k1;
    let v2: u32 = k0 ^ 1819895653;
    let v3: u32 = (k1 ^ 1952801890) ^ m0;
    let p03_a: i64 = std_sipround_half1(v0, v1, v2, v3);
    let p12_a: i64 = std_sipround_half2(v0, v1, v2, v3);
    let w0: u32 = std_pair_lo(p03_a) ^ m0;
    let w1: u32 = std_pair_lo(p12_a);
    let w2: u32 = std_pair_hi(p12_a) ^ 255;
    let w3: u32 = std_pair_hi(p03_a) ^ m1;
    let p03_b: i64 = std_sipround_half1(w0, w1, w2, w3);
    let p12_b: i64 = std_sipround_half2(w0, w1, w2, w3);
    return std_pair_lo(p12_b) ^ std_pair_hi(p03_b);
}
