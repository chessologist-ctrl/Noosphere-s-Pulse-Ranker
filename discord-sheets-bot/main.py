import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os, json
from datetime import datetime
from keep_alive import keep_alive

# Keep-alive server
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
    username = str(message.author.display_name)
    content = message.content
    channel_name = f"💬 {message.channel.name}"
    print(f"[{channel_name}] {username}: {content}")
    sheet.append_row([timestamp, username, content, channel_name])

@client.event
async def on_voice_state_update(member, before, after):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    username = str(member.display_name)

    if before.channel is None and after.channel is not None:
        # Joined VC
        action = "joined voice channel"
        vc_name = after.channel.name
    elif before.channel is not None and after.channel is None:
        # Left VC
        action = "left voice channel"
        vc_name = before.channel.name
    elif before.channel != after.channel:
        # Switched VC
        action = f"switched VC: {before.channel.name} → {after.channel.name}"
        vc_name = f"{before.channel.name} → {after.channel.name}"
    else:
        return

    print(f"[VC] {username} {action}")
    sheet.append_row([timestamp, username, action, f"🎙 {vc_name}"])

# Run the bot
client.run(DISCORD_TOKEN)