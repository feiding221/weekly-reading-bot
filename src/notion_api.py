from notion_client import Client
from config import NOTION_TOKEN, GLOBAL_NOTION_DATABASE_ID, CHINA_NOTION_DATABASE_ID
from datetime import datetime, timezone, timedelta
import time

notion = Client(auth=NOTION_TOKEN)

# Notion's newer database model exposes a data source behind each database.
# Keep the data-source IDs separate from the database/page IDs used elsewhere.
GLOBAL_NOTION_DATA_SOURCE_ID = ""
CHINA_NOTION_DATA_SOURCE_ID = "c01c3ec7-64b6-4d44-876a-6f711df99332"


def create_reading_page(data, database_id=None, data_source_id=None):
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
                "name": data.get("source", "其他")
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
                "name": data.get("category", "行业动态")
            }
        }
    }

    if data_source_id:
        parent = {"data_source_id": data_source_id}
    else:
        if database_id is None:
            database_id = GLOBAL_NOTION_DATABASE_ID
        parent = {"database_id": database_id}

    last_error = None
    for attempt in range(3):
        try:
            return notion.pages.create(
                parent=parent,
                properties=properties
            )
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

    raise last_error
