from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

ALLOWED_CATEGORIES = {
    "AI与模型", "AIGC与生成式AI", "AI Agent", "3D与CG", "VFX与影视",
    "游戏与实时技术", "数字媒体工具", "开发与开源", "AI产业与应用", "研究与前沿",
}

ALLOWED_TAGS = {
    "LLM", "多模态", "AI Agent", "生成式AI", "AI模型", "AI图像", "AI视频", "AI音频",
    "AI 3D", "AI创作", "Blender", "Houdini", "Nuke", "Unreal Engine", "Unity", "Rendering",
    "VFX", "Motion Graphics", "Virtual Production", "Open Source", "GitHub", "API / SDK",
    "MCP", "AI开发", "NVIDIA", "Hugging Face", "OpenAI", "Google", "研究前沿",
}

VALUE_WEIGHTS = {
    "professional_fit": 30,
    "technical_value": 25,
    "career_value": 15,
    "information_density": 15,
    "source_quality": 10,
    "trend_value": 5,
}

GLOBAL_BATCH_SIZE = 10
GLOBAL_TARGET_CANDIDATES = 6


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


def _generate_recommendations_with_prompt(articles, system_prompt, limit=6):
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(articles, ensure_ascii=False)},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    recommendations = _sanitize_recommendations(data.get("recommendations", []), limit)

    return recommendations


def _build_global_prompt(fallback=False):
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

请按综合价值排序，返回这一批中最值得保存的候选，最多 6 篇。
不要为了凑数量提高低价值文章的分数。
如果这一批不存在值得保存的文章，可以返回更少，甚至返回空数组。

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
    if fallback:
        prompt += "\n这是一次兜底重试。只要求返回这一批中实际值得保存的文章；不要为了凑数量而降低标准。"
    return prompt


def generate_reading_recommendations(articles, limit=6, fallback=False):
    return _generate_recommendations_with_prompt(
        articles,
        _build_global_prompt(fallback=fallback),
        limit,
    )


def generate_global_batched_recommendations(articles, batch_size=GLOBAL_BATCH_SIZE, target_candidates=GLOBAL_TARGET_CANDIDATES):
    """Analyze Global articles in small batches and stop once enough candidates exist."""
    all_candidates = []

    # Interleave articles by source so early batches are not dominated by one RSS source.
    grouped = {}
    source_order = []
    for article in articles:
        source = article.get("source", "unknown")
        if source not in grouped:
            grouped[source] = []
            source_order.append(source)
        grouped[source].append(article)

    mixed_articles = []
    while True:
        added = False
        for source in source_order:
            if grouped[source]:
                mixed_articles.append(grouped[source].pop(0))
                added = True
        if not added:
            break

    total_batches = (len(mixed_articles) + batch_size - 1) // batch_size

    for batch_index, start in enumerate(range(0, len(mixed_articles), batch_size), start=1):
        batch = mixed_articles[start:start + batch_size]
        candidates = generate_reading_recommendations(batch, limit=6)
        all_candidates.extend(candidates)
        all_candidates = _sanitize_recommendations(all_candidates, limit=target_candidates)

        print(
            f"Global AI batch {batch_index}/{total_batches}: "
            f"processed={len(batch)}, candidates={len(candidates)}, "
            f"total_candidates={len(all_candidates)}"
        )

        if len(all_candidates) >= target_candidates:
            break

    return all_candidates


def generate_china_ai_recommendations(articles, limit=6):
    prompt = """
你负责 China AI Reading 专栏内容筛选。

输入中的每篇文章可能包含：标题、RSS摘要、网页正文 content。
请优先依据正文 content 判断文章价值；正文缺失时再使用标题和RSS摘要。

【China 内容地域规则】
China AI Reading 的“China”不是指 RSS 来源网站所在地区，而是指文章实际内容所属的中国 AI / 数字媒体生态。
中国来源可能包含大量国际资讯，因此绝不能仅因为 source 来自 InfoQ、量子位、36Kr 等中国媒体，就认为文章属于 China。

必须优先根据网页正文 content 判断文章内容地域：
- content_scope = "china"：文章核心内容直接属于中国 AI / AIGC / 数字内容 / 游戏与实时技术生态，例如中国公司、国产模型、国产产品、中国企业实践、中国高校或研究机构、中国开发者生态、中国行业应用，以及中国机构对国际技术的具体落地实践。
- content_scope = "international"：文章核心内容是海外公司、海外模型、海外产品、海外技术博客、海外行业事件等，即使文章由中国媒体发布或转载，也必须判定为 international。
- 如果标题、摘要与正文存在冲突，以正文为最高依据。
- 正文为空时，不要凭 source 猜测为 China；只有标题和摘要能够明确证明核心内容属于中国生态时，才可以判定为 china，否则判定为 international。

明确排除的典型国际内容包括但不限于：Anthropic / Claude、OpenAI / ChatGPT、Google / Gemini、Meta AI、NVIDIA 等国际公司自身的纯国际产品或公司新闻，以及其他主要围绕海外主体展开的资讯。

请在每个候选对象中额外输出：
"content_scope": "china" 或 "international"，
"content_scope_reason": "一句话说明文章核心内容为什么属于中国或国际生态"。

只有 content_scope = "china" 的文章才允许进入最终 recommendations；content_scope = "international" 的文章必须排除，不得因为价值分数高而保留。

【价值评价】
目标用户：中国数字媒体技术本科生。
重点关注：
- 中国AI大模型
- AIGC图像、视频、3D生成
- AI Agent
- 游戏AI
- 数字内容生产工具
- 国产AI开发平台
- 企业AI应用案例

请对每篇通过地域资格判断的候选文章分别进行以下 6 项 0-100 分评价：
1. professional_fit：与数字媒体技术专业方向的匹配度。
2. technical_value：技术深度、技术含量和实践价值。
3. career_value：对学习、项目实践、技能选择或职业发展的帮助。
4. information_density：正文是否包含具体技术、产品、方法、数据、案例或实践细节。
5. source_quality：来源是否可靠、一手、专业，官方技术来源优先。
6. trend_value：是否代表值得关注的技术趋势或行业变化。

综合分由程序按固定权重计算：professional_fit 30% + technical_value 25% + career_value 15% + information_density 15% + source_quality 10% + trend_value 5%。

请先过滤掉所有 content_scope = "international" 的文章，再按综合价值排序，并尽量返回最多 6 篇高质量、content_scope = "china" 的候选，供后续程序进行来源多样性筛选。
不要为了凑数量提高低价值文章的分数；如果符合 China 内容资格的文章不足，可以少返回，但不要用国际文章补位。

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
      "content_scope": "china",
      "content_scope_reason": "",
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
