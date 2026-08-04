from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
from content_fetcher import fetch_articles
from dedup import filter_new_articles, update_history, get_fallback_articles


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    articles = fetch_articles(limit=20)

    print("Fetched articles:")
    print(len(articles), "articles")

    articles, stats = filter_new_articles(articles)

    print("Dedup statistics:")
    print("Duplicate URLs:", stats["duplicate_urls"])
    print("Duplicate titles:", stats["duplicate_titles"])
    print("New articles:", stats["new_articles"])

    new_articles = list(articles)
    fallback_articles = []

    if len(articles) < 3:
        needed = 3 - len(articles)
        print("Insufficient new articles, adding fallback articles:", needed)
        fallback_articles = get_fallback_articles(needed)
        articles.extend(fallback_articles)

    if not articles:
        print("No articles found.")
        exit(0)

    recommendations = generate_reading_recommendations(articles)

    print("Generated recommendations:")
    print(len(recommendations), "articles")

    created_count = 0

    for item in recommendations:
        result = create_reading_page(item)
        created_count += 1
        print("Created Notion page:", result["id"])

    # Only save real new articles. Fallback articles are temporary supplements.
    update_history(new_articles)

    print("Notion pages created:", created_count)
    print("History updated:", len(new_articles), "articles")
