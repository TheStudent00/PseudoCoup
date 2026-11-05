function classify_number(int $n): int {
    $res = 0;
    if (($n < 0)) {
        $res = -1;
    } else {
        if (($n == 0)) {
            $res = 0;
        } else {
            if (($n < 10)) {
                $res = 1;
            } else {
                $res = 2;
            }
        }
    }
    return $res;
}

function factorial_iter(int $n): int {
    $acc = 1;
    $k = 2;
    while (($k <= $n)) {
        $acc = ($acc * $k);
        $k = ($k + 1);
    }
    return $acc;
}

function euclid_step(int $a, int $b): int {
    $q = (((($a ^ $b) < 0) && (($a % $b) != 0)) ? (($a / $b) - 1) : ($a / $b));
    $r = (((($a ^ $b) < 0) && (($a % $b) != 0)) ? (($a % $b) + $b) : ($a % $b));
    $out = 0;
    if ((($q < 0) && ($r != 0))) {
        $out = ((($q * 100) + $r) - $a);
    } else {
        $out = (($q * 100) - $r);
    }
    return $out;
}

function bit_mixer(int $x, int $sh, int $mask): int {
    $shl_v = ($x << ($sh & 63));
    $shr_v = ($x >> ($sh & 63));
    $mixed = (($shl_v ^ $shr_v) | ($x & $mask));
    return $mixed;
}

function quickfox(int $a, int $b, int $sh, int $limit): int {
    $cls_a = classify_number($a);
    $cls_b = classify_number($b);
    $fact_v = factorial_iter($limit);
    $euc_v = euclid_step($a, $b);
    $mix_v = bit_mixer(($a + $b), $sh, 255);
    $total = ((($fact_v + $euc_v) + ($cls_a * 10)) + $cls_b);
    $i = 0;
    while (($i < $limit)) {
        $total = ($total + ($mix_v ^ $i));
        $i = ($i + 1);
    }
    return $total;
}
