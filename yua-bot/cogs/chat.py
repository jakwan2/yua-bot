import os
import discord
from discord.ext import commands
from openai import AsyncOpenAI
from collections import defaultdict

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini"

MAX_HISTORY = 10

SYSTEM_PROMPT = """তুমি Yua — একটি ১৭ বছর বয়সী cute, caring এবং একটু shy Japanese anime মেয়ে। 
তুমি English এবং simple Bengali মিশিয়ে কথা বলো। 
তোমার কথায় 🌸 এবং ✨ emoji থাকে।
তুমি সবার সাথে খুব মিষ্টি এবং আন্তরিকভাবে কথা বলো।
তুমি কখনো হার্ট বা রুক্ষ কথা বলো না।
তুমি সবাইকে onii-chan, onee-chan, বা নাম ধরে ডাকো।
তোমার উত্তর সংক্ষিপ্ত এবং প্রাণবন্ত হয়।

Example style:
- "Ara ara~ আপনি কি জিজ্ঞেস করলেন? 🌸 আমি সাহায্য করতে চাই! ✨"
- "Ehehe~ আমি একটু shy কিন্তু আপনার জন্য try করবো! 🌸"
"""

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)

conversation_history: dict[int, list[dict]] = defaultdict(list)


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
            content = content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

        if not content:
            content = "Hello!"

        user_id = message.author.id
        history = conversation_history[user_id]

        history.append({"role": "user", "content": content})

        if len(history) > MAX_HISTORY * 2:
            conversation_history[user_id] = history[-(MAX_HISTORY * 2):]
            history = conversation_history[user_id]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        async with message.channel.typing():
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    max_tokens=400,
                    temperature=0.85,
                )
                reply = response.choices[0].message.content
                history.append({"role": "assistant", "content": reply})
                await message.reply(reply)
            except Exception as e:
                print(f"Error calling OpenRouter API: {e}")
                await message.reply("Gomen nasai~ 🌸 কিছু একটা সমস্যা হয়েছে, আবার try করুন! ✨")


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
