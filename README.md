# Stock Price Forecasting Using News Sentiment Analysis

## Purpose

This project aims to enhance stock price forecasting by integrating sentiment analysis of financial news articles. The primary objectives are:

1. **Historical Analysis**: To understand the correlation between stock prices and the sentiment expressed in news articles, helping to identify how positive or negative news impacts stock market movements.

2. **Predictive Forecasting**: To predict future stock prices based on historical price trends and the sentiment derived from the latest news articles, providing a comprehensive tool for investors and analysts.

3. **Stay Updated**: Get the latest news articles related to interested company depending on the dates.

## Domain of Application

This application is designed for financial analysts, quantitative researchers, and algorithmic traders. It sits at the intersection of finance, data science, and computational linguistics, employing advanced techniques from each field to predict stock market trends. By leveraging cutting-edge natural language processing (NLP) and machine learning algorithms, it provides insights that traditional analysis might overlook, making it especially useful in volatile and rapidly changing markets.

## Setup Instructions

### Prerequisites

- Python 3.8 or newer.
- pip (Python package installer).
- uv

### Installation

1. **Clone the Repository**
2. **Install Requirements.txt**


### Initial Data Setup

Due to logistical constraints, the initial data setup involves steps that are challenging to reproduce directly:

Data Procurement: The initial dataset, sourced from the FNSPID Financial News Dataset(https://github.com/Zdong104/FNSPID_Financial_News_Dataset), comprises approximately 30 GB of financial news articles.

Sentiment Analysis: Sentiments of these articles were extracted using a pretrained language model, which required significant computational resources and time.

Data Gap Filling: To address a 5-month gap in the dataset, an open-source (https://eodhd.com/financial-apis/stock-market-financial-news-api) news API was utilized to fetch recent news and their sentiments. This API is available only on a limited trial basis, and my usage has maxed out.

Note: Processed data after these initial steps is included in the repository for ease of access and reproducibility.

### Data APIs and Tools
Latest News and Stock Prices: For ongoing updates, the EOD Historical Data API is used along with yfinance(https://pypi.org/project/yfinance/) for real-time stock price retrieval.

Forecasting: Stock price forecasting is performed using the Prophet library, which is capable of handling daily seasonality patterns in time series data.

### Usage
After setting up the project, launch the Streamlit dashboard to interact with the historical data analyses and stock price forecasts:

streamlit run app.py

Navigate through the dashboard to view graphical representations of data correlations, sentiment analysis, and price forecasts. Select different stocks and adjust parameters to see how news sentiment potentially affects stock prices.

Dashboard
The Streamlit dashboard provides a user-friendly interface similar to Shiny apps, featuring:

Interactive plots of stock prices and news sentiment over time.
Options to select different stocks and forecast horizons.
Live updates of news sentiment and stock prices.

### Special instruction for the usage of streamlit:

I’ve utilized Streamlit to develop an interactive web application that forecasts stock prices using sentiment analysis derived from news articles. Here's a breakdown of how I've applied various Streamlit functions to build and manage different components of the application:

Streamlit Functions Used in My Project
st.set_page_config:

This was my starting point, setting the layout to 'wide' which utilizes more screen space and setting the page title and icon that appears in the browser tab.
st.title:

I used this function to add a main title to the application, "News Sentiment and Stocks," which gives a clear indication of what the application is about right at the top.
st.tabs:

To organize the content neatly, I divided the application into three main tabs: Historical, Forecast, and Details. This helps in separating functionalities and keeping the user interface clean.
st.sidebar:

The sidebar is crucial for user inputs. It houses controls like date input fields and sliders, allowing users to specify parameters like the start and end date for data they wish to view, and settings for the forecast like the number of days to predict.
st.date_input:

Within the sidebar, I used st.date_input for users to pick start and end dates for the data they want to analyze or forecast. This makes the application dynamic, letting users explore different time frames.
st.selectbox:

This function lets users select a stock from predefined options. It populates based on the symbols list, allowing users to choose which company's stock data they want to view.
st.slider:

Sliders are used to let the user define how many days into the future they want to forecast stock prices and how many historical days they want to consider for their forecast. This interaction makes the forecast feature flexible and user-driven.
st.pyplot:

For visual representation, I plotted graphs using Matplotlib and displayed them in the Streamlit app using st.pyplot. This visual output includes stock price trends and sentiment analysis results over time.
st.markdown:

To add formatted text and links that provide additional context or information, I used st.markdown. This is especially useful in the "Details" tab and for displaying links in news items related to the stocks.
Streamlit vs. Shiny
Comparing Streamlit to Shiny, which I've also used in other class projects, I find Streamlit to be particularly user-friendly, especially since it allows for rapid development and deployment. Its simplicity is ideal for Python users like myself, enabling quick iterations without the steep learning curve associated with Shiny's reactive programming model.

Shiny, on the other hand, is incredibly powerful for creating highly interactive web applications and offers more control and flexibility, especially for users deeply embedded in the R ecosystem. It's great for statistical modeling and visualization but requires a good grasp of R.

Overall, my experience with Streamlit has been very positive, especially for integrating Python-based data science workflows. It allows me to focus more on data analysis and less on web development intricacies, making it an excellent tool for educational projects and quick demonstrations

