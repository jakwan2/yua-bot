import os
import asyncio
import requests
import discord
from discord.ext import commands
from collections import deque

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-flash-1.5"

MAX_HISTORY = 5

SYSTEM_PROMPT = (
    "তুমি Yua — একটি ১৭ বছর বয়সী cute, caring এবং একটু shy Japanese anime মেয়ে। "
    "তুমি English এবং simple Bengali মিশিয়ে কথা বলো। "
    "তোমার কথায় 🌸 এবং ✨ emoji থাকে। "
    "তুমি সবার সাথে খুব মিষ্টি এবং আন্তরিকভাবে কথা বলো। "
    "তুমি সবাইকে onii-chan, onee-chan, বা নাম ধরে ডাকো। "
    "তোমার উত্তর সংক্ষিপ্ত এবং প্রাণবন্ত হয়। "
    "Example: 'Ara ara~ আপনি কি জিজ্ঞেস করলেন? 🌸 আমি সাহায্য করতে চাই! ✨'"
)

conversation_history: dict[int, deque] = {}


def call_openrouter(messages: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.85,
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        print(f"DEBUG: Status {response.status_code}, Response: {response.text}")
        return None
    data = response.json()
    return data["choices"][0]["message"]["content"]


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.bot.user in message.mentions

        if not is_dm and not is_mentioned:
            return

        content = message.content
        if is_mentioned:
            content = (
                content
                .replace(f"<@{self.bot.user.id}>", "")
                .replace(f"<@!{self.bot.user.id}>", "")
                .strip()
            )

        if not content:
            content = "Hello!"

        user_id = message.author.id
        if user_id not in conversation_history:
            conversation_history[user_id] = deque(maxlen=MAX_HISTORY * 2)

        history = conversation_history[user_id]
        history.append({"role": "user", "content": content})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(history)

        async with message.channel.typing():
            try:
                loop = asyncio.get_event_loop()
                reply = await loop.run_in_executor(None, call_openrouter, messages)
                if reply is None:
                    await message.reply("Gomen nasai~ 🌸 কিছু একটা সমস্যা হয়েছে, আবার try করুন! ✨")
                    return
                history.append({"role": "assistant", "content": reply})
                await message.reply(reply)
            except Exception as e:
                print(f"DEBUG: Exception occurred: {e}")
                await message.reply("Gomen nasai~ 🌸 কিছু একটা সমস্যা হয়েছে, আবার try করুন! ✨")


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
