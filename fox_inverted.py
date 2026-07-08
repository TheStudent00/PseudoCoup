from typing import List, Dict, Optional, Any

class SpaceStation:
    def __init__(self, name: Any, capacity: Any) -> None:
        self.name = name
        self.capacity = capacity
        self.modules = ["Command", "Life Support", "Laboratory"]
        self.resource_levels = {"Oxygen": 95, "Power": 100}

    def printStatus(self) -> Any:
        print("Station: " + self.name)
        print("Capacity: " + str(self.capacity))


class Astronaut:
    def __init__(self, name: Any, experience: Any, assigned_station: Any) -> None:
        self.name = name
        self.experience = experience
        self.assigned_station = assigned_station
        self.health = 100

    def work(self, hours: Any) -> Any:
        if hours < 0:
            raise Exception("Cannot work negative hours")
        tasks_done = 0
        current_hour = 0
        while current_hour < hours:
            if self.health < 20:
                print("Astronaut is too tired to work.")
                break
            if current_hour % 3 == 0:
                current_hour = current_hour + 1
                continue
            self.health = self.health - 10
            tasks_done = tasks_done + 2
            current_hour = current_hour + 1
        return tasks_done

    def report(self) -> Any:
        if self.assigned_station != None:
            self.assigned_station.printStatus()
            if len(self.assigned_station.modules) > 0:
                print("Primary module: " + self.assigned_station.modules[0])
            if "Oxygen" in self.assigned_station.resource_levels:
                oxy = self.assigned_station.resource_levels["Oxygen"]
                print("Oxygen Level: " + str(oxy))
        else:
            print("No station assigned.")


def main() -> None:
    try:
        station = SpaceStation("Alpha", 50)
        astro = Astronaut("Ripley", 10, station)
        astro.report()
        completed = astro.work(8)
        print("Tasks Completed: " + str(completed))
        print("Health remaining: " + str(astro.health))
        rookie = Astronaut("Newb", 0, None)
        rookie.report()
        rookie.work(-5)
    except Exception as e:
        print("Caught expected exception in Space Station")
    return 0

if __name__ == '__main__':
    main()
