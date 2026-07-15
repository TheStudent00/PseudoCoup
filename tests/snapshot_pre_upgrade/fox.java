import roundtrip.builtins_py.*;

import java.util.*;



public class Box {
    public Box(Object value) {
        this.history_len = 0;
    }
    public Object update_value(Object new_value) {
        this.value = new_value;
        this.history_len = (this.history_len + 1);
    }
    public Object describe() {
        return (((("Box(value=" + builtins_py.str(this.value)) + ", writes=") + builtins_py.str(this.history_len)) + ")");
    }
}

public class Main {
public static void side_effect_marker(Object tag) {
    builtins_py.print(("SIDE_EFFECT:" + tag));
    return true;
}
public static void short_circuit_and_demo() {
    Object result = (false && side_effect_marker("AND_RHS"));
    builtins_py.print(("and_short_circuit_result=" + bool_str(result)));
}
public static void short_circuit_or_demo() {
    Object result = (true || side_effect_marker("OR_RHS"));
    builtins_py.print(("or_short_circuit_result=" + bool_str(result)));
}
public static void bool_str(Object b) {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
public static void none_str(Object v) {
    if ((v == null)) {
        return "None";
    }
    return builtins_py.str(v);
}
public static void classify_number(Object n) {
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
public static void factorial_recursive(Object n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
public static void risky_divide(Object a, Object b) {
    if ((b == 0)) {
        throw new IllegalArgumentException("division by zero not allowed");
    }
    return (a / b);
}
public static void main() {
    Object a = 17;
    Object b = 5;
    Object add_i = (a + b);
    Object sub_i = (a - b);
    Object mul_i = (a * b);
    Object div_f = (a / b);
    Object div_i = ((int)(a / b));
    Object mod_i = (a % b);
    Object neg_i = -(a);
    builtins_py.print(("add_i=" + builtins_py.str(add_i)));
    builtins_py.print(("sub_i=" + builtins_py.str(sub_i)));
    builtins_py.print(("mul_i=" + builtins_py.str(mul_i)));
    builtins_py.print(("div_f=" + builtins_py.str(div_f)));
    builtins_py.print(("div_i=" + builtins_py.str(div_i)));
    builtins_py.print(("mod_i=" + builtins_py.str(mod_i)));
    builtins_py.print(("neg_i=" + builtins_py.str(neg_i)));
    Object fa = 9.0;
    Object fb = 2.0;
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
    for (Object n : new ArrayList<>(Arrays.asList(-(3), 0, 4, 42))) {
        builtins_py.print(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)));
    }
    Object i = 0;
    Object total = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    builtins_py.print(("while_total=" + builtins_py.str(total)));
    Object range_sum = 0;
    for (Object k : builtins_py.range(1, 6)) {
        range_sum = (range_sum + k);
    }
    builtins_py.print(("range_sum=" + builtins_py.str(range_sum)));
    Object words = new ArrayList<>(Arrays.asList("quick", "brown", "fox"));
    Object joined = "";
    for (Object w : words) {
        joined = ((joined + w) + "-");
    }
    builtins_py.print(("joined=" + joined));
    builtins_py.print(("factorial5=" + builtins_py.str(factorial_recursive(5))));
    Object counter = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    builtins_py.print(("counter=" + builtins_py.str(counter)));
    Object fox_list = new ArrayList<>(Arrays.asList(1, 2, 3));
    fox_list[0] = 100;
    fox_list.append(4);
    builtins_py.print(("fox_list0=" + builtins_py.str(fox_list[0])));
    builtins_py.print(("fox_list_len=" + builtins_py.str(builtins_py.len(fox_list))));
    builtins_py.print(("fox_list_last=" + builtins_py.str(fox_list[3])));
    Object fox_map = new HashMap<>();
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    builtins_py.print(("map_get_brown=" + builtins_py.str(fox_map.get("brown"))));
    fox_map["fox"] = 30;
    builtins_py.print(("map_get_fox=" + builtins_py.str(fox_map.get("fox"))));
    Object name = "fox";
    Object speed = 12;
    Object formatted = "The {} runs at {} mph".format(name, speed);
    builtins_py.print(formatted);
    builtins_py.print(("name_len=" + builtins_py.str(builtins_py.len(name))));
    Object pair = new ArrayList<>(Arrays.asList(name, speed));
    Object p_name = pair;
    builtins_py.print(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)));
    Object box = Box(10);
    builtins_py.print(("box_before=" + box.describe()));
    box.update_value(99);
    builtins_py.print(("box_after=" + box.describe()));
    builtins_py.print(("box_value=" + builtins_py.str(box.value)));
    try {
        risky_divide(10, 0);
    } catch (Exception e) {
    }
    Object safe_result = risky_divide(10, 4);
    builtins_py.print(("safe_result=" + builtins_py.str(safe_result)));
    Object maybe_value = null;
    builtins_py.print(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    builtins_py.print(("maybe_after=" + none_str(maybe_value)));
    builtins_py.print(("contains_fox=" + bool_str((words.contains("fox")))));
    builtins_py.print(("contains_wolf=" + bool_str((words.contains("wolf")))));
    builtins_py.print(("contains_key=" + bool_str((fox_map.contains("quick")))));
    builtins_py.print("DONE");
}
    public static void main(String[] args) {
        main();
    }
}