# Telegram Bot API 2026 — Справочник по форматированию и новым функциям

> Составлен 14 июня 2026. Источник: https://core.telegram.org/bots/api
> Для обновления других ботов.

---

## HTML-форматирование (ParseMode.HTML)

Самый надёжный режим. Поддерживается во всех версиях aiogram 3.x.

```python
parse_mode=ParseMode.HTML
```

### Доступные теги

| Тег | Описание | Пример |
|-----|----------|--------|
| `<b>текст</b>` | **Жирный** | `<b>Важно</b>` |
| `<i>текст</i>` | *Курсив* | `<i>примечание</i>` |
| `<u>текст</u>` | Подчёркнутый | `<u>заголовок</u>` |
| `<s>текст</s>` | ~~Зачёркнутый~~ | `<s>устарело</s>` |
| `<code>текст</code>` | `Моноширинный` (inline) | `<code>/command</code>` |
| `<pre>текст</pre>` | Блок кода | многострочный |
| `<pre><code class="python">код</code></pre>` | Блок кода с подсветкой | language hint |
| `<a href="URL">текст</a>` | Ссылка | `<a href="https://...">читать</a>` |
| `<tg-spoiler>текст</tg-spoiler>` | Скрытый спойлер | скрытый текст |
| `<blockquote>текст</blockquote>` | Цитата | визуально выделенная |
| `<blockquote expandable>текст</blockquote>` | Сворачиваемая цитата | по клику разворачивается |
| `<tg-emoji emoji-id="ID">☺</tg-emoji>` | Custom emoji | Telegram Premium |

### Экранирование в HTML

Обязательно экранировать в тексте:
```python
text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
```

---

## MarkdownV2 (ParseMode.MARKDOWN_V2)

> ⚠️ Сложнее в использовании из-за обязательного экранирования. Предпочитайте HTML.

Символы для экранирования: `_ * [ ] ( ) ~ \` > # + - = | { } . !`

```python
import re
def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!\\])', r'\\\1', text)
```

---

## Rich Messages — Bot API 10.1 (11 июня 2026) 🆕

Новый метод `sendRichMessage` для красивых структурированных сообщений.
**aiogram** ещё не поддерживает — нужен raw HTTP запрос.

### Отправка

```python
import aiohttp

async def send_rich_message(token: str, chat_id: int, blocks: list) -> dict | None:
    url = f"https://api.telegram.org/bot{token}/sendRichMessage"
    payload = {"chat_id": chat_id, "rich_message": {"blocks": blocks}}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=payload) as r:
            data = await r.json()
            return data.get("result") if data.get("ok") else None
```

### Структура блоков

```python
# Заголовок секции
{"type": "section_heading", "content": {"type": "bold", "text": {"type": "plain", "text": "Заголовок"}}}

# Параграф с текстом
{"type": "paragraph", "content": {"type": "plain", "text": "Обычный текст"}}

# Ссылка в параграфе
{"type": "paragraph", "content": {"type": "url", "text": {"type": "plain", "text": "Нажми"}, "url": "https://..."}}

# Горизонтальный разделитель
{"type": "divider"}

# Маркированный список
{"type": "list", "items": [
    {"content": {"type": "plain", "text": "Пункт 1"}},
    {"content": {"type": "url",   "text": {"type": "plain", "text": "Ссылка"}, "url": "https://..."}}
]}

# Цитата
{"type": "block_quotation", "content": {"type": "plain", "text": "Цитируемый текст"}}

# Подвал (мелкий текст)
{"type": "footer", "content": {"type": "italic", "text": {"type": "plain", "text": "...и ещё 3 темы"}}}
```

### Типы RichText

| type | Поля | Описание |
|------|------|----------|
| `plain` | `text: str` | Обычный текст |
| `bold` | `text: RichText` | Жирный |
| `italic` | `text: RichText` | Курсив |
| `underline` | `text: RichText` | Подчёркнутый |
| `strikethrough` | `text: RichText` | Зачёркнутый |
| `spoiler` | `text: RichText` | Спойлер |
| `url` | `text: RichText`, `url: str` | Ссылка |
| `marked` | `text: RichText` | Выделение (highlight) |
| `code` | `text: RichText` | Моноширинный |
| `concat` | `texts: list[RichText]` | Склейка нескольких узлов |

### Доступные типы блоков

| type | Описание |
|------|----------|
| `section_heading` | Крупный заголовок секции |
| `paragraph` | Абзац текста |
| `divider` | Горизонтальный разделитель |
| `list` | Маркированный список |
| `block_quotation` | Цитата (блок) |
| `pull_quotation` | Выносная цитата (боковая) |
| `preformatted` | Блок кода |
| `footer` | Подвал / мелкий текст |
| `anchor` | Якорь для ссылок |

### Другие новые методы Bot API 10.1

- `sendRichMessageDraft` — потоковая отправка (streaming AI-ответов)
- `editMessageText` теперь принимает `rich_message` — редактирование rich сообщения

---

## Новое в Bot API 10.0 (8 мая 2026)

### Guest Mode
Бот может отвечать в чатах, где он **не является участником**:

```python
# В Message появились новые поля:
# message.guest_bot_caller_user — пользователь, вызвавший бота как гостя
# message.guest_query_id — ID запроса для answerGuestQuery
await bot(answerGuestQuery(guest_query_id=..., text="ответ"))
```

### Новые типы медиа в опросах
```python
# sendPoll теперь поддерживает media в вопросе и explanation_media
await bot.send_poll(chat_id=..., question="Вопрос?", options=[...], media=InputPollMedia(...))
```

---

## Полезные паттерны

### Авточистка технических сообщений

```python
async def schedule_delete(bot, chat_id: int, message_id: int, delay: float = 60.0):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# Использование:
confirm = await message.reply("✅ Готово")
asyncio.create_task(schedule_delete(bot, chat_id, confirm.message_id, delay=60))
```

### Разворачиваемый blockquote (expandable)

```python
text = (
    "<b>Заголовок новости</b>\n"
    "<blockquote expandable>"
    "Подробное описание, которое сворачивается по умолчанию..."
    "</blockquote>"
)
await message.answer(text, parse_mode=ParseMode.HTML)
```

### Безопасное экранирование HTML

```python
from html import escape

def html_text(value) -> str:
    return escape(str(value))

def html_link(url: str, label: str) -> str:
    return f'<a href="{escape(url)}">{html_text(label)}</a>'
```

### Safe callback_data (лимит 64 байта)

```python
import hashlib

def safe_cb(action: str, topic: str, max_topic_len: int = 50) -> str:
    truncated = topic[:max_topic_len]
    if len(truncated) < len(topic):
        # добавляем хэш чтобы избежать коллизий
        h = hashlib.md5(topic.encode()).hexdigest()[:6]
        return f"{action}|{truncated}|{h}"
    return f"{action}|{truncated}"
```

---

## Ссылки

- Bot API Changelog: https://core.telegram.org/bots/api-changelog
- Formatting options: https://core.telegram.org/bots/api#formatting-options
- Rich Messages: https://core.telegram.org/bots/api#sendrichmessage
- Features overview: https://core.telegram.org/bots/features#rich-messages
