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

目标用户：数字媒体技术专业本科生，需要了解AI、计算机、数字媒体行业趋势以及就业方向。

请从候选文章中筛选最值得阅读的内容。

综合评分标准：
1. 专业匹配度 35%：是否与AI、计算机、数字媒体、AIGC、游戏、动画、影视技术相关。
2. 职业价值 30%：是否帮助本科生提升技能、了解行业机会和未来就业方向。
3. 技术趋势 25%：是否代表重要技术发展趋势。
4. 中国相关性 10%：是否与中国企业、产业、教育或应用场景有关。

推荐原则：
- 保持国际视野，同时关注中国AI产业发展。
- 推荐结果不要固定国际/中国比例，而是在长期保持平衡。
- 如果候选中存在高价值国际技术新闻，应保留国际内容。
- 如果候选中存在中国企业AI应用、国产工具、产业案例，也应优先考虑。

重点关注：
- OpenAI、Google DeepMind、Anthropic、NVIDIA、Meta等国际AI进展。
- 腾讯、阿里、百度、字节、智源、国产AI工具等中国AI发展。
- AIGC、视频生成、图像生成、3D、游戏引擎、Unity、Unreal Engine、XR、虚拟人等数字媒体方向。

降低推荐：
- 纯科研论文或研究项目（除非已经产业化或会影响未来技能）。
- 学术会议动态（除非与本科生学习方向高度相关）。
- 单纯政策、地区基础设施新闻。
- 与大学生技能成长关系弱的企业宣传。

来源控制：
- 推荐的3篇文章尽量避免来自同一个来源。
- 同一来源最多推荐1篇，除非该事件具有重大影响。

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
