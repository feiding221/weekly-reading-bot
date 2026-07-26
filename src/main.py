from notion_client import create_test_page


if __name__ == "__main__":
    print("Starting weekly reading bot...")
    result = create_test_page()
    print("Created Notion page:", result["id"])
