import 'builtins_py.dart';



var side_effect_marker(var tag) {
    print("SIDE_EFFECT:" + tag);
    return true;
}

var short_circuit_and_demo() {
    var result = false && side_effect_marker("AND_RHS");
    print("and_short_circuit_result=" + bool_str(result));
}

var short_circuit_or_demo() {
    var result = true || side_effect_marker("OR_RHS");
    print("or_short_circuit_result=" + bool_str(result));
}

var bool_str(var b) {
        if (b) {
        return "True";
    } else {
        return "False";
    };
}

var none_str(var v) {
        if (v == null) {
        return "None";
    };
    return (v).toString();
}

var classify_number(var n) {
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

var factorial_recursive(var n) {
        if (n <= 1) {
        return 1;
    };
    return n * factorial_recursive(n - 1);
}

class Box {
    Box(this.value) {
        this.history_len = 0;
    }
    var update_value(var new_value) {
        this.value = new_value;
        this.history_len = this.history_len + 1;
    }
    var describe() {
        return "Box(value=" + (this.value).toString() + ", writes=" + (this.history_len).toString() + ")";
    }
}

var risky_divide(var a, var b) {
        if (b == 0) {
        throw(ValueError("division by zero not allowed"));
    };
    return a / b;
}

var main() {
    var a = 17;
    var b = 5;
    var add_i = a + b;
    var sub_i = a - b;
    var mul_i = a * b;
    var div_f = a / b;
    var div_i = a ~/ b;
    var mod_i = a % b;
    var neg_i = -(a);
    print("add_i=" + (add_i).toString());
    print("sub_i=" + (sub_i).toString());
    print("mul_i=" + (mul_i).toString());
    print("div_f=" + (div_f).toString());
    print("div_i=" + (div_i).toString());
    print("mod_i=" + (mod_i).toString());
    print("neg_i=" + (neg_i).toString());
    var fa = 9.0;
    var fb = 2.0;
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
        for (var n in [-(3), 0, 4, 42]) {
        print("classify(" + (n).toString() + ")=" + classify_number(n));
    };
    var i = 0;
    var total = 0;
        while (i < 5) {
        total = total + i;
        i = i + 1;
    };
    print("while_total=" + (total).toString());
    var range_sum = 0;
        for (var k in range(1, 6)) {
        range_sum = range_sum + k;
    };
    print("range_sum=" + (range_sum).toString());
    var words = ["quick", "brown", "fox"];
    var joined = "";
        for (var w in words) {
        joined = joined + w + "-";
    };
    print("joined=" + joined);
    print("factorial5=" + (factorial_recursive(5)).toString());
    var counter = 0;
    counter = counter + 1;
    counter = counter + 1;
    print("counter=" + (counter).toString());
    var fox_list = [1, 2, 3];
    fox_list[0] = 100;
    fox_list.append(4);
    print("fox_list0=" + (fox_list[0]).toString());
    print("fox_list_len=" + (fox_list.length).toString());
    print("fox_list_last=" + (fox_list[3]).toString());
    var fox_map = {};
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    print("map_get_brown=" + (fox_map.get("brown")).toString());
    fox_map["fox"] = 30;
    print("map_get_fox=" + (fox_map.get("fox")).toString());
    var name = "fox";
    var speed = 12;
    var formatted = "The {} runs at {} mph".format(name, speed);
    print(formatted);
    print("name_len=" + (name.length).toString());
    var pair = [name, speed];
    var p_name = pair;
    print("pair_name=" + p_name + " pair_speed=" + (p_speed).toString());
    var box = Box(10);
    print("box_before=" + box.describe());
    box.update_value(99);
    print("box_after=" + box.describe());
    print("box_value=" + (box.value).toString());
        try {
        risky_divide(10, 0);
    } catch (e) {
    };
    var safe_result = risky_divide(10, 4);
    print("safe_result=" + (safe_result).toString());
    var maybe_value = null;
    print("maybe_before=" + none_str(maybe_value));
    maybe_value = 7;
    print("maybe_after=" + none_str(maybe_value));
    print("contains_fox=" + bool_str(words.contains("fox")));
    print("contains_wolf=" + bool_str(words.contains("wolf")));
    print("contains_key=" + bool_str(fox_map.contains("quick")));
    print("DONE");
}