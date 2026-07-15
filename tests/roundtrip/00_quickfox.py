"""quick-fox: a small deterministic program exercising a broad set of
language operations, for cross-language (Python vs Kotlin) IR comparison.
No imports beyond what is unavoidable (none needed here)."""


def side_effect_marker(tag):
    print("SIDE_EFFECT:" + tag)
    return True


def short_circuit_and_demo():
    # right side must NOT run because left side is False
    result = False and side_effect_marker("AND_RHS")
    print("and_short_circuit_result=" + bool_str(result))


def short_circuit_or_demo():
    # right side must NOT run because left side is True
    result = True or side_effect_marker("OR_RHS")
    print("or_short_circuit_result=" + bool_str(result))


def bool_str(b):
    if b:
        return "True"
    else:
        return "False"


def none_str(v):
    if v is None:
        return "None"
    return str(v)


def classify_number(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    elif n < 10:
        return "small"
    else:
        return "large"


def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)


class Box:
    def __init__(self, value):
        self.value = value
        self.history_len = 0

    def update_value(self, new_value):
        self.value = new_value
        self.history_len = self.history_len + 1

    def describe(self):
        return "Box(value=" + str(self.value) + ", writes=" + str(self.history_len) + ")"


def risky_divide(a, b):
    if b == 0:
        raise ValueError("division by zero not allowed")
    return a / b


def main():
    # integer & float arithmetic
    a = 17
    b = 5
    add_i = a + b
    sub_i = a - b
    mul_i = a * b
    div_f = a / b
    div_i = a // b
    mod_i = a % b
    neg_i = -a

    print("add_i=" + str(add_i))
    print("sub_i=" + str(sub_i))
    print("mul_i=" + str(mul_i))
    print("div_f=" + str(div_f))
    print("div_i=" + str(div_i))
    print("mod_i=" + str(mod_i))
    print("neg_i=" + str(neg_i))

    fa = 9.0
    fb = 2.0
    print("float_div=" + str(fa / fb))
    print("float_floordiv=" + str(fa // fb))

    # comparisons
    print("eq=" + bool_str(a == b))
    print("ne=" + bool_str(a != b))
    print("lt=" + bool_str(a < b))
    print("le=" + bool_str(a <= b))
    print("gt=" + bool_str(a > b))
    print("ge=" + bool_str(a >= b))

    # boolean logic with real short-circuit
    short_circuit_and_demo()
    short_circuit_or_demo()
    print("not_demo=" + bool_str(not (a == b)))

    # if / elif / else
    for n in [-3, 0, 4, 42]:
        print("classify(" + str(n) + ")=" + classify_number(n))

    # while loop
    i = 0
    total = 0
    while i < 5:
        total = total + i
        i = i + 1
    print("while_total=" + str(total))

    # for loop over range and over list
    range_sum = 0
    for k in range(1, 6):
        range_sum = range_sum + k
    print("range_sum=" + str(range_sum))

    words = ["quick", "brown", "fox"]
    joined = ""
    for w in words:
        joined = joined + w + "-"
    print("joined=" + joined)

    # function def/call/return + recursion
    print("factorial5=" + str(factorial_recursive(5)))

    # local variable assignment/reassignment
    counter = 0
    counter = counter + 1
    counter = counter + 1
    print("counter=" + str(counter))

    # list construction/indexing/mutation/append
    fox_list = [1, 2, 3]
    fox_list[0] = 100
    fox_list.append(4)
    print("fox_list0=" + str(fox_list[0]))
    print("fox_list_len=" + str(len(fox_list)))
    print("fox_list_last=" + str(fox_list[3]))

    # dict/map construction/get/put
    fox_map = {}
    fox_map["quick"] = 1
    fox_map["brown"] = 2
    fox_map["fox"] = 3
    print("map_get_brown=" + str(fox_map.get("brown")))
    fox_map["fox"] = 30
    print("map_get_fox=" + str(fox_map.get("fox")))

    # string concatenation + interpolation-or-format + length
    name = "fox"
    speed = 12
    formatted = "The {} runs at {} mph".format(name, speed)
    print(formatted)
    print("name_len=" + str(len(name)))

    # tuple construction + destructuring
    pair = (name, speed)
    p_name, p_speed = pair
    print("pair_name=" + p_name + " pair_speed=" + str(p_speed))

    # class with constructor, attribute read/write, method call
    box = Box(10)
    print("box_before=" + box.describe())
    box.update_value(99)
    print("box_after=" + box.describe())
    print("box_value=" + str(box.value))

    # exception raise + try/catch
    try:
        risky_divide(10, 0)
    except ValueError as e:
        print("caught=" + str(e))

    safe_result = risky_divide(10, 4)
    print("safe_result=" + str(safe_result))

    # null/None check
    maybe_value = None
    print("maybe_before=" + none_str(maybe_value))
    maybe_value = 7
    print("maybe_after=" + none_str(maybe_value))

    # 'in' / contains membership test
    print("contains_fox=" + bool_str("fox" in words))
    print("contains_wolf=" + bool_str("wolf" in words))
    print("contains_key=" + bool_str("quick" in fox_map))

    print("DONE")


if __name__ == "__main__":
    main()
