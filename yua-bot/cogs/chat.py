import discord
from discord.ext import commands
import google.generativeai as genai
import os

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # API Configure
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key, transport='rest')
        
        # We will try multiple model names to find the right one
        self.model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        self.model = None

    def get_model(self):
        # Try to initialize the model, fallback if one fails
        for name in self.model_names:
            try:
                return genai.GenerativeModel(name)
            except:
                continue
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if bot is mentioned or it's a DM
        if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            async with message.channel.typing():
                try:
                    prompt = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
                    
                    if not prompt:
                        prompt = "Hello!"

                    # Personality setup
                    system_prompt = "You are Yua, a 17-year-old cute, caring, and slightly shy Japanese anime girl. You speak a mix of English and simple Bengali. Use emojis like 🌸, ✨. You love your Senpai."
                    
                    # Initialize model if not already
                    if not self.model:
                        self.model = self.get_model()
                    
                    if self.model:
                        # Generate content
                        response = self.model.generate_content(f"{system_prompt}\n\nUser: {prompt}")
                        await message.reply(response.text)
                    else:
                        await message.reply("Gomenasai Senpai! I couldn't find a brain to think with. (Model Error)")
                        
                except Exception as e:
                    # Clearer error for us to fix
                    await message.reply(f"Debug Error: {str(e)}")
                    print(f"Detailed Error: {e}")

async def setup(bot):
    await bot.add_cog(Chat(bot))
