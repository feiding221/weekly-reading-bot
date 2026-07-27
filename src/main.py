from notion_api import create_test_page
from ai_service import generate_reading_recommendation


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    recommendation = generate_reading_recommendation()
    print("Generated recommendation:")
    print(recommendation)

    result = create_test_page()
    print("Created Notion page:", result["id"])
