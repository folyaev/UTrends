# Roadmap

UTrends is usable as a personal bot today. This roadmap tracks the next steps
that would make it stronger for a wider public deployment.

## Before Public Deployment

- Rotate the Telegram bot token before the first public push.
- Add integration tests for Radar deduplication, scheduler jobs, callback
  ownership checks, and failed Telegram sends.
- Add a short demo GIF or screenshots of `/search`, Radar, `/feedhealth`, and `/backup`.

## Reliability

- Process RSS sources concurrently in digest and Radar jobs, with an overall
  timeout and per-source metrics.
- Track feed health over time and automatically suppress sources that repeatedly
  fail with 404/timeouts.

## Product Quality

- Improve Russian-language matching with morphology and normalized-title
  deduplication.
- Return partial `/search` results when one provider times out.
- Add per-user source preferences instead of a single global feed list.
- Add pagination for expensive commands that return long result sets.
- Add dedicated adapters or RSSHub feeds for VK, OK, and X/Twitter.

## Code Quality

- Split large Telegram handlers out of `bot.py` into feature modules.
- Add typed DTOs for feed items and search results.
- Add linting/formatting checks once the code layout stabilizes.
