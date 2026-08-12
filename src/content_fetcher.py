import feedparser


# Global AI and digital media sources
GLOBAL_RSS_SOURCES = [
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

    # AI research and creative technology
    "https://blog.adobe.com/en/topics/adobe-firefly/rss.xml",

    # Digital media, 3D, game and creative technology
    "https://www.runwayml.com/blog/rss.xml",
    "https://www.blender.org/feed/",
    "https://www.unrealengine.com/en-US/rss",
    "https://blog.unity.com/feed",
    "https://www.siggraph.org/feed/",
]


# China AI sources
# Used only by China AI Reading pipeline
CHINA_RSS_SOURCES = [
    # China AI research and professional media
    "https://hub.baai.ac.cn/rss",
    "https://www.jiqizhixin.com/rss",
    "https://www.infoq.cn/feed",
    "https://www.qbitai.com/feed",

    # China technology and AI industry
    "https://www.36kr.com/feed",
]


def fetch_articles_from_sources(sources, limit=10):
    articles = []

    for url in sources:
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", "").strip() or url
            print(f"RSS source: {source_name} | {url} | {len(feed.entries)} articles")

            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": source_name
                })

        except Exception as e:
            print("RSS fetch failed:", url, e)

    return articles


def fetch_global_articles(limit=10):
    return fetch_articles_from_sources(
        GLOBAL_RSS_SOURCES,
        limit
    )


def fetch_china_articles(limit=10):
    return fetch_articles_from_sources(
        CHINA_RSS_SOURCES,
        limit
    )


# Backward compatibility for existing Global Reading pipeline
# main.py currently uses fetch_articles().
# Keep this wrapper until the main workflow is migrated to dual pipelines.
def fetch_articles(limit=10):
    return fetch_global_articles(limit)
