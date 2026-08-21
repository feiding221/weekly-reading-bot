from urllib.parse import urlparse

from notion_api import create_reading_page, CHINA_NOTION_DATA_SOURCE_ID
from ai_service import generate_china_ai_recommendations
from content_fetcher import fetch_china_articles, enrich_articles_with_content
from dedup import CHINA_HISTORY_FILE, filter_new_articles, update_history


CHINA_AI_BATCH_SIZE = 10
CHINA_AI_TARGET_CANDIDATES = 6


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


def _generate_china_batched_recommendations(articles):
    """Send China articles to DeepSeek in small batches and stop once enough candidates exist."""
    all_candidates = []
    total_batches = (len(articles) + CHINA_AI_BATCH_SIZE - 1) // CHINA_AI_BATCH_SIZE

    for batch_index, start in enumerate(
        range(0, len(articles), CHINA_AI_BATCH_SIZE),
        start=1,
    ):
        batch = articles[start:start + CHINA_AI_BATCH_SIZE]

        try:
            candidates = generate_china_ai_recommendations(batch, limit=6)
        except Exception as exc:
            print(
                f"China AI batch {batch_index}/{total_batches} failed: "
                f"{type(exc).__name__}: {exc}"
            )
            continue

        all_candidates.extend(candidates)

        # Keep only the strongest candidates gathered so far.
        deduped = []
        seen_urls = set()
        seen_titles = set()
        for item in sorted(
            all_candidates,
            key=lambda value: value.get("value_score", 0),
            reverse=True,
        ):
            url = item.get("url", "").strip()
            title = item.get("title", "").strip()
            if url and url in seen_urls:
                continue
            if title and title in seen_titles:
                continue
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)
            deduped.append(item)

        all_candidates = deduped[:CHINA_AI_TARGET_CANDIDATES]

        print(
            f"China AI batch {batch_index}/{total_batches}: "
            f"processed={len(batch)}, candidates={len(candidates)}, "
            f"total_candidates={len(all_candidates)}"
        )

        if len(all_candidates) >= CHINA_AI_TARGET_CANDIDATES:
            break

    return all_candidates


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

    candidates = _generate_china_batched_recommendations(new_articles)
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
