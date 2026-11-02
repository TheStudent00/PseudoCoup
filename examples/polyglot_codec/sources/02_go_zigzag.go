// Go: Protobuf-style 32-bit ZigZag signed <-> unsigned varint codec.
// Maps signed int32 (i32) deltas to small unsigned uint32 (u32) integers and back.
func zigzag_encode_i32(n int32) uint32 {
    return ((n << 1) ^ (n >> 31))
}

func zigzag_decode_u32(z uint32) int32 {
    return ((z >> 1) ^ (0 - (z & 1)))
}
