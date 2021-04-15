import discord
import pathlib

from stats import *
from discord.ext import commands

bot = commands.Bot(command_prefix='(', description='Lain')

TOKEN_LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/../token.txt"

with open(TOKEN_LOCATION) as token_file:
    TOKEN = token_file.read()

@bot.event  
async def on_ready():
    print(f"\nDiscord.py Version: {discord.__version__}")
    print(f"Logged in as: {bot.user.name} - {bot.user.id}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong")

@bot.command()
async def stats(ctx, mode):
    message = "**Emoji Usage Statistics**"

    if mode == "emoji":
        await ctx.send("Retrieving emoji usage stats... This might take some time")

        usage = await emoji_stats(ctx)

        for emoji, count in usage.items():
            message += f"{emoji} - {count}\n"

    elif mode == "messages":
        await ctx.send("Retrieving message quantity stats... This might take some time")

        quantity = await message_stats(ctx)

        for author, count in quantity.items():
            message += f"{author} - {count}\n"

    else:
        await ctx.send("Not a valid mode")

    await ctx.send(message[:1999])

if __name__ == "__main__":
    bot.run(TOKEN)
