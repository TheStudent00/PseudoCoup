int classify_number(int n) {
    int res = 0;
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

int factorial_iter(int n) {
    int acc = 1;
    int k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

int euclid_step(int a, int b) {
    int q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    int r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    int out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

int bit_mixer(int x, int sh, int mask) {
    int shl_v = (x << (sh & 63));
    int shr_v = (x >> (sh & 63));
    int mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

int quickfox(int a, int b, int sh, int limit) {
    int cls_a = classify_number(a);
    int cls_b = classify_number(b);
    int fact_v = factorial_iter(limit);
    int euc_v = euclid_step(a, b);
    int mix_v = bit_mixer((a + b), sh, 255);
    int total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    int i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
