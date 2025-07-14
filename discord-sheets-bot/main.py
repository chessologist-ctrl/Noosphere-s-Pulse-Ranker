import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from datetime import datetime
from keep_alive import keep_alive
keep_alive()
# Load secret token
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# Setup Discord
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True  # This is needed to detect users in voice channels
client = discord.Client(intents=intents)

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os, json
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

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
    sheet.append_row([timestamp, user, content, channel])
@client.event
async def on_voice_state_update(member, before, after):
    from datetime import datetime

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    user = str(member)
    server = str(member.guild.name)

    if before.channel is None and after.channel is not None:
        # User joined a voice channel
        action = f"joined voice channel: {after.channel.name}"
    elif before.channel is not None and after.channel is None:
        # User left a voice channel
        action = f"left voice channel: {before.channel.name}"
    elif before.channel != after.channel:
        # User switched between voice channels
        action = f"switched from {before.channel.name} to {after.channel.name}"
    else:
        return  # No meaningful change

    print(f"[{server} > VC] {user} {action}")
    sheet.append_row([timestamp, server, user, action, "VC Activity"])
# Keep Replit alive
keep_alive()

# Run the bot
client.run(DISCORD_TOKEN)