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

    recommendations = generate_reading_recommendations(new_articles)

    print("Global recommendations:")
    print(len(recommendations), "recommendations")

    if not recommendations:
        print("No global recommendations generated. Skipping Notion write.")
        print("Global pipeline completed.")
        return

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item)

    update_history(new_articles)
    print("Global pipeline completed.")
