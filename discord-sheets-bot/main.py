import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Keep-alive ping server
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

# Setup Google Sheets using CREDS_JSON
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
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    user = str(message.author)
    content = message.content
    channel = str(message.channel.name)
    print(f"[{channel}] {user}: {content}")
    sheet.append_row([timestamp, user, content, f"💬 {channel}"])

@client.event
async def on_voice_state_update(member, before, after):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    user = str(member)
    action = ""
    channel_name = ""

    if before.channel is None and after.channel is not None:
        action = f"joined voice channel: 🎙 {after.channel.name}"
        channel_name = after.channel.name
    elif before.channel is not None and after.channel is None:
        action = f"left voice channel: 🎙 {before.channel.name}"
        channel_name = before.channel.name
    elif before.channel != after.channel:
        action = f"switched from 🎙 {before.channel.name} to 🎙 {after.channel.name}"
        channel_name = f"{before.channel.name} → {after.channel.name}"
    else:
        return

    print(f"[VC] {user} {action}")
    sheet.append_row([timestamp, user, action, f"🎙 {channel_name} (VC Activity)"])

# Run the bot
client.run(DISCORD_TOKEN)