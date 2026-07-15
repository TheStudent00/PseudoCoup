from typing import List, Dict, Optional, Tuple, Any

class Box:
    def __init__(self, value: object) -> void:
        pass.history_len = 0

    def update_value(self, new_value: object) -> object:
        pass.value = new_value
        pass.history_len = pass.history_len + 1

    def describe(self) -> object:
        return 'Box(value=' + builtins_py.str(pass.value) + ', writes=' + builtins_py.str(pass.history_len) + ')'


class Program:
    def side_effect_marker(self, tag: object) -> void:
        builtins_py.print('SIDE_EFFECT:' + tag)
        return True

    def short_circuit_and_demo(self) -> void:
        result: object = False and side_effect_marker('AND_RHS')
        builtins_py.print('and_short_circuit_result=' + bool_str(result))

    def short_circuit_or_demo(self) -> void:
        result: object = True or side_effect_marker('OR_RHS')
        builtins_py.print('or_short_circuit_result=' + bool_str(result))

    def bool_str(self, b: object) -> void:
        if b:
            return 'True'
        elif True:
            return 'False'

    def none_str(self, v: object) -> void:
        if v == None:
            return 'None'
        return builtins_py.str(v)

    def classify_number(self, n: object) -> void:
        if n < 0:
            return 'negative'
        elif n == 0:
            return 'zero'
        elif n < 10:
            return 'small'
        elif True:
            return 'large'

    def factorial_recursive(self, n: object) -> void:
        if n <= 1:
            return 1
        return n * factorial_recursive(n - 1)

    def risky_divide(self, a: object, b: object) -> void:
        if b == 0:
            throw(ArgumentException('division by zero not allowed'))
        return a / b

    def main(self) -> void:
        a: object = 17
        b: object = 5
        add_i: object = a + b
        sub_i: object = a - b
        mul_i: object = a * b
        div_f: object = a / b
        div_i: object
        mod_i: object = a % b
        neg_i: object
        builtins_py.print('add_i=' + builtins_py.str(add_i))
        builtins_py.print('sub_i=' + builtins_py.str(sub_i))
        builtins_py.print('mul_i=' + builtins_py.str(mul_i))
        builtins_py.print('div_f=' + builtins_py.str(div_f))
        builtins_py.print('div_i=' + builtins_py.str(div_i))
        builtins_py.print('mod_i=' + builtins_py.str(mod_i))
        builtins_py.print('neg_i=' + builtins_py.str(neg_i))
        fa: object = 9.0
        fb: object = 2.0
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
        for n in List<object>():
            builtins_py.print('classify(' + builtins_py.str(n) + ')=' + classify_number(n))
        i: object = 0
        total: object = 0
        builtins_py.print('while_total=' + builtins_py.str(total))
        range_sum: object = 0
        for k in builtins_py.range(1, 6):
            range_sum = range_sum + k
        builtins_py.print('range_sum=' + builtins_py.str(range_sum))
        words: object = List<object>()
        joined: object = ''
        for w in words:
            joined = joined + w + '-'
        builtins_py.print('joined=' + joined)
        builtins_py.print('factorial5=' + builtins_py.str(factorial_recursive(5)))
        counter: object = 0
        counter = counter + 1
        counter = counter + 1
        builtins_py.print('counter=' + builtins_py.str(counter))
        fox_list: object = List<object>()
        pass = 100
        fox_list.append(4)
        builtins_py.print('fox_list0=' + builtins_py.str(pass))
        builtins_py.print('fox_list_len=' + builtins_py.str(builtins_py.len(fox_list)))
        builtins_py.print('fox_list_last=' + builtins_py.str(pass))
        fox_map: object = Dictionary<object, object>()
        pass = 1
        pass = 2
        pass = 3
        builtins_py.print('map_get_brown=' + builtins_py.str(fox_map.get('brown')))
        pass = 30
        builtins_py.print('map_get_fox=' + builtins_py.str(fox_map.get('fox')))
        name: object = 'fox'
        speed: object = 12
        formatted: object = 'The {} runs at {} mph'.format(name, speed)
        builtins_py.print(formatted)
        builtins_py.print('name_len=' + builtins_py.str(builtins_py.len(name)))
        pair: object = List<object>()
        p_name: object = pair
        builtins_py.print('pair_name=' + p_name + ' pair_speed=' + builtins_py.str(p_speed))
        box: object = Box(10)
        builtins_py.print('box_before=' + box.describe())
        box.update_value(99)
        builtins_py.print('box_after=' + box.describe())
        builtins_py.print('box_value=' + builtins_py.str(box.value))
        try:
            risky_divide(10, 0)
        except Exception:
            pass
        safe_result: object = risky_divide(10, 4)
        builtins_py.print('safe_result=' + builtins_py.str(safe_result))
        maybe_value: object = None
        builtins_py.print('maybe_before=' + none_str(maybe_value))
        maybe_value = 7
        builtins_py.print('maybe_after=' + none_str(maybe_value))
        builtins_py.print('contains_fox=' + bool_str(words.Contains('fox')))
        builtins_py.print('contains_wolf=' + bool_str(words.Contains('wolf')))
        builtins_py.print('contains_key=' + bool_str(fox_map.Contains('quick')))
        builtins_py.print('DONE')

    def Main(self, args: string[]) -> void:
        main()

