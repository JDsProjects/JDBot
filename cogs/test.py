from discord.ext import commands
import discord
import typing
import random
import utils
from discord.ext.commands.cooldowns import BucketType
import collections
import itertools
import tweepy
import os
import functools
import traceback


class Test(commands.Cog):
    """A cog to have people test new commands, or wip ones"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ticket_make(self, ctx):
        await ctx.send("WIP, will make ticket soon.. Please Contact the owner with the support command")

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

    @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
    async def setprefix(self, ctx, *, prefix: str = None):
        db = self.bot.db
        if ctx.guild:
            is_dm = 0
            tid = ctx.guild.id
        else:
            is_dm = 1
            tid = ctx.author.id
        if await db.fetchrow("SELECT * FROM PREFIXES WHERE is_dm = $1 AND id = $2", is_dm, tid):
            return await ctx.send("You already have custom prefix set.")

        if prefix:
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
                await ctx.send("Successfully removed prefix.")
            else:
                return await ctx.send("Cancelled.")

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

    # guild_prefixes table in my sql database
    # spyco data table in my sql database

    @commands.command()
    async def afk(self, ctx):
        await ctx.send("EH WIP")

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


class Slash(commands.Cog):
    """A Testing Category for Slash Commands"""

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Test(bot))
    await bot.add_cog(Slash(bot))
