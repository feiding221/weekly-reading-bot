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

输入中的每篇文章可能包含：标题、RSS摘要、网页正文 content。
请优先依据正文 content 判断文章价值；正文缺失时再使用标题和RSS摘要，不要因为正文为空而直接淘汰文章。

目标：生成少量、高质量、长期值得保存的阅读资料，而不是新闻搬运。

筛选标准：
1. 专业匹配度：AI、计算机、AIGC、图像视频生成、3D、游戏、XR等方向。
2. 职业价值：是否帮助本科生了解技能、工具、行业机会。
3. 技术趋势：是否代表重要技术发展方向。
4. 产业价值：是否包含真实产品、企业应用或商业案例。
5. 来源质量：优先官方、一手、专业媒体来源。
6. 信息密度：正文是否提供具体技术、产品、方法、数据或实践信息。

请尽量从候选文章中选择 3 篇高价值内容。只有当候选文章整体都明显不符合上述标准时，才返回空数组。

摘要 summary 必须基于文章正文进行中文总结，不要只是改写标题。
推荐理由 reason 必须说明这篇文章对数字媒体技术本科生具体有什么价值。

输出要求：所有字段中文，严格输出JSON，不要输出Markdown或额外文字。
JSON格式必须为：
{
  "recommendations": [
    {
      "title": "文章标题",
      "summary": "基于正文的中文摘要",
      "reason": "具体推荐理由",
      "source": "来源名称",
      "tags": ["标签1", "标签2"],
      "url": "原文URL",
      "category": "分类"
    }
  ]
}
"""
    return _generate_recommendations_with_prompt(articles, prompt, limit)


def generate_china_ai_recommendations(articles, limit=3):
    prompt = f"""
你负责 China AI Reading 专栏内容筛选。

输入中的每篇文章可能包含：标题、RSS摘要、网页正文 content。
请优先依据正文 content 判断文章价值；正文缺失时再使用标题和RSS摘要。
不要因为正文抓取失败就直接淘汰文章。

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
5. 优先选择不同来源的文章，避免推荐结果过度集中于同一个媒体。
6. 信息密度：优先正文包含具体技术、产品、方法、数据或实践细节的文章。

不要为了数量推荐低价值文章，但如果候选池中存在多个高价值来源，应尽量覆盖不同来源。

summary 必须基于正文内容进行中文概括，不要只翻译或改写标题。
reason 必须结合正文说明其对数字媒体技术本科生的具体价值。

输出JSON：
{{
  "recommendations": [
    {{
      "title": "",
      "summary": "",
      "reason": "",
      "source": "",
      "tags": [],
      "url": "",
      "category": ""
    }}
  ]
}}

请先按综合价值排序，并尽量返回 {limit} 篇高质量候选，供后续程序进行来源多样性筛选。
"""
    return _generate_recommendations_with_prompt(articles, prompt, limit)
