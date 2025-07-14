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

# Setup Discord client with required intents
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

# ======================== TEXT MESSAGE LOGGING ========================
@client.event
async def on_message(message):
    if message.author.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(message.author)
    content = message.content
    channel_name = f"💬 {message.channel.name}"
    server_name = str(message.guild.name) if message.guild else "DM"

    print(f"[TEXT] [{server_name}] [{channel_name}] {username}: {content}")
    sheet.append_row([timestamp, username, content, channel_name, server_name])

# ======================== VOICE STATE LOGGING ========================
@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(member)
    server_name = str(member.guild.name)
    action = ""
    channel_desc = ""

    if before.channel is None and after.channel is not None:
        action = "joined voice channel"
        channel_desc = f"🎙 {after.channel.name}"
    elif before.channel is not None and after.channel is None:
        action = "left voice channel"
        channel_desc = f"🎙 {before.channel.name}"
    elif before.channel != after.channel:
        action = "switched voice channel"
        channel_desc = f"🎙 {before.channel.name} → {after.channel.name}"
    else:
        return  # No meaningful change

    print(f"[VOICE] [{server_name}] {username} {action}: {channel_desc}")
    sheet.append_row([timestamp, username, action, channel_desc, server_name])

# ======================== RUN BOT ========================
client.run(DISCORD_TOKEN)