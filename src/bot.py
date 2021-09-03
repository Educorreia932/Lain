from discord.ext import commands

from stats import *

bot = commands.Bot(command_prefix='(', description='Lain')

TOKEN_LOCATION = os.path.join(os.path.dirname(__file__), '../token.txt')

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
    message = "Not a valid mode"

    if mode == "emoji":
        message = "**Emoji Usage Statistics\n**"

        await ctx.send("Retrieving emoji usage stats... This might take some time")

        usage = await emoji_stats(ctx)

        for emoji, count in usage.items():
            message += f"<:{emoji[0]}:{emoji[1]}> - {count}\n"

    elif mode == "messages":
        message = "**Message Quantity Statistics**\n\n"

        await ctx.send("Retrieving message quantity stats... This might take some time")

        quantity = await message_stats(ctx)

        for author, count in quantity.items():
            message += f"**{author[0]}#{author[1]}** - {count}\n"

        print(message)

    await ctx.send(message[:1999])


if __name__ == "__main__":
    bot.run(TOKEN)
