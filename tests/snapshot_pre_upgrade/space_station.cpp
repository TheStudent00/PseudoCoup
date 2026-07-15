#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <any>
#include <stdexcept>

class SpaceStation {
public:
    std::string name;
    int capacity;
    std::vector<std::string> modules;
    std::unordered_map<std::string, int> resource_levels;
    SpaceStation(std::string name, int capacity) {
        this->name = name;
        this->capacity = capacity;
        this->modules = {"Command", "Life Support", "Laboratory"};
        this->resource_levels = builtins_py::hashmap({{"Oxygen", 95}, {"Power", 100}});
    }
    void printStatus() {
        std::cout << ("Station: " + this->name) << "\n";
        std::cout << (builtins_py::str("Capacity: ") + builtins_py::str(this->capacity)) << "\n";
    }
};
class Astronaut {
public:
    std::string name;
    int experience;
    Optional[SpaceStation] assigned_station;
    int health;
    Astronaut(std::string name, int experience, Optional[SpaceStation] assigned_station) {
        this->name = name;
        this->experience = experience;
        this->assigned_station = assigned_station;
        this->health = 100;
    }
    int work(int hours) {
        if ((hours < 0)) {
            throw std::runtime_error(Exception("Cannot work negative hours"));
        }
        tasks_done = 0;
        current_hour = 0;
        while ((current_hour < hours)) {
            if ((this->health < 20)) {
                std::cout << "Astronaut is too tired to work." << "\n";
            }
            if (((current_hour % 3) == 0)) {
                current_hour = (current_hour + 1);
            }
            this->health = (this->health - 10);
            tasks_done = (tasks_done + 2);
            current_hour = (current_hour + 1);
        }
        return tasks_done;
    }
    void report() {
        if ((this->assigned_station != null)) {
            this->assigned_station.printStatus();
            if ((builtins_py::len(this->assigned_station.modules) > 0)) {
                std::cout << (builtins_py::str("Primary module: ") + builtins_py::str(this->assigned_station.modules[0])) << "\n";
            }
            if (("Oxygen" in this->assigned_station.resource_levels)) {
                oxy = this->assigned_station.resource_levels["Oxygen"];
                std::cout << (builtins_py::str("Oxygen Level: ") + builtins_py::str(oxy)) << "\n";
            }
        } else {
            std::cout << "No station assigned." << "\n";
        }
    }
};
int main() {
    try {
        SpaceStation station = SpaceStation("Alpha", 50);
        Astronaut astro = Astronaut("Ripley", 10, station);
        astro.report();
        int completed = astro.work(8);
        std::cout << (builtins_py::str("Tasks Completed: ") + builtins_py::str(completed)) << "\n";
        std::cout << (builtins_py::str("Health remaining: ") + builtins_py::str(astro.health)) << "\n";
        Astronaut rookie = Astronaut("Newb", 0, null);
        rookie.report();
        rookie.work(-(5));
    } catch (const std::exception& e) {
    }
    return 0;
}
if ((__name__ == "__main__")) {
    main();
}