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
你是一个个人知识管理助手，负责为大学生筛选高价值阅读内容。

请从候选文章中筛选最值得阅读的内容。

优先考虑：AI、编程、创业、商业、科研趋势、AI创作工具和数字媒体技术相关内容。

重要要求：
1. 所有输出字段必须使用中文。
2. title 必须翻译成自然中文标题，不要保留英文标题。
3. summary 必须生成中文导读，不允许直接复制英文原文。
4. reason 必须用中文说明推荐原因。
5. 如果文章是英文，请先理解文章内容，再用中文总结。
6. 内容需要适合中国大学生阅读，突出学习价值和实践意义。
7. 输出严格 JSON，不要 Markdown。

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
      "category": ""
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
