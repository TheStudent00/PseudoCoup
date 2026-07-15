import 'builtins_py.dart';



class SpaceStation {
    String name = "";
    int capacity = 0;
    List<String> modules;
    Map<String, int> resource_levels;
    SpaceStation(this.name, this.capacity) {
        this.modules = ["Command", "Life Support", "Laboratory"];
        this.resource_levels = {"Oxygen": 95, "Power": 100};
    }
    void printStatus() {
        print("Station: " + this.name);
        print(("Capacity: ").toString() + (this.capacity).toString());
    }
}

class Astronaut {
    String name = "";
    int experience = 0;
    Optional[SpaceStation] assigned_station;
    int health = 0;
    Astronaut(this.name, this.experience, this.assigned_station) {
        this.health = 100;
    }
    int work(int hours) {
                if (hours < 0) {
            throw(Exception("Cannot work negative hours"));
        };
        int tasks_done = 0;
        int current_hour = 0;
                while (current_hour < hours) {
                        if (this.health < 20) {
                print("Astronaut is too tired to work.");
            };
                        if (current_hour % 3 == 0) {
                current_hour = current_hour + 1;
            };
            this.health = this.health - 10;
            tasks_done = tasks_done + 2;
            current_hour = current_hour + 1;
        };
        return tasks_done;
    }
    void report() {
                if (this.assigned_station is not null) {
            this.assigned_station.printStatus();
                        if (this.assigned_station.modules.length > 0) {
                print(("Primary module: ").toString() + (this.assigned_station.modules[0]).toString());
            };
                        if (this.assigned_station.resource_levels.contains("Oxygen")) {
                int oxy = this.assigned_station.resource_levels["Oxygen"];
                print(("Oxygen Level: ").toString() + (oxy).toString());
            };
        } else {
            print("No station assigned.");
        };
    }
}

void main() {
        try {
        SpaceStation station = SpaceStation("Alpha", 50);
        Astronaut astro = Astronaut("Ripley", 10, station);
        astro.report();
        int completed = astro.work(8);
        print(("Tasks Completed: ").toString() + (completed).toString());
        print(("Health remaining: ").toString() + (astro.health).toString());
        Astronaut rookie = Astronaut("Newb", 0, null);
        rookie.report();
        rookie.work(-(5));
    } catch (e) {
    };
}