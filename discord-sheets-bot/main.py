import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime, timezone
from keep_alive import keep_alive

# Start keep_alive server
keep_alive()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Discord
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
client = discord.Client(intents=intents)

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.getenv("CREDS_JSON")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Discord Chat Log").sheet1

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    username = message.author.name  # Clean username
    content = message.content
    channel_name = f"💬 {message.channel.name}"

    print(f"[TEXT] {channel_name} | {username}: {content}")
   print("DEBUG VOICE LOG:", [timestamp, username, message, channel])  # just print for now
# sheet.append_row([timestamp, username, message, channel])  # <- disable actual logging


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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
