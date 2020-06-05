"""This file is a holding pen for stuff that is not immediately needed, but we built because it was fun"""
# Stuff in this file probably has dependancies in the main files, so this file probably won't run on its own

def displayTemps(weather):
    """Display all the temperature data within a weather response object"""
    # This is not really useful
    tempTypes = ["temp","feels_like","temp_min","temp_max"]
    for key in weather["main"]:
        if key in tempTypes:
            thisTemp = convertTemp(weather["main"][key])
            rowName = key.title()+"."*(columnwidth-len(key.title()))
            thisCels = str(thisTemp["celsius"])+" celsius"+"."*(columnwidth-(len(str(thisTemp["celsius"]))+len("celsius")))
            thisFare = str(thisTemp["farenheit"])+" farenheit"
            print(rowName+thisCels+thisFare)

def getCoordWeather(coords):
    """Get today's weather for a given set of coordinates"""
    # Not really needed, just another way of hitting the api for data
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
