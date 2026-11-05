func classify_number(n int64) int64 {
    res := 0
    if ((n < 0)) {
        res = -1
    } else {
        if ((n == 0)) {
            res = 0
        } else {
            if ((n < 10)) {
                res = 1
            } else {
                res = 2
            }
        }
    }
    return res
}

func factorial_iter(n int64) int64 {
    acc := 1
    k := 2
    while ((k <= n)) {
        acc = (acc * k)
        k = (k + 1)
    }
    return acc
}

func euclid_step(a int64, b int64) int64 {
    q := func() int64 { if (((a ^ b) < 0) && ((a % b) != 0)) { return ((a / b) - 1) } else { return (a / b) } }()
    r := func() int64 { if (((a ^ b) < 0) && ((a % b) != 0)) { return ((a % b) + b) } else { return (a % b) } }()
    out := 0
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a)
    } else {
        out = ((q * 100) - r)
    }
    return out
}

func bit_mixer(x int64, sh int64, mask int64) int64 {
    shl_v := (x << (sh & 63))
    shr_v := (x >> (sh & 63))
    mixed := ((shl_v ^ shr_v) | (x & mask))
    return mixed
}

func quickfox(a int64, b int64, sh int64, limit int64) int64 {
    cls_a := classify_number(a)
    cls_b := classify_number(b)
    fact_v := factorial_iter(limit)
    euc_v := euclid_step(a, b)
    mix_v := bit_mixer((a + b), sh, 255)
    total := (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    i := 0
    while ((i < limit)) {
        total = (total + (mix_v ^ i))
        i = (i + 1)
    }
    return total
}
