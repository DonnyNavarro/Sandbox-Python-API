import requests
import json
from datetime import datetime
import reverse_geocode

column_width = 15
pagebreak = 50

print(" "+"-"*pagebreak)
print("| International Space Station")
print(" "+"-"*pagebreak)
print("| Current Location in Realtime")
print("|")
# print(" "+"-"*pagebreak)

# GET SPACE STATION LOCATION
response = requests.get("http://api.open-notify.org/iss-now.json")
data = response.json()

# LOG TIME AND MAKE IT READABLE
timestamp = data["timestamp"]
now = datetime.fromtimestamp(timestamp)
print("|"+" "*(column_width-5),"Time:", now)

# GET LOCATION COORDINATES
longitude = data["iss_position"]["longitude"]
latitude = data["iss_position"]["latitude"]
coordinates = (longitude, latitude)
print("|"+" "*(column_width-12),"Coordinates:", str(coordinates))

# GET LOCATION OF COORDINATES
location = reverse_geocode.get(coordinates)
print("|"+" "*(column_width-8),"Country:", location["country"])
print("|"+" "*(column_width-5),"City:", location["city"])

print(" "+"-"*pagebreak)