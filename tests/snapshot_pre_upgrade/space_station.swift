import Foundation

class SpaceStation {
    var name: String
    var capacity: Int
    var modules: [String]
    var resource_levels: [String: Int]
    init(_ name: String, _ capacity: Int) {
        self.modules = ["Command", "Life Support", "Laboratory"]
        self.resource_levels = ["Oxygen": 95, "Power": 100]
    }
    func printStatus() -> Void {
        builtins_py.print(("Station: " + self.name))
        builtins_py.print((builtins_py.str("Capacity: ") + builtins_py.str(self.capacity)))
    }
}
class Astronaut {
    var name: String
    var experience: Int
    var assigned_station: Optional[SpaceStation]
    var health: Int
    init(_ name: String, _ experience: Int, _ assigned_station: Optional[SpaceStation]) {
        self.health = 100
    }
    func work(_ hours: Int) -> Int {
        if (hours < 0) {
            throw Exception("Cannot work negative hours")
        }
        tasks_done = 0
        current_hour = 0
        while (current_hour < hours) {
            if (self.health < 20) {
                builtins_py.print("Astronaut is too tired to work.")
            }
            if ((current_hour % 3) == 0) {
                current_hour = (current_hour + 1)
            }
            self.health = (self.health - 10)
            tasks_done = (tasks_done + 2)
            current_hour = (current_hour + 1)
        }
        return tasks_done
    }
    func report() -> Void {
        if !(self.assigned_station is null) {
            self.assigned_station.printStatus()
            if (builtins_py.len(self.assigned_station.modules) > 0) {
                builtins_py.print((builtins_py.str("Primary module: ") + builtins_py.str(self.assigned_station.modules[0])))
            }
            if ("Oxygen" in self.assigned_station.resource_levels) {
                oxy = self.assigned_station.resource_levels["Oxygen"]
                builtins_py.print((builtins_py.str("Oxygen Level: ") + builtins_py.str(oxy)))
            }
        } else {
            builtins_py.print("No station assigned.")
        }
    }
}
func main() -> Void {
    do {
        var station: SpaceStation = SpaceStation("Alpha", 50)
        var astro: Astronaut = Astronaut("Ripley", 10, station)
        try astro.report()
        var completed: Int = astro.work(8)
        try builtins_py.print((builtins_py.str("Tasks Completed: ") + builtins_py.str(completed)))
        try builtins_py.print((builtins_py.str("Health remaining: ") + builtins_py.str(astro.health)))
        var rookie: Astronaut = Astronaut("Newb", 0, null)
        try rookie.report()
        try rookie.work(-(5))
    } catch let e {
    }
}
main([])