import datetime
import discord
import os
import re

from peewee import *

db = SqliteDatabase(os.path.join(os.path.dirname(__file__), '../database/stats.db'))

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
    discriminator = IntegerField()

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

    emoji_count, created = EmojiCount.get_or_create(
        emoji_name=emoji_name,
        emoji_id=emoji_id,
        channel=channel_id,
        count=count
    )

    if not created:
        emoji_count.update(count=emoji_count.count + count).execute()


def add_message_count(user_name, user_discriminator, user_id, channel_id, count):
    User.get_or_create(identifier=user_id, name=user_name, discriminator=user_discriminator)

    message_count, created = MessageCount.get_or_create(
        user_id=user_id,
        channel=channel_id,
        count=count
    )

    if not created:
        message_count.update(count=message_count.count + count).execute()


def get_emoji_count(channel_id):
    emoji_count = {}
    emoji_count_db = EmojiCount.select().where(EmojiCount.channel == channel_id)

    for row in emoji_count_db:
        emoji = (row.emoji_name, row.emoji_id)
        emoji_count[emoji] = row.count

    return emoji_count


def get_message_count(channel_id):
    message_count = {}
    message_count_db = MessageCount.select().where(MessageCount.channel == channel_id)

    for row in message_count_db:
        user = (row.user.name, row.user.discriminator, row.user.identifier)
        message_count[user] = row.count

    return message_count


db.connect()
db.create_tables([Emoji, Channel, EmojiCount, User, MessageCount])


async def emoji_stats(ctx):
    channel = ctx.guild.text_channels[0]
    channel_db = Channel.get_or_create(identifier=channel.id)[0]

    if channel_db.last_emoji_update is None:
        last_update = channel.created_at

    else:
        last_update = datetime.datetime.fromisoformat(channel_db.last_emoji_update)

    last_update = last_update.replace(tzinfo=None)  # Remove timezone awareness from datetime

    usage = get_emoji_count(channel.id)

    # Iterate over channel's messages
    async for message in channel.history(limit=None, after=last_update):
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

    # Update database
    for emoji, count in usage.items():
        add_emoji_count(emoji[1], emoji[0], channel.id, count)

    # Update channel's last emoji stats update date
    channel_db.update(last_emoji_update=datetime.datetime.now(tz=datetime.timezone.utc)).execute()

    return {k: v for k, v in sorted(usage.items(), key=lambda item: item[1], reverse=True)}


async def message_stats(ctx):
    channel = ctx.guild.text_channels[0]
    channel_db = Channel.get_or_create(identifier=channel.id)[0]

    if channel_db.last_message_update is None:
        last_update = channel.created_at

    else:
        last_update = datetime.datetime.fromisoformat(channel_db.last_message_update)

    last_update = last_update.replace(tzinfo=None)  # Remove timezone awareness from datetime

    message_count = get_message_count(channel.id)

    async for message in channel.history(limit=None, after=last_update):
        author = (message.author.name, int(message.author.discriminator), message.author.id)

        if author not in message_count:
            message_count[author] = 1

        else:
            message_count[author] += 1

    # Update database
    for user, count in message_count.items():
        add_message_count(user[0], user[1], user[2], channel.id, count)

    # Update channel's last message stats update date
    channel_db.update(last_message_update=datetime.datetime.now(tz=datetime.timezone.utc)).execute()

    return {k: v for k, v in sorted(message_count.items(), key=lambda item: item[1], reverse=True)}
