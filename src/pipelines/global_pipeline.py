from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
from content_fetcher import fetch_articles, enrich_articles_with_content
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

    enrich_articles_with_content(new_articles)
    content_count = sum(1 for item in new_articles if item.get("content"))
    print("Global article content:", f"{content_count}/{len(new_articles)} enriched")

    candidates = generate_reading_recommendations(new_articles, limit=6)

    print("Global recommendation candidates:")
    print(len(candidates), "candidates")

    recommendations = candidates[:3]

    print("Global recommendations:")
    print(len(recommendations), "recommendations")

    if not recommendations:
        print("No global recommendations generated. History unchanged so these articles can be evaluated again later.")
        print("Global pipeline completed.")
        return

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item)

    update_history(new_articles)
    print("Global pipeline completed.")
