struct SpaceStation {
    name: String,
    capacity: i32,
    modules: Vec<String>,
    resource_levels: HashMap<String, i32>,
}

impl SpaceStation {
    fn new(name: String, capacity: i32) -> Self {
        Self { name: name, capacity: capacity, modules: vec!["Command", "Life Support", "Laboratory"], resource_levels: builtins_py::hashmap!("Oxygen" => 95, "Power" => 100) }
    }
    fn printStatus(&mut self) -> () {
        println!(("Station: " + self.name));
        println!((builtins_py::str("Capacity: ") + builtins_py::str(self.capacity)));
    }
}
struct Astronaut {
    name: String,
    experience: i32,
    assigned_station: Optional[SpaceStation],
    health: i32,
}

impl Astronaut {
    fn new(name: String, experience: i32, assigned_station: Optional[SpaceStation]) -> Self {
        Self { name: name, experience: experience, assigned_station: assigned_station, health: 100 }
    }
    fn work(&mut self, hours: i32) -> i32 {
        if (hours < 0) {
            panic!(Exception::new("Cannot work negative hours"));
        }
        tasks_done = 0;
        current_hour = 0;
        while (current_hour < hours) {
            if (self.health < 20) {
                println!("Astronaut is too tired to work.");
            }
            if ((current_hour % 3) == 0) {
                current_hour = (current_hour + 1);
            }
            self.health = (self.health - 10);
            tasks_done = (tasks_done + 2);
            current_hour = (current_hour + 1);
        }
        return tasks_done;
    }
    fn report(&mut self) -> () {
        if (self.assigned_station != null) {
            self.assigned_station.printStatus();
            if (builtins_py::len(self.assigned_station.modules) > 0) {
                println!((builtins_py::str("Primary module: ") + builtins_py::str(self.assigned_station.modules[0])));
            }
            if ("Oxygen" in self.assigned_station.resource_levels) {
                oxy = self.assigned_station.resource_levels["Oxygen"];
                println!((builtins_py::str("Oxygen Level: ") + builtins_py::str(oxy)));
            }
        } else {
            println!("No station assigned.");
        }
    }
}
fn main() -> () {
    // try {
        let mut station: SpaceStation = SpaceStation::new("Alpha", 50);
        let mut astro: Astronaut = Astronaut::new("Ripley", 10, station);
        astro.report();
        let mut completed: i32 = astro.work(8);
        println!((builtins_py::str("Tasks Completed: ") + builtins_py::str(completed)));
        println!((builtins_py::str("Health remaining: ") + builtins_py::str(astro.health)));
        let mut rookie: Astronaut = Astronaut::new("Newb", 0, null);
        rookie.report();
        rookie.work(-(5));
    // } catch {
    // }
}
if (__name__ == "__main__") {
    main();
}