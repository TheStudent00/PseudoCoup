require_relative 'builtins_py'

class SpaceStation
  def initialize(name, capacity)
    @name = name
    @capacity = capacity
    @modules = ["Command", "Life Support", "Laboratory"]
    @resource_levels = {"Oxygen" => 95, "Power" => 100}
  end
  def printStatus
    puts(("Station: " + @name))
    puts((builtins_py.str("Capacity: ") + builtins_py.str(@capacity)))
  end
end
class Astronaut
  def initialize(name, experience, assigned_station)
    @name = name
    @experience = experience
    @assigned_station = assigned_station
    @health = 100
  end
  def work(hours)
    if (hours < 0)
      raise StandardError.new(Exception("Cannot work negative hours"))
    end
    tasks_done = 0
    current_hour = 0
    while (current_hour < hours)
      if (@health < 20)
        puts("Astronaut is too tired to work.")
      end
      if ((current_hour % 3) == 0)
        current_hour = (current_hour + 1)
      end
      @health = (@health - 10)
      tasks_done = (tasks_done + 2)
      current_hour = (current_hour + 1)
    end
    return tasks_done
  end
  def report
    if (@assigned_station != null)
      @assigned_station.printStatus()
      if (builtins_py.len(@assigned_station.modules) > 0)
        puts((builtins_py.str("Primary module: ") + builtins_py.str(@assigned_station.modules[0])))
      end
      if ("Oxygen" in @assigned_station.resource_levels)
        oxy = @assigned_station.resource_levels["Oxygen"]
        puts((builtins_py.str("Oxygen Level: ") + builtins_py.str(oxy)))
      end
    else
      puts("No station assigned.")
    end
  end
end
def main
  begin
    station = SpaceStation("Alpha", 50)
    astro = Astronaut("Ripley", 10, station)
    astro.report()
    completed = astro.work(8)
    puts((builtins_py.str("Tasks Completed: ") + builtins_py.str(completed)))
    puts((builtins_py.str("Health remaining: ") + builtins_py.str(astro.health)))
    rookie = Astronaut("Newb", 0, null)
    rookie.report()
    rookie.work(-(5))
  rescue StandardError => e
  end
end
if (__name__ == "__main__")
  main()
end