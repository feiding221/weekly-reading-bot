from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
from content_fetcher import fetch_articles
from dedup import filter_new_articles


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    articles = fetch_articles()
    print("Fetched articles:")
    print(len(articles), "articles")

    articles = filter_new_articles(articles)
    print("After dedup:")
    print(len(articles), "new articles")

    if not articles:
        print("No new articles found.")
        exit(0)

    recommendations = generate_reading_recommendations(articles)

    print("Generated recommendations:")
    print(recommendations)

    for item in recommendations:
        result = create_reading_page(item)
        print("Created Notion page:", result["id"])
