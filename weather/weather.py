import requests
import json
import cmd
import reverse_geocode
import pytemperature
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

apikey = os.getenv("APIKEY_OPENWEATHERMAP")
columnwidth = 15

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
    cityWeather = sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)
    return cityWeather

def getCoordWeather(coords):
    """Get today's weather for a given set of coordinates"""
    lat = str(coords[0])
    lon =  str(coords[1])
    coordWeather = sendRequest('https://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lon+'&appid='+apikey)
    print()
    print("Nearest city:")
    displayNearestCity(coords)
    return coordWeather

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
    response = requests.get(url).json()
    responsePrint = json.dumps(response, indent=4)
    # Display today's weather for city, state
    print()
    print("Request response received:")
    print(responsePrint)
    return response

def convertTemp(kelvin):
    celsius = round(pytemperature.k2c(kelvin), 2) # Kelvin to Celsius
    farenheit = round(pytemperature.k2f(kelvin), 2) # Kelvin to Fahrenheit

    converted = {
        "celsius": celsius,
        "farenheit": farenheit
    }
    return converted

def displayTemps(weather):
    """Display all the temperature data within a weather response object"""
    tempTypes = ["temp","feels_like","temp_min","temp_max"]
    for key in weather["main"]:
        if key in tempTypes:
            thisTemp = convertTemp(weather["main"][key])
            rowName = key.title()+"."*(columnwidth-len(key.title()))
            thisCels = str(thisTemp["celsius"])+" celsius"+"."*(columnwidth-(len(str(thisTemp["celsius"]))+len("celsius")))
            thisFare = str(thisTemp["farenheit"])+" farenheit"
            print(rowName+thisCels+thisFare)

def getTestcases(filename="testcases"):
    """Return testcases as an object based on a local JSON file"""
    with open(filename+".json") as testcases:
        # Return the testcases file as a python dictionary
        return json.load(testcases)

def displayTestcases(tcs):
    """Display currently readied testcases"""
    for tc in tcs:
        print(tc,tcs[tc])

def getNextTestcase(tcs):
    """Remove a tc from tcsToRun and return it"""
    for tc in tcs:
        return {tc: tcs.pop(tc)}

# Load a dictionary of testcases
testcases = getTestcases()
displayTestcases(testcases)
# Create a dictionary of testcases, to have tcs removed as they are run
tcsToRun = testcases
# Grab a tc from tcToRun and queue it up
nextTestCase = getNextTestcase(tcsToRun)
print("Next TC to run:",nextTestCase)
print("TCs still pending:",tcsToRun)

# TODO: Consider whether it is better to track our todo list as a dictionary with full tc details or to just make a list of the keys
# print("[debug]",testcases.keys())

# # Examples and testing
# testCoords = (37.22, -93.3)
# # getCoordWeather(testCoords)

# test = getCityWeather("Tallahassee")
# print("Location"+"."*(columnwidth-len("Location"))+test["name"])
# displayTemps(test)

