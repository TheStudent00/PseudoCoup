import 'builtins_py.dart';



bool side_effect_marker(String tag) {
    print("SIDE_EFFECT:" + tag);
    return true;
}

void short_circuit_and_demo() {
    bool result = false && side_effect_marker("AND_RHS");
    print("and_short_circuit_result=" + bool_str(result));
}

void short_circuit_or_demo() {
    bool result = true || side_effect_marker("OR_RHS");
    print("or_short_circuit_result=" + bool_str(result));
}

String bool_str(bool b) {
        if (b) {
        return "True";
    } else {
        return "False";
    };
}

String none_str(dynamic v) {
        if (v == null) {
        return "None";
    };
    return (v).toString();
}

String classify_number(int n) {
        if (n < 0) {
        return "negative";
    } else if (n == 0) {
        return "zero";
    } else if (n < 10) {
        return "small";
    } else {
        return "large";
    };
}

int factorial_recursive(int n) {
        if (n <= 1) {
        return 1;
    };
    return n * factorial_recursive(n - 1);
}

class Box {
    int value = 0;
    int history_len = 0;
    Box(this.value) {
        this.history_len = 0;
    }
    void update_value(int new_value) {
        this.value = new_value;
        this.history_len = this.history_len + 1;
    }
    String describe() {
        return "Box(value=" + (this.value).toString() + ", writes=" + (this.history_len).toString() + ")";
    }
}

double risky_divide(double a, double b) {
        if (b == 0.0) {
        throw(ValueError("division by zero not allowed"));
    };
    return a / b;
}

void main() {
    int a = 17;
    int b = 5;
    int add_i = a + b;
    int sub_i = a - b;
    int mul_i = a * b;
    double div_f = a / b;
    int div_i = a ~/ b;
    int mod_i = a % b;
    int neg_i = -(a);
    print("add_i=" + (add_i).toString());
    print("sub_i=" + (sub_i).toString());
    print("mul_i=" + (mul_i).toString());
    print("div_f=" + (div_f).toString());
    print("div_i=" + (div_i).toString());
    print("mod_i=" + (mod_i).toString());
    print("neg_i=" + (neg_i).toString());
    double fa = 9.0;
    double fb = 2.0;
    print("float_div=" + (fa / fb).toString());
    print("float_floordiv=" + (fa ~/ fb).toString());
    print("eq=" + bool_str(a == b));
    print("ne=" + bool_str(a != b));
    print("lt=" + bool_str(a < b));
    print("le=" + bool_str(a <= b));
    print("gt=" + bool_str(a > b));
    print("ge=" + bool_str(a >= b));
    short_circuit_and_demo();
    short_circuit_or_demo();
    print("not_demo=" + bool_str(!(a == b)));
    int n = 0;
        for (var n in [-(3), 0, 4, 42]) {
        print("classify(" + (n).toString() + ")=" + classify_number(n));
    };
    int i = 0;
    int total = 0;
        while (i < 5) {
        total = total + i;
        i = i + 1;
    };
    print("while_total=" + (total).toString());
    int range_sum = 0;
    int k = 0;
        for (var k in range(1, 6)) {
        range_sum = range_sum + k;
    };
    print("range_sum=" + (range_sum).toString());
    List<String> words = ["quick", "brown", "quickfox"];
    String joined = "";
    String w = "";
        for (var w in words) {
        joined = joined + w + "-";
    };
    print("joined=" + joined);
    print("factorial5=" + (factorial_recursive(5)).toString());
    int counter = 0;
    counter = counter + 1;
    counter = counter + 1;
    print("counter=" + (counter).toString());
    List<int> quickfox_list = [1, 2, 3];
    quickfox_list[0] = 100;
    quickfox_list.append(4);
    print("quickfox_list0=" + (quickfox_list[0]).toString());
    print("quickfox_list_len=" + (quickfox_list.length).toString());
    print("quickfox_list_last=" + (quickfox_list[3]).toString());
    Map<String, int> quickfox_map = {};
    quickfox_map["quick"] = 1;
    quickfox_map["brown"] = 2;
    quickfox_map["quickfox"] = 3;
    print("map_get_brown=" + (quickfox_map.get("brown")).toString());
    quickfox_map["quickfox"] = 30;
    print("map_get_quickfox=" + (quickfox_map.get("quickfox")).toString());
    String name = "fox";
    int speed = 12;
    String formatted = "The {} runs at {} mph".format(name, speed);
    print(formatted);
    print("name_len=" + (name.length).toString());
    List<dynamic> pair = [name, speed];
    String p_name = pair[0];
    int p_speed = pair[1];
    print("pair_name=" + p_name + " pair_speed=" + (p_speed).toString());
    Box box = Box(10);
    print("box_before=" + box.describe());
    box.update_value(99);
    print("box_after=" + box.describe());
    print("box_value=" + (box.value).toString());
        try {
        risky_divide(10.0, 0.0);
    } catch (e) {
    };
    double safe_result = risky_divide(10.0, 4.0);
    print("safe_result=" + (safe_result).toString());
    int? maybe_value = null;
    print("maybe_before=" + none_str(maybe_value));
    maybe_value = 7;
    print("maybe_after=" + none_str(maybe_value));
    print("contains_quickfox=" + bool_str(words.contains("quickfox")));
    print("contains_wolf=" + bool_str(words.contains("wolf")));
    print("contains_key=" + bool_str(quickfox_map.contains("quick")));
    print("DONE");
}