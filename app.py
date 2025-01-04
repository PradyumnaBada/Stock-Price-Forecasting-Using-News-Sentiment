import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fetch_data import fetch_data
from forecasting import forecast_with_lags
from datetime import datetime

st.set_page_config(layout='wide', page_title="Stock Data and Forecasting", page_icon=":bar_chart:", initial_sidebar_state="expanded")


plt.style.use('ggplot')  

st.title('News Sentiment and Stocks')

symbols = ['AAPL', 'TSLA', 'NVDA', 'AMZN']
symb_dict = {'AAPL': 'Apple', 'TSLA': 'Tesla', 'NVDA': 'Nvidia', 'AMZN': 'Amazon'}
company_names = [symb_dict[symbol] for symbol in symbols]
# Create tabs
tab1, tab2, tab3 = st.tabs(["Historical", "Forecast", "Details"])

def display_news(symbol, news_df):
    """Display news items with sentiment indicators."""
    st.subheader(f"Latest News related to {symbol}")
    for idx, row in news_df.iterrows():
        sentiment = "🟢 Positive" if row['polarity'] > 0 else "🔴 Negative"
        news_item = f"{sentiment} [{row['title']}]({row['link']})"
        st.markdown(news_item, unsafe_allow_html=True)

with tab1:
    st.header("Historical Stock Data")
    # Sidebar controls specific to historical data
    with st.sidebar:
        st.subheader("Historical Data Settings")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", value=pd.to_datetime("2021-09-01"), key='start_historical')
        with col2:
            end_date = st.date_input("End date", value=pd.to_datetime("2024-05-10"), key='end_historical')
        if start_date > end_date:
            st.error('Error: End date must fall after start date.')
        selected_index = st.selectbox('Select a company:',range(len(company_names)),  
         format_func=lambda x: company_names[x])
        symbol_selection = symbols[selected_index]


    # Fetch and plot historical data
    data, news = fetch_data(symbol_selection, start_date, end_date)


    def plot_stock(data, symbol_selection):
        fig, ax1 = plt.subplots(figsize=(10, 5))
        # Improved plot aesthetics
        ax1.plot(data['Date'], data['Adj Close'], label='Stock Price', color='dodgerblue', marker='o', linestyle='-', markersize=4)
        ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Stock Price', color='dodgerblue', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='dodgerblue', labelsize=10)
        ax1.set_title(f'Stock Prices and News Sentiment for {symb_dict[symbol_selection]}', fontsize=14, fontweight='bold', color='black')
        ax1.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

        # Secondary axis for sentiment
        ax2 = ax1.twinx()
        ax2.plot(data['Date'], data['RollingSentiment'], label='News Sentiment', color='limegreen', marker='s', linestyle='--', markersize=4)
        ax2.set_ylabel('News Sentiment', color='limegreen', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='limegreen', labelsize=10)

        # Enhancing the legend
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left', frameon=True, framealpha=0.8, facecolor='white')

        st.pyplot(fig)

    plot_stock(data, symbol_selection)
    display_news(symb_dict[symbol_selection], news)



with tab2:

    # Sidebar controls specific to forecasting
    with st.sidebar:
        st.subheader("Forecast Settings")
        days_to_forecast = st.slider("Days to Forecast", min_value=1, max_value=14, value=7, step=1, key='days_forecast')
        days_of_historical_data = st.slider("Number of Historical Days", min_value=30, max_value=90, value=60, step=5, key='historical_days')
    st.header(f"Forecast for {days_to_forecast} Days")
    historical_start_date = pd.to_datetime(end_date) - pd.DateOffset(days=days_of_historical_data)
    historical_end_date = pd.to_datetime(end_date)
    data['Date'] = pd.to_datetime(data['Date'])
    historical_data_filtered = data[(data['Date'] >= historical_start_date) & (data['Date'] <= pd.to_datetime(end_date) )]

    forecast_results = forecast_with_lags(data, lag_days=days_to_forecast)
    forecast_results = forecast_results.rename(columns={'yhat': 'Adj Close', 'ds': 'Date'})
    new_data = pd.concat([historical_data_filtered, forecast_results], ignore_index=True)

    plot_stock(new_data, symbol_selection)
    display_news(symb_dict[symbol_selection], news)



with tab3:
    st.header("Details")
    st.write("This application is designed for financial analysts, quantitative researchers, and \
                algorithmic traders. It sits at the intersection of finance, data science, and computational\
                 linguistics, employing advanced techniques from each field to predict stock market trends. By leveraging cutting-edge natural language processing (NLP) and machine learning algorithms, it provides insights that traditional analysis might overlook, making it especially useful in volatile and rapidly changing markets.")
