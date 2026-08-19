from urllib.parse import urlparse

from notion_api import create_reading_page
from ai_service import generate_global_batched_recommendations
from content_fetcher import fetch_articles, enrich_articles_with_content
from dedup import filter_new_articles, update_history


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


def _print_stats(stats, label="Global"):
    print(f"{label} dedup: URL={stats['duplicate_urls']}, title={stats['duplicate_titles']}, both={stats['duplicate_both']}, new={stats['new_articles']}")


def run_global_pipeline():
    print("\n=== Global Reading Pipeline ===")

    articles = fetch_articles(limit=20)
    print(f"Global fetch: {len(articles)} articles")

    new_articles, stats = filter_new_articles(articles)
    _print_stats(stats)

    if not new_articles:
        print("Global result: 0 articles (no new articles)")
        print("Global pipeline completed.")
        return

    enrich_articles_with_content(new_articles)
    content_count = sum(1 for item in new_articles if item.get("content"))
    print(f"Global content: {content_count}/{len(new_articles)} enriched")

    candidates = generate_global_batched_recommendations(
        new_articles,
        batch_size=10,
        target_candidates=6,
    )
    print(f"Global AI: {len(candidates)} candidates")

    recommendations = _select_diverse_recommendations(candidates, limit=3)
    sources = [_source_key(item) for item in recommendations]
    print(f"Global recommendations: {len(recommendations)}")
    print(f"Global sources: {', '.join(sources) if sources else 'none'}")

    if not recommendations:
        print("Global result: 0 articles (no recommendations)")
        print("Global pipeline completed.")
        return

    written_articles = []
    for item in recommendations:
        try:
            create_reading_page(item)
            written_articles.append(item)
        except Exception as exc:
            print(f"Global Notion write failed: {item.get('title', 'Untitled')} | {exc}")

    failed_count = len(recommendations) - len(written_articles)
    print(f"Global Notion: written={len(written_articles)}, failed={failed_count}")

    if written_articles:
        update_history(written_articles)
        print(f"Global history: added={len(written_articles)}")
    else:
        print("Global history: unchanged")

    print("Global pipeline completed.")
