from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from datetime import datetime, timedelta

def scrape_google_dynamic(query, start_date, end_date, max_pages=50):
    """
    Scrapes Google search results dynamically using Selenium.

    Args:
    - query (str): The search query.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.
    - max_pages (int): Maximum number of pages to scrape.

    Returns:
    - pandas.DataFrame: DataFrame containing extracted URLs and titles.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(r"C:\Users\prady\Downloads\chromedriver-win32\chromedriver.exe"), options=options)

    base_url = f"https://www.google.com/search?q={query}+after:{start_date}+before:{end_date}&tbm=nws"
    driver.get(base_url)
    all_results = []

    for page in range(max_pages):
        print(f"Scraping page {page + 1} for query: {query} from {start_date} to {end_date}...")
        time.sleep(2)  # Let the page load

        # Extract article links and titles
        articles = driver.find_elements(By.CSS_SELECTOR, "a.WlydOe")
        for article in articles:
            try:
                link = article.get_attribute("href")
                title = article.text
                all_results.append({"Title": title, "URL": link})
            except Exception as e:
                print(f"Error extracting article: {e}")

        # Check if the "Next" button exists and click it
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
        except Exception:
            print("No more pages found. Exiting.")
            break

    driver.quit()
    return pd.DataFrame(all_results)

def get_date_ranges(start_year, start_month, end_year, end_month, interval=2):
    """
    Generates start and end dates for specified intervals.

    Args:
    - start_year (int): Starting year.
    - start_month (int): Starting month.
    - end_year (int): Ending year.
    - end_month (int): Ending month.
    - interval (int): Interval in months.

    Returns:
    - list of (start_date, end_date) tuples.
    """
    ranges = []
    current_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    while current_date < end_date:
        start_date = current_date.strftime("%Y-%m-%d")
        next_date = current_date + timedelta(days=interval * 30)  # Approx. 2 months
        end_range = (next_date - timedelta(days=1)).strftime("%Y-%m-%d")  # End of 2-month range
        ranges.append((start_date, end_range))
        current_date = next_date

    return ranges

def main():
    stocks = ['Apple', 'Tesla', 'NVIDIA', 'Amazon']
    base_query = 'site:nasdaq.com "{stock} stock financial news"'
    start_year = 2023
    start_month = 11
    end_year = 2024
    end_month = 12
    max_pages = 50  # Adjust based on requirements

    # Generate date ranges
    date_ranges = get_date_ranges(start_year, start_month, end_year, end_month)

    for stock in stocks:
        for i, (start_date, end_date) in enumerate(date_ranges):
            query = base_query.format(stock=stock)
            print(f"Scraping for {stock}: Period {i+1} ({start_date} to {end_date})")
            
            # Scrape data
            df = scrape_google_dynamic(query, start_date, end_date, max_pages)

            # Save to CSV
            path = r"C:\Users\prady\OneDrive - University of Illinois - Urbana\Desktop\CS 498\final_project_new\data\New_data"
            filename = f"\{stock.lower()}_news_{start_date}_to_{end_date}.csv"
            if not df.empty:
                df.to_csv(path+filename, index=False)
                print(f"Saved {len(df)} results to '{filename}'.")
            else:
                print(f"No results found for {stock} from {start_date} to {end_date}.")

if __name__ == "__main__":
    main()
