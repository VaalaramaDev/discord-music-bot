"""Utility helpers for embeds and formatting."""

from __future__ import annotations

from datetime import datetime, timezone

import discord


def music_embed(
    title: str,
    description: str = "",
    color: discord.Color = discord.Color.blurple(),
    thumbnail: str | None = None,
) -> discord.Embed:
    """Create a consistent embed for music responses."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed


def format_duration(seconds: int) -> str:
    """Format seconds to MM:SS or HH:MM:SS."""
    if seconds < 3600:
        return f"{seconds // 60}:{seconds % 60:02d}"
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
