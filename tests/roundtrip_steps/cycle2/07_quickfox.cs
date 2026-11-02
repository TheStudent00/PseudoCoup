long classify_number(long n) {
    long res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

long factorial_iter(long n) {
    long acc = 1;
    long k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

long euclid_step(long a, long b) {
    long q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    long r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    long out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

long bit_mixer(long x, long sh, long mask) {
    long shl_v = (x << (sh & 63));
    long shr_v = (x >> (sh & 63));
    long mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

long quickfox(long a, long b, long sh, long limit) {
    long cls_a = classify_number(a);
    long cls_b = classify_number(b);
    long fact_v = factorial_iter(limit);
    long euc_v = euclid_step(a, b);
    long mix_v = bit_mixer((a + b), sh, 255);
    long total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    long i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
