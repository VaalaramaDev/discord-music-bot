"""Music slash commands."""

from __future__ import annotations

from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

from bot.music.extractor import extract_info
from bot.music.player import GuildPlayer
from bot.music.queue import Track
from bot.utils import format_duration, music_embed


class MusicCog(commands.Cog):
    """Slash commands for per-guild music playback."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._players: dict[int, GuildPlayer] = {}

    def _get_player(self, guild_id: int) -> GuildPlayer:
        """Get or create the guild player."""
        if guild_id not in self._players:
            self._players[guild_id] = GuildPlayer(self.bot, guild_id)
        return self._players[guild_id]

    @staticmethod
    def _get_voice_channel(interaction: discord.Interaction) -> discord.VoiceChannel | None:
        """Return the requester's voice channel if present."""
        user = interaction.user
        if not isinstance(user, discord.Member) or not user.voice or not user.voice.channel:
            return None
        if not isinstance(user.voice.channel, discord.VoiceChannel):
            return None
        return user.voice.channel

    async def _respond_error(self, interaction: discord.Interaction, message: str) -> None:
        """Send an ephemeral error message."""
        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name="play", description="Play a track or add it to the queue.")
    @app_commands.describe(query="YouTube/SoundCloud URL or search query")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        """Play a song or add it to the queue."""
        voice_channel = self._get_voice_channel(interaction)
        if voice_channel is None:
            await self._respond_error(
                interaction,
                "You need to be in a voice channel to use this command.",
            )
            return

        await interaction.response.defer(thinking=True)

        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        connected = await player.connect(voice_channel)
        if not connected:
            error_embed = music_embed(
                title="Error",
                description="Could not connect to voice channel. Please try again.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        track_info = await extract_info(query)
        if not track_info:
            await interaction.followup.send(
                "Could not find or play that track. Try a different search or URL.",
                ephemeral=True,
            )
            return

        was_already_active = player.is_playing or player.is_paused or player.queue.current is not None
        track = Track(
            title=track_info["title"],
            url=track_info["url"],
            webpage_url=track_info["webpage_url"],
            duration=track_info["duration"],
            thumbnail=track_info["thumbnail"],
            requested_by=interaction.user.display_name,
            source=track_info["source"],
        )
        started_now, position = await player.add_and_play(track)
        active_track = cast(Track | None, player.queue.current)

        if started_now and active_track is not None:
            embed = music_embed(
                title="🎵 Now Playing",
                color=discord.Color.green(),
                thumbnail=active_track.thumbnail,
            )
            embed.add_field(name="Title", value=active_track.title, inline=False)
            embed.add_field(
                name="Duration",
                value=format_duration(active_track.duration),
                inline=True,
            )
            embed.add_field(name="Source", value=active_track.source, inline=True)
            embed.add_field(name="Requested", value=active_track.requested_by, inline=True)
            await interaction.followup.send(embed=embed)
            return

        queue_position = position if was_already_active else len(player.queue)
        embed = music_embed(
            title=f"📥 Added to Queue • position {queue_position}",
            color=discord.Color.blurple(),
            thumbnail=track.thumbnail,
        )
        embed.add_field(name="Title", value=track.title, inline=False)
        embed.add_field(name="Duration", value=format_duration(track.duration), inline=True)
        embed.add_field(name="Source", value=track.source, inline=True)
        embed.add_field(name="Requested", value=track.requested_by, inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="Pause playback.")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Pause the currently playing track."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        current = player.queue.current
        if not current or not player.pause():
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        embed = music_embed(title="⏸ Paused", description=f'"{current.title}"', color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resume", description="Resume playback.")
    async def resume(self, interaction: discord.Interaction) -> None:
        """Resume the paused track."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        current = player.queue.current
        if not current or not player.resume():
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        embed = music_embed(title="▶ Resumed", description=f'"{current.title}"', color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="Skip the current track.")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Skip the active track."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        current = player.queue.current
        if current is None:
            await self._respond_error(interaction, "Queue is empty.")
            return
        if not player.skip():
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        embed = music_embed(title="⏭ Skipped", description=f'"{current.title}"', color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop", description="Stop playback and clear the queue.")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Stop playback and clear queued tracks."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        removed_tracks = player.stop()
        if removed_tracks == 0:
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        embed = music_embed(
            title="⏹ Stopped",
            description=f"Queue cleared. {removed_tracks} tracks removed.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Show the current queue.")
    async def queue(self, interaction: discord.Interaction) -> None:
        """Display the current track and queued tracks."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        queued_tracks = player.queue.list()
        current = player.queue.current

        if current is None and not queued_tracks:
            await self._respond_error(interaction, "Queue is empty. Use /play to add tracks.")
            return

        lines: list[str] = []
        total_duration = 0

        if current is not None:
            total_duration += current.duration
            lines.append(
                f"**Now:** {current.title} ({format_duration(current.duration)}) — {current.requested_by}"
            )

        for index, track in enumerate(queued_tracks, start=1):
            total_duration += track.duration
            lines.append(
                f"{index}. {track.title} ({format_duration(track.duration)}) — {track.requested_by}"
            )

        total_tracks = len(queued_tracks) + (1 if current else 0)
        embed = music_embed(
            title=f"🎶 Queue • {total_tracks} tracks",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Total duration", value=format_duration(total_duration), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Show the currently playing track.")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        """Display the active track."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        current = player.queue.current
        if current is None:
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        embed = music_embed(
            title="🎵 Now Playing",
            color=discord.Color.green(),
            thumbnail=current.thumbnail,
        )
        embed.add_field(name="Title", value=current.title, inline=False)
        embed.add_field(name="Duration", value=format_duration(current.duration), inline=True)
        embed.add_field(name="Source", value=current.source, inline=True)
        embed.add_field(name="Requested by", value=current.requested_by, inline=True)
        embed.add_field(name="Link", value=current.webpage_url, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Set playback volume.")
    @app_commands.describe(value="Volume between 1 and 100")
    async def volume(self, interaction: discord.Interaction, value: int) -> None:
        """Adjust player volume."""
        if not 1 <= value <= 100:
            await self._respond_error(interaction, "Volume must be between 1 and 100.")
            return

        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        player.set_volume(value / 100)

        embed = music_embed(
            title="🔊 Volume",
            description=f"Volume set to {value}%",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Disconnect from the voice channel.")
    async def leave(self, interaction: discord.Interaction) -> None:
        """Disconnect the bot from voice chat."""
        assert interaction.guild is not None
        player = self._get_player(interaction.guild.id)
        channel_name = player.voice_client.channel.name if player.voice_client and player.voice_client.channel else "voice channel"
        if player.voice_client is None:
            await self._respond_error(interaction, "Nothing is currently playing.")
            return

        await player.leave()
        embed = music_embed(
            title="👋 Disconnected",
            description=f"Disconnected from {channel_name}",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Register the music cog."""
    await bot.add_cog(MusicCog(bot))
