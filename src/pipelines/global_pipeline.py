from urllib.parse import urlparse

from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
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


def _mix_articles_by_source(articles):
    """Interleave articles by source so early AI batches are not dominated by one RSS source."""
    grouped = {}
    source_order = []

    for article in articles:
        source = article.get("source", "unknown")
        if source not in grouped:
            grouped[source] = []
            source_order.append(source)
        grouped[source].append(article)

    mixed_articles = []
    while True:
        added = False
        for source in source_order:
            if grouped[source]:
                mixed_articles.append(grouped[source].pop(0))
                added = True
        if not added:
            break

    return mixed_articles


def _generate_global_batched_recommendations(articles, batch_size=10, target_candidates=6):
    """Fetch content and run DeepSeek only for each batch that actually needs analysis."""
    mixed_articles = _mix_articles_by_source(articles)
    total_batches = (len(mixed_articles) + batch_size - 1) // batch_size
    all_candidates = []
    enriched_count = 0

    for batch_index, start in enumerate(range(0, len(mixed_articles), batch_size), start=1):
        batch = mixed_articles[start:start + batch_size]

        enrich_articles_with_content(batch)
        batch_enriched = sum(1 for item in batch if item.get("content"))
        enriched_count += batch_enriched

        candidates = generate_reading_recommendations(batch, limit=6)
        all_candidates.extend(candidates)
        all_candidates.sort(key=lambda item: item.get("value_score", 0), reverse=True)
        all_candidates = all_candidates[:target_candidates]

        print(
            f"Global AI batch {batch_index}/{total_batches}: "
            f"processed={len(batch)}, enriched={batch_enriched}, "
            f"candidates={len(candidates)}, total_candidates={len(all_candidates)}"
        )

        if len(all_candidates) >= target_candidates:
            break

    return all_candidates, enriched_count


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

    candidates, content_count = _generate_global_batched_recommendations(
        new_articles,
        batch_size=10,
        target_candidates=6,
    )
    print(f"Global content: {content_count}/{len(new_articles)} enriched before stopping")
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
