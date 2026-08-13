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

    # First pass: maximize source diversity.
    for item in recommendations:
        source = _source_key(item)
        if source in used_sources:
            continue
        selected.append(item)
        used_sources.add(source)
        if len(selected) >= limit:
            return selected

    # Fallback: if fewer unique sources are available, keep the highest-ranked
    # remaining recommendations so the pipeline can still fill its normal count.
    for item in recommendations:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) >= limit:
            break

    return selected


def run_china_pipeline():
    print("\n=== China AI Reading Pipeline ===")

    articles = fetch_china_articles(limit=20)

    print("Fetched China AI articles:")
    print(len(articles), "articles")

    if not articles:
        print("No China AI articles found.")
        return

    new_articles, stats = filter_new_articles(
        articles,
        history_file=CHINA_HISTORY_FILE
    )

    print("China dedup statistics:")
    print("Duplicate URLs:", stats["duplicate_urls"])
    print("Duplicate titles:", stats["duplicate_titles"])
    print("New articles:", stats["new_articles"])

    if not new_articles:
        print("No new China AI articles. Skipping recommendation and Notion write.")
        print("China AI pipeline completed.")
        return

    # Enrich only newly fetched articles so the model can judge full article
    # content instead of relying mainly on RSS titles and summaries.
    enrich_articles_with_content(new_articles)
    content_count = sum(1 for item in new_articles if item.get("content"))
    print("China article content:", f"{content_count}/{len(new_articles)} enriched")

    # Ask the model for a larger candidate pool so source diversity can be
    # enforced deterministically after ranking.
    candidates = generate_china_ai_recommendations(new_articles, limit=6)
    recommendations = _select_diverse_recommendations(candidates, limit=3)

    print("China recommendations:")
    print(len(recommendations), "recommendations")
    print("China recommendation sources:", [_source_key(item) for item in recommendations])

    if not recommendations:
        print("No China recommendations generated. Skipping Notion write.")
        print("China AI pipeline completed.")
        return

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item, data_source_id=CHINA_NOTION_DATA_SOURCE_ID)

    update_history(new_articles, history_file=CHINA_HISTORY_FILE)
    print("China AI pipeline completed.")
