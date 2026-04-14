# CLAUDE.md — Project Context

## Project

Telegram To-Do Bot — portfolio project #01.
A personal task manager bot with daily reminders.

## Stack

- Python 3.11+
- python-telegram-bot 20.7 (async)
- APScheduler 3.10.4
- SQLite (built-in sqlite3)
- Docker + docker-compose

## Bot Language

English (all bot messages to users are in English)

## Key Rules

- All bot responses to users must be in **English**
- Use async/await everywhere (python-telegram-bot 20.x)
- Never hardcode secrets — use .env + python-dotenv
- SQLite DB path comes from DB_PATH env var (default: data/todo.db)
- All reminder times are in UTC
- Per-user data isolation: always filter by user_id

## Code Style

- Type hints where practical
- Docstrings on all public functions
- Descriptive variable names (no single-letter vars except loop counters)
- One responsibility per function

## Git

- Commit prefix convention: feat:, fix:, docs:, refactor:, chore:
- Never commit .env or data/ directory
