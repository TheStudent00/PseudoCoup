#include <stdint.h>

__device__ __forceinline__ int64_t classify_number(int64_t n) {
    int64_t res = 0;
    res = (((2 ^ ((1 ^ 2) & (0 - (n < 10)))) ^ ((0 ^ (2 ^ ((1 ^ 2) & (0 - (n < 10))))) & (0 - (n == 0)))) ^ ((-1 ^ ((2 ^ ((1 ^ 2) & (0 - (n < 10)))) ^ ((0 ^ (2 ^ ((1 ^ 2) & (0 - (n < 10))))) & (0 - (n == 0))))) & (0 - (n < 0))));
    return res;
}

__device__ __forceinline__ int64_t factorial_iter(int64_t n) {
    int64_t acc = 1;
    int64_t k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

__device__ __forceinline__ int64_t euclid_step(int64_t a, int64_t b) {
    int64_t q = ((a / (b + (((a == -9223372036854775808) & (b == -1)) << 1))) - (((a ^ b) < 0) & ((a % (b + (((a == -9223372036854775808) & (b == -1)) << 1))) != 0)));
    int64_t r = ((a % (b + (((a == -9223372036854775808) & (b == -1)) << 1))) + (b & (0 - (((a ^ b) < 0) & ((a % (b + (((a == -9223372036854775808) & (b == -1)) << 1))) != 0)))));
    int64_t out = 0;
    out = (((q * 100) - r) ^ (((((q * 100) + r) - a) ^ ((q * 100) - r)) & (0 - ((q < 0) & (r != 0)))));
    return out;
}

__device__ __forceinline__ int64_t bit_mixer(int64_t x, int64_t sh, int64_t mask) {
    int64_t shl_v = (x << (sh & 63));
    int64_t shr_v = (x >> (sh & 63));
    int64_t mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

__device__ __forceinline__ int64_t quickfox(int64_t a, int64_t b, int64_t sh, int64_t limit) {
    int64_t cls_a = classify_number(a);
    int64_t cls_b = classify_number(b);
    int64_t fact_v = factorial_iter(limit);
    int64_t euc_v = euclid_step(a, b);
    int64_t mix_v = bit_mixer((a + b), sh, 255);
    int64_t total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    int64_t i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}

extern "C" __global__ void quickfox_warp_kernel(
    const int64_t* __restrict__ in_a, const int64_t* __restrict__ in_b, const int64_t* __restrict__ in_sh, const int64_t* __restrict__ in_limit,
    int64_t* __restrict__ out_res,
    int32_t n_elements
) {
    int32_t tid = (int32_t)(blockIdx.x * blockDim.x + threadIdx.x);
    if (tid < n_elements) {
        out_res[tid] = quickfox(in_a[tid], in_b[tid], in_sh[tid], in_limit[tid]);
    }
}
