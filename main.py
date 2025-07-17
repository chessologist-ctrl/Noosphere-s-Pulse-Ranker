import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone, timedelta
from keep_alive import keep_alive

# Start keep_alive server (UptimeRobot)
keep_alive()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CREDS_JSON = os.getenv("CREDS_JSON")

# Check for missing credentials
if not DISCORD_TOKEN or not CREDS_JSON:
    raise Exception("❌ Missing DISCORD_TOKEN or CREDS_JSON environment variable!")

# Convert CREDS_JSON string to dictionary
creds_dict = json.loads(CREDS_JSON)

# Setup Google Sheets API client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Pulse Ranker Logs").sheet1

# Setup Discord client with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
client = discord.Client(intents=intents)

# Helper to convert UTC to IST
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
    sheet.append_row([timestamp, username, content, channel_name])

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
    sheet.append_row([timestamp, username, message, channel])

# Run the bot
client.run(DISCORD_TOKEN)