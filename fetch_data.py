import os
import pickle
import ast
from datetime import datetime, timedelta

import pandas as pd
import requests
import yfinance as yf

from news_api import *
def fetch_data(tickers, start_date, end_date):
    path = os.path.join("data", "New_data", "processed")
    sentiment_data = pd.read_csv(path + 'weighted_sentiment.csv')
    news_data = pd.read_csv(path + 'news_data.csv')
    sentiment_data = sentiment_data[sentiment_data['Stock_symbol'] == tickers]
    news_data = news_data[news_data['stock'] == tickers]
    # Check if end_date is beyond the existing data
    latest_date = sentiment_data['date'].max()
    latest_time = news_data['time'].max()
    if pd.to_datetime(end_date) >= pd.to_datetime(latest_date):
        current_time = datetime.now().strftime("%Y%m%dT%H%M")
        live_data = fetch_live_data(tickers, from_date=latest_time, to_date=current_time)
        sentiment_data = pd.concat([sentiment_data, live_data], ignore_index=True)
    
    sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
    sentiment_data.rename(columns={'date': 'Date'}, inplace=True)
    sentiment_data['RollingSentiment'] = sentiment_data['WeightedSentiment'].rolling(window=30).mean()
    data = yf.download(tickers, start=start_date, end=end_date)
    narrowed_data = data['Adj Close'].reset_index()
    final = narrowed_data.merge(sentiment_data, on='Date', how='left')
    news_data = news_data.sort_values(by='time', ascending=False)
    news_data = news_data[news_data['relevance'] > 0.6].head(10)
    # Get the top 
    return final, news_data

# File path for saving data
CACHE_FILE_PATH = 'api_data_cache.pkl'

def load_cached_data(ticker):
    """ Load cached data for a specific ticker from a pickle file. """
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'rb') as file:
            cache = pickle.load(file)
            # Check if the cache for the specific ticker is valid (less than 6 hours old)
            if ticker in cache and datetime.now() - cache[ticker]['timestamp'] < timedelta(hours=6):
                return cache[ticker]['data']
    return None

def save_data_to_cache(ticker, data):
    """ Save data to a pickle file with a timestamp for a specific ticker. """
    cache = {}
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'rb') as file:
            cache = pickle.load(file)
    with open(CACHE_FILE_PATH, 'wb') as file:
        cache[ticker] = {'data': data, 'timestamp': datetime.now()}
        pickle.dump(cache, file)

def fetch_live_data(ticker, from_date, to_date):
    """Fetch live data for a specific ticker if more than 6 hours have passed since the last fetch."""
    # Attempt to load cached data for the ticker
    cached_data = load_cached_data(ticker)
    if cached_data is not None:
        cached_data['date'] = pd.to_datetime(cached_data['date']).dt.tz_localize(None)
        cached_data = cached_data[cached_data['date'] <= pd.to_datetime(to_date)]
        return cached_data

    if to_date >= from_date:
        # Fetch news data using the function from news_api.py
        news_data = api_call(ticker, from_date, to_date)
        processed_data = extract_data(ticker, news_data, from_date, to_date)
        weighted_sentiment = weighted_sentiment(processed_data)

        if not weighted_sentiment.empty:
            weighted_sentiment['date'] = pd.to_datetime(weighted_sentiment['date'])
            save_data_to_cache(ticker, weighted_sentiment)

            # Update the CSV with new data
            csv_path = os.path.join("data", "New_data", "processed", "weighted_sentiment.csv")
            if os.path.exists(csv_path):
                existing_data = pd.read_csv(csv_path)
                updated_data = pd.concat([existing_data, weighted_sentiment], ignore_index=True)
                updated_data.to_csv(csv_path, index=False)
            else:
                weighted_sentiment.to_csv(csv_path, index=False)

            # Store processed_data in news_data.csv
            processed_csv_path = os.path.join("data", "New_data", "processed", "news_data.csv")
            if os.path.exists(processed_csv_path):
                existing_processed_data = pd.read_csv(processed_csv_path)
                updated_processed_data = pd.concat([existing_processed_data, processed_data], ignore_index=True)
                updated_processed_data.to_csv(processed_csv_path, index=False)
            else:
                processed_data.to_csv(processed_csv_path, index=False)

            return weighted_sentiment
            
    return pd.DataFrame()




