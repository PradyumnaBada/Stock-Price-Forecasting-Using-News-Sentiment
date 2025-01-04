import yfinance as yf
import pandas as pd
import ast
import requests
from datetime import datetime, timedelta
import pickle
import os



def prepare_new_data(tickers, filepath=None, start_date='2023-12-12', end_date= '2024-05-10',mean=0,df=None):
    if df is None:
        df = pd.read_csv(filepath)  
    else:
        df = df
        if df.empty:
            return None 
    df['Date'] = pd.to_datetime(df['date']).dt.date
    #df['Stock_symbol'] = tickers
    def convert_string_to_dict(string):
        try:
            return ast.literal_eval(string)
        except ValueError:
            return {}
    if filepath is not None:
        df['sentiment'] = df['sentiment'].apply(convert_string_to_dict)    
 
    df_expanded = pd.DataFrame(df['sentiment'].tolist())
    df_other_columns = df.drop('sentiment', axis=1)
    df = pd.concat([df_other_columns, df_expanded], axis=1)
    df['Date'] = pd.to_datetime(df['date']).dt.date
    #df['WeightedSentiment'] =  (df['pos'] * 1) + (df['neg'] * -1)
    daily_sentiments = df.groupby(['Date']).agg({
        'polarity': 'sum',
        'pos': 'sum',
        'neg': 'sum',
        'neu': 'sum',
        #'WeightedSentiment': 'sum'
    }).reset_index()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    all_dates_df = pd.DataFrame(all_dates, columns=['Date'])
    all_dates_df['Date'] = pd.to_datetime(all_dates_df['Date']).dt.date
    full_data = pd.merge(all_dates_df, daily_sentiments, on='Date', how='left')
    full_data['WeightedSentiment'] =  (full_data['polarity'] * 0.5) + (full_data['neg'] * -(mean)) + (full_data['pos'] * (mean)) 
    full_data['Stock_symbol'] = tickers
    #full_data.rename(columns={'polarity': 'WeightedSentiment', 'pos': 'positive', 'neg': 'negative', 'neu': 'neutral'}, inplace=True)
    full_data.rename(columns={'pos': 'positive', 'neg': 'negative', 'neu': 'neutral'}, inplace=True)
    full_data = full_data[[ 'Date','Stock_symbol', 'positive' , 'neutral','negative', 'WeightedSentiment']]
    return full_data


def fetch_data(tickers, start_date, end_date):
    sentiment_data = pd.read_csv('data_with_wieghted_sentiment.csv')
    sentiment_data = sentiment_data[sentiment_data['Stock_symbol'] == tickers]
    sentiment_data['RollingSentiment'] = sentiment_data['WeightedSentiment'].rolling(window=30).mean()
    mean_sentiment = sentiment_data['RollingSentiment'].mean()
    recent_data = prepare_new_data(tickers, filepath=f'{tickers}.US_news_api_recent.csv',mean=mean_sentiment)
    live_news = fetch_live_data(tickers, to_date = end_date)
    #print(live_news)
    live_data = prepare_new_data(tickers, mean=mean_sentiment,df=live_news,start_date='2024-05-10', end_date=end_date)
    sentiment_data = pd.concat([sentiment_data, recent_data, live_data], ignore_index=True)
    sentiment_data['Date'] = pd.to_datetime(sentiment_data['Date'])
    sentiment_data['RollingSentiment'] = sentiment_data['WeightedSentiment'].rolling(window=30).mean()
    data = yf.download(tickers, start=start_date, end=end_date)
    narrowed_data = data['Adj Close'].reset_index()
    final = narrowed_data.merge(sentiment_data, on='Date', how='left')

    if end_date >= datetime.strptime('2024-05-10', '%Y-%m-%d').date():
        sentiments = live_news['sentiment'].to_list() 
        news_text = pd.DataFrame(sentiments)
        live_news = live_news.reset_index()
        news_text = pd.concat([live_news, news_text], axis=1)
        news_text = news_text.loc[:10, ['title', 'link', 'polarity']]
    elif end_date >= datetime.strptime('2024-01-01', '%Y-%m-%d').date():
        old_news = pd.read_csv(f'{tickers}.US_news_api_recent.csv')
        def convert_string_to_dict(string):
            try:
                return ast.literal_eval(string)
            except ValueError:
                return {}
        old_news['sentiment'] = old_news['sentiment'].apply(convert_string_to_dict)    
        sentiments = old_news['sentiment'].to_list() 
        news_text = pd.DataFrame(sentiments)
        news_text = pd.concat([old_news, news_text], axis=1)
        news_text['date'] = pd.to_datetime(news_text['date']).dt.date
        #print(news_text)
        news_text = news_text.loc[news_text['date'] <= end_date, ['title', 'link', 'polarity']]
        news_text = news_text.loc[:10, ['title', 'link', 'polarity']]
    else:
        news_text = pd.DataFrame()
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

def fetch_live_data(stock, to_date, from_date='2024-05-10'):
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
        primary_url = f'https://eodhd.com/api/news?s={stock}.US&offset=0&api_token=663c5bd6c54c50.39283508&fmt=json&from={from_date}&to={to_date}&limit=1000'
        secondary_url = f'https://eodhd.com/api/news?s={stock}.US&offset=0&api_token=663ea824aa3946.41816462&fmt=json&from={from_date}&to={to_date}&limit=1000'
        third_url = f'https://eodhd.com/api/news?s={stock}.US&offset=0&api_token=663ed06a3d2510.72818393&fmt=json&from={from_date}&to={to_date}&limit=1000'
        urls = [primary_url, secondary_url,third_url]

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    save_data_to_cache(stock, df)
                    return df
            except requests.exceptions.RequestException as e:
                continue  
            
    return pd.DataFrame()




