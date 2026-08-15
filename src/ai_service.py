from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

ALLOWED_CATEGORIES = {
    "AI与模型",
    "AIGC与生成式AI",
    "AI Agent",
    "3D与CG",
    "VFX与影视",
    "游戏与实时技术",
    "数字媒体工具",
    "开发与开源",
    "AI产业与应用",
    "研究与前沿",
}

ALLOWED_TAGS = {
    "LLM",
    "多模态",
    "AI Agent",
    "生成式AI",
    "AI模型",
    "AI图像",
    "AI视频",
    "AI音频",
    "AI 3D",
    "AI创作",
    "Blender",
    "Houdini",
    "Nuke",
    "Unreal Engine",
    "Unity",
    "Rendering",
    "VFX",
    "Motion Graphics",
    "Virtual Production",
    "Open Source",
    "GitHub",
    "API / SDK",
    "MCP",
    "AI开发",
    "NVIDIA",
    "Hugging Face",
    "OpenAI",
    "Google",
    "研究前沿",
}

VALUE_WEIGHTS = {
    "professional_fit": 30,
    "technical_value": 25,
    "career_value": 15,
    "information_density": 15,
    "source_quality": 10,
    "trend_value": 5,
}


def _calculate_value_score(item):
    total = 0.0
    for field, weight in VALUE_WEIGHTS.items():
        try:
            score = float(item.get(field, 0))
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(100.0, score))
        total += score * weight / 100.0
    return round(total, 1)


def _sanitize_recommendations(recommendations, limit):
    sanitized = []
    for item in recommendations:
        if not isinstance(item, dict):
            continue

        category = item.get("category")
        if category not in ALLOWED_CATEGORIES:
            category = "研究与前沿"

        raw_tags = item.get("tags", [])
        if not isinstance(raw_tags, list):
            raw_tags = []
        tags = []
        for tag in raw_tags:
            if tag in ALLOWED_TAGS and tag not in tags:
                tags.append(tag)
            if len(tags) == 3:
                break

        item["category"] = category
        item["tags"] = tags
        item["value_score"] = _calculate_value_score(item)
        sanitized.append(item)

    sanitized.sort(key=lambda item: item.get("value_score", 0), reverse=True)
    return sanitized[:limit]


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
    recommendations = _sanitize_recommendations(
        data.get("recommendations", []),
        limit
    )

    print("AI candidate scores:")
    for item in recommendations:
        print(
            f"- {item.get('title', 'Untitled')} | "
            f"score={item.get('value_score', 0)} | "
            f"category={item.get('category', '')} | "
            f"tags={item.get('tags', [])}"
        )

    return recommendations


