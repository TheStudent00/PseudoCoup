package main

import (
	"fmt"
	"roundtrip/builtins_py"
)

func Contains[T comparable](slice []T, item T) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func Range(start, end int) []int {
	var r []int
	for i := start; i < end; i++ {
		r = append(r, i)
	}
	return r
}

func Ptr[T any](v T) *T {
	return &v
}

func side_effect_marker(tag interface{}) interface{} {
	fmt.Println(builtins_py.String("SIDE_EFFECT:") + tag)
	return true
	return nil
}
func short_circuit_and_demo() interface{} {
	result := false && side_effect_marker(builtins_py.String("AND_RHS"))
	fmt.Println(builtins_py.String("and_short_circuit_result=") + bool_str(result))
	return nil
}
func short_circuit_or_demo() interface{} {
	result := true || side_effect_marker(builtins_py.String("OR_RHS"))
	fmt.Println(builtins_py.String("or_short_circuit_result=") + bool_str(result))
	return nil
}
func bool_str(b interface{}) interface{} {
		if b {
		return builtins_py.String("True")
	} else {
		return builtins_py.String("False")
	}
	return nil
}
func none_str(v interface{}) interface{} {
		if v == nil {
		return builtins_py.String("None")
	}
	return builtins_py.String(fmt.Sprintf("%v", v))
	return nil
}
func classify_number(n interface{}) interface{} {
		if n < 0 {
		return builtins_py.String("negative")
	} else if n == 0 {
		return builtins_py.String("zero")
	} else if n < 10 {
		return builtins_py.String("small")
	} else {
		return builtins_py.String("large")
	}
	return nil
}
func factorial_recursive(n interface{}) interface{} {
		if n <= 1 {
		return 1
	}
	return n * factorial_recursive(n - 1)
	return nil
}
type Box struct {

}

func NewBox(value interface{}) *Box {
	this := &Box{}
	this.value = value
	this.history_len = 0
	return this
}

func (this *Box) Update_value(new_value interface{}) interface{} {
	this.value = new_value
	this.history_len = this.history_len + 1
	return nil
}

