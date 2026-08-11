from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def _generate_recommendations_with_prompt(articles, system_prompt, limit=3):
    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(articles, ensure_ascii=False)}
        ]
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("recommendations", [])[:limit]


def generate_reading_recommendations(articles, limit=3):
    prompt = """
你是一个个人知识管理助手，负责为中国数字媒体技术本科生筛选高价值AI与数字媒体行业阅读内容。

目标：生成少量、高质量、长期值得保存的阅读资料，而不是新闻搬运。

筛选标准：
1. 专业匹配度：AI、计算机、AIGC、图像视频生成、3D、游戏、XR等方向。
2. 职业价值：是否帮助本科生了解技能、工具、行业机会。
3. 技术趋势：是否代表重要技术发展方向。
4. 产业价值：是否包含真实产品、企业应用或商业案例。
5. 来源质量：优先官方、一手、专业媒体来源。

输出要求：所有字段中文，严格输出JSON。
"""
    return _generate_recommendations_with_prompt(articles, prompt, limit)


def generate_china_ai_recommendations(articles, limit=3):
    prompt = """
你负责 China AI Reading 专栏内容筛选。

目标用户：中国数字媒体技术本科生。

重点关注：
- 中国AI大模型
- AIGC图像、视频、3D生成
- AI Agent
- 游戏AI
- 数字内容生产工具
- 国产AI开发平台
- 企业AI应用案例

筛选标准：
1. 是否体现中国AI产业和技术发展趋势。
2. 是否对数字媒体技术学生学习、项目实践或职业规划有价值。
3. 优先官方技术博客、开发者平台、企业案例。
4. 降低纯新闻、营销宣传、无技术细节内容权重。

不要为了数量推荐低价值文章。

输出JSON：
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
    return _generate_recommendations_with_prompt(articles, prompt, limit)
