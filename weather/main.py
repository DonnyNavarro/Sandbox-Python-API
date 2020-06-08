import requests
import json
import cmd
import reverse_geocoder
import pytemperature
from datetime import datetime
from os import path

"""String operator support."""
# This enables us to set inequality parameters in the testcase json and use them cleanly to make comparisons in the code
import operator
ops = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne
}

"""External ENV file support (API KEY)"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

def sendRequest(url):
    """Hit the url with a GET request, display the response, and return it as a dict"""
    # Send GET request to the url
    print()
    print("Sending GET request to")
    print(url)
    response = requests.get(url).json()
    # Display the request response
    print()
    print("Request response received:")
    displayDict(response)
    return response

def displayLocation(coords):
    """Looks up coords and uses an api request to print and return detailed location data"""
    # Get location data for the coords from an api
    print("Referencing third party for details on coordinates location:")
    locationDetails = reverse_geocoder.search(coords)
    # Only display county if it is in the location data
    city2 = "("+locationDetails[0]["admin2"]+")" if locationDetails[0]["admin2"] else "" 
    # Print the location data
    print("     City:",locationDetails[0]["name"],city2)
    print("  Country:",locationDetails[0]["admin1"]+", "+locationDetails[0]["cc"])
    # Return the location data as a dict so it can be stored in reports etc
    location = {
        "city": locationDetails[0]["name"]+" ("+locationDetails[0]["admin2"]+")",
        "country": locationDetails[0]["admin1"]+", "+locationDetails[0]["cc"]
    }
    return location

def sanitize(arg, argType):
    """Sanitize variables for use in URLs"""
    #   Cities with spaces in their names
    #   States are optional
    if argType == "city":
        return arg.replace(" ", "+")

    if argType == "state":
        return ","+arg if arg != "" else ""

def getCityWeather(city, state=""):
    """Get today's weather for a given city. State is optional, but if given then it needs to be a full name and not initials.
    Return a dict with the weather api response as well as location confirmation data."""
    # Today's weather API URL
    city = sanitize(city, "city")
    state = sanitize(state, "state")
    cityWeather = sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)
    location = displayLocation((cityWeather["coord"]["lat"], cityWeather["coord"]["lon"]))
    cityWeather["location"] = location
    return cityWeather

def convertTemp(kelvin, scale, rounding=2):
    """Convert kelvin numbers into another temperature scale and round the result to a number of decimal places."""
    if scale == "celsius":
        return round(pytemperature.k2c(kelvin), rounding)
    elif scale == "farenheit":
        return round(pytemperature.k2f(kelvin), rounding)
    else:
        return False

def loadJson(filename):
    """Load a local JSON file and return it as a dict"""
    with open(filename+".json") as dictionary:
        return json.load(dictionary)

def displayDict(dic):
    """Print a dict with pretty indentations"""
    print(json.dumps(dic, indent=4))

def testTodayWeather(city, tc):
    """Execute a test on a city's weather based on the parameters in the tc"""
    # Send the test call and store the response for evaluation
    results = {}
    results[city] = {}
    results[city]["testing"] = {}
    testResponse = getCityWeather(city)
    results[city]["response"] = testResponse
    # Run each test that is present within the tc object
    print()
    print("Testing city:",(city).title())
    for test in tc:
        testName = (test).title()
        testValue = tc[test]["test value"]
        threshold = tc[test]["fail threshold"]
        comparison = tc[test]["fail comparison"]
        testThresholdType = tc[test]["threshold type"] if "threshold type" in tc[test] else ""

        actual = getActual(testValue, testResponse)

        # Temperature testing needs to be converted from kelvin
        actual = convertTemp(actual, testThresholdType) if testThresholdType in ["farenheit", "celsius"] else actual

        # Test the actual against the tc criteria
        print()
        print(".....testing: "+testName+"?")
        result = testCompare(actual, comparison, threshold)
        print("< "+result+" >",actual,"compared to",comparison,threshold,testThresholdType)
        
        # Store the test results for later reference
        results[city]["testing"][test] = {
            "result": result,
            "time": datetime.today().strftime('%Y-%m-%d-%H%M%S'),
            "testcase": tc[test],
            "actual": {
                "tested value": actual
            }
        }
        # Save the test results as a local log file
        # saveLog(results, city+"-"+testName)
    saveLog(results, city)

