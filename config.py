"""Application configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VOLUME = float(os.getenv("DEFAULT_VOLUME", "0.5"))
YTDLP_COOKIES_FILE = os.getenv("YTDLP_COOKIES_FILE", "cookies.txt")
