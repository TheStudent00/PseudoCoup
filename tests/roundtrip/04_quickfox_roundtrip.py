from typing import List, Dict, Optional, Tuple, Any

def side_effect_marker(tag: str) -> bool:
    print('SIDE_EFFECT:' + tag)
    return True

def short_circuit_and_demo() -> None:
    result: bool = False and side_effect_marker('AND_RHS')
    print('and_short_circuit_result=' + bool_str(result))

def short_circuit_or_demo() -> None:
    result: bool = True or side_effect_marker('OR_RHS')
    print('or_short_circuit_result=' + bool_str(result))

def bool_str(b: bool) -> str:
    if b:
        return 'True'
    elif True:
        return 'False'

def none_str(v: Optional[Any]) -> str:
    if v == None:
        return 'None'
    return str(v)

def classify_number(n: int) -> str:
    if n < 0:
        return 'negative'
    elif n == 0:
        return 'zero'
    elif n < 10:
        return 'small'
    elif True:
        return 'large'

def factorial_recursive(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

class Box:
    value: int
    history_len: int
    def __init__(self, value: int) -> Any:
        self.value = value
        self.history_len = 0

    def update_value(self, new_value: int) -> None:
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self) -> str:
        return 'Box(value=' + str(self) + ', writes=' + str(self) + ')'


def risky_divide(a: float, b: float) -> float:
    if b == 0.0:
        raise ValueError
    return a / b

def main() -> None:
    a: int = 17
    b: int = 5
    add_i: int = a + b
    sub_i: int = a - b
    mul_i: int = a * b
    div_f: float = a / b
    div_i: int = a // b
    mod_i: int = a % b
    neg_i: int =  - a
    print('add_i=' + str(add_i))
    print('sub_i=' + str(sub_i))
    print('mul_i=' + str(mul_i))
    print('div_f=' + str(div_f))
    print('div_i=' + str(div_i))
    print('mod_i=' + str(mod_i))
    print('neg_i=' + str(neg_i))
    fa: float = 9.0
    fb: float = 2.0
    print('float_div=' + str(fa / fb))
    print('float_floordiv=' + str(fa // fb))
    print('eq=' + bool_str(a == b))
    print('ne=' + bool_str(a != b))
    print('lt=' + bool_str(a < b))
    print('le=' + bool_str(a <= b))
    print('gt=' + bool_str(a > b))
    print('ge=' + bool_str(a >= b))
    short_circuit_and_demo()
    short_circuit_or_demo()
    print('not_demo=' + bool_str( not a == b))
    n: int = 0
    for n in [ - 3, 0, 4, 42]:
        print('classify(' + str(n) + ')=' + classify_number(n))
    i: int = 0
    total: int = 0
    while i < 5:
        total = total + i
        i = i + 1
    print('while_total=' + str(total))
    range_sum: int = 0
    k: int = 0
    for k in range(1, 6):
        range_sum = range_sum + k
    print('range_sum=' + str(range_sum))
    words: List[str] = ['quick', 'brown', 'quickfox']
    joined: str = ''
    w: str = ''
    for w in words:
        joined = joined + w + '-'
    print('joined=' + joined)
    print('factorial5=' + str(factorial_recursive))
    counter: int = 0
    counter = counter + 1
    counter = counter + 1
    print('counter=' + str(counter))
    quickfox_list: List[int] = [1, 2, 3]
    quickfox_list[0] = 100
    quickfox_list.append(4)
    print('quickfox_list0=' + str(quickfox_list))
    print('quickfox_list_len=' + str(quickfox_list))
    print('quickfox_list_last=' + str(quickfox_list))
    quickfox_map: Dict[str, int] = {}
    quickfox_map['quick'] = 1
    quickfox_map['brown'] = 2
    quickfox_map['quickfox'] = 3
    print('map_get_brown=' + str(quickfox_map))
    quickfox_map['quickfox'] = 30
    print('map_get_quickfox=' + str(quickfox_map))
    name: str = 'fox'
    speed: int = 12
    formatted: str = 'The {} runs at {} mph'.format(name, speed)
    print(formatted)
    print('name_len=' + str(name))
    pair: List[Any] = [name, speed]
    p_name: str = pair[0]
    p_speed: int = pair[1]
    print('pair_name=' + p_name + ' pair_speed=' + str(p_speed))
    box: Box = Box(10)
    print('box_before=' + box.describe())
    box.update_value(99)
    print('box_after=' + box.describe())
    print('box_value=' + str(box))
    try:
        risky_divide(10.0, 0.0)
    except Exception:
        pass
    safe_result: float = risky_divide(10.0, 4.0)
    print('safe_result=' + str(safe_result))
    maybe_value: Optional[int] = None
    print('maybe_before=' + none_str(maybe_value))
    maybe_value = 7
    print('maybe_after=' + none_str(maybe_value))
    print('contains_quickfox=' + bool_str('quickfox' in words))
    print('contains_wolf=' + bool_str('wolf' in words))
    print('contains_key=' + bool_str('quick' in quickfox_map))
    print('DONE')
