import feedparser
import re
from html import unescape

import requests


# Global AI and digital media sources
GLOBAL_RSS_SOURCES = [
    # AI official sources
    "https://deepmind.google/blog/rss.xml",
    "https://openai.com/news/rss.xml",
    "https://blogs.nvidia.com/feed/",
    "https://developer.nvidia.com/blog/feed/",
    "https://huggingface.co/blog/feed.xml",
    "https://github.blog/feed/",
    "https://machinelearning.apple.com/rss.xml",
    "https://research.google/blog/rss/",

    # AI research and creative technology
    "https://blog.adobe.com/en/topics/adobe-firefly/rss.xml",

    # Digital media, 3D, game and creative technology
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


REQUEST_TIMEOUT = 10
MAX_CONTENT_LENGTH = 8000


def _strip_html(value):
    if not value:
        return ""
    text = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_article_text(url):
    """Best-effort text extraction for a single article page."""
    if not url:
        return ""

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; WeeklyReadingBot/1.0)"}
        )
        response.raise_for_status()
        text = _strip_html(response.text)
        return text[:MAX_CONTENT_LENGTH] if text else ""
    except requests.RequestException:
        return ""


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
                summary = _strip_html(entry.get("summary", ""))
                article_url = entry.get("link", "")
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": summary,
                    "url": article_url,
                    "source": source_name,
                    "content": ""
                })

        except Exception:
            source_stats.append((url, 0))

    return articles, source_stats


def enrich_articles_with_content(articles, limit=None):
    """Fetch article pages only for the articles that need deeper analysis."""
    selected = articles if limit is None else articles[:limit]
    for article in selected:
        if article.get("content"):
            continue
        article["content"] = _extract_article_text(article.get("url", ""))
    return articles


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
def fetch_articles(limit=10):
    return fetch_global_articles(limit)
