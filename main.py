import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime, timezone, timedelta

# Render keep_alive support (only on Render)
if os.getenv("RENDER"):
    from keep_alive import keep_alive
    keep_alive()

# Load environment variables from Render
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CREDS_JSON = os.getenv("CREDS_JSON")

if not DISCORD_TOKEN or not CREDS_JSON:
    raise Exception("❌ Missing DISCORD_TOKEN or CREDS_JSON environment variable!")

# Convert JSON string to dict
try:
    creds_dict = json.loads(CREDS_JSON)
except json.JSONDecodeError:
    raise Exception("❌ CREDS_JSON is not a valid JSON string!")

# Setup Google Sheets API client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Pulse Ranker Logs").sheet1

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

# UTC to IST converter
def utc_to_ist(utc_dt):
    ist_offset = timedelta(hours=5, minutes=30)
    return (utc_dt + ist_offset).strftime("%Y-%m-%d %H:%M:%S")

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    timestamp = utc_to_ist(datetime.now(timezone.utc))
    username = message.author.name
    content = message.content
    channel_name = f"💬 {message.channel.name}"

    print(f"[TEXT] {channel_name} | {username}: {content}")
    try:
        sheet.append_row([timestamp, username, content, channel_name])
    except Exception as e:
        print(f"❌ Failed to log message to sheet: {e}")

@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    timestamp = utc_to_ist(datetime.now(timezone.utc))
    username = member.name
    message = ""
    channel = ""

    if before.channel is None and after.channel is not None:
        message = "joined voice channel"
        channel = f"🎙 {after.channel.name}"
    elif before.channel is not None and after.channel is None:
        message = "left voice channel"
        channel = f"🎙 {before.channel.name}"
    elif before.channel != after.channel:
        message = "switched voice channel"
        channel = f"🎙 {before.channel.name} → {after.channel.name}"
    else:
        return

    print(f"[VC] {username}: {message} in {channel}")
    try:
        sheet.append_row([timestamp, username, message, channel])
    except Exception as e:
        print(f"❌ Failed to log VC event to sheet: {e}")

# Run bot
client.run(DISCORD_TOKEN)