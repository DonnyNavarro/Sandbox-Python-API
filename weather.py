import requests
import json
import cmd
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

####################
# LOCATION TARGET
# State is optional, default is empty string
state = ""
# City to check weather for
city = "Tallahassee"

# Sanitize Location Variables
#   Cities with spaces in their names
#   States are optional
city = city.replace(" ", "+")
state = ","+state if state != "" else ""

#################################
# GET TODAY'S WEATHER FOR CITY
# Today's weather API URL
url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+state+'&appid='+os.getenv("APIKEY_OPENWEATHERMAP")
# Get today's weather for city, state
todayWeather = json.dumps(requests.get(url).json(), indent=4)
# Display today's weather for city, state
print(todayWeather)

