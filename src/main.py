from notion_api import create_reading_page
from ai_service import generate_reading_recommendation
from content_fetcher import fetch_articles


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    articles = fetch_articles()

    print("Fetched articles:")
    print(articles)

    recommendation = generate_reading_recommendation(articles)

    print("Generated recommendation:")
    print(recommendation)

    result = create_reading_page(recommendation)
    print("Created Notion page:", result["id"])
