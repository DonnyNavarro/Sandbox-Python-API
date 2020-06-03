import requests
import cmd
import os
API_KEY = os.environ['NASA_API_KEY'] # Stored in .env

startdate = "2020-06-02"
running = True
while running == True:

    asteroids = requests.get('https://api.nasa.gov/neo/rest/v1/feed?start_date='+startdate+'&api_key='+API_KEY).json()

    # Grab a list of all the dates in the data
    #   We will use this list to iterate through the data
    allDates = []
    for date in asteroids["near_earth_objects"]:
        # Organize the dates in the return and save the last one so we can start there on the next loop
        allDates.append(date)
        allDates.sort()
        lastdate = allDates[-1]
        print(date)

        # Check each asteroid in this date
        for asteroid in asteroids["near_earth_objects"][date]:
            if asteroid["is_potentially_hazardous_asteroid"] == True:
                print("<ALARM> Potentially Hazardous Asteroid:",asteroid["name"])
    
    print()
    startdate = lastdate
