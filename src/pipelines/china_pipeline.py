from notion_api import create_reading_page, CHINA_NOTION_DATA_SOURCE_ID
from ai_service import generate_china_ai_recommendations
from content_fetcher import fetch_china_articles
from dedup import CHINA_HISTORY_FILE, filter_new_articles, update_history


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

    recommendations = generate_china_ai_recommendations(new_articles)

    print("China recommendations:")
    print(len(recommendations), "recommendations")

    if not recommendations:
        print("No China recommendations generated. Skipping Notion write.")
        print("China AI pipeline completed.")
        return

    for item in recommendations:
        print("Creating Notion page:", item.get("title", "Untitled"))
        create_reading_page(item, data_source_id=CHINA_NOTION_DATA_SOURCE_ID)

    update_history(new_articles, history_file=CHINA_HISTORY_FILE)
    print("China AI pipeline completed.")
