from typing import List, Dict, Optional, Tuple, Any

def side_effect_marker(tag: String) -> Boolean:
    print('SIDE_EFFECT:' + tag)
    return true

def short_circuit_and_demo() -> Unit:
    result: Boolean = false and side_effect_marker('AND_RHS')
    print('and_short_circuit_result=' + bool_str(result))

def short_circuit_or_demo() -> Unit:
    result: Boolean = true or side_effect_marker('OR_RHS')
    print('or_short_circuit_result=' + bool_str(result))

def bool_str(b: Boolean) -> String:
    if b:
        return 'True'
    elif True:
        return 'False'

def none_str(v: Any?) -> String:
    if v === None:
        return 'None'
    return str(v)

def classify_number(n: Int) -> String:
    if n < 0:
        return 'negative'
    elif n == 0:
        return 'zero'
    elif n < 10:
        return 'small'
    elif True:
        return 'large'

def factorial_recursive(n: Int) -> Int:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

class Box:
    value: Int
    history_len: Int
    def __init__(self, value: Int) -> Any:
        self.history_len = 0

    def update_value(self, new_value: Int) -> Unit:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> String:
        return 'Box(value=' + str(self.value) + ', writes=' + str(self.history_len) + ')'


def risky_divide(a: Double, b: Double) -> Double:
    if b == 0.0:
        raise IllegalArgumentException('division by zero not allowed')
    return a / b

def main() -> Unit:
    a: Int = 17
    b: Int = 5
    add_i: Int = a + b
    sub_i: Int = a - b
    mul_i: Int = a * b
    div_f: Double = a / b
    div_i: Int = a / b.toInt()
    mod_i: Int = a % b
    neg_i: Int =  - a
    print('add_i=' + str(add_i))
    print('sub_i=' + str(sub_i))
    print('mul_i=' + str(mul_i))
    print('div_f=' + str(div_f))
    print('div_i=' + str(div_i))
    print('mod_i=' + str(mod_i))
    print('neg_i=' + str(neg_i))
    fa: Double = 9.0
    fb: Double = 2.0
    print('float_div=' + str(fa / fb))
    print('float_floordiv=' + str(fa / fb.toInt()))
    print('eq=' + bool_str(a == b))
    print('ne=' + bool_str(a != b))
    print('lt=' + bool_str(a < b))
    print('le=' + bool_str(a <= b))
    print('gt=' + bool_str(a > b))
    print('ge=' + bool_str(a >= b))
    short_circuit_and_demo()
    short_circuit_or_demo()
    print('not_demo=' + bool_str(not a == b))
    n: Int = 0
    for n in mutableListOf( - 3, 0, 4, 42):
        print('classify(' + str(n) + ')=' + classify_number(n))
    i: Int = 0
    total: Int = 0
    while i < 5:
        total = total + i
        i = i + 1
    print('while_total=' + str(total))
    range_sum: Int = 0
    k: Int = 0
    for k in 1  until:
        range_sum = range_sum + k
    print('range_sum=' + str(range_sum))
    words: MutableList<String>? = mutableListOf('quick', 'brown', 'quickfox')
    joined: String = ''
    w: String = ''
    for w in words:
        joined = joined + w + '-'
    print('joined=' + joined)
    print('factorial5=' + str(factorial_recursive(5)))
    counter: Int = 0
    counter = counter + 1
    counter = counter + 1
    print('counter=' + str(counter))
    quickfox_list: MutableList<Int>? = mutableListOf(1, 2, 3)
    quickfox_list[0] = 100
    quickfox_list.append(4)
    print('quickfox_list0=' + str(quickfox_list[0]))
    print('quickfox_list_len=' + str(len(quickfox_list)))
    print('quickfox_list_last=' + str(quickfox_list[3]))
    quickfox_map: MutableMap<String, Int>? = mutableMapOf()
    quickfox_map['quick'] = 1
    quickfox_map['brown'] = 2
    quickfox_map['quickfox'] = 3
    print('map_get_brown=' + str(quickfox_map.get('brown')))
    quickfox_map['quickfox'] = 30
    print('map_get_quickfox=' + str(quickfox_map.get('quickfox')))
    name: String = 'fox'
    speed: Int = 12
    formatted: String = 'The {} runs at {} mph'.format(name, speed)
    print(formatted)
    print('name_len=' + str(len(name)))
    pair: MutableList<Any?>? = mutableListOf(name, speed)
    p_name: String = pair[0]
    p_speed: Int = pair[1]
    print('pair_name=' + p_name + ' pair_speed=' + str(p_speed))
    box: Box = Box(10)
    print('box_before=' + box.describe())
    box.update_value(99)
    print('box_after=' + box.describe())
    print('box_value=' + str(box.value))
    try:
        risky_divide(10.0, 0.0)
    except Exception:
        pass
    safe_result: Double = risky_divide(10.0, 4.0)
    print('safe_result=' + str(safe_result))
    maybe_value: Int? = None
    print('maybe_before=' + none_str(maybe_value))
    maybe_value = 7
    print('maybe_after=' + none_str(maybe_value))
    print('contains_quickfox=' + bool_str('quickfox' in words))
    print('contains_wolf=' + bool_str('wolf' in words))
    print('contains_key=' + bool_str('quick' in quickfox_map))
    print('DONE')

def main(args: Array<String>) -> Any:
    main()
