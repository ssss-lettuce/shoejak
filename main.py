import discord
from keep_alive import keep_alive
from discord.ext import commands, tasks
import logging
import os
from dotenv import load_dotenv
import random
import requests
import asyncio
import datetime


load_dotenv()
token = os.environ.get('DISCORD_TOKEN')
# botid = int(os.environ.get('BOT_ID'))    # Beta

handler = logging.FileHandler(
        filename='discord.log',
        encoding='utf-8',
        mode='w'
        )

keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
        command_prefix='!shoejak ',
        intents=intents,
        )

newday = datetime.time(hour=15, minute=00, second=0, tzinfo=datetime.timezone.utc)


@tasks.loop(time=newday)
async def anewday():
    channel = bot.get_channel(1425869555254956055)
    await channel.send("It's a new day! 🌞")
    await channel.send("https://cdn.discordapp.com/stickers/1425894902037741689.png")
    print("its a new day")


@bot.event
async def on_ready():
    if not anewday.is_running():
        anewday.start()
        print("new day started!")
    print("Shoejak up and running.")


universalCount = 0
universalLimit = 10
shoelines = ["just making sure i dont shoe in", "i am shoejak and this is my message", "glory to umaori", "ohioooo", "shoes or death", "hachimihachimihachimi"]

@bot.event
async def on_message(message):
    global universalCount
    global universalLimit
    universalCount += 1
    if (int(message.author.id) != 1437798966585720944) and (universalLimit == universalCount):
        funnymsg = random.choice(shoelines)
        await message.reply(str(funnymsg))
        universalCount = 0
        universalLimit = random.randint(50, 300)
        print("new universal limit" )


@bot.command()
async def char(ctx, *, name: str = None):
    if name is None:
        list = requests.get("https://api.umapyoi.net/api/v1/character/list").json()
        characters = []

        for char in list:
            characters += [(char["name_en"], char["id"])]

        start, per_page = 0, 10
        total_pages = (len(characters) + per_page - 1) // per_page

        def build_page(start):
            end = start + per_page
            message = ""
            for n, i in characters[start:end]:
                message += f'{n} id: {i}\n'
            return message

        msg = await ctx.send(build_page(start))
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")

        def check(reaction, user):
            return (
                    user == ctx.author
                    and reaction.message.id == msg.id
                    and str(reaction.emoji) in ["➡️", "⬅️"]
                    )

        while True:
            try:
                reaction, user = await bot.wait_for(
                        "reaction_add", timeout=30.0, check=check
                        )
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break

            if str(reaction.emoji) == "⬅️":
                start -= per_page
                if start < 0:
                    start = (total_pages-1)*per_page

            elif str(reaction.emoji) == "➡️":
                start += per_page
                if start >= len(characters):
                    start = 0

            await msg.edit(content=build_page(start))
            await msg.remove_reaction(reaction.emoji, user)
        return

    if name.isdigit():
        id = int(name)

    else:
        list = requests.get("https://api.umapyoi.net/api/v1/character/list").json()
        characters = []

        for char in list:
            characters += [(char["name_en"].lower(), char["id"])]
        print("char listed")
        results = [
                (name_en, id)
                for name_en, id in characters
                if name.lower() in name_en
                   ]
        print("resulst done")

        if len(results) > 1:
            message = "Did you mean? \n"
            for n, i in results[:10]:
                message += f'{n} id: {i}\n'
            await ctx.send(message)
        else:
            id = results[0][1]

    char = requests.get(f'https://api.umapyoi.net/api/v1/character/{id}').json()
    game_id = char["game_id"]
    images = requests.get(f'https://api.umapyoi.net/api/v1/character/images/{id}').json()
    imagecount = len(images)
    imagenumber = 0
    embed = discord.Embed(title=id, color=0x5865f2)
    embed.set_image(url=images[imagenumber]["images"][0]["image"])
    embed.add_field(name=char["name_en"], value=char["profile"])
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("⬅️")
    await msg.add_reaction("➡️")
    def check(reaction, user):
        return (
                user == ctx.author
                and reaction.message.id == msg.id
                and str(reaction.emoji) in ["➡️", "⬅️"]
                )

    while True:
        try:
            reaction, user = await bot.wait_for(
                    "reaction_add", timeout=30.0, check=check
                    )
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            break

        if str(reaction.emoji) == "⬅️":
            if imagenumber == 0:
                imagenumber = imagecount-1
            else:
                imagenumber -= 1

        elif str(reaction.emoji) == "➡️":
            if imagenumber == (imagecount - 1):
                imagenumber = 0
            else:
                imagenumber += 1

        new_embed = discord.Embed(title=id, color=0x5865f2)
        new_embed.set_image(url=images[imagenumber]["images"][0]["image"])
        new_embed.add_field(name=char["name_en"], value=char["profile"])
        await msg.edit(embed=new_embed)
        await msg.remove_reaction(reaction.emoji, user)




@bot.command()
async def test(ctx):
    print("test receieved")
    await ctx.send("sir yes sir")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
