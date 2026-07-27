from openai import OpenAI
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def generate_reading_recommendation():
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业阅读推荐助手，负责生成高质量每周阅读推荐。"
            },
            {
                "role": "user",
                "content": "推荐一本值得大学生每周阅读的书，并输出标题、推荐理由和简介。"
            }
        ]
    )

    return response.choices[0].message.content
