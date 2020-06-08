This project is intended to create an example of a Python testing approach.

In this example we will:
- Define test cases in a local JSON
- Define test scope in a local JSON
- Use an API call to get a JSON of test data
- Use a python commandline app to:
  - Select which testcases to run
  - Select how much of the scope to run
  - Execute the selected testcases across the scope against the API response actuals
  - Export the results of our testing as a JSON

# Setup
1. You will need Python 3
2. You may need to `pip install` modules that are imported
3. You will need to get an API key from 
  - Create a `.env` file in the main folder
  - In this file add `APIKEY_OPENWEATHERMAP = "your_api_key_here"`
4. Run `python3 main.py`