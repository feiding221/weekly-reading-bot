import feedparser


RSS_SOURCES = [
    # Global AI official sources
    "https://www.anthropic.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://openai.com/news/rss.xml",
    "https://blogs.microsoft.com/ai/feed/",
    "https://blogs.nvidia.com/feed/",
    "https://huggingface.co/blog/feed.xml",
    "https://github.blog/feed/",

    # China AI official / institutional sources
    "https://developer.aliyun.com/rss",
    "https://www.paddlepaddle.org.cn/rss",
    "https://www.hiascend.com/rss",

    # Digital media and creative technology official sources
    "https://blog.adobe.com/en/topics/firefly/rss.xml",
    "https://www.runwayml.com/blog/rss.xml",
    "https://www.blender.org/feed/",
    "https://www.unrealengine.com/en-US/rss",
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
