import roundtrip.builtins_py.*

fun side_effect_marker(tag: Any?): Unit {
    print(("SIDE_EFFECT:" + tag))
    return true
}
fun short_circuit_and_demo(): Unit {
    var result: Any? = (false && side_effect_marker("AND_RHS"))
    print(("and_short_circuit_result=" + bool_str(result)))
}
fun short_circuit_or_demo(): Unit {
    var result: Any? = (true || side_effect_marker("OR_RHS"))
    print(("or_short_circuit_result=" + bool_str(result)))
}
fun bool_str(b: Any?): Unit {
    if (b) {
        return "True"
    } else {
        return "False"
    }
}
fun none_str(v: Any?): Unit {
    if ((v === null)) {
        return "None"
    }
    return str(v)
}
fun classify_number(n: Any?): Unit {
    if ((n < 0)) {
        return "negative"
    } else if ((n == 0)) {
        return "zero"
    } else if ((n < 10)) {
        return "small"
    } else {
        return "large"
    }
}
fun factorial_recursive(n: Any?): Unit {
    if ((n <= 1)) {
        return 1
    }
    return (n * factorial_recursive((n - 1)))
}
class Box {
    constructor(value: Any?) {
        this.history_len = 0
    }
    fun update_value(new_value: Any?): Unit {
        this.value = new_value
        this.history_len = (this.history_len + 1)
    }
    fun describe(): Unit {
        return (((("Box(value=" + str(this.value)) + ", writes=") + str(this.history_len)) + ")")
    }
}
fun risky_divide(a: Any?, b: Any?): Unit {
    if ((b == 0)) {
        throw IllegalArgumentException("division by zero not allowed")
    }
    return (a / b)
}
fun main(): Unit {
    var a: Any? = 17
    var b: Any? = 5
    var add_i: Any? = (a + b)
    var sub_i: Any? = (a - b)
    var mul_i: Any? = (a * b)
    var div_f: Any? = (a / b)
    var div_i: Any? = (a / b).toInt()
    var mod_i: Any? = (a % b)
    var neg_i: Any? = -(a)
    print(("add_i=" + str(add_i)))
    print(("sub_i=" + str(sub_i)))
    print(("mul_i=" + str(mul_i)))
    print(("div_f=" + str(div_f)))
    print(("div_i=" + str(div_i)))
    print(("mod_i=" + str(mod_i)))
    print(("neg_i=" + str(neg_i)))
    var fa: Any? = 9.0
    var fb: Any? = 2.0
    print(("float_div=" + str((fa / fb))))
    print(("float_floordiv=" + str((fa / fb).toInt())))
    print(("eq=" + bool_str((a == b))))
    print(("ne=" + bool_str((a != b))))
    print(("lt=" + bool_str((a < b))))
    print(("le=" + bool_str((a <= b))))
    print(("gt=" + bool_str((a > b))))
    print(("ge=" + bool_str((a >= b))))
    short_circuit_and_demo()
    short_circuit_or_demo()
    print(("not_demo=" + bool_str(!((a == b)))))
    for (n in mutableListOf(-(3), 0, 4, 42)) {
        print(((("classify(" + str(n)) + ")=") + classify_number(n)))
    }
    var i: Any? = 0
    var total: Any? = 0
    while ((i < 5)) {
        total = (total + i)
        i = (i + 1)
    }
    print(("while_total=" + str(total)))
    var range_sum: Any? = 0
    for (k in (1 until 6)) {
        range_sum = (range_sum + k)
    }
    print(("range_sum=" + str(range_sum)))
    var words: Any? = mutableListOf("quick", "brown", "fox")
    var joined: Any? = ""
    for (w in words) {
        joined = ((joined + w) + "-")
    }
    print(("joined=" + joined))
    print(("factorial5=" + str(factorial_recursive(5))))
    var counter: Any? = 0
    counter = (counter + 1)
    counter = (counter + 1)
    print(("counter=" + str(counter)))
    var fox_list: Any? = mutableListOf(1, 2, 3)
    fox_list[0] = 100
    fox_list.append(4)
    print(("fox_list0=" + str(fox_list[0])))
    print(("fox_list_len=" + str(len(fox_list))))
    print(("fox_list_last=" + str(fox_list[3])))
    var fox_map: Any? = mutableMapOf()
    fox_map["quick"] = 1
    fox_map["brown"] = 2
    fox_map["fox"] = 3
    print(("map_get_brown=" + str(fox_map.get("brown"))))
    fox_map["fox"] = 30
    print(("map_get_fox=" + str(fox_map.get("fox"))))
    var name: Any? = "fox"
    var speed: Any? = 12
    var formatted: Any? = "The {} runs at {} mph".format(name, speed)
    print(formatted)
    print(("name_len=" + str(len(name))))
    var pair: Any? = mutableListOf(name, speed)
    var p_name: Any? = pair
    print(((("pair_name=" + p_name) + " pair_speed=") + str(p_speed)))
    var box: Any? = Box(10)
    print(("box_before=" + box.describe()))
    box.update_value(99)
    print(("box_after=" + box.describe()))
    print(("box_value=" + str(box.value)))
    try {
        risky_divide(10, 0)
    } catch (e: Exception) {
    }
    var safe_result: Any? = risky_divide(10, 4)
    print(("safe_result=" + str(safe_result)))
    var maybe_value: Any? = null
    print(("maybe_before=" + none_str(maybe_value)))
    maybe_value = 7
    print(("maybe_after=" + none_str(maybe_value)))
    print(("contains_fox=" + bool_str(("fox" in words))))
    print(("contains_wolf=" + bool_str(("wolf" in words))))
    print(("contains_key=" + bool_str(("quick" in fox_map))))
    print("DONE")
}

fun main(args: Array<String>) {
    main()
}