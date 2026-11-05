def std_rotl32_c(x, r)
    return (((x << r) | (x >> (32 - r))) & 4294967295)
end

def std_mul32(a, b)
    lo = ((a * (b & 65535)) & 4294967295)
    hi = (((a * (b >> 16)) << 16) & 4294967295)
    return ((lo + hi) & 4294967295)
end

def std_xxh32_round(acc, input)
    step = ((acc + std_mul32(input, (2246822519 & 4294967295))) & 4294967295)
    rot = std_rotl32_c(step, (13 & 4294967295))
    return std_mul32(rot, (2654435761 & 4294967295))
end

def std_xxh32_avalanche(h)
    h1 = std_mul32((h ^ (h >> 15)), (2246822519 & 4294967295))
    h2 = std_mul32((h1 ^ (h1 >> 13)), (3266489917 & 4294967295))
    return ((h2 ^ (h2 >> 16)) & 4294967295)
end

def std_xxh32_word64(data, seed)
    lo = ((data & 4294967295) & 4294967295)
    hi = (((data >> (32 & 63)) & 4294967295) & 4294967295)
    v1 = std_xxh32_round(((seed + 374761393) + 8), lo)
    v2 = std_xxh32_round(v1, hi)
    return std_xxh32_avalanche(v2)
end

def std_lz4_pack_token(lit_len, match_len, offset, literal_u32)
    lz4_hdr = (((lit_len & 15) << 4) | (match_len & 15))
    off_bits = ((offset & 65535) << 8)
    lit_bits = ((literal_u32 & 4294967295) << 24)
    return ((lz4_hdr | off_bits) | lit_bits)
end

def std_lz4_token_lit_len(frame)
    return (((frame >> (4 & 63)) & 15) & 255)
end

def std_lz4_token_match_len(frame)
    return ((frame & 15) & 255)
end

def std_lz4_match_offset(frame)
    return (((frame >> (8 & 63)) & 65535) & 65535)
end

def std_lz4_literal(frame)
    return (((frame >> (24 & 63)) & 4294967295) & 4294967295)
end

def std_rotl32_rs(x, b)
    return (((x << b) | (x >> (32 - b))) & 4294967295)
end

def std_pack_u32_pair(lo, hi)
    ulo = (lo & 4294967295)
    uhi = ((hi & 4294967295) << 32)
    return (ulo | uhi)
end

def std_pair_lo(p)
    return ((p & 4294967295) & 4294967295)
end

def std_pair_hi(p)
    return (((p >> (32 & 63)) & 4294967295) & 4294967295)
end

def std_sipround_half1(v0, v1, v2, v3)
    a0 = ((v0 + v1) & 4294967295)
    b0 = std_rotl32_rs(a0, (16 & 4294967295))
    a2 = ((v2 + v3) & 4294967295)
    a3 = ((std_rotl32_rs(v3, (8 & 4294967295)) ^ a2) & 4294967295)
    c0 = ((b0 + a3) & 4294967295)
    c3 = ((std_rotl32_rs(a3, (7 & 4294967295)) ^ c0) & 4294967295)
    return std_pack_u32_pair(c0, c3)
end

def std_sipround_half2(v0, v1, v2, v3)
    a0 = ((v0 + v1) & 4294967295)
    a1 = ((std_rotl32_rs(v1, (5 & 4294967295)) ^ a0) & 4294967295)
    a2 = ((v2 + v3) & 4294967295)
    c2 = ((a2 + a1) & 4294967295)
    c1 = ((std_rotl32_rs(a1, (13 & 4294967295)) ^ c2) & 4294967295)
    d2 = std_rotl32_rs(c2, (16 & 4294967295))
    return std_pack_u32_pair(c1, d2)
end

def std_halfsiphash_1_3(k0, k1, m0, m1)
    v0 = k0
    v1 = k1
    v2 = ((k0 ^ 1819895653) & 4294967295)
    v3 = (((k1 ^ 1952801890) ^ m0) & 4294967295)
    p03_a = std_sipround_half1(v0, v1, v2, v3)
    p12_a = std_sipround_half2(v0, v1, v2, v3)
    w0 = ((std_pair_lo(p03_a) ^ m0) & 4294967295)
    w1 = std_pair_lo(p12_a)
    w2 = ((std_pair_hi(p12_a) ^ 255) & 4294967295)
    w3 = ((std_pair_hi(p03_a) ^ m1) & 4294967295)
    p03_b = std_sipround_half1(w0, w1, w2, w3)
    p12_b = std_sipround_half2(w0, w1, w2, w3)
    return ((std_pair_lo(p12_b) ^ std_pair_hi(p03_b)) & 4294967295)
end

def std_zigzag_encode(n)
    return (((n << 1) ^ (n >> 31)) & 4294967295)
end

def std_zigzag_decode(z)
    return (((((z >> 1) ^ (0 - (z & 1))) & 4294967295) ^ 2147483648) - 2147483648)
end

