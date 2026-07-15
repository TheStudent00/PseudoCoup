import roundtrip.builtins_py.*

class SpaceStation {
    var name: String = ""
    var capacity: Int = 0
    var modules: MutableList<String>? = null
    var resource_levels: MutableMap<String, Int>? = null
    constructor(name: String, capacity: Int) {
        this.modules = mutableListOf("Command", "Life Support", "Laboratory")
        this.resource_levels = mutableMapOf("Oxygen" to 95, "Power" to 100)
    }
    fun printStatus(): Unit {
        print(("Station: " + this.name))
        print((str("Capacity: ") + str(this.capacity)))
    }
}
class Astronaut {
    var name: String = ""
    var experience: Int = 0
    var assigned_station: Optional[SpaceStation] = null
    var health: Int = 0
    constructor(name: String, experience: Int, assigned_station: Optional[SpaceStation]) {
        this.health = 100
    }
    fun work(hours: Int): Int {
        if ((hours < 0)) {
            throw Exception("Cannot work negative hours")
        }
        var tasks_done: Int = 0
        var current_hour: Int = 0
        while ((current_hour < hours)) {
            if ((this.health < 20)) {
                print("Astronaut is too tired to work.")
            }
            if (((current_hour % 3) == 0)) {
                current_hour = (current_hour + 1)
            }
            this.health = (this.health - 10)
            tasks_done = (tasks_done + 2)
            current_hour = (current_hour + 1)
        }
        return tasks_done
    }
    fun report(): Unit {
        if ((this.assigned_station !== null)) {
            this.assigned_station.printStatus()
            if ((len(this.assigned_station.modules) > 0)) {
                print((str("Primary module: ") + str(this.assigned_station.modules[0])))
            }
            if (("Oxygen" in this.assigned_station.resource_levels)) {
                var oxy: Int = this.assigned_station.resource_levels["Oxygen"]
                print((str("Oxygen Level: ") + str(oxy)))
            }
        } else {
            print("No station assigned.")
        }
    }
}
fun main(): Unit {
    try {
        var station: SpaceStation = SpaceStation("Alpha", 50)
        var astro: Astronaut = Astronaut("Ripley", 10, station)
        astro.report()
        var completed: Int = astro.work(8)
        print((str("Tasks Completed: ") + str(completed)))
        print((str("Health remaining: ") + str(astro.health)))
        var rookie: Astronaut = Astronaut("Newb", 0, null)
        rookie.report()
        rookie.work(-(5))
    } catch (e: Exception) {
    }
}

fun main(args: Array<String>) {
    main()
}