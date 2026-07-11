#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <any>
#include <stdexcept>

bool side_effect_marker(std::string tag) {
    std::cout << ("SIDE_EFFECT:" + tag) << "\n";
    return true;
}
void short_circuit_and_demo() {
    bool result = (false && side_effect_marker("AND_RHS"));
    std::cout << ("and_short_circuit_result=" + bool_str(result)) << "\n";
}
void short_circuit_or_demo() {
    bool result = (true || side_effect_marker("OR_RHS"));
    std::cout << ("or_short_circuit_result=" + bool_str(result)) << "\n";
}
std::string bool_str(bool b) {
    if (b) {
        return "True";
    } else {
        return "False";
    }
}
std::string none_str(std::optional<std::any> v) {
    if ((v == null)) {
        return "None";
    }
    return builtins_py::str(v);
}
std::string classify_number(int n) {
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
int factorial_recursive(int n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial_recursive((n - 1)));
}
class Box {
public:
    int value;
    int history_len;
    Box(int value) {
        this->value = value;
        this->history_len = 0;
    }
    void update_value(int new_value) {
        this->value = new_value;
        this->history_len = (this->history_len + 1);
    }
    std::string describe() {
        return (((("Box(value=" + builtins_py::str(this->value)) + ", writes=") + builtins_py::str(this->history_len)) + ")");
    }
};
double risky_divide(double a, double b) {
    if ((b == 0.0)) {
        throw std::runtime_error(ValueError("division by zero not allowed"));
    }
    return (a / b);
}
int main() {
    int a = 17;
    int b = 5;
    int add_i = (a + b);
    int sub_i = (a - b);
    int mul_i = (a * b);
    double div_f = (a / b);
    int div_i = (a / b);
    int mod_i = (a % b);
    int neg_i = -(a);
    std::cout << ("add_i=" + builtins_py::str(add_i)) << "\n";
    std::cout << ("sub_i=" + builtins_py::str(sub_i)) << "\n";
    std::cout << ("mul_i=" + builtins_py::str(mul_i)) << "\n";
    std::cout << ("div_f=" + builtins_py::str(div_f)) << "\n";
    std::cout << ("div_i=" + builtins_py::str(div_i)) << "\n";
    std::cout << ("mod_i=" + builtins_py::str(mod_i)) << "\n";
    std::cout << ("neg_i=" + builtins_py::str(neg_i)) << "\n";
    double fa = 9.0;
    double fb = 2.0;
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
    int n = nullptr;
    for (auto n : {-(3), 0, 4, 42}) {
        std::cout << ((("classify(" + builtins_py::str(n)) + ")=") + classify_number(n)) << "\n";
    }
    int i = 0;
    int total = 0;
    while ((i < 5)) {
        total = (total + i);
        i = (i + 1);
    }
    std::cout << ("while_total=" + builtins_py::str(total)) << "\n";
    int range_sum = 0;
    int k = nullptr;
    for (int k = 1; k < 6; k++) {
        range_sum = (range_sum + k);
    }
    std::cout << ("range_sum=" + builtins_py::str(range_sum)) << "\n";
    std::vector<std::string> words = {"quick", "brown", "quickfox"};
    std::string joined = "";
    std::string w = nullptr;
    for (auto w : words) {
        joined = ((joined + w) + "-");
    }
    std::cout << ("joined=" + joined) << "\n";
    std::cout << ("factorial5=" + builtins_py::str(factorial_recursive(5))) << "\n";
    int counter = 0;
    counter = (counter + 1);
    counter = (counter + 1);
    std::cout << ("counter=" + builtins_py::str(counter)) << "\n";
    std::vector<int> quickfox_list = {1, 2, 3};
    quickfox_list[0] = 100;
    quickfox_list.append(4);
    std::cout << ("quickfox_list0=" + builtins_py::str(quickfox_list[0])) << "\n";
    std::cout << ("quickfox_list_len=" + builtins_py::str(builtins_py::len(quickfox_list))) << "\n";
    std::cout << ("quickfox_list_last=" + builtins_py::str(quickfox_list[3])) << "\n";
    std::unordered_map<std::string, int> quickfox_map = builtins_py::hashmap();
    quickfox_map["quick"] = 1;
    quickfox_map["brown"] = 2;
    quickfox_map["quickfox"] = 3;
    std::cout << ("map_get_brown=" + builtins_py::str(quickfox_map.get("brown"))) << "\n";
    quickfox_map["quickfox"] = 30;
    std::cout << ("map_get_quickfox=" + builtins_py::str(quickfox_map.get("quickfox"))) << "\n";
    std::string name = "fox";
    int speed = 12;
    std::string formatted = "The {} runs at {} mph".format(name, speed);
    std::cout << formatted << "\n";
    std::cout << ("name_len=" + builtins_py::str(builtins_py::len(name))) << "\n";
    std::any pair = {name, speed};
    std::string p_name = pair[0];
    int p_speed = pair[1];
    std::cout << ((("pair_name=" + p_name) + " pair_speed=") + builtins_py::str(p_speed)) << "\n";
    Box box = Box(10);
    std::cout << ("box_before=" + box.describe()) << "\n";
    box.update_value(99);
    std::cout << ("box_after=" + box.describe()) << "\n";
    std::cout << ("box_value=" + builtins_py::str(box.value)) << "\n";
    try {
        risky_divide(10.0, 0.0);
    } catch (const std::exception& e) {
    }
    double safe_result = risky_divide(10.0, 4.0);
    std::cout << ("safe_result=" + builtins_py::str(safe_result)) << "\n";
    std::optional<int> maybe_value = null;
    std::cout << ("maybe_before=" + none_str(maybe_value)) << "\n";
    maybe_value = 7;
    std::cout << ("maybe_after=" + none_str(maybe_value)) << "\n";
    std::cout << ("contains_quickfox=" + bool_str(("quickfox" in words))) << "\n";
    std::cout << ("contains_wolf=" + bool_str(("wolf" in words))) << "\n";
    std::cout << ("contains_key=" + bool_str(("quick" in quickfox_map))) << "\n";
    std::cout << "DONE" << "\n";
    return 0;
}
if ((__name__ == "__main__")) {
    main();
}