import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import pandas as pd
# Load the .env file
load_dotenv()

# Access the API key
API_KEY = os.getenv("ALPHA_API_KEY_1")

# Default parameters
DEFAULT_START_DATE = datetime.strptime("20220410T0130", "%Y%m%dT%H%M")
DEFAULT_END_DATE_LIMIT = datetime.strptime("20250110T0130", "%Y%m%dT%H%M")

def api_call(ticker,time_from, time_to):
    time_from = time_from.strftime("%Y%m%dT%H%M")
    time_to = time_to.strftime("%Y%m%dT%H%M")
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&time_from={time_from}&time_to={time_to}&limit=1000&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data

def fetch_news_data(ticker, start_date=None, end_date_limit=None):
    # Use default dates if not provided
    if start_date is None:
        start_date = DEFAULT_START_DATE
    if end_date_limit is None:
        end_date_limit = DEFAULT_END_DATE_LIMIT

    current_start_date = start_date
    while current_start_date < end_date_limit:
        current_end_date = current_start_date + timedelta(days=60)
        if current_end_date > end_date_limit:
            current_end_date = end_date_limit

        # Make the API request
        data = api_call(ticker,current_start_date, current_end_date)

        if len(data) == 1 or 'feed' not in data:
            print(f"Rate limit or invalid response for API key {API_KEY}.")
            break
        # Save the data to a JSON file
        time_from_str = current_start_date.strftime("%Y%m%dT%H%M")
        time_to_str = current_end_date.strftime("%Y%m%dT%H%M")
        output_file = f"data/New_data/{ticker}_{time_from_str}_to_{time_to_str}.json"
        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Data saved to {output_file}")

        # Update the start date for the next iteration
        current_start_date = current_end_date

def extract_data(data,ticker):
    req_data = [
                    {
                        'stock': x['ticker'],
                        'summary': item['summary'],
                        'url': item['url'],
                        'time': item['time_published'],
                        'source': item['source'],
                        'ticker_sentiment_score': x['ticker_sentiment_score'],
                        'relevance': x['relevance_score'],
                    }
                    for item in data.get('feed', [])
                    for x in item.get('ticker_sentiment', [])
                    if x['ticker'] == ticker
                ]
    return req_data

def join_files():
    all_data = []
    for file_name in os.listdir("data/New_data/api_results"):
        if file_name.endswith(".json"):
            file_path = os.path.join("data/New_data/api_results", file_name)
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                
                # Extract the ticker from the file name
                ticker = file_name.split('_')[0]
                
                # Extract relevant details
                req_data = extract_data(data, ticker)
                all_data.extend(req_data)

    # Create a DataFrame
    df = pd.DataFrame(all_data)
    df.to_csv("data/New_data/processed/news_data.csv", index=False)
    return df

def weighted_sentiment(df):
    df_filter = df[df['relevance'] > 0.1]
    df_filter['time'] = pd.to_datetime(df_filter['time'], format='%Y%m%dT%H%M%S')
    df_filter = df_filter[df_filter['time'] <= '2025-01-10 01:30:00']
    df_filter['date'] = df_filter['time'].dt.date
    df_filter['sentiment'] = df_filter['ticker_sentiment_score'] * df_filter['relevance']

    # Group by stock and date, then calculate the sum of weighted sentiments
    grouped_sentiment = df_filter.groupby(['stock', 'date']).agg(weighted_sentiment=('sentiment', 'sum')).reset_index()
    grouped_sentiment.to_csv("data/New_data/processed/weighted_sentiment.csv", index=False)
    # # Group by stock and date, then calculate the mean of positive and negative sentiments separately
    # grouped_sentiment = df_filter.groupby(['stock', 'date']).agg(
    #     positive_sentiment=('sentiment', lambda x: x[x > 0].mean()),
    #     negative_sentiment=('sentiment', lambda x: x[x < 0].mean())
    # ).reset_index()

    # # Fill NaN values with 0 for positive and negative sentiments
    # grouped_sentiment['positive_sentiment'].fillna(0, inplace=True)
    # grouped_sentiment['negative_sentiment'].fillna(0, inplace=True)
    # grouped_sentiment['WeightedSentiment'] = grouped_sentiment['positive_sentiment'] + grouped_sentiment['negative_sentiment']

    return grouped_sentiment


