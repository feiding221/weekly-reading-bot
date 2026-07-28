import json
from pathlib import Path

HISTORY_FILE = Path("data/history_urls.json")


def load_history():
    if not HISTORY_FILE.exists():
        return set()
    try:
        return set(json.loads(HISTORY_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def filter_new_articles(articles):
    history = load_history()
    new_articles = []

    for article in articles:
        url = article.get("url", "").strip()
        if url and url not in history:
            new_articles.append(article)
            history.add(url)

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(list(history), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return new_articles
