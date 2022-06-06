import discord
import os
import time

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX") or "."
STATUS = os.getenv("STATUS") or "online"

bot = commands.Bot(command_prefix=PREFIX, self_bot=True, status=discord.Status.offline, afk=True)
bot.startTime = time.time()
bot.status = getattr(discord.Status, STATUS)
bot.password = os.getenv("LINUX_PASSWORD") or ""

try:
    with open("lastCommitSHA", "r") as f:
        bot.lastCommitSHA = f.read()
except FileNotFoundError:
    bot.lastCommitSHA = "Unknown"

bot.deleted = {}
bot.edited = {}

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    await bot.change_presence(status=bot.status, afk=True)
    print()
    print(f"User: {bot.user}")
    print()

bot.run(TOKEN)
