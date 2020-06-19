import collections
import discord
import random
import requests
import time

from discord.ext import commands

bot = commands.Bot(command_prefix='$')
token_file = "token.txt"

with open(token_file) as f:
    TOKEN = f.read()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.command()
async def cmds(ctx):
    commands = """
All the commands must be preceded by the prefix `$`

- **cmds** - Lists all commands of the bot
- **info** - Display information about the bot
- **stats** - Retrieves statistics about the server
    - **emojis** - Total number of usages of each emoji in messages reactions
    - **messages** - Total number of messages per person
- **what [word]** - Get's the definition of a word from Urban Dictionary. You don't need the []
- **joke** - Tells a nerdy joke
    """

    embed = discord.Embed(
        title = "List of Commands",
        description = commands,
        color = 0xeee657
    )
    await ctx.send(embed = embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Nicest teacher there is ever.", description="You should be studying.", color=0xeee657)

    # give info about you here
    embed.add_field(name = "Author", value = "Skelozard/Raymag")

    # Shows the number of servers the bot is member of.
    embed.add_field(name = "Server count", value = f"{len(bot.guilds)}")

    # give users a link to invite thsi bot to their server
    embed.add_field(name = "Invite", value = "https://discord.com/oauth2/authorize?client_id=723158683491762276&permissions=0&scope=bot")

    await ctx.send(embed = embed)


@bot.command()
async def stats(ctx, mode, display_time):  
    print("stats")
    
    await ctx.send("Retrieving stats...")
    
    start_time = time.time()
    
    channel = bot.get_channel(715142746356187195)
    counter = 1
    
    msg = "Modo incorreto, vai para Campo Alegre rapaz."
    
    if mode == "messages":
        users = {}
        msg = "**Number of messages per author:**\n"
        
        async for message in channel.history(limit = 50000):
            if (message.author.name not in users):
                users[message.author.name] = 1
            
            else:
                users[message.author.name] += 1
            
        sorted_users = sorted(users.items(), key=lambda kv: kv[1], reverse = True)
        users = collections.OrderedDict(sorted_users)
            
        for user in users:
            msg += str(counter) + "º) " + user + ": " + str(users[user]) + "\n"
            counter += 1
            
    elif mode == "emojis":
        emojis = {i : 0 for i in bot.emojis}
        
        msg = "**Number of times that each emoji was used\n**"
        
        async for message in channel.history(limit = 50000):
            for reaction in message.reactions:
                for n in range(reaction.count):
                    try:
                        emojis[reaction.emoji] += 1
                    except:
                        continue                        

        sorted_emojis = sorted(emojis.items(), key=lambda kv: kv[1], reverse = True)
        emojis = collections.OrderedDict(sorted_emojis)

        for emoji in emojis:    
            msg += str(counter) + "º) " + str(emoji) + " : " + str(emojis[emoji]) + "\n"
            counter += 1
            
    else:
        print("Usage: stats emojis/messages <-time>")
            
    total_time = time.time() - start_time
    
    await ctx.send(msg[0:1990])
    
    if (display_time == "-time"):
        await ctx.send("Stats completed in " + str(total_time) + " seconds")

@bot.command()
async def what(ctx, word):
    query = requests.get('http://api.urbandictionary.com/v0/define?term=' + word)
    query = query.json()
    
    try:
        if len(query["list"]) > 0:
            embed = discord.Embed(
                title = "**{}**".format(word.title()),
                description = query["list"][0]["definition"].replace("[","__").replace("]","__"),
                color = 0xeee657
            )

            await ctx.send(embed=embed)
            
        else:
            await ctx.send("Sorry, I don't know the meaning of this term.")
    except:
        print("I'm not very well today :c")
   
@bot.command()
async def iq(ctx):
    await ctx.send("You have a total IQ of " + str(random.randint(1, 201)))
   
@bot.command()
async def joke(ctx):
    try:
        query = requests.get("https://sv443.net/jokeapi/v2/joke/Miscellaneous?blacklistFlags=nsfw,religious,political,racist,sexist&type=single")
        query = query.json()

        embed = discord.Embed(
            title = "Here's the joke",
            description = query["joke"],
            color = 0xeee657
        )
        await ctx.send(embed = embed)
    except:
        await ctx.send("I'm not in the mood for jokes today.")

bot.run(TOKEN)