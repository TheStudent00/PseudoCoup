using System;
using System.Collections.Generic;

public class SpaceStation
{

    public SpaceStation(string name, int capacity)
    {
        this.name = name;
        this.capacity = capacity;
        this.modules = new() { "Command", "Life Support", "Laboratory" };
        this.resource_levels = new() {{"Oxygen", 95}, {"Power", 100}};
    }

    public void printStatus()
    {
        Console.WriteLine("Station: " + this.name);
        Console.WriteLine("Capacity: ".ToString() + this.capacity.ToString());
    }

}

public class Astronaut
{

    public Astronaut(string name, int experience, SpaceStation assigned_station)
    {
        this.name = name;
        this.experience = experience;
        this.assigned_station = assigned_station;
        this.health = 100;
    }

    public int work(int hours)
    {
        if (hours < 0)
        {
            throw new Exception("Cannot work negative hours");
        }
        int tasks_done = 0;
        int current_hour = 0;
        while (current_hour < hours)
        {
            if (this.health < 20)
            {
                Console.WriteLine("Astronaut is too tired to work.");
                break;
            }
            if (current_hour % 3 == 0)
            {
                current_hour = current_hour + 1;
                continue;
            }
            this.health = this.health - 10;
            tasks_done = tasks_done + 2;
            current_hour = current_hour + 1;
        }
        return tasks_done;
    }

    public void report()
    {
        if (this.assigned_station != null)
        {
            this.assigned_station.printStatus();
            if (this.assigned_station.modules.Count > 0)
            {
                Console.WriteLine("Primary module: ".ToString() + this.assigned_station.modules[0].ToString());
            }
            if (this.assigned_station.resource_levels.ContainsKey("Oxygen"))
            {
                int oxy = this.assigned_station.resource_levels["Oxygen"];
                Console.WriteLine("Oxygen Level: ".ToString() + oxy.ToString());
            }
        }
        else
        {
            Console.WriteLine("No station assigned.");
        }
    }

}

public static void main()
{
    try
    {
        SpaceStation station = new SpaceStation("Alpha", 50);
        Astronaut astro = new Astronaut("Ripley", 10, station);
        astro.report();
        int completed = astro.work(8);
        Console.WriteLine("Tasks Completed: ".ToString() + completed.ToString());
        Console.WriteLine("Health remaining: ".ToString() + astro.health.ToString());
        Astronaut rookie = new Astronaut("Newb", 0, null);
        rookie.report();
        rookie.work(-5);
    }
    catch (Exception e)
    {
        Console.WriteLine("Caught expected exception in Space Station");
    }
}

public class Program
{
    public static void Main()
    {
    }
}
