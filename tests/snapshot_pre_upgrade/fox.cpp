#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <any>
#include <stdexcept>

void side_effect_marker(std::any tag) {
    std::cout << ("SIDE_EFFECT:" + tag) << "\n";
    return true;
}
void short_circuit_and_demo() {
    std::any result = (false && side_effect_marker("AND_RHS"));
    std::cout << ("and_short_circuit_result=" + bool_str(result)) << "\n";
}
void short_circuit_or_demo() {
    std::any result = (true || side_effect_marker("OR_RHS"));
    std::cout << ("or_short_circuit_result=" + bool_str(result)) << "\n";
}
void bool_str(std::any b) {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
void none_str(std::any v) {
    if ((v == null)) {
        return "None";
    }
    return builtins_py::str(v);
}
void classify_number(std::any n) {
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
void factorial_recursive(std::any n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
class Box {
public:
    Box(std::any value) {
        this->value = value;
        this->history_len = 0;
    }
    std::any update_value(std::any new_value) {
        this->value = new_value;
        this->history_len = (this->history_len + 1);
    }
    std::any describe() {
        return (((("Box(value=" + builtins_py::str(this->value)) + ", writes=") + builtins_py::str(this->history_len)) + ")");
    }
};
void risky_divide(std::any a, std::any b) {
    if ((b == 0)) {
        throw std::runtime_error(ValueError("division by zero not allowed"));
    }
    return (a / b);
}
int main() {
    std::any a = 17;
    std::any b = 5;
    std::any add_i = (a + b);
    std::any sub_i = (a - b);
    std::any mul_i = (a * b);
    std::any div_f = (a / b);
    std::any div_i = (a / b);
    std::any mod_i = (a % b);
    std::any neg_i = -(a);
    std::cout << ("add_i=" + builtins_py::str(add_i)) << "\n";
    std::cout << ("sub_i=" + builtins_py::str(sub_i)) << "\n";
    std::cout << ("mul_i=" + builtins_py::str(mul_i)) << "\n";
    std::cout << ("div_f=" + builtins_py::str(div_f)) << "\n";
    std::cout << ("div_i=" + builtins_py::str(div_i)) << "\n";
    std::cout << ("mod_i=" + builtins_py::str(mod_i)) << "\n";
    std::cout << ("neg_i=" + builtins_py::str(neg_i)) << "\n";
    std::any fa = 9.0;
    std::any fb = 2.0;
    std::cout << ("float_div=" + builtins_py::str((fa / fb))) << "\n";
    std::cout << ("float_floordiv=" + builtins_py::str((fa / fb))) << "\n";
    std::cout << ("eq=" + bool_str((a == b))) << "\n";
    std::cout << ("ne=" + bool_str((a != b))) << "\n";
    std::cout << ("lt=" + bool_str((a < b))) << "\n";
    std::cout << ("le=" + bool_str((a <= b))) << "\n";
    std::cout << ("gt=" + bool_str((a > b))) << "\n";
    std::cout << ("ge=" + bool_str((a >= b))) << "\n";
    short_circuit_and_demo();
    short_circuit_or_demo();
    std::cout << ("not_demo=" + bool_str(!((a == b)))) << "\n";
    for (auto n : {-(3), 0, 4, 42}) {
        std::cout << ((("classify(" + builtins_py::str(n)) + ")=") + classify_number(n)) << "\n";
    }
    std::any i = 0;
    std::any total = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    std::cout << ("while_total=" + builtins_py::str(total)) << "\n";
    std::any range_sum = 0;
    for (int k = 1; k < 6; k++) {
        range_sum = (range_sum + k);
    }
    std::cout << ("range_sum=" + builtins_py::str(range_sum)) << "\n";
    std::any words = {"quick", "brown", "fox"};
    std::any joined = "";
    for (auto w : words) {
        joined = ((joined + w) + "-");
    }
    std::cout << ("joined=" + joined) << "\n";
    std::cout << ("factorial5=" + builtins_py::str(factorial_recursive(5))) << "\n";
    std::any counter = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    std::cout << ("counter=" + builtins_py::str(counter)) << "\n";
    std::any fox_list = {1, 2, 3};
    fox_list[0] = 100;
    fox_list.append(4);
    std::cout << ("fox_list0=" + builtins_py::str(fox_list[0])) << "\n";
    std::cout << ("fox_list_len=" + builtins_py::str(builtins_py::len(fox_list))) << "\n";
    std::cout << ("fox_list_last=" + builtins_py::str(fox_list[3])) << "\n";
    std::any fox_map = builtins_py::hashmap();
    fox_map["quick"] = 1;
    fox_map["brown"] = 2;
    fox_map["fox"] = 3;
    std::cout << ("map_get_brown=" + builtins_py::str(fox_map.get("brown"))) << "\n";
    fox_map["fox"] = 30;
    std::cout << ("map_get_fox=" + builtins_py::str(fox_map.get("fox"))) << "\n";
    std::any name = "fox";
    std::any speed = 12;
    std::any formatted = "The {} runs at {} mph".format(name, speed);
    std::cout << formatted << "\n";
    std::cout << ("name_len=" + builtins_py::str(builtins_py::len(name))) << "\n";
    std::any pair = {name, speed};
    std::any p_name = pair;
    std::cout << ((("pair_name=" + p_name) + " pair_speed=") + builtins_py::str(p_speed)) << "\n";
    std::any box = Box(10);
    std::cout << ("box_before=" + box.describe()) << "\n";
    box.update_value(99);
    std::cout << ("box_after=" + box.describe()) << "\n";
    std::cout << ("box_value=" + builtins_py::str(box.value)) << "\n";
    try {
        risky_divide(10, 0);
    } catch (const std::exception& e) {
    }
    std::any safe_result = risky_divide(10, 4);
    std::cout << ("safe_result=" + builtins_py::str(safe_result)) << "\n";
    std::any maybe_value = null;
    std::cout << ("maybe_before=" + none_str(maybe_value)) << "\n";
    maybe_value = 7;
    std::cout << ("maybe_after=" + none_str(maybe_value)) << "\n";
    std::cout << ("contains_fox=" + bool_str(("fox" in words))) << "\n";
    std::cout << ("contains_wolf=" + bool_str(("wolf" in words))) << "\n";
    std::cout << ("contains_key=" + bool_str(("quick" in fox_map))) << "\n";
    std::cout << "DONE" << "\n";
    return 0;
}
if ((__name__ == "__main__")) {
    main();
}