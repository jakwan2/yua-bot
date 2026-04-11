import discord
from discord.ext import commands
import google.generativeai as genai
import os

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key, transport='rest')

        # Models your API key actually supports (checked via list_models)
        self.model_names = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash']
        self.model = None
        self.working_model_name = None

    def find_working_model(self, test_prompt="hi"):
        # Actually calls generate_content to confirm the model works
        for name in self.model_names:
            try:
                print(f"Testing model: {name}")
                m = genai.GenerativeModel(name)
                m.generate_content(test_prompt)
                print(f"Model works: {name}")
                return m, name
            except Exception as e:
                print(f"Model {name} failed: {e}")
                continue
        return None, None

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

                    # Initialize and verify model on first use
                    if not self.model:
                        self.model, self.working_model_name = self.find_working_model()

                    if self.model:
                        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nYua:"
                        response = self.model.generate_content(full_prompt)
                        await message.reply(response.text)
                    else:
                        await message.reply("Gomenasai Senpai~ 🌸 No working AI model found for your API key!")

                except Exception as e:
                    print(f"Detailed Error: {e}")
                    await message.reply(f"Debug Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
