import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

if not all([OPENAI_API_KEY, NOTION_TOKEN, NOTION_DATABASE_ID]):
    raise RuntimeError("Missing required environment variables")
