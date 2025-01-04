from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

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
        print(f"Scraping page {page + 1}...")
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

# Example usage
def main():
    query = 'site:nasdaq.com "Apple stock financial news"'
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    max_pages = 10000  # Adjust based on requirements

    # Scrape Google Search results
    df = scrape_google_dynamic(query, start_date, end_date, max_pages)

    # Save results to a CSV
    if not df.empty:
        df.to_csv("apple_2024_news_urls.csv", index=False)
        print(f"Scraping complete! Saved {len(df)} results to 'apple_2024_news_urls.csv'.")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
