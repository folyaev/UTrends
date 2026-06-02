# Security Policy

## Reporting

Please report vulnerabilities privately to the repository owner instead of
opening a public issue.

## Secrets

Never commit `.env`, Telegram bot tokens, or SQLite databases. The database may
contain Telegram `chat_id` values and user preferences.

If a token was exposed in a commit, CI log, screenshot, or chat message, revoke
it through BotFather and issue a new one before redeploying.

## Deployment Scope

The current version is intended for personal use and controlled testing.
Review the required items in [ROADMAP.md](ROADMAP.md) before exposing the bot
to untrusted users.
