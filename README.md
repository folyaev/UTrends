# UTrends Bot

Telegram-бот для личного мониторинга новостной повестки: RSS-источники, Google Trends, Русская Википедия, отслеживаемые темы и отдельная статистика по YouTube-блогерам/новостным каналам.

Основная идея: быстро увидеть, что повторяется в разных источниках, что новое появилось с прошлого дайджеста и какие темы обсуждают выбранные YouTube-каналы.

## Что умеет

- Собирает общий RSS-дайджест по категориям источников.
- Показывает только новые материалы через `/fresh`, чтобы два одинаковых дайджеста подряд не засоряли чат.
- Отслеживает пользовательские темы и присылает уведомления, когда появляются свежие совпадения.
- Ищет по RSS и SearXNG News через `/search`.
- Показывает Google Trends через `/force`.
- Показывает топ читаемых статей Русской Википедии через `/wiki`.
- Отдельно анализирует YouTube-блогеров через `/bloggers`: названия видео, главы/таймкоды из описаний, повторяющиеся темы и одиночные темы.
- Отдельно учитывает YouTube-новостные каналы в общем дайджесте, не смешивая их со списком блогеров.
- Позволяет включать/отключать категории RSS-источников через `/sources`.
- Для админов есть добавление RSS, диагностика источников и резервные копии базы.

## Команды

| Команда | Что делает |
| --- | --- |
| `/start` | Подписаться на автоматический дайджест. |
| `/stop` | Отписаться от автоматического дайджеста. |
| `/help` | Показать подсказку по командам. |
| `/digest` | Собрать общий дайджест вручную. |
| `/digest 6h` | Собрать дайджест за 6 часов. |
| `/digest 3d` | Собрать дайджест за 3 дня. |
| `/fresh` | Показать только то, чего ещё не было во fresh-дайджестах пользователя. |
| `/fresh 12h` | Показать новое за 12 часов. |
| `/bloggers` | Показать статистику тем по YouTube-блогерам за стандартное окно. |
| `/bloggers 6d` | Показать статистику блогеров за 6 дней. |
| `/search запрос` | Найти новости по RSS и SearXNG News. |
| `/force` | Получить горячие поисковые тренды Google Trends. |
| `/wiki` | Показать топ читаемых статей Русской Википедии за вчера. |
| `/subs` | Показать отслеживаемые темы. |
| `/ignored` | Показать скрытые темы. |
| `/sources` | Включить или отключить категории RSS-источников. |
| `/addfeed URL` | Добавить RSS-ленту. Только для админов. |
| `/feedhealth` | Проверить доступность RSS-источников. Только для админов. |
| `/backup` | Создать резервную копию SQLite. Только для админов. |

Окна времени задаются в часах или днях: `6h`, `12h`, `3d`, `6d`. Максимум ограничен настройкой `MAX_DIGEST_WINDOW_HOURS`.

## Источники

Локальные списки источников не должны попадать в Git:

- `feeds.json` — RSS-источники по категориям.
- `bloggers.json` — YouTube-блогеры и авторские каналы.
- `news_channels.json` — YouTube-новостные каналы с большим количеством роликов.
- `news_video_trends_parser_codex.md` — личные заметки по парсеру.

Для публичного репозитория есть безопасные примеры без приватных списков:

```powershell
Copy-Item feeds.example.json feeds.json
Copy-Item bloggers.example.json bloggers.json
Copy-Item news_channels.example.json news_channels.json
```

После копирования замените `example.com` и `UC_REPLACE_WITH...` на свои RSS URL и YouTube channel_id. `source_id` должен быть коротким стабильным идентификатором без пробелов. `feed_type` используйте как `blogger` для `bloggers.json` и `news_channel` для `news_channels.json`.

### Формат YouTube-источника

```json
{
  "source_id": "lucy_grin",
  "name": "Люся Грин",
  "platform": "youtube",
  "feed_type": "blogger",
  "language": "ru",
  "region_focus": "Russia;world",
  "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCWrWMJFCkYWf7GmqoUR4TRA",
  "channel_url": "https://www.youtube.com/channel/UCWrWMJFCkYWf7GmqoUR4TRA",
  "parser_priority": 2,
  "banned_ru": false,
  "notes": ""
}
```

