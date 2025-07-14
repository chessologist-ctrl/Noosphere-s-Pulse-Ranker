import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Keep bot alive on render
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

# Helper function to log rows to Google Sheet
def log_to_sheet(timestamp, username, message, channel):
    sheet.append_row([timestamp, username, message, channel])

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(message.author.display_name)
    content = message.content
    channel_name = f"💬 {message.channel.name}"
    print(f"[Text] {username}: {content} in {channel_name}")
    log_to_sheet(timestamp, username, content, channel_name)

@client.event
async def on_voice_state_update(member, before, after):
    # Avoid duplicate logs by checking only meaningful changes
    if before.channel == after.channel:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(member.display_name)

    # User joined VC
    if before.channel is None and after.channel is not None:
        action = "joined voice channel"
        vc_channel = f"🎙 {after.channel.name}"

    # User left VC
    elif before.channel is not None and after.channel is None:
        action = "left voice channel"
        vc_channel = f"🎙 {before.channel.name}"

    # User switched VC
    elif before.channel != after.channel:
        action = f"switched from 🎙 {before.channel.name} to 🎙 {after.channel.name}"
        vc_channel = f"{before.channel.name} → {after.channel.name}"

    else:
        return  # No change to log

    print(f"[Voice] {username} {action}")
    log_to_sheet(timestamp, username, action, vc_channel)

# Run the bot
client.run(DISCORD_TOKEN)