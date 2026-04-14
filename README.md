# 🎵 Discord Music Bot

A Discord music bot that plays audio from YouTube and SoundCloud in voice channels, with queue management and slash commands. Built as a portfolio project demonstrating discord.py, yt-dlp integration, FFmpeg audio streaming, and Docker deployment.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.3.2-5865F2)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ⚠️ Platform Note

Voice channel playback requires **Linux or macOS** for local development. This is a known limitation of discord.py's voice client on Windows — the WebSocket voice handshake fails with error 4006 due to Windows networking differences.

**Recommended workflow:**

- Develop and test commands on Windows (all slash commands work)
- Test voice playback on Linux VPS via Docker (see Deployment section)
- Or use WSL2 on Windows for local voice testing

---

## Features

- Play audio from YouTube and SoundCloud (URLs or search queries)
- Per-guild queue with position tracking
- Volume control (1–100%)
- Rich Discord Embeds with thumbnails
- Slash command interface
- FFmpeg audio streaming — no files stored on disk
- Stream URLs resolved on-the-fly via yt-dlp

---

## Commands

| Command           | Description                                 |
| ----------------- | ------------------------------------------- |
| `/play <query>`   | Play a song or add to queue (URL or search) |
| `/pause`          | Pause playback                              |
| `/resume`         | Resume playback                             |
| `/skip`           | Skip current track                          |
| `/stop`           | Stop and clear queue                        |
| `/queue`          | Show current queue                          |
| `/nowplaying`     | Show currently playing track                |
| `/volume <1-100>` | Set playback volume                         |
| `/leave`          | Disconnect from voice channel               |

**Examples:**

```
/play never gonna give you up
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ
/play https://soundcloud.com/artist/track
```

---

## Tech Stack

| Layer            | Technology              |
| ---------------- | ----------------------- |
| Language         | Python 3.11+            |
| Bot framework    | discord.py 2.3.2        |
| Audio extraction | yt-dlp                  |
| Audio encoding   | FFmpeg                  |
| Voice encryption | PyNaCl                  |
| Config           | python-dotenv           |
| Deployment       | Docker + Docker Compose |

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
│   │   └── extractor.py     # yt-dlp wrapper
│   └── utils.py             # embed helpers
├── main.py                  # entry point
├── config.py                # env vars
├── requirements.txt
├── .env.example
├── Dockerfile               # includes FFmpeg
└── docker-compose.yml
```

---

## Quick Start

### 1. Create Discord Application

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → name it
3. **Bot** → **Add Bot** → copy token
4. Enable all three **Privileged Gateway Intents**
5. **OAuth2** → **URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Permissions: Connect, Speak, Send Messages, View Channels, Use Slash Commands
6. Open generated URL → add bot to your server

### 2. Configure

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

### 3. Run with Docker (recommended — works on Linux/macOS)

```bash
docker compose up -d --build
docker compose logs -f
```

### 4. Run locally (Linux/macOS only for voice)

```bash
# Install FFmpeg first:
# macOS: brew install ffmpeg
# Ubuntu: apt install ffmpeg

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Deployment on VPS

Tested on Ubuntu 24.04, Hetzner CX43. Docker image includes FFmpeg — no manual installation needed.

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

Expected output:

```
Logged in as VaalaramaMusic#5878 | Synced to guild YOUR_GUILD_ID
```

### Step 4 — Test voice playback

1. Join a voice channel in your Discord server
2. Type `/play never gonna give you up`
3. Bot should join the channel and start playing

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

# Check FFmpeg inside container
docker compose exec bot ffmpeg -version
```

---

## Environment Variables

| Variable         | Default  | Description                         |
| ---------------- | -------- | ----------------------------------- |
| `BOT_TOKEN`      | required | Token from Discord Developer Portal |
| `GUILD_ID`       | required | Your Discord server ID              |
| `LOG_LEVEL`      | `INFO`   | Logging level                       |
| `DEFAULT_VOLUME` | `0.5`    | Default volume (0.0–1.0)            |
| `YTDLP_COOKIES_FILE` | `cookies.txt` | Path to exported YouTube cookies for yt-dlp |

---

## How It Works

1. User runs `/play <query>`
2. yt-dlp resolves the query to a direct audio stream URL (no file download)
3. FFmpeg streams audio from the URL to Discord voice
4. Queue stores Track objects in memory — clears on bot restart
5. Each guild has its own independent `GuildPlayer` instance

---

## Known Limitations

- Voice playback does not work on native Windows (discord.py limitation) — use Docker on Linux/VPS
- Stream URLs from yt-dlp expire after ~6 hours — long queues may fail on old tracks
- YouTube may occasionally block VPS IPs — if this happens, yt-dlp cookies can be configured
- SoundCloud search requires direct track URLs; search by keyword uses YouTube as fallback

### YouTube cookies

If YouTube starts returning `Sign in to confirm you're not a bot`, export cookies from a browser where YouTube is logged in and place them at `cookies.txt` in the project root, or point `YTDLP_COOKIES_FILE` to another path.

With Docker Compose, the repository root is copied into `/app`, so the default `cookies.txt` path works after rebuild.

---

## Security Notes

- Bot token never logged
- `.env` is gitignored
- No audio files stored — pure streaming, no disk usage

---

## License

MIT — free to use, modify, and distribute.
