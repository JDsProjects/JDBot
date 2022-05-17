import collections
import functools
import itertools
import os
import random
import traceback
import typing

import discord
import tweepy
from better_profanity import profanity
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import utils


class Test(commands.Cog):
    """A cog to have people test new commands, or wip ones"""

    def __init__(self, bot):
        self.bot = bot
        self.pool = self.bot.db
        self.afk = {}

    async def cog_load(self):
        pool = self.pool

        records = await pool.fetch("SELECT * FROM AFK")
        self.afk = {record.user_id: record for record in records}

    @commands.command(brief="this command will error by sending no content")
    async def te(self, ctx):
        await ctx.send("this command will likely error...")
        await ctx.send("")

    @commands.command(brief="WIP command to verify")
    async def verify(self, ctx):
        await ctx.send("WIP will make this soon..")

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.testers

    @commands.command(
        brief="a command to email you(work in progress)",
        help="This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary",
    )
    async def email(self, ctx, *args):
        print(args)
        await ctx.send("WIP")
        # will use modals on final
        # :)

    @commands.command(brief="WIP thing for birthday set up lol")
    async def birthday_setup(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="sleep time")
    async def set_sleeptime(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="wakeup time")
    async def set_wakeuptime(self, ctx):
        await ctx.send("WIP")

    def tweepy_grab(self, amount: int, username: str):

        consumer_key = os.getenv("tweet_key")
        consumer_secret = os.getenv("tweet_secret")

        auth = tweepy.OAuth2AppHandler(consumer_key, consumer_secret)

        access_token = os.getenv("tweet_access")
        access_secret = os.getenv("tweet_token")
        bearer_token = os.getenv("tweet_bearer")

        client = tweepy.Client(
            bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

        # tweets = twitter_api.user_timeline(screen_name=username, count=amount, tweet_mode="extended")
        # tweepy_fetch_user = twitter_api.get_user(username)

    @commands.command(brief="gets tweets from a username")
    async def tweet(self, ctx, amount: typing.Optional[int] = None, username=None):

        amount = amount or 10

        if not username:
            return await ctx.send("You Need to pick a username.")

        if amount > 30:
            return await ctx.send("You can only get 30 tweets at a time.")

        try:
            tweet_time = functools.partial(self.tweepy_grab, amount, username)
            post = await self.bot.loop.run_in_executor(None, tweet_time)

        except Exception as e:
            traceback.print_exc()
            return await ctx.send(f"Exception occured at {e}")

        # when fully completed move to extra.py(not the old Twitter Cog.), will also use modals, maybe

    @commands.command(brief="add emoji to your guild lol")
    async def emoji_add(self, ctx):
        await ctx.send("WIP")
        # look at the JDJG Bot orginal

    @commands.command(brief="scans statuses to see if there is any bad ones.")
    async def scan_status(self, ctx):
        await ctx.send("will scan statuses in a guild to see if there is a bad one.")

    @commands.command(brief="sets logs for a guild", name="logging")
    async def _logging(self, ctx):
        await ctx.send("logging wip.")

    # look at global_chat stuff for global_chat features, rank for well rank, add an update system too, add cc_ over. nick too, as well as kick and ban, ofc unban and other guild ban moderation stuff. Port over emoji_check but public and make that do it's best to upload less than 256 kB, try to and ofc an os emulation mode, as well as update mode, and nick.

    # Unrelated to Urban:
    # https://discordpy.readthedocs.io/en/master/api.html?highlight=interaction#discord.InteractionResponse.send_message
    # https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild.query_members

    # spyco data table in my sql database

    @commands.command()
    async def afk(self, ctx, *, reason: typing.Optional[str] = None):

        if ctx.author.id in self.afk:
            return await ctx.send("You can't afk if you are already afk")

        afk_user = await self.bot.db.fetchrow("SELECT * FROM AFK WHERE user_id = $1", ctx.author.id)

        if afk_user:
            return await ctx.send("You are already afk")

        reason = reason or "Unknown"

        reason = profanity.censor(reason, censor_char="#")

        embed = discord.Embed(title="Going AFK:", color=15428885)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        await ctx.send(
            content=f"{ctx.author.mention} is now afk", embed=embed, allowed_mentions=discord.AllowedMentions.none()
        )

        # await self.bot.db.execute("INSERT INTO AFK VALUES($1, $2, $3)", ctx.author.id, ctx.message.created_at, reason)
        # chai gave me a new method which is below
        data = await self.bot.db.fetchrow(
            "INSERT INTO AFK VALUES($1, $2, $3) RETURNING *", ctx.author.id, ctx.message.created_at, reason
        )

        self.afk[ctx.author.id] = data

        # going to be like other afk bots, however this will censor the afk message if contains bad words and will link the orginal message if I can.

    @commands.command(brief="a test of a new paginator :)")
    async def test_pagination(self, ctx):
        buttons = {
            "STOP": utils.PaginatorButton(emoji="<:stop:959853381885775902>", style=discord.ButtonStyle.secondary),
            "RIGHT": utils.PaginatorButton(emoji="<:next:959851091506364486>", style=discord.ButtonStyle.secondary),
            "LEFT": utils.PaginatorButton(emoji="<:back:959851091284095017>", style=discord.ButtonStyle.secondary),
            "LAST": utils.PaginatorButton(emoji="<:last:959851091330220042>", style=discord.ButtonStyle.secondary),
            "FIRST": utils.PaginatorButton(emoji="<:start:959851091502190674>", style=discord.ButtonStyle.secondary),
        }
        pages = [discord.Embed(title="eh")] * 10
        menu = utils.Paginator(pages, ctx=ctx, buttons=buttons, delete_after=True)
        await menu.send()

    @commands.command()
    async def tags(self, ctx):
        await ctx.send("WIP")

    @commands.command()
    async def reminders(self, ctx):
        await ctx.send("WIP")
        # soon to be a reminders like thing like R.danny's ofc with my own code

    @commands.command(brief="Notes so you can refer back to them for important stuff")
    async def notes(self, ctx):
        await ctx.send("WIP")
        # Note this is not like todo, todo is for small things, notes is for big things

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk:
            data = self.afk[message.author.id]

            timestamp = discord.utils.format_dt(data.added_time, style="R")

            embed = discord.Embed(title="Afk:", description=f"Reason : **{data.text}**\nAfk Since : {timestamp}")
            await message.channel.send(
                f"Welcome Back {message.author.mention} you went away with Reason: **{data.text}** for {timestamp}",
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )

            del self.afk[message.author.id]
            await self.bot.db.execute("DELETE FROM AFK WHERE user_id = $1", message.author.id)


class Slash(commands.Cog):
    """A Testing Category for Slash Commands"""

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Test(bot))
    await bot.add_cog(Slash(bot))
