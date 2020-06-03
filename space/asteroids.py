import requests
import cmd
import os
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))
# End ENV file setup

API_KEY = os.getenv("NASA_API_KEY") # Stored in .env

def checkAsteroids(startdate):

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
        print(" "+"-"*50)
        print("| Report for",date)

        # Check each asteroid in this date
        threats = []
        for asteroid in asteroids["near_earth_objects"][date]:
            if asteroid["is_potentially_hazardous_asteroid"] == True:
                threats.append(asteroid["name"])
                print("| <ALARM> Potentially Hazardous Asteroid:",asteroid["name"])

        if not threats:
            print("| <CLEAR> There will be no threats on",date)

        print("|") # Break between day reports
    
    return lastdate

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
        """Check for upcoming asteroid threats"""
        global startdate
        startdate = checkAsteroids(startdate)
        return True

if __name__ == '__main__':
    running = True
    startdate = "2020-06-02"

    while running == True:
        prompt().cmdloop()