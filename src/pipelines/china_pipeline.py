from urllib.parse import urlparse

from notion_api import create_reading_page, CHINA_NOTION_DATA_SOURCE_ID
from ai_service import generate_china_ai_recommendations
from content_fetcher import fetch_china_articles, enrich_articles_with_content
from dedup import CHINA_HISTORY_FILE, filter_new_articles, update_history


def _source_key(item):
    """Use the article URL domain as the stable source identifier."""
    url = item.get("url", "")
    hostname = urlparse(url).netloc.lower()
    return hostname.removeprefix("www.") or item.get("source", "unknown").strip().lower()


def _select_diverse_recommendations(recommendations, limit=3):
    """Prefer one recommendation per source, then fill remaining slots if needed."""
    selected = []
    used_sources = set()

    for item in recommendations:
        source = _source_key(item)
        if source in used_sources:
            continue
        selected.append(item)
        used_sources.add(source)
        if len(selected) >= limit:
            return selected

    for item in recommendations:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) >= limit:
            break

    return selected


def _print_stats(stats):
    print(f"China dedup: URL={stats['duplicate_urls']}, title={stats['duplicate_titles']}, both={stats['duplicate_both']}, new={stats['new_articles']}")


def run_china_pipeline():
    print("\n=== China AI Reading Pipeline ===")

    articles = fetch_china_articles(limit=20)
    print(f"China fetch: {len(articles)} articles")

    if not articles:
        print("China result: 0 articles (RSS returned none)")
        print("China pipeline completed.")
        return

    new_articles, stats = filter_new_articles(
        articles,
        history_file=CHINA_HISTORY_FILE
    )
    _print_stats(stats)

    if not new_articles:
        print("China result: 0 articles (no new articles)")
        print("China pipeline completed.")
        return

    enrich_articles_with_content(new_articles)
    content_count = sum(1 for item in new_articles if item.get("content"))
    print(f"China content: {content_count}/{len(new_articles)} enriched")

    candidates = generate_china_ai_recommendations(new_articles, limit=6)
    print(f"China AI: {len(candidates)} candidates")

    recommendations = _select_diverse_recommendations(candidates, limit=3)
    sources = [_source_key(item) for item in recommendations]
    print(f"China recommendations: {len(recommendations)}")
    print(f"China sources: {', '.join(sources) if sources else 'none'}")

    if not recommendations:
        print("China result: 0 articles (no recommendations)")
        print("China pipeline completed.")
        return

    written_articles = []
    for item in recommendations:
        try:
            create_reading_page(item, data_source_id=CHINA_NOTION_DATA_SOURCE_ID)
            written_articles.append(item)
        except Exception as exc:
            print(f"China Notion write failed: {item.get('title', 'Untitled')} | {exc}")

    failed_count = len(recommendations) - len(written_articles)
    print(f"China Notion: written={len(written_articles)}, failed={failed_count}")

    if written_articles:
        update_history(written_articles, history_file=CHINA_HISTORY_FILE)
        print(f"China history: added={len(written_articles)}")
    else:
        print("China history: unchanged")

    print("China pipeline completed.")
