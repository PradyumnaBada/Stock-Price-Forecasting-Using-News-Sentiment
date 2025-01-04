import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def generate_google_search_url(query, after_date, before_date, page_number):
    """
    Generates a Google search URL for news results with pagination and date filtering.

    Args:
    - query (str): The search query.
    - after_date (str): Start date in the format YYYY-MM-DD.
    - before_date (str): End date in the format YYYY-MM-DD.
    - page_number (int): The desired page number (1-based indexing).

    Returns:
    - str: The constructed Google search URL.
    """
    start = (page_number - 1) * 10
    url = (
        f"https://www.google.com/search?"
        f"q={query.replace(' ', '+')}+after:{after_date}+before:{before_date}"
        f"&tbm=nws&start={start}"
    )
    return url

def scrape_google_results(query, after, before, max_pages=20):
    """
    Scrapes Google Search results dynamically using requests and BeautifulSoup.

    Args:
    - query (str): The search query.
    - after (str): Start date in 'YYYY-MM-DD' format.
    - before (str): End date in 'YYYY-MM-DD' format.
    - max_pages (int): Number of pages to scrape.

    Returns:
    - pandas.DataFrame: DataFrame containing extracted URLs.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }
    results = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")

        # Generate URL manually
        url = generate_google_search_url(query, after, before, page)
        print(f"Generated URL: {url}")

        # Send the request
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("a", class_="WlydOe")

        # Save the HTML for debugging if no articles found
        if not articles:
            print("No more results. Saving the HTML for debugging.")
            with open(f"debug_page_{page}.html", "w", encoding="utf-8") as file:
                file.write(soup.prettify())
            break

        # Extract URLs
        for article in articles:
            url = article.get("href")
            if url:
                results.append(url)

        time.sleep(2)  # Avoid rate-limiting

    # Return as a DataFrame
    return pd.DataFrame({"URL": results})

def main():
    query = 'site:nasdaq.com Apple stock financial news'
    after = "2023-01-01"
    before = "2023-01-31"
    max_pages = 20  # Adjust based on your needs

    # Scrape Google Search results
    df = scrape_google_results(query, after, before, max_pages)

    # Save to a CSV
    if not df.empty:
        df.to_csv("google_search_results.csv", index=False)
        print(f"Scraped {len(df)} URLs and saved to 'google_search_results.csv'.")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
