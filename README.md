# Discord Music Bot

A Discord music bot built with `discord.py` that plays audio from YouTube and SoundCloud in voice channels using slash commands.

## Features

- Slash commands for playback, queue management, volume control, and disconnect
- Per-guild in-memory queues
- Audio extraction with `yt-dlp`
- Voice playback through FFmpeg
- Dockerized runtime with `docker-compose`

## Commands

- `/play query`
- `/pause`
- `/resume`
- `/skip`
- `/stop`
- `/queue`
- `/nowplaying`
- `/volume value`
- `/leave`

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Set `BOT_TOKEN` and `GUILD_ID`.
5. Ensure FFmpeg is installed locally.
6. Run `python main.py`.

## Docker

1. Create `.env` from `.env.example`.
2. Fill in `BOT_TOKEN` and `GUILD_ID`.
3. Run `docker compose up --build -d`.

## Notes

- The queue is stored in memory only.
- yt-dlp extracts stream URLs without downloading files to disk.
- Stream URLs can expire for very long queues.
