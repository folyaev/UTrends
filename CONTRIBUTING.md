# Contributing

UTrends is a small Telegram bot project, so contributions should stay pragmatic:
fix concrete behavior, keep changes focused, and add tests when touching shared
logic.

## Local Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `BOT_TOKEN`, `SEARXNG_BASE_URL`, and `ADMIN_CHAT_IDS` in `.env`.

## Checks

Run before committing:

```powershell
python -m py_compile .\bot.py .\config.py .\db_backup.py .\feed_security.py .\healthcheck.py .\logging_utils.py .\migrations.py .\rate_limit.py .\rss_parser.py .\searxng_client.py .\telegram_html.py .\trends_parser.py .\wiki_trends.py .\url_utils.py
python -m unittest discover -s tests -v
docker compose build
```

## Rules

- Never commit `.env`, Telegram tokens, SQLite databases, backups, or user data.
- Keep admin-only features behind `ADMIN_CHAT_IDS`.
- Escape external text before putting it into Telegram HTML.
- Validate any URL that is fetched based on user/admin input.
- Prefer small modules with unit tests over growing `bot.py` further.

## Useful Areas

- Better Russian-language matching and normalized-title deduplication.
- Integration tests for Radar and callbacks.
- Source health metrics and automatic noisy-feed suppression.
- Dedicated adapters or RSSHub routes for VK, OK, and X/Twitter.
