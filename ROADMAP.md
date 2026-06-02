# UTrends Roadmap

UTrends is a working MVP for personal use. This document lists the remaining
work before exposing the bot to untrusted users.

## Required Before Public Deployment

- Replace ad hoc SQLite schema changes with versioned migrations.
- Add integration tests for Radar deduplication, scheduler jobs, callback
  ownership checks, and failed Telegram sends.
- Rotate the Telegram bot token before the first public push.

## Reliability

- Process RSS sources concurrently in digest and Radar jobs, with an overall
  timeout and per-source metrics.
- Track failing feeds and expose an administrator health report.
- Add structured logging.
- Define a backup and retention policy for `trends.db`.

## Product Quality

- Improve Russian-language matching with morphology and normalized-title
  deduplication.
- Return partial `/search` results when one provider times out.
- Add per-user source preferences instead of a single global feed list.
- Add pagination for expensive commands that return long result sets.
- Add dedicated adapters or RSSHub feeds for VK, OK, and X/Twitter.
