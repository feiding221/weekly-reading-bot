import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


HISTORY_FILE = Path("data/seen_articles.json")



def load_seen_articles():
    if not HISTORY_FILE.exists():
        return []

    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []



def save_seen_articles(articles):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(articles, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )



def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()



def filter_new_articles(articles):
    history = load_seen_articles()

    seen_urls = {
        item.get("url", "")
        for item in history
    }

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
            if title and old_title and title_similarity(title, old_title) >= 0.8:
                duplicate_titles += 1
                duplicated = True
                break

        if duplicated:
            continue

        new_articles.append(article)

    stats = {
        "duplicate_urls": duplicate_urls,
        "duplicate_titles": duplicate_titles,
        "new_articles": len(new_articles)
    }

    return new_articles, stats



def update_history(articles):
    history = load_seen_articles()
    today = datetime.now().strftime("%Y-%m-%d")

    for article in articles:
        history.append({
            "url": article.get("url", ""),
            "title": article.get("title", ""),
            "date": today
        })

    save_seen_articles(history)
