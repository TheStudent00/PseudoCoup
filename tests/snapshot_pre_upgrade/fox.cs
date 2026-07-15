using System;

using System.Collections.Generic;

using roundtrip.builtins_py;



public class Box {
    public Box(object value) {
        this.history_len = 0;
    }
    public object update_value(object new_value) {
        this.value = new_value;
        this.history_len = (this.history_len + 1);
    }
    public object describe() {
        return (((("Box(value=" + builtins_py.str(this.value)) + ", writes=") + builtins_py.str(this.history_len)) + ")");
    }
}

public class Program {
public static void side_effect_marker(object tag) {
    builtins_py.print(("SIDE_EFFECT:" + tag));
    return true;
}
public static void short_circuit_and_demo() {
    object result = (false && side_effect_marker("AND_RHS"));
    builtins_py.print(("and_short_circuit_result=" + bool_str(result)));
}
public static void short_circuit_or_demo() {
    object result = (true || side_effect_marker("OR_RHS"));
    builtins_py.print(("or_short_circuit_result=" + bool_str(result)));
}
public static void bool_str(object b) {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
public static void none_str(object v) {
    if ((v == null)) {
        return "None";
    }
    return builtins_py.str(v);
}
public static void classify_number(object n) {
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
public static void factorial_recursive(object n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
public static void risky_divide(object a, object b) {
    if ((b == 0)) {
        throw new ArgumentException("division by zero not allowed");
    }
    return (a / b);
}
public static void main() {
    object a = 17;
    object b = 5;
    object add_i = (a + b);
    object sub_i = (a - b);
    object mul_i = (a * b);
    object div_f = (a / b);
    object div_i = ((int)(a / b));
    object mod_i = (a % b);
    object neg_i = -(a);
    builtins_py.print(("add_i=" + builtins_py.str(add_i)));
    builtins_py.print(("sub_i=" + builtins_py.str(sub_i)));
    builtins_py.print(("mul_i=" + builtins_py.str(mul_i)));
    builtins_py.print(("div_f=" + builtins_py.str(div_f)));
    builtins_py.print(("div_i=" + builtins_py.str(div_i)));
    builtins_py.print(("mod_i=" + builtins_py.str(mod_i)));
    builtins_py.print(("neg_i=" + builtins_py.str(neg_i)));
    object fa = 9.0;
    object fb = 2.0;
    builtins_py.print(("float_div=" + builtins_py.str((fa / fb))));
    builtins_py.print(("float_floordiv=" + builtins_py.str(((int)(fa / fb)))));
    builtins_py.print(("eq=" + bool_str((a == b))));
    builtins_py.print(("ne=" + bool_str((a != b))));
    builtins_py.print(("lt=" + bool_str((a < b))));
    builtins_py.print(("le=" + bool_str((a <= b))));
    builtins_py.print(("gt=" + bool_str((a > b))));
    builtins_py.print(("ge=" + bool_str((a >= b))));
    short_circuit_and_demo();
    short_circuit_or_demo();
    builtins_py.print(("not_demo=" + bool_str(!((a == b)))));
    foreach (var n in new List<object> { -(3), 0, 4, 42 }) {
        builtins_py.print(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)));
    }
    object i = 0;
    object total = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    builtins_py.print(("while_total=" + builtins_py.str(total)));
    object range_sum = 0;
    foreach (var k in builtins_py.range(1, 6)) {
        range_sum = (range_sum + k);
    }
    builtins_py.print(("range_sum=" + builtins_py.str(range_sum)));
    object words = new List<object> { "quick", "brown", "fox" };
    object joined = "";
    foreach (var w in words) {
        joined = ((joined + w) + "-");
    }
    builtins_py.print(("joined=" + joined));
    builtins_py.print(("factorial5=" + builtins_py.str(factorial_recursive(5))));
    object counter = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    builtins_py.print(("counter=" + builtins_py.str(counter)));
    object fox_list = new List<object> { 1, 2, 3 };
    fox_list[0] = 100;
    fox_list.append(4);
    builtins_py.print(("fox_list0=" + builtins_py.str(fox_list[0])));
    builtins_py.print(("fox_list_len=" + builtins_py.str(builtins_py.len(fox_list))));
    builtins_py.print(("fox_list_last=" + builtins_py.str(fox_list[3])));
    object fox_map = new Dictionary<object, object>();
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    builtins_py.print(("map_get_brown=" + builtins_py.str(fox_map.get("brown"))));
    fox_map["fox"] = 30;
    builtins_py.print(("map_get_fox=" + builtins_py.str(fox_map.get("fox"))));
    object name = "fox";
    object speed = 12;
    object formatted = "The {} runs at {} mph".format(name, speed);
    builtins_py.print(formatted);
    builtins_py.print(("name_len=" + builtins_py.str(builtins_py.len(name))));
    object pair = new List<object> { name, speed };
    object p_name = pair;
    builtins_py.print(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)));
    object box = Box(10);
    builtins_py.print(("box_before=" + box.describe()));
    box.update_value(99);
    builtins_py.print(("box_after=" + box.describe()));
    builtins_py.print(("box_value=" + builtins_py.str(box.value)));
    try {
        risky_divide(10, 0);
    } catch (Exception e) {
    }
    object safe_result = risky_divide(10, 4);
    builtins_py.print(("safe_result=" + builtins_py.str(safe_result)));
    object maybe_value = null;
    builtins_py.print(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    builtins_py.print(("maybe_after=" + none_str(maybe_value)));
    builtins_py.print(("contains_fox=" + bool_str((words.Contains("fox")))));
    builtins_py.print(("contains_wolf=" + bool_str((words.Contains("wolf")))));
    builtins_py.print(("contains_key=" + bool_str((fox_map.Contains("quick")))));
    builtins_py.print("DONE");
}
    public static void Main(string[] args) {
        main();
    }
}