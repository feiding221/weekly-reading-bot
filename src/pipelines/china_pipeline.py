from notion_api import create_reading_page, CHINA_NOTION_DATA_SOURCE_ID
from ai_service import generate_china_ai_recommendations
from content_fetcher import fetch_china_articles


def run_china_pipeline():
    print("\n=== China AI Reading Pipeline ===")

    articles = fetch_china_articles(limit=20)

    print("Fetched China AI articles:")
    print(len(articles), "articles")

    if not articles:
        print("No China AI articles found.")
        return

    recommendations = generate_china_ai_recommendations(articles)

    print("China recommendations:")
    print(len(recommendations), "recommendations")

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item, data_source_id=CHINA_NOTION_DATA_SOURCE_ID)

    print("China AI pipeline completed.")
