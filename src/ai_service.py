from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def generate_reading_recommendations(articles, limit=3):
    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
你是一个个人知识管理助手。

请从候选文章中筛选最值得大学生阅读的内容。
优先考虑：AI、编程、创业、商业、科研趋势。

请输出严格 JSON，不要 Markdown。

返回格式：
{
  "recommendations": [
    {
      "title": "",
      "summary": "",
      "reason": "",
      "source": "",
      "tags": [],
      "reading_time": 0,
      "url": "",
      "category": "",
      "priority": "高/中/低",
      "score": 0
    }
  ]
}

只返回最高价值的3篇文章。
"""
            },
            {
                "role": "user",
                "content": json.dumps(articles, ensure_ascii=False)
            }
        ]
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("recommendations", [])[:limit]
