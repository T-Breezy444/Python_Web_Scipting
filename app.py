from flask import Flask, render_template, jsonify
from Web3Scrape import scrape_news

app = Flask(__name__)

@app.route("/")
def index():
    """
    Retrieve all news articles from database.
    """
    conn = sqlite3.connect("web3_news.db")
    c = conn.cursor()
    c.execute("SELECT * FROM news")
    articles = c.fetchall()
    conn.close()

    return render_template("index.html", articles=articles)

@app.route("/api/news")
def api_news():
    """
    Return JSON data with all news articles.
    """
    conn = sqlite3.connect("web3_news.db")
    c = conn.cursor()
    c.execute("SELECT * FROM news")
    articles = c.fetchall()
    conn.close()

    return jsonify({"articles": articles})

if __name__ == "__main__":
    # Scrape news before starting the server
    scrape_news()
    app.run(debug=True)
