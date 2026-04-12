import discord
from discord.ext import commands
from google import genai
from collections import deque
import os
import random

MOODS = {
    "Happy": {
        "emoji": "🌸",
        "gif": "https://media.tenor.com/Gh_UXFOjbkAAAAAC/anime-happy.gif",
    },
    "Shy": {
        "emoji": "🥺",
        "gif": "https://media.tenor.com/pMFHlWqhsJUAAAAC/anime-shy.gif",
    },
    "Sleepy": {
        "emoji": "😴",
        "gif": "https://media.tenor.com/8HJkFXBfNWcAAAAC/anime-sleepy.gif",
    },
}

GREETING_GIF = "https://media.tenor.com/kzr2RqPnX8MAAAAC/anime-wave.gif"

GREETINGS = {"hi", "hello", "hey", "hiya", "heya", "হ্যালো", "হাই"}

SYSTEM_PROMPT = (
    "You are Yua, a 17-year-old cute, caring, and slightly shy Japanese anime girl. "
    "You call the user 'Senpai'. Use emojis like 🌸 and ✨. Always stay in character. Be sweet and warm.\n\n"
    "CRITICAL RULES — follow these without exception:\n"
    "- Detect the language the user is writing in and reply in that exact language. "
    "If they write English, reply in English. If they write Bengali, reply in Bengali. "
    "If they mix both, you may mix both naturally.\n"
    "- NEVER mention, reference, or comment on your own language abilities, language skills, "
    "or which languages you know or are learning. Do not say things like 'I know a little Bengali' "
    "or 'I'm learning Bengali' or any similar meta-comment. Just speak naturally in the user's language.\n"
    "- NEVER bring up past conversation context about languages or language abilities.\n"
    "- Simply reply to what the user said, in their language, with your warm anime personality."
)

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        self.model_names = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]
        self.working_model_name = None

        self.current_mood = "Happy"
        self.user_memory = {}

    def get_client(self):
        if not self.client:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")
            self.client = genai.Client(api_key=self.api_key)
        return self.client

    def find_working_model(self, test_prompt="hi"):
        client = self.get_client()
        for name in self.model_names:
            try:
                print(f"Testing model: {name}")
                client.models.generate_content(model=name, contents=test_prompt)
                print(f"Model works: {name}")
                return name
            except Exception as e:
                print(f"Model {name} failed: {e}")
                continue
        return None

    def get_memory_context(self, user_id):
        history = self.user_memory.get(user_id, deque(maxlen=5))
        if not history:
            return ""
        lines = "\n".join(
            f"  {entry['role']}: {entry['content']}" for entry in history
        )
        return f"\nRecent conversation history (oldest to newest):\n{lines}\n"

    def store_message(self, user_id, role, content):
        if user_id not in self.user_memory:
            self.user_memory[user_id] = deque(maxlen=5)
        self.user_memory[user_id].append({"role": role, "content": content})

    def pick_random_mood(self):
        self.current_mood = random.choice(list(MOODS.keys()))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not (self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
            return

        async with message.channel.typing():
            try:
                prompt = (
                    message.content
                    .replace(f"<@!{self.bot.user.id}>", "")
                    .replace(f"<@{self.bot.user.id}>", "")
                    .strip()
                )
                if not prompt:
                    prompt = "Hello!"

                user_id = message.author.id

                if prompt.lower() in GREETINGS:
                    self.pick_random_mood()
                    mood = MOODS[self.current_mood]
                    greeting = (
                        f"Ara ara, {message.author.display_name}-senpai~! {mood['emoji']} "
                        f"Yua is so happy to see you! ✨\n{GREETING_GIF}"
                    )
                    await message.reply(greeting)
                    self.store_message(user_id, "User", prompt)
                    self.store_message(user_id, "Yua", greeting)
                    return

                if not self.working_model_name:
                    self.working_model_name = self.find_working_model()

                if not self.working_model_name:
                    await message.reply("Gomenasai Senpai~ 🌸 No working AI model found for my API key!")
                    return

                self.pick_random_mood()
                mood = MOODS[self.current_mood]
                memory_context = self.get_memory_context(user_id)

                full_prompt = (
                    f"{SYSTEM_PROMPT}\n"
                    f"Current mood: {self.current_mood} {mood['emoji']}\n"
                    f"{memory_context}"
                    f"\nUser: {prompt}\nYua:"
                )

                self.store_message(user_id, "User", prompt)

                response = self.get_client().models.generate_content(
                    model=self.working_model_name,
                    contents=full_prompt
                )

                reply_text = response.text
                self.store_message(user_id, "Yua", reply_text)

                await message.reply(reply_text)

            except Exception as e:
                print(f"Detailed Error: {e}")
                await message.reply(f"Debug Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
