import roundtrip.builtins_py.*

fun side_effect_marker(tag: String): Boolean {
    print(("SIDE_EFFECT:" + tag))
    return true
}
fun short_circuit_and_demo(): Unit {
    var result: Boolean = (false && side_effect_marker("AND_RHS"))
    print(("and_short_circuit_result=" + bool_str(result)))
}
fun short_circuit_or_demo(): Unit {
    var result: Boolean = (true || side_effect_marker("OR_RHS"))
    print(("or_short_circuit_result=" + bool_str(result)))
}
fun bool_str(b: Boolean): String {
    if (b) {
        return "True"
    } else {
        return "False"
    }
}
fun none_str(v: Any?): String {
    if ((v === null)) {
        return "None"
    }
    return str(v)
}
fun classify_number(n: Int): String {
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
fun factorial_recursive(n: Int): Int {
    if ((n <= 1)) {
        return 1
    }
    return (n * factorial_recursive((n - 1)))
}
class Box {
    var value: Int = 0
    var history_len: Int = 0
    constructor(value: Int) {
        this.history_len = 0
    }
    fun update_value(new_value: Int): Unit {
        this.value = new_value
        this.history_len = (this.history_len + 1)
    }
    fun describe(): String {
        return (((("Box(value=" + str(this.value)) + ", writes=") + str(this.history_len)) + ")")
    }
}
fun risky_divide(a: Double, b: Double): Double {
    if ((b == 0.0)) {
        throw IllegalArgumentException("division by zero not allowed")
    }
    return (a / b)
}
fun main(): Unit {
    var a: Int = 17
    var b: Int = 5
    var add_i: Int = (a + b)
    var sub_i: Int = (a - b)
    var mul_i: Int = (a * b)
    var div_f: Double = (a / b)
    var div_i: Int = (a / b).toInt()
    var mod_i: Int = (a % b)
    var neg_i: Int = -(a)
    print(("add_i=" + str(add_i)))
    print(("sub_i=" + str(sub_i)))
    print(("mul_i=" + str(mul_i)))
    print(("div_f=" + str(div_f)))
    print(("div_i=" + str(div_i)))
    print(("mod_i=" + str(mod_i)))
    print(("neg_i=" + str(neg_i)))
    var fa: Double = 9.0
    var fb: Double = 2.0
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
    var n: Int = 0
    for (n in mutableListOf(-(3), 0, 4, 42)) {
        print(((("classify(" + str(n)) + ")=") + classify_number(n)))
    }
    var i: Int = 0
    var total: Int = 0
    while ((i < 5)) {
        total = (total + i)
        i = (i + 1)
    }
    print(("while_total=" + str(total)))
    var range_sum: Int = 0
    var k: Int = 0
    for (k in (1 until 6)) {
        range_sum = (range_sum + k)
    }
    print(("range_sum=" + str(range_sum)))
    var words: MutableList<String>? = mutableListOf("quick", "brown", "quickfox")
    var joined: String = ""
    var w: String = ""
    for (w in words) {
        joined = ((joined + w) + "-")
    }
    print(("joined=" + joined))
    print(("factorial5=" + str(factorial_recursive(5))))
    var counter: Int = 0
    counter = (counter + 1)
    counter = (counter + 1)
    print(("counter=" + str(counter)))
    var quickfox_list: MutableList<Int>? = mutableListOf(1, 2, 3)
    quickfox_list[0] = 100
    quickfox_list.append(4)
    print(("quickfox_list0=" + str(quickfox_list[0])))
    print(("quickfox_list_len=" + str(len(quickfox_list))))
    print(("quickfox_list_last=" + str(quickfox_list[3])))
    var quickfox_map: MutableMap<String, Int>? = mutableMapOf()
    quickfox_map["quick"] = 1
    quickfox_map["brown"] = 2
    quickfox_map["quickfox"] = 3
    print(("map_get_brown=" + str(quickfox_map.get("brown"))))
    quickfox_map["quickfox"] = 30
    print(("map_get_quickfox=" + str(quickfox_map.get("quickfox"))))
    var name: String = "fox"
    var speed: Int = 12
    var formatted: String = "The {} runs at {} mph".format(name, speed)
    print(formatted)
    print(("name_len=" + str(len(name))))
    var pair: MutableList<Any?>? = mutableListOf(name, speed)
    var p_name: String = pair[0]
    var p_speed: Int = pair[1]
    print(((("pair_name=" + p_name) + " pair_speed=") + str(p_speed)))
    var box: Box = Box(10)
    print(("box_before=" + box.describe()))
    box.update_value(99)
    print(("box_after=" + box.describe()))
    print(("box_value=" + str(box.value)))
    try {
        risky_divide(10.0, 0.0)
    } catch (e: Exception) {
    }
    var safe_result: Double = risky_divide(10.0, 4.0)
    print(("safe_result=" + str(safe_result)))
    var maybe_value: Int? = null
    print(("maybe_before=" + none_str(maybe_value)))
    maybe_value = 7
    print(("maybe_after=" + none_str(maybe_value)))
    print(("contains_quickfox=" + bool_str(("quickfox" in words))))
    print(("contains_wolf=" + bool_str(("wolf" in words))))
    print(("contains_key=" + bool_str(("quick" in quickfox_map))))
    print("DONE")
}

fun main(args: Array<String>) {
    main()
}