import os
import discord
from discord.ext import commands
from flask import Flask
import threading
import logging
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True  # Required for role checking

bot = commands.Bot(command_prefix="!", intents=intents)

# Flask app to keep Replit alive
app = Flask(__name__)


@app.route("/")
def home():
    return "FRAME Bot is running!"


def run_flask():
    app.run(host="0.0.0.0", port=8080)


@bot.event
async def on_ready():
    logging.info(f"✅ FRAME Bot is online as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only allow users with a specific role ID to use !post
    allowed_role_id = 1383361654724493343
    if not any(role.id == allowed_role_id for role in message.author.roles):
        await message.channel.send("❌ You don't have permission to use this.")
        return

    if message.content.startswith("!post"):
        try:
            parts = message.content.split(" ", 2)
            if len(parts) < 3:
                await message.channel.send("❌ Usage: `!post #channel message`")
                return

            raw_channel, msg_content = parts[1], parts[2]

            if raw_channel.startswith("<#") and raw_channel.endswith(">"):
                channel_id = int(raw_channel[2:-1])
            else:
                found = discord.utils.get(message.guild.channels,
                                          name=raw_channel.replace("#", ""))
                if not found:
                    await message.channel.send("❌ Invalid channel mention.")
                    return
                channel_id = found.id

            target_channel = bot.get_channel(channel_id)
            if not target_channel:
                await message.channel.send("❌ Could not find the channel.")
                return

            await target_channel.send(msg_content)
            await message.channel.send("✅ Message posted.")
        except Exception as e:
            logging.error(f"[ERROR] Exception while posting: {e}")
            await message.channel.send("❌ Something went wrong.")
    else:
        await bot.process_commands(message)


# Start Flask web server
threading.Thread(target=run_flask).start()

# Run the bot
bot.run(TOKEN)
