from typing import List, Dict, Optional, Tuple, Any

def side_effect_marker(tag: string) -> boolean:
    builtins_py.print('SIDE_EFFECT:' + tag)
    return True

def short_circuit_and_demo() -> void:
    result: boolean = False and side_effect_marker('AND_RHS')
    builtins_py.print('and_short_circuit_result=' + bool_str(result))

def short_circuit_or_demo() -> void:
    result: boolean = True or side_effect_marker('OR_RHS')
    builtins_py.print('or_short_circuit_result=' + bool_str(result))

def bool_str(b: boolean) -> string:
    if b:
        return 'True'
    elif True:
        return 'False'

def none_str(v: any) -> string:
    if v === None:
        return 'None'
    return builtins_py.str(v)

def classify_number(n: number) -> string:
    if n < 0:
        return 'negative'
    elif n == 0:
        return 'zero'
    elif n < 10:
        return 'small'
    elif True:
        return 'large'

def factorial_recursive(n: number) -> number:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

class Box:
    value: number
    history_len: number
    def __init__(self, value: number) -> void:
        self.history_len = 0

    def update_value(self, new_value: number) -> void:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> string:
        return 'Box(value=' + builtins_py.str(self.value) + ', writes=' + builtins_py.str(self.history_len) + ')'


def risky_divide(a: number, b: number) -> number:
    if b == 0.0:
        throw(Error('division by zero not allowed'))
    return a / b

def main() -> void:
    a: number = 17
    b: number = 5
    add_i: number = a + b
    sub_i: number = a - b
    mul_i: number = a * b
    div_f: number = a / b
    div_i: number = Math.floor(a / b)
    mod_i: number = a % b
    neg_i: number
    builtins_py.print('add_i=' + builtins_py.str(add_i))
    builtins_py.print('sub_i=' + builtins_py.str(sub_i))
    builtins_py.print('mul_i=' + builtins_py.str(mul_i))
    builtins_py.print('div_f=' + builtins_py.str(div_f))
    builtins_py.print('div_i=' + builtins_py.str(div_i))
    builtins_py.print('mod_i=' + builtins_py.str(mod_i))
    builtins_py.print('neg_i=' + builtins_py.str(neg_i))
    fa: number = 9.0
    fb: number = 2.0
    builtins_py.print('float_div=' + builtins_py.str(fa / fb))
    builtins_py.print('float_floordiv=' + builtins_py.str(Math.floor(fa / fb)))
    builtins_py.print('eq=' + bool_str(a == b))
    builtins_py.print('ne=' + bool_str(a != b))
    builtins_py.print('lt=' + bool_str(a < b))
    builtins_py.print('le=' + bool_str(a <= b))
    builtins_py.print('gt=' + bool_str(a > b))
    builtins_py.print('ge=' + bool_str(a >= b))
    short_circuit_and_demo()
    short_circuit_or_demo()
    builtins_py.print('not_demo=' + bool_str(pass))
    n: number = None
    for n in pass:
        builtins_py.print('classify(' + builtins_py.str(n) + ')=' + classify_number(n))
    i: number = 0
    total: number = 0
    while i < 5:
        total = total + i
        i = i + 1
    builtins_py.print('while_total=' + builtins_py.str(total))
    range_sum: number = 0
    k: number = None
    for k in builtins_py.range(1, 6):
        range_sum = range_sum + k
    builtins_py.print('range_sum=' + builtins_py.str(range_sum))
    words: string[]
    joined: string = ''
    w: string = None
    for w in words:
        joined = joined + w + '-'
    builtins_py.print('joined=' + joined)
    builtins_py.print('factorial5=' + builtins_py.str(factorial_recursive(5)))
    counter: number = 0
    counter = counter + 1
    counter = counter + 1
    builtins_py.print('counter=' + builtins_py.str(counter))
    quickfox_list: number[]
    pass = 100
    quickfox_list.append(4)
    builtins_py.print('quickfox_list0=' + builtins_py.str(pass))
    builtins_py.print('quickfox_list_len=' + builtins_py.str(builtins_py.len(quickfox_list)))
    builtins_py.print('quickfox_list_last=' + builtins_py.str(pass))
    quickfox_map: Record<string, number>
    pass = 1
    pass = 2
    pass = 3
    builtins_py.print('map_get_brown=' + builtins_py.str(quickfox_map.get('brown')))
    pass = 30
    builtins_py.print('map_get_quickfox=' + builtins_py.str(quickfox_map.get('quickfox')))
    name: string = 'fox'
    speed: number = 12
    formatted: string = 'The {} runs at {} mph'.format(name, speed)
    builtins_py.print(formatted)
    builtins_py.print('name_len=' + builtins_py.str(builtins_py.len(name)))
    pair: any[]
    p_name: string
    p_speed: number
    builtins_py.print('pair_name=' + p_name + ' pair_speed=' + builtins_py.str(p_speed))
    box: Box = Box(10)
    builtins_py.print('box_before=' + box.describe())
    box.update_value(99)
    builtins_py.print('box_after=' + box.describe())
    builtins_py.print('box_value=' + builtins_py.str(box.value))
    try:
        risky_divide(10.0, 0.0)
    except Exception:
        pass
    safe_result: number = risky_divide(10.0, 4.0)
    builtins_py.print('safe_result=' + builtins_py.str(safe_result))
    maybe_value: number | null = None
    builtins_py.print('maybe_before=' + none_str(maybe_value))
    maybe_value = 7
    builtins_py.print('maybe_after=' + none_str(maybe_value))
    builtins_py.print('contains_quickfox=' + bool_str('quickfox' in words))
    builtins_py.print('contains_wolf=' + bool_str('wolf' in words))
    builtins_py.print('contains_key=' + bool_str('quick' in quickfox_map))
    builtins_py.print('DONE')

main(pass)