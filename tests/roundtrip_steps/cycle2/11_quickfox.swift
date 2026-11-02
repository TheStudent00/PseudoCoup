func classify_number(_ n: Int64) -> Int64 {
    var res: Int64 = 0
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

func factorial_iter(_ n: Int64) -> Int64 {
    var acc: Int64 = 1
    var k: Int64 = 2
    while ((k <= n)) {
        acc = (acc * k)
        k = (k + 1)
    }
    return acc
}

func euclid_step(_ a: Int64, _ b: Int64) -> Int64 {
    var q: Int64 = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b))
    var r: Int64 = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b))
    var out: Int64 = 0
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a)
    } else {
        out = ((q * 100) - r)
    }
    return out
}

func bit_mixer(_ x: Int64, _ sh: Int64, _ mask: Int64) -> Int64 {
    var shl_v: Int64 = (x << (sh & 63))
    var shr_v: Int64 = (x >> (sh & 63))
    var mixed: Int64 = ((shl_v ^ shr_v) | (x & mask))
    return mixed
}

func quickfox(_ a: Int64, _ b: Int64, _ sh: Int64, _ limit: Int64) -> Int64 {
    var cls_a: Int64 = classify_number(a)
    var cls_b: Int64 = classify_number(b)
    var fact_v: Int64 = factorial_iter(limit)
    var euc_v: Int64 = euclid_step(a, b)
    var mix_v: Int64 = bit_mixer((a + b), sh, 255)
    var total: Int64 = (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    var i: Int64 = 0
    while ((i < limit)) {
        total = (total + (mix_v ^ i))
        i = (i + 1)
    }
    return total
}
