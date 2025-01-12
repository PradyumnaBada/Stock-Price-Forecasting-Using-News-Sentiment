import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

# Load the .env file
load_dotenv()

# Access variables
API_KEYS = [
    os.getenv("ALPHA_API_KEY_1"),
    os.getenv("ALPHA_API_KEY_2"),
    os.getenv("ALPHA_API_KEY_3"),
    os.getenv("ALPHA_API_KEY_4")
]

# Parameters
TICKERS = ["TSLA", "AMZN", "NVDA"]  
start_date = datetime.strptime("20220410T0130", "%Y%m%dT%H%M")
end_date_limit = datetime.strptime("20250110T0130", "%Y%m%dT%H%M") 

# Function to switch API keys
api_key_index = 0

def get_api_key():
    global api_key_index
    return API_KEYS[api_key_index % len(API_KEYS)]

# Iterate through tickers and 2-month windows
for TICKER in TICKERS:
    current_start_date = start_date
    while current_start_date < end_date_limit:
        current_end_date = current_start_date + timedelta(days=60)
        if current_end_date > end_date_limit:
            current_end_date = end_date_limit

        # Format dates for the API
        time_from = current_start_date.strftime("%Y%m%dT%H%M")
        time_to = current_end_date.strftime("%Y%m%dT%H%M")

        # Try different API keys if rate limit is reached
        while True:
            api_key = get_api_key()
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={TICKER}&time_from={time_from}&time_to={time_to}&limit=1000&apikey={api_key}'
            response = requests.get(url)
            data = response.json()

            if "Information" in data and "rate limit" in data["Information"].lower():
                print(f"Rate limit reached for API key {api_key}. Switching to next key.")
                api_key_index += 1
            else:
                break

        # Save the data to a JSON file
        output_file = f"data/New_data/{TICKER}_{time_from}_to_{time_to}.json"
        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Data saved to {output_file}")

        # Update the start date for the next iteration
        current_start_date = current_end_date
