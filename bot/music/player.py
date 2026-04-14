"""Per-guild playback state and control."""

from __future__ import annotations

import asyncio
import logging

import discord

from bot.music.extractor import FFMPEG_OPTIONS
from bot.music.queue import Queue, Track
from config import VOLUME

LOGGER = logging.getLogger(__name__)
PLAYER_FFMPEG_OPTIONS = {
    **FFMPEG_OPTIONS,
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 "
        "-reconnect_delay_max 5 -timeout 30000000"
    ),
}


class GuildPlayer:
    """Per-guild music player state."""

    def __init__(self, bot: discord.Client, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.queue = Queue()
        self.volume = VOLUME
        self.voice_client: discord.VoiceClient | None = None
        self._play_next_lock = asyncio.Lock()

    async def connect(self, channel: discord.VoiceChannel) -> bool:
        """Connect to a voice channel or move there if already connected."""
        try:
            if self.voice_client is not None:
                try:
                    await self.voice_client.disconnect(force=True)
                except Exception:
                    pass
                self.voice_client = None
                await asyncio.sleep(1.0)

            self.voice_client = await channel.connect(
                reconnect=False,
                timeout=15.0,
                self_deaf=True,
            )
            return True
        except Exception as error:
            print(f"Voice connect error: {error}")
            self.voice_client = None
            return False

    async def play_next(self) -> Track | None:
        """Play the next queued track if available."""
        async with self._play_next_lock:
            if not self.voice_client or not self.voice_client.is_connected():
                return None

            next_track = self.queue.next()
            if not next_track:
                return None

            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(next_track.url, **PLAYER_FFMPEG_OPTIONS),
                volume=self.volume,
            )

            def after_playback(error: Exception | None) -> None:
                if error:
                    LOGGER.warning("Playback error in guild %s: %s", self.guild_id, error)
                asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)

            self.voice_client.play(source, after=after_playback)
            return next_track

    async def add_and_play(self, track: Track) -> tuple[bool, int]:
        """Queue a track and start playback immediately if idle."""
        position = self.queue.add(track)
        should_start = not self.is_playing and not self.is_paused and self.queue.current is None
        if should_start:
            await self.play_next()
            return True, 0
        return False, position

    def pause(self) -> bool:
        """Pause current playback."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            return True
        return False

    def resume(self) -> bool:
        """Resume paused playback."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            return True
        return False

    def skip(self) -> bool:
        """Skip the current track."""
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
            self.voice_client.stop()
            return True
        return False

    def stop(self) -> int:
        """Stop playback and clear the queue, returning removed track count."""
        removed_tracks = len(self.queue) + (1 if self.queue.current else 0)
        self.queue.clear()
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
            self.voice_client.stop()
        return removed_tracks

    def set_volume(self, volume: float) -> None:
        """Set playback volume and apply it to the active source."""
        self.volume = volume
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = volume

    async def leave(self) -> None:
        """Disconnect from the voice channel and reset state."""
        self.queue.clear()
        if self.voice_client:
            await self.voice_client.disconnect(force=False)
            self.voice_client = None

    @property
    def is_playing(self) -> bool:
        """Return whether audio is currently playing."""
        return self.voice_client is not None and self.voice_client.is_playing()

    @property
    def is_paused(self) -> bool:
        """Return whether audio is currently paused."""
        return self.voice_client is not None and self.voice_client.is_paused()
