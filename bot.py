import discord
from discord.ext import commands
import os

# Set up intents (permissions for the bot)
intents = discord.Intents.default()
intents.message_content = True  # This is needed to read message content

# Create a bot instance with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event that triggers when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot is connected to {len(bot.guilds)} server(s)')

# Example command
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.name}!')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
# For security, it's better to use environment variables
if __name__ == "__main__":
    # You can set this in environment variables
    # token = os.getenv('DISCORD_TOKEN')
    # bot.run(token)
    
    # Or directly (not recommended for production)
    bot.run('YOUR_BOT_TOKEN')

