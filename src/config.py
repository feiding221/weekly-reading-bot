import os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

if not all([DEEPSEEK_API_KEY, NOTION_TOKEN, NOTION_DATABASE_ID]):
    raise RuntimeError("Missing required environment variables")
