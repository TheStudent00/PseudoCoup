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

type SpaceStation struct {

	name builtins_py.String

	capacity int

	modules builtins_py.List_str

	resource_levels builtins_py.Map_str_int

}

func NewSpaceStation(name builtins_py.String, capacity int) *SpaceStation {
	this := &SpaceStation{}
	this.name = name
	this.capacity = capacity
	this.modules = builtins_py.List_str{builtins_py.String("Command"), builtins_py.String("Life Support"), builtins_py.String("Laboratory")}
	this.resource_levels = builtins_py.Map_str_int{builtins_py.String("Oxygen"): 95, builtins_py.String("Power"): 100}
	return this
}

func (this *SpaceStation) Printstatus() {
	fmt.Println(builtins_py.String("Station: ") + this.name)
	fmt.Println(builtins_py.String(fmt.Sprintf("%v", builtins_py.String("Capacity: "))) + builtins_py.String(fmt.Sprintf("%v", this.capacity)))
}
type Astronaut struct {

	name builtins_py.String

	experience int

	assigned_station Optional[SpaceStation]

	health int

}

func NewAstronaut(name builtins_py.String, experience int, assigned_station Optional[SpaceStation]) *Astronaut {
	this := &Astronaut{}
	this.name = name
	this.experience = experience
	this.assigned_station = assigned_station
	this.health = 100
	return this
}

func (this *Astronaut) Work(hours int) int {
		if hours < 0 {
		panic(NewException(builtins_py.String("Cannot work negative hours")))
	}
	var tasks_done int = 0
	var current_hour int = 0
		for current_hour < hours {
				if this.health < 20 {
			fmt.Println(builtins_py.String("Astronaut is too tired to work."))
		}
				if current_hour % 3 == 0 {
			current_hour = current_hour + 1
		}
		this.health = this.health - 10
		tasks_done = tasks_done + 2
		current_hour = current_hour + 1
	}
	return tasks_done
	return 0
}

func (this *Astronaut) Report() {
		if this.assigned_station != nil {
		this.assigned_station.Printstatus()
				if len(this.assigned_station.modules) > 0 {
			fmt.Println(builtins_py.String(fmt.Sprintf("%v", builtins_py.String("Primary module: "))) + builtins_py.String(fmt.Sprintf("%v", this.assigned_station.modules[0])))
		}
				if Contains(this.assigned_station.resource_levels, builtins_py.String("Oxygen")) {
			var oxy int = this.assigned_station.resource_levels[builtins_py.String("Oxygen")]
			fmt.Println(builtins_py.String(fmt.Sprintf("%v", builtins_py.String("Oxygen Level: "))) + builtins_py.String(fmt.Sprintf("%v", oxy)))
		}
	} else {
		fmt.Println(builtins_py.String("No station assigned."))
	}
}
func main() {
		func() {
		defer func() {
			if e := recover(); e != nil {
			}
		}()
		var station *SpaceStation = NewSpaceStation(builtins_py.String("Alpha"), 50)
		var astro *Astronaut = NewAstronaut(builtins_py.String("Ripley"), 10, station)
		astro.Report()
		var completed int = astro.Work(8)
		fmt.Println(builtins_py.String(fmt.Sprintf("%v", builtins_py.String("Tasks Completed: "))) + builtins_py.String(fmt.Sprintf("%v", completed)))
		fmt.Println(builtins_py.String(fmt.Sprintf("%v", builtins_py.String("Health remaining: "))) + builtins_py.String(fmt.Sprintf("%v", astro.health)))
		var rookie *Astronaut = NewAstronaut(builtins_py.String("Newb"), 0, nil)
		rookie.Report()
		rookie.Work( - 5)
	}()
}