from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID

notion = Client(auth=NOTION_TOKEN)


def create_reading_page(data):
    return notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "标题": {
                "title": [
                    {"text": {"content": data.get("title", "Weekly Reading")}}
                ]
            },
            "中文导读": {
                "rich_text": [
                    {"text": {"content": data.get("summary", "")[:1900]}}
                ]
            },
            "推荐理由": {
                "rich_text": [
                    {"text": {"content": data.get("reason", "")[:1900]}}
                ]
            },
            "来源": {
                "rich_text": [
                    {"text": {"content": data.get("source", "")[:1900]}}
                ]
            },
            "标签": {
                "multi_select": [
                    {"name": tag} for tag in data.get("tags", [])
                ]
            },
            "阅读时间": {
                "rich_text": [
                    {"text": {"content": data.get("reading_time", "")}}
                ]
            },
            "链接": {
                "url": data.get("url") or None
            }
        }
    )
