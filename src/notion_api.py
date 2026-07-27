from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
from datetime import datetime

notion = Client(auth=NOTION_TOKEN)


def create_reading_page(data):
    today = datetime.now().strftime("%Y-%m-%d")

    return notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "标题": {
                "title": [
                    {"text": {"content": data.get("title", "Weekly Reading")}}
                ]
            },
            "日期": {
                "date": {
                    "start": today
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
            "阅读时间": {
                "number": parse_reading_time(data.get("reading_time", ""))
            }
        }
    )


def parse_reading_time(value):
    import re

    if not value:
        return None

    match = re.search(r"\d+", str(value))
    if match:
        return int(match.group())

    return None
