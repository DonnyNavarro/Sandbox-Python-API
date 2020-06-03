import requests
import json
import reverse_geocode
import cmd
import urllib.parse
from datetime import datetime
from geopy.distance import geodesic 

def getIss():
    """Get ISS data"""
    # GET ISS INTERNATIONAL SPACE STATION LOCATION
    getIss = requests.get("http://api.open-notify.org/iss-now.json").json()

    # Store current iss data
    iss = {
        "time": datetime.fromtimestamp(getIss["timestamp"]),
        "timestamp": getIss["timestamp"],
        "coordinates": (getIss["iss_position"]["latitude"],getIss["iss_position"]["longitude"])
    }
    return iss

def displayIss(iss):
    """Display ISS Report"""
    print("|"+" "*(column_width-5),"Time:", iss["time"])
    print("|"+" "*(column_width-12),"Coordinates:",iss["coordinates"])

def getNearestLocation(iss):
    """Return the nearest city to the ISS"""
    
    nearestLocation = reverse_geocode.get(iss["coordinates"])
    # print("[debug] dumps",json.dumps(nearestGeodata))
    return nearestLocation

def getLocationCoordinates(location):
    geodata = requests.get('https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(location["city"]+","+location["country"]) +'?format=json').json()
    lat = geodata[0]["lat"]
    lon = geodata[0]["lon"]
    nearestCoordinates = (lat, lon)
    return nearestCoordinates

def displayDistance(coord1, coord2):
    """Return the distance between two coordinate sets"""
    distance = {
        "km": geodesic(coord1, coord2).km,
        "mi": geodesic(coord1, coord2).mi
    }
    distanceKm = round(distance["km"], 1) # cleanup decimals for display
    distanceMi = round(distance["mi"], 1) # cleanup decimals for display
    print("|"+" "*(column_width-12),"Coordinates:",coord2)
    print("|"+" "*(column_width-len("Distance from ISS:")),"Distance from ISS:", distanceKm,"km", "("+str(distanceMi),"miles)")

def displayLocation(location):
    """Display a report of the city"""
    print("|"+" "*(column_width-5),"City:", location["city"])
    print("|"+" "*(column_width-8),"Country:", location["country"])
    
class prompt(cmd.Cmd):
    """Command line input prompt"""
    prompt = ": "

    def emptyline(self):
        return False

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_where(self, arg):
        """Display the location of the International Space Station"""
        return True

if __name__ == '__main__':
    column_width = 20
    pagebreak = 65
    running = True

    while running == True:
        print(" "+"-"*pagebreak)
        print("| International Space Station")
        print(" -"*int(pagebreak/2))
        iss = getIss()
        displayIss(iss)

        print(" "+"-"*pagebreak)
        print("| Nearest Earth City")
        print(" -"*int(pagebreak/2))
        nearest = getNearestLocation(iss)
        displayLocation(nearest)
        displayDistance(iss["coordinates"], getLocationCoordinates(nearest))

        print(" "+"-"*pagebreak)

        prompt().cmdloop()