def std_leb128_encode_u32(v)
    b0 = (((v & 127) | ((v >= 128) ? 128 : 0)) & 4294967295)
    v1 = ((v >> 7) & 4294967295)
    b1 = (((v1 & 127) | ((v1 >= 128) ? 128 : 0)) & 4294967295)
    v2 = ((v >> 14) & 4294967295)
    b2 = (((v2 & 127) | ((v2 >= 128) ? 128 : 0)) & 4294967295)
    v3 = (((v >> 21) & 127) & 4294967295)
    nbytes = (((1 + ((v >= 128) ? 1 : 0)) + ((v >= 16384) ? 1 : 0)) + ((v >= 2097152) ? 1 : 0))
    wire = ((((b0 | (b1 << 8)) | (b2 << 16)) | (v3 << 24)) & 4294967295)
    return (wire | (((32 >= 0) && (32 < 64)) ? (nbytes << (32 & 63)) : 0))
end

def std_leb128_decode_u32(packed)
    b0 = (packed & 255)
    b1 = ((((8 >= 0) && (8 < 64)) ? (packed >> (8 & 63)) : (packed >> 63)) & 255)
    b2 = ((((16 >= 0) && (16 < 64)) ? (packed >> (16 & 63)) : (packed >> 63)) & 255)
    b3 = ((((24 >= 0) && (24 < 64)) ? (packed >> (24 & 63)) : (packed >> 63)) & 255)
    acc = (b0 & 127)
    if ((b0 & 128) != 0)
        acc = (acc | (((7 >= 0) && (7 < 64)) ? ((b1 & 127) << (7 & 63)) : 0))
        if ((b1 & 128) != 0)
            acc = (acc | (((14 >= 0) && (14 < 64)) ? ((b2 & 127) << (14 & 63)) : 0))
            if ((b2 & 128) != 0)
                acc = (acc | (((21 >= 0) && (21 < 64)) ? ((b3 & 127) << (21 & 63)) : 0))
            end
        end
    end
    return (acc & 4294967295)
end

def std_ringbuf_push(head, tail, cap_mask, n_items)
    cap_size = ((((cap_mask + 1) & 4294967295) ^ 2147483648) - 2147483648)
    used = (((((tail - head) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    free_slots = (((((cap_size - 1) - used) & 4294967295) ^ 2147483648) - 2147483648)
    accepted = (((((n_items < free_slots) ? n_items : free_slots) & 4294967295) ^ 2147483648) - 2147483648)
    new_tail = (((((tail + accepted) & cap_mask) & 4294967295) ^ 2147483648) - 2147483648)
    new_used = ((((used + accepted) & 4294967295) ^ 2147483648) - 2147483648)
    return std_pack_u32_pair((new_tail & 4294967295), (new_used & 4294967295))
end

def std_circular_tensor_offset(coord_t, coord_ch, dim_t, dim_ch, stride_t, stride_ch)
    wt = ((((coord_t ^ dim_t) < 0) && ((coord_t.remainder(dim_t)) != 0)) ? ((coord_t.remainder(dim_t)) + dim_t) : (coord_t.remainder(dim_t)))
    wch = ((((coord_ch ^ dim_ch) < 0) && ((coord_ch.remainder(dim_ch)) != 0)) ? ((coord_ch.remainder(dim_ch)) + dim_ch) : (coord_ch.remainder(dim_ch)))
    return ((wt * stride_t) + (wch * stride_ch))
end

def std_polyglot_packet_pipeline(delta_a, delta_b, lookback_t, key0, key1)
    tensor_off = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1)
    ring_st = std_ringbuf_push((((3 & 4294967295) ^ 2147483648) - 2147483648), (((11 & 4294967295) ^ 2147483648) - 2147483648), (((31 & 4294967295) ^ 2147483648) - 2147483648), (((4 & 4294967295) ^ 2147483648) - 2147483648))
    ring_occ = std_pair_hi(ring_st)
    zz_a = std_zigzag_encode((((delta_a & 4294967295) ^ 2147483648) - 2147483648))
    zz_b = std_zigzag_encode((((delta_b & 4294967295) ^ 2147483648) - 2147483648))
    leb_a = std_leb128_encode_u32(zz_a)
    leb_b = std_leb128_encode_u32(zz_b)
    dec_a = std_zigzag_decode(std_leb128_decode_u32(leb_a))
    dec_b = std_zigzag_decode(std_leb128_decode_u32(leb_b))
    if ((dec_a != delta_a) || (dec_b != delta_b))
        return -1
    end
    wire_bytes = (((leb_a >> (32 & 63)) & 15) + ((leb_b >> (32 & 63)) & 15))
    lz4_frame = std_lz4_pack_token((wire_bytes & 255), (ring_occ & 255), (tensor_off & 65535), zz_a)
    xxh = std_xxh32_word64(lz4_frame, (key0 & 4294967295))
    mac = std_halfsiphash_1_3((key0 & 4294967295), (key1 & 4294967295), xxh, zz_b)
    unpacked_lit = std_lz4_literal(lz4_frame)
    if (unpacked_lit != zz_a)
        return -2
    end
    return (((((mac * 100003) + xxh) + (tensor_off * 257)) + (wire_bytes * 17)) + ring_occ)
end
