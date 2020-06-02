import requests
import json
from datetime import datetime
import reverse_geocode

column_width = 17
pagebreak = 65

print(" "+"-"*pagebreak)
print("| International Space Station")

# GET ISS INTERNATIONAL SPACE STATION LOCATION
response = requests.get("http://api.open-notify.org/iss-now.json")
data = response.json()

# LOG TIME AND MAKE IT READABLE
timestamp = data["timestamp"]
now = datetime.fromtimestamp(timestamp)
print("|"+" "*(column_width-5),"Time:", now)

# GET ISS COORDINATES
longitude = data["iss_position"]["longitude"]
latitude = data["iss_position"]["latitude"]
issCoordinates = (longitude, latitude)
print("|"+" "*(column_width-12),"Coordinates:", str(issCoordinates))

# GET NEAREST CITY TO ISS COORDINATES
locationRaw = reverse_geocode.get(issCoordinates)
country = locationRaw["country"]
city = locationRaw["city"]
print(" "+"-"*pagebreak)
print("| Nearest Earth City")
print("|"+" "*(column_width-5),"City:", city)
print("|"+" "*(column_width-8),"Country:", country)


# GET COORDINATES OF ESTIMATED LOCATION CITY
#   Find the coordinates of the city identified as nearest the ISS,
#   so we can compare them to the ISS coordinates and determine how close 
#   the nearest city is to the space station
import urllib.parse
location = city+", "+country
getCityCoordinates = requests.get('https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(location) +'?format=json').json()
lat = getCityCoordinates[0]["lat"]
lon = getCityCoordinates[0]["lon"]
cityCoordinates = (lat, lon)
print("|"+" "*(column_width-12),"Coordinates:",cityCoordinates)

print(" "+"-"*pagebreak)

# DISTANCE BETWEEN NEAREST ISS AND NEAREST CITY