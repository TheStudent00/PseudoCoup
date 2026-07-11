from typing import List, Dict, Optional, Tuple, Any

class Box:
    value: int
    history_len: int
    def __init__(self, value: int) -> void:
        self.history_len = 0

    def update_value(self, new_value: int) -> void:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> String:
        return 'Box(value=' + builtins_py.str(self.value) + ', writes=' + builtins_py.str(self.history_len) + ')'


class Main:
    def side_effect_marker(self, tag: String) -> boolean:
        builtins_py.print('SIDE_EFFECT:' + tag)
        return

    def short_circuit_and_demo(self) -> void:
        result: boolean = pass and side_effect_marker('AND_RHS')
        builtins_py.print('and_short_circuit_result=' + bool_str(result))

    def short_circuit_or_demo(self) -> void:
        result: boolean = pass or side_effect_marker('OR_RHS')
        builtins_py.print('or_short_circuit_result=' + bool_str(result))

    def bool_str(self, b: boolean) -> String:
        if b:
            return 'True'
        elif True:
            return 'False'

    def none_str(self, v: Object) -> String:
        if v == None:
            return 'None'
        return builtins_py.str(v)

    def classify_number(self, n: int) -> String:
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
            throw(IllegalArgumentException('division by zero not allowed'))
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
        builtins_py.print('classify(' + builtins_py.str(n) + ')=' + classify_number(n))
        while i: Any = 0:
            range_sum: Any = range_sum + k
        builtins_py.print('range_sum=' + builtins_py.str(range_sum))
        words: ArrayList<String> = ArrayList<>(Arrays.asList('quick', 'brown', 'quickfox'))
        joined: String = ''
        w: String = ''

