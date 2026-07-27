from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def generate_reading_recommendation():
    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
你是一个专业阅读推荐助手。
请严格输出 JSON，不要输出 Markdown。

字段要求：
- title: 书籍标题
- summary: 中文导读
- reason: 推荐理由
- source: 来源（作者、出版社或推荐来源）
- tags: 标签数组
- reading_time: 预计阅读时间
- url: 相关链接，没有则为空字符串
"""
            },
            {
                "role": "user",
                "content": "推荐一本适合大学生每周阅读的书，并生成结构化信息。"
            }
        ]
    )

    content = response.choices[0].message.content
    return json.loads(content)
