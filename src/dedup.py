import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit


GLOBAL_HISTORY_FILE = Path("data/seen_articles.json")
CHINA_HISTORY_FILE = Path("data/seen_china_articles.json")
TITLE_SIMILARITY_THRESHOLD = 0.8


def load_seen_articles(history_file=GLOBAL_HISTORY_FILE):
    if not history_file.exists():
        return []

    try:
        return json.loads(history_file.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_seen_articles(articles, history_file=GLOBAL_HISTORY_FILE):
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(
        json.dumps(articles, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def normalize_url(url):
    """Normalize URLs so harmless tracking/query differences do not bypass dedup."""
    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))
    except Exception:
        return url.strip()


def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()


def filter_new_articles(articles, history_file=GLOBAL_HISTORY_FILE):
    history = load_seen_articles(history_file)

    seen_urls = {
        normalize_url(item.get("url", ""))
        for item in history
        if item.get("url", "")
    }
    history_titles = [item.get("title", "").strip() for item in history]

    new_articles = []
    new_urls = set()
    new_titles = []
    duplicate_urls = 0
    duplicate_titles = 0
    duplicate_both = 0

    for article in articles:
        url = article.get("url", "").strip()
        title = article.get("title", "").strip()
        normalized_url = normalize_url(url)

        # URL and title are evaluated independently. An article is blocked only
        # when both checks identify it as a duplicate.
        url_duplicate = bool(normalized_url and (
            normalized_url in seen_urls or normalized_url in new_urls
        ))

        title_duplicate = False
        for old_title in history_titles + new_titles:
            if (
                title
                and old_title
                and title_similarity(title, old_title) >= TITLE_SIMILARITY_THRESHOLD
            ):
                title_duplicate = True
                break

        if url_duplicate:
            duplicate_urls += 1
        if title_duplicate:
            duplicate_titles += 1

        if url_duplicate and title_duplicate:
            duplicate_both += 1
            continue

        new_articles.append(article)
        if normalized_url:
            new_urls.add(normalized_url)
        if title:
            new_titles.append(title)

    stats = {
        "duplicate_urls": duplicate_urls,
        "duplicate_titles": duplicate_titles,
        "duplicate_both": duplicate_both,
        "new_articles": len(new_articles)
    }

    return new_articles, stats


def get_fallback_articles(limit=10, history_file=GLOBAL_HISTORY_FILE):
    """When new articles are insufficient, reuse recent high-value history."""
    history = load_seen_articles(history_file)
    return history[-limit:]


def update_history(articles, history_file=GLOBAL_HISTORY_FILE):
    history = load_seen_articles(history_file)
    today = datetime.now().strftime("%Y-%m-%d")

    existing_urls = {
        normalize_url(item.get("url", ""))
        for item in history
        if item.get("url", "")
    }

    for article in articles:
        url = article.get("url", "")
        normalized_url = normalize_url(url)

        # Keep history itself clean even if an upstream caller passes duplicates.
        if normalized_url and normalized_url in existing_urls:
            continue

        history.append({
            "url": url,
            "title": article.get("title", ""),
            "date": today
        })
        if normalized_url:
            existing_urls.add(normalized_url)

    save_seen_articles(history, history_file)
