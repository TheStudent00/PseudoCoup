# 04_py_numpy_telemetry_store.py -- Python `NumPy` Circular Tensor Indexing & Polyglot Packet Pipeline (Python)

def std_circular_tensor_offset(coord_t: int, coord_ch: int, dim_t: int, dim_ch: int, stride_t: int, stride_ch: int) -> int:
    wt = coord_t % dim_t
    wch = coord_ch % dim_ch
    return (wt * stride_t) + (wch * stride_ch)

def std_polyglot_packet_pipeline(delta_a: int, delta_b: int, lookback_t: int, key0: int, key1: int) -> int:
    tensor_off = std_circular_tensor_offset(lookback_t, delta_b, 16, 8, 8, 1)
    ring_st = std_ringbuf_push(3, 11, 31, 4)
    ring_occ = std_pair_hi(ring_st)
    zz_a = std_zigzag_encode(delta_a)
    zz_b = std_zigzag_encode(delta_b)
    leb_a = std_leb128_encode_u32(zz_a)
    leb_b = std_leb128_encode_u32(zz_b)
    dec_a = std_zigzag_decode(std_leb128_decode_u32(leb_a))
    dec_b = std_zigzag_decode(std_leb128_decode_u32(leb_b))
    if dec_a != delta_a or dec_b != delta_b:
        return -1
    wire_bytes = ((leb_a >> 32) & 15) + ((leb_b >> 32) & 15)
    lz4_frame = std_lz4_pack_token(wire_bytes, ring_occ, tensor_off, zz_a)
    xxh = std_xxh32_word64(lz4_frame, key0)
    mac = std_halfsiphash_1_3(key0, key1, xxh, zz_b)
    unpacked_lit = std_lz4_literal(lz4_frame)
    if unpacked_lit != zz_a:
        return -2
    return (mac * 100003) + xxh + (tensor_off * 257) + (wire_bytes * 17) + ring_occ
