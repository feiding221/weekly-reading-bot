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
    source_stats = []

    for url in sources:
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", "").strip() or url
            entry_count = len(feed.entries)
            source_stats.append((source_name, entry_count))

            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": source_name
                })

        except Exception:
            source_stats.append((url, 0))

    return articles, source_stats


def _fetch_articles(sources, limit, label):
    articles, source_stats = fetch_articles_from_sources(sources, limit=limit)

    active_sources = sum(1 for _, count in source_stats if count > 0)
    failed_sources = len(source_stats) - active_sources
    total_entries = sum(count for _, count in source_stats)

    print(
        f"{label} RSS: {len(sources)} sources, "
        f"{active_sources} active, {failed_sources} failed, "
        f"{total_entries} entries, {len(articles)} fetched"
    )

    if failed_sources:
        failed = [name for name, count in source_stats if count == 0]
        print(f"{label} RSS failed sources: {', '.join(failed)}")

    return articles


def fetch_global_articles(limit=10):
    return _fetch_articles(
        GLOBAL_RSS_SOURCES,
        limit,
        "Global"
    )


def fetch_china_articles(limit=10):
    return _fetch_articles(
        CHINA_RSS_SOURCES,
        limit,
        "China"
    )


# Backward compatibility for existing Global Reading pipeline
# main.py currently uses fetch_articles().
def fetch_articles(limit=10):
    return fetch_global_articles(limit)
