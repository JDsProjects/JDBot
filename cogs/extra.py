import asyncio
import contextlib
import functools
import math
import os
import random
import re
import time
import traceback
import typing
import zoneinfo

import aiohttp
import asuna_api
import asyncpraw
import chardet
import discord
from better_profanity import profanity
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord_games import button_games

import utils
from utils import fuzzy


class Extra(commands.Cog):
    "Uncategorized Commands, these are more random commands"

    def __init__(self, bot):
        self.bot = bot
        self.pool = self.bot.db
        self.afk = {}

    async def cog_load(self):
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("reddit_client_id"),
            client_secret=os.getenv("reddit_client_secret"),
            password=os.getenv("reddit_password"),
            requestor_kwargs={"session": self.bot.session},
            user_agent="JDBot 2.0",
            username=os.getenv("reddit_username"),
        )

        self.sr_client = self.bot.sr_client

        pool = self.pool

        records = await pool.fetch("SELECT * FROM AFK")
        self.afk = {record.user_id: record for record in records}
        self.available_timezones = sorted(list(await asyncio.to_thread(zoneinfo.available_timezones)))

    @commands.command(
        brief="a way to look up minecraft usernames",
        help="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)",
    )
    async def mchistory(self, ctx, *, args=None):
        if args is None:
            await ctx.send("Please pick a minecraft user.")

        if args:
            asuna = asuna_api.Client(self.bot.session)
            minecraft_info = await asuna.mc_user(args)
            embed = discord.Embed(title=f"Minecraft Username: {args}", color=random.randint(0, 16777215))
            embed.set_footer(text=f"Minecraft UUID: {minecraft_info.uuid}")
            embed.add_field(name="Orginal Name:", value=minecraft_info.name)

            for y, x in enumerate(minecraft_info.from_dict):
                if y > 0:
                    embed.add_field(
                        name=f"Username:\n{x.name}",
                        value=f"Date and Time Changed:\n{discord.utils.format_dt(x.changed_at, style = 'd')} \n{discord.utils.format_dt(x.changed_at, style = 'T')}",
                    )

            embed.set_author(name=f"Requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
            await ctx.send(embed=embed)

    @commands.command(
        help="This gives random history using Sp46's api.",
        brief="a command that uses SP46's api's random history command to give you random history responses",
    )
    async def random_history(self, ctx, *, number: typing.Optional[int] = None):
        number = number or 1

        if number < 1 or number > 50:
            await ctx.send(
                "You can not request more than 50 results, you also can not request less than 1 result. We will give you one as this is the default."
            )
            number = 1

        response = random.sample(self.bot.history, number)

        pag = commands.Paginator(prefix="", suffix="")
        for x in response:
            pag.add_line(f":earth_africa: {x}")

        menu = utils.RandomHistoryEmbed(pag.pages, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="gives you the digits of pi that Python knows")
    async def pi(self, ctx):
        await ctx.send(math.pi)

    @commands.command(brief="reverses text")
    async def reverse(self, ctx, *, args=None):
        if args:
            reversed_text = args[::-1]

            await ctx.send(content=f"{reversed_text}", allowed_mentions=discord.AllowedMentions.none())

        if args is None:
            await ctx.send("Try sending actual to reverse")

    @commands.command(brief="Oh no Dad Jokes, AHHHHHH!")
    async def dadjoke(self, ctx):
        response = await self.bot.session.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
        joke = await response.json()
        embed = discord.Embed(title="Random Dad Joke:", color=random.randint(0, 16777215))
        embed.set_author(name=f"Dad Joke Requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
        embed.add_field(name="Dad Joke:", value=joke["joke"])
        embed.set_footer(text=f"View here:\n https://icanhazdadjoke.com/j/{joke['id']}")
        await ctx.send(embed=embed)

    @commands.command(brief="gets a panel from the xkcd comic", aliases=["astrojoke", "astro_joke"])
    async def xkcd(self, ctx):
        response = await self.bot.session.get("https://xkcd.com/info.0.json")
        info = await response.json()

        num = random.randint(1, info["num"])
        comic = await self.bot.session.get(f"https://xkcd.com/{num}/info.0.json")
        data = await comic.json()
        title = data["title"]
        embed = discord.Embed(title=f"{title}", color=random.randint(0, 16777215))
        embed.set_image(url=data["img"])
        embed.set_footer(text=f"Made on {data['month']}/{data['day']}/{data['year']}")
        await ctx.send(embed=embed)

    @commands.command(brief="Gets a cat based on http status code", aliases=["http"])
    async def http_cat(self, ctx, args: typing.Optional[int] = None):
        if args is None:
            code = "404"
        if args:
            if args > 99 and args < 600:
                code = args
            else:
                code = "404"

        response = await self.bot.session.get(f"https://http.cat/{code}")
        if response.status:
            image = f"https://http.cat/{code}.jpg"

        embed = discord.Embed(title=f"Status Code: {code}", color=random.randint(0, 16777215))
        embed.set_author(name=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=image)
        embed.set_footer(text="Powered by http.cat")
        await ctx.send(embed=embed)

    @commands.command(help="Gives advice from Senarc api.", aliases=["ad"])
    async def advice(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/advice")
        res = await r.json()
        embed = discord.Embed(title="Here is some advice for you!", color=random.randint(0, 16777215))
        embed.add_field(name=f"{res['text']}", value="Hopefully this helped!")
        embed.set_footer(text="Powered by Senarc Api!")
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send("was too long...")

    @commands.command(help="gives random compliment")
    async def compliment(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/compliment")
        res = await r.json()
        embed = discord.Embed(title="Here is a compliment:", color=random.randint(0, 16777215))
        embed.add_field(name=f"{res['text']}", value="Hopefully this helped your day!")
        embed.set_footer(text="Powered by Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(help="gives an insult")
    async def insult(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/insult")
        res = await r.json()
        embed = discord.Embed(title="Here is a insult:", color=random.randint(0, 16777215))
        embed.add_field(name=f"{res['text']}", value="Hopefully this Helped?")
        embed.set_footer(text="Powered by Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(help="gives response to slur")
    async def noslur(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/noslur")
        res = await r.json()
        embed = discord.Embed(title="Don't Swear", color=random.randint(0, 16777215))
        embed.add_field(name=f"{res['text']}", value="WHY MUST YOU SWEAR?")
        embed.set_footer(text="Powered by Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(help="gives random message", aliases=["rm"])
    async def random_message(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/randomMessage")
        res = await r.json()
        embed = discord.Embed(title="Random Message:", color=random.randint(0, 16777215))
        embed.add_field(name="Here:", value=res["text"])
        embed.set_footer(text="Powered by Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(
        help="a command to talk to Google TTS", brief="using the power of the asyncgtts module you can now do tts"
    )
    async def tts(self, ctx, *, args=None):
        files = []
        if args:
            files.append(await utils.google_tts(self.bot, args))

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                file = await a.read()
                if file:
                    encoding = chardet.detect(file)["encoding"]
                    if encoding:
                        text = file.decode(encoding)

                        files.append(await utils.google_tts(self.bot, text))

                    if encoding is None:
                        await ctx.send("it looks like it couldn't decode this file, if this is an issue DM jdjg")
                if not file:
                    await ctx.send("this doesn't contain any bytes.")

        if not files:
            return await ctx.send("You didn't specify any text.")

        await ctx.send(content="Big Text will cut off!", files=files)

    @commands.command()
    async def tts_test(self, ctx, *, args=None):
        args = args or "Test"

        time_before = time.perf_counter()
        file1 = await utils.google_tts(self.bot, args)
        time_after = time.perf_counter()

        await ctx.send(content=f"Time to do this: {int((time_after - time_before)*1000)} ms", file=file1)

    @commands.command(brief="Uses google translate to make text to latin in a voice mode :D", aliases=["latin_tts"])
    async def tts_latin(self, ctx, *, args=None):
        if not args:
            await ctx.send("you can't have No text to say")

        else:
            time_before = time.perf_counter()
            file = await utils.google_tts(self.bot, args, "la")
            time_after = time.perf_counter()

            await ctx.send(content=f"Time to do this: {int((time_after - time_before)*1000)} ms", file=file)

    @commands.command(
        help="learn about a secret custom xbox controller",
        brief="this will give you a message of JDJG's classic wanted xbox design.",
    )
    async def sc(self, ctx):
        favorite_color = "Zest Orange"

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name="Secret Xbox Image:")
        embed.add_field(name="Body:", value=favorite_color)
        embed.add_field(name="Back:", value=favorite_color)
        embed.add_field(name="Bumpers:", value=favorite_color)
        embed.add_field(name="Triggers:", value=favorite_color)
        embed.add_field(name="D-pad:", value="Electric Green")
        embed.add_field(name="Thumbsticks:", value="Electric Green")
        embed.add_field(name="ABXY:", value="Colors on Black")
        embed.add_field(name="View & Menu:", value="White on Black")
        embed.add_field(name="Engraving(not suggested):", value="jdjg")
        embed.add_field(
            name="Disclaimer:",
            value="I do not work at microsoft,or suggest you buy this I just wanted a place to represent a controller that I designed a while back.",
        )
        embed.set_image(url="https://i.imgur.com/QCh4M2W.png")
        embed.set_footer(
            text="This is Xbox's custom controller design that I picked for myself.\nXbox is owned by Microsoft. I don't own the image"
        )
        await ctx.send(embed=embed)

    @commands.command(
        brief="repeats what you say", help="a command that repeats what you say the orginal message is deleted"
    )
    async def say(self, ctx, *, args=None):
        if args is None:
            args = "You didn't give us any text to use."

        args = discord.utils.escape_markdown(args, as_needed=False, ignore_links=False)
        try:
            await ctx.message.delete()

        except discord.errors.Forbidden:
            pass

        await ctx.send(args, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(brief="does say but more powerful with the optional option of a channel to say in")
    async def say2(
        self,
        ctx,
        channel: typing.Optional[typing.Union[discord.TextChannel, discord.Thread]] = commands.CurrentChannel,
        *,
        args=None,
    ):
        args = args or "You didn't give us any text to use."
        args = discord.utils.escape_markdown(args, as_needed=False, ignore_links=False)

        bot_member = channel.me if isinstance(channel, discord.DMChannel) else channel.guild.me

        if channel.permissions_for(bot_member).send_messages:
            if isinstance(bot_member, discord.Member):
                author_member = await self.bot.try_member(bot_member.guild, ctx.author.id)

                channel = channel if author_member else ctx.channel

            await channel.send(f"{args}\nMessage From {ctx.author}", allowed_mentions=discord.AllowedMentions.none())

        else:
            await ctx.send("doesn't have permissions to send in that channel.")

    @commands.command(
        brief="a command to backup text", help="please don't upload any private files that aren't meant to be seen"
    )
    async def text_backup(self, ctx, *, args=None):
        if ctx.message.attachments:
            for a in ctx.message.attachments:
                file = await a.read()
                if file:
                    encoding = chardet.detect(file)["encoding"]
                    if encoding:
                        text = file.decode(encoding)
                        paste = await utils.post(self.bot, code=text)
                        # max paste size is 400,000(find easiest to upload and to render then use textwrap in asyncio to handle it.)
                        await ctx.send(content=f"Added text file to Senarc Bin: \n{paste}")
                    if encoding is None:
                        await ctx.send(
                            "it looks like it couldn't decode this file, if this is an issue DM jdjg or it wasn't a text file."
                        )
                if not file:
                    await ctx.send("this doesn't contain any bytes.")

        if args:
            await ctx.send("this is meant to backup text files and such.")

        if not args and not ctx.message.attachments:
            await ctx.send("you didn't give it any attachments.")

    @commands.group(name="apply", invoke_without_command=True)
    async def apply(self, ctx):
        await ctx.send("this command is meant to apply")

    @apply.command(brief="a command to apply for our Bloopers.", help="a command to apply for our bloopers.")
    async def bloopers(self, ctx, *, args=None):
        if args is None:
            await ctx.send("You didn't give us any info.")
        if args:
            if isinstance(ctx.message.channel, discord.TextChannel):
                await ctx.message.delete()

            for x in [708167737381486614, 168422909482762240]:
                apply_user = await self.bot.try_user(x)

            embed_message = discord.Embed(
                title=args, color=random.randint(0, 16777215), timestamp=(ctx.message.created_at)
            )
            embed_message.set_author(name=f"Application from {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed_message.set_footer(text=f"{ctx.author.id}")
            embed_message.set_thumbnail(url="https://i.imgur.com/PfWlEd5.png")
            await apply_user.send(embed=embed_message)

    @commands.command(aliases=["bird", "birb"])
    async def caw(self, ctx):
        url = await utils.alexflipnote_api(self.bot.session, "birb")
        await ctx.send(url)

    @commands.command(aliases=["bark", "dogs"])
    async def dog(self, ctx):
        url = await utils.alexflipnote_api(self.bot.session, "dogs")
        await ctx.send(url)

    @commands.command(aliases=["meow", "cats"])
    async def cat(self, ctx):
        url = await utils.alexflipnote_api(self.bot.session, "cats")
        await ctx.send(url)

    @commands.command(aliases=["joke"])
    async def jokeapi(self, ctx):
        jokeapi_grab = await self.bot.session.get(
            "https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"
        )
        response_dict = await jokeapi_grab.json()
        embed = discord.Embed(title=f"{response_dict['joke']}", color=random.randint(0, 16777215))
        embed.set_author(name=f"{response_dict['category']} Joke:")
        embed.add_field(name="Language:", value=f"{response_dict['lang']}")
        embed.add_field(name="Joke ID:", value=f"{response_dict['id']}")
        embed.add_field(name="Type:", value=f"{response_dict['type']}")
        embed.set_footer(text=f"Joke Requested By {ctx.author} \nPowered by jokeapi.dev")
        await ctx.send(embed=embed)

    @commands.command(brief="a cookie clicker save")
    async def cc_save(self, ctx):
        import io

        paste = await utils.get_paste(self.bot, "YrQBLL")
        s = io.StringIO()
        s.write(paste)
        s.seek(0)

        await ctx.reply(
            "The save editor used: https://coderpatsy.bitbucket.io/cookies/v10466/editor.html \n Warning may be a bit cursed. (because of the grandmas having madness at this level.) \n To be Used with https://orteil.dashnet.org/cookieclicker/",
            file=discord.File(s, filename="cookie_save.txt"),
        )
        # will be fixed soon

    @commands.command(brief="allows you to quote a user, without pings")
    async def quote(self, ctx, *, message=None):
        message = message or "Empty Message :("

        await ctx.send(f"> {message} \n -{ctx.message.author}", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(brief="hopefully use this to show to not laugh but instead help out and such lol")
    async def letsnot(self, ctx):
        emoji = discord.utils.get(self.bot.emojis, name="commandfail")
        await ctx.send(
            f"Let's not go like {emoji} instead let's try to be nice about this. \nGet a copy of this image from imgur: https://i.imgur.com/CykdOIz.png",
            reference=ctx.message.reference,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(brief="edits a message with a specific twist(100)% lol")
    async def edit_that(self, ctx):
        message = await ctx.send("Hello guys I am going to be edited")
        await asyncio.sleep(2)
        await message.edit(content="hello guys I am going to be edited \u202b  Heck yeah")

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(
        brief="cleansup bot message's history in a channel if need be.(Doesn't cleanup other people's message history)"
    )
    async def cleanup(self, ctx, *, amount: typing.Optional[int] = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.send(
                "doesn't work in DMS, due to discord limitations about builking deletes messages(if we could we would)"
            )

        amount = amount or 10
        if amount > 100:
            await ctx.send("max 100 messages, going to 10 messages.")

            amount = 10
            amount += 1

        if not utils.cleanup_permission(ctx):
            amount = 10

            await ctx.send("you don't have manage messages permissions nor is it a dm")
            amount += 1

        await ctx.send("attempting to delete history of commands")
        amount += 1

        messages = None
        with contextlib.suppress(discord.Forbidden, discord.HTTPException):
            messages = await ctx.channel.purge(limit=amount, bulk=False, check=utils.Membercheck(ctx))

        if not messages:
            return await ctx.send(
                "it likely errored with not having the proper manage message permissions(shouldn't happen), or any http exception happened."
            )

        page = "\n".join(f"{msg.author} ({('Bot' if msg.author.bot else 'User')}) : {msg.content}" for msg in messages)

        try:
            paste = await utils.post(self.bot, page)
        except:
            return await ctx.send("failed posting back of messages")

        await ctx.author.send(content=f"Added text file to Senarc Bin: \n{paste}")

    @commands.cooldown(1, 40, BucketType.user)
    @commands.command(brief="allows you to review recent embeds", aliases=["embedhistory", "embed_history"])
    async def closest_embed(self, ctx):
        embed_history = [embed async for embed in ctx.channel.history(limit=50)]
        embeds = [embed for e in embed_history for embed in e.embeds][:10]

        if not embeds:
            return await ctx.send("No embeds found :D")

        await ctx.send(
            "Sending you the previous 10 embeds sent in 50 messages if under 10 well the amount that exists, if none well you get none."
        )

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="takes two numbers and does a cool command")
    async def radical(self, ctx, *numbers: typing.Union[int, str]):
        if not numbers:
            return await ctx.send("sorry boss you didn't give us any numbers to use.")

        numbers = sorted(list(filter(lambda x: isinstance(x, int), numbers)))

        if not numbers:
            return await ctx.send("Not enough numbers")

        elif len(numbers) < 2:
            num = 1

        elif len(numbers) > 1:
            num = numbers[0]

        root = numbers[-1]

        embed = discord.Embed(title="The Radical Function Has Been Completed!", color=random.randint(0, 16777215))

        embed.set_footer(text=f"{ctx.author} | {ctx.author.id}")
        embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")
        embed.add_field(name=f"Formula: {num}√ {root}", value=f"Result: {int(root**(1/num))}")

        await ctx.send(embed=embed)

    @commands.command(brief="takes two numbers and does a cool command")
    async def power(self, ctx, *numbers: typing.Union[int, str]):
        if not numbers:
            return await ctx.send("sorry boss you didn't give us any numbers to use.")

        numbers = sorted(list(filter(lambda x: isinstance(x, int), numbers)))

        if not numbers:
            return await ctx.send("Not enough numbers")

        elif len(numbers) < 2:
            root = 1

        elif len(numbers) > 1:
            root = numbers[0]

        num = numbers[-1]

        embed = discord.Embed(title="Result of the function", color=random.randint(0, 16777215))
        embed.add_field(name=f"Formula: {num} ^ {root}", value=f"Result: {(num**root)}")
        embed.set_footer(text=f"{ctx.author.id}")
        embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")
        await ctx.send(embed=embed)

    @commands.max_concurrency(number=1, per=BucketType.channel, wait=True)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(brief="a way to talk to cleverbot", aliases=["chatbot"])
    async def cleverbot(self, ctx):
        view = utils.ChatBotView(ctx)

        return await ctx.send("out of commission right now.")

        view.ask = self.cleverbot.ask
        # update to use the chatbot system Soheab made and also figure out how to use a rsap api or to run a free open ai chatbot for view.ask2.
        # view.ask2 = self.sr_api.chatbot

        await ctx.reply(
            "we firstly apoligize if chatbot offends you or hurts your feelings(like actually does so not as a joke or trying to cause drama thing.)\nPlease Hit the buttons now to start the modal ",
            view=view,
        )

    @commands.command(brief="a command to create a voice channel")
    async def voice_create(self, ctx, *, args=None):
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.send("you can't make a voice channel in a DM")

        if not args:
            return await ctx.send("You need to give me some text to use.")

        if not utils.create_channel_permission(ctx):
            return await ctx.send("you don't have permission to use that.")

        if not ctx.me.guild_permissions.manage_channels:
            return await ctx.send(
                "I can't make a voice channel! If you want this to work you need to give manage channel permissions :("
            )

        channel = await ctx.guild.create_voice_channel(args)

        invite = "N/A"
        if channel.permissions_for(ctx.me).create_instant_invite:
            invite = await channel.create_invite()

        await ctx.send(f"join the channel at {channel.mention} \n Invite to join: {invite}")

    @commands.command(brief="a command to create a text channel")
    async def channel_create(self, ctx, *, args=None):
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.send("you can't make a text channel in a DM")

        if not args:
            return await ctx.send("You need to give me some text to use.")

        if not utils.create_channel_permission(ctx):
            return await ctx.send("you don't have permission to use that.")

        if not ctx.me.guild_permissions.manage_channels:
            return await ctx.send(
                "I can't make a text channel! If you want this to work you need to give manage channel permissions :("
            )

        channel = await ctx.guild.create_text_channel(args)

        invite = "N/A"
        if channel.permissions_for(ctx.me).create_instant_invite:
            invite = await channel.create_invite()

        await ctx.send(f"join the channel at {channel.mention} \n Invite to join: {invite}")

    @commands.command(brief="makes a discord profile link")
    async def profile_link(self, ctx, user: utils.SuperConverter = commands.Author):

        user_link = f"discord:///users/{user.id}"
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"{user}'s profile link", url=user_link, style=discord.ButtonStyle.link))
        await ctx.send(f"The profile for {user} is https://discord.com/users/{user.id}", view=view)

    @commands.command(bried="tells you the current time with discord's speacil time converter", name="time")
    async def _time(self, ctx):
        embed = discord.Embed(
            title="Current Time :",
            description=f"{discord.utils.format_dt(ctx.message.created_at, style = 'd')}{discord.utils.format_dt(ctx.message.created_at, style = 'T')}",
            color=random.randint(0, 16777215),
        )

        embed.set_footer(text=f"Requested By {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(brief="takes three values lol")
    async def arithmetic(self, ctx, *numbers: typing.Union[int, str]):
        if not numbers:
            return await ctx.send("sorry boss you didn't give us any numbers to use.")

        numbers = sorted(list(filter(lambda x: isinstance(x, int), numbers)))

        if not numbers:
            return await ctx.send("Not enough numbers, you need 3 values ")

        elif len(numbers) < 3:
            return await ctx.send(
                "Not enough numbers, you need 3 values (the orginal number, how many times it per time you run it, and how many times it goes)"
            )

        elif len(numbers) > 2:
            orginal = numbers[0]
            number_each_time = numbers[1]
            times_ran = numbers[-1]

            embed = discord.Embed(title="Result of the function", color=random.randint(0, 16777215))

            embed.add_field(
                name=f"Formula: {orginal} + {number_each_time} * ( {times_ran} - 1 )",
                value=f"Result: {orginal+number_each_time*(times_ran-1)}",
            )

            embed.set_footer(text=f"{ctx.author.id}")
            embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")

        await ctx.send(embed=embed)

    @commands.command(
        brief="a command that uses discord.py's query_members to cache users(only use this if you want to cache yourself, you can't cache others to with this)"
    )
    async def cache_member(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.send("querying members doesn't work in dms.")

        view = utils.BasicButtons(ctx)

        msg = await ctx.send(
            "Do you agree to cache yourself in the temp guild members list(this is something in discord.py where it caches members, but it's gone after bot startup, it will also not be stored anywhere else as that would be bad if it did, it will only be used to bring api calls down)?",
            view=view,
        )

        await view.wait()

        if view.value is None:
            await ctx.reply("You let me time out :(")
            return await msg.delete()

        if view.value:
            if not ctx.guild.get_member(ctx.author.id):
                await msg.delete()

                msg = await ctx.send(
                    "attempting to cache you with query_members in discord.py(this way you don't need to make api calls if you wish.) If you don't trust us you can always use the support command to get info about this or jdjgsummon, and I'll gladly so you this what I say."
                )

                try:
                    await ctx.guild.query_members(cache=True, limit=5, user_ids=[ctx.author.id])

                except Exception as e:
                    await asyncio.sleep(1)
                    return await msg.edit(
                        content=f"failed caching members with query_members in discord.py with error {e}"
                    )

                await asyncio.sleep(1)
                await msg.edit(content="successfully cached you")

            else:
                await msg.delete()
                return await ctx.send("You are already cached :D, you don't need to cache again")

        if not view.value:
            await msg.delete()
            await ctx.reply("You didn't agree to being cached.")

    @commands.command(brief="says nook nook and shows an image")
    async def pingu(self, ctx):
        embed = discord.Embed(description="nook nook", color=random.randint(0, 16777215))
        embed.set_image(url="https://i.imgur.com/Z6NURwi.gif")
        embed.set_author(name=f"Pingu has been summoned by {ctx.author}:", icon_url=ctx.author.display_avatar.url)
        await ctx.send("nook nook", embed=embed)

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(
        brief="generates a random sm64 color code",
        aliases=["generate_color_code", "generate_colorcode", "g_cc", "cc_generator"],
    )
    async def generate_cc(self, ctx):
        embed = discord.Embed(description=f"```{utils.cc_generate()}```", color=random.randint(0, 16777215))

        embed.set_author(name=f"{ctx.author} Generated A Random CC:", icon_url=ctx.author.display_avatar.url)

        embed.set_footer(text="Generated a random sm64 color code.")
        await ctx.send(embed=embed)

    @commands.command(brief="brings up two sites of logical fallicies")
    async def fallacies_list(self, ctx):
        await ctx.send(
            "https://www.futurelearn.com/info/courses/logical-and-critical-thinking/0/steps/9131 \nhttps://yourlogicalfallacyis.com/"
        )

    @commands.command(brief="based on pog bot's nitro command")
    async def nitro(self, ctx):
        embed = discord.Embed(
            title="You've been gifted a subscription!",
            description="You've been gifted Nitro for **1 month!**\nExpires in **24 hours**",
            color=3092790,
        )
        embed.set_thumbnail(url="https://i.imgur.com/w9aiD6F.png")

        view = utils.nitroButtons(timeout=180.0)
        await ctx.send(embed=embed, view=view)

    @commands.cooldown(1, 60, BucketType.user)
    @commands.cooldown(1, 60, BucketType.channel)
    @commands.command(brief="gets the first message in a channel", aliases=["first_message", "firstmessage"])
    async def firstmsg(
        self,
        ctx,
        channel: typing.Optional[
            typing.Union[
                discord.TextChannel,
                discord.Thread,
                discord.DMChannel,
                discord.GroupChannel,
                discord.User,
                discord.Member,
            ]
        ] = commands.CurrentChannel,
    ):
        print(type(channel))

        messages = [message async for message in channel.history(limit=1, oldest_first=True)]

        if not messages:
            return await ctx.send(
                "Couldn't find the first message or any message :shrug: Not sure why \nPlease Check if you dmed the bot at all, if not dm it :) \nOtherwise, please note that it will always return this message"
            )

        embed = discord.Embed(
            color=random.randint(0, 16777215),
            timestamp=ctx.message.created_at,
            description=f"Click on [message link]({messages[0].jump_url}) to see the channel listed below's first message \nChannel : {channel.mention}",
        )

        embed.set_author(
            name=f"Message Author: {messages[0].author}", icon_url=f"{messages[0].author.display_avatar.url}"
        )

        await ctx.send(content="here's the first message in that channel", embed=embed)

    @commands.is_nsfw()
    @commands.command(
        brief="Shows the meaning of word using the urban dictionary.", aliases=["dict", "dictionary", "meaning"]
    )
    async def urban(self, ctx, *, search: commands.clean_content = None):
        if search is None:
            return await ctx.send("Specify what you need to be searched in the urban dictionary.")

        try:
            response = await self.bot.session.get(
                f"https://api.urbandictionary.com/v0/define?term={search}", headers={"Accept": "application/json"}
            )

        except Exception:
            return await ctx.send("Urban API returned invalid data.")

        url = await response.json()

        if not url:
            return await ctx.send(":fire: an Error has occured.")

        if not len(url["list"]):
            return await ctx.send("Couldn't find your search in the dictionary.")

        result = sorted(url["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]
        definition = result["definition"]

        if len(definition) >= 1000:
            definition = definition[:1000]
            definition = definition.rsplit(" ", 1)[0]
            definition += "..."

        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            title="Urban Dictionary",
            description=f"**Search:** {search}\n\n**Result:** {result['word']}\n```fix\n{definition}```",
            color=242424,
        )
        embed.set_author(name=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(brief="says hi to you")
    async def hi(self, ctx):
        await ctx.send(f"hi {ctx.author}")

    @commands.command(brief="snipe")
    async def snipe(self, ctx):
        await ctx.send("We don't snipe messages, sorry :(")

    async def asyncpraw_handler(self, sub_name):
        subreddit = await self.reddit.subreddit(sub_name)
        meme_list = [result async for result in subreddit.new()]

        meme_list = list(filter(lambda m: not m.over_18, meme_list))

        data = random.choice(meme_list)
        embed = discord.Embed(
            title=f"{data.subreddit_name_prefixed}",
            description=f"[{data.title}](https://reddit.com{data.permalink})",
            color=0x00FF00,
        )
        embed.set_image(url=data.url)
        embed.set_footer(text=f"Upvote ratio : {data.upvote_ratio}")
        return embed

    @commands.command(brief="looks up stuff from reddit")
    async def reddit(self, ctx):
        subreddits = await self.bot.db.fetch("SELECT * FROM SUBREDDITS")

        view = utils.SubredditChoice(ctx, subreddits, timeout=15.0)

        await ctx.send("Please Pick a Subreddit to get a random post from:", view=view)
        await view.wait()

        subreddit = await self.bot.db.fetchrow("SELECT * FROM SUBREDDITS WHERE name = $1", view.value)

        subreddit_name = subreddit.get("name")

        embed = await self.asyncpraw_handler(subreddit_name)
        await ctx.send(embed=embed)

    @commands.group(brief="list of commands of plans of stuff to do in the future", invoke_without_command=True)
    async def todo(self, ctx):
        await ctx.send_help(ctx.command)

    @todo.command(brief="lists stuff in todo", name="list")
    async def todo_list(self, ctx):
        values = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1 ORDER BY added_time ASC", ctx.author.id)

        if not values:
            embed = discord.Embed(
                description="No items in your Todo List", color=1246983, timestamp=ctx.message.created_at
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            return await ctx.send(embed=embed)

        pag = commands.Paginator(max_size=4098, prefix="", suffix="")

        for index, todo_entry in enumerate(values):
            pag.add_line(
                f"[{index+1}]({todo_entry['jump_url']}). {discord.utils.format_dt(todo_entry['added_time'], 'R')} {todo_entry['text']}"
            )

        menu = utils.TodoEmbed(pag.pages, ctx=ctx, delete_after=True)

        await menu.send()

    @todo.command(brief="adds items to todo")
    async def add(self, ctx, *, text: commands.clean_content = None):
        if not text:
            return await ctx.send("Please tell me what to add")

        value = await self.bot.db.fetchrow("SELECT * FROM todo WHERE user_id = $1 AND TEXT = $2", ctx.author.id, text)

        if value:
            embed = discord.Embed(
                description=f"[ADDED HERE]({value['jump_url']}) : {discord.utils.format_dt(value['added_time'], 'R')}",
                color=random.randint(0, 16777215),
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Text:", value=f"{value['text']}")
            embed.set_footer(text="Repeated Text", icon_url="https://i.imgur.com/nPAONbK.png")
            return await ctx.send(content="That was already added here:", embed=embed)

        await self.bot.db.execute(
            "INSERT INTO todo (user_id, text, jump_url, added_time) VALUES ($1, $2, $3, $4)",
            ctx.author.id,
            text[0:4000],
            ctx.message.jump_url,
            ctx.message.created_at,
        )

        embed = discord.Embed(color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.add_field(name="Text:", value=f"{text[0:4000]}")
        embed.set_footer(text="Text Added Successfully", icon_url=ctx.author.display_avatar.url)
        await ctx.send(content="**Added Succesfully**:", embed=embed)

    @todo.command(brief="edits items in todo")
    async def edit(self, ctx, number: typing.Optional[int] = None, *, text=None):
        if not number:
            return await ctx.send("Looks like you didn't input a valid number starting from one.")

        values = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1 ORDER BY added_time ASC", ctx.author.id)

        if not text:
            return await ctx.send("I have no text to work with.")

        if not values:
            return await ctx.send("You can't edit anything as you lack items.")

        if number < 1:
            return await ctx.send("You need to start from 1.")

        if (number - 1) > len(values):
            return await ctx.send("You don't have that many items, pick something lower.")

        todo = values[number - 1]

        embed = discord.Embed(color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.add_field(name="Text:", value=f"{todo['text']}")

        view = utils.BasicButtons(ctx, timeout=15.0)

        msg = await ctx.send("Are you sure you want to edit the item?:", embed=embed, view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit(content="you didn't respond quickly enough")

        if not view.value:
            return await msg.edit(content="Not editing your item from todo.")

        if view.value:
            value = await self.bot.db.fetchrow(
                "SELECT * FROM todo WHERE user_id = $1 AND TEXT = $2", ctx.author.id, text
            )

            if value:
                return await ctx.send("Looks like you already edited that text.")

            await self.bot.db.execute(
                "UPDATE TODO SET TEXT = $1 WHERE user_id = $2 and added_time = $3",
                text[0:4000],
                ctx.author.id,
                todo["added_time"],
            )

            embed = discord.Embed(
                title=f"You edited task {number} from todo",
                color=random.randint(0, 16777215),
                timestamp=todo["added_time"],
            )
            embed.add_field(name="Old Text:", value=f"{todo['text']}")
            embed.add_field(name="New Text:", value=f"{text[0:4000]}")
            embed.set_footer(text="Creation Date")
            await msg.edit(content="Edited the item Succesfully.", embed=embed)

    @todo.command(brief="removes items in todo")
    async def remove(self, ctx, *, number: typing.Optional[int] = None):
        if not number:
            return await ctx.send("Looks like you didn't input a valid number starting from one.")

        values = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1 ORDER BY added_time ASC", ctx.author.id)

        if not values:
            return await ctx.send("Good News, you don't need to remove anything as you lack items.")

        if number < 1:
            return await ctx.send("You need to start from 1.")

        if (number - 1) > len(values):
            return await ctx.send("You don't have that many items, pick something lower.")

        todo = values[number - 1]

        embed = discord.Embed(color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.add_field(name="Text:", value=f"{todo['text']}")

        view = utils.BasicButtons(ctx, timeout=15.0)

        msg = await ctx.send("Are you sure you want to remove the item?:", embed=embed, view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit(content="you didn't respond quickly enough")

        if not view.value:
            return await msg.edit(content="Not remove your item from todo.")

        if view.value:
            await self.bot.db.execute(
                "DELETE FROM todo WHERE user_id = $1 and ADDED_TIME = $2", ctx.author.id, todo["added_time"]
            )

            await msg.edit(content="Successfully removed your item :D")

    @todo.command(brief="removes all your items in todo")
    async def clear(self, ctx):
        values = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1 ORDER BY added_time ASC", ctx.author.id)

        if not values:
            return await ctx.send(
                "You haven't added any todo items, so we can't clear any items as you don't have any."
            )

        view = utils.BasicButtons(ctx)

        msg = await ctx.send("Are you sure you want to clear your todo list?", view=view)

        await view.wait()
        if view.value is None:
            return await msg.edit(content="you didn't respond quickly enough")

        if not view.value:
            return await msg.edit(
                content="Not removing your todo list from the database, 0 items are removed as a result."
            )

        if view.value:
            await self.bot.db.execute("DELETE FROM todo WHERE user_id = $1", ctx.author.id)
            await msg.edit(content=f"We Removed **{len(values)}** values")

    @commands.command(brief="a command that does calc with buttons", aliases=["calculator"])
    async def calc(self, ctx):
        view = utils.CalcView(ctx)
        await ctx.send("\u200b", view=view)

    @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
    async def setprefix(self, ctx, *, prefix: str = None):
        # I have to add regex to prevent mentioning as a prefix lol(as this encouarges spam

        db = self.bot.db
        if ctx.guild:
            if not ctx.author.guild_permissions.administrator and not await self.bot.is_owner(ctx.author):
                # better method to run handle permissions.

                return await ctx.send("You do not have proper permission for this.")
            is_dm = 0
            tid = ctx.guild.id
        else:
            is_dm = 1
            tid = ctx.author.id
        existing = await db.fetchrow("SELECT * FROM PREFIXES WHERE is_dm = $1 AND id = $2", is_dm, tid)

        if prefix:
            if profanity.contains_profanity(prefix):
                return await ctx.send("Prefix contains profanity, so cannot add it into prefix list.")
            if existing:
                return await ctx.send("You already have custom prefix set.")
        if not prefix and not existing:
            return await ctx.send("You are trying to remove an inexistant prefix.")

        cache = self.bot.prefix_cache
        if prefix:
            is_mentionable = re.search(r"<(?:@|#|@&)!?(?P<user_id>[0-9]{15,23})>|@(?:here|everyone)", prefix)

            if is_mentionable:
                return await ctx.send("We don't allow mentions as it leads to spam")

            view = utils.BasicButtons(ctx)
            msg = await ctx.send("Are you sure you want to add prefix ?", view=view)
            await view.wait()
            if view.value == None:
                await msg.delete()
                return await ctx.send("You did not respond in time.")

            if view.value:
                if len(prefix) > 5:
                    return await ctx.send("Prefix cannot be longer than 5 characters.")
                await db.execute("INSERT INTO PREFIXES VALUES ($1, $2, $3)", is_dm, tid, prefix)
                cache[tid] = prefix
                await ctx.send("Successfully set the prefix.")
            else:
                return await ctx.send("Cancelled.")

        else:
            view = utils.BasicButtons(ctx)
            msg = await ctx.send("Are you sure you want to clear custom prefix ?", view=view)
            await view.wait()

            if view.value == None:
                await msg.delete()
                return await ctx.send("You did not respond in time.")

            if view.value:
                await db.execute("DELETE FROM PREFIXES WHERE is_dm = $1 AND id = $2", is_dm, tid)
                if tid in cache:  # to account potential race condition
                    del cache[tid]
                await ctx.send("Successfully removed prefix.")
            else:
                return await ctx.send("Cancelled.")

    @commands.command(aliases=["aki"], brief="akinator game made by Tom the Bomb")
    async def akinator(self, ctx):
        game = button_games.BetaAkinator()
        await game.start(ctx, timeout=120, delete_button=True)

    @commands.command()
    async def afk(self, ctx, *, reason: typing.Optional[str] = None):
        if ctx.author.id in self.afk:
            return

        reason = reason or "Unknown"

        reason = profanity.censor(reason, censor_char="#")

        embed = discord.Embed(title="You Are Now Afk", color=15428885)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(
            content=f"{ctx.author.mention} is now afk", embed=embed, allowed_mentions=discord.AllowedMentions.none()
        )

        data = await self.bot.db.fetchrow(
            "INSERT INTO AFK VALUES($1, $2, $3) RETURNING *", ctx.author.id, ctx.message.created_at, reason
        )

        self.afk[ctx.author.id] = data

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author.id in self.afk:
            data = self.afk[message.author.id]

            timestamp = discord.utils.format_dt(data.added_time, style="R")

            embed = discord.Embed(
                title="AFK", description=f"Reason : **{data.text}**\nAfk Since : {timestamp}", color=15428885
            )
            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)

            await message.channel.send(
                f"Welcome Back {message.author.mention}",
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )

            del self.afk[message.author.id]
            await self.bot.db.execute("DELETE FROM AFK WHERE user_id = $1", message.author.id)

        afk = list(filter(lambda u: u.id in self.afk, message.mentions))

        if not afk:
            return

        if len(afk) > 1:
            msg = "Sorry, several people you mentioned are afk\n\n"
            msg += "\n".join(
                f'{u.mention} - {self.afk[u.id].text} (since {discord.utils.format_dt(self.afk[u.id].added_time, style="R")})'
                for u in afk
            )

        else:
            u = afk[0]
            data = self.afk[u.id]
            timestamp = discord.utils.format_dt(data.added_time, style="R")
            msg = f"Sorry {u.mention} is afk right now \nReason: {data.text} \nAfk Since: {timestamp}"

        await message.channel.send(msg, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.user_install()
    @app_commands.guild_install()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        temperature_unit="Select a Unit Temperature from the dropdown.",
        temperature="Please enter a number",
    )
    @app_commands.command(description="A command to convert temperatures to different scales")
    async def convert_temperature(
        self,
        interaction: discord.Interaction,
        temperature_unit: utils.Temperature,
        temperature: float,
    ):
        temps = temperature_unit.convert_to(temperature)

        if temps.celsius < 20:
            color = 0x0000FF

        if temps.celsius >= 20 and temps.celsius <= 30:
            color = 0xFFA500

        if temps.celsius > 30:
            color = 0xFF0000

        embed = discord.Embed(title="Temperature:", color=color)
        embed.add_field(name="Celsius:", value=f"{temps.celsius:,} °C")
        embed.add_field(name="Fahrenheit:", value=f"{temps.fahrenheit:,} °F")
        embed.add_field(name="Kelvin:", value=f"{temps.kelvin:,} K")
        embed.add_field(name="Rankine:", value=f"{temps.rankine:,} °R")
        embed.set_footer(text=f"Chose: {temperature_unit.value}")

        await interaction.response.send_message(embed=embed)

    @convert_temperature.error
    async def convert_temperature_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}! Please Send to this to my developer", ephemeral=True)
        print(interaction.command)
        traceback.print_exc()

    @app_commands.user_install()
    @app_commands.guild_install()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        speed_unit="Select a Unit of Speed from the dropdown.",
        speed="Please enter a number",
    )
    @app_commands.command(description="A command to convert speeds to different scales")
    async def convert_speed(self, interaction: discord.Interaction, speed_unit: utils.Speed, speed: float):
        speeds = speed_unit.convert_to(speed)

        if speeds.miles <= 25:
            color = 0xFFFF00

            # 25 miles per hour in a us residence zone
            # yellow for a small speed

        if speeds.miles > 25 and speeds.miles <= 55:

            color = 0x8450

            # 55 mph speed limit on rural highways
            # green for about a not so slow speed.

        if speeds.miles > 55 and speeds.miles <= 70:

            color = 0x26F7FD

            # 70 mph is the max on rural interstate highways
            # color is choosen from the hydro thunder hurriance boost colors as close as I could match

        # https://highways.dot.gov/safety/speed-management/speed-limit-basics
        # information gathered from here.

        if speeds.miles > 70 and speeds.miles <= 85:

            # texas has the highest maximum sped limit at 85 mph according to
            # https://worldpopulationreview.com/state-rankings/speed-limit-map-by-state

            color = 0x8B

            # color choosen for faster boost color essentially

        if speeds.miles > 85 and speeds.miles <= 212.81:

            # https://rerev.com/articles/how-fast-do-nascar-cars-go
            # 212.809 miles per hour is the maximum they go up to.
            # rounded to 212.81 for convivence

            color = 0xCC0202
            # red for please don't go this speed normally.

        if speeds.miles > 212.81:
            # basically please don't go more than this speed unless you are in a plane or so other faster vehicle
            color = 0x0
            # pure black for emphasis.

        embed = discord.Embed(title="Speed:", color=color)

        embed.add_field(name="Miles:", value=f"{speeds.miles:,} mi")
        embed.add_field(name="Kilometers:", value=f"{speeds.kilometers:,} km")
        embed.add_field(name="Meters:", value=f"{speeds.meters:,} m")
        embed.add_field(name="Feet", value=f"{speeds.feet:,} ft")
        embed.add_field(name="Megameters", value=f"{speeds.megameters:,} Mm")
        # speed of light's name value needs a better name
        embed.add_field(name="Constants (Speed of Light):", value=f"{speeds.light:,} C")
        # megameters and light speed are elite dangerous references
        # see https://www.reddit.com/r/EliteDangerous/s/1AgiKH9Xj0

        embed.set_footer(text=f"Chose: {speed_unit.value}")
        await interaction.response.send_message(embed=embed)

        # embed could be be better

    @convert_speed.error
    async def convert_speed_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}! Please Send to this to my developer", ephemeral=True)
        print(interaction.command)
        traceback.print_exc()

    @app_commands.user_install()
    @app_commands.guild_install()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        timezone="Select the timezone you would like to convert to.",
    )
    @app_commands.command(description="A command to convert the message timestamp to the region's time.")
    async def convert_timezone(self, interaction: discord.Interaction, timezone: typing.Optional[str] = None):

        timezones = self.available_timezones

        if not timezone:
            timestamp = discord.utils.format_dt(interaction.created_at)
            embed = discord.Embed(title="Time:", description=timestamp)
            embed.set_footer(text="Timezone: Not Specified")

        elif not timezone in timezones:
            timestamp = discord.utils.format_dt(interaction.created_at)
            embed = discord.Embed(title="Time:", description=timestamp)
            embed.set_footer(text="Timezone: Not Found")

        else:
            now_tz = interaction.created_at.astimezone(zoneinfo.ZoneInfo(timezone))
            am_pm_format = now_tz.strftime("%I:%M:%S %p")
            twenty_four_format = now_tz.strftime("%H:%M:%S")
            first_format = now_tz.strftime("%Y-%m-%d")
            second_format = now_tz.strftime("%Y-%d-%m")
            third_format = now_tz.strftime("%d-%m-%Y")
            fourth_format = now_tz.strftime("%m-%d-%Y")

            # possibly do colors depending on time but not sure.

            embed = discord.Embed(
                title="Time:",
                description=f"12 hour: {am_pm_format}\n24 hour: {twenty_four_format}\n\nYYYY-MM-DD: {first_format} \nYYYY-DD-MM: {second_format}\nDD-MM-YYYY: {third_format}\nMM-DD-YYYY: {fourth_format}",
            )
            embed.set_footer(text=f"Timezone: {timezone}")

        await interaction.response.send_message(embed=embed)

    @convert_timezone.autocomplete("timezone")
    async def convert_timezone_autocomplete(self, interaction: discord.Interaction, current: str) -> list[Choice]:

        timezones = self.available_timezones
        all_choices = [Choice(name=timezone, value=timezone) for timezone in timezones]

        if not (current):
            return all_choices[0:25]

        filtered_results = fuzzy.finder(current, timezones)
        results = [Choice(name=result, value=result) for result in filtered_results]

        return results[0:25]

    @convert_timezone.error
    async def convert_timezone_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}! Please Send to this to my developer", ephemeral=True)
        print(interaction.command)
        traceback.print_exc()

    # convert economy soon here.


async def setup(bot):
    await bot.add_cog(Extra(bot))
