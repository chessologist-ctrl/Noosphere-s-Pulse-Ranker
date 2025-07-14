import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Start ping server
keep_alive()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Discord intents
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

# Prevent duplicate entries: store last activity per user temporarily
last_vc_event = {}

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    user = message.author.display_name
    content = message.content
    channel = f"💬 {message.channel.name}"
    print(f"[{channel}] {user}: {content}")
    sheet.append_row([timestamp, user, content, channel])

@client.event
async def on_voice_state_update(member, before, after):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = member.display_name
    user_id = member.id

    # Detect activity
    if before.channel is None and after.channel is not None:
        action = "joined"
        channel_name = after.channel.name
    elif before.channel is not None and after.channel is None:
        action = "left"
        channel_name = before.channel.name
    elif before.channel != after.channel:
        action = f"switched from {before.channel.name} to {after.channel.name}"
        channel_name = f"{before.channel.name} → {after.channel.name}"
    else:
        return

    # Avoid duplicate logging
    event_signature = f"{action}-{channel_name}"
    if last_vc_event.get(user_id) == event_signature:
        return  # Already logged this exact event
    last_vc_event[user_id] = event_signature

    print(f"[VC] {username} {action} {channel_name}")
    sheet.append_row([timestamp, username, action, f"🎙 {channel_name}", "VC Activity"])

# Run the bot
client.run(DISCORD_TOKEN)