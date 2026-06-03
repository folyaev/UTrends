# UTrends Bot

![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-MVP-orange)

UTrends — Telegram-бот для отслеживания новостных трендов, RSS-лент, Google
Trends, популярных статей Википедии и пользовательских тем. Идея простая:
подписаться на тему, получать уведомления о свежих совпадениях и держать под
рукой дайджест того, что сейчас движется в источниках.

Проект уже упакован для Docker, содержит CI-проверки, миграции SQLite, бэкапы,
админские команды обслуживания, SSRF-защиту при добавлении RSS, экранирование
Telegram HTML, rate limit, структурированные JSON-логи и unit-тесты.

## Возможности

- Плановый RSS-дайджест по категориям источников.
- Радар отслеживаемых тем с дедупликацией URL и приоритетом источников.
- Ручной `/search` по RSS и SearXNG News с частичными результатами при timeout.
- Получение Google Trends через `/force`.
- Топ читаемых статей русской Википедии через `/wiki`.
- Пользовательские настройки категорий RSS-источников через `/sources`.
- Админское добавление RSS-лент через `/addfeed`.
- Админская диагностика RSS-источников через `/feedhealth`.
- Админские резервные копии SQLite через `/backup`.
- Docker healthcheck и JSON-логи для эксплуатации.

## Команды

| Команда | Описание |
| --- | --- |
| `/start` | Подписаться на плановый дайджест. |
| `/stop` | Отписаться от планового дайджеста. |
| `/digest` | Собрать дайджест вручную. |
| `/search запрос` | Искать по RSS и SearXNG News. |
| `/force` | Получить текущие Google Trends. |
| `/wiki` | Показать топ статей русской Википедии. |
| `/subs` | Показать отслеживаемые темы. |
| `/ignored` | Показать скрытые темы. |
| `/sources` | Включить или отключить категории RSS-источников. |
| `/addfeed URL` | Добавить RSS-ленту. Только для админов. |
| `/feedhealth` | Проверить доступность RSS-источников. Только для админов. |
| `/backup` | Создать резервную копию SQLite. Только для админов. |

## Архитектура

```text
Пользователь Telegram
   |
aiogram bot.py
   |
   +-- rss_parser.py       RSS, кластеризация дайджеста, healthcheck источников
   +-- searxng_client.py   Поиск SearXNG News и парсинг дат
   +-- trends_parser.py    Google Trends RSS
   +-- wiki_trends.py      Wikimedia Pageviews API
   +-- migrations.py       Версии схемы SQLite
   +-- db_backup.py        Консистентные бэкапы SQLite
   +-- feed_security.py    SSRF-safe проверка добавляемых RSS
   +-- rate_limit.py       Cooldown тяжёлых команд
   +-- social_feeds.py     Опциональные RSSHub-адаптеры VK/OK/X
   +-- telegram_html.py    Экранирование Telegram HTML
   +-- text_match.py       Нормализация, matching и дедупликация заголовков
   |
trends.db + feeds.json + backups/
```

## Что уже сделано для production-подхода

UTrends не выглядит как одноразовый скрипт: в проекте уже есть базовая
инженерная защита и эксплуатационные механики.

- `.env`, SQLite-базы, бэкапы и виртуальные окружения исключены из Git.
- `ADMIN_CHAT_IDS` закрывает команды, которые меняют общие данные или показывают диагностику.
- Добавление RSS проверяет каждый редирект и запрещает private/local/reserved IP.
- RSS-запросы используют retry/backoff для временных DNS, connection и HTTP-сбоев.
- Тяжёлые команды имеют cooldown на пользователя.
- URL и заголовки нормализуются перед дедупликацией.
- RSS-поиск и радар используют нормализованные токены, а не только точную строку.
- Внешние заголовки, URL, источники и поисковые запросы экранируются перед Telegram HTML.
- Изменения схемы SQLite фиксируются в `schema_migrations`.
- `docker compose ps` показывает статус `healthy`.
- Логи выводятся в JSON-формате.

## Быстрый запуск

Создайте локальный `.env`:

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

`trends.db`, `feeds.json` и `backups/` монтируются как локальные volume.
Старые бэкапы удаляются по настройке `BACKUP_RETENTION_COUNT`.

## Конфигурация

Все runtime-настройки перечислены в `.env.example`:

- интервалы дайджеста и радара;
- окна свежести;
- сетевые timeout-ы;
- retry/backoff для RSS;
- cooldown команд;
- директория, интервал и retention бэкапов.
- опциональные RSSHub-маршруты для VK, OK и X/Twitter.

Если локальный DNS нестабилен для `api.telegram.org`, скопируйте
`docker-compose.override.example.yml` в `docker-compose.override.yml` и укажите
актуальный IP Telegram API. Override должен оставаться локальным.

## Локальная разработка

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

Проверки:

```powershell
python -m py_compile .\bot.py .\config.py .\db_backup.py .\feed_security.py .\healthcheck.py .\logging_utils.py .\migrations.py .\rate_limit.py .\rss_parser.py .\searxng_client.py .\social_feeds.py .\telegram_html.py .\text_match.py .\trends_parser.py .\wiki_trends.py .\url_utils.py
python -m unittest discover -s tests -v
```

## Ограничения

- Matching использует простую нормализацию слов, но пока не полноценную морфологию или semantic search.
- SearXNG/Bing может возвращать неполные или неточные даты публикации.
- VK, OK и X/Twitter подключаются через опциональные RSSHub-маршруты, если задан `RSSHUB_BASE_URL`.
- Перед публичной публикацией нужно перевыпустить Telegram-токен.

Оставшиеся задачи находятся в [ROADMAP.md](ROADMAP.md).

## Лицензия

[MIT](LICENSE)
