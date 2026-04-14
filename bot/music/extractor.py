"""yt-dlp extraction wrapper for YouTube and SoundCloud."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import yt_dlp
from config import YTDLP_COOKIES_FILE

logger = logging.getLogger(__name__)

YDL_OPTIONS: dict[str, Any] = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "scsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "cookiefile": "cookies.txt",
}

cookies_file = Path(YTDLP_COOKIES_FILE)
if cookies_file.is_file():
    YDL_OPTIONS["cookiefile"] = str(cookies_file)
else:
    logger.warning("yt-dlp cookies file not found: %s", cookies_file)

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def _normalize_query(query: str) -> str:
    """Normalize user input into a yt-dlp compatible query."""
    lowered_query = query.lower().strip()
    if lowered_query.startswith(("http://", "https://")):
        return query
    if lowered_query.startswith("scsearch:"):
        return query
    if "soundcloud.com" in lowered_query:
        return query
    if "youtube.com" in lowered_query or "youtu.be" in lowered_query:
        return query
    return f"scsearch:{query}"


def _extract_sync(query: str) -> dict[str, Any] | None:
    """Run yt-dlp extraction synchronously for use in a worker thread."""
    lookup = _normalize_query(query)
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as youtube_dl:
        info = youtube_dl.extract_info(lookup, download=False)

    if info is None:
        return None

    if "entries" in info:
        entries = [entry for entry in info["entries"] if entry]
        if not entries:
            return None
        info = entries[0]

    stream_url = info.get("url")
    if not stream_url:
        return None

    extractor_name = (info.get("extractor_key") or info.get("extractor") or "").lower()
    if "soundcloud" in extractor_name:
        source = "SoundCloud"
    else:
        source = "YouTube"

    return {
        "title": info.get("title", "Unknown title"),
        "url": stream_url,
        "duration": int(info.get("duration") or 0),
        "thumbnail": info.get("thumbnail"),
        "webpage_url": info.get("webpage_url") or info.get("original_url") or query,
        "source": source,
    }


async def extract_info(query: str) -> dict[str, Any] | None:
    """Extract playable audio metadata for a URL or search query."""
    try:
        return await asyncio.to_thread(_extract_sync, query)
    except yt_dlp.utils.DownloadError as exc:
        logger.warning("yt-dlp failed to extract query %r: %s", query, exc)
        return None
    except Exception:
        logger.exception("Unexpected extractor error for query %r", query)
        return None
