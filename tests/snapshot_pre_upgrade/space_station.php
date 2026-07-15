<?php
require_once 'builtins_py.php';

class SpaceStation {
    public function __construct(string $name, int $capacity) {
        $this->name = $name;
        $this->capacity = $capacity;
        $this->modules = ["Command", "Life Support", "Laboratory"];
        $this->resource_levels = ["Oxygen" => 95, "Power" => 100];
    }
    public function printStatus() {
        print(("Station: " + $this->name));
        print((builtins_py_str("Capacity: ") + builtins_py_str($this->capacity)));
    }
}
class Astronaut {
    public function __construct(string $name, int $experience, $assigned_station) {
        $this->name = $name;
        $this->experience = $experience;
        $this->assigned_station = $assigned_station;
        $this->health = 100;
    }
    public function work(int $hours): int {
        if (($hours < 0)) {
            throw new \Exception(Exception("Cannot work negative hours"));
        }
        $tasks_done = 0;
        $current_hour = 0;
        while (($current_hour < $hours)) {
            if (($this->health < 20)) {
                print("Astronaut is too tired to work.");
            }
            if ((($current_hour % 3) == 0)) {
                $current_hour = ($current_hour + 1);
            }
            $this->health = ($this->health - 10);
            $tasks_done = ($tasks_done + 2);
            $current_hour = ($current_hour + 1);
        }
        return $tasks_done;
    }
    public function report() {
        if (($this->assigned_station !== $null)) {
            $this->assigned_station->printStatus();
            if ((builtins_py_len($this->assigned_station->modules) > 0)) {
                print((builtins_py_str("Primary module: ") + builtins_py_str($this->assigned_station->modules[0])));
            }
            if (("Oxygen" in $this->assigned_station->resource_levels)) {
                $oxy = $this->assigned_station->resource_levels["Oxygen"];
                print((builtins_py_str("Oxygen Level: ") + builtins_py_str($oxy)));
            }
        } else {
            print("No station assigned.");
        }
    }
}
function main() {
    try {
        $station = SpaceStation("Alpha", 50);
        $astro = Astronaut("Ripley", 10, $station);
        astro->report();
        $completed = astro->work(8);
        print((builtins_py_str("Tasks Completed: ") + builtins_py_str($completed)));
        print((builtins_py_str("Health remaining: ") + builtins_py_str($astro->health)));
        $rookie = Astronaut("Newb", 0, $null);
        rookie->report();
        rookie->work(-(5));
    } catch (\Exception $e) {
    }
}
if (($__name__ == "__main__")) {
    main();
}