func (this *Box) Describe() interface{} {
	return builtins_py.String("Box(value=") + builtins_py.String(fmt.Sprintf("%v", this.value)) + builtins_py.String(", writes=") + builtins_py.String(fmt.Sprintf("%v", this.history_len)) + builtins_py.String(")")
	return nil
}
func risky_divide(a interface{}, b interface{}) interface{} {
		if b == 0 {
		panic(builtins_py.String("division by zero not allowed"))
	}
	return (float64(a) / float64(b))
	return nil
}
func main() interface{} {
	a := 17
	b := 5
	add_i := a + b
	sub_i := a - b
	mul_i := a * b
	div_f := (float64(a) / float64(b))
	div_i := (a / b)
	mod_i := a % b
	neg_i :=  - a
	fmt.Println(builtins_py.String("add_i=") + builtins_py.String(fmt.Sprintf("%v", add_i)))
	fmt.Println(builtins_py.String("sub_i=") + builtins_py.String(fmt.Sprintf("%v", sub_i)))
	fmt.Println(builtins_py.String("mul_i=") + builtins_py.String(fmt.Sprintf("%v", mul_i)))
	fmt.Println(builtins_py.String("div_f=") + builtins_py.String(fmt.Sprintf("%v", div_f)))
	fmt.Println(builtins_py.String("div_i=") + builtins_py.String(fmt.Sprintf("%v", div_i)))
	fmt.Println(builtins_py.String("mod_i=") + builtins_py.String(fmt.Sprintf("%v", mod_i)))
	fmt.Println(builtins_py.String("neg_i=") + builtins_py.String(fmt.Sprintf("%v", neg_i)))
	fa := 9.0
	fb := 2.0
	fmt.Println(builtins_py.String("float_div=") + builtins_py.String(fmt.Sprintf("%v", (float64(fa) / float64(fb)))))
	fmt.Println(builtins_py.String("float_floordiv=") + builtins_py.String(fmt.Sprintf("%v", (fa / fb))))
	fmt.Println(builtins_py.String("eq=") + bool_str(a == b))
	fmt.Println(builtins_py.String("ne=") + bool_str(a != b))
	fmt.Println(builtins_py.String("lt=") + bool_str(a < b))
	fmt.Println(builtins_py.String("le=") + bool_str(a <= b))
	fmt.Println(builtins_py.String("gt=") + bool_str(a > b))
	fmt.Println(builtins_py.String("ge=") + bool_str(a >= b))
	short_circuit_and_demo()
	short_circuit_or_demo()
	fmt.Println(builtins_py.String("not_demo=") + bool_str(!(a == b)))
		for _, n := range (builtins_py.List_int{ - 3, 0, 4, 42}) {
		fmt.Println(builtins_py.String("classify(") + builtins_py.String(fmt.Sprintf("%v", n)) + builtins_py.String(")=") + classify_number(n))
	}
	i := 0
	total := 0
		for i < 5 {
		total = total + i
		i = i + 1
	}
	fmt.Println(builtins_py.String("while_total=") + builtins_py.String(fmt.Sprintf("%v", total)))
	range_sum := 0
		for _, k := range (Range(1, 6)) {
		range_sum = range_sum + k
	}
	fmt.Println(builtins_py.String("range_sum=") + builtins_py.String(fmt.Sprintf("%v", range_sum)))
	words := builtins_py.List_str{builtins_py.String("quick"), builtins_py.String("brown"), builtins_py.String("fox")}
	joined := builtins_py.String("")
		for _, w := range (words) {
		joined = joined + w + builtins_py.String("-")
	}
	fmt.Println(builtins_py.String("joined=") + joined)
	fmt.Println(builtins_py.String("factorial5=") + builtins_py.String(fmt.Sprintf("%v", factorial_recursive(5))))
	counter := 0
	counter = counter + 1
	counter = counter + 1
	fmt.Println(builtins_py.String("counter=") + builtins_py.String(fmt.Sprintf("%v", counter)))
	fox_list := builtins_py.List_int{1, 2, 3}
	fox_list[0] = 100
	fox_list.Append(4)
	fmt.Println(builtins_py.String("fox_list0=") + builtins_py.String(fmt.Sprintf("%v", fox_list[0])))
	fmt.Println(builtins_py.String("fox_list_len=") + builtins_py.String(fmt.Sprintf("%v", len(fox_list))))
	fmt.Println(builtins_py.String("fox_list_last=") + builtins_py.String(fmt.Sprintf("%v", fox_list[3])))
	fox_map := map[interface{}]interface{}{}
	fox_map[builtins_py.String("quick")] = 1
	fox_map[builtins_py.String("brown")] = 2
	fox_map[builtins_py.String("fox")] = 3
	fmt.Println(builtins_py.String("map_get_brown=") + builtins_py.String(fmt.Sprintf("%v", fox_map.Get(builtins_py.String("brown")))))
	fox_map[builtins_py.String("fox")] = 30
	fmt.Println(builtins_py.String("map_get_fox=") + builtins_py.String(fmt.Sprintf("%v", fox_map.Get(builtins_py.String("fox")))))
	name := builtins_py.String("fox")
	speed := 12
	formatted := builtins_py.String("The {} runs at {} mph").Format(name, speed)
	fmt.Println(formatted)
	fmt.Println(builtins_py.String("name_len=") + builtins_py.String(fmt.Sprintf("%v", len(name))))
	pair := []interface{}{name, speed}
	p_name := pair
	fmt.Println(builtins_py.String("pair_name=") + p_name + builtins_py.String(" pair_speed=") + builtins_py.String(fmt.Sprintf("%v", p_speed)))
	box := NewBox(10)
	fmt.Println(builtins_py.String("box_before=") + box.Describe())
	box.Update_value(99)
	fmt.Println(builtins_py.String("box_after=") + box.Describe())
	fmt.Println(builtins_py.String("box_value=") + builtins_py.String(fmt.Sprintf("%v", box.value)))
		func() {
		defer func() {
			if e := recover(); e != nil {
			}
		}()
		risky_divide(10, 0)
	}()
	safe_result := risky_divide(10, 4)
	fmt.Println(builtins_py.String("safe_result=") + builtins_py.String(fmt.Sprintf("%v", safe_result)))
	maybe_value := nil
	fmt.Println(builtins_py.String("maybe_before=") + none_str(maybe_value))
	maybe_value = 7
	fmt.Println(builtins_py.String("maybe_after=") + none_str(maybe_value))
	fmt.Println(builtins_py.String("contains_fox=") + bool_str(Contains(words, builtins_py.String("fox"))))
	fmt.Println(builtins_py.String("contains_wolf=") + bool_str(Contains(words, builtins_py.String("wolf"))))
	fmt.Println(builtins_py.String("contains_key=") + bool_str(Contains(fox_map, builtins_py.String("quick"))))
	fmt.Println(builtins_py.String("DONE"))
	return nil
}