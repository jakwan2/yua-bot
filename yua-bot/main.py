import os
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Yua is online! ✨")

async def main():
    async with bot:
        await bot.load_extension("cogs.chat")
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is not set.")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
