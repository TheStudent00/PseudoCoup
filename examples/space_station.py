from typing import List, Dict, Optional, Any

class SpaceStation:
    name: str
    capacity: int
    modules: List[str]
    resource_levels: Dict[str, int]

    def __init__(self, name: str, capacity: int) -> None:
        self.name = name
        self.capacity = capacity
        self.modules = ["Command", "Life Support", "Laboratory"]
        self.resource_levels = {"Oxygen": 95, "Power": 100}

    def printStatus(self) -> None:
        print("Station: " + self.name)
        print(str("Capacity: ") + str(self.capacity))


class Astronaut:
    name: str
    experience: int
    assigned_station: Optional[SpaceStation]
    health: int

    def __init__(self, name: str, experience: int, assigned_station: Optional[SpaceStation]) -> None:
        self.name = name
        self.experience = experience
        self.assigned_station = assigned_station
        self.health = 100

    def work(self, hours: int) -> int:
        if hours < 0:
            raise Exception("Cannot work negative hours")
        
        tasks_done: int = 0
        current_hour: int = 0
        
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

    def report(self) -> None:
        if self.assigned_station is not None:
            self.assigned_station.printStatus()
            if len(self.assigned_station.modules) > 0:
                print(str("Primary module: ") + str(self.assigned_station.modules[0]))
            
            if "Oxygen" in self.assigned_station.resource_levels:
                oxy: int = self.assigned_station.resource_levels["Oxygen"]
                print(str("Oxygen Level: ") + str(oxy))
        else:
            print("No station assigned.")

def main() -> None:
    try:
        station: SpaceStation = SpaceStation("Alpha", 50)
        astro: Astronaut = Astronaut("Ripley", 10, station)
        
        astro.report()
        
        completed: int = astro.work(8)
        print(str("Tasks Completed: ") + str(completed))
        print(str("Health remaining: ") + str(astro.health))
        
        rookie: Astronaut = Astronaut("Newb", 0, None)
        rookie.report()
        rookie.work(-5)
        
    except Exception as e:
        print("Caught expected exception in Space Station")

if __name__ == '__main__':
    main()
