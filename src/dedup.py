import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


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


def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()


def filter_new_articles(articles, history_file=GLOBAL_HISTORY_FILE):
    history = load_seen_articles(history_file)

    seen_urls = {item.get("url", "") for item in history}
    new_articles = []
    duplicate_urls = 0
    duplicate_titles = 0
    history_titles = [item.get("title", "") for item in history]

    for article in articles:
        url = article.get("url", "").strip()
        title = article.get("title", "").strip()

        if url and url in seen_urls:
            duplicate_urls += 1
            continue

        duplicated = False
        for old_title in history_titles:
            if (
                title
                and old_title
                and title_similarity(title, old_title) >= TITLE_SIMILARITY_THRESHOLD
            ):
                duplicate_titles += 1
                duplicated = True
                break

        if not duplicated:
            new_articles.append(article)

    stats = {
        "duplicate_urls": duplicate_urls,
        "duplicate_titles": duplicate_titles,
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

    for article in articles:
        history.append({
            "url": article.get("url", ""),
            "title": article.get("title", ""),
            "date": today
        })

    save_seen_articles(history, history_file)
