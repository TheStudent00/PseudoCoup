fn classify_number(n: i64) -> i64 {
    let mut res: i64 = 0;
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

fn factorial_iter(n: i64) -> i64 {
    let mut acc: i64 = 1;
    let mut k: i64 = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

fn euclid_step(a: i64, b: i64) -> i64 {
    let mut q: i64 = (if (((a ^ b) < 0) && ((a % b) != 0)) { ((a / b) - 1) } else { (a / b) });
    let mut r: i64 = (if (((a ^ b) < 0) && ((a % b) != 0)) { ((a % b) + b) } else { (a % b) });
    let mut out: i64 = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

fn bit_mixer(x: i64, sh: i64, mask: i64) -> i64 {
    let mut shl_v: i64 = (x << (sh & 63));
    let mut shr_v: i64 = (x >> (sh & 63));
    let mut mixed: i64 = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

fn quickfox(a: i64, b: i64, sh: i64, limit: i64) -> i64 {
    let mut cls_a: i64 = classify_number(a);
    let mut cls_b: i64 = classify_number(b);
    let mut fact_v: i64 = factorial_iter(limit);
    let mut euc_v: i64 = euclid_step(a, b);
    let mut mix_v: i64 = bit_mixer((a + b), sh, 255);
    let mut total: i64 = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    let mut i: i64 = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
