def classify_number(n):
    res = 0
    res = (((2 ^ ((1 ^ 2) & (0 - (n < 10)))) ^ ((0 ^ (2 ^ ((1 ^ 2) & (0 - (n < 10))))) & (0 - (n == 0)))) ^ ((-1 ^ ((2 ^ ((1 ^ 2) & (0 - (n < 10)))) ^ ((0 ^ (2 ^ ((1 ^ 2) & (0 - (n < 10))))) & (0 - (n == 0))))) & (0 - (n < 0))))
    return res

def factorial_iter(n):
    acc = 1
    k = 2
    while (k <= n):
        acc = (acc * k)
        k = (k + 1)
    return acc

def euclid_step(a, b):
    q = (int(a / (b + (((a == -9223372036854775808) & (b == -1)) << 1))) - (((a ^ b) < 0) & ((a - (int(a / (b + (((a == -9223372036854775808) & (b == -1)) << 1))) * (b + (((a == -9223372036854775808) & (b == -1)) << 1)))) != 0)))
    r = ((a - (int(a / (b + (((a == -9223372036854775808) & (b == -1)) << 1))) * (b + (((a == -9223372036854775808) & (b == -1)) << 1)))) + (b & (0 - (((a ^ b) < 0) & ((a - (int(a / (b + (((a == -9223372036854775808) & (b == -1)) << 1))) * (b + (((a == -9223372036854775808) & (b == -1)) << 1)))) != 0)))))
    out = 0
    out = (((q * 100) - r) ^ (((((q * 100) + r) - a) ^ ((q * 100) - r)) & (0 - ((q < 0) & (r != 0)))))
    return out

def bit_mixer(x, sh, mask):
    shl_v = (x << (sh & 63))
    shr_v = (x >> (sh & 63))
    mixed = ((shl_v ^ shr_v) | (x & mask))
    return mixed

def quickfox(a, b, sh, limit):
    cls_a = classify_number(a)
    cls_b = classify_number(b)
    fact_v = factorial_iter(limit)
    euc_v = euclid_step(a, b)
    mix_v = bit_mixer((a + b), sh, 255)
    total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    i = 0
    while (i < limit):
        total = (total + (mix_v ^ i))
        i = (i + 1)
    return total
