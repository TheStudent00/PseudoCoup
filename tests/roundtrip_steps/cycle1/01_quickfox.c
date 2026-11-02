int64_t classify_number(int64_t n) {
    int64_t res = 0;
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

int64_t factorial_iter(int64_t n) {
    int64_t acc = 1;
    int64_t k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

int64_t euclid_step(int64_t a, int64_t b) {
    int64_t q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    int64_t r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    int64_t out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

int64_t bit_mixer(int64_t x, int64_t sh, int64_t mask) {
    int64_t shl_v = (x << (sh & 63));
    int64_t shr_v = (x >> (sh & 63));
    int64_t mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

int64_t quickfox(int64_t a, int64_t b, int64_t sh, int64_t limit) {
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
