import * as builtins_py from "./builtins_py";

class SpaceStation {
    name: string;
    capacity: number;
    modules: string[];
    resource_levels: Record<string, number>;
    constructor(name: string, capacity: number) {
        this.modules = ["Command", "Life Support", "Laboratory"];
        this.resource_levels = { "Oxygen": 95, "Power": 100 };
    }
    printStatus(): void {
        builtins_py.print(("Station: " + this.name));
        builtins_py.print((builtins_py.str("Capacity: ") + builtins_py.str(this.capacity)));
    }
}
class Astronaut {
    name: string;
    experience: number;
    assigned_station: Optional[SpaceStation];
    health: number;
    constructor(name: string, experience: number, assigned_station: Optional[SpaceStation]) {
        this.health = 100;
    }
    work(hours: number): number {
        if ((hours < 0)) {
            throw Exception("Cannot work negative hours");
        }
        tasks_done = 0;
        current_hour = 0;
        while ((current_hour < hours)) {
            if ((this.health < 20)) {
                builtins_py.print("Astronaut is too tired to work.");
            }
            if (((current_hour % 3) == 0)) {
                current_hour = (current_hour + 1);
            }
            this.health = (this.health - 10);
            tasks_done = (tasks_done + 2);
            current_hour = (current_hour + 1);
        }
        return tasks_done;
    }
    report(): void {
        if ((this.assigned_station !== null)) {
            this.assigned_station.printStatus();
            if ((builtins_py.len(this.assigned_station.modules) > 0)) {
                builtins_py.print((builtins_py.str("Primary module: ") + builtins_py.str(this.assigned_station.modules[0])));
            }
            if (("Oxygen" in this.assigned_station.resource_levels)) {
                oxy = this.assigned_station.resource_levels["Oxygen"];
                builtins_py.print((builtins_py.str("Oxygen Level: ") + builtins_py.str(oxy)));
            }
        } else {
            builtins_py.print("No station assigned.");
        }
    }
}
function main(): void {
    try {
        let station: SpaceStation = new SpaceStation("Alpha", 50);
        let astro: Astronaut = new Astronaut("Ripley", 10, station);
        astro.report();
        let completed: number = astro.work(8);
        builtins_py.print((builtins_py.str("Tasks Completed: ") + builtins_py.str(completed)));
        builtins_py.print((builtins_py.str("Health remaining: ") + builtins_py.str(astro.health)));
        let rookie: Astronaut = new Astronaut("Newb", 0, null);
        rookie.report();
        rookie.work(-(5));
    } catch (e) {
    }
}
main([]);