from bs4 import BeautifulSoup
from newspaper import Article
import requests
import sqlite3
from transformers import pipeline

# Database connection
conn = sqlite3.connect("web3_news.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    summary TEXT,
    link TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    keyword TEXT NOT NULL
)""")

# Search keywords
keywords = ["blockchain", "ethereum", "nfts", "ai", "future of technology"]

# Scrape news
def scrape_news():
    for keyword in keywords:
        # Build search URL
        url = f"https://www.google.com/search?q={keyword}"

        # Get HTML content
        response = requests.get(url)
        content = response.content

        # Parse HTML
        soup = BeautifulSoup(content, "lxml")

        # Find news articles
        articles = soup.find_all("div", class_="ZINbbc xpd O9g5cc uUPGi")

        # Counter for scraped articles
        scraped_articles = 0

        # Set seen URLs to avoid duplicates
        seen_urls = set()

        for article in articles:
            # Extract title and link
            title = article.find("h3", class_="LC20lb DKV0Md").text
            link = article.find("a", href=True)["href"]

            # Check if URL has been seen before
            if link in seen_urls:
                continue

            # Download and summarize article
            try:
                article = Article(link)
                article.download()
                article.parse()
                summary = summarizer(article.text, min_length=50, max_length=200)

                # Extract author (if available)
                author = article.authors[0] if article.authors else None

                # Store data in database
                c.execute("""INSERT INTO news (title, author, summary, link, keyword) VALUES (?, ?, ?, ?, ?)""", (title, author, summary, link, keyword))
                conn.commit()

                seen_urls.add(link)
                scraped_articles += 1

                # Stop scraping if desired number of articles reached
                if scraped_articles >= 10:
                    break
            except:
                # Log errors
                print(f"Error scrapping article: {link}")

# Summarize text using AI
summarizer = pipeline("summarization")

# Scrape news
scrape_news()

# Close database connection
conn.close()
