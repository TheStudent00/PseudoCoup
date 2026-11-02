function classify_number(n: number): number {
    let res: number = 0;
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

function factorial_iter(n: number): number {
    let acc: number = 1;
    let k: number = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

function euclid_step(a: number, b: number): number {
    let q: number = ((((a ^ b) < 0) && ((a % b) != 0)) ? (Math.trunc(a / b) - 1) : Math.trunc(a / b));
    let r: number = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    let out: number = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

function bit_mixer(x: number, sh: number, mask: number): number {
    let shl_v: number = (x << (sh & 63));
    let shr_v: number = (x >> (sh & 63));
    let mixed: number = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

function quickfox(a: number, b: number, sh: number, limit: number): number {
    let cls_a: number = classify_number(a);
    let cls_b: number = classify_number(b);
    let fact_v: number = factorial_iter(limit);
    let euc_v: number = euclid_step(a, b);
    let mix_v: number = bit_mixer((a + b), sh, 255);
    let total: number = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    let i: number = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
