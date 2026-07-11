package builtins_py

import (
	"fmt"
	"strings"
)

type List_int []int

func (l *List_int) Append(item int) {
	*l = append(*l, item)
}

type List_str []String

func (l *List_str) Append(item String) {
	*l = append(*l, item)
}

type Map_str_int map[String]int

func (m Map_str_int) Get(key String) int {
	return m[key]
}

func (m Map_str_int) Contains(key String) bool {
	_, ok := m[key]
	return ok
}

type String string

func (s String) Format(arg1 interface{}, arg2 interface{}) String {
	res := strings.Replace(string(s), "{}", fmt.Sprintf("%v", arg1), 1)
	res = strings.Replace(res, "{}", fmt.Sprintf("%v", arg2), 1)
	return String(res)
}
