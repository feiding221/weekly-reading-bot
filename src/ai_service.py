from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def generate_reading_recommendation(articles):
    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
你是一个个人知识管理助手。

从候选文章中选择最值得大学生阅读的一篇。
优先考虑：AI、编程、创业、商业、科研趋势。

输出严格 JSON，不要 Markdown。

字段要求：
- title: 标题
- summary: 中文导读
- reason: 推荐理由
- source: 来源
- tags: 标签数组
- reading_time: 阅读时间数字
- url: 原文链接
- category: 分类
- priority: 优先级（高/中/低）
- score: 0-10综合评分
"""
            },
            {
                "role": "user",
                "content": json.dumps(articles, ensure_ascii=False)
            }
        ]
    )

    return json.loads(response.choices[0].message.content)
