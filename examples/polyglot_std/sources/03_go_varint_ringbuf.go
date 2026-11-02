// 03_go_varint_ringbuf.go -- Go `encoding/binary` ZigZag + LEB128 `Uvarint` & Ring Buffer (Go)

func std_zigzag_encode(n int32) uint32 {
    return (n << 1) ^ (n >> 31)
}

func std_zigzag_decode(z uint32) int32 {
    return (z >> 1) ^ (0 - (z & 1))
}

func std_leb128_encode_u32(v uint32) int64 {
    b0 := (v & 127) | (func() int64 { if v >= 128 { return 128 } else { return 0 } }())
    v1 := v >> 7
    b1 := (v1 & 127) | (func() int64 { if v1 >= 128 { return 128 } else { return 0 } }())
    v2 := v >> 14
    b2 := (v2 & 127) | (func() int64 { if v2 >= 128 { return 128 } else { return 0 } }())
    v3 := (v >> 21) & 127
    nbytes := 1 + (func() int64 { if v >= 128 { return 1 } else { return 0 } }()) + (func() int64 { if v >= 16384 { return 1 } else { return 0 } }()) + (func() int64 { if v >= 2097152 { return 1 } else { return 0 } }())
    wire := b0 | (b1 << 8) | (b2 << 16) | (v3 << 24)
    return wire | (nbytes << 32)
}

func std_leb128_decode_u32(packed int64) uint32 {
    b0 := packed & 255
    b1 := (packed >> 8) & 255
    b2 := (packed >> 16) & 255
    b3 := (packed >> 24) & 255
    acc := b0 & 127
    if (b0 & 128) != 0 {
        acc = acc | ((b1 & 127) << 7)
        if (b1 & 128) != 0 {
            acc = acc | ((b2 & 127) << 14)
            if (b2 & 128) != 0 {
                acc = acc | ((b3 & 127) << 21)
            }
        }
    }
    return acc
}

func std_ringbuf_push(head int32, tail int32, cap_mask int32, n_items int32) int64 {
    cap_size := cap_mask + 1
    used := (tail - head) & cap_mask
    free_slots := cap_size - 1 - used
    accepted := func() int64 { if n_items < free_slots { return n_items } else { return free_slots } }()
    new_tail := (tail + accepted) & cap_mask
    new_used := used + accepted
    return std_pack_u32_pair(new_tail, new_used)
}
