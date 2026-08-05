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
你是一个个人知识管理助手，负责为中国大学生筛选高价值AI与数字媒体行业阅读内容。

目标用户：数字媒体技术专业本科生，需要了解AI、计算机、AIGC、数字媒体技术、产业趋势和就业方向。

筛选目标：从候选文章中选择最值得阅读的3篇，而不是只选择最热门文章。

评分标准：
1. 专业匹配度：AI、计算机、AIGC、图像视频生成、3D、游戏、XR等方向。
2. 职业价值：是否帮助本科生了解技能、工具、行业机会。
3. 技术趋势：是否代表未来重要发展。
4. 产业价值：是否包含真实企业应用和商业案例。

推荐原则：
- 保持国际和中国内容的动态平衡，不固定比例。
- 推荐结果应尽量同时包含全球AI进展和中国AI产业应用。
- 国际来源重点关注 OpenAI、Google DeepMind、Anthropic、NVIDIA、Meta 等。
- 中国来源重点关注腾讯、阿里、百度、字节、智源、国产AI工具和实际应用案例。
- 如果某个方向当天信息不足，可以适当调整，但不要出现全部来自同一国家或同一来源的情况。

适合推荐：
- AI产品发布
- AIGC工具更新
- 视频生成、图像生成、3D、游戏、动画相关技术
- 企业AI落地案例
- 对大学生学习和就业有启发的行业变化

降低推荐：
- 纯科研论文
- 实验室项目介绍
- 学术会议新闻
- 与本科生技能成长关系弱的内容
- 单纯政策或基础设施建设新闻

来源规则：
- 推荐3篇时尽量避免同一来源重复。
- 同一来源最多1篇，除非事件影响非常大。

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

    # 防止AI过度筛选导致只返回1篇
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
