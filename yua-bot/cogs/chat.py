import discord
from discord.ext import commands
from google import genai
import os

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        self.model_names = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash']
        self.working_model_name = None

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
                client.models.generate_content(
                    model=name,
                    contents=test_prompt
                )
                print(f"Model works: {name}")
                return name
            except Exception as e:
                print(f"Model {name} failed: {e}")
                continue
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            async with message.channel.typing():
                try:
                    prompt = (
                        message.content
                        .replace(f'<@!{self.bot.user.id}>', '')
                        .replace(f'<@{self.bot.user.id}>', '')
                        .strip()
                    )
                    if not prompt:
                        prompt = "Hello!"

                    system_prompt = (
                        "You are Yua, a 17-year-old cute, caring, and slightly shy Japanese anime girl. "
                        "You speak a mix of English and simple Bengali. "
                        "Use emojis like 🌸 and ✨. You call the user 'Senpai'. "
                        "Always stay in character. Be sweet and warm."
                    )

                    if not self.working_model_name:
                        self.working_model_name = self.find_working_model()

                    if self.working_model_name:
                        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nYua:"
                        response = self.get_client().models.generate_content(
                            model=self.working_model_name,
                            contents=full_prompt
                        )
                        await message.reply(response.text)
                    else:
                        await message.reply("Gomenasai Senpai~ 🌸 No working AI model found for your API key!")

                except Exception as e:
                    print(f"Detailed Error: {e}")
                    await message.reply(f"Debug Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
