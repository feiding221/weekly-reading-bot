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
你是一个个人知识管理助手，负责为中国大学生筛选高价值阅读内容。

请从候选文章中筛选最值得阅读的内容。

综合评分标准：
1. 技术价值 40%：是否代表AI、编程、数字媒体等领域的重要进展。
2. 职业相关性 40%：是否帮助大学生提升技能、了解行业机会。
3. 中国相关性 20%：是否与中国技术产业、教育、就业或应用场景有关。

优先考虑：
- 中国AI产业动态
- 国产大模型和AI工具
- AIGC、游戏、动画、影视、XR等数字媒体技术
- 全球前沿技术中会影响中国行业发展的内容
- 适合计算机和数字媒体专业学生学习的案例

降低推荐：
- 单纯海外政策项目
- 与个人技能成长关系弱的地区新闻
- 只有企业宣传价值，没有学习价值的内容

重要要求：
1. 所有输出字段必须使用中文。
2. title 必须翻译成自然中文标题，不要保留英文标题。
3. summary 必须生成中文导读，不允许直接复制英文原文。
4. reason 必须说明为什么值得大学生阅读。
5. 如果文章是英文，请先理解内容，再用中文总结。
6. 输出严格 JSON，不要 Markdown。

返回格式：
{
  "recommendations": [
    {
      "title": "",
      "summary": "",
      "reason": "",
      "source": "",
      "tags": [],
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
