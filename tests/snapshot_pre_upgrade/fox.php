<?php
require_once 'builtins_py.php';

function side_effect_marker($tag) {
    print(("SIDE_EFFECT:" + $tag));
    return true;
}
function short_circuit_and_demo() {
    $result = (false && side_effect_marker("AND_RHS"));
    print(("and_short_circuit_result=" + bool_str($result)));
}
function short_circuit_or_demo() {
    $result = (true || side_effect_marker("OR_RHS"));
    print(("or_short_circuit_result=" + bool_str($result)));
}
function bool_str($b) {
    if ($b) {
        return "True";
    } else {
        return "False";
    }
}
function none_str($v) {
    if (($v === $null)) {
        return "None";
    }
    return builtins_py_str($v);
}
function classify_number($n) {
    if (($n < 0)) {
        return "negative";
    } elseif (($n == 0)) {
        return "zero";
    } elseif (($n < 10)) {
        return "small";
    } else {
        return "large";
    }
}
function factorial_recursive($n) {
    if (($n <= 1)) {
        return 1;
    }
    return ($n * factorial_recursive(($n - 1)));
}
class Box {
    public function __construct($value) {
        $this->value = $value;
        $this->history_len = 0;
    }
    public function update_value($new_value) {
        $this->value = $new_value;
        $this->history_len = ($this->history_len + 1);
    }
    public function describe() {
        return (((("Box(value=" + builtins_py_str($this->value)) + ", writes=") + builtins_py_str($this->history_len)) + ")");
    }
}
function risky_divide($a, $b) {
    if (($b == 0)) {
        throw new \Exception(ValueError("division by zero not allowed"));
    }
    return ($a / $b);
}
function main() {
    $a = 17;
    $b = 5;
    $add_i = ($a + $b);
    $sub_i = ($a - $b);
    $mul_i = ($a * $b);
    $div_f = ($a / $b);
    $div_i = intdiv($a, $b);
    $mod_i = ($a % $b);
    $neg_i = -($a);
    print(("add_i=" + builtins_py_str($add_i)));
    print(("sub_i=" + builtins_py_str($sub_i)));
    print(("mul_i=" + builtins_py_str($mul_i)));
    print(("div_f=" + builtins_py_str($div_f)));
    print(("div_i=" + builtins_py_str($div_i)));
    print(("mod_i=" + builtins_py_str($mod_i)));
    print(("neg_i=" + builtins_py_str($neg_i)));
    $fa = 9.0;
    $fb = 2.0;
    print(("float_div=" + builtins_py_str(($fa / $fb))));
    print(("float_floordiv=" + builtins_py_str(intdiv($fa, $fb))));
    print(("eq=" + bool_str(($a == $b))));
    print(("ne=" + bool_str(($a != $b))));
    print(("lt=" + bool_str(($a < $b))));
    print(("le=" + bool_str(($a <= $b))));
    print(("gt=" + bool_str(($a > $b))));
    print(("ge=" + bool_str(($a >= $b))));
    short_circuit_and_demo();
    short_circuit_or_demo();
    print(("not_demo=" + bool_str(!(($a == $b)))));
    foreach ([-(3), 0, 4, 42] as $n) {
        print(((("classify(" + builtins_py_str($n)) + ")=") + classify_number($n)));
    }
    $i = 0;
    $total = 0;
    while (($i < 5)) {
        $total = ($total + $i);
        $i = ($i + 1);
    }
    print(("while_total=" + builtins_py_str($total)));
    $range_sum = 0;
    foreach (builtins_py_range(1, 6) as $k) {
        $range_sum = ($range_sum + $k);
    }
    print(("range_sum=" + builtins_py_str($range_sum)));
    $words = ["quick", "brown", "fox"];
    $joined = "";
    foreach ($words as $w) {
        $joined = (($joined + $w) + "-");
    }
    print(("joined=" + $joined));
    print(("factorial5=" + builtins_py_str(factorial_recursive(5))));
    $counter = 0;
    $counter = ($counter + 1);
    $counter = ($counter + 1);
    print(("counter=" + builtins_py_str($counter)));
    $fox_list = [1, 2, 3];
    $fox_list[0] = 100;
    fox_list->append(4);
    print(("fox_list0=" + builtins_py_str($fox_list[0])));
    print(("fox_list_len=" + builtins_py_str(builtins_py_len($fox_list))));
    print(("fox_list_last=" + builtins_py_str($fox_list[3])));
    $fox_map = builtins_py_hashmap();
    $fox_map["quick"] = 1;
    $fox_map["brown"] = 2;
    $fox_map["fox"] = 3;
    print(("map_get_brown=" + builtins_py_str(fox_map->get("brown"))));
    $fox_map["fox"] = 30;
    print(("map_get_fox=" + builtins_py_str(fox_map->get("fox"))));
    $name = "fox";
    $speed = 12;
    $formatted = "The {} runs at {} mph"->format($name, $speed);
    print($formatted);
    print(("name_len=" + builtins_py_str(builtins_py_len($name))));
    $pair = [$name, $speed];
    $p_name = $pair;
    print(((("pair_name=" + $p_name) + " pair_speed=") + builtins_py_str($p_speed)));
    $box = Box(10);
    print(("box_before=" + box->describe()));
    box->update_value(99);
    print(("box_after=" + box->describe()));
    print(("box_value=" + builtins_py_str($box->value)));
    try {
        risky_divide(10, 0);
    } catch (\Exception $e) {
    }
    $safe_result = risky_divide(10, 4);
    print(("safe_result=" + builtins_py_str($safe_result)));
    $maybe_value = $null;
    print(("maybe_before=" + none_str($maybe_value)));
    $maybe_value = 7;
    print(("maybe_after=" + none_str($maybe_value)));
    print(("contains_fox=" + bool_str(("fox" in $words))));
    print(("contains_wolf=" + bool_str(("wolf" in $words))));
    print(("contains_key=" + bool_str(("quick" in $fox_map))));
    print("DONE");
}
if (($__name__ == "__main__")) {
    main();
}