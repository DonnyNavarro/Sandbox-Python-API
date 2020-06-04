import requests
import json
import cmd
import reverse_geocode
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

apikey = os.getenv("APIKEY_OPENWEATHERMAP")

def sanitize(arg, locType):
    """Sanitize variables for use in URLs"""
    #   Cities with spaces in their names
    #   States are optional
    if locType == "city":
        return arg.replace(" ", "+")

    if locType == "state":
        return ","+arg if arg != "" else ""

def getCityWeather(city, state=""):
    """Get today's weather for a given city. State is optional, but if given then it needs to be a full name and not initials"""
    # Today's weather API URL
    city = sanitize(city, "city")
    state = sanitize(state, "state")
    sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)

def getCoordWeather(coords):
    """Get today's weather for a given set of coordinates"""
    lat = str(coords[0])
    lon =  str(coords[1])
    sendRequest('https://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lon+'&appid='+apikey)
    print()
    print("Nearest city:")
    displayNearestCity(coords)

def displayNearestCity(coords):
    """Display the nearest city to a given pair of coordinates"""
    # Mostly for troubleshooting that locations returned are correct
    nearestLocation = reverse_geocode.get(coords)
    print(nearestLocation)
    # targetCoords = (todayWeather["coord"]["lat"], todayWeather["coord"]["lon"])

def sendRequest(url):
    """Send an api request and print the response"""
    # Get today's weather for city, state
    print()
    print("Sending GET request to")
    print(url)
    todayWeather = requests.get(url).json()
    responsePrint = json.dumps(todayWeather, indent=4)
    # Display today's weather for city, state
    print()
    print("Request response received:")
    print(responsePrint)

# Examples and testing
testCoords = (37.22, -93.3)
# getCoordWeather(testCoords)

getCityWeather("Springfield", "Illinois")