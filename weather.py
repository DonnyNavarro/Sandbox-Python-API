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

def sanitize(arg, type):
    # Sanitize Location Variables
    #   Cities with spaces in their names
    #   States are optional
    if "type" == "city":
        return arg.replace(" ", "+")
    if "type" == "state":
        return ","+arg if arg != "" else ""

def getCityWeather(city, state=""):
    #################################
    # GET TODAY'S WEATHER FOR CITY
    # Today's weather API URL
    sanitize(city, "city")
    sanitize(state, "state")
    sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)

def getCoordWeather(coords):
    lat = str(coords[0])
    lon =  str(coords[1])
    sendRequest('https://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lon+'&appid='+apikey)

def displayNearestCity(coords):
    nearestLocation = reverse_geocode.get(coords)
    print(nearestLocation)
    # targetCoords = (todayWeather["coord"]["lat"], todayWeather["coord"]["lon"])

def sendRequest(url):
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
getCoordWeather(testCoords)

getCityWeather("Orlando")