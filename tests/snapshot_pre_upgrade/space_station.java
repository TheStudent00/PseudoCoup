import roundtrip.builtins_py.*;

import java.util.*;



public class SpaceStation {
    public String name = "";
    public int capacity = 0;
    public ArrayList<String> modules = null;
    public HashMap<String, Integer> resource_levels = null;
    public SpaceStation(String name, int capacity) {
        this.modules = new ArrayList<>(Arrays.asList("Command", "Life Support", "Laboratory"));
        this.resource_levels = new HashMap<>(Map.of("Oxygen", 95, "Power", 100));
    }
    public void printStatus() {
        builtins_py.print(("Station: " + this.name));
        builtins_py.print((builtins_py.str("Capacity: ") + builtins_py.str(this.capacity)));
    }
}

public class Astronaut {
    public String name = "";
    public int experience = 0;
    public Optional[SpaceStation] assigned_station = null;
    public int health = 0;
    public Astronaut(String name, int experience, Optional[SpaceStation] assigned_station) {
        this.health = 100;
    }
    public int work(int hours) {
        if ((hours < 0)) {
            throw Exception("Cannot work negative hours");
        }
        int tasks_done = 0;
        int current_hour = 0;
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
    public void report() {
        if ((this.assigned_station != null)) {
            this.assigned_station.printStatus();
            if ((builtins_py.len(this.assigned_station.modules) > 0)) {
                builtins_py.print((builtins_py.str("Primary module: ") + builtins_py.str(this.assigned_station.modules[0])));
            }
            if ((this.assigned_station.resource_levels.contains("Oxygen"))) {
                int oxy = this.assigned_station.resource_levels["Oxygen"];
                builtins_py.print((builtins_py.str("Oxygen Level: ") + builtins_py.str(oxy)));
            }
        } else {
            builtins_py.print("No station assigned.");
        }
    }
}

public class Main {
public static void main() {
    try {
        SpaceStation station = SpaceStation("Alpha", 50);
        Astronaut astro = Astronaut("Ripley", 10, station);
        astro.report();
        int completed = astro.work(8);
        builtins_py.print((builtins_py.str("Tasks Completed: ") + builtins_py.str(completed)));
        builtins_py.print((builtins_py.str("Health remaining: ") + builtins_py.str(astro.health)));
        Astronaut rookie = Astronaut("Newb", 0, null);
        rookie.report();
        rookie.work(-(5));
    } catch (Exception e) {
    }
}
    public static void main(String[] args) {
        main();
    }
}