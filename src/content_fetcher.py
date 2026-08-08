import feedparser


RSS_SOURCES = [
    # Global AI official sources
    "https://www.anthropic.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://openai.com/news/rss.xml",
    "https://blogs.microsoft.com/ai/feed/",
    "https://blogs.nvidia.com/feed/",
    "https://developer.nvidia.com/blog/feed/",
    "https://huggingface.co/blog/feed.xml",
    "https://github.blog/feed/",
    "https://ai.meta.com/blog/rss/",
    "https://machinelearning.apple.com/rss.xml",
    "https://research.google/blog/rss/",

    # AI research and technology ecosystem
    "https://blog.adobe.com/en/topics/adobe-firefly/rss.xml",

    # Digital media, 3D, game and creative technology sources
    "https://www.runwayml.com/blog/rss.xml",
    "https://www.blender.org/feed/",
    "https://www.unrealengine.com/en-US/rss",
    "https://blog.unity.com/feed",
    "https://www.siggraph.org/feed/",
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
