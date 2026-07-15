import * as builtins_py from "./builtins_py";

function side_effect_marker(tag: any): void {
    builtins_py.print(("SIDE_EFFECT:" + tag));
    return true;
}
function short_circuit_and_demo(): void {
    let result: any = (false && side_effect_marker("AND_RHS"));
    builtins_py.print(("and_short_circuit_result=" + bool_str(result)));
}
function short_circuit_or_demo(): void {
    let result: any = (true || side_effect_marker("OR_RHS"));
    builtins_py.print(("or_short_circuit_result=" + bool_str(result)));
}
function bool_str(b: any): void {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
function none_str(v: any): void {
    if ((v === null)) {
        return "None";
    }
    return builtins_py.str(v);
}
function classify_number(n: any): void {
    if ((n < 0)) {
        return "negative";
    } else if ((n == 0)) {
        return "zero";
    } else if ((n < 10)) {
        return "small";
    } else {
        return "large";
    }
}
function factorial_recursive(n: any): void {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
class Box {
    constructor(value: any) {
        this.history_len = 0;
    }
    update_value(new_value: any): any {
        this.value = new_value;
        this.history_len = (this.history_len + 1);
    }
    describe(): any {
        return (((("Box(value=" + builtins_py.str(this.value)) + ", writes=") + builtins_py.str(this.history_len)) + ")");
    }
}
function risky_divide(a: any, b: any): void {
    if ((b == 0)) {
        throw new Error("division by zero not allowed");
    }
    return (a / b);
}
function main(): void {
    let a: any = 17;
    let b: any = 5;
    let add_i: any = (a + b);
    let sub_i: any = (a - b);
    let mul_i: any = (a * b);
    let div_f: any = (a / b);
    let div_i: any = Math.floor(a / b);
    let mod_i: any = (a % b);
    let neg_i: any = -(a);
    builtins_py.print(("add_i=" + builtins_py.str(add_i)));
    builtins_py.print(("sub_i=" + builtins_py.str(sub_i)));
    builtins_py.print(("mul_i=" + builtins_py.str(mul_i)));
    builtins_py.print(("div_f=" + builtins_py.str(div_f)));
    builtins_py.print(("div_i=" + builtins_py.str(div_i)));
    builtins_py.print(("mod_i=" + builtins_py.str(mod_i)));
    builtins_py.print(("neg_i=" + builtins_py.str(neg_i)));
    let fa: any = 9.0;
    let fb: any = 2.0;
    builtins_py.print(("float_div=" + builtins_py.str((fa / fb))));
    builtins_py.print(("float_floordiv=" + builtins_py.str(Math.floor(fa / fb))));
    builtins_py.print(("eq=" + bool_str((a == b))));
    builtins_py.print(("ne=" + bool_str((a != b))));
    builtins_py.print(("lt=" + bool_str((a < b))));
    builtins_py.print(("le=" + bool_str((a <= b))));
    builtins_py.print(("gt=" + bool_str((a > b))));
    builtins_py.print(("ge=" + bool_str((a >= b))));
    short_circuit_and_demo();
    short_circuit_or_demo();
    builtins_py.print(("not_demo=" + bool_str(!((a == b)))));
    for (let n of [-(3), 0, 4, 42]) {
        builtins_py.print(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)));
    }
    let i: any = 0;
    let total: any = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    builtins_py.print(("while_total=" + builtins_py.str(total)));
    let range_sum: any = 0;
    for (let k of builtins_py.range(1, 6)) {
        range_sum = (range_sum + k);
    }
    builtins_py.print(("range_sum=" + builtins_py.str(range_sum)));
    let words: any = ["quick", "brown", "fox"];
    let joined: any = "";
    for (let w of words) {
        joined = ((joined + w) + "-");
    }
    builtins_py.print(("joined=" + joined));
    builtins_py.print(("factorial5=" + builtins_py.str(factorial_recursive(5))));
    let counter: any = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    builtins_py.print(("counter=" + builtins_py.str(counter)));
    let fox_list: any = [1, 2, 3];
    fox_list[0] = 100;
    fox_list.append(4);
    builtins_py.print(("fox_list0=" + builtins_py.str(fox_list[0])));
    builtins_py.print(("fox_list_len=" + builtins_py.str(builtins_py.len(fox_list))));
    builtins_py.print(("fox_list_last=" + builtins_py.str(fox_list[3])));
    let fox_map: any = {};
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    builtins_py.print(("map_get_brown=" + builtins_py.str(fox_map.get("brown"))));
    fox_map["fox"] = 30;
    builtins_py.print(("map_get_fox=" + builtins_py.str(fox_map.get("fox"))));
    let name: any = "fox";
    let speed: any = 12;
    let formatted: any = "The {} runs at {} mph".format(name, speed);
    builtins_py.print(formatted);
    builtins_py.print(("name_len=" + builtins_py.str(builtins_py.len(name))));
    let pair: any = [name, speed];
    let p_name: any = pair;
    builtins_py.print(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)));
    let box: any = new Box(10);
    builtins_py.print(("box_before=" + box.describe()));
    box.update_value(99);
    builtins_py.print(("box_after=" + box.describe()));
    builtins_py.print(("box_value=" + builtins_py.str(box.value)));
    try {
        risky_divide(10, 0);
    } catch (e) {
    }
    let safe_result: any = risky_divide(10, 4);
    builtins_py.print(("safe_result=" + builtins_py.str(safe_result)));
    let maybe_value: any = null;
    builtins_py.print(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    builtins_py.print(("maybe_after=" + none_str(maybe_value)));
    builtins_py.print(("contains_fox=" + bool_str(("fox" in words))));
    builtins_py.print(("contains_wolf=" + bool_str(("wolf" in words))));
    builtins_py.print(("contains_key=" + bool_str(("quick" in fox_map))));
    builtins_py.print("DONE");
}
main([]);