def generate_reading_recommendations(articles, limit=6):
    prompt = """
你是一个个人知识管理助手，负责为中国数字媒体技术本科生筛选高价值AI与数字媒体行业阅读内容。

输入中的每篇文章可能包含：标题、RSS摘要、网页正文 content。
请优先依据正文 content 判断文章价值；正文缺失时再使用标题和RSS摘要，不要因为正文为空而直接淘汰文章。

目标：生成少量、高质量、长期值得保存的阅读资料，而不是新闻搬运。

请对每篇候选文章分别进行以下 6 项 0-100 分评价：
1. professional_fit：与数字媒体技术专业方向的匹配度。
2. technical_value：技术深度、技术含量和实践价值。
3. career_value：对学习、项目实践、技能选择或职业发展的帮助。
4. information_density：正文是否包含具体技术、产品、方法、数据、案例或实践细节。
5. source_quality：来源是否可靠、一手、专业，官方技术来源优先。
6. trend_value：是否代表值得关注的技术趋势或行业变化。

综合分由程序按固定权重计算：professional_fit 30% + technical_value 25% + career_value 15% + information_density 15% + source_quality 10% + trend_value 5%。

请先按综合价值排序，尽量返回最多 6 篇候选。不要为了凑数量提高低价值文章的分数；如果候选池确实不足，可以少返回，但不要因为候选数量少就随意返回空数组。

【分类规则】
category 必须且只能从下面 10 个固定分类中选择 1 个：
AI与模型、AIGC与生成式AI、AI Agent、3D与CG、VFX与影视、游戏与实时技术、数字媒体工具、开发与开源、AI产业与应用、研究与前沿。

【标签规则】
tags 只能从下面 30 个固定标签中选择，最多 3 个，可以少于 3 个，不得创造新标签：
LLM、多模态、AI Agent、生成式AI、AI模型、AI图像、AI视频、AI音频、AI 3D、AI创作、Blender、Houdini、Nuke、Unreal Engine、Unity、Rendering、VFX、Motion Graphics、Virtual Production、Open Source、GitHub、API / SDK、MCP、AI开发、NVIDIA、Hugging Face、OpenAI、Google、研究前沿。

不要使用 AI、科技、商业、科研、趋势、编程、行业动态等宽泛词作为标签。分类和标签不要表达同一个概念。

输出JSON，不要输出Markdown：
{
  "recommendations": [
    {
      "title": "中文标题",
      "summary": "基于正文的中文摘要",
      "reason": "具体推荐理由",
      "source": "来源名称",
      "tags": ["标签1", "标签2"],
      "url": "原文URL",
      "category": "分类",
      "professional_fit": 0,
      "technical_value": 0,
      "career_value": 0,
      "information_density": 0,
      "source_quality": 0,
      "trend_value": 0
    }
  ]
}
"""
    return _generate_recommendations_with_prompt(articles, prompt, limit)


def generate_china_ai_recommendations(articles, limit=6):
    prompt = """
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

请对每篇候选文章分别进行以下 6 项 0-100 分评价：
1. professional_fit：与数字媒体技术专业方向的匹配度。
2. technical_value：技术深度、技术含量和实践价值。
3. career_value：对学习、项目实践、技能选择或职业发展的帮助。
4. information_density：正文是否包含具体技术、产品、方法、数据、案例或实践细节。
5. source_quality：来源是否可靠、一手、专业，官方技术来源优先。
6. trend_value：是否代表值得关注的技术趋势或行业变化。

综合分由程序按固定权重计算：professional_fit 30% + technical_value 25% + career_value 15% + information_density 15% + source_quality 10% + trend_value 5%。

请先按综合价值排序，并尽量返回最多 6 篇高质量候选，供后续程序进行来源多样性筛选。不要为了凑数量提高低价值文章的分数；如果候选池确实不足，可以少返回，但不要因为候选数量少就随意返回空数组。

【分类规则】
category 必须且只能从下面 10 个固定分类中选择 1 个：
AI与模型、AIGC与生成式AI、AI Agent、3D与CG、VFX与影视、游戏与实时技术、数字媒体工具、开发与开源、AI产业与应用、研究与前沿。

【标签规则】
tags 只能从下面 30 个固定标签中选择，最多 3 个，可以少于 3 个，不得创造新标签：
LLM、多模态、AI Agent、生成式AI、AI模型、AI图像、AI视频、AI音频、AI 3D、AI创作、Blender、Houdini、Nuke、Unreal Engine、Unity、Rendering、VFX、Motion Graphics、Virtual Production、Open Source、GitHub、API / SDK、MCP、AI开发、NVIDIA、Hugging Face、OpenAI、Google、研究前沿。

不要使用 AI、科技、商业、科研、趋势、编程等宽泛词作为标签。分类和标签不要重复表达同一个概念。

输出JSON，不要输出Markdown：
{
  "recommendations": [
    {
      "title": "",
      "summary": "",
      "reason": "",
      "source": "",
      "tags": [],
      "url": "",
      "category": "",
      "professional_fit": 0,
      "technical_value": 0,
      "career_value": 0,
      "information_density": 0,
      "source_quality": 0,
      "trend_value": 0
    }
  ]
}
"""
    return _generate_recommendations_with_prompt(articles, prompt, limit)
