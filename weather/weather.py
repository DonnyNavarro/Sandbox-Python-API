import requests
import json
import cmd
import reverse_geocode
import pytemperature
import operator
ops = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne
}

# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

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
    print("[debug]",kelvin)
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

def testTodayWeather(city, tc):
    """Execute a test on a city's weather based on the parameters in the tc"""
    for name in tc:
        print("Running Test Case:",(name).title())
        testName = (name).title()
        testValue = tc[name]["test value"]
        threshold = tc[name]["fail threshold"]
        comparison = tc[name]["fail comparison"]
        testThresholdType = tc[name]["threshold type"] if "threshold type" in tc[name] else False

    testResponse = getCityWeather(city)

    actual = getActual(testValue, testResponse)
    if testThresholdType:
        convertedTemp = convertTemp(actual)
        actual = convertedTemp[testThresholdType]

    # Compare the actuals to the thresholds using the comparison operator
    if ops[comparison](actual,threshold):
        print(city+" | "+testName+"? <FAIL>",actual,"is",comparison,threshold)
    else:
        print(city+" | "+testName+"? <PASS>",actual,"is not",comparison,threshold)
    
def getActual(field, response):
    """Provide the name of a field and response data, and return the value in the data that corresponds to that field"""
    valueActualMap = {
        "temp": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "wind speed": response["wind"]["speed"]
    }
    return valueActualMap[field]

class prompt(cmd.Cmd):
    """Command line input prompt"""
    prompt = "\n (Type <help> to see available commands)\n: "

    def emptyline(self):
        return False

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_reload(self, arg):
        """Reload the testcase queue from scratch"""
        return True

    def do_load(self, arg):
        """Load a specific testcase to be run next, specified as an argument"""
        global nextTestCase
        nextTestCase = tcsToRun[arg]
        print("Next TC to run:",{arg: nextTestCase})

    def do_loadnext(self, arg):
        """Load the next testcase so that it is ready to be run"""
        # Grab a tc from tcToRun and queue it up
        global nextTestCase
        nextTestCase = getNextTestcase(tcsToRun)

    def do_next(self, arg):
        """Display the testcase that is current loaded to be run"""
        print("Next TC to run:",nextTestCase)

    def do_pending(self, arg):
        """Display the testcases that are still waiting to be run"""
        print("TCs still pending:",tcsToRun)

    def do_testnext(self, arg):
        """Run the next testcase. You can display what TC this will be with the <next> command"""
        testTodayWeather(nextTestCase)

    def do_test(self, arg):
        """Run a specfic testcase immediately, specified as an argument"""
        if not city:
            print("ERROR: Use the <city> command to specify a city!")
        else:
            if arg in testcases:
                testTodayWeather(city, {arg: testcases[arg]})     
            else:
                print("ERROR: Please specify which testcase to test!")

    def do_try(self, arg):
        """Send a request for today's weather to a city, specified as an argument"""
        getCityWeather(arg)

    def do_city(self, arg):
        if arg:
            global city
            city = (arg).title()

if __name__ == '__main__':
    running = True
    apikey = os.getenv("APIKEY_OPENWEATHERMAP")
    columnwidth = 15
    global city

    while running == True:
        testcases = getTestcases() # Load a dictionary of testcases
        tcsToRun = testcases # Create a dictionary of testcases, to have tcs removed as they are run
        nextTestCase = {}
        displayTestcases(testcases)
        prompt().cmdloop()

# TODO: Consider whether it is better to track our todo list as a dictionary with full tc details or to just make a list of the keys
# print("[debug]",testcases.keys())

# # Examples and testing
# testCoords = (37.22, -93.3)
# # getCoordWeather(testCoords)

# test = getCityWeather("Tallahassee")
# print("Location"+"."*(columnwidth-len("Location"))+test["name"])
# displayTemps(test)

