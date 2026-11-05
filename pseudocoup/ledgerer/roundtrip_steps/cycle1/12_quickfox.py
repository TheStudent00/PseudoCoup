def classify_number(n):
    res = 0
    if (n < 0):
        res = -1
    else:
        if (n == 0):
            res = 0
        else:
            if (n < 10):
                res = 1
            else:
                res = 2
    return res

def factorial_iter(n):
    acc = 1
    k = 2
    while (k <= n):
        acc = (acc * k)
        k = (k + 1)
    return acc

def euclid_step(a, b):
    q = ((int(a / b) - 1) if (((a ^ b) < 0) and ((a - (int(a / b) * b)) != 0)) else int(a / b))
    r = (((a - (int(a / b) * b)) + b) if (((a ^ b) < 0) and ((a - (int(a / b) * b)) != 0)) else (a - (int(a / b) * b)))
    out = 0
    if ((q < 0) and (r != 0)):
        out = (((q * 100) + r) - a)
    else:
        out = ((q * 100) - r)
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
