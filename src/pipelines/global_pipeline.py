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

    # First pass: maximize source diversity without changing the model ranking.
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


def run_global_pipeline():
    print("\n=== Global Reading Pipeline ===")

    articles = fetch_articles(limit=20)

    print("Fetched global articles:")
    print(len(articles), "articles")

    new_articles, stats = filter_new_articles(articles)

    print("Global dedup statistics:")
    print("Duplicate URLs:", stats["duplicate_urls"])
    print("Duplicate titles:", stats["duplicate_titles"])
    print("New articles:", stats["new_articles"])

    if not new_articles:
        print("No new global articles. Skipping recommendation and Notion write.")
        print("Global pipeline completed.")
        return

    enrich_articles_with_content(new_articles)
    content_count = sum(1 for item in new_articles if item.get("content"))
    print("Global article content:", f"{content_count}/{len(new_articles)} enriched")

    # Ask the model for a larger candidate pool. The model ranks the pool;
    # the pipeline then applies source diversity before taking the top 3.
    candidates = generate_reading_recommendations(new_articles, limit=6)

    print("Global recommendation candidates:")
    print(len(candidates), "candidates")

    # If the model unexpectedly returns no candidates despite having new,
    # enriched articles, retry once with an explicit fallback prompt.
    if not candidates:
        print("Global AI returned 0 candidates. Retrying once with fallback prompt...")
        candidates = generate_reading_recommendations(
            new_articles,
            limit=6,
            fallback=True,
        )
        print("Global fallback candidates:")
        print(len(candidates), "candidates")

    recommendations = _select_diverse_recommendations(candidates, limit=3)

    print("Global recommendations:")
    print(len(recommendations), "recommendations")
    print("Global recommendation sources:", [_source_key(item) for item in recommendations])

    if not recommendations:
        print("No global recommendations generated. History unchanged so these articles can be evaluated again later.")
        print("Global pipeline completed.")
        return

    # Only articles whose Notion page was actually created are added to history.
    # Unrecommended articles and failed Notion writes remain eligible for later runs.
    written_articles = []
    for item in recommendations:
        title = item.get("title", "Untitled")
        print("Creating Notion page:", title)
        try:
            create_reading_page(item)
            written_articles.append(item)
            print("Notion page created successfully:", title)
        except Exception as exc:
            print("Failed to create Notion page:", title)
            print("Notion error:", exc)

    if written_articles:
        update_history(written_articles)
        print("Global history updated:", len(written_articles), "articles")
    else:
        print("No global articles were written to Notion. History unchanged.")

    print("Global AI pipeline completed.\n"):