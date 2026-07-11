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

func side_effect_marker(tag builtins_py.String) bool {
	fmt.Println(builtins_py.String("SIDE_EFFECT:") + tag)
	return true
	return false
}
func short_circuit_and_demo() {
	var result bool = false && side_effect_marker(builtins_py.String("AND_RHS"))
	fmt.Println(builtins_py.String("and_short_circuit_result=") + bool_str(result))
}
func short_circuit_or_demo() {
	var result bool = true || side_effect_marker(builtins_py.String("OR_RHS"))
	fmt.Println(builtins_py.String("or_short_circuit_result=") + bool_str(result))
}
func bool_str(b bool) builtins_py.String {
		if b {
		return builtins_py.String("True")
	} else {
		return builtins_py.String("False")
	}
}
func none_str(v interface{}) builtins_py.String {
		if v == nil {
		return builtins_py.String("None")
	}
	return builtins_py.String(fmt.Sprintf("%v", v))
}
func classify_number(n int) builtins_py.String {
		if n < 0 {
		return builtins_py.String("negative")
	} else if n == 0 {
		return builtins_py.String("zero")
	} else if n < 10 {
		return builtins_py.String("small")
	} else {
		return builtins_py.String("large")
	}
}
func factorial_recursive(n int) int {
		if n <= 1 {
		return 1
	}
	return n * factorial_recursive(n - 1)
	return 0
}
type Box struct {

	value int

	history_len int

}

func NewBox(value int) *Box {
	this := &Box{}
	this.value = value
	this.history_len = 0
	return this
}

func (this *Box) Update_value(new_value int) {
	this.value = new_value
	this.history_len = this.history_len + 1
}

