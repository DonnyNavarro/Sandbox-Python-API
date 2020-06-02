import requests
import json
from datetime import datetime
import reverse_geocode

# VISUAL DISPLAY PARAMETERS
column_width = 20
pagebreak = 65

# GET ISS INTERNATIONAL SPACE STATION LOCATION
getIss = requests.get("http://api.open-notify.org/iss-now.json").json()

# Store current iss data
iss = {
    "time": datetime.fromtimestamp(getIss["timestamp"]),
    "timestamp": getIss["timestamp"],
    "coordinates": (getIss["iss_position"]["latitude"],getIss["iss_position"]["longitude"])
}
# Find the nearest city of the iss coordinates and store it with the current iss data
iss["nearestLocation"] = reverse_geocode.get(iss["coordinates"])

# DISPLAY ISS
print(" "+"-"*pagebreak)
print("| International Space Station")
print(" -"*int(pagebreak/2))
print("|"+" "*(column_width-5),"Time:", iss["time"])
print("|"+" "*(column_width-12),"Coordinates:",iss["coordinates"])

# GET COORDINATES OF ESTIMATED LOCATION CITY
#   Find the coordinates of the city identified as nearest the ISS,
#   so we can compare them to the ISS coordinates and determine how close 
#   the nearest city is to the space station
# TODO: Need sanity check or improved syntax for cases where the nearest location data isn't able to be matched to coordinates
import urllib.parse
nearestLocation = iss["nearestLocation"]["city"]+", "+iss["nearestLocation"]["country"]
getCityCoordinates = requests.get('https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(nearestLocation) +'?format=json').json()
lat = getCityCoordinates[0]["lat"]
lon = getCityCoordinates[0]["lon"]
iss["nearestLocation"]["coordinates"] = (lat, lon)

# DISPLAY NEAREST EARTH CITY
print(" "+"-"*pagebreak)
print("| Nearest Earth City")
print(" -"*int(pagebreak/2))
print("|"+" "*(column_width-5),"City:", iss["nearestLocation"]["city"])
print("|"+" "*(column_width-8),"Country:", iss["nearestLocation"]["country"])
print("|"+" "*(column_width-12),"Coordinates:",iss["nearestLocation"]["coordinates"])

# # DISTANCE BETWEEN NEAREST ISS AND NEAREST CITY
from geopy.distance import geodesic 
iss["nearestLocation"]["distance"] = {
    "km": geodesic(iss["coordinates"], iss["nearestLocation"]["coordinates"]).km,
    "mi": geodesic(iss["coordinates"], iss["nearestLocation"]["coordinates"]).mi
}
distanceKm = round(iss["nearestLocation"]["distance"]["km"], 1) # cleanup decimals for display
distanceMi = round(iss["nearestLocation"]["distance"]["mi"], 1) # cleanup decimals for display
print("|"+" "*(column_width-len("Distance from ISS:")),"Distance from ISS:", distanceKm,"km", "("+str(distanceMi),"miles)")

# END
print(" "+"-"*pagebreak)