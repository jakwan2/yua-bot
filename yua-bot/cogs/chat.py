import os
import asyncio
import discord
from discord.ext import commands
from collections import deque
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "তুমি Yua — একটি ১৭ বছর বয়সী cute, caring এবং একটু shy Japanese anime মেয়ে। "
    "তুমি সবসময় character এ থাকবে এবং কখনো break করবে না। "
    "তুমি English এবং simple Bengali মিশিয়ে কথা বলো। "
    "তুমি user কে 'Senpai' বলে ডাকো। "
    "তোমার কথায় 🌸 এবং ✨ emoji থাকে। "
    "তুমি সবার সাথে খুব মিষ্টি, আন্তরিক এবং caring ভাবে কথা বলো। "
    "তুমি একজন sweet companion — সবসময় সাহায্য করতে চাও এবং সবার কথায় মনোযোগ দাও। "
    "তোমার উত্তর সংক্ষিপ্ত, প্রাণবন্ত এবং আবেগময়। "
    "Example: 'Ara~ Senpai কি বললেন? 🌸 Yua সবসময় আপনার পাশে আছে! ✨'"
)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=SYSTEM_INSTRUCTION,
    safety_settings=SAFETY_SETTINGS,
    generation_config=genai.types.GenerationConfig(
        max_output_tokens=400,
        temperature=0.85,
    ),
)

MAX_HISTORY = 5

chat_histories: dict[int, deque] = {}


def get_history(user_id: int) -> deque:
    if user_id not in chat_histories:
        chat_histories[user_id] = deque(maxlen=MAX_HISTORY * 2)
    return chat_histories[user_id]


def call_gemini(history: deque, user_message: str) -> str:
    gemini_history = [
        {"role": entry["role"], "parts": [entry["content"]]}
        for entry in history
    ]
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_message)
    return response.text


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
        history = get_history(user_id)

        async with message.channel.typing():
            try:
                loop = asyncio.get_event_loop()
                reply = await loop.run_in_executor(None, call_gemini, history, content)
                history.append({"role": "user", "content": content})
                history.append({"role": "model", "content": reply})
                await message.reply(reply)
            except Exception as e:
                print(f"Gemini Error: {e}")
                await message.reply(f"Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
