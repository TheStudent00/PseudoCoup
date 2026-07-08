#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <stdexcept>

class SpaceStation
{
public:
    std::string name;
    int capacity;
    std::vector<std::string> modules;
    std::unordered_map<std::string, int> resource_levels;

    SpaceStation(std::string name, int capacity)
    {
        this->name = name;
        this->capacity = capacity;
        this->modules = std::vector<std::string>{"Command", "Life Support", "Laboratory"};
        this->resource_levels = std::unordered_map<std::string, int>{{"Oxygen", 95}, {"Power", 100}};
    }

    auto printStatus()
    {
        std::cout << "Station: " + this->name << std::endl;
        std::cout << "Capacity: " + std::to_string(this->capacity) << std::endl;
    }

};

class Astronaut
{
public:
    std::string name;
    int experience;
    SpaceStation* assigned_station;
    int health;

    Astronaut(std::string name, int experience, SpaceStation* assigned_station)
    {
        this->name = name;
        this->experience = experience;
        this->assigned_station = assigned_station;
        this->health = 100;
    }

    int work(int hours)
    {
        if (hours < 0)
        {
            throw std::runtime_error("Cannot work negative hours");
        }
        int tasks_done = 0;
        int current_hour = 0;
        while (current_hour < hours)
        {
            if (this->health < 20)
            {
                std::cout << "Astronaut is too tired to work." << std::endl;
                break;
            }
            if (current_hour % 3 == 0)
            {
                current_hour = current_hour + 1;
                continue;
            }
            this->health = this->health - 10;
            tasks_done = tasks_done + 2;
            current_hour = current_hour + 1;
        }
        return tasks_done;
    }

    auto report()
    {
        if (this->assigned_station != nullptr)
        {
            this->assigned_station->printStatus();
            if (this->assigned_station->modules.size() > 0)
            {
                std::cout << "Primary module: " + this->assigned_station->modules[0] << std::endl;
            }
            if ((this->assigned_station->resource_levels.count("Oxygen") > 0))
            {
                int oxy = this->assigned_station->resource_levels["Oxygen"];
                std::cout << "Oxygen Level: " + std::to_string(oxy) << std::endl;
            }
        }
        else
        {
            std::cout << "No station assigned." << std::endl;
        }
    }

};

int main()
{
    try
    {
        SpaceStation* station = new SpaceStation("Alpha", 50);
        Astronaut* astro = new Astronaut("Ripley", 10, station);
        astro->report();
        int completed = astro->work(8);
        std::cout << "Tasks Completed: " + std::to_string(completed) << std::endl;
        std::cout << "Health remaining: " + std::to_string(astro->health) << std::endl;
        Astronaut* rookie = new Astronaut("Newb", 0, nullptr);
        rookie->report();
        rookie->work(-5);
    }
    catch (const std::exception& e)
    {
        std::cout << "Caught expected exception in Space Station" << std::endl;
    }
    return 0;
}
