fn side_effect_marker(tag: Any) -> () {
    println!(("SIDE_EFFECT:" + tag));
    return true;
}
fn short_circuit_and_demo() -> () {
    let mut result: Any = (false && side_effect_marker("AND_RHS"));
    println!(("and_short_circuit_result=" + bool_str(result)));
}
fn short_circuit_or_demo() -> () {
    let mut result: Any = (true || side_effect_marker("OR_RHS"));
    println!(("or_short_circuit_result=" + bool_str(result)));
}
fn bool_str(b: Any) -> () {
    if b {
        return "True";
    } else {
        return "False";
    }
}
fn none_str(v: Any) -> () {
    if (v == null) {
        return "None";
    }
    return builtins_py::str(v);
}
fn classify_number(n: Any) -> () {
    if (n < 0) {
        return "negative";
    } else if (n == 0) {
        return "zero";
    } else if (n < 10) {
        return "small";
    } else {
        return "large";
    }
}
fn factorial_recursive(n: Any) -> () {
    if (n <= 1) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
struct Box {
}

impl Box {
    fn new(value: Any) -> Self {
        Self { value: value, history_len: 0 }
    }
    fn update_value(&mut self, new_value: Any) -> Any {
        self.value = new_value;
        self.history_len = (self.history_len + 1);
    }
    fn describe(&mut self) -> Any {
        return (((("Box(value=" + builtins_py::str(self.value)) + ", writes=") + builtins_py::str(self.history_len)) + ")");
    }
}
fn risky_divide(a: Any, b: Any) -> () {
    if (b == 0) {
        panic!(ValueError::new("division by zero not allowed"));
    }
    return (a / b);
}
fn main() -> () {
    let mut a: Any = 17;
    let mut b: Any = 5;
    let mut add_i: Any = (a + b);
    let mut sub_i: Any = (a - b);
    let mut mul_i: Any = (a * b);
    let mut div_f: Any = (a / b);
    let mut div_i: Any = (a / b);
    let mut mod_i: Any = (a % b);
    let mut neg_i: Any = -(a);
    println!(("add_i=" + builtins_py::str(add_i)));
    println!(("sub_i=" + builtins_py::str(sub_i)));
    println!(("mul_i=" + builtins_py::str(mul_i)));
    println!(("div_f=" + builtins_py::str(div_f)));
    println!(("div_i=" + builtins_py::str(div_i)));
    println!(("mod_i=" + builtins_py::str(mod_i)));
    println!(("neg_i=" + builtins_py::str(neg_i)));
    let mut fa: Any = 9.0;
    let mut fb: Any = 2.0;
    println!(("float_div=" + builtins_py::str((fa / fb))));
    println!(("float_floordiv=" + builtins_py::str((fa / fb))));
    println!(("eq=" + bool_str((a == b))));
    println!(("ne=" + bool_str((a != b))));
    println!(("lt=" + bool_str((a < b))));
    println!(("le=" + bool_str((a <= b))));
    println!(("gt=" + bool_str((a > b))));
    println!(("ge=" + bool_str((a >= b))));
    short_circuit_and_demo();
    short_circuit_or_demo();
    println!(("not_demo=" + bool_str(!((a == b)))));
    for n in vec![-(3), 0, 4, 42] {
        println!(((("classify(" + builtins_py::str(n)) + ")=") + classify_number(n)));
    }
    let mut i: Any = 0;
    let mut total: Any = 0;
    while (i < 5) {
        total = (total + i);
        i = (i + 1);
    }
    println!(("while_total=" + builtins_py::str(total)));
    let mut range_sum: Any = 0;
    for k in builtins_py::range(1, 6) {
        range_sum = (range_sum + k);
    }
    println!(("range_sum=" + builtins_py::str(range_sum)));
    let mut words: Any = vec!["quick", "brown", "fox"];
    let mut joined: Any = "";
    for w in words {
        joined = ((joined + w) + "-");
    }
    println!(("joined=" + joined));
    println!(("factorial5=" + builtins_py::str(factorial_recursive(5))));
    let mut counter: Any = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    println!(("counter=" + builtins_py::str(counter)));
    let mut fox_list: Any = vec![1, 2, 3];
    fox_list[0] = 100;
    fox_list.append(4);
    println!(("fox_list0=" + builtins_py::str(fox_list[0])));
    println!(("fox_list_len=" + builtins_py::str(builtins_py::len(fox_list))));
    println!(("fox_list_last=" + builtins_py::str(fox_list[3])));
    let mut fox_map: Any = builtins_py::hashmap!();
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    println!(("map_get_brown=" + builtins_py::str(fox_map.get("brown"))));
    fox_map["fox"] = 30;
    println!(("map_get_fox=" + builtins_py::str(fox_map.get("fox"))));
    let mut name: Any = "fox";
    let mut speed: Any = 12;
    let mut formatted: Any = "The {} runs at {} mph".format(name, speed);
    println!(formatted);
    println!(("name_len=" + builtins_py::str(builtins_py::len(name))));
    let mut pair: Any = vec![name, speed];
    let mut p_name: Any = pair;
    println!(((("pair_name=" + p_name) + " pair_speed=") + builtins_py::str(p_speed)));
    let mut box: Any = Box::new(10);
    println!(("box_before=" + box.describe()));
    box.update_value(99);
    println!(("box_after=" + box.describe()));
    println!(("box_value=" + builtins_py::str(box.value)));
    // try {
        risky_divide(10, 0);
    // } catch {
    // }
    let mut safe_result: Any = risky_divide(10, 4);
    println!(("safe_result=" + builtins_py::str(safe_result)));
    let mut maybe_value: Any = null;
    println!(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    println!(("maybe_after=" + none_str(maybe_value)));
    println!(("contains_fox=" + bool_str(("fox" in words))));
    println!(("contains_wolf=" + bool_str(("wolf" in words))));
    println!(("contains_key=" + bool_str(("quick" in fox_map))));
    println!("DONE");
}
if (__name__ == "__main__") {
    main();
}