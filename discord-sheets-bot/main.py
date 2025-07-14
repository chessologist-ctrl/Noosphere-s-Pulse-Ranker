import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Keep Replit/Render alive
keep_alive()

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Discord client
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

# ========== Text Message Logging ==========
@client.event
async def on_message(message):
    if message.author.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(message.author)
    content = message.content
    channel_name = f"💬 {message.channel.name}"

    print(f"[TEXT] {username} in {channel_name}: {content}")
    sheet.append_row([timestamp, username, content, channel_name])

# ========== Voice Channel Logging ==========
@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(member)

    if before.channel is None and after.channel is not None:
        action = "joined voice channel"
        channel_name = f"🎙 {after.channel.name}"
    elif before.channel is not None and after.channel is None:
        action = "left voice channel"
        channel_name = f"🎙 {before.channel.name}"
    elif before.channel != after.channel:
        action = "switched voice channel"
        channel_name = f"🎙 {before.channel.name} → {after.channel.name}"
    else:
        return

    print(f"[VOICE] {username} {action} | {channel_name}")
    sheet.append_row([timestamp, username, action, channel_name])

# Run the bot
client.run(DISCORD_TOKEN)