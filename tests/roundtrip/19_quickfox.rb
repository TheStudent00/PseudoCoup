require_relative 'builtins_py'

def side_effect_marker(tag)
  puts(("SIDE_EFFECT:" + tag))
  return true
end
def short_circuit_and_demo
  result = (false && side_effect_marker("AND_RHS"))
  puts(("and_short_circuit_result=" + bool_str(result)))
end
def short_circuit_or_demo
  result = (true || side_effect_marker("OR_RHS"))
  puts(("or_short_circuit_result=" + bool_str(result)))
end
def bool_str(b)
  if b
    return "True"
  else
    return "False"
  end
end
def none_str(v)
  if (v == null)
    return "None"
  end
  return builtins_py.str(v)
end
def classify_number(n)
  if (n < 0)
    return "negative"
  elsif (n == 0)
    return "zero"
  elsif (n < 10)
    return "small"
  else
    return "large"
  end
end
def factorial_recursive(n)
  if (n <= 1)
    return 1
  end
  return (n * factorial_recursive((n - 1)))
end
class Box
  def initialize(value)
    @value = value
    @history_len = 0
  end
  def update_value(new_value)
    @value = new_value
    @history_len = (@history_len + 1)
  end
  def describe
    return (((("Box(value=" + builtins_py.str(@value)) + ", writes=") + builtins_py.str(@history_len)) + ")")
  end
end
def risky_divide(a, b)
  if (b == 0.0)
    raise StandardError.new(ValueError("division by zero not allowed"))
  end
  return (a / b)
end
def main
  a = 17
  b = 5
  add_i = (a + b)
  sub_i = (a - b)
  mul_i = (a * b)
  div_f = (a / b)
  div_i = (a / b)
  mod_i = (a % b)
  neg_i = -(a)
  puts(("add_i=" + builtins_py.str(add_i)))
  puts(("sub_i=" + builtins_py.str(sub_i)))
  puts(("mul_i=" + builtins_py.str(mul_i)))
  puts(("div_f=" + builtins_py.str(div_f)))
  puts(("div_i=" + builtins_py.str(div_i)))
  puts(("mod_i=" + builtins_py.str(mod_i)))
  puts(("neg_i=" + builtins_py.str(neg_i)))
  fa = 9.0
  fb = 2.0
  puts(("float_div=" + builtins_py.str((fa / fb))))
  puts(("float_floordiv=" + builtins_py.str((fa / fb))))
  puts(("eq=" + bool_str((a == b))))
  puts(("ne=" + bool_str((a != b))))
  puts(("lt=" + bool_str((a < b))))
  puts(("le=" + bool_str((a <= b))))
  puts(("gt=" + bool_str((a > b))))
  puts(("ge=" + bool_str((a >= b))))
  short_circuit_and_demo()
  short_circuit_or_demo()
  puts(("not_demo=" + bool_str(!((a == b)))))
  n = nil
  for n in [-(3), 0, 4, 42]
    puts(((("classify(" + builtins_py.str(n)) + ")=") + classify_number(n)))
  end
  i = 0
  total = 0
  while (i < 5)
    total = (total + i)
    i = (i + 1)
  end
  puts(("while_total=" + builtins_py.str(total)))
  range_sum = 0
  k = nil
  for k in builtins_py.range(1, 6)
    range_sum = (range_sum + k)
  end
  puts(("range_sum=" + builtins_py.str(range_sum)))
  words = ["quick", "brown", "quickfox"]
  joined = ""
  w = nil
  for w in words
    joined = ((joined + w) + "-")
  end
  puts(("joined=" + joined))
  puts(("factorial5=" + builtins_py.str(factorial_recursive(5))))
  counter = 0
  counter = (counter + 1)
  counter = (counter + 1)
  puts(("counter=" + builtins_py.str(counter)))
  quickfox_list = [1, 2, 3]
  quickfox_list[0] = 100
  quickfox_list.append(4)
  puts(("quickfox_list0=" + builtins_py.str(quickfox_list[0])))
  puts(("quickfox_list_len=" + builtins_py.str(builtins_py.len(quickfox_list))))
  puts(("quickfox_list_last=" + builtins_py.str(quickfox_list[3])))
  quickfox_map = builtins_py.hashmap()
  quickfox_map["quick"] = 1
  quickfox_map["brown"] = 2
  quickfox_map["quickfox"] = 3
  puts(("map_get_brown=" + builtins_py.str(quickfox_map.get("brown"))))
  quickfox_map["quickfox"] = 30
  puts(("map_get_quickfox=" + builtins_py.str(quickfox_map.get("quickfox"))))
  name = "fox"
  speed = 12
  formatted = "The {} runs at {} mph".format(name, speed)
  puts(formatted)
  puts(("name_len=" + builtins_py.str(builtins_py.len(name))))
  pair = [name, speed]
  p_name = pair[0]
  p_speed = pair[1]
  puts(((("pair_name=" + p_name) + " pair_speed=") + builtins_py.str(p_speed)))
  box = Box(10)
  puts(("box_before=" + box.describe()))
  box.update_value(99)
  puts(("box_after=" + box.describe()))
  puts(("box_value=" + builtins_py.str(box.value)))
  begin
    risky_divide(10.0, 0.0)
  rescue StandardError => e
  end
  safe_result = risky_divide(10.0, 4.0)
  puts(("safe_result=" + builtins_py.str(safe_result)))
  maybe_value = null
  puts(("maybe_before=" + none_str(maybe_value)))
  maybe_value = 7
  puts(("maybe_after=" + none_str(maybe_value)))
  puts(("contains_quickfox=" + bool_str(("quickfox" in words))))
  puts(("contains_wolf=" + bool_str(("wolf" in words))))
  puts(("contains_key=" + bool_str(("quick" in quickfox_map))))
  puts("DONE")
end
if (__name__ == "__main__")
  main()
end