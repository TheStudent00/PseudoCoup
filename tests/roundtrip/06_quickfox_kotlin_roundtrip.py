from typing import List, Dict, Optional, Tuple, Any

def side_effect_marker(tag: Any?) -> Unit:
    print('SIDE_EFFECT:' + tag)
    return true

def short_circuit_and_demo() -> Unit:
    result: Any? = false and side_effect_marker('AND_RHS')
    print('and_short_circuit_result=' + bool_str(result))

def short_circuit_or_demo() -> Unit:
    result: Any? = true or side_effect_marker('OR_RHS')
    print('or_short_circuit_result=' + bool_str(result))

def bool_str(b: Any?) -> Unit:
    if b:
        return 'True'
    elif True:
        return 'False'

def none_str(v: Any?) -> Unit:
    if v === None:
        return 'None'
    return str(v)

def classify_number(n: Any?) -> Unit:
    if n < 0:
        return 'negative'
    elif n == 0:
        return 'zero'
    elif n < 10:
        return 'small'
    elif True:
        return 'large'

def factorial_recursive(n: Any?) -> Unit:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

class Box:
    def __init__(self, value: Any?) -> Any:
        self.history_len = 0

    def update_value(self, new_value: Any?) -> Unit:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> Unit:
        return 'Box(value=' + str(self.value) + ', writes=' + str(self.history_len) + ')'


def risky_divide(a: Any?, b: Any?) -> Unit:
    if b == 0:
        raise IllegalArgumentException('division by zero not allowed')
    return a / b

def main() -> Unit:
    a: Any? = 17
    b: Any? = 5
    add_i: Any? = a + b
    sub_i: Any? = a - b
    mul_i: Any? = a * b
    div_f: Any? = a / b
    div_i: Any? = a / b.toInt()
    mod_i: Any? = a % b
    neg_i: Any? =  - a
    print('add_i=' + str(add_i))
    print('sub_i=' + str(sub_i))
    print('mul_i=' + str(mul_i))
    print('div_f=' + str(div_f))
    print('div_i=' + str(div_i))
    print('mod_i=' + str(mod_i))
    print('neg_i=' + str(neg_i))
    fa: Any? = 9.0
    fb: Any? = 2.0
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
    for n in mutableListOf( - 3, 0, 4, 42):
        print('classify(' + str(n) + ')=' + classify_number(n))
    i: Any? = 0
    total: Any? = 0
    while i < 5:
        total = total + i
        i = i + 1
    print('while_total=' + str(total))
    range_sum: Any? = 0
    for k in 1  until:
        range_sum = range_sum + k
    print('range_sum=' + str(range_sum))
    words: Any? = mutableListOf('quick', 'brown', 'fox')
    joined: Any? = ''
    for w in words:
        joined = joined + w + '-'
    print('joined=' + joined)
    print('factorial5=' + str(factorial_recursive(5)))
    counter: Any? = 0
    counter = counter + 1
    counter = counter + 1
    print('counter=' + str(counter))
    fox_list: Any? = mutableListOf(1, 2, 3)
    fox_list[0] = 100
    fox_list.append(4)
    print('fox_list0=' + str(fox_list[0]))
    print('fox_list_len=' + str(len(fox_list)))
    print('fox_list_last=' + str(fox_list[3]))
    fox_map: Any? = mutableMapOf()
    fox_map['quick'] = 1
    fox_map['brown'] = 2
    fox_map['fox'] = 3
    print('map_get_brown=' + str(fox_map.get('brown')))
    fox_map['fox'] = 30
    print('map_get_fox=' + str(fox_map.get('fox')))
    name: Any? = 'fox'
    speed: Any? = 12
    formatted: Any? = 'The {} runs at {} mph'.format(name, speed)
    print(formatted)
    print('name_len=' + str(len(name)))
    pair: Any? = mutableListOf(name, speed)
    p_name: Any? = pair
    print('pair_name=' + p_name + ' pair_speed=' + str(p_speed))
    box: Any? = Box(10)
    print('box_before=' + box.describe())
    box.update_value(99)
    print('box_after=' + box.describe())
    print('box_value=' + str(box.value))
    try:
        risky_divide(10, 0)
    except Exception:
        pass
    safe_result: Any? = risky_divide(10, 4)
    print('safe_result=' + str(safe_result))
    maybe_value: Any? = None
    print('maybe_before=' + none_str(maybe_value))
    maybe_value = 7
    print('maybe_after=' + none_str(maybe_value))
    print('contains_fox=' + bool_str('fox' in words))
    print('contains_wolf=' + bool_str('wolf' in words))
    print('contains_key=' + bool_str('quick' in fox_map))
    print('DONE')

def main(args: Array<String>) -> Any:
    main()
