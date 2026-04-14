# 🎵 Discord Music Bot

A Discord music bot that plays audio from SoundCloud in voice channels, with queue management and slash commands. Built as a portfolio project demonstrating discord.py, yt-dlp integration, FFmpeg audio streaming, and Docker deployment.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- Play audio from SoundCloud by search query
- Per-guild queue with position tracking
- Rich Discord Embeds with track info and thumbnails
- Slash command interface
- FFmpeg audio streaming — no files stored on disk
- Stream URLs resolved on-the-fly via yt-dlp

---

## Commands

| Command         | Description                                 |
| --------------- | ------------------------------------------- |
| `/play <query>` | Search SoundCloud and play, or add to queue |
| `/pause`        | Pause playback                              |
| `/resume`       | Resume playback                             |
| `/skip`         | Skip current track                          |
| `/stop`         | Stop and clear queue                        |
| `/queue`        | Show current queue                          |
| `/nowplaying`   | Show currently playing track                |
| `/leave`        | Disconnect from voice channel               |

**Examples:**

```
/play bohemian rhapsody
/play never gonna give you up
/play hotel california
```

---

## Tech Stack

| Layer            | Technology                             |
| ---------------- | -------------------------------------- |
| Language         | Python 3.11+                           |
| Bot framework    | discord.py 2.7.1                       |
| Audio extraction | yt-dlp (SoundCloud)                    |
| Audio encoding   | FFmpeg + Deno (JS runtime)             |
| Voice encryption | PyNaCl + davey (Discord DAVE protocol) |
| Config           | python-dotenv                          |
| Deployment       | Docker + Docker Compose                |

---

## Audio Source

This bot uses **SoundCloud** as its primary audio source via yt-dlp. YouTube was evaluated but consistently blocked VPS IP addresses with anti-bot checks — a known limitation affecting all self-hosted music bots. SoundCloud provides reliable playback without authentication requirements.

---

## Project Structure

```
discord-music-bot/
├── bot/
│   ├── cogs/
│   │   └── music.py         # all slash commands
│   ├── music/
│   │   ├── player.py        # GuildPlayer — per-guild state
│   │   ├── queue.py         # Queue + Track dataclass
│   │   └── extractor.py     # yt-dlp wrapper (SoundCloud)
│   └── utils.py             # embed helpers
├── main.py                  # entry point
├── config.py                # env vars
├── requirements.txt
├── .env.example
├── Dockerfile               # includes FFmpeg + Deno
└── docker-compose.yml
```

---

## Quick Start

### 1. Create Discord Application

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → name it
3. **Bot** → **Add Bot** → copy token
4. Enable all three **Privileged Gateway Intents**:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
5. **OAuth2** → **URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Permissions: Connect, Speak, Send Messages, View Channels, Use Slash Commands
6. Open generated URL → add bot to your server

### 2. Get your Guild ID

1. Discord Settings → Advanced → enable **Developer Mode**
2. Right-click your server → **Copy Server ID**

### 3. Configure

```bash
git clone https://github.com/VaalaramaDev/discord-music-bot.git
cd discord-music-bot
cp .env.example .env
nano .env
```

```env
BOT_TOKEN=your_token_here
GUILD_ID=your_guild_id_here
LOG_LEVEL=INFO
DEFAULT_VOLUME=0.5
```

### 4. Run with Docker (recommended)

```bash
docker compose up -d --build
docker compose logs -f
```

Expected output:

```
Logged in as VaalaramaMusic#5878 | Synced 9 commands to guild YOUR_GUILD_ID
```

---

## Deployment on VPS

Tested on Ubuntu 24.04, Hetzner CX43. Docker image includes FFmpeg and Deno.

### Step 1 — Connect and clone

```bash
ssh root@YOUR_SERVER_IP
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/VaalaramaDev/discord-music-bot.git
cd discord-music-bot
```

### Step 2 — Configure

```bash
cp .env.example .env
nano .env
# Add BOT_TOKEN and GUILD_ID
```

### Step 3 — Start

```bash
docker compose up -d --build
docker compose logs -f
```

### Step 4 — Test

1. Join a voice channel in your Discord server
2. Type `/play bohemian rhapsody`
3. Bot joins and starts playing from SoundCloud

### Updating

```bash
git pull
docker compose up -d --build
```

---

### Useful commands

```bash
# Live logs
docker compose logs -f

# Restart
docker compose restart

# Shell inside container
docker compose exec bot bash

# Check FFmpeg
docker compose exec bot ffmpeg -version

# Check Deno
docker compose exec bot deno --version
```

---

## Environment Variables

| Variable         | Default  | Description                         |
| ---------------- | -------- | ----------------------------------- |
| `BOT_TOKEN`      | required | Token from Discord Developer Portal |
| `GUILD_ID`       | required | Your Discord server ID              |
| `LOG_LEVEL`      | `INFO`   | Logging level                       |
| `DEFAULT_VOLUME` | `0.5`    | Default volume (0.0–1.0)            |

---

## How It Works

1. User runs `/play <query>`
2. yt-dlp searches SoundCloud and resolves a direct audio stream URL
3. FFmpeg streams audio to Discord voice channel
4. Queue stores Track objects in memory — clears on bot restart
5. Each guild has its own independent `GuildPlayer` instance

---

## Known Limitations

- YouTube search is disabled — VPS IPs are consistently blocked by YouTube anti-bot checks (affects all self-hosted music bots)
- Direct SoundCloud URLs may return 404 if the artist profile path differs — use search queries instead
- Stream URLs expire after ~6 hours — long queues may fail on older tracks
- Queue resets on bot restart (in-memory only, by design)

---

## Security Notes

- Bot token never logged
- `.env` is gitignored
- No audio files stored — pure streaming, no disk usage

---

## License

MIT — free to use, modify, and distribute.
