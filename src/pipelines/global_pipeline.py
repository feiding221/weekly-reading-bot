from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
from content_fetcher import fetch_articles
from dedup import filter_new_articles, update_history


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

    # Ask the model for a larger candidate pool so the final selection is more
    # robust when some newly fetched articles are low-value.
    candidates = generate_reading_recommendations(new_articles, limit=6)

    print("Global recommendation candidates:")
    print(len(candidates), "candidates")

    recommendations = candidates[:3]

    print("Global recommendations:")
    print(len(recommendations), "recommendations")

    if not recommendations:
        # These articles have already been evaluated, so record them as seen
        # even when the model finds no suitable recommendation. Otherwise the
        # same articles would be treated as new again on the next run.
        update_history(new_articles)
        print("No global recommendations generated. Updated article history and skipped Notion write.")
        print("Global pipeline completed.")
        return

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item)

    update_history(new_articles)
    print("Global pipeline completed.")
