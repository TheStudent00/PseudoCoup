fn side_effect_marker(tag: String) -> bool {
    println!(("SIDE_EFFECT:" + tag));
    return true;
}
fn short_circuit_and_demo() -> () {
    let mut result: bool = (false && side_effect_marker("AND_RHS"));
    println!(("and_short_circuit_result=" + bool_str(result)));
}
fn short_circuit_or_demo() -> () {
    let mut result: bool = (true || side_effect_marker("OR_RHS"));
    println!(("or_short_circuit_result=" + bool_str(result)));
}
fn bool_str(b: bool) -> String {
    if b {
        return "True";
    } else {
        return "False";
    }
}
fn none_str(v: Option<Any>) -> String {
    if (v == null) {
        return "None";
    }
    return builtins_py::str(v);
}
fn classify_number(n: i32) -> String {
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
fn factorial_recursive(n: i32) -> i32 {
    if (n <= 1) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
struct Box {
    value: i32,
    history_len: i32,
}

impl Box {
    fn new(value: i32) -> Self {
        Self { value: value, history_len: 0 }
    }
    fn update_value(&mut self, new_value: i32) -> () {
        self.value = new_value;
        self.history_len = (self.history_len + 1);
    }
    fn describe(&mut self) -> String {
        return (((("Box(value=" + builtins_py::str(self.value)) + ", writes=") + builtins_py::str(self.history_len)) + ")");
    }
}
fn risky_divide(a: f64, b: f64) -> f64 {
    if (b == 0.0) {
        panic!(ValueError::new("division by zero not allowed"));
    }
    return (a / b);
}
fn main() -> () {
    let mut a: i32 = 17;
    let mut b: i32 = 5;
    let mut add_i: i32 = (a + b);
    let mut sub_i: i32 = (a - b);
    let mut mul_i: i32 = (a * b);
    let mut div_f: f64 = (a / b);
    let mut div_i: i32 = (a / b);
    let mut mod_i: i32 = (a % b);
    let mut neg_i: i32 = -(a);
    println!(("add_i=" + builtins_py::str(add_i)));
    println!(("sub_i=" + builtins_py::str(sub_i)));
    println!(("mul_i=" + builtins_py::str(mul_i)));
    println!(("div_f=" + builtins_py::str(div_f)));
    println!(("div_i=" + builtins_py::str(div_i)));
    println!(("mod_i=" + builtins_py::str(mod_i)));
    println!(("neg_i=" + builtins_py::str(neg_i)));
    let mut fa: f64 = 9.0;
    let mut fb: f64 = 2.0;
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
    let mut n: i32 = None;
    for n in vec![-(3), 0, 4, 42] {
        println!(((("classify(" + builtins_py::str(n)) + ")=") + classify_number(n)));
    }
    let mut i: i32 = 0;
    let mut total: i32 = 0;
    while (i < 5) {
        total = (total + i);
        i = (i + 1);
    }
    println!(("while_total=" + builtins_py::str(total)));
    let mut range_sum: i32 = 0;
    let mut k: i32 = None;
    for k in builtins_py::range(1, 6) {
        range_sum = (range_sum + k);
    }
    println!(("range_sum=" + builtins_py::str(range_sum)));
    let mut words: Vec<String> = vec!["quick", "brown", "quickfox"];
    let mut joined: String = "";
    let mut w: String = None;
    for w in words {
        joined = ((joined + w) + "-");
    }
    println!(("joined=" + joined));
    println!(("factorial5=" + builtins_py::str(factorial_recursive(5))));
    let mut counter: i32 = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    println!(("counter=" + builtins_py::str(counter)));
    let mut quickfox_list: Vec<i32> = vec![1, 2, 3];
    quickfox_list[0] = 100;
    quickfox_list.append(4);
    println!(("quickfox_list0=" + builtins_py::str(quickfox_list[0])));
    println!(("quickfox_list_len=" + builtins_py::str(builtins_py::len(quickfox_list))));
    println!(("quickfox_list_last=" + builtins_py::str(quickfox_list[3])));
    let mut quickfox_map: HashMap<String, i32> = builtins_py::hashmap!();
    quickfox_map["quick"] = 1;
    quickfox_map["brown"] = 2;
    quickfox_map["quickfox"] = 3;
    println!(("map_get_brown=" + builtins_py::str(quickfox_map.get("brown"))));
    quickfox_map["quickfox"] = 30;
    println!(("map_get_quickfox=" + builtins_py::str(quickfox_map.get("quickfox"))));
    let mut name: String = "fox";
    let mut speed: i32 = 12;
    let mut formatted: String = "The {} runs at {} mph".format(name, speed);
    println!(formatted);
    println!(("name_len=" + builtins_py::str(builtins_py::len(name))));
    let mut pair: Any = vec![name, speed];
    let mut p_name: String = pair[0];
    let mut p_speed: i32 = pair[1];
    println!(((("pair_name=" + p_name) + " pair_speed=") + builtins_py::str(p_speed)));
    let mut box: Box = Box::new(10);
    println!(("box_before=" + box.describe()));
    box.update_value(99);
    println!(("box_after=" + box.describe()));
    println!(("box_value=" + builtins_py::str(box.value)));
    // try {
        risky_divide(10.0, 0.0);
    // } catch {
    // }
    let mut safe_result: f64 = risky_divide(10.0, 4.0);
    println!(("safe_result=" + builtins_py::str(safe_result)));
    let mut maybe_value: Option<i32> = null;
    println!(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    println!(("maybe_after=" + none_str(maybe_value)));
    println!(("contains_quickfox=" + bool_str(("quickfox" in words))));
    println!(("contains_wolf=" + bool_str(("wolf" in words))));
    println!(("contains_key=" + bool_str(("quick" in quickfox_map))));
    println!("DONE");
}
if (__name__ == "__main__") {
    main();
}