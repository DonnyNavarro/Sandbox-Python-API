import requests
import cmd
import os
import json
from datetime import datetime
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))
# End ENV file setup

API_KEY = os.getenv("NASA_API_KEY") # Stored in .env

def checkAsteroids(startdate):
    global lastdate
    asteroids = requests.get('https://api.nasa.gov/neo/rest/v1/feed?start_date='+startdate+'&api_key='+API_KEY).json()

    # Grab a list of all the dates in the data
    #   We will use this list to iterate through the data
    allDates = []
    for dateRaw in asteroids["near_earth_objects"]:
        # Organize the dates in the return into a list and save the last one so we can start there on the next loop
        allDates.append(dateRaw)
        allDates.sort()

    lastdate = allDates[-1]
    for date in allDates:
        print(" "+"-"*pagewidth)
        print("| Report for",date)

        # Start each day presuming there are no threats
        todayThreat = False

        # Check each asteroid in this date
        for asteroid in asteroids["near_earth_objects"][date]:
            if asteroid["is_potentially_hazardous_asteroid"] == True:
                todayThreat = True
                newThreat = {
                    asteroid["name"]: {
                        "time": asteroid["close_approach_data"][0]["close_approach_date_full"],
                        "velocity": {
                            "kmps": asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"],
                            "kmph": asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"],
                            "mph": asteroid["close_approach_data"][0]["relative_velocity"]["miles_per_hour"]
                        },
                        "diameter": {
                            "minimum": asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"],
                            "maximum": asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]
                        }
                    }
                }
                # Check for missing times and replace them with the projection date
                if newThreat[asteroid["name"]]["time"] == None:
                    newThreat[asteroid["name"]]["time"] = date

                # Add the new threat to our threat tracker
                threats[asteroid["name"]] = newThreat[asteroid["name"]]
                
                # Print the new threat stats
                print(" -"*int(pagewidth/2))
                print("|   <ALARM> Potentially Hazardous Asteroid <ALARM>")
                displayAsteroid(newThreat)
                print("|") # Break between day reports

        if not todayThreat:
            print("|   <CLEAR> There will be no threats on",date)

            print("|") # Break between day reports
    print(" "+"-"*pagewidth)
    return lastdate

def displayAsteroid(asteroid):
    for name in asteroid:
        print(" -"*(int(pagewidth/2)))
        print("|         Name:",name)
        print("|         Time:",asteroid[name]["time"])
        print("|     Velocity:",round(float(asteroid[name]["velocity"]["mph"]),2),"mph")
        print("|     Diameter:",round(asteroid[name]["diameter"]["minimum"],2),"to",round(asteroid[name]["diameter"]["maximum"],2),"meters")

def biggestYet():
    global threats
    biggestSize = 0
    biggest = {} # Asteroid data for the biggest asteroid in threats
    for asteroid in threats:
        if threats[asteroid]["diameter"]["maximum"] > biggestSize:
            biggest = {}
            biggestSize = threats[asteroid]["diameter"]["maximum"]
            biggest[asteroid] = threats[asteroid]
    return biggest

def fastestYet():
    global threats
    fastestSpeed = 0
    fastest = {} # Asteroid data for the fastest asteroid in threats
    for asteroid in threats:
        if float(threats[asteroid]["velocity"]["mph"]) > fastestSpeed:
            fastest = {}
            fastestSpeed = float(threats[asteroid]["velocity"]["mph"])
            fastest[asteroid] = threats[asteroid]
    return fastest

class prompt(cmd.Cmd):
    """Command line input prompt"""
    prompt = " (Type <help> to see available commands)\n: "

    def emptyline(self):
        return False

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_check(self, arg):
        """Check for upcoming asteroid threats. Each time will check the following week."""
        global startdate
        startdate = checkAsteroids(startdate)
        return True

    def do_biggest(self, arg):
        biggest = biggestYet()
        if biggest:
            print(" "+"-"*pagewidth)
            print("| Biggest asteroid")
            print("| Threatening Earth between",firstdate,"and",lastdate)
            displayAsteroid(biggest)
            print(" "+"-"*pagewidth)
        else:
            print(" No threats found between",firstdate,"and",lastdate)
            print("Run <check> to find threats.")

    def do_fastest(self, arg):
        fastest = fastestYet()
        if fastest:
            print(" "+"-"*pagewidth)
            print("| Fastest asteroid")
            print("| Threatening Earth between",firstdate,"and",lastdate)
            displayAsteroid(fastest)
            print(" "+"-"*pagewidth)
        else:
            print(" No threats found between",firstdate,"and",lastdate)
            print("Run <check> to find threats.")

    def do_save(self, arg):
        """Save the threats that have been checked"""
        # Save files with datetime to make each file unique and avoid overwriting
        time = datetime.today().strftime('-%Y-%m-%d-%H%M%S')
        with open("logs/threats"+time+".json", "w") as outfile:
            json.dump(threats, outfile, indent=4)

    def do_threats(self, arg):
        global threats
        print(threats)

if __name__ == '__main__':
    running = True
    firstdate = datetime.today().strftime('%Y-%m-%d')
    startdate = firstdate # change this var to send api requests with different start dates
    lastdate = firstdate # gets updated at the end of each run so we know what the last report was
    threats = {}
    pagewidth = 50

    while running == True:
        prompt().cmdloop()

# TODO: At the end of each week check, print the fastest and the largest asteroids found to date