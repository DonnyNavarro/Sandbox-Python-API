import requests
import json
import cmd
# External ENV file support
#   Then we can store secure environmentals in the .env file, and grab them with os.getenv("varname")
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('') # local path
load_dotenv(os.path.join(project_folder, '.env'))

city = "Tallahassee"

# Sanitize city name
city = city.replace(" ", "+")

# GET TODAY'S WEATHER FOR CITY
url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&appid='+os.getenv("APIKEY_OPENWEATHERMAP")
todayWeather = json.dumps(requests.get(url).json(), indent=4)

# DISPLAY TODAY'S WEATHER FOR CITY
print(todayWeather)

