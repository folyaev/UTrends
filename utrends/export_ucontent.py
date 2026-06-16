import argparse
import datetime as dt
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import rss_parser
from .migrations import apply_migrations


DEFAULT_HOURS = 504
DEFAULT_UCONTENT_URL = "http://127.0.0.1:5197"
DEFAULT_DB_PATH = "trends.db"


def _today_id(now: dt.datetime) -> str:
    return now.strftime("utrends-%Y-%m-%d")


def _title(now: dt.datetime, hours: int) -> str:
    return f"UTrends {now:%Y-%m-%d} / {hours}h"


def _clean(value: object) -> str:
    return str(value or "").strip()


def build_markdown(digest: dict, *, title: str, hours: int) -> str:
    lines: list[str] = [
        f"# {title}",
        "",
        f"RSS-дайджест за последние {hours} часов.",
        "",
        "К новостям!",
        "",
    ]

    for category, topics in digest.items():
        for topic in topics:
            topic_title = _clean(topic.get("main_title")) or "Без названия"
            lines.extend([
                f"### {category} / {topic_title}",
                "",
            ])

            items = topic.get("items") or []
            for item in items[:6]:
                source = _clean(item.get("source_name")) or _clean(item.get("source")) or "Источник"
                item_title = _clean(item.get("title")) or topic_title
                link = _clean(item.get("link")) or _clean(item.get("url"))

                lines.extend([
                    f"{source}: {item_title}",
                    "",
                ])
                if link:
                    lines.extend([link, ""])

            if not items:
                lines.extend(["Empty topic. Add segment", ""])

    return "\n".join(lines).rstrip() + "\n"


def post_to_ucontent(base_url: str, payload: dict) -> dict:
    endpoint = base_url.rstrip("/") + "/api/import-markdown"
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"content-type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export UTrends RSS digest to UContent.")
    parser.add_argument("--hours", type=int, default=DEFAULT_HOURS, help=f"RSS window in hours. Default: {DEFAULT_HOURS}.")
    parser.add_argument("--id", default="", help="UContent scrape id. Default: utrends-YYYY-MM-DD.")
    parser.add_argument("--title", default="", help="UContent title. Default: UTrends YYYY-MM-DD / <hours>h.")
    parser.add_argument("--feeds", default="feeds.json", help="Path to feeds.json.")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=f"Path to trends.db. Default: {DEFAULT_DB_PATH}.")
    parser.add_argument("--ucontent-url", default=DEFAULT_UCONTENT_URL, help=f"UContent base URL. Default: {DEFAULT_UCONTENT_URL}.")
    parser.add_argument("--dry-run", action="store_true", help="Print markdown instead of posting to UContent.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.hours <= 0:
        print("--hours must be positive", file=sys.stderr)
        return 2

    now = dt.datetime.now()
    scrape_id = args.id.strip() or _today_id(now)
    title = args.title.strip() or _title(now, args.hours)

    apply_migrations(args.db)
    rss_parser.fetch_category_digest(args.feeds, time_window_hours=args.hours, archive_db_path=args.db)
    archived_items = rss_parser.load_archived_items(args.db, time_window_hours=args.hours)
    digest = rss_parser.build_category_digest_from_items(archived_items)
    content = build_markdown(digest, title=title, hours=args.hours)

    if args.dry_run:
        print(content)
        return 0

    payload = {
        "id": scrape_id,
        "title": title,
        "url": f"utrends://rss-digest?hours={args.hours}",
        "content": content,
    }
    try:
        response = post_to_ucontent(args.ucontent_url, payload)
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        print(f"UContent import failed: HTTP {exc.code}: {details}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"UContent is not reachable at {args.ucontent_url}: {exc}", file=sys.stderr)
        return 1

    scrape = response.get("scrape", {})
    print(f"Imported {scrape.get('id', scrape_id)}: {len(scrape.get('segments') or [])} segments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
