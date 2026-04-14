"""Bot entrypoint."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from config import BOT_TOKEN, GUILD_ID, LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("yt_dlp").setLevel(logging.WARNING)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
MY_GUILD = discord.Object(id=GUILD_ID)


@bot.event
async def on_ready() -> None:
    """Load extensions and sync commands when the bot is ready."""
    if getattr(bot, "_music_extension_loaded", False):
        return

    try:
        await bot.load_extension("bot.cogs.music")
    except Exception as error:
        print(f"Failed to load extension: {error}")
        raise

    bot.tree.copy_global_to(guild=MY_GUILD)

    try:
        synced = await bot.tree.sync(guild=MY_GUILD)
        setattr(bot, "_music_extension_loaded", True)
        print(f"Logged in as {bot.user} | Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as error:
        print(f"Failed to sync commands: {error}")
        raise


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set.")

if GUILD_ID <= 0:
    raise RuntimeError("GUILD_ID must be configured with a valid Discord guild ID.")

bot.run(BOT_TOKEN)
