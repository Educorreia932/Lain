import re
import discord

async def emoji_stats(ctx):
    channel = ctx.guild.text_channels[1]
    usage = {}

    async for message in channel.history(limit=100000):
        # Message's content emoji

        custom_emojis = re.findall(r'<:\w*:\d*>', message.content)

        for emoji in custom_emojis:
            if emoji not in usage:
                usage[emoji] = 1

            else:
                usage[emoji] += 1

        # Message's reaction emoji

        for reaction in message.reactions:
            if type(reaction.emoji) == discord.Emoji and reaction.emoji.guild_id == ctx.guild.id:
                emoji = str(reaction.emoji)

                if emoji not in usage:
                    usage[emoji] = reaction.count

                else:
                    usage[emoji] += reaction.count

    return {k: v for k, v in sorted(usage.items(), key=lambda item: item[1], reverse=True)}

async def message_stats(ctx):
    channel = ctx.guild.text_channels[0]
    quantity = {}
    
    async for message in channel.history(limit=10000):
        author = message.author.mention

        if author not in quantity:
            quantity[author] = 1

        else:
            quantity[author] += 1

    return {k: v for k, v in sorted(quantity.items(), key=lambda item: item[1], reverse=True)}
