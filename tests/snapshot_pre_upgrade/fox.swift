import Foundation

func side_effect_marker(_ tag: Any) -> Void {
    builtins_py.print(("SIDE_EFFECT:" + tag))
    return true
}
func short_circuit_and_demo() -> Void {
    var result: Any = (false && side_effect_marker("AND_RHS"))
    builtins_py.print(("and_short_circuit_result=" + bool_str(result)))
}
func short_circuit_or_demo() -> Void {
    var result: Any = (true || side_effect_marker("OR_RHS"))
    builtins_py.print(("or_short_circuit_result=" + bool_str(result)))
}
func bool_str(_ b: Any) -> Void {
    if b {
        return "True"
    } else {
        return "False"
    }
}
func none_str(_ v: Any) -> Void {
    if (v is null) {
        return "None"
    }
    return builtins_py.str(v)
}
func classify_number(_ n: Any) -> Void {
    if (n < 0) {
        return "negative"
    } else if (n == 0) {
        return "zero"
    } else if (n < 10) {
        return "small"
    } else {
        return "large"
    }
}
func factorial_recursive(_ n: Any) -> Void {
    if (n <= 1) {
        return 1
    }
    return (n * factorial_recursive((n - 1)))
}
class Box {
    init(_ value: Any) {
        self.history_len = 0
    }
    func update_value(_ new_value: Any) -> Any {
        self.value = new_value
        self.history_len = (self.history_len + 1)
    }
    func describe() -> Any {
        return (((("Box(value=" + builtins_py.str(self.value)) + ", writes=") + builtins_py.str(self.history_len)) + ")")
    }
}
func risky_divide(_ a: Any, _ b: Any) -> Void {
    if (b == 0) {
        throw ValueError("division by zero not allowed")
    }
    return (a / b)
}
func main() -> Void {
    var a: Any = 17
    var b: Any = 5
    var add_i: Any = (a + b)
    var sub_i: Any = (a - b)
    var mul_i: Any = (a * b)
    var div_f: Any = (a / b)
    var div_i: Any = Int(a / b)
    var mod_i: Any = (a % b)
    var neg_i: Any = -(a)
    builtins_py.print(("add_i=" + builtins_py.str(add_i)))
    builtins_py.print(("sub_i=" + builtins_py.str(sub_i)))
    builtins_py.print(("mul_i=" + builtins_py.str(mul_i)))
    builtins_py.print(("div_f=" + builtins_py.str(div_f)))
    builtins_py.print(("div_i=" + builtins_py.str(div_i)))
    builtins_py.print(("mod_i=" + builtins_py.str(mod_i)))
    builtins_py.print(("neg_i=" + builtins_py.str(neg_i)))
    var fa: Any = 9.0
    var fb: Any = 2.0
    builtins_py.print(("float_div=" + builtins_py.str((fa / fb))))
    builtins_py.print(("float_floordiv=" + builtins_py.str(Int(fa / fb))))
    builtins_py.print(("eq=" + bool_str((a == b))))
    builtins_py.print(("ne=" + bool_str((a != b))))
    builtins_py.print(("lt=" + bool_str((a < b))))
    builtins_py.print(("le=" + bool_str((a <= b))))
    builtins_py.print(("gt=" + bool_str((a > b))))
    builtins_py.print(("ge=" + bool_str((a >= b))))
    short_circuit_and_demo()
    short_circuit_or_demo()
    builtins_py.print(("not_demo=" + bool_str(!((a == b)))))
    for n in [-(3), 0, 4, 42] {
        builtins_py.print(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)))
    }
    var i: Any = 0
    var total: Any = 0
    while (i < 5) {
        total = (total + i)
        i = (i + 1)
    }
    builtins_py.print(("while_total=" + builtins_py.str(total)))
    var range_sum: Any = 0
    for k in builtins_py.range(1, 6) {
        range_sum = (range_sum + k)
    }
    builtins_py.print(("range_sum=" + builtins_py.str(range_sum)))
    var words: Any = ["quick", "brown", "fox"]
    var joined: Any = ""
    for w in words {
        joined = ((joined + w) + "-")
    }
    builtins_py.print(("joined=" + joined))
    builtins_py.print(("factorial5=" + builtins_py.str(factorial_recursive(5))))
    var counter: Any = 0
    counter = (counter + 1)
    counter = (counter + 1)
    builtins_py.print(("counter=" + builtins_py.str(counter)))
    var fox_list: Any = [1, 2, 3]
    fox_list[0] = 100
    fox_list.append(4)
    builtins_py.print(("fox_list0=" + builtins_py.str(fox_list[0])))
    builtins_py.print(("fox_list_len=" + builtins_py.str(builtins_py.len(fox_list))))
    builtins_py.print(("fox_list_last=" + builtins_py.str(fox_list[3])))
    var fox_map: Any = [:]
    fox_map["quick"] = 1
    fox_map["brown"] = 2
    fox_map["fox"] = 3
    builtins_py.print(("map_get_brown=" + builtins_py.str(fox_map.get("brown"))))
    fox_map["fox"] = 30
    builtins_py.print(("map_get_fox=" + builtins_py.str(fox_map.get("fox"))))
    var name: Any = "fox"
    var speed: Any = 12
    var formatted: Any = "The {} runs at {} mph".format(name, speed)
    builtins_py.print(formatted)
    builtins_py.print(("name_len=" + builtins_py.str(builtins_py.len(name))))
    var pair: Any = [name, speed]
    var p_name: Any = pair
    builtins_py.print(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)))
    var box: Any = Box(10)
    builtins_py.print(("box_before=" + box.describe()))
    box.update_value(99)
    builtins_py.print(("box_after=" + box.describe()))
    builtins_py.print(("box_value=" + builtins_py.str(box.value)))
    do {
        try risky_divide(10, 0)
    } catch let e {
    }
    var safe_result: Any = risky_divide(10, 4)
    builtins_py.print(("safe_result=" + builtins_py.str(safe_result)))
    var maybe_value: Any = null
    builtins_py.print(("maybe_before=" + none_str(maybe_value)))
    maybe_value = 7
    builtins_py.print(("maybe_after=" + none_str(maybe_value)))
    builtins_py.print(("contains_fox=" + bool_str(("fox" in words))))
    builtins_py.print(("contains_wolf=" + bool_str(("wolf" in words))))
    builtins_py.print(("contains_key=" + bool_str(("quick" in fox_map))))
    builtins_py.print("DONE")
}
main([])