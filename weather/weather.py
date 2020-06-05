import requests
import json
import cmd
import reverse_geocoder
import pytemperature
from datetime import datetime

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

"""External ENV file support"""
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

def sendRequest(url):
    """Hit the url with a GET request and display the response"""
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

    location = displayLocation((response["coord"]["lat"], response["coord"]["lon"]))
    response["location"] = location
    return response

def displayLocation(coords):
    """Looks up coords and finds more detailed location data to verify what place it is precisely"""
    print("Referencing third party for details on coordinates location:")
    locationDetails = reverse_geocoder.search(coords)
    print("     City:",locationDetails[0]["name"]+" ("+locationDetails[0]["admin2"]+")")
    print("  Country:",locationDetails[0]["admin1"]+", "+locationDetails[0]["cc"])
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
    """Get today's weather for a given city. State is optional, but if given then it needs to be a full name and not initials"""
    # Today's weather API URL
    city = sanitize(city, "city")
    state = sanitize(state, "state")
    cityWeather = sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)
    return cityWeather

def convertTemp(kelvin):
    """Convert kelvin into a dictionary with both farenheit and celsius"""
    celsius = round(pytemperature.k2c(kelvin), 2) # Kelvin to Celsius
    farenheit = round(pytemperature.k2f(kelvin), 2) # Kelvin to Fahrenheit

    converted = {
        "celsius": celsius,
        "farenheit": farenheit
    }
    return converted

def getTestcases(filename="testcases"):
    """Return testcases as an object based on a local JSON file"""
    with open(filename+".json") as testcases:
        # Return the testcases file as a python dictionary
        return json.load(testcases)

def displayTestcases(tcs):
    """Display currently readied testcases"""
    print(" AVAILABLE TEST CASES:")
    for tc in tcs:
        print(" - Test Case: \""+(tc).title()+"\" fail if",tcs[tc]["test value"],tcs[tc]["fail comparison"],tcs[tc]["fail threshold"])

def getNextTestcase(tcs):
    """Remove a tc from tcsToRun and return it"""
    for tc in tcs:
        return {tc: tcs.pop(tc)}

def getScope(filename="scope"):
    """Return scope as an object based on a local JSON file"""
    with open(filename+".json") as scope:
        # Return the scope file as a python dictionary
        return json.load(scope)

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
        if testThresholdType in ["farenheit", "celsius"]:
            convertedTemp = convertTemp(actual)
            actual = convertedTemp[testThresholdType]

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

def saveLog(saveStuff, organize=""):
    """Save saveStuff as a file in the local folder "logs" as a .json file"""
    time = datetime.today().strftime('-%Y-%m-%d-%H%M%S')
    subfolder = organize
    filenameAppend = organize
    # If we are adding to the end of the filename
    if filenameAppend != "":
        filenameAppend = "-"+filenameAppend
        filenameAppend = filenameAppend.replace(" ","_")
    # If we are storing in a subfolder
    if subfolder != "":
        subfolder = subfolder+"/"
        os.mkdir("logs/"+subfolder)
    with open("logs/"+subfolder+"results"+time+filenameAppend+".json", "w") as outfile:
        json.dump(saveStuff, outfile, indent=4)

def testCompare(comparing, comparison, compareto):
    # Compare the actuals to the thresholds using the comparison operator
    if ops[comparison](comparing,compareto):
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

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, arg):
        """Close the program"""
        quit()

    """The following functions are an attempt to create a queuing system, but needs to be improved"""
    # def do_reload(self, arg):
    #     """Reload the testcase queue from scratch"""
    #     return True

    # def do_load(self, arg):
    #     """Load a specific testcase to be run next, specified as an argument"""
    #     global nextTestCase
    #     nextTestCase = tcsToRun[arg]
    #     print("Next TC to run:",{arg: nextTestCase})

    # def do_loadnext(self, arg):
    #     """Load the next testcase so that it is ready to be run"""
    #     # Grab a tc from tcToRun and queue it up
    #     global nextTestCase
    #     nextTestCase = getNextTestcase(tcsToRun)

    # def do_next(self, arg):
    #     """Display the testcase that is current loaded to be run"""
    #     print("Next TC to run:",nextTestCase)

    # def do_pending(self, arg):
    #     """Display the testcases that are still waiting to be run"""
    #     print("TCs still pending:",tcsToRun)

    # def do_testnext(self, arg):
    #     """Run the next testcase. You can display what TC this will be with the <next> command"""
    #     testTodayWeather(nextTestCase)

    def do_list(self, arg):
        """Display a list of testcases available"""
        print("Available Testcases:")
        for tc in testcases:
            print(" ",(tc).title())

    def do_test(self, arg):
        """Run a specfic testcase immediately, specified as an argument"""
        if not city:
            print("ERROR: Use the <city> command to specify a city before using this command!")
        else:
            if arg in testcases:
                testTodayWeather(city, {arg: testcases[arg]})     
            else:
                print("ERROR: Please specify which testcase to test as an argument!")
                print("  (View a list of available testcases with the <list> command.)")

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
    global city
    city = ""

    while running == True:
        # Load the test cases we want available
        testcases = getTestcases("testcases") # Load a dictionary of testcases
        tcsToRun = testcases # Create a dictionary of testcases, to have tcs removed as they are run
        nextTestCase = {}
        displayTestcases(testcases)
        # Load the scope we want available
        scope = getScope("scope")
        # COMMAND LINE PROMPT
        prompt().cmdloop()

# TODO: Consider whether it is better to track our todo list as a dictionary with full tc details or to just make a list of the keys
# print("[debug]",testcases.keys())
# TODO: Cycle through cities based on the local scope.json file
# TODO: Save function should be flexible for bulk running to create subfolders...city/testcase/datetime ?
# TODO: Remove coordinate lookup function (its hella slow) and replace it by assigning coordinates to cities in scope.json