func (this *Box) Describe() builtins_py.String {
	return builtins_py.String("Box(value=") + builtins_py.String(fmt.Sprintf("%v", this.value)) + builtins_py.String(", writes=") + builtins_py.String(fmt.Sprintf("%v", this.history_len)) + builtins_py.String(")")
}
func risky_divide(a float64, b float64) float64 {
		if b == 0.0 {
		panic(builtins_py.String("division by zero not allowed"))
	}
	return (float64(a) / float64(b))
	return 0.0
}
func main() {
	var a int = 17
	var b int = 5
	var add_i int = a + b
	var sub_i int = a - b
	var mul_i int = a * b
	var div_f float64 = (float64(a) / float64(b))
	var div_i int = (a / b)
	var mod_i int = a % b
	var neg_i int =  - a
	fmt.Println(builtins_py.String("add_i=") + builtins_py.String(fmt.Sprintf("%v", add_i)))
	fmt.Println(builtins_py.String("sub_i=") + builtins_py.String(fmt.Sprintf("%v", sub_i)))
	fmt.Println(builtins_py.String("mul_i=") + builtins_py.String(fmt.Sprintf("%v", mul_i)))
	fmt.Println(builtins_py.String("div_f=") + builtins_py.String(fmt.Sprintf("%v", div_f)))
	fmt.Println(builtins_py.String("div_i=") + builtins_py.String(fmt.Sprintf("%v", div_i)))
	fmt.Println(builtins_py.String("mod_i=") + builtins_py.String(fmt.Sprintf("%v", mod_i)))
	fmt.Println(builtins_py.String("neg_i=") + builtins_py.String(fmt.Sprintf("%v", neg_i)))
	var fa float64 = 9.0
	var fb float64 = 2.0
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
	var n int
		for _, n = range (builtins_py.List_int{ - 3, 0, 4, 42}) {
		fmt.Println(builtins_py.String("classify(") + builtins_py.String(fmt.Sprintf("%v", n)) + builtins_py.String(")=") + classify_number(n))
	}
	var i int = 0
	var total int = 0
		for i < 5 {
		total = total + i
		i = i + 1
	}
	fmt.Println(builtins_py.String("while_total=") + builtins_py.String(fmt.Sprintf("%v", total)))
	var range_sum int = 0
	var k int
		for _, k = range (Range(1, 6)) {
		range_sum = range_sum + k
	}
	fmt.Println(builtins_py.String("range_sum=") + builtins_py.String(fmt.Sprintf("%v", range_sum)))
	var words builtins_py.List_str = builtins_py.List_str{builtins_py.String("quick"), builtins_py.String("brown"), builtins_py.String("quickfox")}
	var joined builtins_py.String = builtins_py.String("")
	var w builtins_py.String
		for _, w = range (words) {
		joined = joined + w + builtins_py.String("-")
	}
	fmt.Println(builtins_py.String("joined=") + joined)
	fmt.Println(builtins_py.String("factorial5=") + builtins_py.String(fmt.Sprintf("%v", factorial_recursive(5))))
	var counter int = 0
	counter = counter + 1
	counter = counter + 1
	fmt.Println(builtins_py.String("counter=") + builtins_py.String(fmt.Sprintf("%v", counter)))
	var quickfox_list builtins_py.List_int = builtins_py.List_int{1, 2, 3}
	quickfox_list[0] = 100
	quickfox_list.Append(4)
	fmt.Println(builtins_py.String("quickfox_list0=") + builtins_py.String(fmt.Sprintf("%v", quickfox_list[0])))
	fmt.Println(builtins_py.String("quickfox_list_len=") + builtins_py.String(fmt.Sprintf("%v", len(quickfox_list))))
	fmt.Println(builtins_py.String("quickfox_list_last=") + builtins_py.String(fmt.Sprintf("%v", quickfox_list[3])))
	var quickfox_map builtins_py.Map_str_int = builtins_py.Map_str_int{}
	quickfox_map[builtins_py.String("quick")] = 1
	quickfox_map[builtins_py.String("brown")] = 2
	quickfox_map[builtins_py.String("quickfox")] = 3
	fmt.Println(builtins_py.String("map_get_brown=") + builtins_py.String(fmt.Sprintf("%v", quickfox_map.Get(builtins_py.String("brown")))))
	quickfox_map[builtins_py.String("quickfox")] = 30
	fmt.Println(builtins_py.String("map_get_quickfox=") + builtins_py.String(fmt.Sprintf("%v", quickfox_map.Get(builtins_py.String("quickfox")))))
	var name builtins_py.String = builtins_py.String("fox")
	var speed int = 12
	var formatted builtins_py.String = builtins_py.String("The {} runs at {} mph").Format(name, speed)
	fmt.Println(formatted)
	fmt.Println(builtins_py.String("name_len=") + builtins_py.String(fmt.Sprintf("%v", len(name))))
	var pair []interface{} = []interface{}{name, speed}
	var p_name builtins_py.String = pair[0].(builtins_py.String)
	var p_speed int = pair[1].(int)
	fmt.Println(builtins_py.String("pair_name=") + p_name + builtins_py.String(" pair_speed=") + builtins_py.String(fmt.Sprintf("%v", p_speed)))
	var box *Box = NewBox(10)
	fmt.Println(builtins_py.String("box_before=") + box.Describe())
	box.Update_value(99)
	fmt.Println(builtins_py.String("box_after=") + box.Describe())
	fmt.Println(builtins_py.String("box_value=") + builtins_py.String(fmt.Sprintf("%v", box.value)))
		func() {
		defer func() {
			if e := recover(); e != nil {
			}
		}()
		risky_divide(10.0, 0.0)
	}()
	var safe_result float64 = risky_divide(10.0, 4.0)
	fmt.Println(builtins_py.String("safe_result=") + builtins_py.String(fmt.Sprintf("%v", safe_result)))
	var maybe_value *int = nil
	fmt.Println(builtins_py.String("maybe_before=") + none_str(maybe_value))
	maybe_value = Ptr(7)
	fmt.Println(builtins_py.String("maybe_after=") + none_str(maybe_value))
	fmt.Println(builtins_py.String("contains_quickfox=") + bool_str(Contains(words, builtins_py.String("quickfox"))))
	fmt.Println(builtins_py.String("contains_wolf=") + bool_str(Contains(words, builtins_py.String("wolf"))))
	fmt.Println(builtins_py.String("contains_key=") + bool_str(func() bool { _, ok := quickfox_map[builtins_py.String("quick")]; return ok }()))
	fmt.Println(builtins_py.String("DONE"))
}