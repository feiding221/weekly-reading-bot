import os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

# Notion databases
GLOBAL_NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
CHINA_NOTION_DATABASE_ID = os.environ.get("CHINA_NOTION_DATABASE_ID")

# Keep backward compatibility for existing workflow
NOTION_DATABASE_ID = GLOBAL_NOTION_DATABASE_ID

if not all([DEEPSEEK_API_KEY, NOTION_TOKEN, GLOBAL_NOTION_DATABASE_ID]):
    raise RuntimeError("Missing required environment variables")
