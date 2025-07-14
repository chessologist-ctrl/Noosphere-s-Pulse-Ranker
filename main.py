import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Start keep_alive server
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

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(message.author)
    content = message.content
    channel = str(message.channel.name)

    print(f"[TEXT] {channel} | {username}: {content}")
    sheet.append_row([timestamp, username, content, channel])

@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(member)
    action = ""
    channel = ""

    if before.channel is None and after.channel is not None:
        action = f"joined voice channel"
        channel = after.channel.name
    elif before.channel is not None and after.channel is None:
        action = f"left voice channel"
        channel = before.channel.name
    elif before.channel != after.channel:
        action = f"switched from {before.channel.name} to {after.channel.name}"
        channel = f"{before.channel.name} → {after.channel.name}"
    else:
        return  # No meaningful change

    print(f"[VC] {username} {action} in {channel}")
    sheet.append_row([timestamp, username, action, channel])

# Run the bot
client.run(DISCORD_TOKEN)
