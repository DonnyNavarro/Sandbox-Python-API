import requests
import json
from datetime import datetime
import reverse_geocode
import time

# VISUAL DISPLAY PARAMETERS
column_width = 20
pagebreak = 65
running = True
iss = {}
nearestLocation = {}
nearestLocation["city"] = False

while running:
    # GET ISS INTERNATIONAL SPACE STATION LOCATION
    getIss = requests.get("http://api.open-notify.org/iss-now.json").json()

    # Store current iss data
    iss = {
        "time": datetime.fromtimestamp(getIss["timestamp"]),
        "timestamp": getIss["timestamp"],
        "coordinates": (getIss["iss_position"]["latitude"],getIss["iss_position"]["longitude"]),
    }
    
    checkNearest = reverse_geocode.get(iss["coordinates"])
    # print("[debug] checkNearest",checkNearest["city"],"nearestLocation",nearestLocation["city"])
    if checkNearest["city"] is not nearestLocation["city"]:
        newCity = True
    else:
        newCity = False

    nearestLocation = reverse_geocode.get(iss["coordinates"])
    # GET COORDINATES OF ESTIMATED LOCATION CITY
    #   Find the coordinates of the city identified as nearest the ISS,
    #   so we can compare them to the ISS coordinates and determine how close 
    #   the nearest city is to the space station. Otherwise displaying 
    #   the nearest city can be very misleading, especially when over oceans
    # TODO: Need sanity check or improved syntax for cases where the nearest location data isn't able to be matched to coordinates
    import urllib.parse
    nearestLocation["id"] = nearestLocation["city"]+", "+nearestLocation["country"]
    getCityCoordinates = requests.get('https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(nearestLocation["id"]) +'?format=json').json()
    lat = getCityCoordinates[0]["lat"]
    lon = getCityCoordinates[0]["lon"]
    nearestLocation["coordinates"] = (lat, lon)

    # DISTANCE BETWEEN NEAREST ISS AND NEAREST CITY
    from geopy.distance import geodesic 
    nearestLocation["distance"] = {
        "km": geodesic(iss["coordinates"], nearestLocation["coordinates"]).km,
        "mi": geodesic(iss["coordinates"], nearestLocation["coordinates"]).mi
    }
    distanceKm = round(nearestLocation["distance"]["km"], 1) # cleanup decimals for display
    distanceMi = round(nearestLocation["distance"]["mi"], 1) # cleanup decimals for display

    
    # DISPLAY: 
    #   Only update the display when ISS is closest to a new city
    if newCity:

        # DISPLAY ISS
        print(" "+"-"*pagebreak)
        print("| International Space Station")
        print(" -"*int(pagebreak/2))
        print("|"+" "*(column_width-5),"Time:", iss["time"])
        print("|"+" "*(column_width-12),"Coordinates:",iss["coordinates"])

        # DISPLAY NEAREST EARTH CITY
        print(" "+"-"*pagebreak)
        print("| Nearest Earth City")
        print(" -"*int(pagebreak/2))
        print("|"+" "*(column_width-5),"City:", nearestLocation["city"])
        print("|"+" "*(column_width-8),"Country:", nearestLocation["country"])
        print("|"+" "*(column_width-12),"Coordinates:",nearestLocation["coordinates"])
        print("|"+" "*(column_width-len("Distance from ISS:")),"Distance from ISS:", distanceKm,"km", "("+str(distanceMi),"miles)")

        # END
        print(" "+"-"*pagebreak)
    else:
        print("Distance to",nearestLocation["city"]+",",nearestLocation["country"]+":", distanceKm,"km", "("+str(distanceMi),"miles)")
    # PAUSE
    # for seconds in range(10):
    time.sleep(2)
    # # CLEAR TERMINAL
    # print(chr(27) + "[2J")