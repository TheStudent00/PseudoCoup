import roundtrip.builtins_py.*;

import java.util.*;



public class Box {
    public int value = 0;
    public int history_len = 0;
    public Box(int value) {
        this.history_len = 0;
    }
    public void update_value(int new_value) {
        this.value = new_value;
        this.history_len = (this.history_len + 1);
    }
    public String describe() {
        return (((("Box(value=" + builtins_py.str(this.value)) + ", writes=") + builtins_py.str(this.history_len)) + ")");
    }
}

public class Main {
public static boolean side_effect_marker(String tag) {
    builtins_py.print(("SIDE_EFFECT:" + tag));
    return true;
}
public static void short_circuit_and_demo() {
    boolean result = (false && side_effect_marker("AND_RHS"));
    builtins_py.print(("and_short_circuit_result=" + bool_str(result)));
}
public static void short_circuit_or_demo() {
    boolean result = (true || side_effect_marker("OR_RHS"));
    builtins_py.print(("or_short_circuit_result=" + bool_str(result)));
}
public static String bool_str(boolean b) {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
public static String none_str(Object v) {
    if ((v == null)) {
        return "None";
    }
    return builtins_py.str(v);
}
public static String classify_number(int n) {
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
public static int factorial_recursive(int n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
public static double risky_divide(double a, double b) {
    if ((b == 0.0)) {
        throw new IllegalArgumentException("division by zero not allowed");
    }
    return (a / b);
}
public static void main() {
    int a = 17;
    int b = 5;
    int add_i = (a + b);
    int sub_i = (a - b);
    int mul_i = (a * b);
    double div_f = (a / b);
    int div_i = ((int)(a / b));
    int mod_i = (a % b);
    int neg_i = -(a);
    builtins_py.print(("add_i=" + builtins_py.str(add_i)));
    builtins_py.print(("sub_i=" + builtins_py.str(sub_i)));
    builtins_py.print(("mul_i=" + builtins_py.str(mul_i)));
    builtins_py.print(("div_f=" + builtins_py.str(div_f)));
    builtins_py.print(("div_i=" + builtins_py.str(div_i)));
    builtins_py.print(("mod_i=" + builtins_py.str(mod_i)));
    builtins_py.print(("neg_i=" + builtins_py.str(neg_i)));
    double fa = 9.0;
    double fb = 2.0;
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
    int n = 0;
    for (n : new ArrayList<>(Arrays.asList(-(3), 0, 4, 42))) {
        builtins_py.print(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)));
    }
    int i = 0;
    int total = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    builtins_py.print(("while_total=" + builtins_py.str(total)));
    int range_sum = 0;
    int k = 0;
    for (k : builtins_py.range(1, 6)) {
        range_sum = (range_sum + k);
    }
    builtins_py.print(("range_sum=" + builtins_py.str(range_sum)));
    ArrayList<String> words = new ArrayList<>(Arrays.asList("quick", "brown", "quickfox"));
    String joined = "";
    String w = "";
    for (w : words) {
        joined = ((joined + w) + "-");
    }
    builtins_py.print(("joined=" + joined));
    builtins_py.print(("factorial5=" + builtins_py.str(factorial_recursive(5))));
    int counter = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    builtins_py.print(("counter=" + builtins_py.str(counter)));
    ArrayList<Integer> quickfox_list = new ArrayList<>(Arrays.asList(1, 2, 3));
    quickfox_list[0] = 100;
    quickfox_list.append(4);
    builtins_py.print(("quickfox_list0=" + builtins_py.str(quickfox_list[0])));
    builtins_py.print(("quickfox_list_len=" + builtins_py.str(builtins_py.len(quickfox_list))));
    builtins_py.print(("quickfox_list_last=" + builtins_py.str(quickfox_list[3])));
    HashMap<String, Integer> quickfox_map = new HashMap<>();
    quickfox_map["quick"] = 1;
    quickfox_map["brown"] = 2;
    quickfox_map["quickfox"] = 3;
    builtins_py.print(("map_get_brown=" + builtins_py.str(quickfox_map.get("brown"))));
    quickfox_map["quickfox"] = 30;
    builtins_py.print(("map_get_quickfox=" + builtins_py.str(quickfox_map.get("quickfox"))));
    String name = "fox";
    int speed = 12;
    String formatted = "The {} runs at {} mph".format(name, speed);
    builtins_py.print(formatted);
    builtins_py.print(("name_len=" + builtins_py.str(builtins_py.len(name))));
    ArrayList<Object> pair = new ArrayList<>(Arrays.asList(name, speed));
    String p_name = pair[0];
    int p_speed = pair[1];
    builtins_py.print(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)));
    Box box = Box(10);
    builtins_py.print(("box_before=" + box.describe()));
    box.update_value(99);
    builtins_py.print(("box_after=" + box.describe()));
    builtins_py.print(("box_value=" + builtins_py.str(box.value)));
    try {
        risky_divide(10.0, 0.0);
    } catch (Exception e) {
    }
    double safe_result = risky_divide(10.0, 4.0);
    builtins_py.print(("safe_result=" + builtins_py.str(safe_result)));
    Integer maybe_value = null;
    builtins_py.print(("maybe_before=" + none_str(maybe_value)));
    maybe_value = 7;
    builtins_py.print(("maybe_after=" + none_str(maybe_value)));
    builtins_py.print(("contains_quickfox=" + bool_str((words.contains("quickfox")))));
    builtins_py.print(("contains_wolf=" + bool_str((words.contains("wolf")))));
    builtins_py.print(("contains_key=" + bool_str((quickfox_map.contains("quick")))));
    builtins_py.print("DONE");
}
    public static void main(String[] args) {
        main();
    }
}