def saveLog(saveStuff, tag=""):
    """Save saveStuff as a file in the local folder "logs" as a .json file. If used, tag will append a string to the filename and store the log in a folder named the tag string"""
    time = datetime.today().strftime('-%Y-%m-%d-%H%M%S')
    subfolder = tag
    filenameAppend = tag
    # If we are adding to the end of the filename
    if filenameAppend != "":
        filenameAppend = "-"+filenameAppend
        filenameAppend = filenameAppend.replace(" ","_")
    # If we are storing in a subfolder
    if subfolder != "":
        subfolder = subfolder+"/"
        # Make the subfolder if it doesn't exist
        os.mkdir("logs/"+subfolder) if not os.path.exists("logs/"+subfolder) else False
    # Save the log file
    with open("logs/"+subfolder+"results"+time+filenameAppend+".json", "w") as outfile:
        json.dump(saveStuff, outfile, indent=4)

def testCompare(actual, comparison, threshold):
    """Compare the actual to the threshold using the comparison operator. Returns Pass or Fail string"""
    if ops[comparison](actual,threshold):
        return "Fail"
    else:
        return "Pass"
    
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

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_list(self, arg):
        """Display a list of testcases available"""
        print("Available Testcases:")
        for tc in testcases:
            print(" ",(tc).title())

    def do_test(self, arg):
        """Run a specfic testcase immediately, specified as an argument"""
        if not arg:
            print("Testcases Available:")
            displayDict(testcases)
        print()
        print("City to test:",city) if city else print("ERROR: Use the <city> command to specify a city before using this command!")
        if arg in testcases and city:
            testTodayWeather(city, {arg: testcases[arg]})     
        else:
            print("ERROR: Please specify which testcase to test as an argument!")

    def do_try(self, arg):
        """Send a request for today's weather to a city, specified as an argument"""
        # TODO: Should this command also save the city used for future use?
        if not arg:
            if not city:
                print("ERROR: Either specify a city as an argument or use the <city> command to do so.")
            else:
                getCityWeather(city)
        else:
            getCityWeather(arg)

    def do_city(self, arg):
        """Saves a city name as the city to be used in tests"""
        if arg:
            global city
            city = (arg).title()
        else:
            if not city:
                print("ERROR: Please specify a city name when using this command.")
            else:
                print("Current city target:",city)
                print("  (Use this command with an argument to set that argument as the new city target.)")

    def do_fullrun(self, arg):
        """Run every testcase on every aspect of the scope"""
        for city in scope["cities"]:
            testTodayWeather(city, testcases)

if __name__ == '__main__':
    running = True
    apikey = os.getenv("APIKEY_OPENWEATHERMAP")
    columnwidth = 15
    city = ""

    while running == True:
        """Runtime loop"""
        # Splash Intro Screen
        print("Welcome to the weather tester")

        # Testcases: load local json into dict and display it to the user
        print()
        print("Testcases available:")
        testcases = loadJson("testcases") # Load a dictionary of testcases
        displayDict(testcases)

        # Scope: load local json into dict and display it to the user
        print()
        print("Scope available:")
        scope = loadJson("scope")
        displayDict(scope)

        # COMMAND LINE PROMPT
        prompt().cmdloop()

# TODO: Cycle through cities based on the local scope.json file
# TODO: Save function should be flexible for bulk running to create subfolders...city/testcase/datetime ?
# TODO: Remove coordinate lookup function (its hella slow) and replace it by assigning coordinates to cities in scope.json