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

def loadJson(filename):
    """Load a local JSON file and return it as a dict"""
    with open(filename+".json") as dictionary:
        return json.load(dictionary)

def displayDict(dic):
    """Print a dict with pretty indentations"""
    print(json.dumps(dic, indent=4))

def sendRequest(url):
    """Hit the url with a GET request, display the response, and return it as a dict"""
    # Send GET request to the url
    print()
    print("Sending GET request to")
    print(url)
    response = requests.get(url)

    # Validate that the request succeeded
    if response.status_code != 200:
        print("Request failed: Status code",response.status_code)
        return False

    # Convert the response from JSON to dict
    responseJson = (response).json()
    # Display the request response
    print()
    print("Request response received:",response.status_code)
    displayDict(responseJson)
    return responseJson

def getCityWeather(city, state=""):
    """Get today's weather for a given city. State is optional, but if given then it needs to be a full name and not initials.
    Return a dict with the weather api response as well as location confirmation data."""
    # String requirements for city and state to be used in the api url
    city = city.replace(" ", "+")
    state = ","+state if state != "" else ""
    # Send the request
    cityWeather = sendRequest('https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+apikey)
    if cityWeather:
        # Grab the coordinates from the response, so we can verify they are the location we were hoping to get from the city we named
        location = matchLocation((cityWeather["coord"]["lat"], cityWeather["coord"]["lon"]))
        cityWeather["location"] = location
        return cityWeather
    else:
        return False

def matchLocation(coords):
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

        # Temperature testing needs to convert kelvin to human 
        if testThresholdType in ["farenheit", "celsius"] :
            if testThresholdType == "celsius":
                actual = round(pytemperature.k2c(actual), 2)
            elif testThresholdType == "farenheit":
                actual = round(pytemperature.k2f(actual), 2)

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

def getActual(field, response):
    """Provide the name of a field and response data, and return the value in the data that corresponds to that field"""
    valueActualMap = {
        "temp": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "wind speed": response["wind"]["speed"]
    }
    return valueActualMap[field]

def testCompare(actual, comparison, threshold):
    """Compare the actual to the threshold using the comparison operator. Returns Pass or Fail string"""
    if ops[comparison](actual,threshold):
        return "Fail"
    else:
        return "Pass"
    
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

def confirmPrompt():
    """Returns True only if the user responds to the prompt in the affirmative"""
    confirm = input("\nAccept? y/[n] ")
    if (confirm).lower() in ["y", "yes"]:
        return True

def chooseCities(options):
    """Prompt the user to choose cities and return a list of their selections"""
    cityQueue = []
    cityChoice = input("\nWhat cities would you like to test? ")
    cityChoice = cityChoice.title() # make pretty
    cityChoice = cityChoice.split(",") # each space indicates something to treat as a new list item
    # allow all as an easy option
    if cityChoice == ["All"]:
        cityChoice = options
    # if only one item is presented, make it a list so type handling is uniform
    cityChoice = [cityChoice] if type(cityChoice) == str else cityChoice 
    for key, val in enumerate(cityChoice):
        cityChoice[key] = val.strip()
        if cityChoice[key] in options:
            cityQueue.append(cityChoice[key])
        else:
            print("ERROR:",cityChoice[key],"is not among the cities in our scope.")
    if cityQueue:
        print("City Queue:",cityQueue)
        cityQueue = [] if not confirmPrompt() else cityQueue
        return cityQueue
    else:
        return False

def chooseTestcases(options):
    """Prompt the user to choose testcases and return a list of their selections"""
    testQueue = []
    testChoice = input("What testcases would you like to test? ")
    testChoice = testChoice.split(",") # each space indicates something to treat as a new list item
    # allow all as an easy option
    if testChoice == ["all"]:
        testChoice = [*testcases]
    # if only one item is presented, make it a list so type handling is uniform
    testChoice = [testChoice] if type(testChoice) == str else testChoice
    for key, val in enumerate(testChoice):
        testChoice[key] = val.strip()
        if testChoice[key] in testcases:
            testQueue.append(testChoice[key])
        else:
            print("ERROR:",testChoice[key],"is not among the available testcases.")
    if testQueue:
        print("Testcase Queue:",testQueue)
        testQueue = [] if not confirmPrompt() else testQueue
        return testQueue
    else:
        return False

class prompt(cmd.Cmd):
    """Command line input prompt"""
    prompt = "\n (Type <help> to see available commands)\n: "

    def emptyline(self):
        return False

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_tc(self, arg):
        """Display a list of testcases available"""
        print("Available Testcases:")
        displayDict(testcases)
    
    def do_scope(self, arg):
        """Display the options available in scope.json"""
        displayDict(scope)

    def do_try(self, arg):
        """Send a request for today's weather to a city, specified as an argument. Basically a dry run for pretesting."""
        getCityWeather(arg) if arg else print("Please provide a city to try")

    def do_test(self, arg):
        """Run a specfic testcase immediately, specified as an argument. Use the 'all' arg to run the entire testcase.json on the entire scope.json """

        # SELECT CITIES
        cityQueue = []
        while not cityQueue:
            print()
            print("Cities Available:")
            print(scope["cities"])
            cityQueue = chooseCities(scope["cities"])

        # SELECT TEST CASES
        testQueue = []
        while not testQueue:
            print()
            print("Testcases Available:")
            displayDict(testcases)
            testQueue = chooseTestcases(testcases)

        # RUN SELECTED TEST CASES AGAINST SELECTED CITIES
        collectedTcs = {}
        for place in cityQueue:
            for tc in testQueue:
                # Collect the tcs to test so they can all be run in a single city data request
                collectedTcs[tc] = testcases[tc]
            testTodayWeather(place, collectedTcs)

if __name__ == '__main__':
    running = True
    apikey = os.getenv("APIKEY_OPENWEATHERMAP")
    columnwidth = 15
    city = []
    testQueue = []
    testcases = loadJson("testcases")
    scope = loadJson("scope")
    commands = ["scope", "try", "test", "tc"]

    """Runtime loop"""
    # Splash Intro Screen
    print("Welcome to the Weather Tester")
    while running == True:
        print()
        print("The following commands are available:")
        displayDict(commands)
        # for cmd in commands:
        #     print(cmd)
        print("Type help <command> for more info")
            
        # COMMAND LINE PROMPT
        prompt().cmdloop()

# TODO: Remove coordinate lookup function (its hella slow) and replace it by assigning coordinates to cities in scope.json