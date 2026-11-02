// C (GNU-C): 32-bit unsigned xxHash32 avalanche & lane mixer.
// Relies on native uint32_t (u32) 32-bit modular wraparound and unsigned right shifts.
uint32_t xxhash32_avalanche(uint32_t h, uint32_t seed) {
    uint32_t acc = (h + seed + 374761393);
    acc = ((acc ^ (acc >> 15)) * 2246822519);
    acc = ((acc ^ (acc >> 13)) * 3266489917);
    return (acc ^ (acc >> 16));
}