`banned_ru` — ручной флаг для каналов, которые имеют ограничительный статус в России. Бот читает это поле, но статус нужно проставлять вручную и проверенно.

## Как работает YouTube-блок

`/bloggers` берёт каналы из `bloggers.json`.

Общий `/digest` дополнительно может показывать:

- блок блогеров из `bloggers.json`;
- отдельный блок новостных YouTube-каналов из `news_channels.json`.

Темы берутся из:

- названий видео;
- глав/таймкодов из описания видео, если YouTube RSS отдал описание с таймкодами.

Важно: YouTube RSS не всегда отдаёт полное описание. Если таймкодов нет в RSS summary/description, текущая версия не сможет их увидеть. Возможные улучшения описаны в [ROADMAP.md](ROADMAP.md).

## Быстрый запуск

Создать `.env`:

```powershell
Copy-Item .env.example .env
```

Минимально нужно указать:

```env
BOT_TOKEN=replace_with_your_telegram_bot_token
SEARXNG_BASE_URL=http://host.docker.internal:8888
ADMIN_CHAT_IDS=replace_with_your_telegram_chat_id
```

Запуск:

```powershell
docker compose up -d --build
```

Проверить статус и логи:

```powershell
docker compose ps
docker logs -f trends-bot
```

Остановка:

```powershell
docker compose down
```

Если локальный DNS нестабилен для `api.telegram.org`, можно скопировать `docker-compose.override.example.yml` в `docker-compose.override.yml` и указать актуальный IP Telegram API. Override должен оставаться локальным.

## Конфигурация

Все runtime-настройки перечислены в `.env.example`.

Основные:

- `DIGEST_INTERVAL_HOURS` — период автоматического дайджеста.
- `DIGEST_WINDOW_HOURS` — окно дайджеста по умолчанию.
- `MAX_DIGEST_WINDOW_HOURS` — максимальное окно для `/digest`, `/fresh`, `/bloggers`.
- `WATCHDOG_INTERVAL_HOURS` и `WATCHDOG_WINDOW_HOURS` — частота и окно проверки отслеживаемых тем.
- `BLOGGER_*` — лимиты и таймауты YouTube-блока.
- `RSS_FETCH_*` — таймауты и retry для RSS.
- `BACKUP_*` — настройки резервных копий.
- `RSSHUB_*` — опциональные RSSHub-маршруты для VK, OK и X/Twitter.

## Локальная разработка

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m utrends.bot
```

Проверки:

```powershell
python -m compileall -q utrends tests
python -m unittest discover -s tests -v
```

## Архитектура

```text
Telegram user
   |
aiogram utrends.bot
   |
   +-- utrends/rss_parser.py       RSS, общий дайджест, категории, healthcheck
   +-- utrends/blogger_digest.py   YouTube RSS, темы блогеров, главы и таймкоды
   +-- utrends/searxng_client.py   SearXNG News
   +-- utrends/trends_parser.py    Google Trends RSS
   +-- utrends/wiki_trends.py      Wikimedia Pageviews API
   +-- utrends/migrations.py       SQLite migrations
   +-- utrends/db_backup.py        SQLite backups
   +-- utrends/feed_security.py    SSRF-safe проверка RSS
   +-- utrends/text_match.py       Нормализация, matching, дедупликация
   +-- utrends/time_window.py      Парсинг 6h/3d окон
   +-- utrends/telegram_html.py    Экранирование Telegram HTML
   |
trends.db + feeds.json + bloggers.json + news_channels.json + backups/
```

## Ограничения

- Matching пока эвристический, без полноценной морфологии и semantic search.
- YouTube RSS может не отдавать полное описание видео, поэтому часть таймкодов может быть недоступна.
- SearXNG может возвращать неполные или неточные даты публикации.
- `feeds.json`, `bloggers.json` и `news_channels.json` приватные: перед публикацией репозитория нужно убедиться, что они не закоммичены.
- Перед публичной публикацией нужно перевыпустить Telegram-токен, если он когда-либо был в локальных файлах.

## Что дальше

Список будущих улучшений ведётся в [ROADMAP.md](ROADMAP.md).

## Лицензия

[MIT](LICENSE)
