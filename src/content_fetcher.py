import feedparser


RSS_SOURCES = [
    "https://www.anthropic.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
]


def fetch_articles(limit=5):
    articles = []

    for url in RSS_SOURCES:
        feed = feedparser.parse(url)

        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "source": feed.feed.get("title", url)
            })

    return articles
