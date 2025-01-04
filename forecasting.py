import pandas as pd
from prophet import Prophet
def prepare_data(df, date_col='Date', price_col='Adj Close', sentiment_col='WeightedSentiment'):
    """ Prepares data for Prophet modeling. """
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.rename(columns={date_col: 'ds', price_col: 'y', sentiment_col: 'sentiment'})
    return df

def add_lagged_features(data, lag_days=7, rolling_window=30):
    """ Add lagged and rolling features to the DataFrame. """
    # Lagged features
    data['lagged_sentiment'] = data['sentiment'].shift(lag_days)

    # Rolling mean of sentiment
    data['rolling_sentiment'] = data['sentiment'].rolling(window=rolling_window, min_periods=1).mean()
    
    return data


def forecast_with_lags(data, lag_days=7, rolling_window=30):

    df = prepare_data(data, date_col='Date', price_col='Adj Close', sentiment_col='WeightedSentiment')
    df = add_lagged_features(df, lag_days=lag_days, rolling_window=rolling_window)
    df.dropna(inplace=True)
    m = Prophet()
    m.add_country_holidays(country_name='US')
    m.add_regressor('sentiment')
    m.add_regressor('lagged_sentiment')
    m.add_regressor('rolling_sentiment')
    m.fit(df)
    
    last_date = df['ds'].max()

    future_dates = m.make_future_dataframe(periods=7, include_history=False, freq='D')

    last_week_sentiment = df[['sentiment', 'lagged_sentiment', 'rolling_sentiment']].tail(7)

    future_sentiments = pd.concat([last_week_sentiment] * 1, ignore_index=True)

    future_dates = pd.concat([future_dates.reset_index(drop=True), future_sentiments.reset_index(drop=True)], axis=1)

    forecast = m.predict(future_dates)

    return forecast[['ds','yhat']]