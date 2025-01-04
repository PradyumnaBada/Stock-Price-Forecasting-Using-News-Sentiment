import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure Selenium WebDriver
def get_webdriver():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--log-level=3")  # Suppress logs
    driver = webdriver.Chrome(service=Service(r"C:\Users\prady\Downloads\chromedriver-win32\chromedriver.exe"), options=options)
    return driver

# Scrape NASDAQ News
def scrape_nasdaq_news():
    url = "https://www.nasdaq.com/market-activity/stocks/aapl/news-headlines"
    driver = get_webdriver()
    driver.get(url)

    articles = []
    page_number = 1

    try:
        while True:
            print(f"Scraping page {page_number}...")

            # Wait for the articles to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "jupiter22-c-article-list__item"))
            )

            # Find all news items on the page
            news_items = driver.find_elements(By.CLASS_NAME, "jupiter22-c-article-list__item")
            for item in news_items:
                try:
                    # Extract headline
                    headline = item.find_element(By.CLASS_NAME, "jupiter22-c-article-list__item_title_wrapper").text

                    # Extract link
                    link = item.find_element(By.CLASS_NAME, "jupiter22-c-article-list__item_title_wrapper").get_attribute("href")

                    # Extract category
                    category = item.find_element(By.CLASS_NAME, "jupiter22-c-article-list__item_category").text

                    # Extract time and publisher
                    timestamp = item.find_element(By.CLASS_NAME, "jupiter22-c-article-list__item_timeline").text
                    publisher = item.find_element(By.CLASS_NAME, "jupiter22-c-article-list__item_publisher").text

                    # Add to articles list
                    articles.append({
                        "Headline": headline,
                        "Link": link,
                        "Category": category,
                        "Time": timestamp,
                        "Publisher": publisher
                    })
                except Exception as e:
                    print(f"Error extracting article: {e}")

            # Check for the "Next" button and navigate
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "pagination__next"))
                )
                if next_button.get_attribute("disabled") == "true":
                    print("No more pages available.")
                    break
                next_button.click()
                time.sleep(2)
                page_number += 1
            except Exception:
                print("No next page button found.")
                break
    finally:
        driver.quit()

    # Save articles to CSV
    df = pd.DataFrame(articles)
    df.to_csv("nasdaq_news_aapl.csv", index=False)
    print(f"Scraping complete! {len(articles)} articles saved to 'nasdaq_news_aapl.csv'.")

# Run the script
if __name__ == "__main__":
    scrape_nasdaq_news()
