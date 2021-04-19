import re
import discord
from peewee import *

db = SqliteDatabase('database/stats.db')

# Models

class Emoji(Model):
    identifier = IntegerField()
    name = CharField()
    usage_count = IntegerField()

    class Meta:
        database = db 

class User(Model):
    identifier = IntegerField()
    message_count = IntegerField()

    class Meta:
        database = db 

def add_emoji(id, name, usage_count):
    emoji = Emoji(identifier=id, name=name, usage_count=usage_count)
    emoji.save()

def setup_database():
    db.connect()
    db.create_tables([Emoji])

async def emoji_stats(ctx, bot):
    # channel = ctx.guild.text_channels[0]
    channel = bot.get_channel(826490855111655469)
    usage = {}

    async for message in channel.history(limit=100):
        # Message's content emoji

        custom_emojis = re.findall(r'<:\w*:\d*>', message.content)

        for emoji in custom_emojis:
            emoji = tuple(re.findall(r"(?<=:)\w+", emoji))
            name = emoji[0]
            id = int(emoji[1])
            emoji = (name, id)

            if emoji not in usage:
                usage[emoji] = 1

            else:
                usage[emoji] += 1

        # Message's reaction emoji

        for reaction in message.reactions:
            if type(reaction.emoji) == discord.Emoji and reaction.emoji.guild_id == ctx.guild.id:
                emoji = (reaction.emoji.name, reaction.emoji.id)

                if emoji not in usage:
                    usage[emoji] = reaction.count

                else:
                    usage[emoji] += reaction.count

    for emoji, count in usage.items():
        add_emoji(emoji[0], emoji[1], count)

    return {k: v for k, v in sorted(usage.items(), key=lambda item: item[1], reverse=True)}

async def message_stats(ctx):
    channel = ctx.guild.text_channels[0]
    quantity = {}
    
    async for message in channel.history(limit=100000):
        author = message.author.mention

        if author not in quantity:
            quantity[author] = 1

        else:
            quantity[author] += 1

    return {k: v for k, v in sorted(quantity.items(), key=lambda item: item[1], reverse=True)}
