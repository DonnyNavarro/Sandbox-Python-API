import requests
import json

testrequest = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx&q=New+York&date=2020-04-20&key=62bb496255964e918cf142535200406"
# testrequest = "http://api.open-notify.org/astros.json"

# print(json.dumps(requests.get(testrequest).json(), indent=4))
print(requests.get(testrequest))
