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
你是一个个人知识管理助手，负责为中国数字媒体技术本科生筛选高价值AI与数字媒体行业阅读内容。

目标：生成少量、高质量、长期值得保存的阅读资料，而不是新闻搬运。

筛选标准：
1. 专业匹配度：AI、计算机、AIGC、图像视频生成、3D、游戏、XR等方向。
2. 职业价值：是否帮助本科生了解技能、工具、行业机会。
3. 技术趋势：是否代表重要技术发展方向。
4. 产业价值：是否包含真实产品、企业应用或商业案例。
5. 来源质量：优先选择官方、一手、专业媒体来源。

来源优先级：
最高：OpenAI、Google DeepMind、Anthropic、NVIDIA、Meta、Microsoft、Adobe、Hugging Face、GitHub等官方博客。
其次：中国大型科技企业官方技术平台、AI实验室和开发者平台。
再次：MIT Technology Review、IEEE Spectrum、Reuters、TechCrunch等专业媒体。

禁止或大幅降低：
- IT之家
- 量子位
- CSDN
- 普通自媒体
- 聚合转载平台
- 无技术价值的热点新闻

推荐原则：
- 不固定国际/中国比例，根据当天高质量内容动态选择。
- 不要为了中国来源强行加入低质量文章。
- 同一来源最多推荐1篇，避免来源集中。
- 如果当天优质内容不足，宁愿少推荐，也不要降低质量。

适合推荐：
- AI模型、工具、平台重大更新
- AIGC图像、视频、3D、游戏技术进展
- 企业AI落地案例
- 对数字媒体技术学生学习和就业有帮助的行业变化

降低推荐：
- 纯科研论文
- 面向研究生的实验室项目
- 学术会议介绍
- 与本科生技能成长关系弱的政策新闻

输出要求：
- 所有字段中文。
- title使用自然中文标题。
- summary生成中文导读。
- reason说明为什么值得数字媒体技术本科生阅读。
- 严格输出JSON。

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

必须尽量返回3篇高价值文章。
"""
            },
            {
                "role": "user",
                "content": json.dumps(articles, ensure_ascii=False)
            }
        ]
    )

    data = json.loads(response.choices[0].message.content)
    recommendations = data.get("recommendations", [])

    if len(recommendations) < limit:
        used_urls = {item.get("url") for item in recommendations}
        for article in articles:
            if len(recommendations) >= limit:
                break
            if article.get("url") not in used_urls:
                recommendations.append({
                    "title": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "reason": "该内容与AI技术、数字媒体行业或大学生职业发展相关，值得关注。",
                    "source": article.get("source", ""),
                    "tags": article.get("tags", []),
                    "url": article.get("url", ""),
                    "category": article.get("category", "")
                })

    return recommendations[:limit]
