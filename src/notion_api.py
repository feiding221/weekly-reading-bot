from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID

notion = Client(auth=NOTION_TOKEN)


def create_test_page():
    return notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "标题": {
                "title": [{"text": {"content": "Weekly Reading Bot 测试"}}]
            },
            "推荐理由": {
                "rich_text": [{"text": {"content": "自动化测试页面"}}]
            }
        }
    )
