import json
from urllib.parse import urlparse

from notion_api import create_reading_page
from ai_service import client, _build_global_prompt, _sanitize_recommendations
from content_fetcher import fetch_articles, enrich_articles_with_content
from dedup import filter_new_articles, update_history


GLOBAL_AI_CONTENT_LIMIT = 3000
GLOBAL_AI_MAX_OUTPUT_TOKENS = 2200


def _source_key(item):
    """Use the article URL domain as the stable source identifier."""
    url = item.get("url", "")
    hostname = urlparse(url).netloc.lower()
    return hostname.removeprefix("www.") or item.get("source", "unknown").strip().lower()


def _print_stats(stats, label="Global"):
    print(f"{label} dedup: URL={stats['duplicate_urls']}, title={stats['duplicate_titles']}, both={stats['duplicate_both']}, new={stats['new_articles']}")


def _mix_articles_by_source(articles):
    """Interleave articles by source so early AI batches are not dominated by one RSS source."""
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

    return mixed_articles


def _compact_article_for_ai(article):
    """Send only the fields needed by the Global selector and cap long page text."""
    content = article.get("content", "") or ""
    if len(content) > GLOBAL_AI_CONTENT_LIMIT:
        content = (
            content[:2200]
            + "\n...[正文中段已省略，仅保留首尾关键信息]...\n"
            + content[-800:]
        )

    return {
        "title": article.get("title", ""),
        "summary": article.get("summary", ""),
        "source": article.get("source", ""),
        "url": article.get("url", ""),
        "content": content,
    }


def _generate_global_batch_recommendations(batch, limit=3):
    """Let each batch directly return final recommendations; do not build a candidate pool."""
    compact_articles = [_compact_article_for_ai(article) for article in batch]

    final_prompt = _build_global_prompt() + """

【Global最终推荐模式】
本次不是建立候选池，而是直接为 Global AI Reading 选择最终要写入 Notion 的文章。
请在这一批文章中直接挑选最值得保存的文章，最多 3 篇。
只返回你认为真正达到保存标准的文章；如果没有足够高价值的文章，可以返回更少，甚至返回空数组。
不要为了后续排序而额外扩大返回数量，不要返回“候选文章”。
"""

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        response_format={"type": "json_object"},
        max_tokens=GLOBAL_AI_MAX_OUTPUT_TOKENS,
        extra_body={"thinking": {"type": "disabled"}},
        messages=[
            {"role": "system", "content": final_prompt},
            {"role": "user", "content": json.dumps(compact_articles, ensure_ascii=False)},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    return _sanitize_recommendations(data.get("recommendations", []), limit)


def _generate_global_batched_recommendations(articles, batch_size=6, target_recommendations=3):
    """Process Global articles in small batches and collect final recommendations directly."""
    mixed_articles = _mix_articles_by_source(articles)
    total_batches = (len(mixed_articles) + batch_size - 1) // batch_size
    recommendations = []
    used_sources = set()
    enriched_count = 0

    for batch_index, start in enumerate(range(0, len(mixed_articles), batch_size), start=1):
        batch = mixed_articles[start:start + batch_size]

        # Global only: article pages are independent HTTP requests, so bounded
        # concurrency cuts wall-clock time without increasing article count or API calls.
        enrich_articles_with_content(batch, max_workers=8)
        batch_enriched = sum(1 for item in batch if item.get("content"))
        enriched_count += batch_enriched

        batch_recommendations = _generate_global_batch_recommendations(batch, limit=3)

        # Add suitable articles directly to the final list. Keep source diversity
        # here instead of building a larger candidate pool and sorting it later.
        added_this_batch = 0
        for item in batch_recommendations:
            source = _source_key(item)
            if source in used_sources:
                continue
            recommendations.append(item)
            used_sources.add(source)
            added_this_batch += 1
            if len(recommendations) >= target_recommendations:
                break

        print(
            f"Global AI batch {batch_index}/{total_batches}: "
            f"processed={len(batch)}, enriched={batch_enriched}, "
            f"recommendations={added_this_batch}, "
            f"total_recommendations={len(recommendations)}"
        )

        if len(recommendations) >= target_recommendations:
            break

    return recommendations, enriched_count


def run_global_pipeline():
    print("\n=== Global Reading Pipeline ===")

    articles = fetch_articles(limit=20)
    print(f"Global fetch: {len(articles)} articles")

    new_articles, stats = filter_new_articles(articles)
    _print_stats(stats)

    if not new_articles:
        print("Global result: 0 articles (no new articles)")
        print("Global pipeline completed.")
        return

    recommendations, content_count = _generate_global_batched_recommendations(
        new_articles,
        batch_size=6,
        target_recommendations=3,
    )
    print(f"Global content: {content_count}/{len(new_articles)} enriched before stopping")
    print(f"Global AI: {len(recommendations)} final recommendations")

    sources = [_source_key(item) for item in recommendations]
    print(f"Global sources: {', '.join(sources) if sources else 'none'}")

    if not recommendations:
        print("Global result: 0 articles (no recommendations)")
        print("Global pipeline completed.")
        return

    written_articles = []
    for item in recommendations:
        try:
            create_reading_page(item)
            written_articles.append(item)
        except Exception as exc:
            print(f"Global Notion write failed: {item.get('title', 'Untitled')} | {exc}")

    failed_count = len(recommendations) - len(written_articles)
    print(f"Global Notion: written={len(written_articles)}, failed={failed_count}")

    if written_articles:
        update_history(written_articles)
        print(f"Global history: added={len(written_articles)}")
    else:
        print("Global history: unchanged")

    print("Global pipeline completed.")
