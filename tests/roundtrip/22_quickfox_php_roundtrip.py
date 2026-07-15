from typing import List, Dict, Optional, Tuple, Any

def side_effect_marker(tag: Any) -> Any:
    print('SIDE_EFFECT:' + tag)
    return True

def short_circuit_and_demo() -> Any:
    result: Any = False and side_effect_marker('AND_RHS')
    print('and_short_circuit_result=' + bool_str(result))

def short_circuit_or_demo() -> Any:
    result: Any = True or side_effect_marker('OR_RHS')
    print('or_short_circuit_result=' + bool_str(result))

def bool_str(b: Any) -> Any:
    if b:
        return 'True'
    elif True:
        return 'False'

def none_str(v: Any) -> Any:
    if v === None:
        return 'None'
    return builtins_py_str(v)

def classify_number(n: Any) -> Any:
    if n < 0:
        return 'negative'

def factorial_recursive(n: Any) -> Any:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

class Box:
    def __init__(self, value: Any) -> Box:
        self.value = value
        self.history_len = 0

    def update_value(self, new_value: Any) -> Any:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> Any:
        return 'Box(value=' + builtins_py_str(self.value) + ', writes=' + builtins_py_str(self.history_len) + ')'


def risky_divide(a: Any, b: Any) -> Any:
    if b == 0:
        pass
    return a / b

def main() -> Any:
    a: Any = 17
    b: Any = 5
    add_i: Any = a + b
    sub_i: Any = a - b
    mul_i: Any = a * b
    div_f: Any = a / b
    div_i: Any = intdiv(a, b)
    mod_i: Any = a % b
    neg_i: Any
    print('add_i=' + builtins_py_str(add_i))
    print('sub_i=' + builtins_py_str(sub_i))
    print('mul_i=' + builtins_py_str(mul_i))
    print('div_f=' + builtins_py_str(div_f))
    print('div_i=' + builtins_py_str(div_i))
    print('mod_i=' + builtins_py_str(mod_i))
    print('neg_i=' + builtins_py_str(neg_i))
    fa: Any = 9.0
    fb: Any = 2.0
    print('float_div=' + builtins_py_str(fa / fb))
    print('float_floordiv=' + builtins_py_str(intdiv(fa, fb)))
    print('eq=' + bool_str(a == b))
    print('ne=' + bool_str(a != b))
    print('lt=' + bool_str(a < b))
    print('le=' + bool_str(a <= b))
    print('gt=' + bool_str(a > b))
    print('ge=' + bool_str(a >= b))
    short_circuit_and_demo()
    short_circuit_or_demo()
    print('not_demo=' + bool_str(pass))
    i: Any = 0
    total: Any = 0
    while i < 5:
        total = total + i
        i = i + 1
    print('while_total=' + builtins_py_str(total))
    range_sum: Any = 0
    print('range_sum=' + builtins_py_str(range_sum))
    words: Any
    joined: Any = ''
    print('joined=' + joined)
    print('factorial5=' + builtins_py_str(factorial_recursive(5)))
    counter: Any = 0
    counter = counter + 1
    counter = counter + 1
    print('counter=' + builtins_py_str(counter))
    fox_list: Any
    pass = 100
    print('fox_list0=' + builtins_py_str(pass))
    print('fox_list_len=' + builtins_py_str(builtins_py_len(fox_list)))
    print('fox_list_last=' + builtins_py_str(pass))
    fox_map: Any = builtins_py_hashmap()
    pass = 1
    pass = 2
    pass = 3
    print('map_get_brown=' + builtins_py_str(pass))
    pass = 30
    print('map_get_fox=' + builtins_py_str(pass))
    name: Any = 'fox'
    speed: Any = 12
    formatted: Any
    print(formatted)
    print('name_len=' + builtins_py_str(builtins_py_len(name)))
    pair: Any
    p_name: Any = pair
    print('pair_name=' + p_name + ' pair_speed=' + builtins_py_str(p_speed))
    box: Any = Box(10)
    print('box_before=' + pass)
    print('box_after=' + pass)
    print('box_value=' + builtins_py_str(box.value))
    try:
        risky_divide(10, 0)
    except Exception:
        pass
    safe_result: Any = risky_divide(10, 4)
    print('safe_result=' + builtins_py_str(safe_result))
    maybe_value: Any = None
    print('maybe_before=' + none_str(maybe_value))
    maybe_value = 7
    print('maybe_after=' + none_str(maybe_value))
    print('contains_fox=' + bool_str(pass))
    print('contains_wolf=' + bool_str(pass))
    print('contains_key=' + bool_str(pass))
    print('DONE')

if __name__ == '__main__':
    main()