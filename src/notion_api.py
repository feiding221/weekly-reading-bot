from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID

notion = Client(auth=NOTION_TOKEN)


def create_reading_page(content):
    return notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "标题": {
                "title": [{"text": {"content": "Weekly Reading Bot 推荐"}}]
            },
            "推荐理由": {
                "rich_text": [{"text": {"content": content[:1900]}}]
            }
        }
    )
