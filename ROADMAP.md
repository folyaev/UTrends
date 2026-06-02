# UTrends Roadmap

UTrends is a working MVP for personal use. This document lists the remaining
work before exposing the bot to untrusted users.

## Required Before Public Deployment

- Restrict `/addfeed` to administrators. It currently changes the shared
  `feeds.json` file for every user and accepts arbitrary HTTP URLs.
- Add SSRF protection for feed URLs: allow only `http` and `https`, reject
  loopback and private network addresses, and re-check redirects.
- Escape all external and user-controlled text before rendering Telegram HTML.
  Feed titles, search queries, source names, and URLs currently reach formatted
  messages without a single sanitization layer.
- Replace ad hoc SQLite schema changes with versioned migrations.
- Add integration tests for Radar deduplication, scheduler jobs, callback
  ownership checks, and failed Telegram sends.
- Rotate the Telegram bot token before the first public push.

## Reliability

- Process RSS sources concurrently in digest and Radar jobs, with an overall
  timeout and per-source metrics.
- Track failing feeds and expose an administrator health report.
- Add structured logging and a container health check.
- Move runtime configuration such as intervals, limits, and timeouts to
  environment variables.
- Define a backup and retention policy for `trends.db`.

## Product Quality

- Improve Russian-language matching with morphology and normalized-title
  deduplication.
- Return partial `/search` results when one provider times out.
- Add per-user source preferences instead of a single global feed list.
- Add pagination and rate limits for expensive commands.
- Add dedicated adapters or RSSHub feeds for VK, OK, and X/Twitter.
