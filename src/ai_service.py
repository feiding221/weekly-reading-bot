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

# The model evaluates these dimensions; Python calculates the final score so
# the weighting is stable across runs and is not left entirely to the model.
VALUE_WEIGHTS = {
    "professional_fit": 30,
    "technical_value": 25,
    "career_value": 15,
    "information_density": 15,
    "source_quality": 10,
    "trend_value": 5,
}
MIN_VALUE_SCORE = 60


def _calculate_value_score(item):
    """Calculate a deterministic 0-100 value score from model sub-scores."""
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

        # Do not let malformed/missing score fields silently turn an article
        # into a high-value recommendation. The final threshold is applied
        # after the deterministic Python calculation.
        if item["value_score"] < MIN_VALUE_SCORE:
            continue

        sanitized.append(item)

    # Rank by the deterministic final score before applying the output limit.
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
    return _sanitize_recommendations(data.get("recommendations", []), limit)


def generate_reading_recommendations(articles, limit=3):
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

综合分不是由你自由决定，而是由程序按以下固定权重计算：
professional_fit 30% + technical_value 25% + career_value 15% + information_density 15% + source_quality 10% + trend_value 5%。
程序会按综合分排序，并淘汰综合分低于 60 分的文章。

请从候选池中先按综合价值排序，尽量返回最多 6 篇候选，让程序从中选择最终推荐内容。
不要为了凑数量提高低价值文章的分数。如果候选文章确实不足，可以少返回；但不要因为只有少数候选就随意返回空数组。

【分类规则】
category 必须且只能从下面 10 个固定分类中选择 1 个，不得创造新分类、修改名称或输出其他语言版本：
1. AI与模型
2. AIGC与生成式AI
3. AI Agent
4. 3D与CG
5. VFX与影视
6. 游戏与实时技术
7. 数字媒体工具
8. 开发与开源
9. AI产业与应用
10. 研究与前沿

分类表示文章的“主领域”，只能选择一个。不要把 AI、科技、趋势、编程、商业、科研等宽泛词作为分类。

【标签规则】
tags 只能从下面 30 个固定标签中选择，最多 3 个，可以少于 3 个，不能为了凑数添加标签，不得创造新标签：
LLM、多模态、AI Agent、生成式AI、AI模型、AI图像、AI视频、AI音频、AI 3D、AI创作、Blender、Houdini、Nuke、Unreal Engine、Unity、Rendering、VFX、Motion Graphics、Virtual Production、Open Source、GitHub、API / SDK、MCP、AI开发、NVIDIA、Hugging Face、OpenAI、Google、研究前沿。

标签表示文章涉及的具体模型、软件、平台或技术主题。不要使用 AI、科技、商业、科研、趋势、编程、行业动态等宽泛词作为标签。

分类和标签不要表达同一个概念。例如分类为“VFX与影视”时，不要因为分类本身而添加“VFX”；分类为“AI与模型”时，不要添加“生成式AI”作为泛化重复标签，除非文章确实涉及该具体技术主题。

标题要求：
- Global AI Reading 的“title”必须输出自然、准确、简洁的中文标题，不要直接保留英文原题。
- 专有名词、模型名、产品名、公司名可以保留英文或官方名称，例如 OpenAI、Gemini、Qwen、NVIDIA。
- 不要逐词生硬直译；应根据正文含义生成适合中文阅读的标题。
- 标题不得添加原文中没有的事实、数字或结论。

摘要 summary 必须基于文章正文进行中文总结，不要只是改写标题。
推荐理由 reason 必须说明这篇文章对数字媒体技术本科生具体有什么价值。

输出要求：所有字段中文，严格输出JSON，不要输出Markdown或额外文字。
JSON格式必须为：
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


def generate_china_ai_recommendations(articles, limit=3):
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

综合分由程序按固定权重计算：professional_fit 30% + technical_value 25% + career_value 15% + information_density 15% + source_quality 10% + trend_value 5%。程序会按综合分排序，并淘汰综合分低于 60 分的文章。

请先按综合价值排序，并尽量返回 LIMIT_VALUE 篇高质量候选，供后续程序进行来源多样性筛选。
不要为了凑数量提高低价值文章的分数。如果候选文章不足，可以少返回；但不要因为候选数量少就随意返回空数组。

重点关注：
1. 是否体现中国AI产业和技术发展趋势。
2. 是否对数字媒体技术学生学习、项目实践或职业规划有价值。
3. 优先官方技术博客、开发者平台、企业案例。
4. 降低纯新闻、营销宣传、无技术细节内容权重。
5. 优先选择不同来源的文章，避免推荐结果过度集中于同一个媒体。
6. 信息密度：优先正文包含具体技术、产品、方法、数据或实践细节的文章。

【分类规则】
category 必须且只能从下面 10 个固定分类中选择 1 个：
AI与模型、AIGC与生成式AI、AI Agent、3D与CG、VFX与影视、游戏与实时技术、数字媒体工具、开发与开源、AI产业与应用、研究与前沿。
不得创造新分类。分类表示文章的主领域，只能选择一个。

【标签规则】
tags 只能从下面 30 个固定标签中选择，最多 3 个，可以少于 3 个，不得创造新标签：
LLM、多模态、AI Agent、生成式AI、AI模型、AI图像、AI视频、AI音频、AI 3D、AI创作、Blender、Houdini、Nuke、Unreal Engine、Unity、Rendering、VFX、Motion Graphics、Virtual Production、Open Source、GitHub、API / SDK、MCP、AI开发、NVIDIA、Hugging Face、OpenAI、Google、研究前沿。
不要使用 AI、科技、商业、科研、趋势、编程等宽泛词作为标签，也不要为了凑数量添加标签。

分类和标签不要重复表达同一个概念。

summary 必须基于正文内容进行中文概括，不要只翻译或改写标题。
reason 必须结合正文说明其对数字媒体技术本科生的具体价值。

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

请先按综合价值排序，并尽量返回 LIMIT_VALUE 篇高质量候选，供后续程序进行来源多样性筛选。
""".replace("LIMIT_VALUE", str(limit))
    return _generate_recommendations_with_prompt(articles, prompt, limit)
