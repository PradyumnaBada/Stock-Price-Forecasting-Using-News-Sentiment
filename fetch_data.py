import yfinance as yf
import pandas as pd
import ast
import requests
from datetime import datetime, timedelta
import pickle
import os
from news_api import fetch_news_data

def fetch_data(tickers, start_date, end_date):
    path = r"data\New_data\processed\\"
    sentiment_data = pd.read_csv(path + 'weighted_sentiment.csv')
    sentiment_data = sentiment_data[sentiment_data['Stock_symbol'] == tickers]
    live_news = fetch_live_data(tickers, to_date = end_date)
    #print(live_news)
    live_data = prepare_new_data(tickers, df=live_news,start_date='2024-05-10', end_date=end_date)
    sentiment_data = pd.concat([sentiment_data, live_data], ignore_index=True)
    sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
    sentiment_data['RollingSentiment'] = sentiment_data['WeightedSentiment'].rolling(window=30).mean()
    data = yf.download(tickers, start=start_date, end=end_date)
    narrowed_data = data['Adj Close'].reset_index()
    final = narrowed_data.merge(sentiment_data, on='Date', how='left')

    # For news text, find a way to send top 5 news for each day
    return final,news_text
    


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

def fetch_live_data(stock, to_date, from_date='2025-01-10'):
    """Fetch live data for a specific ticker if more than 6 hours have passed since the last fetch."""
    # Attempt to load cached data for the ticker
    cached_data = load_cached_data(stock)
    if cached_data is not None:
        #cached_data['date'] = pd.to_datetime(cached_data['date'])  
        cached_data['date'] = cached_data['date'].dt.tz_localize(None)
        cached_data = cached_data[cached_data['date'] <= pd.to_datetime(to_date)]
        return cached_data

    # Convert date strings to date objects
    from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    #to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    if to_date >= from_date:
        # Fetch news data using the function from news_api.py
        news_data = fetch_news_data(stock, from_date, to_date)

        if not news_data.empty:
            news_data['date'] = pd.to_datetime(news_data['date'])
            save_data_to_cache(stock, news_data)

            # Update the CSV with new data
            csv_path = r"data\New_data\processed\weighted_sentiment.csv"
            if os.path.exists(csv_path):
                existing_data = pd.read_csv(csv_path)
                updated_data = pd.concat([existing_data, news_data], ignore_index=True)
                updated_data.to_csv(csv_path, index=False)
            else:
                news_data.to_csv(csv_path, index=False)

            return news_data
            
    return pd.DataFrame()




