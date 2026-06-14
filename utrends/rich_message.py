"""
Rich Message helpers — Telegram Bot API 10.1 (June 11, 2026)
https://core.telegram.org/bots/api#sendrichmessage

Отправляет RichMessage через прямой HTTP-запрос (aiogram ещё не поддерживает
методы Bot API 10.1). При ошибке возвращает None — вызывающий код должен
сделать fallback на обычный HTML send_message.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence

import aiohttp


# ── RichText node builders ──────────────────────────────────────────────────────

def rt_plain(text: str) -> dict:
    """Простой текст."""
    return {"type": "plain", "text": text}


def rt_bold(inner: str | dict) -> dict:
    """Жирный. inner — строка или RichText-узел."""
    if isinstance(inner, str):
        inner = rt_plain(inner)
    return {"type": "bold", "text": inner}


def rt_italic(inner: str | dict) -> dict:
    if isinstance(inner, str):
        inner = rt_plain(inner)
    return {"type": "italic", "text": inner}


def rt_url(label: str, url: str) -> dict:
    """Кликабельная ссылка."""
    return {"type": "url", "text": rt_plain(label), "url": url}


def rt_concat(*parts: str | dict) -> dict:
    """Склеивает несколько RichText-узлов в один параграф."""
    nodes = [rt_plain(p) if isinstance(p, str) else p for p in parts]
    return {"type": "concat", "texts": nodes}


# ── RichBlock builders ──────────────────────────────────────────────────────────

def rb_heading(content: str | dict) -> dict:
    """Заголовок секции (крупный, выделенный)."""
    if isinstance(content, str):
        content = rt_plain(content)
    return {"type": "section_heading", "content": content}


def rb_paragraph(*parts: str | dict) -> dict:
    """Параграф — один или несколько RichText-узлов."""
    if len(parts) == 1:
        content = rt_plain(parts[0]) if isinstance(parts[0], str) else parts[0]
    else:
        content = rt_concat(*parts)
    return {"type": "paragraph", "content": content}


def rb_divider() -> dict:
    """Горизонтальный разделитель."""
    return {"type": "divider"}


def rb_list(items: Sequence[str | dict]) -> dict:
    """Маркированный список. items — строки или RichText-узлы."""
    list_items = [
        {"content": rt_plain(i) if isinstance(i, str) else i}
        for i in items
    ]
    return {"type": "list", "items": list_items}


def rb_blockquote(content: str | dict) -> dict:
    if isinstance(content, str):
        content = rt_plain(content)
    return {"type": "block_quotation", "content": content}


def rb_footer(content: str | dict) -> dict:
    if isinstance(content, str):
        content = rt_plain(content)
    return {"type": "footer", "content": content}


# ── Дайджест-специфические блоки ───────────────────────────────────────────────

def build_blocks_google_trends(
    trends: list[dict],
    min_traffic: int,
    limit: int,
) -> list[dict]:
    """Блоки для Google Trends дайджеста."""
    formatted_traffic = f"{min_traffic:,}".replace(",", "\u00a0")
    blocks: list[dict] = [
        rb_heading(rt_bold(f"🔎 Google Trends: больше {formatted_traffic} запросов")),
        rb_divider(),
    ]
    for idx, trend in enumerate(trends[:limit], 1):
        traffic = trend.get("traffic") or ""
        title = trend.get("title", "")

        parts: list[str | dict] = [rt_plain(f"{idx}. "), rt_bold(title)]
        if traffic:
            parts += [rt_plain(" — "), rt_italic(traffic)]
        blocks.append(rb_paragraph(*parts))

        news_items = [
            rt_url(n["title"], n["url"])
            for n in (trend.get("news") or [])[:2]
        ]
        if news_items:
            blocks.append(rb_list(news_items))

        if idx < min(len(trends), limit):
            blocks.append(rb_divider())

    return blocks


def build_blocks_wiki(
    articles: list[dict],
    limit: int,
) -> list[dict]:
    """Блоки для Википедия-дайджеста."""
    blocks: list[dict] = [
        rb_heading(rt_bold("📚 Русская Википедия: топ просмотров")),
        rb_divider(),
    ]
    items = []
    for idx, article in enumerate(articles[:limit], 1):
        views = f"{article['views']:,}".replace(",", "\u00a0")
        label = f"{idx}. {article['title']} — {views} просм."
        items.append(rt_url(label, article["url"]))
    if items:
        blocks.append(rb_list(items))
    return blocks


def build_blocks_blogger(
    digest: dict,
    title: str,
    repeated_limit: int,
    examples_per_topic: int,
    snippet_chars: int,
    chapters_per_example: int,
    latest_limit: int,
    include_latest: bool,
    include_single_topics: bool,
    single_topic_limit: int,
) -> list[dict]:
    """Блоки для дайджеста блогеров / YouTube-каналов."""
    repeated = digest.get("repeated_topics") or digest.get("repeated", [])
    single_topics = digest.get("single_topics", [])
    latest = digest.get("latest", [])
    total = len(digest.get("videos", []))

    blocks: list[dict] = [
        rb_heading(rt_bold(f"🎥 {title}")),
        rb_paragraph(rt_plain("📊 Свежих видео: "), rt_bold(str(total))),
        rb_divider(),
    ]

    # ── Повторяющиеся темы ──────────────────────────────────────────────────
    if repeated:
        blocks.append(rb_heading(rt_plain("🔥 Повторяющиеся темы")))
        for idx, cluster in enumerate(repeated[:repeated_limit], 1):
            count_label = (
                f"каналов: {cluster['channel_count']}, "
                f"видео: {cluster['item_count']}"
            )
            blocks.append(rb_paragraph(
                rt_plain(f"{idx}. "),
                rt_bold(cluster["main_title"]),
                rt_plain(f"  ({count_label})"),
            ))

            link_items: list[str | dict] = []
            for item_idx, item in enumerate(cluster["items"][:examples_per_topic]):
                link_title = (
                    item.get("video_title") or item.get("title") or cluster["main_title"]
                )
                timecode = f" ⏱ {item['start_time']}" if item.get("start_time") else ""
                label = f"🔗 {link_title} — {item['channel']}{timecode}"
                link_items.append(rt_url(label, item["link"]))

                if item_idx == 0 and chapters_per_example and item.get("chapters"):
                    chapters_text = " / ".join(
                        f"{c['start_time']} {c['title']}"
                        for c in item["chapters"][:chapters_per_example]
                    )
                    link_items.append(rt_italic(chapters_text))
                elif item_idx == 0 and snippet_chars and item.get("description_snippet"):
                    snippet = item["description_snippet"][:snippet_chars].rstrip()
                    if len(item["description_snippet"]) > snippet_chars:
                        snippet += "..."
                    link_items.append(rt_italic(snippet))

            if link_items:
                blocks.append(rb_list(link_items))

        hidden_clusters = len(repeated) - repeated_limit
        if hidden_clusters > 0:
            blocks.append(rb_footer(rt_italic(
                f"...и ещё {hidden_clusters} повторяющихся тем."
            )))
    else:
        blocks.append(rb_paragraph(
            rt_plain("🔥 Повторяющихся тем за окно дайджеста не найдено.")
        ))

    # ── Одиночные темы ──────────────────────────────────────────────────────
    if include_single_topics and single_topics and single_topic_limit:
        blocks.append(rb_divider())
        blocks.append(rb_heading(rt_plain("▫️ Одиночные темы")))
        items: list[str | dict] = []
        for cluster in single_topics[:single_topic_limit]:
            item = cluster["items"][0]
            link_title = (
                item.get("video_title") or item.get("title") or cluster["main_title"]
            )
            timecode = f" ⏱ {item['start_time']}" if item.get("start_time") else ""
            label = (
                f"{cluster['main_title']} — {link_title} "
                f"{item.get('channel', '')}{timecode}"
            )
            items.append(rt_url(label, item["link"]))
        if items:
            blocks.append(rb_list(items))

        hidden_single = len(single_topics) - single_topic_limit
        if hidden_single > 0:
            blocks.append(rb_footer(rt_italic(
                f"...и ещё {hidden_single} одиночных тем."
            )))

    # ── Что вышло (latest) ──────────────────────────────────────────────────
    if include_latest and latest and latest_limit:
        blocks.append(rb_divider())
        blocks.append(rb_heading(rt_plain("🆕 Что вышло")))
        items = []
        for item in latest[:latest_limit]:
            timecodes = item.get("timecodes") or []
            tc_text = f" ⏱ {', '.join(timecodes[:2])}" if timecodes else ""
            label = f"🔹 {item['title']} — {item['channel']}{tc_text}"
            items.append(rt_url(label, item["link"]))
        if items:
            blocks.append(rb_list(items))

        hidden_latest = len(latest) - latest_limit
        if hidden_latest > 0:
            blocks.append(rb_footer(rt_italic(
                f"...и ещё {hidden_latest} свежих видео."
            )))

    return blocks


# ── Низкоуровневая отправка ─────────────────────────────────────────────────────

async def send_rich_message(
    token: str,
    chat_id: int,
    blocks: list[dict],
    **kwargs,
) -> dict | None:
    """
    Отправляет Rich Message через прямой HTTP к Bot API 10.1.

    Возвращает result-объект при успехе, None при ошибке.
    Вызывающий код должен сделать fallback на send_message + HTML при None.
    """
    url = f"https://api.telegram.org/bot{token}/sendRichMessage"
    payload: dict = {
        "chat_id": chat_id,
        "rich_message": {"blocks": blocks},
        **kwargs,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.json()
                if not data.get("ok"):
                    logging.warning(
                        "sendRichMessage failed for chat_id=%s: %s",
                        chat_id,
                        data.get("description", "unknown error"),
                    )
                    return None
                return data.get("result")
    except Exception as exc:
        logging.error("sendRichMessage HTTP error for chat_id=%s: %s", chat_id, exc)
        return None
