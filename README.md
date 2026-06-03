# UTrends Bot

![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-MVP-orange)

UTrends is a Telegram bot that watches news trends, RSS feeds, Google Trends,
Wikipedia pageviews, and user-tracked topics. It is built as a practical
personal radar: subscribe to a topic, get notified when fresh matching material
appears, and keep a digest of what is moving across sources.

The project is already packaged for Docker, has CI checks, SQLite migrations,
backups, admin-only maintenance commands, SSRF protection for feed additions,
Telegram HTML escaping, rate limits, structured JSON logs, and unit tests.

## Highlights

- Scheduled RSS digest grouped by source category.
- Radar for tracked topics with URL deduplication and source prioritization.
- Manual `/search` across RSS and SearXNG news results.
- Google Trends pull via `/force`.
- Russian Wikipedia top pageviews via `/wiki`.
- Admin-only RSS feed management through `/addfeed`.
- Admin-only RSS diagnostics through `/feedhealth`.
- Admin-only SQLite backups through `/backup`.
- Docker healthcheck and JSON logs for operational visibility.

## Commands

| Command | Description |
| --- | --- |
| `/start` | Subscribe to the scheduled digest. |
| `/stop` | Unsubscribe from the scheduled digest. |
| `/digest` | Build a digest manually. |
| `/search query` | Search RSS and SearXNG news. |
| `/force` | Pull current Google Trends. |
| `/wiki` | Show top Russian Wikipedia articles. |
| `/subs` | Show tracked topics. |
| `/ignored` | Show hidden topics. |
| `/addfeed URL` | Add an RSS feed. Admin only. |
| `/feedhealth` | Check RSS source availability. Admin only. |
| `/backup` | Create a SQLite backup. Admin only. |

## Architecture

```text
Telegram user
   |
aiogram bot.py
   |
   +-- rss_parser.py       RSS fetch, digest clustering, feed health
   +-- searxng_client.py   SearXNG news search and date parsing
   +-- trends_parser.py    Google Trends RSS
   +-- wiki_trends.py      Wikimedia pageviews API
   +-- migrations.py       SQLite schema versions
   +-- db_backup.py        Consistent SQLite backups
   +-- feed_security.py    SSRF-safe feed validation
   +-- rate_limit.py       Per-user command cooldowns
   +-- telegram_html.py    Telegram HTML escaping helpers
   |
trends.db + feeds.json + backups/
```

## Production Hardening

UTrends includes several safeguards that make the repository cleaner than a
throwaway bot script:

- `.env`, SQLite databases, backups, and virtual environments are ignored by Git.
- `ADMIN_CHAT_IDS` gates commands that mutate shared state or expose diagnostics.
- Feed additions validate every redirect and reject private, local, and reserved IP ranges.
- RSS requests use retry/backoff for transient DNS, connection, and HTTP errors.
- Expensive commands have per-user cooldowns.
- URLs are normalized before Radar deduplication.
- External titles, URLs, source names, and search queries are escaped before Telegram HTML rendering.
- SQLite schema changes are tracked in `schema_migrations`.
- `docker compose ps` exposes a `healthy` status.
- Logs are emitted as JSON for easier parsing.

## Quick Start

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Set at least:

```env
BOT_TOKEN=replace_with_your_telegram_bot_token
SEARXNG_BASE_URL=http://host.docker.internal:8888
ADMIN_CHAT_IDS=replace_with_your_telegram_chat_id
```

Start the bot:

```powershell
docker compose up -d --build
```

Check status and logs:

```powershell
docker compose ps
docker logs -f trends-bot
```

Stop:

```powershell
docker compose down
```

`trends.db`, `feeds.json`, and `backups/` are mounted as local volumes. Backups
are pruned according to `BACKUP_RETENTION_COUNT`.

## Configuration

All runtime tuning lives in `.env.example`:

- digest and Radar intervals;
- freshness windows;
- network timeouts;
- RSS retry/backoff settings;
- command cooldowns;
- backup directory, interval, and retention.

If local DNS resolution for `api.telegram.org` is unstable, copy
`docker-compose.override.example.yml` to `docker-compose.override.yml` and set
the current Telegram API IP. Keep the override local.

## Local Development

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

Run checks:

```powershell
python -m py_compile .\bot.py .\config.py .\db_backup.py .\feed_security.py .\healthcheck.py .\logging_utils.py .\migrations.py .\rate_limit.py .\rss_parser.py .\searxng_client.py .\telegram_html.py .\trends_parser.py .\wiki_trends.py .\url_utils.py
python -m unittest discover -s tests -v
```

## Current Limitations

- RSS text matching is still simple substring matching.
- Radar matching uses keyword overlap, not full morphology or semantic search.
- SearXNG/Bing can return incomplete or inaccurate publication dates.
- VK, OK, and X/Twitter are prioritized if discovered, but do not yet have dedicated adapters.
- Public deployment should rotate the Telegram token before the first push.

The remaining work is tracked in [ROADMAP.md](ROADMAP.md).

## GitHub Publishing Checklist

1. Rotate the Telegram token through BotFather before publishing.
2. Confirm `git status --ignored` shows `.env`, `*.db`, `backups/`, and `venv/` as ignored.
3. Run tests and Docker build.
4. Push only source, config examples, docs, and tests.

## License

[MIT](LICENSE)
