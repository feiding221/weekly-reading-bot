from notion_api import create_reading_page
from ai_service import generate_reading_recommendations
from content_fetcher import fetch_china_articles


def run_china_pipeline():
    print("\n=== China AI Reading Pipeline ===")

    articles = fetch_china_articles(limit=20)

    print("Fetched China AI articles:")
    print(len(articles), "articles")

    if not articles:
        print("No China AI articles found.")
        return

    recommendations = generate_reading_recommendations(articles)

    for item in recommendations:
        create_reading_page(item)

    print("China AI pipeline completed.")
