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

    @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
    async def setprefix(self, ctx, *, arg=None):
        await ctx.send("WIP")

    @commands.command(brief="WIP thing for birthday set up lol")
    async def birthday_setup(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="sleep time")
    async def set_sleeptime(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="wakeup time")
    async def set_wakeuptime(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="gets tweets from a username")
    async def tweet(self, ctx, amount: typing.Optional[int] = None, username=None):

        amount = amount or 10

        if not username:
            return await ctx.send("You Need to pick a username.")

        await ctx.send("WIP")
        
        #when fully completed move to extra.py(not the old Twitter Cog.)

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


class Slash(commands.Cog):
    """A Testing Category for Slash Commands"""

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Test(bot))
    bot.add_cog(Slash(bot))
