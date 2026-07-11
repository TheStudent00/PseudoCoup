from typing import List, Dict, Optional, Tuple, Any

class Box:
    value: int
    history_len: int
    def __init__(self, value: int) -> void:
        pass.history_len = 0

    def update_value(self, new_value: int) -> void:
        pass.value = new_value
        pass.history_len = pass.history_len + 1

    def describe(self) -> string:
        return 'Box(value=' + builtins_py.str(pass.value) + ', writes=' + builtins_py.str(pass.history_len) + ')'


class Program:
    def side_effect_marker(self, tag: string) -> bool:
        builtins_py.print('SIDE_EFFECT:' + tag)
        return True

    def short_circuit_and_demo(self) -> void:
        result: bool = False and side_effect_marker('AND_RHS')
        builtins_py.print('and_short_circuit_result=' + bool_str(result))

    def short_circuit_or_demo(self) -> void:
        result: bool = True or side_effect_marker('OR_RHS')
        builtins_py.print('or_short_circuit_result=' + bool_str(result))

    def bool_str(self, b: bool) -> string:
        if b:
            return 'True'
        elif True:
            return 'False'

    def none_str(self, v: object) -> string:
        if v == None:
            return 'None'
        return builtins_py.str(v)

    def classify_number(self, n: int) -> string:
        if n < 0:
            return 'negative'
        elif n == 0:
            return 'zero'
        elif n < 10:
            return 'small'
        elif True:
            return 'large'

    def factorial_recursive(self, n: int) -> int:
        if n <= 1:
            return 1
        return n * factorial_recursive(n - 1)

    def risky_divide(self, a: double, b: double) -> double:
        if b == 0.0:
            throw(ArgumentException('division by zero not allowed'))
        return a / b

    def main(self) -> void:
        a: int = 17
        b: int = 5
        add_i: int = a + b
        sub_i: int = a - b
        mul_i: int = a * b
        div_f: double = a / b
        div_i: int
        mod_i: int = a % b
        neg_i: int
        builtins_py.print('add_i=' + builtins_py.str(add_i))
        builtins_py.print('sub_i=' + builtins_py.str(sub_i))
        builtins_py.print('mul_i=' + builtins_py.str(mul_i))
        builtins_py.print('div_f=' + builtins_py.str(div_f))
        builtins_py.print('div_i=' + builtins_py.str(div_i))
        builtins_py.print('mod_i=' + builtins_py.str(mod_i))
        builtins_py.print('neg_i=' + builtins_py.str(neg_i))
        fa: double = 9.0
        fb: double = 2.0
        builtins_py.print('float_div=' + builtins_py.str(fa / fb))
        builtins_py.print('float_floordiv=' + builtins_py.str(pass))
        builtins_py.print('eq=' + bool_str(a == b))
        builtins_py.print('ne=' + bool_str(a != b))
        builtins_py.print('lt=' + bool_str(a < b))
        builtins_py.print('le=' + bool_str(a <= b))
        builtins_py.print('gt=' + bool_str(a > b))
        builtins_py.print('ge=' + bool_str(a >= b))
        short_circuit_and_demo()
        short_circuit_or_demo()
        builtins_py.print('not_demo=' + bool_str(pass))
        n: int = 0
        for n in List<object>():
            builtins_py.print('classify(' + builtins_py.str(n) + ')=' + classify_number(n))
        i: int = 0
        total: int = 0
        builtins_py.print('while_total=' + builtins_py.str(total))
        range_sum: int = 0
        k: int = 0
        for k in builtins_py.range(1, 6):
            range_sum = range_sum + k
        builtins_py.print('range_sum=' + builtins_py.str(range_sum))
        words: List<string> = List<object>()
        joined: string = ''
        w: string = ''
        for w in words:
            joined = joined + w + '-'
        builtins_py.print('joined=' + joined)
        builtins_py.print('factorial5=' + builtins_py.str(factorial_recursive(5)))
        counter: int = 0
        counter = counter + 1
        counter = counter + 1
        builtins_py.print('counter=' + builtins_py.str(counter))
        quickfox_list: List<int> = List<object>()
        pass = 100
        quickfox_list.append(4)
        builtins_py.print('quickfox_list0=' + builtins_py.str(pass))
        builtins_py.print('quickfox_list_len=' + builtins_py.str(builtins_py.len(quickfox_list)))
        builtins_py.print('quickfox_list_last=' + builtins_py.str(pass))
        quickfox_map: Dictionary<string, int> = Dictionary<object, object>()
        pass = 1
        pass = 2
        pass = 3
        builtins_py.print('map_get_brown=' + builtins_py.str(quickfox_map.get('brown')))
        pass = 30
        builtins_py.print('map_get_quickfox=' + builtins_py.str(quickfox_map.get('quickfox')))
        name: string = 'fox'
        speed: int = 12
        formatted: string = 'The {} runs at {} mph'.format(name, speed)
        builtins_py.print(formatted)
        builtins_py.print('name_len=' + builtins_py.str(builtins_py.len(name)))
        pair: List<object> = List<object>()
        p_name: string
        p_speed: int
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
        safe_result: double = risky_divide(10.0, 4.0)
        builtins_py.print('safe_result=' + builtins_py.str(safe_result))
        maybe_value: int? = None
        builtins_py.print('maybe_before=' + none_str(maybe_value))
        maybe_value = 7
        builtins_py.print('maybe_after=' + none_str(maybe_value))
        builtins_py.print('contains_quickfox=' + bool_str(words.Contains('quickfox')))
        builtins_py.print('contains_wolf=' + bool_str(words.Contains('wolf')))
        builtins_py.print('contains_key=' + bool_str(quickfox_map.Contains('quick')))
        builtins_py.print('DONE')

    def Main(self, args: string[]) -> void:
        main()

