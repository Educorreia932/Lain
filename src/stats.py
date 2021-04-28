import re
import datetime

import discord

from peewee import *

db = SqliteDatabase('../database/stats.db')


# Models

class Channel(Model):
    identifier = IntegerField(primary_key=True)
    last_emoji_update = DateTimeField(null=True)
    last_message_update = DateTimeField(null=True)

    class Meta:
        database = db


class Emoji(Model):
    identifier = IntegerField()
    name = CharField()

    class Meta:
        database = db
        primary_key = CompositeKey("identifier", "name")


class User(Model):
    identifier = IntegerField(primary_key=True)
    name = CharField()

    class Meta:
        database = db


class EmojiCount(Model):
    emoji_name = CharField()
    emoji_id = IntegerField()
    channel = ForeignKeyField(Channel)
    count = IntegerField()

    class Meta:
        database = db
        # primary_key = CompositeKey("emoji_name", "emoji_id", "channel")

    @property
    def emoji(self):
        return Emoji.get(
            Emoji.name == self.emoji_name &
            Emoji.identifier == self.emoji_id
        )


class MessageCount(Model):
    user = ForeignKeyField(User)
    channel = ForeignKeyField(Channel)
    count = IntegerField()

    class Meta:
        database = db


def add_emoji_count(emoji_id, emoji_name, channel_id, count):
    Emoji.get_or_create(identifier=emoji_id, name=emoji_name)

    emoji_count, update = EmojiCount.get_or_create(emoji_name=emoji_name, emoji_id=emoji_id, channel=channel_id,
                                                   count=count)

    if update:
        emoji_count.update(count=emoji_count.count + count).execute()


def get_emoji_count(channel_id):
    usage = {}

    emoji_count = EmojiCount.select().where(EmojiCount.channel == channel_id)

    for row in emoji_count:
        emoji = (row.emoji_name, row.emoji_id)
        usage[emoji] = row.count

    return usage


db.connect()
db.create_tables([Emoji, Channel, EmojiCount])


async def emoji_stats(ctx, bot):
    # channel = ctx.guild.text_channels[0]
    channel = bot.get_channel(826490855111655469)
    channel_db = Channel.get_or_create(identifier=channel.id)[0]

    if channel_db.last_emoji_update is None:
        last_update = channel.created_at

    else:
        last_update = datetime.datetime.fromisoformat(channel_db.last_emoji_update)

    last_update = last_update.replace(tzinfo=None)  # Remove timezone awareness from datetime

    usage = get_emoji_count(channel.id)

    # Iterate over channel's messages
    async for message in channel.history(limit=100, after=last_update):
        # Message's content emoji

        custom_emojis = re.findall(r"<:\w*:\d*>", message.content)

        for emoji in custom_emojis:
            emoji = tuple(re.findall(r'(?<=:)\w+', emoji))
            name = emoji[0]
            identifier = int(emoji[1])
            emoji = (name, identifier)

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
        add_emoji_count(emoji[1], emoji[0], channel.id, count)

    # Update channel's last emoji stats update date
    channel_db.update(last_emoji_update=datetime.datetime.now(tz=datetime.timezone.utc)).execute()

    return {k: v for k, v in sorted(usage.items(), key=lambda item: item[1], reverse=True)}


async def message_stats(ctx):
    channel = ctx.guild.text_channels[0]
    quantity = {}

    async for message in channel.history(limit=None):
        author = message.author.mention

        if author not in quantity:
            quantity[author] = 1

        else:
            quantity[author] += 1

    return {k: v for k, v in sorted(quantity.items(), key=lambda item: item[1], reverse=True)}
