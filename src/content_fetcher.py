import feedparser


RSS_SOURCES = [
    # AI companies
    "https://www.anthropic.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://openai.com/news/rss.xml",

    # Developer and research
    "https://huggingface.co/blog/feed.xml",
    "https://github.blog/feed/",
]


def fetch_articles(limit=10):
    articles = []

    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", url)
                })

        except Exception as e:
            print("RSS fetch failed:", url, e)

    return articles
