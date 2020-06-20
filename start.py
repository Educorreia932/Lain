import collections
import discord
import random
import requests
import time
import json
import math
import asyncio

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

    # Give info about you here
    embed.add_field(name = "Author", value = "Skelozard/Raymag")

    # Shows the number of servers the bot is member of.
    embed.add_field(name = "Server count", value = f"{len(bot.guilds)}")

    # Give users a link to invite thsi bot to their server
    embed.add_field(name = "Invite", value = "https://discord.com/oauth2/authorize?client_id=723158683491762276&permissions=0&scope=bot")

    await ctx.send(embed = embed)


@bot.command()
async def stats(ctx, mode, display_time = 0, limit = 50000 ):  
    print("stats")
    print("Display_Time: {}\n limit: {}".format(display_time, limit))

    await ctx.send("Retrieving stats...")
    
    start_time = time.time()
    
    channel = bot.get_channel(715142746356187195)
    
    msg = "Modo incorreto, vai para Campo Alegre rapaz."
    msg_title = ""
    current_page = 1
    total_pages = 1
    items_per_page = 50
    array = []
    channel = ctx.channel


    def render_msg_list(array, msg = "", current_page=1, items_per_page=5):
        subarray = array[ ((current_page * items_per_page) - items_per_page ) : ((current_page * items_per_page) - 1) ]
        counter = 1
        if current_page > 1:
            counter = (current_page * items_per_page) - items_per_page
        for item in subarray:
            msg += str(counter) + ". " + str(item[0]) + ": " + str(item[1]) + "\n"
            counter += 1
        return msg
    
    if mode == "messages":
        users = {}
        msg_title = "**Number of messages per author:**\n\n"
        
        async for message in channel.history(limit = limit):
            if (message.author.mention not in users):
                users[message.author.mention] = 1
            
            else:
                users[message.author.mention] += 1
            
        #users
        array = sorted(users.items(), key=lambda kv: kv[1], reverse = True)
            
        current_page = 1
        total_pages = math.ceil(len(array)/items_per_page)
        
            
    elif mode == "emojis":
        emojis = {i : 0 for i in bot.emojis}
        
        msg_title = "**Number of times that each emoji was used\n\n**"
        
        async for message in channel.history(limit = limit):
            for reaction in message.reactions:
                for n in range(reaction.count):
                    try:
                        emojis[reaction.emoji] += 1
                    except:
                        continue                        

        #emojis
        array = sorted(emojis.items(), key=lambda kv: kv[1], reverse = True)

        current_page = 1
        total_pages = math.ceil(len(array)/items_per_page)

    else:
        print("Usage: stats emojis/messages <-time>")

    total_time = time.time() - start_time

    async def show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list):
        msg = render_msg_list(array, msg_title, current_page, items_per_page) 
    
        embed = discord.Embed(
            title = "",
            description = msg[0:1990],
            color = 0xeee657
        )
        embed.add_field(name = 'Page', value = '{}/{}'.format(current_page, total_pages))
        stats = await ctx.send(embed = embed)

        react_emojis = ['◀️', '▶️']
        for emoji in react_emojis:
            await stats.add_reaction(emoji)

        def check_react(reaction, user):
                if reaction.message.id != stats.id:
                    return False
                if str(reaction.emoji) not in react_emojis:
                    return False
                if user != ctx.message.author:
                    return False
                return True
        try:
            res, user = await bot.wait_for('reaction_add', check=check_react, timeout=30)
            if user != ctx.message.author:
                pass
            elif '◀️' in str(res.emoji) and current_page > 1:
                print('Previous page')
                current_page -= 1
                await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list)
            elif '▶️' in str(res.emoji) and current_page < total_pages:
                print('Next page')
                current_page += 1
                await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, user, render_msg_list)
        except asyncio.TimeoutError:
            print("Timeout")
            await stats.delete()
    

    await show_stats(ctx, array, current_page, total_pages, items_per_page, msg_title, ctx.message.author, render_msg_list)        
    
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
            embed = discord.Embed(
                title = "Sorry, I don't know the meaning of this term.",
                color = 0xeee657
            )
            await ctx.send(embed = embed)
    except:
        embed = discord.Embed(
                title = "I'm not feeling well today, please call the dev :(",
                color = 0xeee657
        )
        await ctx.send(embed = embed)
   
@bot.command()
async def iq(ctx):
    embed = discord.Embed(
        title = "You have a total IQ of " + str(random.randint(1, 201)),
        color = 0xeee657
    )
    
    await ctx.send(embed = embed)
   
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
        embed = discord.Embed(
                title = "I'm not feeling well today, please call the dev :(",
                color = 0xeee657
        )
        
        await ctx.send(embed = embed)

@bot.command()
async def excuse(ctx):
    try:
        excuses = []
        with open('excuses.json', 'r', encoding='utf-8') as excuses:
            excuses = json.load(excuses)
        
        embed = discord.Embed(
            title = "I'm not with the homework...",
            description = random.choice(excuses),
            color = 0xeee657
        )
        await ctx.send(embed = embed)
        
    except:
        embed = discord.Embed(
            title = "I'm not feeling well today, please call the dev :(",
            color = 0xeee657
        )
        
        await ctx.send(embed = embed)
        
@bot.command()
async def study(ctx, command, *argv):    
    if command == "request" or command == "submit":
        subjects = {
                "Maths": "📐",
                "Physics": "🌌",
                "Chemistry": "🧪",
                "Computers": "🖥️",
                "Literature": "📚",
                "Philosophy": "🧠",
                "Biology": "🧬",
                "Economics": "💰",
                "Language": "🗣️",
                "History": "⚱",
                "Geography": "🌍" 
            }
        
        subject = argv[0].title()
        
        if (subject not in subjects):
            await ctx.send("That subject is not currently present. Please choose one of the following:")
            
            message = ""
            
            for subject in subjects:
                message += subject + " " + subjects[subject] + "\n"
            
            embed = discord.Embed(
                title = "Supported subjects",
                description = message,
                color = 0xeee657
            )
            
            await ctx.send(embed = embed)
            
            return
        
        title = argv[1]
        description = ""
        
        if (len(argv) > 2):
            description = argv[2]
        
        message = "**Subject:** " + subject + " " + subjects[subject] + "\n" 
        message += "**Title**: " + title + "\n" 
        
        if (description != ""):
            message += "**Description**: " + description + "\n" 
            
        if (command == "request"):
            message += "**Request by**: "
            
        else:
            message += "**Submitted by**: "
        
        message += "<@" + str(ctx.message.author.id) + ">"
        
        embed = discord.Embed(
                title = "New " + command.title(),
                description = message,
                color = 0xeee657
            )
        
        await ctx.send(embed = embed)

bot.run(TOKEN)