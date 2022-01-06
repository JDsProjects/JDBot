from discord.ext import commands
import discord
import os
import tweepy
import functools


class Twitter(commands.Cog):
    "Commands related to Twitter"

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Twitter(bot))
