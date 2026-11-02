// Rust: 64-bit FxHash/Sip-style word accumulator fold.
// Takes a 64-bit signed accumulator (i64) and a 32-bit unsigned hash word (u32).
fn fx_fold64(acc: i64, word: u32) -> i64 {
    let mut rotated: i64 = (((acc << 5) | ((acc >> 59) & 31)) ^ word);
    return ((rotated * 2654435761) & 2147483647);
}
