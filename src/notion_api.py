from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
from datetime import datetime, timezone, timedelta

notion = Client(auth=NOTION_TOKEN)


def create_reading_page(data):
    beijing_timezone = timezone(timedelta(hours=8))
    created_time = datetime.now(beijing_timezone).isoformat(timespec="minutes")

    properties = {
        "标题": {
            "title": [
                {"text": {"content": data.get("title", "Weekly Reading")}}
            ]
        },
        "日期": {
            "date": {
                "start": created_time
            }
        },
        "中文导读": {
            "rich_text": [
                {"text": {"content": data.get("summary", "")[:1900]}}
            ]
        },
        "已读": {
            "checkbox": False
        },
        "推荐理由": {
            "rich_text": [
                {"text": {"content": data.get("reason", "")[:1900]}}
            ]
        },
        "来源": {
            "select": {
                "name": data.get("source", "未知来源")
            }
        },
        "标签": {
            "multi_select": [
                {"name": tag} for tag in data.get("tags", [])
            ]
        },
        "链接": {
            "url": data.get("url") or None
        },
        "分类": {
            "select": {
                "name": data.get("category", "其他")
            }
        }
    }

    return notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=properties
    )
