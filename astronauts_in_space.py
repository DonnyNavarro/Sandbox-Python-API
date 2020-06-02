import requests
import json

# Get the response from the API endpoint.
response = requests.get("http://api.open-notify.org/astros.json")
data = response.json()

print(" "+"-"*47)
# The number of people in space
print("|",data["number"],"Humans currently offworld")

print(" "+"-"*47)
# Names of people in space
for person in data["people"]:
    print("| Location:", person["craft"],"| Name:",person["name"])
    
print(" "+"-"*47)