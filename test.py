import requests
import json

# testrequest = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx&q=New+York&date=2020-04-20&key=62bb496255964e918cf142535200406"
# # testrequest = "http://api.open-notify.org/astros.json"

# # print(json.dumps(requests.get(testrequest).json(), indent=4))
# print(requests.get(testrequest))


import operator
ops = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne
}

comparisonType = ">"
print(ops[comparisonType](1,2))

# if (1,greaterthan,2):
#     print("1 greater than 2")
# else:
#     print("1 less than 2")